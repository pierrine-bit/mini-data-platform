
import os
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from transform import transform_sales


def test_transform_sales():
    """Transformation should keep valid records and convert amount to float."""
    data = {
        "order_id": ["1"],
        "customer_id": ["C1"],
        "product": ["Laptop"],
        "amount": [1000],
        "region": ["Africa"],
        "order_date": ["2024-01-01"],
    }

    df = pd.DataFrame(data)
    result = transform_sales(df)

    assert not result.empty
    assert "amount" in result.columns
    assert result["amount"].dtype == float


def test_transform_removes_duplicates():
    """Transformation should remove duplicate order IDs."""
    data = {
        "order_id": ["1", "1"],
        "customer_id": ["C1", "C1"],
        "product": ["Laptop", "Laptop"],
        "amount": [1000, 1000],
        "region": ["Africa", "Africa"],
        "order_date": ["2024-01-01", "2024-01-01"],
    }

    df = pd.DataFrame(data)
    result = transform_sales(df)

    assert len(result) == 1