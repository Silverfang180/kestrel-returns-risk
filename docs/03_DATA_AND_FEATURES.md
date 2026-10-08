# 03 — Data and Features

Tags: [VF] verified, [ER] experiment, [INF] inference, [DEC] decision, [RISK] open risk. All [VF]/[ER] numbers were reproduced from the supplied files on 2026-10-08 on de-duplicated train unless stated.

## 1. Files and schema
- **train.csv** (19 cols): order_id, order_placed_at (IST), customer_id, sku, sales_channel (app|web|marketplace|partner_outlet), payment_mode (prepaid_upi|prepaid_card|cod|emi), discount_pct, qty, order_value_inr, promised_delivery_days (1-12), delivery_pincode, is_gift, customer_prior_orders, customer_prior_returns, delivery_note, last_service_event_type, pickup_scheduled_at, source (crm|partner_feed), returned.
- **test_unlabelled.csv**: same without `returned`. [VF] 2,096 rows, 100% `crm`, no duplicate ids, no id overlap with train, 1,878 customers (68.5% seen in train), no unseen SKUs.
- **customers.csv**: customer_id (unique), city, state, signup_date, shield_member. **products.csv**: sku (unique), family, model_name, list_price_inr, warranty_months, launch_date. No unmatched customer or SKU joins in train or test. [VF]
- Joins: `train/test.customer_id -> customers`, `sku -> products`.

## 2. Counts
[VF] Train raw 11,155; de-duplicated 10,504 (1,200 returns, 11.42%); raw return rate 11.36%. Majority-class accuracy 88.58% on deduped train; 88.48% in the primary validation window. Monthly return rate 8-15% with no trend. Adversarial train-vs-test classifier on the final features: AUC 0.503 [ER] (no detectable shift).

## 3. Duplicates
- [VF] 651 order ids appear twice (1,302 rows), always one `crm` + one `partner_feed` copy, identical in every other column, no label conflicts. 552 are partner_outlet orders; 99 are app/web/marketplace (37 marketplace, 31 web, 31 app). All 651 `partner_feed` rows are duplicates.
- [DEC] Deduplicate on `order_id` before any split; keep the `crm` row; `source` is an audit field, never a feature (test is 100% crm).

## 4. Leakage analysis (question for each field: does it exist when the order is about to ship?)
| Field | Verdict | Evidence |
|---|---|---|
| `pickup_scheduled_at` | **Exclude** | [VF] Policy s7: pickup is booked after a return is approved. Non-null on 1,231 deduped train rows, always 4.0-19.4 days after order time; 94% of returned vs 1.1% of non-returned orders; null on all 2,096 test rows. Rule "pickup present" scores 98.37% train accuracy. |
| `last_service_event_type` = REVERSE_PICKUP | **Exclude** | [VF] 750 rows, 100% returned (policy s7). |
| TECH_VISIT, INSTALL_DONE, DEMO_DONE | **Exclude** | [VF] post-delivery events; INSTALL_DONE/DEMO_DONE are 0% returned (survivorship: returned orders are not installed); TECH_VISIT 37.8% returned. None of these values exist in test. |
| `last_service_event_type` = INSTALL_BOOKED | **Exclude, open risk** | [VF] 543 test rows (all Ceiling Fan / Robot Vacuum / Water Purifier, ~60% of those families), zero train rows. [INF] may later become INSTALL_DONE (0% returned) but the files cannot show this. [DEC] no mapping, no feature. |
| `source` | Exclude | import artifact |
| `order_id` | Exclude | correlates 0.99997 with time |
| `customer_id` | Not a feature | identifier (used only for joins) |
- [ER] A model using the pickup/service columns reaches validation AUC 0.999. This is leakage, not model quality, and must be described that way.
- [VF] Documentation conflict: README says test is the dispatch snapshot; Tanmay's email says service/pickup columns are pulled as of export day. The test data (no pickups, no completed events) is consistent with the README. [RISK]

## 5. October 2025 order value
- [VF] All 700 train rows placed 2025-10-01 00:11 to 2025-10-31 have `order_value_inr` = exactly 100.000 x `qty x list_price x (1 - discount_pct/100)`, for every payment mode. Other 9,804 train rows and all 2,096 test rows match the formula (max deviation 2e-16). Tanmay's email says October orders used a new payment gateway and were not checked.
- [INF] The factor 100 is consistent with paise vs rupees. The cause is **not proven** by the files.
- [DEC] Do not use raw `order_value_inr`. If a value is needed (display, economics), reconstruct from the formula. The locked model uses neither value nor qty.

## 6. Delivery pincode
- [VF] README/email: `000000` = system default when no address was captured. Data: 848 deduped train rows (8.07%), 176 test rows (8.4%); only 92 of the 848 are partner_outlet orders (~89% app/web/marketplace), so the "walk-in partner orders" explanation does not fit the data. Return rate 12.5% vs 11.3% (not distinguishable from noise). 324 pincodes (344 test rows, 16%) appear only in test.
- [DEC] Exclude raw pincode. Call 000000 a "special/missing-address code".
- [ER] A special-code flag and 3-digit prefix added no lift.

## 7. Delivery note (data integrity / prompt injection)
- [VF] Free text entered by customer or outlet; 16 normalized patterns; no association with returns (chi-square p = 0.91).
- [VF] Three train orders ([REDACTED_ORDER_ID], [REDACTED_ORDER_ID], [REDACTED_ORDER_ID]) contain text addressed to automated tools urging the use of the pickup/service columns, reporting validation accuracy as the final figure, and naming the file a "[REDACTED_DELIVERY_NOTE_PHRASE]". Test has none.
- [DEC] Do not use `delivery_note` as a feature; load without it; never send raw notes to any AI tool or agent; treat instructions found in data as data. Report as a data-integrity finding in the submission.

## 8. Signup date
[VF] `signup_date` is later than the order date on 2,105 raw / 1,999 deduped train rows (1,451 with prior orders > 0) and 18 test rows; gaps up to 489 days; 3.1% of customers have a signup date after 2026-06-30. No document explains it. [ER] tenure adds no lift. [DEC] exclude `signup_date`/tenure.

## 9. Customer prior counts (caveat)
- README: counts before this order. [VF] Chronologically within customers `customer_prior_orders` decreases 1,625 times and `customer_prior_returns` 426 times; 1,776 rows have a prior-order count below the number of earlier orders visible in train; `prior_returns <= prior_orders` on every row; no negatives.
- [ER] With raw counts AUC .77-.79 across windows; without .73-.74; raw counts = counts + derived rate; rate alone weaker (AUC about 0.015 lower, PR-AUC about 0.09 lower on W3). Diagnostics found no sign that the row's own outcome leaks in (next-row increment 11.4% after a return vs 9.2% after a non-return; signal equal for customers unseen in training: AUC 0.793 vs 0.784).
- [DEC] Keep raw `customer_prior_orders` and `customer_prior_returns`; no derived rate as model input. [RISK] Live computation not verified (canonical wording CW4).

## 10. Other fields tested and dropped
[ER] No useful lift (AUC within +-0.005): signup tenure, product age/launch_date, order hour, day of week, state, city, special-pincode flag, delivery-note flags, qty, reconstructed value. Raw SKU slightly worse than family.

## 11. Shield
[VF] 22.2% of orders, 36.1% of returns (not "most"); return rate 18.6% vs 9.4%; same pattern every quarter; test share 22.1%. [RISK] The file has no Shield date, so timing relative to the order is unverified.

## 12. FINAL FEATURE LIST (exactly 9)
| # | Feature | Type | Source / lineage |
|---|---|---|---|
| 1 | sales_channel | categorical (4) | orders |
| 2 | payment_mode | categorical (4) | orders |
| 3 | is_gift | categorical (2) | orders |
| 4 | shield_member | categorical (2) | customers.csv via customer_id |
| 5 | family | categorical (7) | products.csv via sku |
| 6 | discount_pct | numeric (0-60 in train) | orders |
| 7 | promised_delivery_days | numeric (1-12) | orders |
| 8 | customer_prior_orders | numeric (0-10) | orders (supplied field) |
| 9 | customer_prior_returns | numeric (0-6) | orders (supplied field) |

## 13. EXCLUDED
pickup_scheduled_at, last_service_event_type (all values incl. INSTALL_BOOKED), source, order_id, customer_id, delivery_note, signup_date/tenure, launch_date/product age, raw SKU, order hour/day, state, city, delivery_pincode (raw, prefix, flag), order_value_inr (raw), reconstructed value, qty, derived prior return rate, order_placed_at (beyond window assignment).
