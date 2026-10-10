from openwish.budgets import check_budgets
from openwish.storage import read_json, write_json

from tests.support import ProjectCase


class BudgetTests(ProjectCase):
    def config(self, **kwargs):
        path = self.root / "openwish/config.json"
        write_json(path, {**read_json(path), **kwargs})

    def test_artifact_499_lines_passes_but_500_fails(self):
        path = self.root / "openwish/large.md"
        path.write_text("fact\n" * 499, encoding="utf-8")
        errors, warnings = check_budgets(self.project())
        self.assertEqual(errors, [])
        self.assertTrue(warnings)
        path.write_text("fact\n" * 500, encoding="utf-8")
        self.assertIn("under 500", "\n".join(check_budgets(self.project())[0]))

    def test_short_lines_do_not_bypass_the_global_token_budget(self):
        self.fixture()
        self.edit_document("needs/N-001.md", outcome="long outcome " * 100)
        self.config(needs_token_budget=100)
        self.assertIn("tokens", "\n".join(check_budgets(self.project())[0]))

    def test_source_soft_and_hard_boundaries(self):
        path = self.root / "app.py"
        path.write_text("pass\n" * 499, encoding="utf-8")
        self.assertEqual(check_budgets(self.project()), ([], []))
        path.write_text("pass\n" * 500, encoding="utf-8")
        errors, warnings = check_budgets(self.project())
        self.assertFalse(errors)
        self.assertIn("soft target", "\n".join(warnings))
        path.write_text("pass\n" * 1000, encoding="utf-8")
        self.assertIn("under 1000", "\n".join(check_budgets(self.project())[0]))

    def test_justified_source_exception_does_not_exempt_ow_knowledge(self):
        (self.root / "routes.py").write_text("pass\n" * 1100, encoding="utf-8")
        self.config(code_exceptions=[{"path": "routes.py", "kind": "low-complexity",
                                      "reason": "Flat generated routing declarations"}])
        errors, warnings = check_budgets(self.project())
        self.assertFalse(errors)
        self.assertIn("exception", "\n".join(warnings))
        (self.root / "openwish/routes.json").write_text("{}\n" * 500, encoding="utf-8")
        self.assertIn("under 500", "\n".join(check_budgets(self.project())[0]))

    def test_data_files_are_exempt_but_source_cannot_claim_to_be_data(self):
        (self.root / "data.json").write_text("{}\n" * 1100, encoding="utf-8")
        self.assertEqual(check_budgets(self.project()), ([], []))
        (self.root / "app.py").write_text("pass\n" * 1100, encoding="utf-8")
        self.config(code_exceptions=[{"path": "app.py", "kind": "data", "reason": "attempted bypass"}])
        self.assertIn("data-file extension", "\n".join(check_budgets(self.project())[0]))
