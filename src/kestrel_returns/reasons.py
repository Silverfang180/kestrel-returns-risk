import numpy as np

def generate_reasons(pipeline, X_row, model_meta):
    """
    Generate deterministic reasons based on model coefficients.
    X_row should be a DataFrame with exactly 1 row, containing the 9 features.
    """
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]

    coefs = classifier.coef_[0]

    cat_transformer = preprocessor.transformers_[0][1]
    cat_features = preprocessor.transformers_[0][2]
    num_features = preprocessor.transformers_[1][2]

    cat_names = cat_transformer.get_feature_names_out(cat_features)
    feature_names = list(cat_names) + list(num_features)

    X_transformed = preprocessor.transform(X_row)

    contributions = []

    rates = model_meta.get("historical_rates", {})

    for i, name in enumerate(feature_names):
        val = X_transformed[0, i]
        contrib = coefs[i] * val

        # For categoricals, val is either 1 or 0. We only care about the active categories.
        if abs(contrib) > 0.0001 and val != 0:
            orig_feature = None
            orig_value = None
            if name in num_features:
                orig_feature = name
                orig_value = X_row[name].iloc[0]
            else:
                for c in cat_features:
                    if name.startswith(c + "_"):
                        orig_feature = c
                        orig_value = X_row[c].iloc[0]
                        break

            if orig_feature:
                direction = "raises" if contrib > 0 else "lowers"
                text = _format_reason(orig_feature, orig_value, direction, rates)

                contributions.append({
                    "text": text,
                    "direction": direction,
                    "contribution": float(contrib),
                    "abs_contrib": float(abs(contrib))
                })

    # Sort by absolute contribution and take top 4
    contributions.sort(key=lambda x: x["abs_contrib"], reverse=True)
    top_4 = contributions[:4]

    # Remove abs_contrib from output
    for r in top_4:
        del r["abs_contrib"]

    return top_4

def _format_reason(feature, value, direction, rates):
    if feature == "payment_mode":
        rate = rates.get("payment_mode", {}).get(str(value), 0)
        if direction == "raises":
            return f"{str(value).replace('_', ' ').capitalize()} orders return more often (historical rate {rate:.1%})."
        else:
            return f"{str(value).replace('_', ' ').capitalize()} orders return less often (historical rate {rate:.1%})."

    elif feature == "shield_member":
        if str(value) == "Y" and direction == "raises":
            return "Shield member: higher return rate in past data (not a reason to hold)."
        return f"Shield member status ({value}) {direction} risk."

    elif feature == "customer_prior_returns":
        return f"Customer has {value} previous returns."

    elif feature == "customer_prior_orders":
        return f"Customer has {value} previous orders."

    elif feature == "family":
        return f"Product family '{value}' {direction} risk."

    elif feature == "discount_pct":
        if direction == "raises":
            return f"High discount ({value}%) increases risk."
        else:
            return f"Low discount ({value}%) decreases risk."

    elif feature == "promised_delivery_days":
        return f"Promised delivery of {value} days {direction} risk."

    else:
        return f"{feature} = {value} {direction} risk."
