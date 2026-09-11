# Submission Checklist

The final gate before a task ships. Ten minutes here prevents the two most common post-mortem findings: "the rubric wasn't checkable" and "the reference leaked".

## Rubric

- [ ] Zero-score definition written first, in one paragraph
- [ ] Every hard constraint is binary and names one behavior
- [ ] Every soft constraint has 0 / 0.5 / 1.0 anchors (no adjectives like "good", "reasonable")
- [ ] Weights sum to a stated total
- [ ] `rubric_lint.py` clean on the filled rubric
- [ ] Adversarial (cheap-but-compliant) answer written and rejected

## Tolerances

- [ ] Every checked number has a spec (type, value, unit)
- [ ] `pp` written explicitly wherever percentages are compared
- [ ] Each spec exercised with one constructed PASS and one constructed FAIL
- [ ] Two defensible methods either both land in-band, or the method is pinned in the prompt

## Contamination

- [ ] Judge assets named `*_judge*`, excluded from the agent bundle by pattern
- [ ] Agent bundle unzipped and read file-by-file on a clean machine
- [ ] Top-3 gold values grepped across the bundle (string forms + roundings)
- [ ] No scoring discussion lives in a channel the model can see

## Multi-turn (if applicable)

- [ ] Canonical prior outputs frozen and versioned
- [ ] Follow-up turns use canonical priors, not live model outputs
- [ ] Each curveball introduces exactly one new constraint
- [ ] "No change needed" accepted as a valid curveball outcome in the rubric

## Packaging

- [ ] Zip contents listed and eyeballed before sending
- [ ] Version number in the task spec changelog
- [ ] Deliverable inventory stated (what "done" means, in files)
- [ ] `python tools/playbook_check.py <package>` exits clean

## LLM pre-screening (if used — see docs/07)

- [ ] Judge calibrated on 30–50 double-scored items; agreement logged
- [ ] Verdicts are criterion-by-criterion with evidence quotes
- [ ] Judge never overrides Tier-0 tolerance checks
- [ ] 5–10% blind re-arbitration sample scheduled for drift detection
