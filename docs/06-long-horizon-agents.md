# 06 · Long-Horizon Agent Task Design

Long-horizon tasks (agent runs lasting hours, thousands of files, many stages) fail differently from chat tasks: errors compound, state drifts, and "completed" often means "stopped". Evaluation has to target the failure modes, not just the final artifact.

## Failure modes specific to long-horizon runs

| Failure mode | What it looks like | What the rubric must catch |
|---|---|---|
| Compounding drift | Each stage is 95% right; the pipeline output is wrong | Checkpoint correctness, not just final output |
| Silent partial completion | Reports "done" with 3 of 5 deliverables | Deliverable inventory as a hard constraint |
| Conflicting sources unreconciled | Two files disagree; agent averages or picks silently | Explicit conflict-detection turns |
| Zombie branches | A subtask started, stalled, never killed | Explicit terminate/continue decisions in the trace |
| Lost scope | Agent re-reads everything after each step; or forgets the goal by stage 6 | Goal-restatement checkpoints |

## Design patterns

### Staged deliverables
Force intermediate artifacts the rubric can inspect: a data baseline, a rules summary, a work-in-progress workbench, a final export. Each stage gets its own mini-rubric with hard constraints (inventory: which files must exist, which fields populated).

### Gap-detection turns
Insert turns whose correct answer is "there is missing information": a source group that is incomplete, a reference file that does not exist. The rubric's zero-score answer is the agent inventing plausible data. This is the single cheapest test for hallucination under time pressure.

### Conflict-resolution turns
Give two sources that disagree on a number with different credibility cues (freshness, specificity, provenance). Score the *decision rule* the agent states ("source B is fresher but A is audited; I use A for X and flag B") more than the final pick.

### Dynamic re-planning turns
Introduce a mid-run event that invalidates a branch (a deadline moves, a batch is corrupted). Correct behavior: stop, re-scope, explicitly terminate the dead branch. The failure to catch is not "wrong answer" but "kept working on the dead branch and reported success".

## Checkpoint rubrics, not final-artifact rubrics

Score the trajectory:

```text
C1. Baseline stage: inventory complete, no invented files          [binary]
C2. Mid stage: conflict list explicit (>= N known conflicts found) [graded]
C3. Termination decisions: every abandoned branch has a reason     [binary]
C4. Final export: schema + row-count checks against spec           [tolerance]
C5. Reproducibility: re-running stage N yields same result         [binary, sampled]
```

Idempotency (C5) deserves its own criterion: long-horizon agents get restarted, and a task where a restart produces a different answer is testing luck.

## Practical constraints for task authors

- Realistic scale teaches more than toy scale: a task that processes 3 files cannot exhibit drift. Synthetic-but-plausible scale (thousands of small files) is fine; the *content* can be fully fictional.
- Freeze the environment: file set, timestamps, and any seeded randomness must be pinned, or C5 is unmeasurable.
- Write the failure atlas before the task: list the 5 ways you expect agents to fail, and confirm each is caught by a criterion. A criterion set that catches nothing you predicted is a coincidence, not a rubric.
