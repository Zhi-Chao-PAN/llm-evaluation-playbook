# 01 · Three-Tier Rubric Design

A rubric is an API between the task designer and every future reviewer. If two reviewers can read the same criterion and disagree about what it means, the rubric is under-specified — the model did not fail, your spec did.

## The three tiers

### Tier 1 — Hard constraints (binary, fail-fast)

Things that make the answer *wrong*, not *worse*. Each one is checkable with yes/no logic.

```text
H1. Uses only the figures provided in attachments (no invented data).     [yes/no]
H2. States the final recommendation exactly once, in the closing section. [yes/no]
H3. All monetary values include the currency unit.                       [yes/no]
```

Rules:

- One observable behavior per constraint. "Well-structured and complete" is two constraints pretending to be one.
- Violating **any** hard constraint caps the total score at a fixed ceiling (e.g., 30%) regardless of everything else. Write the ceiling down.
- Hard constraints should survive paraphrase: restate each one in three different words and check it still means the same thing.

### Tier 2 — Soft constraints (weighted dimensions)

Quality dimensions that have degrees. Each gets an explicit weight and a 0 / partial / full anchor.

```text
S1. Calculation chain transparency                     weight 30
    0  = final numbers appear without derivation
    0.5 = key steps shown but one link unverifiable
    1   = every number traceable to input or prior step

S2. Handling of the ambiguous clause (attachment B)     weight 25
    0  = ignores it
    0.5 = acknowledges but does not resolve it
    1   = states assumption, resolves, and flags sensitivity
```

Rules:

- Weights must sum to a stated total. If they sum to 100, say so; silent mismatches are how review arguments start.
- Partial credit needs *anchors*, not adjectives. "Good handling" is not an anchor; "states assumption + resolves + flags sensitivity" is.
- 3–6 soft constraints is the sweet spot. Beyond that, reviewers skim and the weights stop meaning anything.

### Tier 3 — Optional constraints (tie-breakers, bonuses)

Small things that distinguish a 92 from a 97: naming the limitation unprompted, choosing the better of two defensible methods, formatting that a domain expert would actually forward to a colleague. Cap their combined effect (e.g., ±5%) so they cannot rescue a hard-constraint violation.

## Define zero before defining excellence

Most rubric drafts spend all their words describing the perfect answer. Spend your first paragraph on the worthless one:

> **Zero-score answer.** The response restates the question, produces numbers not derivable from the attachments, or reaches a conclusion without any calculation chain. If a reviewer cannot point to *where* the answer broke, it is a 3, not a 0.

This one paragraph eliminates the most common reviewer disagreement: whether "confident nonsense" is a 0 or a 4.

## Anti-gaming: paraphrase-attack your own rubric

Before shipping a rubric, try to write an answer that is **bad but technically compliant**:

- Criterion says "cites evidence"? A model can cite irrelevant rows and comply.
- Criterion says "discusses risks"? One boilerplate sentence about market volatility complies.
- Criterion says "correct conclusion"? A coin flip complies 50% of the time.

Fix the criterion until the bad-but-compliant answer no longer exists. Concretely: change "cites evidence" → "cites evidence **that changes the conclusion if removed**".

## Sanity checks before shipping

1. Cold-read test: a reviewer who has never seen the task scores a gold answer. Expectation: within one weight-step of your own score.
2. Adversarial test: write the cheapest compliant answer you can. The rubric should catch it.
3. Zero test: write a confident nonsense answer. The rubric should score it at the zero anchor, not in the middle.
