# 07 · LLM-as-Judge: Tiered Arbitration

Human-only review does not scale to 30+ batches, and judge-only review drifts silently. The working pattern is neither — it is a three-tier arbitration where each tier handles only what it is provably good at.

## The three tiers

```text
Tier 0 — Deterministic checks (scripts, zero judgment)
    tolerance specs, set membership, deliverable inventory, format gates
        ↓ only what passes (or is unmeasurable here) goes up
Tier 1 — LLM pre-screen (rubric-grounded, criterion-by-criterion)
        ↓ flagged / low-confidence / sampled items go up
Tier 2 — Human arbitration (the expensive tier, spent deliberately)
```

Two hard rules:

1. **A judge never overrides Tier 0.** If the tolerance spec says FAIL, it failed. A judge "finding the reasoning acceptable" does not resurrect an out-of-band number.
2. **Tier 2 sees the judge's verdict blind.** The human arbitrates the criterion, not the judge's confidence theater. Show the judge's evidence quote, hide its score until the human has recorded their own.

## What judges are actually good at

Ranked by reliability, highest first:

| Judgment type | Judge reliability | Why |
|---|---|---|
| Binary hard-constraint checks ("does it cite attachment B?") | high | retrieval, not taste |
| Presence/absence inventories ("which of these 5 sections exist?") | high | enumeration |
| Evidence quoting ("quote where it handles the ambiguous clause") | medium-high | grounded, auditable |
| Graded soft scores (0 / 0.5 / 1 anchors) | medium | anchors help; taste leaks in |
| Holistic quality ("rate 1–10") | low | do not use |

The pattern: push everything toward the top of this table. A rubric designed per [01 · Rubric Design](01-rubric-design.md) is mostly judgeable; a rubric of adjectives is not.

## Judge failure modes and mitigations

| Failure mode | Symptom | Mitigation |
|---|---|---|
| Position bias | prefers first (or last) answer shown | swap order; score A/B twice, disagree → escalate |
| Verbosity bias | longer answers score higher | length is never a criterion; explicit "brevity is not penalized" |
| Self-preference | favors outputs stylistically similar to the judge model | judge ≠ model under test; different family when possible |
| Leniency drift | scores creep up over a long session | batch small, rotate rubric excerpt order, re-anchor with a known item every N |
| Rubric paraphrase drift | judge "summarizes" criteria and scores the summary | verdict must cite criterion ID + quote evidence, per criterion |
| Sycophancy to framing | "the analyst explains convincingly..." | score the artifact, ignore its self-praise |

## The verdict format (make the judge legible)

Force a structured verdict, one per criterion:

```json
{
  "criterion": "S2",
  "verdict": "0.5",
  "evidence_quote": "flags C4 as churn driver but quotes no numbers",
  "confidence": "low"
}
```

No quote, no verdict — an unsupported verdict is discarded. Low-confidence or missing-evidence verdicts route straight to Tier 2.

## Calibration protocol

Before trusting a judge on a new task family:

1. **Sample 30–50 items** already double-scored by humans.
2. Run the judge; compute agreement on hard constraints (expect near-perfect) and soft constraints (target: exact-anchor agreement ≥ 70%, within-one-anchor ≥ 95%).
3. Read every disagreement — each one is either a judge bug (fix the judge prompt) or a rubric bug (the criterion is ambiguous; fix the rubric). Both outcomes improve the task.
4. Re-run until stable; log the agreement numbers with the task package.
5. In production, blindly re-arbitrate a fixed sample (5–10%) of judge-passed items — drift detection is a process, not a one-time gate.

## Anti-patterns

- Judge-on-judge chaining (a second LLM "reviewing" the first adds variance, not truth).
- Letting the judge restate the rubric in its own words before scoring.
- Holistic 1–10 scores with no criterion mapping.
- Tuning the judge prompt until it agrees with a single human's idiosyncrasies instead of with the rubric.
- Trusting judge confidence percentages as probabilities — they are vibes with decimals.
