import json
import os
from pathlib import Path
import subprocess
import sys

from tests.support import ProjectCase


class CliTests(ProjectCase):
    def cli(self, *arguments, success=True, cwd=None):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
        result = subprocess.run([sys.executable, "-m", "openwish", *arguments],
                                cwd=cwd or self.root, env=environment,
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0 if success else 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def test_end_to_end_fast_forward_is_addressed_by_need_id(self):
        self.fixture(mode="fast-forward")
        self.cli("check")
        for stage in ("needs", "align", "implement"):
            self.cli("gate", stage, "N-001", "--by", "fast-forward")
        ready = json.loads(self.cli("ready", "N-001", "--json").stdout)
        self.assertEqual(len(ready["ready"]), 1)
        self.assertEqual(ready["ready"][0]["lineage"][0]["id"], "S-001")
        self.finish_tasks()
        self.cli("record-review", "N-001", "--summary", "Reconciliation verified",
                 "--check", "Representative export: passed", "--covered-need", "N-001")
        self.cli("gate", "review", "N-001", "--by", "fast-forward")
        self.cli("approve", "N-001")
        status = json.loads(self.cli("status", "--json").stdout)
        self.assertNotIn("changes", status)
        self.assertEqual(status["needs"][0]["implementation"], "approved")
        self.assertIn("approved", self.cli("context").stdout)
        self.assertFalse((self.root / "openwish/changes").exists())

    def test_combined_authorization_and_scoped_shared_spec_through_cli(self):
        self.fixture()
        self.cli("new", "need", "N-002", "--title", "Privacy")
        self.edit_document("needs/N-002.md", actor="Staff", outcome="Keep data local",
                           acceptance=["No uploads"])
        self.edit_document("specs/S-001/design.md", needs=["N-001", "N-002"])
        self.edit_document("epics/E-001/design.md", needs=["N-001"])
        self.cli("authorize", "N-001", "--by", "human")
        ready = json.loads(self.cli("ready", "N-001", "--json").stdout)
        self.assertEqual(len(ready["ready"]), 1)
        self.assertFalse(ready["waiting"])
        self.assertEqual(ready["ready"][0]["execution_needs"], ["N-001"])
        self.assertIn("Execution needs: N-001", self.cli("ready", "N-001").stdout)
        self.finish_tasks()
        self.cli("record-review", "N-001", "--summary", "Local reconciliation verified",
                 "--check", "Local export passed", "--covered-need", "N-001", "--covered-need", "N-002")
        self.cli("approve", "N-001", success=False)
        self.cli("gate", "review", "N-001", "--by", "human")
        self.cli("approve", "N-001")
        self.assertEqual(self.project()["needs"]["N-001"]["meta"]["implementation"], "approved")
        self.assertEqual(self.project()["needs"]["N-002"]["meta"]["implementation"], "open")

    def test_final_summary_contains_need_spec_outcome_and_evidence(self):
        self.fixture()
        self.approve()
        self.finish_tasks()
        self.review()
        output = self.cli("summary", "N-001").stdout
        for text in ("N-001", "Reconcile without retyping", "S-001", "Export records", "passed"):
            self.assertIn(text, output)

    def test_empty_project_passes_and_has_a_context(self):
        result = json.loads(self.cli("check", "--json").stdout)
        self.assertEqual(result, {"errors": [], "warnings": []})
        self.assertIn("Current needs", self.cli("context").stdout)

    def test_need_template_requires_completion_before_decisions(self):
        self.cli("new", "need", "N-001", "--title", "New need")
        self.assertIn("actor is required", self.cli("check", "--json", success=False).stdout)

    def test_ready_reports_missing_authority_without_authorizing_work(self):
        self.fixture()
        result = json.loads(self.cli("ready", "N-001", "--json").stdout)
        self.assertEqual(result["ready"], [])
        self.assertIn("Missing or stale", result["waiting"][0]["blocker"])

    def test_malformed_json_has_an_actionable_error(self):
        (self.root / "openwish/config.json").write_text("{broken", encoding="utf-8")
        self.assertIn("Cannot read", self.cli("check", success=False).stderr)

    def test_json_check_remains_machine_readable_on_parse_failure(self):
        (self.root / "openwish/config.json").write_text("{broken", encoding="utf-8")
        result = json.loads(self.cli("check", "--json", success=False).stdout)
        self.assertIn("Cannot read", result["errors"][0])

    def test_root_flag_works_from_another_directory(self):
        self.assertIn("PASS", self.cli("--root", str(self.root), "check", cwd=self.root.parent).stdout)

    def test_no_work_need_can_be_verified_without_inventing_tasks(self):
        self.fixture(mode="fast-forward")
        self.edit_state(no_work_reason="Existing implementation satisfies the design")
        (self.root / "openwish/epics/E-001/design.md").unlink()
        (self.root / "openwish/epics/E-001/tasks.json").unlink()
        for stage in ("needs", "align", "implement"):
            self.cli("gate", stage, "N-001", "--by", "fast-forward")
        self.cli("record-review", "N-001", "--summary", "Existing behavior verified",
                 "--check", "Representative export passed", "--covered-need", "N-001")
        self.cli("gate", "review", "N-001", "--by", "fast-forward")
        self.cli("approve", "N-001")

    def test_reopen_resets_authority_without_creating_a_new_need(self):
        self.fixture(mode="fast-forward")
        self.approve(by="fast-forward")
        self.cli("reopen", "N-001")
        state = self.project()["needs"]["N-001"]["state"]
        self.assertEqual((state["revision"], state["mode"], state["gates"]), (2, "default", {}))
        self.assertEqual(len(self.project()["needs"]), 1)

    def test_legacy_schema_fails_explicitly_without_touching_files(self):
        path = self.root / "openwish/config.json"
        original = path.read_text().replace('"version": 2', '"version": 1')
        path.write_text(original, encoding="utf-8")
        self.assertIn("expected 2", self.cli("check", success=False).stderr)
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
