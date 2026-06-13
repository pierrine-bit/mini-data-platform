import logging
import os

import pandas as pd
import psycopg2

from minio_client import download_sales_file

logger = logging.getLogger(__name__)

LOCAL_FILE = os.getenv("AIRFLOW_DATA_PATH", "/opt/airflow/data/sales_data.csv")


def get_last_loaded_date():
    """Returns None on failure, which triggers a full load in extract_data."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        result = pd.read_sql("SELECT MAX(order_date) FROM sales;", conn)
        conn.close()
        return result.iloc[0, 0]

    except Exception as exc:
        logger.warning("Could not fetch last loaded date: %s", exc)
        return None


def extract_data(file_path: str = LOCAL_FILE) -> pd.DataFrame:
    """Downloads from MinIO and returns only records newer than the last load."""
    download_sales_file(file_path)

    df = pd.read_csv(file_path)
    df["order_date"] = pd.to_datetime(df["order_date"])

    last_loaded_date = get_last_loaded_date()

    if last_loaded_date is not None:
        df = df[df["order_date"] > last_loaded_date]

    logger.info("New records to process: %s", len(df))
    return df
