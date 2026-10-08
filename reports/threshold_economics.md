# Threshold Economics

## 0.112 Calculation
Theoretical break-even is calculated as call_cost / (prevention_rate * return_cost) = 45 / (0.35 * 1150) = 0.1118 (rounded to 0.112).

## Economics at 0.112
| Window | Flagged Share | Precision | Recall | Net Rs (scaled to 700/mo) |
|---|---|---|---|---|
| W3 | 0.310 | 0.258 | 0.694 | Rs 12,750 |

## Monthly 700-order Estimate (W3 Basis)
- Calls: ~218
- Prevented returns: ~20
- Avoided cost: ~Rs 22,500
- Call cost: ~Rs 9,800
- Net savings: ~Rs 12,750/month

Sensitivity assumptions: 35% prevention rate, Rs 1150 average return cost, Rs 45 call cost.

## Conclusion
The 0.112 threshold is chosen purely on business break-even economics rather than F1 optimization (CW3).
