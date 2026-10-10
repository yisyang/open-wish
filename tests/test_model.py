from openwish.model import connected_specs, needs_context, ready_tasks
from openwish.scaffold import new_artifact
from openwish.validation import validate

from tests.support import ProjectCase


class ModelTests(ProjectCase):
    def test_current_approved_needs_remain_in_global_context(self):
        self.fixture()
        self.edit_document("needs/N-001.md", implementation="approved")
        self.assertIn("N-001", needs_context(self.project()))
        self.edit_document("needs/N-001.md", currency="retired")
        self.assertNotIn("N-001", needs_context(self.project()))

    def test_spec_status_is_derived_from_authoritative_spec(self):
        self.fixture()
        self.edit_document("specs/S-001/spec.md", implementation="review")
        self.assertIn("S-001 (review)", needs_context(self.project()))

    def test_reverse_dependency_and_parent_are_in_impact_set(self):
        self.fixture()
        new_artifact(self.root, "spec", "S-002", "Consumer")
        self.edit_document("specs/S-002/spec.md", depends_on=["S-001"])
        self.edit_document("specs/S-002/design.md", needs=["N-001"])
        project = self.project()
        self.assertEqual(connected_specs(project, ["N-001"]), ["S-001", "S-002"])

    def test_later_independent_work_runs_while_manual_task_waits(self):
        self.fixture()
        self.write_tasks([self.task(kind="manual"), self.task("E-001/T-002", order=2)])
        project = self.project()
        self.assertEqual(validate(project), [])
        ready, waiting = ready_tasks(project, ["N-001"])
        self.assertEqual([task["id"] for task in ready], ["E-001/T-002"])
        self.assertEqual([task["id"] for task in waiting], ["E-001/T-001"])

    def test_prerequisite_blocks_dependent_but_not_other_work(self):
        self.fixture()
        self.write_tasks([self.task(kind="manual"),
                          self.task("E-001/T-002", order=2, depends_on=["E-001/T-001"]),
                          self.task("E-001/T-003", group=2, order=1)])
        project = self.project()
        ready, waiting = ready_tasks(project, ["N-001"])
        self.assertEqual([task["id"] for task in ready], ["E-001/T-003"])
        self.assertEqual(len(waiting), 2)

    def test_forward_dependencies_and_cycles_are_reported(self):
        self.fixture()
        self.write_tasks([self.task(depends_on=["E-001/T-002"]),
                          self.task("E-001/T-002", order=2, depends_on=["E-001/T-001"])])
        errors = "\n".join(validate(self.project()))
        self.assertIn("cycle", errors)
        self.assertIn("lower group/order", errors)

    def test_duplicate_ordinals_and_dangling_links_fail(self):
        self.fixture()
        self.write_tasks([self.task(), self.task("E-001/T-002")])
        self.assertIn("unique", "\n".join(validate(self.project())))
        self.write_tasks([self.task(depends_on=["E-999/T-001"])])
        self.assertIn("unknown depends_on", "\n".join(validate(self.project())))

    def test_malformed_task_types_report_errors_instead_of_crashing(self):
        self.fixture()
        self.write_tasks([self.task(id=[], group=True, depends_on=None, files="app.py")])
        errors = validate(self.project())
        self.assertGreaterEqual(len(errors), 4)

    def test_done_requires_evidence_and_completed_prerequisites(self):
        self.fixture()
        self.write_tasks([self.task(status="done")])
        self.assertIn("direct evidence", "\n".join(validate(self.project())))
        self.write_tasks([self.task(), self.task("E-001/T-002", order=2,
                          depends_on=["E-001/T-001"], status="done", evidence="check passed")])
        self.assertIn("unfinished", "\n".join(validate(self.project())))

    def test_spec_design_is_the_authoritative_need_reference(self):
        self.fixture()
        project = self.project()
        self.assertNotIn("needs", project["specs"]["S-001"]["meta"])
        self.assertEqual(project["specs"]["S-001"]["design"]["meta"]["needs"], ["N-001"])
        ready, _ = ready_tasks(project, ["N-001"])
        self.assertEqual(ready[0]["lineage"][0]["id"], "S-001")
        self.assertEqual(ready[0]["lineage"][0]["needs"][0]["outcome"], "Reconcile without retyping")

    def test_ask_metadata_is_rejected(self):
        self.fixture()
        self.edit_document("needs/N-001.md", ask="Do not persist this conversation input")
        self.assertIn("not an ask field", "\n".join(validate(self.project())))
