"""Airflow DAG for the sales ETL pipeline."""

import logging
import sys
from datetime import datetime, timedelta

sys.path.append("/opt/airflow/src")

from airflow.decorators import dag, task

logger = logging.getLogger(__name__)

LOCAL_FILE = "/opt/airflow/data/sales_data.csv"

default_args = {
    "owner": "pierrine",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="sales_etl_pipeline",
    description="Sales ETL: MinIO to PostgreSQL",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["sales", "etl", "minio", "postgres"],
)
def sales_etl_pipeline():
    """Define the sales ETL workflow."""

    @task
    def check_source() -> None:
        """Confirm the input CSV exists in MinIO."""
        from minio_client import sales_file_exists

        if not sales_file_exists():
            raise FileNotFoundError("sales_data.csv not found in MinIO bucket")

    @task
    def extract() -> list[dict]:
        """Extract raw sales records from MinIO."""
        import pandas as pd
        from minio_client import download_sales_file

        download_sales_file(LOCAL_FILE)
        df = pd.read_csv(LOCAL_FILE)
        df["order_date"] = pd.to_datetime(df["order_date"]).astype(str)

        logger.info("Extracted %d rows", len(df))
        return df.to_dict(orient="records")

    @task
    def transform(records: list[dict]) -> list[dict]:
        """Transform raw records into clean records."""
        import pandas as pd
        from transform import transform_sales

        df = pd.DataFrame(records)
        cleaned = transform_sales(df)
        cleaned["order_date"] = cleaned["order_date"].astype(str)

        logger.info("Transformed %d rows", len(cleaned))
        return cleaned.to_dict(orient="records")

    @task
    def validate(records: list[dict]) -> list[dict]:
        """Run data quality checks before loading."""
        import pandas as pd
        from validation import validate_sales

        validate_sales(pd.DataFrame(records))
        logger.info("Validation passed")
        return records

    @task
    def load(records: list[dict]) -> int:
        """Load validated records into PostgreSQL."""
        import pandas as pd
        from load import load_data

        df = pd.DataFrame(records)
        df["order_date"] = pd.to_datetime(df["order_date"])

        inserted = load_data(df)
        logger.info("Inserted %d rows into PostgreSQL", inserted)
        return inserted

    source = check_source()
    raw = extract()
    cleaned = transform(raw)
    valid = validate(cleaned)
    loaded = load(valid)

    source >> raw >> cleaned >> valid >> loaded


sales_etl_pipeline()