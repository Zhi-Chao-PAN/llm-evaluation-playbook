# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-09-11

### Added

- `tools/playbook_check.py`: one-shot validator for a whole task package —
  required files, Tier-2 weight sums, tolerance-spec coverage of rubric IDs,
  agent/judge namespace isolation, judge-asset shipping; `--strict` promotes
  warnings to failures.
- Spec-validation mode in `tools/tolerance_check.py`: omit `--answer` (or use
  `"answer": null` in batch lines) to validate spec structure only, so
  definition files are CI-checkable before answers exist.
- `docs/07-llm-as-judge.md`: tiered arbitration (deterministic checks,
  rubric-grounded LLM pre-screen, human arbitration), judge failure modes
  with mitigations, structured verdict format, calibration protocol.
- CI workflow (GitHub Actions): 17 unit tests, example-package validation,
  and tolerance-spec validation across Python 3.9 / 3.11 / 3.12.
- Mermaid lifecycle overview in the README; example package made complete and
  executable (data CSVs, derived reference answer, demo answers with one
  deliberate FAIL); all gold values recomputed from the CSVs.

## [0.1.0] - 2026-09-11

### Added

- Six methodology chapters: three-tier rubric design, machine-checkable
  numeric tolerances, contamination control, multi-turn task design,
  large-scale feedback quality, long-horizon agent task patterns.
- `tools/rubric_lint.py` (vague-language detection) and
  `tools/tolerance_check.py` (five band types), stdlib only, 11 unit tests.
- Fillable templates: task spec, rubric, submission checklist.
- `examples/synthetic-saas-analysis/`: fictional end-to-end example.
