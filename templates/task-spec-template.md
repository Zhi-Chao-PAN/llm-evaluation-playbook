# Task Spec — <TASK-ID>

> One page. If it does not fit on one page, the task is two tasks.

## Scenario

<One paragraph, written as a plausible real-world request. If the agent namespace cannot be read as "something a real user would send", redesign (see docs/03).>

## Inputs (agent namespace)

| Asset | Format | Notes |
|---|---|---|
| <data.csv> | CSV | <row count, key columns> |
| <glossary.md> | MD | domain terms, fair game |

## Judge assets (judge namespace — never ship to agent)

| Asset | Notes |
|---|---|
| reference_answer.md | gold answer + method chain |
| rubric.md | three-tier rubric (see rubric-template) |
| tolerances.json | numeric tolerance specs |
| canonical_priors/ | frozen turn outputs, if multi-turn |

## Turn plan (if multi-turn)

| Turn | Purpose | Type (baseline / curveball / re-plan) | New info introduced |
|---|---|---|---|

## Expected difficulty

- Predicted failure modes (write before running):
  1. ...
  2. ...
- Criterion that catches each: ...

## Packaging checklist

- [ ] Judge assets named `*_judge*` and excluded from agent bundle
- [ ] Agent bundle unzipped and read file-by-file on a clean machine
- [ ] Gold values grepped across the agent bundle (string forms + roundings)
- [ ] Turn prompts embed canonical prior outputs, not live model outputs
- [ ] Every numeric answer has a tolerance spec with one constructed pass + fail case
