# Reference Answer — SYNTH-SaaS-001 (judge asset)

> Fictional numbers, derived step by step from the two CSVs in this package.
> Every number below is traceable; this is the shape a Tier-1 chain should have.

## Step 1 — Current MRR base

Sum of `mrr_usd` across all 8 cohorts:

```
1,800,000 + 1,200,000 + 900,000 + 700,000 + 250,000 + 100,000 + 30,000 + 20,000
= 5,000,000 USD
```

## Step 2 — Churn impact (apply churn first, per H2)

Per cohort: `churn_rate x mrr_usd`

| Cohort | MRR | Rate | Churn |
|---|---:|---:|---:|
| C1_Enterprise | 1,800,000 | 3.0% | 54,000 |
| C2_Growth | 1,200,000 | 4.0% | 48,000 |
| C3_MidMarket | 900,000 | 8.0% | 72,000 |
| C4_SMB_Legacy | 700,000 | 14.0% | 98,000 |
| C5_SMB_New | 250,000 | 6.0% | 15,000 |
| C6_Startup | 100,000 | 9.0% | 9,000 |
| C7_Edu | 30,000 | 5.0% | 1,500 |
| C8_Nonprofit | 20,000 | 4.0% | 800 |

Total churn = **298,300 USD = 5.97 pp** of the 5,000,000 base.

## Step 3 — Expansion (assumption: booked on beginning-of-period base)

Per cohort: `expansion_rate x mrr_usd` → total = **115,800 USD** (2.32%).

**Assumption (S3):** expansion is booked against the beginning-of-period MRR
(upsells are contracted on original seats before churn lands). Applied
consistently; sensitivity below.

## Step 4 — Bridge to next quarter

```
5,000,000 - 298,300 + 115,800 = 4,817,500 USD
```

**Next-quarter MRR = 4,817,500 USD** (tolerance T1: relative 2%).

## Step 5 — Churn drivers (churn exposure, not cohort size)

Ranked by absolute churn impact: **C4_SMB_Legacy (98,000)** and
**C3_MidMarket (72,000)**. (C1 has the largest MRR but only 54,000 exposure —
flagging C1 over C3 is the trap this dimension catches.)

## Sensitivity note

If expansion were applied to the post-churn base instead, next-quarter MRR
would be ~4,810,992 (−0.14%) — inside tolerance T1; the drivers do not change.
