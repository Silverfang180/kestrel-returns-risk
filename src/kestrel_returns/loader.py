import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple

DATA_DIR = Path(__file__).parent.parent.parent / "data"

TRAIN_USECOLS = [
    "order_id", "order_placed_at", "customer_id", "sku", "sales_channel",
    "payment_mode", "discount_pct", "qty", "order_value_inr",
    "promised_delivery_days", "delivery_pincode", "is_gift",
    "customer_prior_orders", "customer_prior_returns", "source", "returned"
]

TEST_USECOLS = [
    "order_id", "order_placed_at", "customer_id", "sku", "sales_channel",
    "payment_mode", "discount_pct", "qty", "order_value_inr",
    "promised_delivery_days", "delivery_pincode", "is_gift",
    "customer_prior_orders", "customer_prior_returns", "source"
]

def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load train, test, customers, and products data with explicit usecols."""
    train = pd.read_csv(DATA_DIR / "train.csv", usecols=TRAIN_USECOLS, dtype={"delivery_pincode": str})
    test = pd.read_csv(DATA_DIR / "test_unlabelled.csv", usecols=TEST_USECOLS, dtype={"delivery_pincode": str})
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    products = pd.read_csv(DATA_DIR / "products.csv")

    return train, test, customers, products

def deduplicate_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate on order_id before any split, keeping the 'crm' row."""
    # 'crm' comes before 'partner_feed' alphabetically, so sorting by source ensures 'crm' is first
    df_sorted = df.sort_values(by=["order_id", "source"])
    df_deduped = df_sorted.drop_duplicates(subset=["order_id"], keep="first").copy()

    # Drop 'source' as it is an audit field and never a feature
    if "source" in df_deduped.columns:
        df_deduped = df_deduped.drop(columns=["source"])

    return df_deduped

def join_reference_data(df: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Join customers (for shield_member) and products (for family)."""
    df_joined = df.merge(customers[["customer_id", "shield_member"]], on="customer_id", how="left")
    df_joined = df_joined.merge(products[["sku", "family"]], on="sku", how="left")

    return df_joined

def load_and_prepare() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Full loader pipeline for train and test."""
    train, test, customers, products = load_data()

    train_deduped = deduplicate_orders(train)
    test_deduped = deduplicate_orders(test)

    train_final = join_reference_data(train_deduped, customers, products)
    test_final = join_reference_data(test_deduped, customers, products)

    return train_final, test_final
