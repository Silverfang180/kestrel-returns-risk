# 00 — Task Brief

Kestrel Home — Returns Risk (Variant A). Banao Technologies internship assessment, Task 2.
Doc date: 2026-10-08. Read ANTIGRAVITY_CONTEXT.md first.

**Evidence tags used in every doc:** `[VF]` verified fact (checked against the supplied files) · `[ER]` experimental result (our own run) · `[INF]` inference · `[DEC]` decision · `[ASM]` assumption · `[RISK]` open risk.

## 1. Business problem
- Client: Kestrel Home Appliances (Pune). Sells air fryers, mixer-grinders, water purifiers, robot vacuums, cooktops, fans, heaters direct to consumers and via ~380 service-partner outlets. [VF]
- Stakeholder: Ritu Deshpande, Head of D2C Operations. Other voices: Farhan Sheikh (Finance Controller), Meenal Joshi (Service Desk Manager), Tanmay Kulkarni (Data & IT Admin). [VF]
- Ask: a model that scores orders **before dispatch** by likelihood of return; flag and hold risky orders; "95%+ accuracy" promised to the board; "working, not a slide". [VF]
- Hard constraint from Finance: no model bill that scales per order without being told the number first. [VF]

## 2. Input files (supplied pack)
| File | Content |
|---|---|
| train.csv | 11,155 raw rows x 19 columns, 2025-04-01 to 2026-06-30, with `returned` |
| test_unlabelled.csv | 2,096 rows x 18 columns, 2026-07-01 to 2026-09-30, no `returned`; README calls it the snapshot the warehouse sees at dispatch |
| customers.csv | 9,000 customers: city, state, signup_date, shield_member |
| products.csv | 21 SKUs: family, model_name, list_price_inr, warranty_months, launch_date |
| sample_submission.csv | order_id, score (placeholder 0.5) |
| ops-policy.pdf | Policy v4.1: costs, Shield, returns process, systems/timestamps, data handling |
| email-thread.txt | Ritu, Tanmay, Farhan, Meenal |
| README.txt | Column definitions |

## 3. Required deliverables
1. `predictions.csv` — one row per test `order_id`, shape of sample_submission.csv, higher score = more likely returned. Expected score must be written down before submission (in submission-form.md).
2. Working service — one endpoint taking one order as JSON, returning model output plus employee-readable reasons; one screen calling it; starts from README on a clean machine; no paid API key.
3. Evidence it works and how often it does not.
4. One-page non-technical memo to Ritu: the decision, the number, the rupees, what to do next week.
5. Screen recording, max 3 minutes: what was tried, changed, thrown away; no slides.
6. `submission-form.md`, fully completed (GitHub URL, what was built and the number, expected score and metric, validation, pushback, what is wrong with the work/data, cost per prediction and per month at ~700 orders, what was left out, extras, AI usage, three Monday hand-off facts).

## 4. Rules and constraints
- Time box: 48 hours from receipt. No one to ask: decide, write down, explain. [VF]
- AI tools allowed; honest reporting of tools, cost, discards required. [VF]
- **Data handling (policy s10):** customer/operational data must not be published, uploaded to public repositories, or shared beyond the engagement team. [VF] => **No raw CSV, no raw rows, no raw outputs, no predictions.csv and no delivery_note text in the public GitHub repo, and no delivery_note content sent to any AI tool.** [DEC]
- If a model API is used, the product must still start and fail politely without a key. [DEC] No model API is used.

## 5. Acceptance criteria (project-level)
- predictions.csv: 2,096 rows, order_ids exactly those of test_unlabelled.csv, finite scores, row order irrelevant.
- Service starts on a clean machine from README with no key; `/predict` returns score, recommended action, reasons; UI calls it; invalid input returns a polite error.
- Documented validation reproduces the numbers in 05_VALIDATION_AND_ECONOMICS.md within tolerance (see 07).
- Every leakage exclusion in 03_DATA_AND_FEATURES.md is enforced in code by an automated check.
- 95% accuracy is handled using the canonical wording in 04_MODEL_DECISIONS.md.
- No raw data in the repository; no delivery_note text sent to any AI tool.
