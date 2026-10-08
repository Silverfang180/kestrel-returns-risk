# 05 — Validation and Economics

All figures [ER] unless marked; reproduced 2026-10-08 from the supplied files with the locked 9-feature design. Antigravity must reproduce them (tolerances in 07). Rs figures use policy values: return Rs 1,150; call Rs 45; prevention 35% [ASM].

## 1. Method
- Deduplicate on `order_id` first. Time-based windows; each window is scored by a model fitted only on orders **before** the window; encoders/scalers fitted on the training side only. No random split.
- W1 = Oct-Dec 2025 (train Apr-Sep 2025, 4,170 rows); W2 = Jan-Mar 2026 (train through Dec 2025, 6,252 rows); **W3 = Apr-Jun 2026, primary** (train through Mar 2026, 8,378 rows).
- Window sizes / positives / base rate: W1 2,082 / 225 / 10.8%; W2 2,126 / 247 / 11.6%; W3 2,126 / 245 / 11.5%.
- Caveat: features and models were compared on the same windows, so results are mildly optimistic. With 245 positives in W3 an AUC estimate is good to about +-0.03.

## 2. Logistic Regression (final design), per window
| Window | AUC | PR-AUC | Acc @0.5 | Prec @0.5 | Rec @0.5 | F1 @0.5 | Brier | Majority acc | Best acc over thresholds* |
|---|---|---|---|---|---|---|---|---|---|
| W1 | .769 | .346 | .8943 | .561 | .102 | .173 | .0842 | .8919 | .8953 |
| W2 | .776 | .392 | .8932 | .738 | .126 | .215 | .0868 | .8838 | .8942 |
| W3 | .788 | .418 | .8956 | .735 | .147 | .245 | .0844 | .8848 | .8956 |
*Threshold selected on the validation window itself, so optimistic. Accuracy at the 0.112 operating point is lower (W3 73.3%) because 31% of orders are flagged; accuracy is not the objective there.

Confusion matrices [[TN, FP],[FN, TP]]: W3 @0.5 [[1868,13],[209,36]]; W3 @0.112 [[1388,493],[75,170]]. W1 @0.5 [[1839,18],[202,23]]; W2 @0.5 [[1868,11],[216,31]].

## 3. LR vs HGB (same 9 features; HGB depth 3, lr 0.05, 150 iter, min leaf 50, L2 1.0)
| Window | AUC LR / HGB | PR-AUC LR / HGB | Brier LR / HGB | Paired bootstrap AUC diff (LR-HGB) 95% | PR-AUC diff 95% |
|---|---|---|---|---|---|
| W1 | .769 / .762 | .346 / .331 | .0842 / .0847 | [-0.002, 0.018] | [-0.009, 0.036] |
| W2 | .776 / .769 | .392 / .362 | .0868 / .0887 | [-0.004, 0.017] | [0.006, 0.056] |
| W3 | .788 / .772 | .418 / .389 | .0844 / .0865 | [0.007, 0.027] | [0.007, 0.055] |
HGB @0.5 W3: acc .8923, precision .711, recall .110. Decision wording: CW2.

## 4. Customer-prior ablation (LR, 11-feature base: the 9 features plus qty and value)
| Variant | W1 AUC/PR | W2 AUC/PR | W3 AUC/PR |
|---|---|---|---|
| A counts + rate | .770/.344 | .774/.393 | .788/.420 |
| B none | .732/.272 | .725/.296 | .740/.298 |
| C raw counts only | .770/.344 | .774/.392 | .788/.420 |
| D rate only | .761/.287 | .764/.330 | .772/.331 |
Paired bootstrap on W3: A-B AUC +0.047 [0.025, 0.071], PR +0.120 [0.069, 0.169]; A-C AUC 0.000, PR 0.001; D-C AUC -0.015 [-0.025, -0.008], PR -0.088 [-0.124, -0.054]. Further checks (diagnostic only): signal on customers unseen in training AUC 0.793 (n=805) vs seen 0.784 (n=1,321). The 9-feature final model without qty/value matches the 11-feature one (AUC .769/.776/.788).

## 5. Calibration (LR)
| Window | Mean predicted | Actual | Brier | Constant-baseline Brier | Slope | Intercept |
|---|---|---|---|---|---|---|
| W1 | .1076 | .1081 | .0842 | .0964 | .928 | -.125 |
| W2 | .1130 | .1162 | .0868 | .1027 | .998 | .033 |
| W3 | .1136 | .1152 | .0844 | .1020 | 1.03 | .071 |
W3 top decile predicted .427 vs observed .437. Probabilities are usable as approximate risk estimates, not guarantees. HGB W3 top decile .393 vs .441.

## 6. Threshold table (LR, W3, 2,126 orders, 245 returns; scaled to 700 orders/month)
| Prob >= | Flagged | Precision | Recall | Returns caught | Call cost Rs | Prevented (35%) | Avoided Rs | Net Rs | Net per 700 orders Rs |
|---|---|---|---|---|---|---|---|---|---|
| 5% | 63.2% | .168 | .918 | 225 | 60,435 | 78.8 | 90,562 | 30,128 | 9,920 |
| 10% | 35.8% | .235 | .731 | 179 | 34,290 | 62.6 | 72,048 | 37,758 | 12,432 |
| **11.2%** | **31.2%** | **.256** | **.694** | **170** | **29,835** | **59.5** | **68,425** | **38,590** | **12,706** |
| 15% | 22.1% | .300 | .576 | 141 | 21,150 | 49.3 | 56,752 | 35,602 | 11,722 |
| 20% | 14.9% | .347 | .449 | 110 | 14,265 | 38.5 | 44,275 | 30,010 | 9,881 |
| 25% | 10.5% | .424 | .388 | 95 | 10,080 | 33.2 | 38,238 | 28,158 | 9,271 |
| 30% | 8.3% | .492 | .355 | 87 | 7,965 | 30.4 | 35,018 | 27,052 | 8,907 |
Net = 0.35 x 1,150 x returns caught - 45 x orders flagged.
Top-k (W3): top 5% prec .585 rec .253 net Rs 20,185; top 10% .437/.380/27,848; top 20% .318/.551/35,212; top 30% .262/.682/38,508 (min score included 0.378 / 0.266 / 0.162 / 0.115).

## 7. Threshold status and stability
- **0.112 is the theoretical break-even** (45 / (0.35 x 1,150) = 0.1118), a business operating default, **not model-selected** (CW3).
- Net per 700 orders at 0.1118: W1 Rs 11,052; W2 Rs 11,699; W3 Rs 12,706. Calling everyone: W1 -1,052; W2 +1,234; W3 +969 (about break-even; value comes from choosing whom to call).
- Net curve is flat between 0.09 and 0.15. Threshold maximizing net on W1+W2 = 0.13; applied to W3 it gave Rs 12,274 vs Rs 12,706 at 0.112 — tuning adds nothing.
- W3 bootstrap (1,000 resamples) of net per 700 orders at 0.1118: median Rs 12,731, 95% interval Rs 9,720-15,729.
- Sensitivity of the break-even: at 25% prevention it is 15.7%; at 20% it is 19.6%; at Rs 600 return cost it is 21.4% (arithmetic, not experiments).

## 8. Monthly operating picture (about 700 orders/month, W3 rates; estimate not a guarantee)
About 218 calls, about 20 prevented returns, and about 61 returns remaining, with estimated net savings of about Rs 12.7k/month under the stated assumptions. (Basis: about 81 returns expected per 700 orders at an 11.5% rate; about 20 prevented; about 61 remaining. Avoided cost about Rs 22,500, call cost about Rs 9,800.) Estimate, not a guarantee.

## 9. Error analysis (W3, @0.112, aggregate)
- Missed returns: 75 of 245 (30.6%); 97% of them had no prior returns, 85% were non-Shield, 72% were prepaid/EMI orders. Low-visibility returns: orders from customers with no history and prepaid payment.
- False alarms: 493 non-returned orders flagged; 38% Shield, 56% COD, 24.5% from customers with prior returns.
- By segment (flag share / precision / recall): Shield 57.7% / .315 / .888 vs non-Shield 23.5% / .214 / .565; Robot Vacuum flag share 58.6% (return rate 18.2%), Ceiling Fan 13.4% (recall .435); COD flag 58.8%; customers with prior returns flag 69.7% / .366 / .972; customers with no prior orders AUC .750 vs .796 with prior orders.
- Interpretation: the model leans heavily on payment mode, Shield, product family and prior returns; it is weakest on first-time prepaid customers.

## 10. Hold economics (unresolved)
12% cancellation after a hold over 24h (policy s7) [VF]. No margin or lost-sale value in the pack, and no evidence a hold prevents returns [RISK]. Conditional framing only: if cancellations were unrelated to return intent, a hold on an order with return probability p breaks even when the margin lost per cancelled order equals p x 1,150 / (1 - p) (about Rs 493 at p = 0.30; average order value about Rs 8,056). This is not a result (CW6).

## 11. Hidden-test expectation (CW8)
ROC-AUC roughly 0.75-0.80; PR-AUC roughly 0.33-0.46 (assuming a 11-12% return rate); accuracy at 0.5 roughly 88.5-90%. Basis: three consistent windows, adversarial AUC 0.503, bootstrap width. If the hidden metric is unknown or INSTALL_BOOKED matters in test, the realized score may fall outside this range.
