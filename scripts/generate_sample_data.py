
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


PRODUCT_PRICES = {
    "Laptop": (800, 2000),
    "Monitor": (200, 800),
    "Tablet": (300, 1200),
    "Phone": (400, 1500),
}

CUSTOMER_POOL = [fake.uuid4() for _ in range(200)]


def generate_sales_data(rows: int = 2000) -> pd.DataFrame:
    data = []
    for _ in range(rows):
        product = random.choice(PRODUCTS)
        low, high = PRODUCT_PRICES[product]
        data.append(
            {
                "order_id": fake.uuid4(),
                "customer_id": random.choice(CUSTOMER_POOL),
                "product": product,
                "amount": round(random.uniform(low, high), 2),
                "region": random.choice(REGIONS),
                "order_date": fake.date_time_between(start_date="-1y", end_date="now"),
            }
        )
    return pd.DataFrame(data)


if __name__ == "__main__":
    df = generate_sales_data()
    output_path = OUTPUT_DIR / "sales_data.csv"
    df.to_csv(output_path, index=False)
    logger.info("Generated %s", output_path)