import pandas as pd
from typing import List

REQUIRED_FEATURES = [
    "sales_channel",
    "payment_mode",
    "is_gift",
    "shield_member",
    "family",
    "discount_pct",
    "promised_delivery_days",
    "customer_prior_orders",
    "customer_prior_returns"
]

EXCLUDED_FIELDS = [
    "pickup_scheduled_at",
    "last_service_event_type",
    "source",
    "order_id",
    "customer_id",
    "delivery_note",
    "signup_date",
    "launch_date",
    "delivery_pincode",
    "order_value_inr",
    "qty",
    "sku",
    "state",
    "city",
    "tenure"
]

def check_exclusion_guard(columns: List[str]):
    """Guard that fails if any excluded field appears."""
    for col in EXCLUDED_FIELDS:
        if col in columns:
            raise ValueError(f"Excluded field '{col}' found in input path.")

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs the feature matrix enforcing the exact 9-feature contract.
    """
    # Will raise KeyError if a required feature is missing
    X = df[REQUIRED_FEATURES].copy()

    check_exclusion_guard(X.columns.tolist())

    # Assert exact order and exact names
    assert list(X.columns) == REQUIRED_FEATURES, f"Feature columns must exactly match {REQUIRED_FEATURES}"

    return X
