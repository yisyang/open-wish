import json
import subprocess

from openwish.model import ready_tasks, unplanned_changes
from openwish.storage import WishError, read_json, write_json
from openwish.validation import validate
from openwish.workflow import clean_changes, close_changes, set_task, validate_review

from tests.support import ProjectCase


class SequenceTests(ProjectCase):
    def setUp(self):
        super().setUp()
        self.fixture()
        self.add_change("C-002", after=["C-001"])
        self.add_change("C-003", after=["C-002"])

    def waiting(self):
        return {change["id"]: change["waiting_on"] for change in unplanned_changes(self.project())}

    def gate(self, value):
        path = self.root / "openwish/config.json"
        write_json(path, {**read_json(path), "successors_wait_for": value})

    def test_successors_become_plannable_on_a_passing_review_by_default(self):
        self.assertEqual(self.waiting(), {"C-002": ["C-001 (open)"], "C-003": ["C-002 (open)"]})
        self.finish_tasks()
        self.review()
        self.assertEqual(self.waiting(), {"C-002": [], "C-003": ["C-002 (open)"]})

    def test_acceptance_gate_waits_for_closure(self):
        self.gate("acceptance")
        self.finish_tasks()
        self.review()
        self.assertEqual(self.waiting()["C-002"], ["C-001 (review)"])
        close_changes(self.project(), ["C-001"], "human")
        self.assertEqual(self.waiting()["C-002"], [])

    def test_tasks_of_a_waiting_change_are_not_ready(self):
        self.write_tasks([self.task("C-002/T-001")], "C-002")
        ready, waiting = ready_tasks(self.project())
        self.assertEqual([task["id"] for task in ready], ["C-001/T-001"])
        self.assertEqual(waiting[0]["blocker"], "Change waits for C-001 (open)")

    def test_investigations_run_ahead_of_predecessors_without_planning_the_change(self):
        decide = self.task("C-002/T-001", kind="investigate", title="Decide storage billing timing")
        build = self.task("C-002/T-002", depends_on=["C-002/T-001"])
        self.write_tasks([decide, build], "C-002")
        self.write_tasks([self.task("C-003/T-001", kind="investigate")], "C-003")
        ready, waiting = ready_tasks(self.project())
        self.assertEqual([task["id"] for task in ready], ["C-001/T-001", "C-002/T-001", "C-003/T-001"])
        self.assertEqual([(task["id"], task["blocker"]) for task in waiting],
                         [("C-002/T-002", "Change waits for C-001 (open)")])
        # A change holding only investigations still needs delivery planning once its turn comes.
        self.assertEqual(self.waiting(), {"C-003": ["C-002 (open)"]})
        self.assertIn("READY C-002/T-001 [investigate] Decide storage billing timing", self.cli("ready").stdout)
        # Investigating does not start delivery; the change stays open.
        set_task(self.project(), "C-002/T-001", "done", "Billing starts at the first full day; see docs/billing.md")
        self.assertEqual(self.project()["changes"]["C-002"]["meta"]["status"], "open")
        ready, waiting = ready_tasks(self.project())
        self.assertEqual(waiting[0]["blocker"], "Change waits for C-001 (open)")
        self.finish_tasks()
        self.review()
        self.assertIn("C-002/T-002", [task["id"] for task in ready_tasks(self.project())[0]])
        set_task(self.project(), "C-002/T-002", "in-progress")
        self.assertEqual(self.project()["changes"]["C-002"]["meta"]["status"], "in-progress")

    def test_questions_awaiting_a_human_are_listed_for_one_batch(self):
        question = self.task("C-002/T-001", kind="investigate", status="blocked",
                             evidence="Awaiting decision: charge on move-in day (Recommended) or the next day?")
        probing = self.task("C-003/T-001", kind="investigate", status="in-progress")
        stuck = self.task("C-001/T-002", status="blocked", evidence="Vendor sandbox is down")
        self.write_tasks([self.task(), stuck])
        self.write_tasks([question], "C-002")
        self.write_tasks([probing], "C-003")
        ready, waiting = ready_tasks(self.project())
        self.assertEqual([task["id"] for task in waiting if task.get("ask")], ["C-002/T-001"])
        output = self.cli("ready").stdout
        self.assertIn("ASK C-002/T-001 [investigate]", output)
        self.assertIn("WAIT C-001/T-002", output)
        self.assertIn("Investigations in flight: 2, 1 awaiting a human.", output)
        work = json.loads(self.cli("context", "--json").stdout)["work"]
        self.assertEqual([task["id"] for task in work["waiting"] if task.get("ask")], ["C-002/T-001"])
        self.assertIn("ASK C-002/T-001", self.cli("context").stdout)

    def test_investigations_still_hold_a_review(self):
        self.finish_tasks()
        self.review()
        self.assertEqual(self.project()["changes"]["C-001"]["meta"]["status"], "review")
        self.write_tasks([self.task(status="done", evidence="Representative export check passed"),
                          self.task("C-001/T-002", kind="investigate")])
        set_task(self.project(), "C-001/T-002", "in-progress")
        self.assertEqual(self.project()["changes"]["C-001"]["meta"]["status"], "in-progress")

    def test_unknown_task_kinds_are_rejected(self):
        self.write_tasks([self.task(kind="decide")])
        self.assertIn("C-001/T-001: kind must be agent, manual or investigate", validate(self.project()))

    def test_successors_close_after_or_with_their_predecessors(self):
        self.finish_tasks()
        self.review()
        self.finish_tasks("C-002")
        self.review("C-002")
        with self.assertRaisesRegex(WishError, "close its predecessors first"):
            close_changes(self.project(), ["C-002"], "human")
        close_changes(self.project(), ["C-002", "C-001"], "human")

    def test_cleanup_releases_successors_without_staling_their_reviews(self):
        self.finish_tasks()
        self.review()
        self.finish_tasks("C-002")
        self.review("C-002")
        close_changes(self.project(), ["C-001"], "human")
        report = clean_changes(self.project(), ["C-001"])
        self.assertEqual(report["successors"], {"C-002": ["C-001"]})
        self.assertFalse(report["warnings"])
        project = self.project()
        self.assertNotIn("after", project["changes"]["C-002"]["meta"])
        self.assertEqual(project["changes"]["C-003"]["meta"]["after"], ["C-002"])
        validate_review(project, "C-002")
        self.assertEqual(validate(project), [])

    def test_malformed_sequences_are_reported_not_crashed_on(self):
        self.edit_document("changes/C-001/change.md", after=5)
        self.assertIn("C-001: after must be an array of non-empty IDs", self.cli("check", success=False).stdout)
        self.edit_document("changes/C-001/change.md", after="C-001")
        errors = validate(self.project())
        self.assertIn("C-001: after must be an array of non-empty IDs", errors)
        self.assertNotIn("C-001: a change cannot come after itself", errors)

    def test_sequence_must_name_known_changes_without_cycles(self):
        self.edit_document("changes/C-001/change.md", after=["C-003"])
        self.assertTrue(any("Change sequence" in error for error in validate(self.project())))
        self.edit_document("changes/C-001/change.md", after=["C-009"])
        self.assertIn("C-001: unknown after reference C-009", validate(self.project()))
        self.edit_document("changes/C-001/change.md", after=["C-001"])
        self.assertIn("C-001: a change cannot come after itself", validate(self.project()))

    def test_cli_creates_sequences_and_shows_only_unblocked_candidates(self):
        self.cli("new", "change", "C-004", "--title", "Later", "--need", "N-001", "--after", "C-003")
        self.cli("new", "change", "C-005", "--title", "Bad", "--need", "N-001", "--after", "C-404", success=False)
        output = self.cli("ready").stdout
        self.assertNotIn("PLAN", output)
        self.assertIn("LATER 3 unplanned changes wait for predecessors: C-002, C-003, C-004", output)
        self.assertIn("after C-003", self.cli("status").stdout)
        data = json.loads(self.cli("ready", "--json").stdout)
        self.assertEqual([change["id"] for change in data["unplanned"]], ["C-002", "C-003", "C-004"])


class OpenItemTests(ProjectCase):
    def test_recording_an_open_item_keeps_pending_reviews_fresh(self):
        self.fixture()
        self.finish_tasks()
        self.review()
        self.edit_document("needs/N-001.md", open=["Should voided rows be exported?"])
        validate_review(self.project(), "C-001")
        self.edit_document("needs/N-001.md", acceptance=["No manual row copying", "Voided rows are excluded"])
        with self.assertRaisesRegex(WishError, "N-001 modified"):
            validate_review(self.project(), "C-001")

    def test_open_items_are_validated_and_shown(self):
        self.fixture()
        self.edit_document("needs/N-001.md", open=["Should exports include voided rows?"])
        self.assertEqual(validate(self.project()), [])
        self.assertIn("1 open", self.cli("status").stdout)
        self.edit_document("needs/N-001.md", open="voided rows?")
        self.assertIn("N-001: open must be an array of undecided questions or proposed criteria",
                      validate(self.project()))


class ReadinessTests(ProjectCase):
    def test_unconfirmed_intent_and_open_items_never_gate_ready_work(self):
        self.fixture()
        self.edit_document("needs/N-001.md", confirmed_at="", open=["Should voided rows be exported?"])
        ready, waiting = ready_tasks(self.project())
        self.assertEqual([task["id"] for task in ready], ["C-001/T-001"])
        self.assertEqual(waiting, [])

    def test_context_returns_intent_and_work_state_in_one_call(self):
        self.fixture()
        self.add_change("C-002", after=["C-001"])
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / ".gitignore").write_text("tmp/\n", encoding="utf-8")
        (self.root / "tmp").mkdir()
        (self.root / "tmp/rates.json").write_text("{}", encoding="utf-8")
        need = self.root / "openwish/needs/N-001.md"
        need.write_text(need.read_text() + "Rates come from tmp/rates.json.\n")
        data = json.loads(self.cli("context", "--json").stdout)
        self.assertIn("Reconcile without retyping", data["needs"])
        work = data["work"]
        self.assertEqual([change["id"] for change in work["changes"]], ["C-001", "C-002"])
        self.assertEqual(work["ready"], [{"id": "C-001/T-001", "title": "Export records", "kind": "agent",
                                          "status": "open"}])
        self.assertEqual(work["unplanned"][0]["waiting_on"], ["C-001 (open)"])
        self.assertTrue(any("tmp/rates.json" in warning for warning in work["warnings"]))
        text = self.cli("context", "C-001").stdout
        self.assertIn("READY C-001/T-001", text)
        self.assertNotIn("C-002", text.split("# Work")[1].split("# Retrieval")[0])
