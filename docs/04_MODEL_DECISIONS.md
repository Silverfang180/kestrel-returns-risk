# 04 — Model Decisions

Format: Decision / Evidence / Rejected / Impact / Open risk. Numbers are defined in 05.

## Canonical wordings (reuse verbatim; do not paraphrase into contradictions)

* **CW1 (95% target):** "95% accuracy was not demonstrated under honest time-based validation; the best demonstrated accuracy was about 89.6%, against an approximately 88.5% do-nothing baseline. Accuracy is misleading here because only about 11.5% of orders are returned."

* **CW2 (LR vs HGB):** "Logistic Regression was at least as good as the gradient-boosted alternative and was selected because it is simpler and easier to explain."

* **CW3 (threshold):** "0.112 is the economic break-even probability, 45 / (0.35 x 1,150), not a validation-optimized threshold."

* **CW4 (prior fields):** "customer_prior_orders and customer_prior_returns are described as pre-order counts but do not behave like a running ledger in the supplied data. Tests found no sign that the row's own outcome leaks in, and they improve validation AUC from about 0.73-0.74 to about 0.77-0.79. How the live system computes them at dispatch has not been verified and should be confirmed before operational reliance."

* **CW5 (leakage):** "pickup_scheduled_at and post-delivery service events are recorded after a return begins; a model using them looks near-perfect (AUC about 0.999) because it reads the outcome, not because it predicts it."

* **CW6 (hold economics):** "Hold economics are unresolved: the policy gives a 12% cancellation rate after a 24-hour hold but the pack contains no margin or lost-sale value, so no hold ROI is claimed."

* **CW7 (Shield):** "Shield members return more often (about 18.6% vs 9.4%) and are the highest-lifetime-value segment; we recommend a confirmation call rather than an automatic hold as the safer action. This is a business recommendation, not causal proof."

* **CW8 (hidden test):** "No hidden-test score has been observed. Expected: ROC-AUC roughly 0.75-0.80, PR-AUC roughly 0.33-0.46, accuracy at a 0.5 threshold roughly 88.5-90%, estimated from time-based validation."

* **CW9 (pincode):** "000000 is a special/missing-address code (README: default when no address was captured)."

* **CW10 (October):** "700 October 2025 rows carry order_value_inr exactly 100x the checkout formula; the cause is not proven by the files (the email mentions an unchecked new payment gateway)."

* **CW11 (delivery_note):** "Three training rows contain instructions aimed at automated tools; they were not followed and the column is not used."

## D001 Exclude post-outcome columns

**Decision:** exclude `pickup_scheduled_at` and `last_service_event_type`.

**Evidence:** policy s7, 4-19 day lag, test absence (see 03 s4).

**Rejected:** using them "because test lacks them"; mapping `INSTALL_BOOKED`.

**Impact:** honest AUC about 0.77-0.79 instead of 0.999.

**Open risk:** `INSTALL_BOOKED` may carry signal we cannot learn.

## D002 De-duplicate before splitting, keep crm copy

**Decision:** deduplicate on `order_id` before any train/validation split and keep the `crm` copy.

**Evidence:** 651 identical pairs, no label conflicts.

**Rejected:** keeping both copies (double-weights approximately 6% of rows); using `source`.

**Impact:** 10,504 training rows.

## D003 Order value

**Decision:** do not use raw `order_value_inr`; the model does not need value or `qty`.

**Evidence:** 700 October rows are exactly 100x the trusted checkout formula; qty/value ablation shows no material improvement.

**Rejected:** dividing October values by 100 and retaining the raw field.

**Impact:** the corrupted field cannot reach the model.

**Open risk:** exact technical cause of the October factor is unproven.

## D004 Feature selection (9 features)

**Decision:** use exactly the following 9 production features:

### Categorical

1. `sales_channel`
2. `payment_mode`
3. `is_gift`
4. `shield_member`
5. `family`

### Numeric

6. `discount_pct`
7. `promised_delivery_days`
8. `customer_prior_orders`
9. `customer_prior_returns`

**Evidence:** ablations on W1-W3 (see 03 and 05).

Removing `shield_member` costs approximately 0.02-0.03 AUC; removing `promised_delivery_days` costs approximately 0.02; removing `discount_pct` costs approximately 0.007-0.009.

**Rejected:** tenure, product age, hour/day, state/city, pincode flags, delivery-note flags, SKU, qty, value, reconstructed value, derived prior return rate and all post-outcome service/pickup fields.

**Impact:** small, explainable production model.

**Open risk:** ablations used the same validation windows, so feature-selection results have mild selection optimism.

## D005 Keep raw customer-prior counts

**Decision:** keep `customer_prior_orders` and `customer_prior_returns` as supplied; do not create a derived prior return-rate feature.

**Evidence:** AUC approximately 0.77-0.79 with the counts versus approximately 0.73-0.74 without them.

Paired bootstrap on W3 using the 11-feature analysis base:

* counts + rate vs none: AUC +0.047 [0.025, 0.071], PR-AUC +0.120 [0.069, 0.169];
* counts + rate vs counts only: effectively zero difference;
* rate only is weaker than counts.

**Rejected:** dropping the prior fields; using only the derived return rate; reconstructing the counts from visible order history.

**Impact:** these are the largest single source of predictive lift.

**Open risk:** their supplied values do not behave like a clean running ledger. Production/live computation at dispatch has not been verified. Use CW4. A no-prior fallback is approximately 0.73-0.74 AUC.

## D006 Logistic Regression over HGB

**Decision:** use Logistic Regression with `C=0.5` as the production model.

**Evidence:** Logistic Regression has at least as good AUC and PR-AUC across W1-W3, lower Brier score in all three windows, and cleaner calibration. Paired bootstrap AUC differences overlap zero in W1/W2.

**Rejected:** HGB in the production service; larger ensembles; unnecessary model complexity.

**Impact:** simple, deterministic and easier to explain using model coefficients.

**Open risk:** use CW2 wording; do not claim that Logistic Regression clearly dominates HGB.

## D007 95% accuracy pushback

**Decision:** do not claim or manufacture a 95% accuracy result.

**Evidence:** the majority baseline is approximately 88.5%; the best demonstrated accuracy for the locked 9-feature model is about 89.6% on W3, and that threshold is selected on the validation window itself, so the maximum is optimistic.

Observed precision is approximately 58% in the top 5% and approximately 44% in the top 10%.

**Rejected:** claiming 95%; saying 95% is mathematically impossible; using leakage or invalid validation to produce a 95% figure.

**Impact:** report ROC-AUC, PR-AUC, precision/recall at the operating point, calibration and business economics instead of treating accuracy as the primary success metric.

**Canonical wording:** CW1.

## D008 Operating threshold 0.112

**Decision:** default `recommend_call` threshold = `0.112`.

**Evidence:** economic break-even arithmetic:

`45 / (0.35 x 1,150) = 0.1118 ≈ 0.112`

The threshold is stable enough across W1-W3 to support it as a reasonable operating default, and tuning for maximum validation profit added little value.

**Rejected:** selecting the threshold solely to maximize accuracy; repeatedly tuning the threshold on the primary validation window; treating 0.112 as a model-optimized threshold.

**Impact:** provides a transparent business operating rule.

**Canonical wording:** CW3.

**Open risk:** the 35% pilot prevention rate may not transfer exactly to the high-risk orders selected by the model.

## D009 Call, not hold

**Decision:** recommend confirmation calls for orders with score >= 0.112. Do not automatically hold or block orders.

**Evidence:** call economics are priced (Rs 45; approximately 35% prevention in the pilot). Hold economics are incomplete because the pack lacks the margin/lost-sale value needed to calculate reliable hold ROI. Shield is also a high-LTV segment with a higher return rate.

**Rejected:** making "hold" the automatic action requested by the stakeholder; claiming that holds are definitively harmful.

**Impact:** the system recommends a confirmation call while leaving the final decision with operations staff.

**Recommended next action:** run a 4-week confirmation-call pilot with a control group and measure actual prevented returns, completion rate, cancellations and customer complaints.

**Open risk:** pilot effect may not transfer; unanswered calls may reduce realized economics.

Use CW6 and CW7 where applicable.

## D010 No LLM / external API

**Decision:** reasons are deterministic and derived from Logistic Regression contributions. No LLM or external inference API is used.

**Evidence:** the assessment requires a clean-machine start without a paid API key; the service can produce useful employee-readable reasons directly from model coefficients.

**Rejected:** per-order LLM explanations; external inference APIs; unnecessary AI orchestration.

**Impact:** Rs 0 per prediction in paid API calls, no API key, deterministic behavior and simpler deployment.

## D011 Data handling and artifact publication

**Decision:** `data/`, raw CSVs, raw rows, raw outputs and `predictions.csv` are never committed to the public GitHub repository. `delivery_note` text is never committed or passed to an AI tool.

The fitted model artifact is required for local service operation, but its public-repository publication remains **subject to OQ2**. Keep the artifact local/untracked by default until publication is explicitly cleared.

Aggregate, non-row-level reports may be committed if they contain no customer/order-level information.

**Evidence:** policy s10 prohibits publishing customer and operational data to public repositories or sharing it beyond the engagement team.

**Rejected:** committing raw datasets; committing row-level predictions; assuming that fitted artifacts are automatically safe to publish without checking policy.

**Impact:** the public repository remains code/documentation focused while the service can still run locally from a separately supplied model artifact.

**Open risk:** OQ2 — whether the fitted artifact and aggregate metadata are permitted in the public repository.

## Canonical decision summary

The production system is therefore:

```text
Dispatch-time order
        ↓
Exact 9-feature input
        ↓
Logistic Regression (C=0.5)
        ↓
Return-risk probability
        ↓
score >= 0.112 ?
     /             \
   YES              NO
    ↓                ↓
Recommend         Standard
confirmation      dispatch
call
```

The system does not automatically hold, block or cancel orders.

The model is evaluated using chronological W1-W3 validation, with W3 as the primary window.

The model intentionally excludes all post-outcome service/pickup information and all other documented weak, corrupted, identifier, undocumented or privacy-sensitive fields.

The final business recommendation is a confirmation-call strategy rather than automatic holding, subject to the stated assumptions and limitations.
