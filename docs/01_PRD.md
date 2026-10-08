# 01 — Product Requirements

## Users
- **Primary:** D2C operations staff (Ritu's team) deciding, per order before dispatch, whether to make a confirmation call.
- **Secondary:** Finance (Farhan) checking cost and ROI; Service Desk (Meenal) worried about Shield customers; assessors at Banao.

## Problem statement
About 11.4% of orders are returned [VF], each costing about Rs 1,150 on top of the refund (policy s4; Finance email) [VF]. Ops cannot currently tell which orders will come back before they ship.

## Objective
Produce a calibrated, explainable risk score from information available at dispatch, and a clear action rule that is profitable under the policy economics.

## Workflow
1. Order reaches dispatch with the 9 model inputs available (see 03).
2. Service scores it: probability of return, recommended action, top reasons.
3. If probability >= 0.112 (economic break-even): **recommend a confirmation call** before dispatch. Otherwise dispatch normally.
4. Staff decide; the tool recommends, it does not block or hold anything. [DEC]

## Functional requirements
- FR1 `POST /predict` accepts one JSON order, returns `{score, recommend_call, threshold, reasons[], caveats[]}`.
- FR2 `GET /health` returns status and model metadata (version, training window, feature list).
- FR3 One HTML screen: form for the 9 inputs, submit button, shows score, action, reasons, caveat text.
- FR4 Batch script scores test_unlabelled.csv into predictions.csv.
- FR5 Reasons are deterministic and derived from the fitted model (see 02). No LLM.
- FR6 Unknown/invalid inputs return HTTP 422 with a plain-language message; the UI shows it politely.
- FR7 Fields that must not be used (pickup, service event, delivery_note, etc.) are ignored if sent and never influence the score. A response flag lists ignored fields.

## Non-functional requirements
- Runs locally on a clean machine: Python venv, pinned dependencies, no network calls at inference, no API key, no database, no auth.
- Deterministic: same input gives same output; fixed seeds for training.
- Latency not a concern (single logistic regression); cost per prediction Rs 0 in paid calls. [DEC]
- Privacy: no raw data in repo; logs must not store submitted records.

## Output behaviour
- `score` is the predicted probability of return in [0, 1]; higher = riskier. It is the value written to predictions.csv.
- `recommend_call` = `score >= 0.112`. The threshold is a config constant, named as economic break-even.
- Reasons: up to 4 plain-language statements ranked by contribution to the logit, with direction (raises/lowers risk).

## Business decision framing
- Ritu asked for flag-and-hold at 95% accuracy. We recommend **score-and-call**: use the model to choose whom to call (Rs 45/call, ~35% of returns prevented on called orders per the pilot), not whom to hold.
- Reason: calls are priced and supported by a pilot; holds cost about 12% cancellations (policy s7) but the pack gives no margin to price it. [VF/RISK]
- 95% accuracy was not demonstrated; accuracy is not the right yardstick (see canonical wording CW1).

## Out of scope
LLM or chatbot features, RAG, embeddings, external inference API, deep learning, database, authentication, microservices, cloud deployment, automatic dispatch holds, Shield-specific policy engine, retraining pipeline in the service, publishing any customer data.
