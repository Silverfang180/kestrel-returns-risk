# Validation Summary

Metrics across time-based validation windows (Logistic Regression):

| Window | AUC | PR-AUC | Accuracy@0.5 | Precision@0.5 | Recall@0.5 | F1@0.5 | Brier | Majority Baseline | Confusion Matrix |
|---|---|---|---|---|---|---|---|---|---|
| W1 | 0.769 | 0.346 | 0.8943 | 0.561 | 0.102 | 0.173 | 0.0842 | 0.8919 | [[1839, 18], [202, 23]] |
| W2 | 0.776 | 0.393 | 0.8932 | 0.738 | 0.126 | 0.215 | 0.0868 | 0.8838 | [[1868, 11], [216, 31]] |
| W3 | 0.788 | 0.418 | 0.8956 | 0.735 | 0.147 | 0.245 | 0.0844 | 0.8848 | [[1868, 13], [209, 36]] |

W3 is the primary validation window as it represents the most recent period (Apr-Jun 2026), trained on all preceding data.
