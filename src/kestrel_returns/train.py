import pandas as pd
import joblib
import json
import sklearn
import sys
from pathlib import Path
from datetime import datetime

from kestrel_returns.loader import load_and_prepare
from kestrel_returns.features import build_features, REQUIRED_FEATURES
from kestrel_returns.model import get_model_pipeline

ARTIFACTS_DIR = Path(__file__).parent.parent.parent / "artifacts"

def train_and_save():
    ARTIFACTS_DIR.mkdir(exist_ok=True)

    train_df, _ = load_and_prepare()

    X = build_features(train_df)
    y = train_df["returned"]

    pipeline = get_model_pipeline("lr")
    pipeline.fit(X, y)

    # Save the model
    model_path = ARTIFACTS_DIR / "model.joblib"
    joblib.dump(pipeline, model_path)

    # Extract metadata for deterministic reasons
    rates = {}

    for cat_feat in ["payment_mode", "shield_member", "family", "sales_channel", "is_gift"]:
        cat_rates = train_df.groupby(cat_feat)["returned"].mean().to_dict()
        rates[cat_feat] = {str(k): float(v) for k, v in cat_rates.items()}

    metadata = {
        "model_version": "1.0.0",
        "training_rows": len(train_df),
        "feature_list": REQUIRED_FEATURES,
        "python_version": sys.version.split()[0],
        "sklearn_version": sklearn.__version__,
        "training_date_range": {
            "start": str(train_df["order_placed_at"].min()),
            "end": str(train_df["order_placed_at"].max())
        },
        "threshold": 0.112,
        "historical_rates": rates,
        "training_time_utc": datetime.utcnow().isoformat()
    }

    with open(ARTIFACTS_DIR / "model_meta.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Model saved to {model_path}")
    print(f"Metadata saved to {ARTIFACTS_DIR / 'model_meta.json'}")

if __name__ == "__main__":
    train_and_save()
