# Rubric — <TASK-ID>

> Lint this file before shipping: `python tools/rubric_lint.py templates/rubric-template.md`
> (The template itself intentionally contains vague words in the placeholder rows — lint your filled copy.)

## Zero-score definition

<What a worthless answer looks like. Write this before the tiers.>

> Example: "The response restates the question, produces numbers not derivable from the inputs, or reaches a conclusion with no calculation chain. If a reviewer cannot point to where the answer broke, it scores above zero."

## Tier 1 — Hard constraints (binary)

Violating any hard constraint caps the total at <CAP>%.

| ID | Constraint (one observable behavior) | Check |
|---|---|---|
| H1 | <Uses only figures provided in attachments> | yes/no |
| H2 | <States the final recommendation exactly once> | yes/no |
| H3 | <All monetary values carry a currency unit> | yes/no |

## Tier 2 — Soft constraints (weighted)

Weights sum to <TOTAL>.

| ID | Dimension | Weight | 0 anchor | 0.5 anchor | 1.0 anchor |
|---|---|---|---|---|---|
| S1 | <Calculation chain transparency> | 30 | <numbers appear without derivation> | <key steps shown, one link unverifiable> | <every number traceable> |
| S2 | <Handling of ambiguous clause> | 25 | <ignores it> | <acknowledges, does not resolve> | <assumption + resolution + sensitivity flag> |
| S3 | <…> | … | | | |

## Tier 3 — Optional constraints (tie-breakers)

Combined effect capped at ±<5>%.

| ID | Bonus behavior |
|---|---|
| O1 | <Names the key limitation unprompted> |
| O2 | <Chooses the more defensible of two methods and says why> |

## Anti-gaming review

Before shipping, write the cheapest technically-compliant answer you can, then fix criteria until it fails:

- [ ] Adversarial answer written and rejected by this rubric
- [ ] Every soft constraint has anchors, not adjectives
- [ ] "Percentage points" written as `pp` wherever rates are scored
