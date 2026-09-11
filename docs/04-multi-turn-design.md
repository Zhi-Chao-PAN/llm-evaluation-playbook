# 04 · Multi-Turn Task Design

In a multi-turn task, turn 3 is not one question — it is a function of the prompt, turn 1's output, turn 2's output, and the user's follow-up. Uncontrolled, the later turns score noise: you cannot tell whether the model failed, or whether it inherited a poisoned context.

## Canonical prior outputs

Freeze the past. For every turn after the first, ship an **authoritative version of what happened before**:

```text
TURN 2 prompt given to the model:
  [user]: <turn-1 question>            <- identical to turn 1's prompt
  [assistant]: <canonical turn-1 answer>  <- frozen gold version, NOT the model's own output
  [user]: <turn-2 follow-up>
```

Why: if the model sees its *own* turn-1 answer, a weak turn-1 poisons turn-2 and you learn nothing about turn-2 ability — you just measured error propagation. With canonical prior outputs, every turn becomes an independent, comparable measurement against a fixed baseline.

Practical notes:

- Store canonical answers next to the reference answer in the judge namespace.
- If the canonical answer needs to be "a good but imperfect answer" (to test recovery from a flawed premise), say so explicitly and label it — an unlabeled imperfect premise is indistinguishable from a typo.
- Keep a changelog of canonical answers. If turn 2's canonical answer changes, every downstream score is incomparable until re-baselined.

## The curveball turn

The most informative follow-ups add information that **invalidates part of the earlier answer**:

> Turn 1: "Which supplier should we consolidate to?"
> Turn 2: "New info: supplier B just lost their ISO certification, and we can only switch once this year. Does the recommendation change?"

A good curveball turn tests three things at once: whether the model tracks its own claims, whether it can revise under new constraints, and whether it distinguishes "recommendation changes" from "recommendation survives, reasoning updates". Weak models rubber-stamp their first answer; sycophantic models flip without justification. Both failure modes are now visible.

Design rules for curveballs:

- The new information must be **decision-relevant** — if the correct answer is "no change", that is a valid curveball too, but say so in the rubric so reviewers do not expect drama.
- One new constraint per curveball. Two simultaneous changes make failure attribution impossible.
- The rubric scores the *transition*, not just the final answer: acknowledges the change, re-evaluates affected parts only, and states explicitly what survives.

## Persona and state consistency

- Fix the user persona's goals in the task spec (risk tolerance, deadline, budget). Follow-ups that drift the persona are contaminating their own task.
- If the scenario has state ("we are now in week 3"), maintain a small state ledger in the spec so turn authors don't contradict each other.

## Scoring structure

Per-turn scores + one end-to-end score:

| Score | Measures |
|---|---|
| Turn N (each) | That turn's ability, given canonical context |
| End-to-end | Coherence of the model's *own* trajectory when it sees its real outputs |
| Transition quality | Curveball handling: revise vs rubber-stamp vs sycophantic flip |

The end-to-end run (model sees its own outputs, like a real session) and the canonical run (model sees frozen golds) answer different questions. Run both when budget allows; when it doesn't, canonical runs give you the comparable per-turn numbers.
