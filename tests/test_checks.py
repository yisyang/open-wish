import json
from pathlib import Path
import subprocess
import sys
import tempfile

from tests.support import ProjectCase


class RunCheckTests(ProjectCase):
    def setUp(self):
        super().setUp()
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        self.evidence = Path(outside.name)

    def run_check(self, *script, name="unit", code=0, attempts=None, evidence=None):
        options = ["--attempts", str(attempts)] if attempts else []
        return self.cli("run-check", "--name", name, "--evidence", str(evidence or self.evidence), *options,
                        "--", sys.executable, "-c", *script, code=code)

    def test_passing_check_writes_a_record_and_keeps_output_in_the_log(self):
        result = self.run_check("print('hello from the check')")
        self.assertIn("PASS unit: exit 0", result.stdout)
        self.assertNotIn("hello from the check", result.stdout)
        record = json.loads((self.evidence / "unit.json").read_text())
        self.assertEqual((record["status"], record["exit_code"]), ("PASS", 0))
        self.assertIn("hello from the check", Path(record["log"]).read_text())

    def test_failing_check_returns_its_exit_code_and_prints_the_log_tail(self):
        result = self.run_check("import sys; print('boom'); sys.exit(3)", code=3)
        self.assertIn("FAIL unit: exit 3", result.stdout)
        self.assertIn("boom", result.stdout)
        self.assertEqual(json.loads((self.evidence / "unit.json").read_text())["status"], "FAIL")

    def test_same_name_gets_a_new_record(self):
        self.run_check("pass")
        self.run_check("pass")
        self.assertTrue((self.evidence / "unit-2.json").exists())

    def test_fail_then_pass_is_flaky_not_pass(self):
        marker = self.evidence / "marker"
        script = ("import pathlib, sys; p = pathlib.Path(sys.argv[1]); seen = p.exists(); "
                  "p.touch(); sys.exit(0 if seen else 1)")
        result = self.run_check(script, str(marker), attempts=2, code=4)
        self.assertIn("FLAKY unit: exit 4 on attempt 2 of 2", result.stdout)
        record = json.loads((self.evidence / "unit.json").read_text())
        self.assertEqual(record["status"], "FLAKY")
        self.assertEqual(len(record["attempts"]), 2)

    def test_evidence_inside_the_repository_must_be_ignored(self):
        inside = self.root / "evidence"
        result = self.run_check("pass", evidence=inside, code=1)
        self.assertIn("outside the repository", result.stderr)
        self.assertFalse(inside.exists())
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / ".gitignore").write_text("evidence/\n", encoding="utf-8")
        self.run_check("pass", evidence=inside)
        self.assertTrue((inside / "unit.json").exists())
