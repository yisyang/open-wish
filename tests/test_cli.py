import json
import os
from pathlib import Path
import subprocess
import sys

from tests.support import ProjectCase


class CliTests(ProjectCase):
    def test_graph_exposes_reasoned_intent_and_preserves_all_current_context(self):
        self.fixture()
        self.add_need()
        self.edit_document("needs/N-002.md", relations=[{
            "kind": "constrains", "need": "N-001", "reason": "Reconciliation stays local."}])
        graph = json.loads(self.cli("graph", "N-001", "--json").stdout)
        self.assertEqual(graph["relations"], [{"source": "N-002", "target": "N-001",
                                              "kind": "constrains", "reason": "Reconciliation stays local."}])
        self.assertIn("N-002 constrains N-001", self.cli("graph").stdout)
        self.assertIn("Reconciliation stays local.", self.cli("context", "N-001").stdout)
        self.cli("graph", "N-999", success=False)

    def cli(self, *arguments, success=True, cwd=None):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
        result = subprocess.run([sys.executable, "-m", "openwish", *arguments],
                                cwd=cwd or self.root, env=environment,
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0 if success else 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def test_end_to_end_fast_forward_disposes_work_and_preserves_needs(self):
        self.fixture(mode="fast-forward")
        self.cli("check")
        ready = json.loads(self.cli("ready", "N-001", "--json").stdout)
        self.assertEqual(len(ready["ready"]), 1)
        self.assertEqual(ready["ready"][0]["needs"][0]["id"], "N-001")
        self.finish_tasks()
        self.cli("record-review", "C-001", "--summary", "Reconciliation verified",
                 "--check", "Representative export: passed", "--covered-need", "N-001")
        self.cli("close", "C-001", "--by", "fast-forward")
        status = json.loads(self.cli("status", "--json").stdout)
        self.assertEqual(status["changes"][0]["closed_by"], "fast-forward")
        self.cli("clean", "C-001")
        self.assertIn("N-001", self.cli("context").stdout)
        self.assertFalse((self.root / "openwish/changes/C-001").exists())
        self.assertEqual(self.project()["needs"]["N-001"]["meta"]["confirmed_at"], "")
        self.cli("check")

    def test_many_to_many_scope_and_regression_review_through_cli(self):
        self.fixture()
        self.cli("new", "need", "N-002", "--title", "Privacy")
        self.edit_document("needs/N-002.md", actor="Staff", outcome="Keep data local",
                           acceptance=["No uploads"])
        self.cli("new", "change", "C-002", "--title", "Shared improvement", "--need", "N-001", "--need", "N-002")
        ready = json.loads(self.cli("ready", "N-001", "--json").stdout)
        self.assertEqual(len(ready["ready"]), 1)
        self.assertFalse(ready["waiting"])
        self.assertIn("N-001", self.cli("ready", "C-001").stdout)
        self.finish_tasks()
        self.cli("record-review", "C-001", "--summary", "Local reconciliation verified",
                 "--check", "Local export passed", "--covered-need", "N-001", success=False)
        self.cli("record-review", "C-001", "--summary", "Local reconciliation verified",
                 "--check", "Local export passed", "--covered-need", "N-001", "--covered-need", "N-002")
        self.cli("close", "C-001", "--by", "human")
        self.cli("clean", "C-001")
        self.assertEqual(self.project()["changes"]["C-002"]["meta"]["status"], "open")
        self.assertEqual(self.project()["needs"]["N-002"]["meta"]["currency"], "current")

    def test_final_summary_contains_need_change_outcome_and_evidence(self):
        self.fixture()
        self.finish_tasks()
        self.review()
        output = self.cli("summary", "N-001").stdout
        for text in ("N-001", "Reconcile without retyping", "C-001", "Improve reconciliation", "passed"):
            self.assertIn(text, output)

    def test_empty_project_passes_and_has_a_context(self):
        result = json.loads(self.cli("check", "--json").stdout)
        self.assertEqual(result, {"errors": [], "warnings": []})
        self.assertIn("Current needs", self.cli("context").stdout)

    def test_need_template_requires_completion_before_work(self):
        self.cli("new", "need", "N-001", "--title", "New need")
        self.assertIn("actor is required", self.cli("check", "--json", success=False).stdout)

    def test_ready_does_not_require_stage_receipts(self):
        self.fixture()
        result = json.loads(self.cli("ready", "N-001", "--json").stdout)
        self.assertEqual(len(result["ready"]), 1)
        self.assertEqual(result["waiting"], [])

    def test_malformed_json_has_an_actionable_error(self):
        (self.root / "openwish/config.json").write_text("{broken", encoding="utf-8")
        self.assertIn("Cannot read", self.cli("check", success=False).stderr)

    def test_json_check_remains_machine_readable_on_parse_failure(self):
        (self.root / "openwish/config.json").write_text("{broken", encoding="utf-8")
        result = json.loads(self.cli("check", "--json", success=False).stdout)
        self.assertIn("Cannot read", result["errors"][0])

    def test_root_flag_works_from_another_directory(self):
        self.assertIn("PASS", self.cli("--root", str(self.root), "check", cwd=self.root.parent).stdout)

    def test_verification_only_change_can_close_without_inventing_tasks(self):
        self.fixture(mode="fast-forward")
        self.write_tasks([])
        self.cli("record-review", "C-001", "--summary", "Existing behavior verified",
                 "--check", "Representative export passed", "--covered-need", "N-001")
        self.cli("close", "C-001", "--by", "fast-forward")

    def test_mode_is_scoped_to_change(self):
        self.fixture()
        self.cli("mode", "fast-forward", "C-001")
        self.cli("new", "change", "C-002", "--title", "Follow-up", "--need", "N-001")
        self.assertEqual(self.project()["changes"]["C-002"]["meta"]["mode"], "default")

    def test_unsupported_schema_fails_without_touching_files(self):
        path = self.root / "openwish/config.json"
        original = path.read_text().replace('"version": 3', '"version": 999')
        path.write_text(original, encoding="utf-8")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        for args in (("check",), ("init", "--harness", "opencode"),
                     ("skills", "--harness", "opencode"), ("new", "need", "N-001", "--title", "Need")):
            self.assertIn("expected 3", self.cli(*args, success=False).stderr)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.assertEqual(path.read_text(), original)

    def test_init_supports_multiple_and_repeated_harness_flags(self):
        output = self.cli("init", "--harness", "opencode", "claude", "--harness", "codex").stdout
        self.assertIn("Harnesses: opencode, claude, codex", output)
        for directory in (".opencode", ".claude", ".agents"):
            self.assertTrue((self.root / directory / "skills/ow-propose/SKILL.md").is_file())
        self.assertIn("37 unchanged", self.cli("init", "--harness", "opencode", "claude", "codex").stdout)

    def test_init_without_tty_requires_explicit_harnesses_and_writes_nothing(self):
        root = self.root / "new-project"
        result = self.cli("init", str(root), success=False)
        self.assertIn("No interactive terminal", result.stderr)
        self.assertFalse(root.exists())

    def test_init_cannot_downgrade_noninteractively(self):
        from unittest.mock import patch
        from openwish.integrations import install_skills
        with patch("openwish.integrations.__version__", "9.0.0"):
            install_skills(self.root, "opencode")
        result = self.cli("init", "--harness", "opencode", "claude", success=False)
        self.assertIn("Downgrade requires confirmation", result.stderr)
        self.assertFalse((self.root / ".claude").exists())
        self.assertIn("9.0.0", (self.root / ".opencode/skills/ow-propose/SKILL.md").read_text())
