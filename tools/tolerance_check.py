#!/usr/bin/env python3
"""tolerance_check.py — validate a numeric answer against a tolerance spec.

Implements the band types described in docs/02-numeric-tolerances.md:

    absolute   |expected - answer| <= value
    relative   |expected - answer| <= value * |expected|
    points     |expected - answer| <= value      (percentage POINTS, not %)
    interval   low <= answer <= high
    set        answer is an exact member of values

Spec-validation mode: omit --answer (or use "answer": null in batch mode)
to validate the spec structure only — useful for CI and packaging checks.

Exit codes: 0 = pass, 1 = fail, 2 = usage/spec error.

Usage:
    python tools/tolerance_check.py \
        --expected 12.4 --spec '{"type":"points","value":0.5}' --answer 12.8

    # spec definition only (no answer yet)
    python tools/tolerance_check.py \
        --expected 12.4 --spec '{"type":"points","value":0.5}'

    # batch mode: one JSON object per line on stdin
    echo '{"id":"Q1","expected":1250,"spec":{"type":"relative","value":0.02},"answer":1280}' \
        | python tools/tolerance_check.py --batch
"""

import argparse
import json
import math
import sys

VALID_TYPES = {"absolute", "relative", "points", "interval", "set"}
REQUIRED_KEYS = {
    "absolute": ("value",),
    "relative": ("value",),
    "points": ("value",),
    "interval": ("low", "high"),
    "set": ("values",),
}


def _finite_number(value) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def spec_problems(spec) -> list:
    """Validate the values as well as the shape of a tolerance spec."""
    if not isinstance(spec, dict):
        return [f"spec must be an object, got {type(spec).__name__}"]
    t = spec.get("type")
    if not isinstance(t, str) or t not in VALID_TYPES:
        return [f"unknown tolerance type: {t!r}"]
    missing = [k for k in REQUIRED_KEYS[t] if k not in spec]
    if missing:
        return [f"spec type '{t}' requires '{k}'" for k in missing]
    if t in {"absolute", "relative", "points"}:
        if not _finite_number(spec["value"]) or spec["value"] < 0:
            return ["value must be a finite, non-negative number"]
    elif t == "interval":
        if not all(_finite_number(spec[k]) for k in ("low", "high")):
            return ["interval bounds must be finite numbers"]
        if spec["low"] > spec["high"]:
            return ["interval low must not exceed high"]
    elif t == "set":
        values = spec["values"]
        if not isinstance(values, list) or not values:
            return ["values must be a non-empty list"]
        if any(not isinstance(v, str) and not _finite_number(v) for v in values):
            return ["set members must be strings or finite numbers"]
    return []


def check_one(expected: float, spec: dict, answer: float) -> dict:
    """Return {'pass': bool, 'diff': float, 'band': str} for a single answer."""
    problems = spec_problems(spec)
    if problems:
        raise ValueError("; ".join(problems))
    expected = _parse_number(expected, "expected")
    answer = _parse_number(answer, "answer")
    t = spec.get("type")
    if t == "absolute":
        diff = abs(expected - answer)
        ok = diff <= spec["value"]
        band = f"|{expected} - {answer}| <= {spec['value']}"
    elif t == "relative":
        diff = abs(expected - answer)
        limit = spec["value"] * abs(expected)
        if not math.isfinite(limit):
            raise ValueError("relative tolerance produces a non-finite bound")
        ok = diff <= limit
        band = f"|{expected} - {answer}| <= {spec['value']}*|{expected}| ({limit:.6g})"
    elif t == "points":
        # Percentage POINTS: identical arithmetic to absolute, different intent.
        # Kept as a distinct type so specs are self-documenting.
        diff = abs(expected - answer)
        ok = diff <= spec["value"]
        band = f"|{expected} - {answer}| <= {spec['value']} pp"
    elif t == "interval":
        low, high = spec["low"], spec["high"]
        diff = 0.0 if low <= answer <= high else min(abs(answer - low), abs(answer - high))
        ok = low <= answer <= high
        band = f"{low} <= {answer} <= {high}"
    elif t == "set":
        values = spec["values"]
        try:
            ok = answer in values
        except TypeError:
            ok = False
        diff = 0.0
        band = f"{answer} in {values}"
    else:
        raise ValueError(f"unknown tolerance type: {t!r}")
    return {"pass": ok, "diff": diff, "band": band}


def _parse_number(value, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric, not boolean")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f"{name} must be a finite number, got: {value!r}")
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite, got: {value!r}")
    return number


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expected", help="expected (gold) numeric value")
    parser.add_argument("--spec", help='tolerance spec JSON, e.g. {"type":"points","value":0.5}')
    parser.add_argument("--answer", help="the numeric answer under test")
    parser.add_argument("--batch", action="store_true",
                        help="read JSON lines {id, expected, spec, answer} from stdin")
    args = parser.parse_args(argv)

    if args.batch:
        failed = 0
        errors = 0
        total = 0
        for line_number, line in enumerate(sys.stdin, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError("each row must be a JSON object")
            except (ValueError, json.JSONDecodeError) as e:
                print(f"ERROR  line {line_number}: {e}")
                failed += 1
                errors += 1
                continue
            sid = item.get("id", "?")
            try:
                expected = _parse_number(item["expected"], "expected")
            except (KeyError, ValueError) as e:
                print(f"ERROR  {sid}: {e}")
                failed += 1
                errors += 1
                continue
            problems = spec_problems(item.get("spec"))
            if problems:
                print(f"BAD-SPEC  {sid}: " + "; ".join(problems))
                failed += 1
                errors += 1
                continue
            if item.get("answer") is None:
                print(f"SPEC-OK  {sid}: type={item['spec']['type']} (definition only, no answer)")
                continue
            try:
                r = check_one(expected, item["spec"], _parse_number(item["answer"], "answer"))
            except ValueError as e:
                print(f"ERROR  {sid}: {e}")
                failed += 1
                errors += 1
                continue
            status = "PASS" if r["pass"] else "FAIL"
            if not r["pass"]:
                failed += 1
            print(f"{status}  {sid}: {r['band']}")
        print(f"\n{total - failed}/{total} passed")
        if total == 0:
            print("error: batch contains no records", file=sys.stderr)
            return 2
        return 2 if errors else (0 if failed == 0 else 1)

    if not (args.expected and args.spec):
        parser.print_help()
        return 2

    try:
        expected = _parse_number(args.expected, "--expected")
        spec = json.loads(args.spec)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    problems = spec_problems(spec)
    if problems:
        for p in problems:
            print(f"error: {p}", file=sys.stderr)
        return 2

    # Spec-validation mode: no answer given, structure check only.
    if args.answer is None:
        print(f"SPEC-OK  type={spec['type']} (definition only, no answer)")
        return 0

    try:
        answer = _parse_number(args.answer, "--answer")
        result = check_one(expected, spec, answer)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(f"{'PASS' if result['pass'] else 'FAIL'}  {result['band']}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
