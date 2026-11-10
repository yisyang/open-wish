"""The dry-run judge validates what a grading agent writes; a fake agent stands in for a model."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ow_eval_runner_judge", ROOT / "evals/run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

ITEM = {"id": 99, "name": "fake", "prompt": "Do the task.", "expected_output": "It is done.",
        "assertions": ["States the outcome.", "Asks no question."], "files": [], "skills": []}


class EvalJudgeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.workspace = Path(temp.name)
        runner.shim(self.workspace)
        self.stage = runner.arm_dir(self.workspace, ITEM, "skills") / "stage-1"
        self.stage.mkdir(parents=True)
        (self.stage / "response.md").write_text("Done.\n", encoding="utf-8")

    def agent(self, written):
        script = self.workspace / "fake_judge.py"
        script.write_text("import pathlib, sys\n"
                          f"pathlib.Path(sys.argv[1], 'judgement.json').write_text({written!r})\n", encoding="utf-8")
        return {"name": "custom", "harness": "generic", "command": f"{sys.executable} {script} {{stage_dir}}"}

    def test_valid_verdicts_are_counted_and_failed_assertions_named(self):
        written = json.dumps({"assertions": [{"n": 1, "verdict": "pass", "evidence": "Done."},
                                             {"n": 2, "verdict": "fail", "evidence": "none"}]})
        result = runner.judge(self.workspace, ITEM, "skills", self.agent(written), 60)
        self.assertEqual(result, {"status": "judged", "passed": 1, "total": 2, "failed": ["Asks no question."]})
        self.assertTrue((self.stage / "judge-transcript.txt").exists())

    def test_malformed_or_incomplete_verdicts_are_rejected_and_can_be_rejudged(self):
        for written in ("not json", json.dumps({"assertions": [{"n": 1, "verdict": "pass"}]})):
            with self.subTest(written=written):
                result = runner.judge(self.workspace, ITEM, "skills", self.agent(written), 60)
                self.assertTrue(result["status"].startswith("judge failed"))
                self.assertFalse((self.stage / "judgement.json").exists())

    def test_line_metrics_count_tests_apart_from_source(self):
        product = self.workspace / "product"
        (product / "tests").mkdir(parents=True)
        (product / "app.py").write_text("a = 1\n\nb = 2\n", encoding="utf-8")
        (product / "tests/test_app.py").write_text("import app\n", encoding="utf-8")
        (product / "test_more.py").write_text("x = 1\ny = 2\n", encoding="utf-8")
        self.assertEqual(runner.line_metrics(product), {"source": 2, "tests": 3})


if __name__ == "__main__":
    unittest.main()
