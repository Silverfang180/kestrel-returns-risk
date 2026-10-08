# PROMPT_LOG — AI assistance (honest log)

Entries marked [confirm] need the author to confirm dates/costs. Paid API calls made: none. Subscription costs: [confirm].

| # | Date | Tool | Purpose | Important instruction / content | Result | Discarded | Changed a decision? |
|---|---|---|---|---|---|---|---|
| 1 | 2026-10 [confirm] | ChatGPT | First plan for Task 2 | Asked to plan data inspection, validation, leakage checks, call-vs-hold economics | Reasonable high-level plan: time-based split, challenge 95%, rupee trade-offs, leakage review | Suggested possible LLM use for explanations; planned version log V1-V6 (pre-planned, not honest history) | Yes: kept pushback on 95% and time validation; LLM idea discarded |
| 2 | 2026-10 [confirm] | Claude | Review of the ChatGPT plan | Compare with brief | Added: point-in-time customer history, Shield timing, label definition, template reasons without API | Per-order LLM reasons | Yes: no LLM in service |
| 3 | 2026-10 [confirm] | Claude | First data inspection | Upload of all pack files | Found leakage columns, duplicates, October x100, pincode; HGB AUC 0.74; DECISIONS.md v1 | v1 feature set, divide-by-100, landmark flags | Superseded by later review |
| 4 | 2026-10 [confirm] | Claude | Skeptical review report | 19-section challenge brief | Verified/corrected claims; found prompt-injection rows, prior-field inconsistency, rolling windows; LR beat HGB | "95% impossible" wording; landmark/hour/tenure/age features | Yes: dropped features, softened wording |
| 5 | 2026-10 [confirm] | Claude | Prior features, thresholds, model choice | Controlled A-D ablation; calibration; threshold tables | Raw counts kept; LR chosen; 0.112 break-even; call-not-hold; 9-feature set | Derived rate, value, qty, SKU, HGB in service | Yes: final feature list |
| 6 | 2026-10-08 [confirm] | Claude | Documentation pack | Docs for Antigravity | docs/00-07 + context files; re-verified state ablation and final 9-feature metrics; corrected 89.7% to 89.6% | Nothing | Corrected accuracy wording |
| 7 | 2026-10-08 [confirm] | Claude | Correction pass on the pack | Fix monthly picture, make `family` the API input, keep OQ3 open, restore conservative privacy defaults | Patched docs 02, 05, 07 and context files | sku lookup file in repo | No locked decision changed |
| 8 | 2026-10-08 | Antigravity | Implementation from docs | Implement constraints, validation gate, batch scoring, API, and UI | Repository complete, validation gate passed, 2096 predictions generated | none | No locked decision changed |
| 9 | 2026-10-08 | Antigravity | Final repair from Audit | Fixed HGB discrepancy via OrdinalEncoder, completed 13+ missing unit tests, implemented Markdown report automation in validate.py, cleaned up scratch, and re-verified | Full pytest suite passes; HGB metrics match docs; missing reports generated; no PII leaks | none | Fixed implementation to strictly match original analysis decisions |

## Where AI misled or needed correction
- Early claims were too strong ("95% not reachable", landmark flags useful, divide October by 100); corrected by later tests.
- The 89.7% accuracy figure came from a different feature set than the locked model.
- The delivery_note injection rows were shown to Claude in analysis output; their instructions were not followed and the finding is documented.

## Data-sharing disclosure
Task files were uploaded to Claude for analysis (and the brief text was shared with ChatGPT). Whether this fits policy s10 is unverified (OQ4).
