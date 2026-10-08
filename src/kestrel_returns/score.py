import pandas as pd
import joblib
from pathlib import Path

from kestrel_returns.loader import load_and_prepare
from kestrel_returns.features import build_features

ARTIFACTS_DIR = Path(__file__).parent.parent.parent / "artifacts"
PREDICTIONS_PATH = Path(__file__).parent.parent.parent / "predictions.csv"

def generate_predictions():
    _, test_df = load_and_prepare()

    # Validation tests for input
    assert len(test_df) == 2096, f"Expected 2096 test rows, got {len(test_df)}"

    X_test = build_features(test_df)

    # Load model
    model_path = ARTIFACTS_DIR / "model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Model artifact not found at {model_path}")

    pipeline = joblib.load(model_path)

    # Predict probabilities (positive class)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    # Create output dataframe
    predictions = pd.DataFrame({
        "order_id": test_df["order_id"],
        "score": y_prob
    })

    # Output validations
    assert len(predictions) == 2096, "Output must have 2096 rows"
    assert predictions["order_id"].nunique() == 2096, "Output order_ids must be unique"
    assert set(predictions["order_id"]) == set(test_df["order_id"]), "Output order_ids must match test order_ids"
    assert predictions["score"].notna().all(), "Scores must be finite (not NA)"
    assert (predictions["score"] >= 0).all() and (predictions["score"] <= 1).all(), "Scores must be in [0, 1]"

    # Save
    predictions.to_csv(PREDICTIONS_PATH, index=False)
    print(f"Successfully wrote {len(predictions)} predictions to {PREDICTIONS_PATH}")

if __name__ == "__main__":
    generate_predictions()
