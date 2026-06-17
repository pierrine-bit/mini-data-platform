import logging
import os

import boto3
import pandas as pd
import psycopg2

logger = logging.getLogger(__name__)

LOCAL_FILE = os.getenv("AIRFLOW_DATA_PATH", "/opt/airflow/data/sales_data.csv")

_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
_BUCKET = os.getenv("MINIO_BUCKET", "sales-data")
_OBJECT = os.getenv("MINIO_OBJECT", "sales_data.csv")


def _get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=_ENDPOINT,
        aws_access_key_id=_ACCESS_KEY,
        aws_secret_access_key=_SECRET_KEY,
    )


def sales_file_exists() -> bool:
    """Uses head_object — a lightweight metadata check that avoids downloading the file."""
    client = _get_minio_client()
    try:
        client.head_object(Bucket=_BUCKET, Key=_OBJECT)
        return True
    except Exception as exc:
        logger.warning("Sales file not found in MinIO: %s", exc)
        return False


def download_sales_file(local_path: str) -> None:
    client = _get_minio_client()
    client.download_file(_BUCKET, _OBJECT, local_path)
    logger.info("Downloaded %s from bucket '%s'", _OBJECT, _BUCKET)


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
