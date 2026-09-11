#!/usr/bin/env python3
"""rubric_lint.py — flag vague, unscoreable language in a rubric draft.

A rubric criterion that contains adjectives like "reasonable" or "clearly"
cannot be applied consistently by two reviewers. This linter scans a
markdown rubric and reports:

  1. vague adjectives/adverbs that usually mark missing anchors
  2. tier rows whose anchor cells contain only adjectives (no verbs/numbers)

Exit codes: 0 = clean (or warnings only), 1 = findings present, 2 = usage error.

Usage:
    python tools/rubric_lint.py <rubric.md> [--strict]
    --strict  treat warnings as findings (non-zero exit)
"""

import argparse
import re
import sys
from pathlib import Path

# Words that almost always signal an un-anchorable criterion.
# Each entry: (pattern, suggestion)
VAGUE_TERMS = [
    (r"\breasonabl\w*\b", 'replace "reasonable" with a measurable anchor or a tolerance spec'),
    (r"\bappropriate\w*\b", 'replace "appropriate" with the specific expected behavior'),
    (r"\bclearly\b", '"clearly" is unverifiable; state what makes it clear (quote/number/reference)'),
    (r"\bgood\b", '"good" needs a 0/0.5/1.0 anchor definition'),
    (r"\bbad\b", '"bad" needs a 0/0.5/1.0 anchor definition'),
    (r"\badequate\w*\b", 'replace "adequate" with the minimum threshold (count/value/structure)'),
    (r"\bproper\w*\b", 'replace "proper" with the exact expected property'),
    (r"\bsome\b", '"some" is not a quantity; state how many or which'),
    (r"\bseveral\b", '"several" is not a quantity; state how many'),
    (r"\bfew\b", '"few" is not a quantity; state how many'),
    (r"\baccurate\w*\b", 'pair "accurate" with a tolerance spec (see docs/02)'),
    (r"\bthorough\w*\b", 'replace "thorough" with an inventory of what must be covered'),
    (r"\belegant\w*\b", '"elegant" is not scoreable; move to optional/tie-breaker tier or delete'),
]

# Verbs/numerals that suggest a cell actually contains an anchor.
ANCHOR_SIGNALS = re.compile(
    r"(\d|state[sd]?|cite[sd]?|quote[sd]?|list[sd]?|include[sd]?|shows?|shown|"
    r"derives?|derived|traceable|flag[sd]?|assumption|reference|step|number|"
    r"currency|unit|per\b|each\b|every\b|exactly|at least|at most|only|never)"
)


def lint_line(line: str, lineno: int, findings: list, warnings: list) -> None:
    """Check a single line for vague terms."""
    # Skip code blocks and the template's own placeholder rows.
    stripped = line.strip()
    if stripped.startswith("```") or stripped.startswith("> Example:"):
        return
    for pattern, suggestion in VAGUE_TERMS:
        m = re.search(pattern, line, re.IGNORECASE)
        if m:
            msg = f"line {lineno}: '{m.group(0)}' -> {suggestion}"
            if m.group(0).lower() in ("good", "bad"):
                warnings.append(msg)
            else:
                findings.append(msg)


def lint_anchors(text: str, findings: list) -> None:
    """Check table rows: anchor cells need verbs/numbers, not bare adjectives."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        # Rubric table rows typically have >= 4 cells (id, dimension, weight, anchors...).
        if len(cells) < 4:
            continue
        # Skip header and separator rows.
        if set(cells[0]) <= set("-: ") or cells[0].lower() in ("id", "tier", "dimension"):
            continue
        anchors = cells[3:]
        for cell in anchors:
            if cell and not ANCHOR_SIGNALS.search(cell.lower()):
                findings.append(
                    f"line {lineno}: anchor cell '{cell[:60]}' has no verb/number/quantity; "
                    "an anchor must describe observable behavior"
                )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("rubric", type=Path, help="path to the rubric markdown file")
    parser.add_argument("--strict", action="store_true", help="treat warnings as findings")
    args = parser.parse_args(argv)

    if not args.rubric.is_file():
        print(f"error: file not found: {args.rubric}", file=sys.stderr)
        return 2

    text = args.rubric.read_text(encoding="utf-8")
    findings, warnings = [], []
    for lineno, line in enumerate(text.splitlines(), start=1):
        lint_line(line, lineno, findings, warnings)
    lint_anchors(text, findings)

    for w in warnings:
        print(f"WARN  {w}")
    for f in findings:
        print(f"FIND  {f}")

    total = len(findings) + (len(warnings) if args.strict else 0)
    print(f"\n{total} issue(s) ({len(findings)} findings, {len(warnings)} warnings)")
    if total:
        print("A rubric two reviewers can disagree on is a spec bug, not a judgment call.")
        return 1
    print("Clean. Go run the adversarial-answer test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
