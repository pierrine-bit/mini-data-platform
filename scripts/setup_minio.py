"""Creates the MinIO bucket and uploads sales_data.csv."""
import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
BUCKET = os.getenv("MINIO_BUCKET", "sales-data")
LOCAL_FILE = Path("data/sales_data.csv")


def main():
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

    client.upload_file(str(LOCAL_FILE), BUCKET, "sales_data.csv")
    print(f"Uploaded {LOCAL_FILE} → s3://{BUCKET}/sales_data.csv")


if __name__ == "__main__":
    main()
