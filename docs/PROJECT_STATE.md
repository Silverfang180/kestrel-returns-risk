# PROJECT_STATE (as of 2026-10-08)

Evidence note: the documentation step had access to the supplied task files and the analysis performed in conversation, not to a code repository. No repository files existed to inspect; nothing below is marked done unless it exists as an artifact.

## DONE
- Task pack read and verified: data, leakage, October values, duplicates, pincode, notes, signup, priors, Shield (docs/03).
- Validation, model comparison, calibration, threshold/economics and error analysis run in analysis scripts (not in a repository); results recorded in docs/05.
- Modeling decisions locked (docs/04).
- Documentation pack written: docs/00-07, ANTIGRAVITY_CONTEXT.md, PROJECT_STATE.md, PROMPT_LOG.md.
- Repository skeleton; loader/dedup/guard; training and validation scripts in the repo; artifacts; predictions.csv; FastAPI service; HTML screen; tests; README; reports/.
- Final repair: HGB model uses native categoricals, comprehensive test coverage added, markdown reports dynamically generated.

## IN PROGRESS
- Nothing.

## NOT STARTED
- memo; screen recording; submission-form.md; GitHub push.

## BLOCKED
- Nothing blocking implementation.

## SUPERSEDED / DO NOT USE
- `DECISIONS.md` and `explore.py` (earlier draft, Claude): DECISIONS.md lists the old 11-feature design, divides October values by 100, mentions hour/age/state features and an 89.7%-era wording. It conflicts with docs/. Treat docs/ as authoritative and delete or rewrite DECISIONS.md.

## OPEN QUESTIONS
- OQ1: May predictions.csv be committed to a public repo? Default: deliver via the submission channel only.
- OQ2: May the fitted model artifact and aggregate group rates be committed? Default: yes (no raw rows); confirm.
- OQ3: May a 21-row sku->family lookup be committed? Open. v1 default: not committed; the API takes `family` directly; any mapping is a future/interface question.
- OQ4: Does policy s10 ("approved vendors") cover uploading the files to ChatGPT/Claude/Antigravity? Unverified; disclose in the form.
- OQ5: How does Kestrel's live system compute customer_prior_orders/returns at dispatch?
- OQ6: When is shield_member set relative to the order?
- OQ7: Which metric will the hidden score use?
- OQ8: What do INSTALL_BOOKED orders do later (returned or installed)?
- OQ9: Contribution margin per order and cancellation behaviour, needed to price holds.

## Numbers not independently reproduced / corrected
- "Best demonstrated accuracy about 89.7%" (earlier brief): reproduced only for the earlier 11-feature LR (89.70%). Locked 9-feature LR gives 89.56% on W3. Docs use "about 89.6%".
- Hidden-test ranges (CW8) are estimates, not reproducible results.
- The 35% prevention rate and Rs figures are policy/pilot assumptions, not tested by us.
