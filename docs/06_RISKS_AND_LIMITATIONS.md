# 06 — Risks and Limitations

Each item: type, evidence, mitigation, owner of next action.

1. **[RISK] customer_prior_* semantics.** Not a running ledger (1,625 / 426 decreases; 1,776 rows below visible history). Largest feature gain. Mitigation: CW4 in memo/form; report no-prior floor (AUC about 0.73-0.74); ask Kestrel to confirm how the CRM computes them at dispatch.
2. **[RISK] Temporal leakage and documentation conflict.** README says test is a dispatch snapshot; email says service columns are as of export day. Excluded columns enforced by code (guard test). If any excluded column re-enters, validation becomes meaningless.
3. **[RISK] INSTALL_BOOKED (test only, 543 rows).** [INF] may precede 0%-returned INSTALL_DONE states. Not learnable from train. Could move the hidden score either way; not used.
4. **[RISK] Shield timing.** No Shield date; adds 0.02-0.03 AUC. Test share (22.1%) matches train, giving no sign of a post-order effect.
5. **[RISK] Hidden-test uncertainty.** Metric unknown; range in CW8 is an estimate; 245 positives per window, +-0.03 AUC noise; features/models chosen on the same windows (optimism).
6. **[ASM/RISK] Pilot transfer.** 35% prevention comes from a pilot whose selection is unknown; may not hold for high-risk orders. Rs 45 is per completed call; unanswered calls change economics.
7. **[RISK] Hold economics incomplete.** No margin/lost-sale value; no evidence on hold effect on returns. No hold ROI claimed (CW6).
8. **[RISK] Data quality.** October x100 values (cause unproven); signup_date after order date (2,105 raw rows, undocumented); pincode 000000 contradicts walk-in explanation; uniform order-hour distribution suggests simulated timestamps [INF]; duplicates from partner feed.
9. **[RISK] Prompt injection in data.** Three delivery_note rows. Any AI tool reading raw notes could be steered. Mitigation: never load the column; treat data text as data; document the finding. Note: raw text of these three rows was displayed to Claude during analysis (not acted on).
10. **[RISK] Privacy / policy s10.** Raw data must not go to public repos or beyond the engagement team. Open: whether uploading files to ChatGPT/Claude/Antigravity counts as an "approved vendor" use; whether committing fitted artifacts, aggregates and predictions.csv is acceptable (OQ1, OQ2). Mitigation: repository contains code and aggregates only.
11. **[RISK] Model limits.** Weak on first-time prepaid customers; 31% of orders flagged at the break-even threshold means most calls (about 74%) go to orders that would not have been returned; probabilities approximately calibrated, W1 slope .93.
12. **[RISK] Final model trained on all data including W3**, leaving no clean holdout; evidence rests on the three earlier windows.
13. **[RISK] Reproducibility.** Pin Python/scikit-learn/numpy versions; the joblib artifact is version-sensitive.
