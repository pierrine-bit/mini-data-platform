import logging
import os

import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


def _build_db_uri() -> str:
    return os.getenv("DB_URI") or (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', '5432')}"
        f"/{os.getenv('POSTGRES_DB')}"
    )


def load_data(df: pd.DataFrame) -> int:
    if df.empty:
        logger.info("No records to load")
        return 0

    engine = create_engine(_build_db_uri())

    with engine.begin() as conn:
        # Skip records already in the table to avoid duplicates
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
