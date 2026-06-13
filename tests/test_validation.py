
import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from validation import validate_sales


@pytest.fixture
def valid_df():
    """Create a valid sales DataFrame for tests."""
    return pd.DataFrame(
        {
            "order_id": ["1"],
            "customer_id": ["C1"],
            "product": ["Laptop"],
            "amount": [1000],
            "region": ["Africa"],
            "order_date": ["2024-01-01"],
        }
    )


def test_validate_sales_passes(valid_df):
    """Valid sales data should pass validation."""
    validate_sales(valid_df)


def test_validate_sales_rejects_negative_amount(valid_df):
    """Negative sales amount should fail validation."""
    df = valid_df.copy()
    df["amount"] = [-10]

    with pytest.raises(ValueError):
        validate_sales(df)


def test_validate_sales_rejects_duplicate_order_id(valid_df):
    """Duplicate order IDs should fail validation."""
    df = pd.concat([valid_df, valid_df], ignore_index=True)

    with pytest.raises(ValueError):
        validate_sales(df)