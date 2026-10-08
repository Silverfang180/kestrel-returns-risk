# 07 — Implementation Plan (for Antigravity)

Rules: follow docs; do not add features, libraries beyond the minimal set (pandas, numpy, scikit-learn, joblib, fastapi, uvicorn, pydantic, pytest, httpx), LLMs, databases, or auth. Never open or print `delivery_note`. Never commit `data/`. Use `usecols` when reading CSVs. If code or data contradict these docs, stop and report; do not silently change a decision.

## Step 1 — Repository and data loading
- Create layout per 02; `.gitignore` (data/, all *.csv with no exceptions, predictions*, __pycache__, .venv). Do not create or commit `reference/sku_family.csv` or any sku-to-family file: OQ3 is open. `family` is joined from the local, git-ignored `data/products.csv` in training/validation/batch scripts only. `requirements.txt` pinned (record the Python and sklearn versions used to train; local analysis used sklearn 1.8.0).
- `loader.py`: read train/test/customers/products from `data/` with explicit `usecols` (exclude delivery_note, pickup_scheduled_at, last_service_event_type, source after dedup; read source only to choose the crm row). Read delivery_pincode as str if read at all.
- Acceptance: train 11,155 -> 10,504 rows after dedup; 1,200 returns; test 2,096; no join NaNs.

## Step 2 — Deduplication
- Sort so `crm` precedes `partner_feed`; `drop_duplicates('order_id', keep='first')`; assert 651 removed pairs and no label conflicts; assert test unchanged.

## Step 3 — Feature construction
- Join shield_member and family; build exactly the 9 features; leakage guard: assert the feature frame columns equal the locked list and none of the excluded names appear anywhere in the model input; unit test fails on any extra column.

## Step 4 — Preprocessing and model
- `ColumnTransformer` (OneHotEncoder handle_unknown='ignore'; StandardScaler) + `LogisticRegression(C=0.5, max_iter=3000, random_state=0)`.

## Step 5 — Validation
- `validate.py`: W1-W3 as in 05; write aggregate tables to `reports/` (AUC, PR-AUC, accuracy, precision, recall, F1, Brier, calibration slope/intercept, confusion matrices, HGB comparison with same features, threshold table, top-k, stability table, error analysis by segment). No row-level output.
- Acceptance (tolerance +-0.003 AUC/PR-AUC, +-0.002 Brier): LR W1/W2/W3 AUC .769/.776/.788, PR-AUC .346/.392/.418, Brier .0842/.0868/.0844; HGB W3 AUC .772, PR-AUC .389; W3 threshold row at 0.112: flagged 31.2%, precision .256, recall .694, net Rs 38,590 (+-1%). Any larger deviation: stop and report.

## Step 6 — Final model
- Fit on all 10,504 deduped train rows; save `artifacts/model.joblib`; write `model_meta.json` (feature list, versions, row count, date range, historical group return rates from train as aggregates, threshold constants, validation summary).

## Step 7 — predictions.csv
- Score the 2,096 test rows; write `order_id,score` with the sample_submission header and exactly the test order_ids. Assert count, uniqueness, id set equality, finite values in [0,1]. Do not commit it and do not push it to GitHub (OQ1); it stays local and is delivered through the submission channel.

## Step 8 — API
- Implement per 02: `/predict`, `/health`, `/`. `family` is a required request field; do not add sku handling or any lookup file. Reasons from contributions; fixed templates. Polite 422/503 handling. Tests: valid record, each invalid enum, prior_returns > prior_orders, ignored fields listed, deterministic output, no network access.

## Step 9 — UI
- One static HTML file calling `/predict`; shows score, action, reasons, caveats, friendly errors; works with no external assets.

## Step 10 — Tests
- Unit: loader dedup, leakage guard, feature list, reasons, threshold constant; integration: API; smoke: train->score reproducibility (same seed same score).

## Step 11 — Documentation
- README: clean-machine steps, data placement (`data/` not committed), reproduce validation, start service, limitations, honest cost statement (Rs 0 per prediction in paid calls; no API used).
- Evidence report in `reports/`; memo, recording script outline, submission-form.md drafted by humans from docs 04-06.

## Step 12 — Final QA
- Fresh venv install and run; port 8000 serves UI; predictions.csv checks; `git ls-files` contains no CSV data, no raw rows, no delivery_note text; grep for excluded column names in the model path; run full tests; update PROJECT_STATE.md and PROMPT_LOG.md.
