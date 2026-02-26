"""Web scraping module - SSO authentication and HTML table extraction."""

from __future__ import annotations

from datetime import date

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sso_auth import authenticate, create_session

BASE_URL = "https://webmonitoring.bps.go.id/sen/progress"

TAHAPAN_URLS: dict[str, str] = {
    "Pemutakhiran": "pemutakhiran",
    "Pencacahan": "pencacahan",
    "Pemeriksaan": "edcod",
    "Pengiriman ke KabKota": "pengiriman",
    "Penerimaan di KabKota": "penerimaan",
    "Penerimaan di IPDS": "ipds",
    "Pengolahan Dokumen K": "pengolahan",
    "Pengolahan Dokumen KP": "pengolahan2",
}


def build_url(tahapan_path: str, wil: str = "65", tgl_his: str | None = None) -> str:
    """Build full URL for a given tahapan.

    Args:
        tahapan_path: URL path segment (e.g. 'pemutakhiran').
        wil: Wilayah code, default '65' (Kalimantan Utara).
        tgl_his: Date string YYYY-MM-DD. Defaults to today.

    Returns:
        Full URL string.
    """
    if tgl_his is None:
        tgl_his = date.today().isoformat()
    return f"{BASE_URL}/{tahapan_path}?wil={wil}&view=tabel&tgl_his={tgl_his}"


def login_sso(username: str, password: str) -> requests.Session:
    """Authenticate via SSO and return a session with cookies.

    Args:
        username: SSO username.
        password: SSO password.

    Returns:
        Authenticated requests.Session.

    Raises:
        RuntimeError: If authentication fails.
    """
    session = create_session()
    result = authenticate(username, password, session=session)

    if not result:
        raise RuntimeError("SSO authentication failed - no result returned.")

    # If auth_code or direct_grant returned access_token, session cookies may
    # already be populated. For session_based, cookies are set directly.
    if "_cookies" in result:
        for name, value in result["_cookies"].items():
            session.cookies.set(name, value)

    return session


def scrape_table(session: requests.Session, url: str) -> pd.DataFrame:
    """Scrape HTML table from the monitoring page.

    Args:
        session: Authenticated requests session.
        url: Full URL to scrape.

    Returns:
        Raw DataFrame parsed from the HTML table.

    Raises:
        ValueError: If no table found on the page.
    """
    resp = session.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id="tabel-progress")
    if table is None:
        raise ValueError(f"Table 'tabel-progress' not found at {url}")

    # Parse header - get first row of thead for column names
    thead = table.find("thead")
    header_row = thead.find("tr") if thead else None
    headers = []
    if header_row:
        for th in header_row.find_all("th"):
            headers.append(th.get_text(strip=True))

    # Parse body rows
    tbody = table.find("tbody")
    rows = []
    if tbody:
        for tr in tbody.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            row = [cell.get_text(strip=True) for cell in cells]
            rows.append(row)

    # Ensure column count matches
    if headers and rows:
        max_cols = max(len(headers), max(len(r) for r in rows))
        headers = headers + [f"col_{i}" for i in range(len(headers), max_cols)]
        rows = [r + [""] * (max_cols - len(r)) for r in rows]

    return pd.DataFrame(rows, columns=headers if headers else None)
