
import logging
import os

import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DB_URI = os.getenv(
    "DB_URI",
    "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
)


def load_data(df: pd.DataFrame) -> int:
    """Append new sales records to PostgreSQL and return inserted row count."""
    if df.empty:
        logger.info("No records to load")
        return 0

    engine = create_engine(DB_URI)

    with engine.begin() as conn:
        existing = pd.read_sql(text("SELECT order_id FROM sales"), conn)
        df = df[~df["order_id"].isin(existing["order_id"])]

        if df.empty:
            logger.info("No new records to insert")
            return 0

        df.to_sql(
            "sales",
            conn,
            if_exists="append",
            index=False,
            method="multi",
        )

    logger.info("Inserted %s records into PostgreSQL", len(df))
    return len(df)