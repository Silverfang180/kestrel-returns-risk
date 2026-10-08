# Kestrel Home — Returns Risk (Variant A)

This project implements a pre-dispatch returns-risk scoring service for Kestrel Home Appliances.

Kestrel Home Appliances is based in Pune and sells through direct online channels and approximately 380 service-partner outlets. The original client ask was to predict returns before shipment with a target of 95% accuracy to automatically hold dispatch on flagged orders.

However, honest chronological validation demonstrated a best accuracy of approximately 89.6% (compared with an ~88.5% do-nothing baseline). More importantly, accuracy is an ineffective metric because the return rate is only ~11.5%, so a high-accuracy model can still miss most returns.

Instead of automatically blocking orders, this service:
1. Accepts a single order record.
2. Predicts the probability that the order will be returned.
3. Gives deterministic human-readable reasons for the score.
4. Uses an economic threshold (0.112) to recommend a confirmation call.
5. Does NOT automatically hold, cancel, reject, or block an order.

## Data and Features

The training dataset consisted of 11,155 raw rows. After strict deduplication (where CRM rows were retained over partner-feed rows without conflicting labels), there were 10,504 usable rows containing 1,200 returns (~11.42%).

**Final 9 Features:**
* **Categorical:** `sales_channel`, `payment_mode`, `is_gift`, `shield_member`, `family`
* **Numeric:** `discount_pct`, `promised_delivery_days`, `customer_prior_orders`, `customer_prior_returns`

**Critical Exclusions & Pushbacks:**
* **Leakage:** Fields such as `pickup_scheduled_at`, `last_service_event_type`, and service/pickup outcomes were rigorously excluded. These occur *after* the business outcome. A model using these post-outcome fields reached an unrealistic ~0.999 validation AUC, identifying them as severe target leakage.
* **Delivery Note:** The `delivery_note` field was completely excluded. The analysis found no useful return association, and it contained instructions aimed at automated tools. The field is treated strictly as data and is never processed, summarized, logged, embedded, or passed to an AI system.
* **Order Value Anomaly:** October 2025 contained an unexplained anomaly where `order_value_inr` was exactly 100x the expected checkout formula. Rather than applying an unverified correction, raw `order_value_inr` was dropped entirely.
* **Customer Prior Fields:** `customer_prior_orders` and `customer_prior_returns` improved validation performance and were retained. However, some chronological records showed decreasing prior counts, meaning their live-system timing/semantics have not been independently verified. They must be treated as an important production caveat.

## Modeling & Validation

The service uses a standard **Logistic Regression** model (`C=0.5`, fixed random state, `max_iter >= 3000`). Preprocessing is handled cleanly via a scikit-learn Pipeline and `ColumnTransformer` (`OneHotEncoder(handle_unknown="ignore")` and `StandardScaler`).

**Chronological Validation (not random split):**
* **W1:** Train April–September 2025, Validate October–December 2025
* **W2:** Train through December 2025, Validate January–March 2026
* **W3 (Primary):** Train through March 2026, Validate April–June 2026

### Validation Results (Logistic Regression)

| Metric | W1 | W2 | W3 (Primary) |
|---|---|---|---|
| ROC-AUC | 0.769354 | 0.775618 | 0.788113 |
| PR-AUC | 0.346207 | 0.392838 | 0.418062 |
| Brier Score | 0.0842287 | 0.0867628 | 0.0844067 |
| Accuracy @ 0.5 | 0.89433 | 0.893227 | 0.895579 |
| Precision @ 0.5 | 0.56098 | 0.738095 | 0.734694 |
| Recall @ 0.5 | 0.10222 | 0.125506 | 0.146939 |
| F1 Score @ 0.5 | 0.17293 | 0.21453 | 0.244898 |

*Note: 95% accuracy was NOT demonstrated.*

**Model Comparison:**
A gradient-boosted alternative (HistGradientBoosting) was also evaluated, yielding ROC-AUCs of ~0.7621 (W1), ~0.7688 (W2), and ~0.7716 (W3). Logistic Regression was at least as good as the gradient-boosted alternative and was selected because it is simpler and easier to explain.

## Economics & Operating Threshold

The model does not classify at 0.5. Instead, it flags orders at or above an economic break-even probability threshold of **0.112**.

**Economic Calculation (Pilot Assumptions):**
* Completed confirmation call cost = ₹45
* Estimated return prevention rate on called orders = 35%
* Cost of one return = ₹1,150
* Break-even risk: ₹45 / (0.35 × ₹1,150) = 0.1118 ≈ 0.112

At threshold 0.112 on the W3 validation window (2,126 orders, 245 returns; validation-window estimates, not guarantees):
* Flagged share: 31.04%
* Precision: 25.76%
* Recall: 69.39%
* Estimated net value: approximately ₹38,725 over the validation window

**Monthly Economic Interpretation (extrapolation, not a guarantee):**
Scaling the W3 validation-window estimates to approximately 700 orders/month (an extrapolation from validation results and pilot assumptions), the 0.112 threshold translates to:
* Roughly 218 orders would be called
* Roughly 20 returns could be prevented under the 35% pilot assumption
* Approximately 61 returns would remain
* Estimated net value is about ₹12,750/month under the stated assumptions (₹38,725 scaled by 700 / 2,126).
*Important: These are extrapolated validation estimates based on policy assumptions, not guaranteed savings. The 35% prevention rate comes from a pilot and is an operating assumption; it is not causally proven by this model and may not transfer to the highest-risk orders.*

**Error Analysis (W3 @ 0.112 Threshold):**
* **False Negatives:** Missed roughly 75 out of 245 actual returns. Many had no prior returns, ~85% were non-Shield members, and ~72% were prepaid/EMI. The weakest area identified was first-time prepaid customers.
* **False Positives:** Flagged 490 non-returning orders (660 flagged, 170 of them true returns). Approximately 38% were Shield members, 56% were COD, and 24.5% had a prior-return history.

## API & UI

**API Configuration:**
The service exposes three endpoints via FastAPI:
* `GET /health`
* `POST /predict`
* `GET /` (Static UI)

`POST /predict` accepts one order record (JSON) and validates enums, numeric fields, and logical prior-count relationships. Extra ignored fields are safely discarded. If the model artifacts are missing, the service still starts, `GET /health` reports `unhealthy`, and `POST /predict` returns HTTP 503 rather than a fake prediction. A corrupt or incompatible artifact is not handled that way: startup can fail while loading it, so artifacts should be regenerated with `train.py` in the same environment.
The API returns a risk score/probability, a recommendation flag, deterministic human-readable reasons, and a list of ignored fields when applicable. No outbound network calls, external paid API keys, or LLMs are used by the product.

**UI:**
A single static web screen at `GET /` calls the `/predict` endpoint and presents the score, recommendation, and reasons.

## Project Structure

```text
docs/                  # Project specifications, architecture, and context decisions
reports/               # Generated validation, calibration, and economic reports
src/kestrel_returns/   # Application source code (loader, features, model, API, etc.)
tests/                 # Automated test suite
requirements.txt       # Python dependencies
README.md              # Project documentation (this file)
```

## Reproducibility

**1. Create a virtual environment & install requirements:**
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Unix-like
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Local Data Placement:**
The training, validation and scoring workflow requires these four private, supplied Kestrel task files:
```text
data/train.csv
data/test_unlabelled.csv
data/customers.csv
data/products.csv
```
They are not included in the public repository (`data/` and `*.csv` are git-ignored) because of the data-handling policy. Without all four files, `validate.py`, `train.py` and `score.py` stop with a file-not-found error.

**What a public clone can and cannot do:**
* A public clone alone installs successfully and can start the service (`python run.py`), and the UI loads.
* A public clone alone contains neither the private Kestrel dataset nor a fitted model artifact. It cannot reproduce validation, training or `predictions.csv`, and `POST /predict` returns HTTP 503 until the artifacts exist.
* With the four supplied files in `data/`, the full workflow below reproduces the validation reports, the model artifacts, `predictions.csv` and the test suite.
* With previously generated local artifacts (and no data), the service starts healthy and `POST /predict` works.

**3. Run Validation & Training:**
`artifacts/model.joblib` and `artifacts/model_meta.json` are intentionally git-ignored and are created locally by `train.py`. They must exist locally before `/predict` can return model predictions, so a clean checkout should train the model before starting the service. Note that `validate.py` rewrites the generated files in `reports/`, including the tracked `reports/validation_summary.json` (differences are floating-point noise).
```bash
# Windows
$env:PYTHONPATH="src"
python src/kestrel_returns/validate.py
python src/kestrel_returns/train.py
python src/kestrel_returns/score.py

# Unix-like
export PYTHONPATH="src"
python src/kestrel_returns/validate.py
python src/kestrel_returns/train.py
python src/kestrel_returns/score.py
```

**4. Run Automated Tests:**
The implementation currently has 19 automated tests covering the API, feature handling, loaders, and prediction behavior. All 19 pass once the four data files are in `data/` and `train.py` and `score.py` have been run. On a public clone without the private data and artifacts, the data-dependent tests (loader, prediction-file and healthy-API tests) fail by design; the feature-contract and API-validation tests still pass.
```bash
# Windows
$env:PYTHONPATH="src"
pytest tests/

# Unix-like
export PYTHONPATH="src"
pytest tests/
```

**5. Start the API and UI:**
The recommended way to start the existing FastAPI service and static UI is using the root launcher:

```bash
python run.py
```

This starts the existing FastAPI service. The static UI is served through the same service and can be opened in a browser at `http://127.0.0.1:8000/`. The service reports `healthy` and returns model predictions only when the locally generated artifacts from step 3 are present.

*(Optional alternative, manual startup):*
```bash
# Windows
$env:PYTHONPATH="src"
uvicorn kestrel_returns.api:app --host 127.0.0.1 --port 8000

# Unix-like
export PYTHONPATH="src"
uvicorn kestrel_returns.api:app --host 127.0.0.1 --port 8000
```

## Privacy

The public repository strictly adheres to privacy constraints:
* `data/`, `artifacts/`, and `predictions.csv` are explicitly git-ignored and never committed.
* The repository does not contain raw Kestrel customer/order data, raw prediction outputs, or raw delivery-note content.
* No API keys or secrets are committed.

## AI Usage

I built this project individually and used AI tools as development assistance. AI was used for documentation support, reasoning/checking, implementation assistance, and review. I independently evaluated outputs and discarded or corrected suggestions when they conflicted with the supplied data, leakage controls, validation design, privacy requirements, or project behavior.

## Submission Links

* GitHub Repository: https://github.com/Silverfang180/kestrel-returns-risk
* Three-minute screen recording: TODO
* Public Google Drive submission folder: TODO
