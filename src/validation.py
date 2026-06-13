
import logging

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "order_id",
    "customer_id",
    "product",
    "amount",
    "region",
    "order_date",
}

VALID_PRODUCTS = {"Laptop", "Phone", "Tablet", "Monitor"}
VALID_REGIONS = {"Africa", "Europe", "Asia", "America"}


def validate_sales(df) -> None:
    """Raises ValueError if the DataFrame fails any data quality check."""
    logger.info("Running sales data validation")

    if df.empty:
        raise ValueError("DataFrame is empty")

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if df["order_id"].isna().any():
        raise ValueError("Null order_id detected")

    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order_id detected")

    if df["amount"].isna().any():
        raise ValueError("Null amount detected")

    if (df["amount"] <= 0).any():
        raise ValueError("Invalid amount detected")

    if df["order_date"].isna().any():
        raise ValueError("Invalid or missing order_date detected")

    invalid_products = set(df["product"]) - VALID_PRODUCTS
    if invalid_products:
        raise ValueError(f"Invalid products detected: {invalid_products}")

    invalid_regions = set(df["region"]) - VALID_REGIONS
    if invalid_regions:
        raise ValueError(f"Invalid regions detected: {invalid_regions}")

    logger.info("Validation passed")