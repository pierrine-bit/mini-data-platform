"""Extract sales data from MinIO and filter already-loaded records."""

import logging
import os

import pandas as pd
import psycopg2

from minio_client import download_sales_file

logger = logging.getLogger(__name__)

LOCAL_FILE = "/opt/airflow/data/sales_data.csv"

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "airflow")
DB_USER = os.getenv("POSTGRES_USER", "airflow")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")


def get_last_loaded_date():
    """Return the latest loaded order date from PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )

        result = pd.read_sql("SELECT MAX(order_date) FROM sales;", conn)
        conn.close()

        return result.iloc[0, 0]

    except Exception as exc:
        logger.warning("Could not fetch last loaded date: %s", exc)
        return None


def extract_data(file_path: str = LOCAL_FILE) -> pd.DataFrame:
    """Download sales CSV and return only new records."""
    download_sales_file(file_path)

    df = pd.read_csv(file_path)
    df["order_date"] = pd.to_datetime(df["order_date"])

    last_loaded_date = get_last_loaded_date()

    if last_loaded_date is not None:
        df = df[df["order_date"] > last_loaded_date]

    logger.info("New records to process: %s", len(df))
    return df