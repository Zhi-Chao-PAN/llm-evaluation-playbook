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
