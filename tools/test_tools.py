#!/usr/bin/env python3
"""test_tools.py — unit tests for rubric_lint and tolerance_check.

Run with:  python tools/test_tools.py
No third-party dependencies; uses unittest from the standard library.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def run_tool(script: str, *args: str, stdin: str = None):
    return subprocess.run(
        [sys.executable, str(TOOLS / script), *args],
        capture_output=True, text=True, encoding="utf-8", input=stdin,
    )


class ToleranceCheckTests(unittest.TestCase):
    def _check(self, expected, spec, answer):
        r = run_tool("tolerance_check.py",
                     "--expected", str(expected),
                     "--spec", json.dumps(spec),
                     "--answer", str(answer))
        return r

    def test_absolute_pass_and_fail(self):
        spec = {"type": "absolute", "value": 50}
        self.assertEqual(self._check(1250, spec, 1290).returncode, 0)
        self.assertEqual(self._check(1250, spec, 1310).returncode, 1)

    def test_relative(self):
        spec = {"type": "relative", "value": 0.02}
        self.assertEqual(self._check(1250, spec, 1270).returncode, 0)   # 1.6% off
        self.assertEqual(self._check(1250, spec, 1290).returncode, 1)   # 3.2% off

    def test_points_boundary(self):
        spec = {"type": "points", "value": 0.5}
        self.assertEqual(self._check(12.4, spec, 12.9).returncode, 0)    # exactly 0.5
        self.assertEqual(self._check(12.4, spec, 12.91).returncode, 1)  # just outside

    def test_interval(self):
        spec = {"type": "interval", "low": 118, "high": 126}
        self.assertEqual(self._check(122, spec, 125.5).returncode, 0)
        self.assertEqual(self._check(122, spec, 126.5).returncode, 1)

    def test_set(self):
        # Numeric answer against a string set: no crash, just a clean FAIL.
        spec = {"type": "set", "values": ["A", "C"]}
        self.assertEqual(self._check(0, spec, 0).returncode, 1)
        # numeric set
        spec2 = {"type": "set", "values": [1, 2, 3]}
        self.assertEqual(self._check(0, spec2, 2).returncode, 0)
        self.assertEqual(self._check(0, spec2, 5).returncode, 1)

    def test_batch_mode(self):
        lines = "\n".join([
            json.dumps({"id": "Q1", "expected": 1250, "spec": {"type": "relative", "value": 0.02}, "answer": 1270}),
            json.dumps({"id": "Q2", "expected": 12.4, "spec": {"type": "points", "value": 0.5}, "answer": 13.0}),
        ])
        r = run_tool("tolerance_check.py", "--batch", stdin=lines)
        self.assertEqual(r.returncode, 1)  # Q2 fails
        self.assertIn("PASS  Q1", r.stdout)
        self.assertIn("FAIL  Q2", r.stdout)
        self.assertIn("1/2 passed", r.stdout)

    def test_bad_spec_errors(self):
        r = self._check(100, {"type": "nope", "value": 1}, 100)
        self.assertEqual(r.returncode, 2)

    def test_invalid_spec_values_are_rejected_without_tracebacks(self):
        invalid = [
            {"type": "relative", "value": -0.1},
            {"type": "absolute", "value": "invalid"},
            {"type": "points", "value": True},
            {"type": "absolute", "value": float("inf")},
            {"type": "interval", "low": 10, "high": 1},
            {"type": "interval", "low": float("nan"), "high": 1},
            {"type": "set", "values": []},
            {"type": "set", "values": "123"},
            {"type": "set", "values": [True]},
            {"type": "set", "values": [[1]]},
            {"type": []},
        ]
        for spec in invalid:
            with self.subTest(spec=spec):
                result = self._check(100, spec, 100)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_non_finite_operands_and_overflow_are_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity", "1e999"):
            with self.subTest(value=value):
                result = self._check(100, {"type": "absolute", "value": 1}, value)
                self.assertEqual(result.returncode, 2)
                result = self._check(value, {"type": "absolute", "value": 1}, 100)
                self.assertEqual(result.returncode, 2)
        result = self._check(1e308, {"type": "relative", "value": 10}, 100)
        self.assertEqual(result.returncode, 2)

    def test_batch_recovers_after_invalid_rows(self):
        good = {"id": "valid", "expected": 10,
                "spec": {"type": "absolute", "value": 0}, "answer": 10}
        bad_boolean = dict(good, expected=True)
        result = run_tool("tolerance_check.py", "--batch", stdin="\n".join([
            "{broken", "[]", "null", json.dumps(bad_boolean), json.dumps(good),
        ]))
        self.assertEqual(result.returncode, 2)
        self.assertIn("PASS  valid", result.stdout)
        self.assertIn("1/5 passed", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_empty_batch_is_not_a_successful_evaluation(self):
        result = run_tool("tolerance_check.py", "--batch", stdin="\n ")
        self.assertEqual(result.returncode, 2)

    def test_direct_calls_validate_specs(self):
        from tolerance_check import check_one
        with self.assertRaises(ValueError):
            check_one(100, {"type": "relative", "value": -0.1}, 100)

    def test_spec_validation_mode_single(self):
        # No --answer: structure check only.
        r = run_tool("tolerance_check.py",
                     "--expected", "4817500",
                     "--spec", '{"type":"relative","value":0.02}')
        self.assertEqual(r.returncode, 0)
        self.assertIn("SPEC-OK", r.stdout)
        # Structurally invalid spec fails even without an answer.
        r2 = run_tool("tolerance_check.py",
                      "--expected", "100",
                      "--spec", '{"type":"interval","low":1}')
        self.assertEqual(r2.returncode, 2)

    def test_spec_validation_mode_batch(self):
        lines = "\n".join([
            json.dumps({"id": "T1", "expected": 100, "spec": {"type": "absolute", "value": 5}, "answer": None}),
            json.dumps({"id": "T2", "expected": 100, "spec": {"type": "set", "values": [1, 2]}, "answer": 2}),
        ])
        r = run_tool("tolerance_check.py", "--batch", stdin=lines)
        self.assertEqual(r.returncode, 0)
        self.assertIn("SPEC-OK  T1", r.stdout)
        self.assertIn("PASS  T2", r.stdout)
        self.assertIn("2/2 passed", r.stdout)


EXAMPLE_PACKAGE = Path(__file__).resolve().parent.parent / "examples" / "synthetic-saas-analysis"


class PlaybookCheckTests(unittest.TestCase):
    def test_example_package_valid(self):
        r = run_tool("playbook_check.py", str(EXAMPLE_PACKAGE))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("Package clean", r.stdout)

    def test_example_package_strict_fails_on_warning(self):
        r = run_tool("playbook_check.py", str(EXAMPLE_PACKAGE), "--strict")
        # The example rubric intentionally quotes a vague phrase in its
        # anti-gaming section, which lints as a warning.
        self.assertEqual(r.returncode, 1)

    def test_broken_package_fails(self):
        with tempfile.TemporaryDirectory() as td:
            pkg = Path(td)
            (pkg / "task-spec.md").write_text(
                "# Task Spec — TEST\n\n"
                "## Inputs (agent namespace)\n\n"
                "| Asset | Format | Notes |\n|---|---|---|\n| data.csv | CSV | test |\n\n"
                "## Judge assets (judge namespace — never ship to agent)\n\n"
                "| Asset | Notes |\n|---|---|\n"
                "| rubric_judge.md | test |\n| tolerances_judge.json | test |\n",
                encoding="utf-8")
            # Weights sum to 55 but declare 100; references T1 with no spec.
            (pkg / "rubric_judge.md").write_text(
                "# Rubric\n\n"
                "## Tier 2 — Soft constraints (weights sum to 100)\n\n"
                "| ID | Dimension | Weight | 0 anchor | 0.5 anchor | 1.0 anchor |\n"
                "|---|---|---|---|---|---|\n"
                "| S1 | Chain | 30 | numbers appear without derivation | "
                "steps shown | every number traceable |\n"
                "| S2 | Assumption | 25 | none stated | stated | "
                "applied and sensitivity noted |\n\n"
                "## Tolerance specs\n\n"
                "| ID | Quantity | Expected | Band |\n|---|---|---|---|\n"
                "| T1 | Total | 100 | relative 2% |\n",
                encoding="utf-8")
            (pkg / "tolerances_judge.json").write_text(
                '{"id": "T9-total", "expected": 100, "spec": {"type": "relative", "value": 0.02}}',
                encoding="utf-8")
            r = run_tool("playbook_check.py", str(pkg))
            self.assertEqual(r.returncode, 1)
            self.assertIn("weights sum to 55", r.stdout)
            self.assertIn("T1", r.stdout)

    def test_contamination_detected(self):
        with tempfile.TemporaryDirectory() as td:
            pkg = Path(td)
            (pkg / "task-spec.md").write_text(
                "# Task Spec — TEST\n\n"
                "## Inputs (agent namespace)\n\n"
                "| Asset | Format | Notes |\n|---|---|---|\n"
                "| reference_answer_judge.md | MD | oops |\n\n"
                "## Judge assets (judge namespace)\n\n"
                "| Asset | Notes |\n|---|---|\n"
                "| rubric_judge.md | test |\n",
                encoding="utf-8")
            (pkg / "rubric_judge.md").write_text(
                "# Rubric\n\n## Tier 2 — Soft constraints (weights sum to 100)\n\n"
                "| ID | Dimension | Weight | 0 anchor | 1.0 anchor |\n|---|---|---|---|---|\n"
                "| S1 | Chain | 100 | numbers appear without derivation | every number traceable |\n",
                encoding="utf-8")
            (pkg / "tolerances_judge.json").write_text(
                '{"id": "T9", "expected": 1, "spec": {"type": "absolute", "value": 1}}',
                encoding="utf-8")
            r = run_tool("playbook_check.py", str(pkg))
            self.assertEqual(r.returncode, 1)
            self.assertIn("contamination", r.stdout)


class RubricLintTests(unittest.TestCase):
    def _lint(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(text)
            path = f.name
        return run_tool("rubric_lint.py", path)

    def test_vague_terms_flagged(self):
        r = self._lint("# Rubric\n\n- The answer must be reasonable and clearly accurate.\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("reasonable", r.stdout)
        self.assertIn("clearly", r.stdout)
        self.assertIn("accurate", r.stdout)

    def test_clean_rubric_passes(self):
        text = (
            "# Rubric\n\n"
            "## Tier 1\n\n"
            "| ID | Dimension | Weight | 0 anchor | 1.0 anchor |\n"
            "|---|---|---|---|---|\n"
            "| S1 | Chain transparency | 30 | numbers appear without derivation | "
            "every number traceable to input or a prior step |\n"
        )
        r = self._lint(text)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_adjective_only_anchor_flagged(self):
        text = (
            "| ID | Dimension | Weight | 0 anchor | 1.0 anchor |\n"
            "|---|---|---|---|---|\n"
            "| S1 | Structure | 20 | messy | very nice |\n"
        )
        r = self._lint(text)
        self.assertEqual(r.returncode, 1)
        self.assertIn("anchor cell", r.stdout)

    def test_missing_file_is_usage_error(self):
        r = run_tool("rubric_lint.py", "does_not_exist.md")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
