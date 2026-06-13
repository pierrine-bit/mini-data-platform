
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def transform_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize sales data. Rows with unparseable dates are dropped."""
    logger.info("Starting sales transformation")

    df = df.copy()
    df = df.dropna()
    df["amount"] = df["amount"].astype(float)
    # errors="coerce" turns unparseable dates into NaT, which dropna then removes
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"])
    df = df.drop_duplicates(subset=["order_id"])

    logger.info("Transformation completed with %s rows", len(df))
    return df