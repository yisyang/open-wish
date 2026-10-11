from openwish.model import need_graph, needs_context, ready_tasks
from openwish.storage import WishError
from openwish.validation import validate
from openwish.workflow import clean_changes, close_changes, validate_review

from tests.support import ProjectCase


class RelationTests(ProjectCase):
    def linked(self):
        self.fixture()
        self.add_need()
        self.relation = {"kind": "constrains", "need": "N-001",
                         "reason": 'Reconciliation must keep "raw" records local.\nNo uploads.'}
        self.edit_document("needs/N-002.md", relations=[self.relation])

    def test_reasoned_relations_round_trip_enter_context_and_survive_disposal(self):
        self.linked()
        project = self.project()
        self.assertEqual(validate(project), [])
        self.assertEqual(project["needs"]["N-002"]["meta"]["relations"], [self.relation])
        self.assertIn("No uploads.", needs_context(project))
        before = need_graph(project)
        self.finish_tasks()
        self.review(needs=["N-001", "N-002"])
        close_changes(self.project(), ["C-001"], "human")
        clean_changes(self.project(), ["C-001"])
        self.assertEqual(need_graph(self.project()), before)
        self.assertFalse((self.root / "openwish/graph.json").exists())

    def test_selection_includes_incoming_and_outgoing_but_not_unrelated_edges(self):
        self.linked()
        self.add_need("N-003")
        self.add_need("N-004")
        self.edit_document("needs/N-001.md", relations=[
            {"kind": "requires", "need": "N-003", "reason": "Records must be available to reconcile."}])
        self.edit_document("needs/N-003.md", relations=[
            {"kind": "requires", "need": "N-004", "reason": "Separate prerequisite."}])
        graph = need_graph(self.project(), ["N-001"])
        self.assertEqual([n["id"] for n in graph["needs"]], ["N-001", "N-002", "N-003"])
        self.assertEqual(len(graph["relations"]), 2)
        with self.assertRaisesRegex(WishError, "Unknown need"):
            need_graph(self.project(), ["N-999"])

    def test_semantic_cycles_do_not_create_task_dependencies(self):
        self.linked()
        self.edit_document("needs/N-001.md", relations=[
            {"kind": "requires", "need": "N-002", "reason": "Local processing is necessary."}])
        self.assertEqual(validate(self.project()), [])
        self.assertEqual(len(ready_tasks(self.project())[0]), 1)
        self.assertEqual(len(need_graph(self.project())["relations"]), 2)

    def test_malformed_self_duplicate_and_unknown_relations_are_actionable(self):
        self.linked()
        for relations in (None, "N-001", [{}], [["N-001"]],
                          [{**self.relation, "kind": []}], [{**self.relation, "need": []}],
                          [{**self.relation, "reason": " "}], [{**self.relation, "need": "N-002"}],
                          [{**self.relation, "need": "N-999"}], [self.relation, self.relation]):
            with self.subTest(relations=relations):
                project = self.project()
                project["needs"]["N-002"]["meta"]["relations"] = relations
                self.assertTrue(validate(project))

    def test_retirement_requires_reconciling_current_links_but_preserves_history(self):
        self.linked()
        self.edit_document("needs/N-001.md", currency="retired")
        self.assertIn("retired need N-001", "\n".join(validate(self.project())))
        self.edit_document("needs/N-002.md", currency="retired")
        self.assertEqual(validate(self.project()), [])
        self.assertEqual({n["currency"] for n in need_graph(self.project())["needs"]}, {"retired"})
        (self.root / "openwish/needs/N-001.md").unlink()
        self.assertIn("unknown relation target", "\n".join(validate(self.project())))

    def test_changing_a_relationship_requires_fresh_review(self):
        self.linked()
        self.finish_tasks()
        self.review(needs=["N-001", "N-002"])
        self.edit_document("needs/N-002.md", relations=[{**self.relation, "reason": "Stricter local-only scope."}])
        with self.assertRaisesRegex(WishError, "stale"):
            validate_review(self.project(), "C-001")
