import json

from openwish.repository import project_files
from openwish.trace import is_check, trace_data
from openwish.workflow import clean_changes, close_changes

from tests.support import ProjectCase


class TraceTests(ProjectCase):
    def setUp(self):
        super().setUp()
        self.fixture()
        self.add_need()

    def trace(self, *keys):
        return trace_data(self.project(), project_files(self.root), keys)

    def test_need_mentions_in_tests_are_traced_as_checks(self):
        (self.root / "tests").mkdir()
        (self.root / "tests/test_export.py").write_text("# Protects N-001: no manual row copying\n")
        (self.root / "app.py").write_text("# Implements N-001 export\ndef export():\n    return []\n")
        data = self.trace()
        self.assertEqual(data["needs"][0]["checks"], ["tests/test_export.py"])
        self.assertEqual(data["needs"][0]["files"], ["app.py"])
        self.assertEqual(data["untraced_current"], ["N-002"])
        self.assertEqual(self.trace("N-002")["needs"][0]["checks"], [])

    def test_check_warns_about_unknown_and_retired_need_mentions_but_not_installed_guidance(self):
        self.cli("init", "--harness", "claude")
        (self.root / "app.py").write_text("# See N-009 and N-002\n")
        self.edit_document("needs/N-002.md", currency="retired")
        output = self.cli("check").stdout
        self.assertIn("app.py: mentions unknown need N-009", output)
        self.assertIn("app.py: mentions retired need N-002", output)
        self.assertNotIn(".claude", output)
        self.assertNotIn("N-009", self.cli("check", "--artifacts-only").stdout)

    def test_trace_cli_and_cleanup_report_change_mentions_in_code(self):
        (self.root / "app.py").write_text("# Approach decided in C-001\n")
        data = json.loads(self.cli("trace", "--json").stdout)
        self.assertEqual(data["change_mentions"], {"app.py": ["C-001"]})
        self.assertIn("N-001", self.cli("trace", "N-001").stdout)
        self.finish_tasks()
        self.review()
        close_changes(self.project(), ["C-001"], "human")
        report = clean_changes(self.project(), ["C-001"], dry_run=True)
        self.assertIn("app.py", " ".join(report["warnings"]))

    def test_conventional_test_locations(self):
        for path in ("tests/x.py", "pkg/test_x.py", "x_test.go", "a/b.spec.ts", "src/__tests__/x.js"):
            self.assertTrue(is_check(path), path)
        for path in ("src/testing_utils.py", "contest.py", "docs/latest.md"):
            self.assertFalse(is_check(path), path)
