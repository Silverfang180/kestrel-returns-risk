import pandas as pd
import pytest
from kestrel_returns.loader import load_data, deduplicate_orders, load_and_prepare, TRAIN_USECOLS

def test_loader_counts():
    train_final, test_final = load_and_prepare()
    assert len(train_final) == 10504, f"Expected 10504 deduped train rows, got {len(train_final)}"
    assert len(test_final) == 2096, f"Expected 2096 test rows, got {len(test_final)}"
    assert train_final["returned"].sum() == 1200, f"Expected 1200 returns, got {train_final['returned'].sum()}"

def test_deduplication():
    train, test, _, _ = load_data()
    raw_train_len = len(train)
    assert raw_train_len == 11155, f"Expected 11155 raw train rows, got {raw_train_len}"

    train_deduped = deduplicate_orders(train)
    assert len(train_deduped) == 10504, "Deduped train should have 10504 rows"
    assert raw_train_len - len(train_deduped) == 651, "Expected 651 duplicates removed"

    assert train_deduped["order_id"].nunique() == len(train_deduped), "Duplicate order_ids remain"

    raw_test_len = len(test)
    test_deduped = deduplicate_orders(test)
    assert raw_test_len == len(test_deduped), "Test set should not have duplicates removed"
    assert len(test_deduped) == 2096, "Expected 2096 test rows"

def test_joins():
    train_final, test_final = load_and_prepare()

    assert "shield_member" in train_final.columns
    assert "family" in train_final.columns
    assert "shield_member" in test_final.columns
    assert "family" in test_final.columns

    assert not train_final["shield_member"].isna().any(), "Missing shield_member after join"
    assert not train_final["family"].isna().any(), "Missing family after join"
    assert not test_final["shield_member"].isna().any(), "Missing shield_member after join"
    assert not test_final["family"].isna().any(), "Missing family after join"

def test_no_conflicting_labels():
    train, _, _, _ = load_data()
    # Check if any order_id has multiple rows with different 'returned' values
    grouped = train.groupby("order_id")["returned"].nunique()
    assert (grouped == 1).all(), "Found order_ids with conflicting labels!"

def test_crm_retention():
    # Construct a dummy dataframe to test deduplicate_orders directly
    data = {
        "order_id": ["A", "A", "B", "B"],
        "source": ["partner_feed", "crm", "crm", "partner_feed"],
        "returned": [1, 0, 1, 1]
    }
    df = pd.DataFrame(data)
    deduped = deduplicate_orders(df)

    assert len(deduped) == 2
    # Order A should have kept the CRM row, which had returned = 0
    assert deduped.loc[deduped["order_id"] == "A", "returned"].iloc[0] == 0
    # Order B should have kept the CRM row, which had returned = 1
    assert deduped.loc[deduped["order_id"] == "B", "returned"].iloc[0] == 1

def test_delivery_note_exclusion():
    assert "delivery_note" not in TRAIN_USECOLS

    train, _, _, _ = load_data()
    assert "delivery_note" not in train.columns
