"""Database setup with SQLAlchemy - PostgreSQL backend."""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}".format(
        user=os.getenv("POSTGRES_USER", "prefect"),
        password=os.getenv("POSTGRES_PASSWORD", "prefect"),
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        db=os.getenv("POSTGRES_DB", "prefect"),
    ),
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class ProgressData(Base):
    """Model untuk data progress monitoring Susenas."""

    __tablename__ = "progress_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tahapan: Mapped[str] = mapped_column(String, nullable=False)
    wilayah: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    persentase: Mapped[float] = mapped_column(Float, nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


def init_db() -> None:
    """Create all tables in the database."""
    Base.metadata.create_all(engine)


def insert_data(df: pd.DataFrame) -> int:
    """Insert DataFrame rows into progress_data table.

    Returns:
        Number of rows inserted.
    """
    if df.empty:
        return 0

    records = df.to_dict(orient="records")
    with SessionLocal() as session:
        session.bulk_insert_mappings(ProgressData, records)
        session.commit()
    return len(records)


def read_data(scraped_date: str | None = None) -> pd.DataFrame:
    """Read progress data from database, optionally filtered by date.

    Args:
        scraped_date: Optional date string (YYYY-MM-DD) to filter by.

    Returns:
        DataFrame with all matching records.
    """
    query = "SELECT * FROM progress_data"
    params = {}
    if scraped_date:
        query += " WHERE DATE(scraped_at) = :dt"
        params["dt"] = scraped_date

    return pd.read_sql(query, engine, params=params)


def get_available_dates() -> list[str]:
    """Return list of distinct scraped dates."""
    query = "SELECT DISTINCT DATE(scraped_at) as dt FROM progress_data ORDER BY dt DESC"
    df = pd.read_sql(query, engine)
    return df["dt"].tolist()
