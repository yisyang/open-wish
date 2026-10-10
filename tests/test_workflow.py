from openwish.scaffold import new_artifact
from openwish.storage import WishError, read_json
from openwish.workflow import (approve_needs, authorized_tasks, gate_valid, record_gate,
                               record_review, reopen_needs, set_mode, validate_review)

from tests.support import ProjectCase


class WorkflowTests(ProjectCase):
    def test_combined_authorization_keeps_final_acceptance_separate(self):
        self.fixture()
        record_gate(self.project(), ["N-001"], "implement", "human", through=True)
        need = self.project()["needs"]["N-001"]
        self.assertEqual(set(need["state"]["gates"]), {"needs", "align", "implement"})
        self.assertTrue(need["meta"]["confirmed_at"])
        self.assertTrue(gate_valid(self.project(), "N-001", "implement"))
        self.finish_tasks()
        self.review()
        with self.assertRaisesRegex(WishError, "missing or stale"):
            approve_needs(self.project(), ["N-001"])

    def test_combined_authorization_preflights_plan_and_entire_selection(self):
        self.fixture()
        self.add_second_need()
        before = self.project()["needs"]["N-001"]["state"]
        with self.assertRaisesRegex(WishError, "linked spec"):
            record_gate(self.project(), ["N-001", "N-002"], "implement", "human", through=True)
        self.assertEqual(self.project()["needs"]["N-001"]["state"], before)
        self.assertEqual(self.project()["needs"]["N-001"]["meta"]["confirmed_at"], "")
        self.write_tasks([])
        with self.assertRaisesRegex(WishError, "epics with tasks"):
            record_gate(self.project(), ["N-001"], "implement", "human", through=True)
        self.assertEqual(self.project()["needs"]["N-001"]["state"], before)

    def test_combined_fast_forward_requires_mode_and_preserves_provenance(self):
        self.fixture()
        with self.assertRaisesRegex(WishError, "explicitly enabling"):
            record_gate(self.project(), ["N-001"], "implement", "fast-forward", through=True)
        set_mode(self.project(), ["N-001"], "fast-forward")
        record_gate(self.project(), ["N-001"], "implement", "fast-forward", through=True)
        self.assertEqual(self.project()["needs"]["N-001"]["meta"]["confirmed_at"], "")
        self.assertTrue(gate_valid(self.project(), "N-001", "implement"))

    def test_individual_gates_require_sequential_decisions_for_a_need(self):
        self.fixture()
        with self.assertRaisesRegex(WishError, "missing or stale"):
            record_gate(self.project(), ["N-001"], "implement", "human")
        with self.assertRaisesRegex(WishError, "explicitly enabling"):
            record_gate(self.project(), ["N-001"], "needs", "fast-forward")
        self.approve()
        self.assertEqual(self.project()["needs"]["N-001"]["meta"]["implementation"], "in-progress")
        self.finish_tasks()
        self.review()
        with self.assertRaisesRegex(WishError, "missing or stale"):
            approve_needs(self.project(), ["N-001"])
        record_gate(self.project(), ["N-001"], "review", "human")
        approve_needs(self.project(), ["N-001"])
        meta = self.project()["needs"]["N-001"]["meta"]
        self.assertEqual((meta["currency"], meta["implementation"]), ("current", "approved"))
        self.assertTrue(meta["confirmed_at"] and meta["verified_at"])

    def test_fast_forward_approves_without_claiming_human_confirmation(self):
        self.fixture(mode="fast-forward")
        self.approve(by="fast-forward")
        self.finish_tasks()
        self.review()
        record_gate(self.project(), ["N-001"], "review", "fast-forward")
        approve_needs(self.project(), ["N-001"])
        need = self.project()["needs"]["N-001"]
        self.assertEqual(need["meta"]["confirmed_at"], "")
        self.assertEqual(need["meta"]["implementation"], "approved")
        self.assertTrue(all(gate["by"] == "fast-forward" for gate in need["state"]["gates"].values()))

    def test_need_revision_invalidates_downstream_authority(self):
        self.fixture()
        self.approve()
        self.edit_document("needs/N-001.md", outcome="Reconcile offline")
        self.assertFalse(gate_valid(self.project(), "N-001", "implement"))
        with self.assertRaisesRegex(WishError, "missing or stale"):
            self.review()

    def test_progress_preserves_plan_but_task_definition_invalidates_it(self):
        self.fixture()
        self.approve()
        self.finish_tasks()
        self.assertTrue(gate_valid(self.project(), "N-001", "implement"))
        self.write_tasks([self.task(acceptance="Export offline")])
        self.assertFalse(gate_valid(self.project(), "N-001", "implement"))
        self.assertTrue(gate_valid(self.project(), "N-001", "align"))

    def test_renewing_a_decision_clears_later_receipts(self):
        self.fixture()
        self.approve()
        record_gate(self.project(), ["N-001"], "needs", "human")
        self.assertEqual(set(self.project()["needs"]["N-001"]["state"]["gates"]), {"needs"})

    def test_fast_forward_cannot_skip_manual_work(self):
        self.fixture(mode="fast-forward")
        self.write_tasks([self.task(kind="manual")])
        self.approve(by="fast-forward")
        with self.assertRaisesRegex(WishError, "Unfinished work"):
            self.review()

    def test_code_edits_after_review_require_refreshed_verification(self):
        self.fixture()
        self.approve()
        self.finish_tasks()
        self.review()
        (self.root / "app.py").write_text("raise RuntimeError('regression')\n", encoding="utf-8")
        with self.assertRaisesRegex(WishError, "repository files changed"):
            record_gate(self.project(), ["N-001"], "review", "human")

    def test_new_untracked_file_invalidates_review(self):
        self.fixture()
        self.approve()
        self.finish_tasks()
        self.review()
        (self.root / "new.py").write_text("pass\n", encoding="utf-8")
        with self.assertRaisesRegex(WishError, "repository files changed"):
            validate_review(self.project(), "N-001")

    def test_revised_task_results_invalidate_review(self):
        self.fixture()
        self.approve()
        self.finish_tasks()
        self.review()
        self.write_tasks([self.task(status="done", evidence="Different checks were performed")])
        with self.assertRaisesRegex(WishError, "task results changed"):
            validate_review(self.project(), "N-001")

    def test_review_requires_direct_results_and_need_coverage(self):
        self.fixture()
        self.approve()
        self.finish_tasks()
        with self.assertRaisesRegex(WishError, "affected needs"):
            record_review(self.project(), ["N-001"], "Fine", ["check passed"], [], "pass")
        with self.assertRaisesRegex(WishError, "direct check"):
            record_review(self.project(), ["N-001"], "Fine", [], ["N-001"], "pass")

    def test_mode_is_need_owned_and_invalidates_authority(self):
        self.fixture(mode="fast-forward")
        self.approve(by="fast-forward")
        set_mode(self.project(), ["N-001"], "default")
        self.assertFalse(gate_valid(self.project(), "N-001", "implement"))

    def test_reopening_keeps_identity_and_resets_fast_forward(self):
        self.fixture(mode="fast-forward")
        self.approve(by="fast-forward")
        self.finish_tasks()
        self.review()
        record_gate(self.project(), ["N-001"], "review", "fast-forward")
        approve_needs(self.project(), ["N-001"])
        with self.assertRaisesRegex(WishError, "Reopen"):
            record_gate(self.project(), ["N-001"], "needs", "human")
        reopen_needs(self.project(), ["N-001"])
        need = self.project()["needs"]["N-001"]
        self.assertEqual((need["meta"]["id"], need["meta"]["implementation"]), ("N-001", "open"))
        self.assertEqual(need["state"], {"revision": 2, "mode": "default", "no_work_reason": "", "gates": {}})
        with self.assertRaisesRegex(WishError, "approved plan changed"):
            validate_review(self.project(), "N-001")
        self.assertFalse((self.root / "openwish/changes").exists())

    def test_latest_review_is_replaced_on_the_need(self):
        self.fixture()
        self.approve()
        self.finish_tasks()
        self.review()
        self.review()
        path = self.root / "openwish/needs/N-001.review.json"
        self.assertEqual(read_json(path)["verdict"], "pass")
        self.assertEqual(len(list(path.parent.glob("*.review.json"))), 1)

    def add_second_need(self):
        new_artifact(self.root, "need", "N-002", "Private reconciliation")
        self.edit_document("needs/N-002.md", actor="Operations staff", outcome="Keep records local",
                           acceptance=["No raw records leave the device"])

    def test_shared_spec_work_requires_authority_for_both_open_needs(self):
        self.fixture()
        self.add_second_need()
        self.edit_document("specs/S-001/design.md", needs=["N-001", "N-002"])
        self.approve()
        ready, waiting = authorized_tasks(self.project(), ["N-001"])
        self.assertFalse(ready)
        self.assertIn("N-002", waiting[0]["blocker"])
        for stage in ("needs", "align", "implement"):
            record_gate(self.project(), ["N-002"], stage, "human")
        self.assertEqual(len(authorized_tasks(self.project(), ["N-001", "N-002"])[0]), 1)

    def test_scoped_epic_does_not_authorize_or_block_on_regression_needs(self):
        self.fixture()
        self.add_second_need()
        self.edit_document("specs/S-001/design.md", needs=["N-001", "N-002"])
        self.edit_document("epics/E-001/design.md", needs=["N-001"])
        record_gate(self.project(), ["N-001"], "implement", "human", through=True)
        ready, waiting = authorized_tasks(self.project(), ["N-001", "N-002"])
        self.assertEqual([task["id"] for task in ready], ["E-001/T-001"])
        self.assertFalse(waiting)
        self.assertEqual(authorized_tasks(self.project(), ["N-002"]), ([], []))
        self.assertEqual(self.project()["needs"]["N-002"]["state"]["gates"], {})
        self.assertEqual([need["id"] for need in ready[0]["lineage"][0]["needs"]], ["N-001", "N-002"])
        self.finish_tasks()
        with self.assertRaisesRegex(WishError, "affected needs.*N-002"):
            self.review()
        record_review(self.project(), ["N-001"], "Export remains private", ["Local export passed"],
                      ["N-001", "N-002"], "pass")
        record_gate(self.project(), ["N-001"], "review", "human")
        approve_needs(self.project(), ["N-001"])
        self.assertEqual(self.project()["needs"]["N-002"]["meta"]["implementation"], "open")
        self.assertEqual(self.project()["specs"]["S-001"]["meta"]["implementation"], "open")

    def test_changing_execution_scope_invalidates_authority(self):
        self.fixture()
        self.add_second_need()
        self.edit_document("specs/S-001/design.md", needs=["N-001", "N-002"])
        self.edit_document("epics/E-001/design.md", needs=["N-001"])
        self.approve()
        self.edit_document("epics/E-001/design.md", needs=["N-001", "N-002"])
        self.assertFalse(gate_valid(self.project(), "N-001", "implement"))
        ready, waiting = authorized_tasks(self.project(), ["N-001"])
        self.assertFalse(ready)
        self.assertIn("N-002", waiting[0]["blocker"])

    def test_scoped_epic_retains_all_linked_specs_for_review_and_freshness(self):
        self.fixture()
        self.add_second_need()
        new_artifact(self.root, "spec", "S-002", "Privacy")
        self.edit_document("specs/S-002/design.md", needs=["N-002"])
        self.edit_document("epics/E-001/design.md", specs=["S-001", "S-002"], needs=["N-001"])
        record_gate(self.project(), ["N-001"], "implement", "human", through=True)
        ready, waiting = authorized_tasks(self.project(), ["N-001"])
        self.assertEqual([task["id"] for task in ready], ["E-001/T-001"])
        self.assertFalse(waiting)
        self.finish_tasks()
        with self.assertRaisesRegex(WishError, "affected needs.*N-002"):
            self.review()
        record_review(self.project(), ["N-001"], "Export remains private", ["Local export passed"],
                      ["N-001", "N-002"], "pass")
        self.edit_document("specs/S-002/spec.md", title="Revised privacy contract")
        self.assertFalse(gate_valid(self.project(), "N-001", "implement"))
        with self.assertRaisesRegex(WishError, "approved plan changed"):
            validate_review(self.project(), "N-001")
        self.assertEqual(self.project()["needs"]["N-002"]["state"]["gates"], {})

    def test_shared_spec_is_not_approved_until_both_needs_are_approved(self):
        self.fixture()
        self.add_second_need()
        self.edit_document("specs/S-001/design.md", needs=["N-001", "N-002"])
        keys = ["N-001", "N-002"]
        for stage in ("needs", "align", "implement"):
            record_gate(self.project(), keys, stage, "human")
        self.finish_tasks()
        record_review(self.project(), keys, "Reconciliation works locally", ["Local export check passed"], keys, "pass")
        record_gate(self.project(), keys, "review", "human")
        approve_needs(self.project(), ["N-001"])
        self.assertEqual(self.project()["specs"]["S-001"]["meta"]["implementation"], "review")
        approve_needs(self.project(), ["N-002"])
        self.assertEqual(self.project()["specs"]["S-001"]["meta"]["implementation"], "approved")

    def test_unapproved_independent_work_does_not_block_authorized_tasks(self):
        self.fixture()
        self.add_second_need()
        new_artifact(self.root, "spec", "S-002", "Privacy")
        self.edit_document("specs/S-002/design.md", needs=["N-002"])
        new_artifact(self.root, "epic", "E-002", "Privacy work")
        self.edit_document("epics/E-002/design.md", specs=["S-002"])
        from openwish.storage import write_json
        write_json(self.root / "openwish/epics/E-002/tasks.json", {"tasks": [self.task("E-002/T-001")]})
        self.approve()
        ready, waiting = authorized_tasks(self.project(), ["N-001", "N-002"])
        self.assertEqual([t["id"] for t in ready], ["E-001/T-001"])
        self.assertEqual([t["id"] for t in waiting], ["E-002/T-001"])

    def test_batch_gate_preflights_every_need_before_writing_receipts(self):
        self.fixture()
        self.add_second_need()
        self.approve(through="needs")
        with self.assertRaisesRegex(WishError, "missing or stale"):
            record_gate(self.project(), ["N-001", "N-002"], "align", "human")
        self.assertNotIn("align", self.project()["needs"]["N-001"]["state"]["gates"])
