from openwish.model import needs_context, ready_tasks, review_needs, select_changes
from openwish.validation import validate

from tests.support import ProjectCase


class ModelTests(ProjectCase):
    def test_current_needs_remain_in_context_without_execution(self):
        self.fixture()
        self.assertIn("N-001", needs_context(self.project()))
        self.edit_document("needs/N-001.md", currency="retired")
        self.assertNotIn("N-001", needs_context(self.project()))
        self.assertEqual(review_needs(self.project(), "C-001"), ["N-001"])

    def test_changes_and_needs_are_many_to_many(self):
        self.fixture()
        self.add_need()
        self.edit_document("changes/C-001/change.md", needs=["N-001", "N-002"])
        self.add_change(needs=["N-002"])
        project = self.project()
        self.assertEqual(validate(project), [])
        self.assertEqual(select_changes(project, ["N-001"]), ["C-001"])
        self.assertEqual(select_changes(project, ["N-002"]), ["C-001", "C-002"])
        self.assertEqual(select_changes(project, ["N-002", "C-001"]), ["C-001", "C-002"])
        ready, _ = ready_tasks(project, ["N-001"])
        self.assertEqual([need["id"] for need in ready[0]["needs"]], ["N-001", "N-002"])

    def test_unlinked_current_needs_are_regression_constraints(self):
        self.fixture()
        self.add_need()
        self.assertEqual(review_needs(self.project(), "C-001"), ["N-001", "N-002"])
        self.assertEqual(select_changes(self.project(), ["N-002"]), [])

    def test_additional_need_constraints_are_never_silently_dropped_from_context(self):
        self.fixture()
        self.edit_document("needs/N-001.md", constraints=["All processing is offline"])
        self.assertIn("All processing is offline", needs_context(self.project()))

    def test_open_items_enter_context_marked_not_binding(self):
        self.fixture()
        self.edit_document("needs/N-001.md", open=["Should voided rows appear?"], constraints=["Offline"])
        lines = needs_context(self.project()).splitlines()
        self.assertIn('Open (not binding): ["Should voided rows appear?"]', lines)
        self.assertFalse([line for line in lines if line.startswith("Additional intent") and "voided" in line])

    def test_unsupported_toml_metadata_reports_an_error_before_projection(self):
        self.fixture()
        path = self.root / "openwish/needs/N-001.md"
        path.write_text(path.read_text().replace('confirmed_at = ""', 'confirmed_at = ""\ncustom = 2026-01-01'),
                        encoding="utf-8")
        self.assertIn("header values", "\n".join(validate(self.project())))

    def test_independent_work_continues_around_manual_and_explicit_blockers(self):
        self.fixture()
        self.write_tasks([self.task(kind="manual"),
                          self.task("C-001/T-002", depends_on=["C-001/T-001"]),
                          self.task("C-001/T-003"),
                          self.task("C-001/T-004", status="blocked", evidence="Access missing")])
        project = self.project()
        self.assertEqual(validate(project), [])
        ready, waiting = ready_tasks(project, ["N-001"])
        self.assertEqual([task["id"] for task in ready], ["C-001/T-003"])
        self.assertEqual(len(waiting), 3)
        self.assertIn("Access missing", waiting[-1]["blocker"])

    def test_dependencies_control_readiness_without_global_ordinals(self):
        self.fixture()
        self.write_tasks([self.task(depends_on=["C-001/T-002"]), self.task("C-001/T-002")])
        self.assertEqual(validate(self.project()), [])
        self.assertEqual([t["id"] for t in ready_tasks(self.project())[0]], ["C-001/T-002"])
        self.write_tasks([self.task(depends_on=["C-001/T-002"]),
                          self.task("C-001/T-002", status="done", evidence="Dependency checked")])
        self.assertEqual([t["id"] for t in ready_tasks(self.project())[0]], ["C-001/T-001"])

    def test_cycles_and_dangling_links_are_reported(self):
        self.fixture()
        self.write_tasks([self.task(depends_on=["C-001/T-002"]),
                          self.task("C-001/T-002", depends_on=["C-001/T-001"])])
        self.assertIn("cycle", "\n".join(validate(self.project())))
        self.write_tasks([self.task(depends_on=["C-999/T-001"])])
        self.assertIn("unknown depends_on", "\n".join(validate(self.project())))

    def test_cross_change_dependencies_cannot_prevent_disposal(self):
        self.fixture()
        self.add_change()
        self.write_tasks([self.task("C-002/T-001", depends_on=["C-001/T-001"])], "C-002")
        self.assertIn("within the change", "\n".join(validate(self.project())))

    def test_minimal_task_omits_optional_fields(self):
        self.fixture()
        self.write_tasks([{"id": "C-001/T-001", "title": "Export", "status": "open", "acceptance": "Rows match"}])
        self.assertEqual(validate(self.project()), [])
        self.assertEqual(len(ready_tasks(self.project())[0]), 1)

    def test_malformed_task_types_report_errors_instead_of_crashing(self):
        self.fixture()
        self.write_tasks([self.task(id=[], depends_on=None, files="app.py", status=[])])
        self.assertGreaterEqual(len(validate(self.project())), 4)

    def test_done_requires_evidence_and_completed_prerequisites(self):
        self.fixture()
        self.write_tasks([self.task(status="done")])
        self.assertIn("direct evidence", "\n".join(validate(self.project())))
        self.write_tasks([self.task(), self.task("C-001/T-002", depends_on=["C-001/T-001"],
                                               status="done", evidence="check passed")])
        self.assertIn("unfinished", "\n".join(validate(self.project())))

    def test_duplicate_task_ids_fail(self):
        self.fixture()
        self.write_tasks([self.task(), self.task()])
        self.assertIn("Duplicate task ID", "\n".join(validate(self.project())))

    def test_change_scope_must_be_nonempty_known_and_unique(self):
        self.fixture()
        for value in ([], None, "N-001", ["N-001", "N-001"], ["N-999"], [[]]):
            with self.subTest(needs=value):
                project = self.project()
                project["changes"]["C-001"]["meta"]["needs"] = value
                self.assertTrue(validate(project))

    def test_needs_preserve_intent_rather_than_conversation_asks(self):
        self.fixture()
        self.edit_document("needs/N-001.md", ask="Do this")
        errors = "\n".join(validate(self.project()))
        self.assertIn("not an ask field", errors)

    def test_orphan_change_directory_is_not_silently_ignored(self):
        (self.root / "openwish/changes/old-request").mkdir(parents=True)
        self.assertIn("Unrecognized change artifact", "\n".join(validate(self.project())))

    def test_nested_need_cannot_silently_leave_current_context(self):
        self.add_need()
        path = self.root / "openwish/needs/N-002.md"
        nested = path.parent / "privacy"
        nested.mkdir()
        path.rename(nested / path.name)
        self.assertIn("Unrecognized need artifact", "\n".join(validate(self.project())))
