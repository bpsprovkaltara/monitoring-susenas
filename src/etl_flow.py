"""Prefect ETL flow - extract, transform, load for monitoring Susenas."""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from prefect import flow, get_run_logger, task

from src.database import init_db, insert_data
from src.scraper import TAHAPAN_URLS, build_url, login_sso, scrape_table

load_dotenv()


@task(retries=3, retry_delay_seconds=10, log_prints=True)
def extract(session, tahapan: str, url: str) -> pd.DataFrame:
    """Extract raw table data from a single tahapan URL.

    Args:
        session: Authenticated requests session.
        tahapan: Name of the tahapan.
        url: Full URL to scrape.

    Returns:
        Raw DataFrame from the scraped table.
    """
    logger = get_run_logger()
    logger.info(f"Extracting: {tahapan} from {url}")

    df = scrape_table(session, url)
    logger.info(f"Extracted {len(df)} rows for {tahapan}")
    return df


@task(log_prints=True)
def transform(df: pd.DataFrame, tahapan: str) -> pd.DataFrame:
    """Transform raw scraped data into clean format.

    Logic:
    - Filter rows where Wilayah contains '(65'
    - Clean wilayah names (remove codes in parentheses)
    - Set status label based on tahapan type
    - Convert percentage column to numeric
    - Keep only rows with persentase > 0
    - Add scraped_at timestamp

    Args:
        df: Raw DataFrame from extract.
        tahapan: Name of the tahapan.

    Returns:
        Cleaned DataFrame ready for loading.
    """
    logger = get_run_logger()

    if df.empty:
        logger.warning(f"Empty DataFrame for {tahapan}, skipping transform.")
        return pd.DataFrame()

    # Filter rows containing '(65' in first column (Wilayah)
    col_wilayah = df.columns[0]
    mask = df[col_wilayah].astype(str).str.contains(r"\(65", na=False)
    df_filtered = df[mask].copy()

    if df_filtered.empty:
        logger.warning(f"No rows with '(65' found for {tahapan}.")
        return pd.DataFrame()

    # Clean wilayah names - remove code in parentheses
    df_filtered[col_wilayah] = (
        df_filtered[col_wilayah]
        .str.replace(r"\(.*\)\s*", "", regex=True)
        .str.strip()
    )

    # Determine status label
    label_status = "Error" if "Pengolahan" in tahapan else "Belum Selesai"

    # Convert percentage column (index 5, i.e. 6th column) to numeric
    # Indonesian format uses comma as decimal separator
    col_persen = df_filtered.columns[5]
    df_filtered[col_persen] = (
        df_filtered[col_persen]
        .astype(str)
        .str.replace(".", "", regex=False)   # remove thousand separator
        .str.replace(",", ".", regex=False)  # comma → dot for decimal
    )
    df_filtered[col_persen] = pd.to_numeric(df_filtered[col_persen], errors="coerce").fillna(0)

    # Keep only rows with persentase > 0
    df_filtered = df_filtered[df_filtered[col_persen] > 0].copy()

    if df_filtered.empty:
        logger.info(f"All percentages are 0 for {tahapan}, nothing to load.")
        return pd.DataFrame()

    # Build output DataFrame
    result = pd.DataFrame(
        {
            "tahapan": tahapan,
            "wilayah": df_filtered[col_wilayah].values,
            "status": label_status,
            "persentase": df_filtered[col_persen].values,
            "scraped_at": datetime.now(),
        }
    )

    logger.info(f"Transformed {len(result)} rows for {tahapan} (status: {label_status})")
    return result


@task(log_prints=True)
def load(df: pd.DataFrame) -> int:
    """Load transformed data into the SQLite database.

    Args:
        df: Cleaned DataFrame to insert.

    Returns:
        Number of rows inserted.
    """
    logger = get_run_logger()

    if df.empty:
        logger.info("No data to load.")
        return 0

    count = insert_data(df)
    logger.info(f"Loaded {count} rows into database.")
    return count


@flow(name="Monitoring Susenas ETL", log_prints=True)
def monitoring_flow(wil: str = "65", tgl_his: str | None = None) -> dict[str, int]:
    """Main ETL flow: authenticate, scrape all tahapan, transform, and load.

    Args:
        wil: Wilayah code. Default '65' (Kalimantan Utara).
        tgl_his: Date string YYYY-MM-DD. Defaults to today.

    Returns:
        Dict mapping tahapan name → number of rows loaded.
    """
    logger = get_run_logger()

    # Initialize database
    init_db()

    # Authenticate
    username = os.getenv("SSO_USERNAME")
    password = os.getenv("SSO_PASSWORD")
    if not username or not password:
        raise ValueError("SSO_USERNAME and SSO_PASSWORD must be set in .env")

    logger.info("Authenticating via SSO...")
    session = login_sso(username, password)
    logger.info("SSO authentication successful.")

    # Process each tahapan
    results: dict[str, int] = {}
    for tahapan, path in TAHAPAN_URLS.items():
        url = build_url(path, wil=wil, tgl_his=tgl_his)

        raw_df = extract(session, tahapan, url)
        clean_df = transform(raw_df, tahapan)
        count = load(clean_df)
        results[tahapan] = count

    total = sum(results.values())
    logger.info(f"Flow complete. Total rows loaded: {total}")
    return results


if __name__ == "__main__":
    monitoring_flow()
