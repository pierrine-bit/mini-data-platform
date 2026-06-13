import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

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
        print(f"Bucket '{BUCKET}' already exists.")
    except ClientError:
        client.create_bucket(Bucket=BUCKET)
        print(f"Created bucket '{BUCKET}'.")

    if not LOCAL_FILE.exists():
        print(f"ERROR: {LOCAL_FILE} not found. Run: python scripts/generate_sample_data.py")
        sys.exit(1)

    client.upload_file(str(LOCAL_FILE), BUCKET, os.getenv("MINIO_OBJECT", "sales_data.csv"))
    print(f"Uploaded {LOCAL_FILE} → s3://{BUCKET}/sales_data.csv")


if __name__ == "__main__":
    main()
