# Model Comparison

Logistic Regression vs HistGradientBoosting (same 9 features):

| Window | AUC LR / HGB | PR-AUC LR / HGB | Brier LR / HGB |
|---|---|---|---|
| W1 | 0.769 / 0.762 | 0.346 / 0.331 | 0.0842 / 0.0847 |
| W2 | 0.776 / 0.769 | 0.393 / 0.362 | 0.0868 / 0.0887 |
| W3 | 0.788 / 0.772 | 0.418 / 0.389 | 0.0844 / 0.0865 |

## HGB Configuration
Depth 3, lr 0.05, 150 iter, min leaf 50, L2 1.0, with native categorical support (via OrdinalEncoder).

## Conclusion
LR matches or slightly exceeds HGB across windows while offering transparent explainability for the confirmation agents. Decision: Use Logistic Regression (CW2).
