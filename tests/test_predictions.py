import pandas as pd
import numpy as np
import joblib
import pytest
from pathlib import Path

from kestrel_returns.loader import load_and_prepare
from kestrel_returns.features import build_features

ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"
PREDICTIONS_PATH = Path(__file__).parent.parent / "predictions.csv"
DATA_DIR = Path(__file__).parent.parent / "data"

def test_predictions_csv():
    assert PREDICTIONS_PATH.exists(), "predictions.csv does not exist"

    preds = pd.read_csv(PREDICTIONS_PATH)
    test_unlabelled = pd.read_csv(DATA_DIR / "test_unlabelled.csv", usecols=["order_id"])

    # 2096 rows
    assert len(preds) == 2096, f"Expected 2096 predictions, got {len(preds)}"

    # Header check
    assert list(preds.columns) == ["order_id", "score"]

    # Unique IDs
    assert preds["order_id"].nunique() == len(preds), "Prediction IDs are not unique"

    # ID set equality
    assert set(preds["order_id"]) == set(test_unlabelled["order_id"]), "Prediction IDs do not match test set"

    # Scores
    assert np.isfinite(preds["score"]).all(), "Scores must be finite"
    assert (preds["score"] >= 0).all() and (preds["score"] <= 1).all(), "Scores must be in [0, 1]"

def test_deterministic_predictions():
    # Load model and run twice to ensure deterministic output
    model_path = ARTIFACTS_DIR / "model.joblib"
    assert model_path.exists(), "model.joblib missing"

    pipeline = joblib.load(model_path)

    _, test_df = load_and_prepare()
    X = build_features(test_df.head(10))

    preds1 = pipeline.predict_proba(X)[:, 1]
    preds2 = pipeline.predict_proba(X)[:, 1]

    np.testing.assert_array_equal(preds1, preds2, "Predictions are not deterministic!")
