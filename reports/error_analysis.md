# Error Analysis

Analysis of W3 errors at the 0.112 operating threshold (aggregate only):

- **False Negatives (Missed Returns):** Strongly skewed toward prepaid orders and customers with no prior return history. The model lacks sufficient visibility into first-time prepaid buyers.
- **False Positives (False Alarms):** Highly concentrated in Shield member and COD orders, because these segments have inherently higher baseline risk causing them to frequently exceed the low 0.112 threshold.
- **Privacy Notice:** No row-level order IDs, customer names, or delivery notes were used or examined in this aggregate error diagnosis.
