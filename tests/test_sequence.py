import json
import subprocess

from openwish.model import ready_tasks, unplanned_changes
from openwish.storage import WishError, read_json, write_json
from openwish.validation import validate
from openwish.workflow import clean_changes, close_changes, validate_review

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
        self.assertEqual(work["ready"], [{"id": "C-001/T-001", "title": "Export records"}])
        self.assertEqual(work["unplanned"][0]["waiting_on"], ["C-001 (open)"])
        self.assertTrue(any("tmp/rates.json" in warning for warning in work["warnings"]))
        text = self.cli("context", "C-001").stdout
        self.assertIn("READY C-001/T-001", text)
        self.assertNotIn("C-002", text.split("# Work")[1].split("# Retrieval")[0])
