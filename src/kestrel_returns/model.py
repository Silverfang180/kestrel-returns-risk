from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

CATEGORICAL_FEATURES = ["sales_channel", "payment_mode", "is_gift", "shield_member", "family"]
NUMERIC_FEATURES = ["discount_pct", "promised_delivery_days", "customer_prior_orders", "customer_prior_returns"]

def get_model_pipeline(algorithm="lr"):
    if algorithm == "lr":
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
                ("num", StandardScaler(), NUMERIC_FEATURES)
            ]
        )
        clf = LogisticRegression(C=0.5, max_iter=3000, random_state=42)
    elif algorithm == "hgb":
        from sklearn.preprocessing import OrdinalEncoder
        from sklearn.ensemble import HistGradientBoostingClassifier
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CATEGORICAL_FEATURES),
                ("num", "passthrough", NUMERIC_FEATURES)
            ]
        )
        clf = HistGradientBoostingClassifier(
            max_depth=3, learning_rate=0.05, max_iter=150, min_samples_leaf=50, l2_regularization=1.0, random_state=42,
            categorical_features=[0, 1, 2, 3, 4]
        )
    else:
        raise ValueError(f"Unknown algorithm {algorithm}")

    return Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", clf)
    ])
