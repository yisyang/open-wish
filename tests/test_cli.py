import json

from openwish.workflow import clean_changes, close_changes

from tests.support import ProjectCase


class CliTests(ProjectCase):
    def test_ready_surfaces_unplanned_changes_before_and_after_predecessor_disposal(self):
        self.fixture()
        self.add_change("C-002")
        data = json.loads(self.cli("ready", "--json").stdout)
        self.assertEqual([task["id"] for task in data["ready"]], ["C-001/T-001"])
        self.assertEqual([change["id"] for change in data["unplanned"]], ["C-002"])
        self.finish_tasks()
        self.review()
        close_changes(self.project(), ["C-001"], "human")
        clean_changes(self.project(), ["C-001"])
        output = self.cli("ready").stdout
        self.assertIn("PLAN C-002", output)
        self.assertNotIn("C-001", output)
        self.write_tasks([self.task("C-002/T-001")], "C-002")
        self.assertFalse(json.loads(self.cli("ready", "--json").stdout)["unplanned"])

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

    def test_end_to_end_fast_forward_disposes_work_and_preserves_needs(self):
        self.fixture(mode="fast-forward")
        self.cli("check")
        ready = json.loads(self.cli("ready", "N-001", "--json").stdout)
        self.assertEqual(len(ready["ready"]), 1)
        self.assertEqual(ready["ready"][0]["needs"][0]["id"], "N-001")
        self.cli("task", "C-001/T-001", "done", success=False)
        self.cli("task", "C-001/T-001", "done", "--evidence", "Representative export check passed")
        self.cli("record-review", "C-001", "--summary", "Reconciliation verified",
                  "--check", "Representative export: passed", "--handoff", self.review_input())
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
                 "--check", "Local export passed", "--affected", "N-404", "--handoff", self.review_input(),
                 success=False)
        output = self.cli("record-review", "C-001", "--summary", "Local reconciliation verified",
                          "--check", "Local export passed", "--handoff", "-",
                          stdin=json.dumps({"handoff": [self.handoff()]})).stdout
        self.assertIn("assessed unaffected: N-002", output)
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
                  "--check", "Representative export passed",
                  "--handoff", self.review_input())
        self.cli("close", "C-001", "--by", "fast-forward")

    def test_mode_is_scoped_to_change(self):
        self.fixture()
        self.cli("mode", "fast-forward", "C-001")
        self.cli("new", "change", "C-002", "--title", "Follow-up", "--need", "N-001")
        self.assertEqual(self.project()["changes"]["C-002"]["meta"]["mode"], "default")

    def test_large_intent_remains_complete_and_inspection_works_over_soft_target(self):
        from openwish.storage import read_json, write_json
        self.fixture()
        path = self.root / "openwish/needs/N-001.md"
        path.write_text(path.read_text() + "\n" + "A meaningful rule.\n" * 600 + "FINAL EXCEPTION\n")
        config = self.root / "openwish/config.json"
        write_json(config, {**read_json(config), "needs_token_budget": 100})
        context = json.loads(self.cli("context", "C-001", "--json").stdout)
        self.assertIn("FINAL EXCEPTION", context["needs"])
        self.assertGreater(len(context["needs"].splitlines()), 500)
        self.assertEqual({item["category"] for item in context["retrieve"]}, {"changes", "tasks"})
        self.assertTrue(all(not item["included"] for item in context["retrieve"]))
        for command in ("status", "ready", "summary"):
            self.cli(command, *(["C-001"] if command == "summary" else []))
        self.assertFalse(json.loads(self.cli("check", "--json").stdout)["errors"])

    def test_detailed_references_are_sized_and_missing_or_ephemeral_paths_rejected(self):
        self.fixture()
        (self.root / "rules.md").write_text("Specific calibration retained here.\n")
        self.edit_document("needs/N-001.md", references=["rules.md"])
        context = json.loads(self.cli("context", "--json").stdout)
        self.assertEqual(context["retrieve"][0]["path"], "rules.md")
        self.assertNotIn("Specific calibration", context["needs"])
        self.assertGreater(context["estimated_tokens"]["references"], 0)
        (self.root / "rules.md").unlink()
        self.assertIn("does not exist", self.cli("check", success=False).stdout)
        self.edit_document("needs/N-001.md", references=["openwish/changes/C-001/change.md"])
        self.assertIn("disposable", self.cli("check", success=False).stdout)

    def test_review_requires_handoff_and_cleanup_preview_does_not_write(self):
        self.fixture()
        self.finish_tasks()
        result = self.cli("record-review", "C-001", "--summary", "Complete", "--check", "Checked",
                          success=False)
        self.assertIn("handoff", result.stderr)
        self.review()
        self.cli("close", "C-001", "--by", "human")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        preview = json.loads(self.cli("clean", "C-001", "--dry-run", "--json").stdout)
        self.assertEqual(len(preview["remove"]), 3)
        self.assertTrue(preview["handoff"]["C-001"])
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_summary_reports_malformed_handoff_instead_of_crashing(self):
        from openwish.storage import read_json, write_json
        self.fixture()
        self.finish_tasks()
        self.review()
        path = self.root / "openwish/changes/C-001/review.json"
        write_json(path, {**read_json(path), "handoff": [{"requirement": "Incomplete edit"}]})
        self.assertIn("Invalid handoff", self.cli("summary", "C-001").stdout)

    def test_unsupported_schema_fails_without_touching_files(self):
        path = self.root / "openwish/config.json"
        original = path.read_text().replace('"version": 4', '"version": 999')
        path.write_text(original, encoding="utf-8")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        for args in (("check",), ("init", "--harness", "opencode"),
                     ("skills", "--harness", "opencode"), ("new", "need", "N-001", "--title", "Need")):
            self.assertIn("expected 4", self.cli(*args, success=False).stderr)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.assertEqual(path.read_text(), original)

    def test_init_supports_multiple_and_repeated_harness_flags(self):
        output = self.cli("init", "--harness", "opencode", "claude", "--harness", "codex").stdout
        self.assertIn("Harnesses: opencode, claude, codex", output)
        for directory in (".opencode", ".claude", ".agents"):
            self.assertTrue((self.root / directory / "skills/ow-propose/SKILL.md").is_file())
        self.assertIn("38 unchanged", self.cli("init", "--harness", "opencode", "claude", "codex").stdout)

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
