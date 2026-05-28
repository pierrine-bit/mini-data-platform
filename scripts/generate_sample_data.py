"""Generate fake sales data for the mini data platform demo."""

import logging
import random
from pathlib import Path

import pandas as pd
from faker import Faker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

fake = Faker()

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

PRODUCTS = ["Laptop", "Phone", "Tablet", "Monitor"]
REGIONS = ["Africa", "Europe", "Asia", "America"]


def generate_sales_data(rows: int = 500) -> pd.DataFrame:
    """Create sample sales records."""
    data = []

    for _ in range(rows):
        data.append(
            {
                "order_id": fake.uuid4(),
                "customer_id": fake.uuid4(),
                "product": random.choice(PRODUCTS),
                "amount": round(random.uniform(50, 2000), 2),
                "region": random.choice(REGIONS),
                "order_date": fake.date_between(start_date="-1y", end_date="today"),
            }
        )

    return pd.DataFrame(data)


if __name__ == "__main__":
    df = generate_sales_data()
    output_path = OUTPUT_DIR / "sales_data.csv"
    df.to_csv(output_path, index=False)

    logger.info("Generated %s", output_path)