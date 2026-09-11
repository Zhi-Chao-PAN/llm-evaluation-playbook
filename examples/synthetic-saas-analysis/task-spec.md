# Example Task Spec — SYNTH-SaaS-001

> Fully fictional scenario and numbers, written to demonstrate the templates.
> Not derived from any real task, client, or dataset.

## Scenario

A junior analyst at a (fictional) SaaS company asks for help building next quarter's revenue bridge: given this quarter's MRR by cohort and a churn/expansion table, produce the bridge from current MRR to next-quarter MRR, flag the two cohorts driving most of the churn, and state the assumption about expansion timing.

## Inputs (agent namespace)

| Asset | Format | Notes |
|---|---|---|
| mrr_by_cohort.csv | CSV | 8 cohorts, columns: cohort, seats, mrr_usd |
| churn_expansion.csv | CSV | columns: cohort, churn_rate, expansion_rate |

## Judge assets (judge namespace)

| Asset | Notes |
|---|---|
| reference_answer_judge.md | gold bridge + method chain |
| rubric_judge.md | three-tier rubric (this folder) |
| tolerances_judge.json | numeric bands |

## Turn plan

Single-turn for the base task. (A curveball extension: "churn for the two largest cohorts doubles — does the worst cohort change?" — would make it multi-turn per docs/04.)

## Expected difficulty

Predicted failure modes:

1. Applying expansion before churn (order-of-operations) — caught by H2 + T1
2. Mixing currency units with percentage points — caught by H3 + T2 (`pp` band)
3. Flagging the largest cohort instead of the largest churn driver — caught by S2

## Packaging checklist

- [x] Judge assets carry `_judge` suffix; packaging excludes `*_judge*`
- [x] Gold values (4,812,000 / 6.2 pp) grepped across agent bundle — absent
- [x] Every tolerance spec exercised with one PASS and one FAIL case
