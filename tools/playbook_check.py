#!/usr/bin/env python3
"""playbook_check.py — validate an evaluation task package end to end.

A task package is a directory containing:

    task-spec.md        scenario, inputs, judge assets, turn plan
    rubric*.md          three-tier rubric (e.g. rubric_judge.md)
    tolerance*.json     numeric tolerance specs (JSON array or JSON-lines)
    answers_demo.jsonl  optional: batch-mode answers for tolerance_check

Checks performed:

  structure        required files present
  rubric           Tier-2 weights sum to the declared total
  lint             rubric_lint findings surfaced (vague language, bare-adjective anchors)
  tolerances       every T-id referenced by the rubric has a structurally
                   valid spec; duplicate ids rejected
  contamination    agent-namespace table must not reference *_judge* assets;
                   judge-namespace assets must actually ship in the package

Exit codes: 0 = clean, 1 = issues found, 2 = usage error.

Usage:
    python tools/playbook_check.py examples/synthetic-saas-analysis
    python tools/playbook_check.py <dir> --strict   # warnings also fail
"""

import argparse
import json
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
import rubric_lint  # noqa: E402


# ---------------------------------------------------------------- parsing

def load_tolerance_specs(path: Path):
    """Tolerances may be a JSON array or JSON-lines; return (specs, errors)."""
    text = path.read_text(encoding="utf-8").strip()
    errors, items = [], []
    try:
        data = json.loads(text)
        items = data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        for lineno, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            # JSON-lines files may carry `#` comment lines.
            if not line or line.startswith("#"):
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as e:
                errors.append(f"{path.name}:{lineno}: invalid JSON ({e})")
    specs = []
    for i, item in enumerate(items):
        if isinstance(item, dict):
            specs.append(item)
        else:
            errors.append(f"{path.name}: spec #{i} is not an object")
    return specs, errors


def parse_rubric(text: str):
    """Return (declared_weight_total, tier2_weights, tolerance_ids_referenced)."""
    m = re.search(r"weights sum to (\d+)", text, re.IGNORECASE)
    declared = int(m.group(1)) if m else None
    weights, tids = [], set()
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 3 and re.fullmatch(r"S\d+", cells[0]):
                if re.fullmatch(r"\d+", cells[2]):
                    weights.append(int(cells[2]))
        tids.update(re.findall(r"\bT\d+\b", line))
    return declared, weights, tids


def parse_spec_tables(text: str):
    """Return (agent_files, judge_files) referenced in the task-spec tables."""
    agent, judge, section = [], [], None
    for raw in text.splitlines():
        if raw.strip().startswith("#"):
            h = raw.lower()
            if "agent namespace" in h:
                section = "agent"
            elif "judge" in h:
                section = "judge"
            else:
                section = None
            continue
        s = raw.strip()
        if section and s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            first = cells[0] if cells else ""
            if (len(cells) >= 2 and first
                    and not set(first) <= set("-: ")
                    and first.lower() != "asset"):
                (agent if section == "agent" else judge).append(first)
    return agent, judge


# ---------------------------------------------------------------- checking

def _spec_covers_tid(spec_id: str, tid: str) -> bool:
    return spec_id == tid or spec_id.startswith(tid + "-")


def check_package(pkg: Path):
    errors, warnings = [], []
    tids = set()

    spec_path = pkg / "task-spec.md"
    rubric_path = next(iter(sorted(pkg.glob("rubric*.md"))), None)
    tol_path = next(iter(sorted(pkg.glob("tolerance*.json"))), None)

    if not spec_path.is_file():
        errors.append("structure: missing task-spec.md")
    if rubric_path is None:
        errors.append("structure: missing rubric file (rubric*.md)")
    if tol_path is None:
        errors.append("structure: missing tolerance specs (tolerance*.json)")

    agent_files, judge_files = [], []
    if spec_path.is_file():
        agent_files, judge_files = parse_spec_tables(
            spec_path.read_text(encoding="utf-8"))

    if rubric_path is not None:
        rtext = rubric_path.read_text(encoding="utf-8")
        declared, weights, tids = parse_rubric(rtext)

        if weights:
            total = sum(weights)
            if declared is None:
                warnings.append(f"rubric: Tier-2 weights sum to {total} "
                                "but no declared total found")
            elif total != declared:
                errors.append(f"rubric: Tier-2 weights sum to {total}, "
                              f"declared total is {declared}")

        lint_findings, lint_warnings = [], []
        for lineno, line in enumerate(rtext.splitlines(), 1):
            rubric_lint.lint_line(line, lineno, lint_findings, lint_warnings)
        rubric_lint.lint_anchors(rtext, lint_findings)
        errors += [f"rubric_lint: {f}" for f in lint_findings]
        warnings += [f"rubric_lint: {w}" for w in lint_warnings]

    if tol_path is not None:
        specs, load_errors = load_tolerance_specs(tol_path)
        errors += load_errors
        spec_ids = set()
        for item in specs:
            sid = item.get("id", "?")
            if sid in spec_ids:
                errors.append(f"{tol_path.name}: duplicate spec id '{sid}'")
            spec_ids.add(sid)
            errors += [f"{tol_path.name}:{sid}: {p}"
                       for p in _validate_spec(item)]
        if rubric_path is not None:
            for tid in sorted(tids):
                if not any(_spec_covers_tid(s, tid) for s in spec_ids):
                    errors.append(f"tolerances: rubric references {tid} "
                                  "but no spec with that id")
            for sid in sorted(spec_ids):
                if not any(_spec_covers_tid(sid, t) for t in tids):
                    warnings.append(f"tolerances: spec '{sid}' is not "
                                    "referenced by the rubric")

    for f in agent_files:
        if "_judge" in f.lower():
            errors.append(f"contamination: agent namespace references "
                          f"judge asset '{f}'")
        elif not (pkg / f).exists():
            warnings.append(f"inputs: '{f}' listed in agent namespace but not "
                            "in the package (external data?)")

    for f in judge_files:
        if not (pkg / f).exists():
            errors.append(f"packaging: judge asset '{f}' listed in task spec "
                          "but not shipped in the package")

    return errors, warnings


def _validate_spec(item: dict):
    """Structural check of one tolerance spec entry (reuses tolerance_check)."""
    import tolerance_check
    return tolerance_check.spec_problems(item.get("spec"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("package", type=Path, help="task package directory")
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as failures")
    args = parser.parse_args(argv)

    if not args.package.is_dir():
        print(f"error: not a directory: {args.package}", file=sys.stderr)
        return 2

    errors, warnings = check_package(args.package)
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    failed = len(errors) + (len(warnings) if args.strict else 0)
    print(f"\n{failed} issue(s) ({len(errors)} errors, {len(warnings)} warnings)")
    if failed:
        return 1
    print("Package clean: structure, rubric weights, tolerances, isolation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
