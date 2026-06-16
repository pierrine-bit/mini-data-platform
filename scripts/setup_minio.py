import logging
import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET = os.getenv("MINIO_BUCKET", "sales-data")
LOCAL_FILE = Path("data/sales_data.csv")


def main():
    """Creates the MinIO bucket if absent, then uploads the local sales CSV."""
    client = boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )

    try:
        client.head_bucket(Bucket=BUCKET)
        log.info("Bucket '%s' already exists.", BUCKET)
    except ClientError:
        client.create_bucket(Bucket=BUCKET)
        log.info("Created bucket '%s'.", BUCKET)

    if not LOCAL_FILE.exists():
        log.error(
            "%s not found. Run: python scripts/generate_sample_data.py",
            LOCAL_FILE,
        )
        sys.exit(1)

    object_name = os.getenv("MINIO_OBJECT", "sales_data.csv")

    client.upload_file(
        str(LOCAL_FILE),
        BUCKET,
        object_name,
    )

    log.info(
        "Uploaded %s -> s3://%s/%s",
        LOCAL_FILE,
        BUCKET,
        object_name,
    )


if __name__ == "__main__":
    main()