# Example Rubric — SYNTH-SaaS-001 (judge asset)

> Fictional numbers. Demonstrates the three-tier structure from docs/01.
> Lint a copy with `python tools/rubric_lint.py` after editing — this file
> keeps its anchors concrete on purpose.

## Zero-score definition

The response restates the inputs, produces numbers not derivable from `mrr_by_cohort.csv` and `churn_expansion.csv`, or presents a bridge total with no calculation chain. A reviewer must be able to point at the exact step where the answer broke; if they cannot, the answer scores above zero.

## Tier 1 — Hard constraints (binary)

Violating any hard constraint caps the total at 30%.

| ID | Constraint | Check |
|---|---|---|
| H1 | Uses only figures from the two CSVs; no invented data | yes/no |
| H2 | Applies churn before expansion (order stated or derivable) | yes/no |
| H3 | Rates quoted in `pp` (e.g., "6.2 pp"), never as bare "%" | yes/no |
| H4 | Names exactly two cohorts as churn drivers | yes/no |

## Tier 2 — Soft constraints (weights sum to 100)

| ID | Dimension | Weight | 0 anchor | 0.5 anchor | 1.0 anchor |
|---|---|---|---|---|---|
| S1 | Bridge transparency | 40 | total stated without derivation | each component shown but one link unverifiable | every component traceable to a CSV row and stated rate |
| S2 | Churn-driver identification | 35 | flags by cohort size only | flags by churn rate but ignores MRR exposure | ranks by churn × MRR exposure and quotes the numbers |
| S3 | Expansion-timing assumption | 25 | no assumption stated | assumption stated but unused | assumption stated, applied consistently, sensitivity noted in one sentence |

## Tier 3 — Optional constraints (combined effect ≤ 5%)

| ID | Bonus behavior |
|---|---|
| O1 | Notes that the two flagged cohorts overlap with the largest revenue at risk, unprompted |
| O2 | Recommends a specific follow-up check (e.g., cohort age vs churn) |

## Tolerance specs (see tolerances_judge.json)

| ID | Quantity | Expected | Band |
|---|---|---|---|
| T1 | Next-quarter MRR (USD) | 4,817,500 | relative 2% |
| T2 | Total churn impact (pp of MRR) | 5.97 | points 0.5 |

## Anti-gaming review

Cheapest compliant answer attempted: "Bridge = 4.81M, churn is bad in cohorts C3/C4."
Rejected by: S1 0-anchor (no chain), S2 0.5 anchor floor (no quoted numbers), H4 borderline.
