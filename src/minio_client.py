
import logging
import os

import boto3

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET_NAME = os.getenv("MINIO_BUCKET", "sales-data")
OBJECT_NAME = os.getenv("MINIO_OBJECT", "sales_data.csv")


def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )


def sales_file_exists() -> bool:
    """Uses head_object — a lightweight metadata check that avoids downloading the file."""
    client = get_minio_client()

    try:
        client.head_object(Bucket=BUCKET_NAME, Key=OBJECT_NAME)
        return True
    except Exception as exc:
        logger.warning("Sales file not found in MinIO: %s", exc)
        return False


def download_sales_file(local_path: str) -> None:
    client = get_minio_client()
    client.download_file(BUCKET_NAME, OBJECT_NAME, local_path)

    logger.info("Downloaded %s from bucket '%s'", OBJECT_NAME, BUCKET_NAME)