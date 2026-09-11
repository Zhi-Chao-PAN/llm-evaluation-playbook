#!/usr/bin/env python3
"""tolerance_check.py — validate a numeric answer against a tolerance spec.

Implements the band types described in docs/02-numeric-tolerances.md:

    absolute   |expected - answer| <= value
    relative   |expected - answer| <= value * |expected|
    points     |expected - answer| <= value      (percentage POINTS, not %)
    interval   low <= answer <= high
    set        answer is an exact member of values

Exit codes: 0 = pass, 1 = fail, 2 = usage/spec error.

Usage:
    python tools/tolerance_check.py \
        --expected 12.4 --spec '{"type":"points","value":0.5}' --answer 12.8

    # batch mode: one JSON object per line on stdin
    echo '{"id":"Q1","expected":1250,"spec":{"type":"relative","value":0.02},"answer":1280}' \
        | python tools/tolerance_check.py --batch
"""

import argparse
import json
import sys


def check_one(expected: float, spec: dict, answer: float) -> dict:
    """Return {'pass': bool, 'diff': float, 'band': str} for a single answer."""
    t = spec.get("type")
    if t == "absolute":
        diff = abs(expected - answer)
        ok = diff <= spec["value"]
        band = f"|{expected} - {answer}| <= {spec['value']}"
    elif t == "relative":
        diff = abs(expected - answer)
        limit = spec["value"] * abs(expected)
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
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be numeric, got: {value!r}")


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
        total = 0
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            total += 1
            try:
                r = check_one(
                    _parse_number(item["expected"], "expected"),
                    item["spec"],
                    _parse_number(item["answer"], "answer"),
                )
            except (KeyError, ValueError) as e:
                print(f"ERROR  {item.get('id', '?')}: {e}")
                failed += 1
                continue
            status = "PASS" if r["pass"] else "FAIL"
            if not r["pass"]:
                failed += 1
            print(f"{status}  {item.get('id', '?')}: {r['band']}")
        print(f"\n{total - failed}/{total} passed")
        return 0 if failed == 0 else 1

    if not (args.expected and args.spec and args.answer):
        parser.print_help()
        return 2

    try:
        expected = _parse_number(args.expected, "--expected")
        answer = _parse_number(args.answer, "--answer")
        spec = json.loads(args.spec)
        result = check_one(expected, spec, answer)
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(f"{'PASS' if result['pass'] else 'FAIL'}  {result['band']}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
