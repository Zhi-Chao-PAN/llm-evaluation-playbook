# 05 · Large-Scale Feedback Quality

Producing human feedback at scale (10k+ items per month across multiple product modules) turns quality from an adjective into a process. This chapter is the working method that kept validity above 99% at that volume.

## What "feedback" is for

Every feedback item should be usable by someone who never sees your session: an engineer triaging a bug, a data scientist building a regression set, an analyst comparing model versions. If the item only makes sense with a screenshot of your screen, it is a note, not feedback.

## Validity taxonomy

Reject or repair items that fall into any of these buckets, and track the buckets — the *distribution* of invalidity is more diagnostic than the rate:

| Bucket | Definition | Typical fix |
|---|---|---|
| Duplicate | Same issue already submitted (by you or visible in queue) | Drop; link to original |
| Off-spec | Not about the behavior under evaluation | Drop or route to the right queue |
| Unverifiable | Cannot be reproduced from the information given | Repair: add steps/quote |
| Self-contradictory | Claim and evidence in the same item disagree | Rewrite after re-check |
| Preference-only | "I like X better" with no consequence | Repair: state the consequence |

## Process controls

1. **Daily spot-check.** Before submitting a batch, re-read 5 random items as if you were the recipient. This 5-item read catches drift that per-item attention cannot.
2. **Module-level validity tracking.** Compute validity per module/track, per day. A single module's validity sliding 3 days in a row is a signal — usually task instructions changed or you are fatigued; it is almost never the model's fault.
3. **Keep rejected samples.** The items you rejected are the calibration set for your own judgment. Re-reading last month's rejects is the fastest way to notice that this month's standards have quietly shifted.
4. **Volume honesty.** Validity beats volume in every settlement conversation. 19k valid + 2k self-rejected is a better month than 21k submitted with 6% bouncing back.

## Writing a single feedback item

Template:

```text
[Module] short title
Observed:  <exact quoted output or minimal repro, verbatim>
Expected:  <what a correct/usable behavior would be>
Why it matters:  <who is blocked or misled, and when>
Severity:  blocker / major / minor
```

Rules of thumb:

- Quote, don't paraphrase. Paraphrase is where hallucinated feedback is born.
- One issue per item. Two issues in one item means one of them never gets fixed.
- "Why it matters" is the field reviewers skip and triagers need most; one sentence.
- If you cannot write the Expected line, you do not have a bug report — you have a feeling. Investigate before submitting.

## Fatigue management

At volume, the failure mode is not dishonesty, it is autopilot:

- Cap focused hours per module; switch modules rather than grinding one.
- The 5-item spot-check doubles as a fatigue probe: if you catch yourself skimming it, stop.
- Log submission counts per day. A day that looks like a productivity spike is often a validity dip in disguise.
