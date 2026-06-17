
import logging
import os
import sys
from datetime import datetime, timedelta

sys.path.append("/opt/airflow/src")

from airflow.decorators import dag, task

logger = logging.getLogger(__name__)

default_args = {
    "owner": os.getenv("AIRFLOW_ADMIN_USER", "airflow"),
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="sales_etl_pipeline",
    description="Sales ETL: MinIO → transform → validate → PostgreSQL",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["sales", "etl", "minio", "postgres"],
)
def sales_etl_pipeline():

    @task
    def check_source() -> None:
        # Abort early if source file is missing
        from extract import sales_file_exists
        if not sales_file_exists():
            raise FileNotFoundError("sales_data.csv not found in MinIO bucket")

    @task
    def extract() -> list[dict]:
        from extract import extract_data
        df = extract_data()
        logger.info("Extracted %d new rows", len(df))
        if df.empty:
            return []
        df["order_date"] = df["order_date"].astype(str)
        return df.to_dict(orient="records")

    @task
    def transform(records: list[dict]) -> list[dict]:
        import pandas as pd
        from transform import transform_sales
        if not records:
            logger.info("No records to transform")
            return []
        df = pd.DataFrame(records)
        df["order_date"] = pd.to_datetime(df["order_date"])
        cleaned = transform_sales(df)
        cleaned["order_date"] = cleaned["order_date"].astype(str)
        logger.info("Transformed %d rows", len(cleaned))
        return cleaned.to_dict(orient="records")

    @task
    def validate(records: list[dict]) -> list[dict]:
        import pandas as pd
        from validation import validate_sales
        if not records:
            logger.info("No records to validate")
            return []
        df = pd.DataFrame(records)
        df["order_date"] = pd.to_datetime(df["order_date"])
        validate_sales(df)
        logger.info("Validation passed for %d rows", len(records))
        return records

    @task
    def load(records: list[dict]) -> int:
        import pandas as pd
        from load import load_data
        if not records:
            logger.info("No records to load")
            return 0
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
