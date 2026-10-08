import pandas as pd
import pytest
from kestrel_returns.features import build_features, REQUIRED_FEATURES, EXCLUDED_FIELDS, check_exclusion_guard

def test_check_exclusion_guard():
    # Should not raise
    check_exclusion_guard(["some_col", "another_col"])

    # Should raise
    for field in EXCLUDED_FIELDS:
        with pytest.raises(ValueError, match=f"Excluded field '{field}' found"):
            check_exclusion_guard(["good_col", field, "another_good_col"])

def test_build_features_success():
    # Create dummy dataframe with exactly required features + some random safe extra features
    data = {f: [1, 2] for f in REQUIRED_FEATURES}
    data["safe_extra_column"] = [3, 4]
    df = pd.DataFrame(data)

    X = build_features(df)

    # Check shape and columns
    assert len(X) == 2
    assert list(X.columns) == REQUIRED_FEATURES
    assert "safe_extra_column" not in X.columns

def test_build_features_missing_required():
    data = {f: [1, 2] for f in REQUIRED_FEATURES[:-1]} # Missing last one
    df = pd.DataFrame(data)

    with pytest.raises(KeyError):
        build_features(df)

def test_privacy_exclusions():
    data = {f: [1, 2] for f in REQUIRED_FEATURES}
    for field in EXCLUDED_FIELDS:
        data[field] = [1, 2]
    df = pd.DataFrame(data)

    # building features should drop them
    X = build_features(df)

    for field in EXCLUDED_FIELDS:
        assert field not in X.columns, f"{field} leaked into feature matrix!"
