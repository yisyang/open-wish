from openwish.budgets import check_budgets
from openwish.model import estimate_tokens, needs_context
from openwish.storage import read_json, write_json

from tests.support import ProjectCase


class BudgetTests(ProjectCase):
    def config(self, **kwargs):
        path = self.root / "openwish/config.json"
        write_json(path, {**read_json(path), **kwargs})

    def test_readable_artifacts_have_size_warnings_not_line_failures(self):
        path = self.root / "openwish/large.md"
        path.write_text("fact\n" * 499, encoding="utf-8")
        errors, warnings = check_budgets(self.project())
        self.assertEqual(errors, [])
        self.assertFalse(warnings)
        path.write_text("Important facts.\n" * 2000, encoding="utf-8")
        errors, warnings = check_budgets(self.project())
        self.assertFalse(errors)
        self.assertIn("preserve meaning", "\n".join(warnings))

    def test_needs_token_budget_is_a_soft_target(self):
        self.fixture()
        self.edit_document("needs/N-001.md", outcome="long outcome " * 100)
        self.config(needs_token_budget=100)
        errors, warnings = check_budgets(self.project())
        self.assertFalse(errors)
        self.assertIn("soft target", "\n".join(warnings))

    def test_context_warns_before_reaching_its_budget(self):
        self.fixture()
        tokens = estimate_tokens(needs_context(self.project()))
        self.config(needs_token_budget=tokens + 1)
        errors, warnings = check_budgets(self.project())
        self.assertFalse(errors)
        self.assertIn("review sizing and duplication", "\n".join(warnings))

    def test_source_soft_and_hard_boundaries(self):
        path = self.root / "app.py"
        path.write_text("pass\n" * 499, encoding="utf-8")
        self.assertEqual(check_budgets(self.project()), ([], []))
        path.write_text("pass\n" * 500, encoding="utf-8")
        errors, warnings = check_budgets(self.project())
        self.assertFalse(errors)
        self.assertIn("soft target", "\n".join(warnings))
        path.write_text("pass\n" * 1000, encoding="utf-8")
        self.assertFalse(check_budgets(self.project())[0])
        self.config(source_hard_limit=1000)
        self.assertIn("under 1000", "\n".join(check_budgets(self.project())[0]))

    def test_justified_source_exception_does_not_exempt_ow_knowledge(self):
        (self.root / "routes.py").write_text("pass\n" * 1100, encoding="utf-8")
        self.config(code_exceptions=[{"path": "routes.py", "kind": "low-complexity",
                                      "reason": "Flat generated routing declarations"}])
        errors, warnings = check_budgets(self.project())
        self.assertFalse(errors)
        self.assertIn("exception", "\n".join(warnings))
        (self.root / "openwish/routes.json").write_text("{}\n" * 500, encoding="utf-8")
        self.assertFalse(check_budgets(self.project())[0])

    def test_data_files_are_exempt_but_source_cannot_claim_to_be_data(self):
        (self.root / "data.json").write_text("{}\n" * 1100, encoding="utf-8")
        self.assertEqual(check_budgets(self.project()), ([], []))
        (self.root / "app.py").write_text("pass\n" * 1100, encoding="utf-8")
        self.config(code_exceptions=[{"path": "app.py", "kind": "data", "reason": "attempted bypass"}])
        self.assertIn("data-file extension", "\n".join(check_budgets(self.project())[0]))
