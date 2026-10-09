# MEMORANDUM

**TO:** Ritu Deshpande, Head of D2C Operations  
**SUBJECT:** Kestrel Returns Risk — Pilot Recommendation and Operating Strategy

## 1. DECISION

I recommend using the returns-risk model to decide which orders get a confirmation call before dispatch. I do not recommend using it as an automatic dispatch-hold or cancellation system. For every order, the model gives a return-risk score and plain-language reasons.

> **Risk ≥ 0.112 → Confirmation call**  
> **Risk < 0.112 → Standard dispatch**

## 2. WHAT THE DATA SAYS

I could not demonstrate the 95% accuracy promised to the board. The best accuracy I demonstrated in time-based validation was about 89.6%. Only about 11.5% of orders are returned, so predicting “no return” for every order would already be right about 88.5% of the time. Raw accuracy therefore says little about whether the model finds the returns that matter, so I focus on the returns it catches and what that is worth in rupees.

| Primary W3 validation (April–June 2026) | Result |
|---|---:|
| Orders | **2,126** |
| Actual returns | **245** |
| Orders flagged | **31.04%** |
| Returns captured | **69.39%** |
| Precision (flagged orders that were truly returned) | **25.76%** |
| Estimated net value | **₹38,725** |

*These are validation estimates under the stated pilot assumptions, not guaranteed savings.*

## 3. WHY 0.112?

A confirmation call costs ₹45. The pilot uses an assumption that a call can prevent about 35% of the returns that would otherwise happen on called orders, and one return costs ₹1,150. Under these assumptions, a call pays for itself when an order’s estimated return risk is at least:

> **₹45 ÷ (0.35 × ₹1,150) = 0.1118 ≈ 0.112**

Below that level, the call is expected to cost more than it saves under the same assumptions.

## 4. MONTHLY ILLUSTRATION

**Estimate only: extrapolated from validation results and pilot assumptions, not guaranteed savings.**

**~700 orders/month → ~218 calls → ~20 potentially prevented returns → ~61 returns remaining → ~₹12,750 estimated net/month**

## 5. WHAT I RECOMMEND NEXT WEEK

1. **Pilot confirmation calls.** Call the customer before dispatch for every order scoring at or above 0.112.
2. **Do not automatically hold, cancel, reject or block flagged orders.** The score prompts a call; it does not stop the order.
3. **Track the real results.** Record call completion, cancellations, prevented returns, remaining returns and actual rupee savings.
4. **Review and recalibrate.** After the pilot, compare actual outcomes with these estimates and adjust the 0.112 threshold if the real economics differ.

## 6. IMPORTANT PRODUCTION CHECK

The customer prior-order and prior-return fields improved the model, but I could not independently verify how and when the live system calculates them. Before relying on the scores operationally, please have the owner of that system confirm that these fields count only orders placed before the order being dispatched.

## 7. BOTTOM LINE

I would start with a controlled confirmation-call pilot at 0.112, measure the real economics, and only consider stronger intervention after actual operational evidence supports it.
