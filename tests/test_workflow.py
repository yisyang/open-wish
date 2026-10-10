from openwish.model import needs_context
from openwish.storage import WishError, read_json, write_json
from openwish.views import status_data, summary
from openwish.workflow import (clean_changes, close_changes, record_review, set_mode, validate_review)

from tests.support import ProjectCase


class WorkflowTests(ProjectCase):
    def reviewed(self, *, mode="default"):
        self.fixture(mode=mode)
        self.finish_tasks()
        self.review()

    def test_default_closure_retains_needs_and_provenance(self):
        self.reviewed()
        path = self.root / "openwish/needs/N-001.md"
        before = path.read_bytes()
        close_changes(self.project(), ["C-001"], "human")
        change = self.project()["changes"]["C-001"]["meta"]
        self.assertEqual((change["status"], change["closed_by"]), ("closed", "human"))
        self.assertTrue(change["closed_at"])
        self.assertEqual(path.read_bytes(), before)
        self.assertIn("N-001", needs_context(self.project()))

    def test_review_does_not_close_change_or_approve_entire_need(self):
        self.reviewed()
        self.assertEqual(self.project()["changes"]["C-001"]["meta"]["status"], "review")
        self.assertNotIn("implementation", self.project()["needs"]["N-001"]["meta"])
        self.assertEqual(self.project()["needs"]["N-001"]["meta"]["confirmed_at"], "")

    def test_fast_forward_requires_explicit_change_mode(self):
        self.reviewed()
        with self.assertRaisesRegex(WishError, "explicitly enabling"):
            close_changes(self.project(), ["C-001"], "fast-forward")
        set_mode(self.project(), "C-001", "fast-forward")
        with self.assertRaisesRegex(WishError, "stale"):
            close_changes(self.project(), ["C-001"], "fast-forward")
        self.review()
        close_changes(self.project(), ["C-001"], "fast-forward")
        self.assertEqual(self.project()["changes"]["C-001"]["meta"]["closed_by"], "fast-forward")
        self.assertEqual(self.project()["needs"]["N-001"]["meta"]["confirmed_at"], "")
        self.add_change()
        self.assertEqual(self.project()["changes"]["C-002"]["meta"]["mode"], "default")

    def test_fast_forward_cannot_skip_manual_work(self):
        self.fixture(mode="fast-forward")
        self.write_tasks([self.task(kind="manual")])
        with self.assertRaisesRegex(WishError, "Unfinished work"):
            self.review()

    def test_review_requires_direct_results_and_all_current_intent(self):
        self.fixture()
        self.add_need()
        self.finish_tasks()
        with self.assertRaisesRegex(WishError, "N-002"):
            self.review()
        with self.assertRaisesRegex(WishError, "direct verification"):
            record_review(self.project(), "C-001", "Fine", [], ["N-001", "N-002"])
        self.review(needs=["N-001", "N-002"])
        self.assertEqual(validate_review(self.project(), "C-001")["verdict"], "pass")

    def test_repository_add_edit_and_delete_each_invalidate_review(self):
        self.reviewed()
        path = self.root / "new.py"
        path.write_text("pass\n", encoding="utf-8")
        with self.assertRaisesRegex(WishError, "stale"):
            close_changes(self.project(), ["C-001"], "human")
        self.review()
        path.write_text("raise RuntimeError()\n", encoding="utf-8")
        with self.assertRaisesRegex(WishError, "stale"):
            validate_review(self.project(), "C-001")
        self.review()
        path.unlink()
        with self.assertRaisesRegex(WishError, "stale"):
            validate_review(self.project(), "C-001")

    def test_need_approach_evidence_and_policy_edits_each_invalidate_review(self):
        self.reviewed()
        for relative in ("needs/N-001.md", "changes/C-001/change.md", "policy.md"):
            with self.subTest(path=relative):
                path = self.root / "openwish" / relative
                path.write_text(path.read_text() + "\nA consequential clarification.\n", encoding="utf-8")
                with self.assertRaisesRegex(WishError, "stale"):
                    validate_review(self.project(), "C-001")
                self.review()
        self.write_tasks([self.task(status="done", evidence="Different checks were performed")])
        with self.assertRaisesRegex(WishError, "stale"):
            validate_review(self.project(), "C-001")

    def test_new_current_need_requires_review_but_unrelated_plan_edits_do_not(self):
        self.reviewed()
        self.add_change()
        self.assertEqual(validate_review(self.project(), "C-001")["verdict"], "pass")
        self.add_need()
        with self.assertRaisesRegex(WishError, "missing current"):
            validate_review(self.project(), "C-001")

    def test_blocked_review_cannot_close_and_latest_review_replaces_it(self):
        self.fixture()
        record_review(self.project(), "C-001", "Waiting for observation", ["Import check unavailable"],
                      ["N-001"], "blocked")
        with self.assertRaisesRegex(WishError, "not passing"):
            close_changes(self.project(), ["C-001"], "human")
        self.finish_tasks()
        self.review()
        self.assertEqual(read_json(self.root / "openwish/changes/C-001/review.json")["verdict"], "pass")
        self.assertEqual(len(list((self.root / "openwish/changes/C-001").glob("*review*"))), 1)

    def test_zero_task_verification_change_needs_no_invented_work(self):
        self.fixture()
        self.write_tasks([])
        self.review()
        close_changes(self.project(), ["C-001"], "human")

    def test_batch_closure_preflights_all_changes_before_writing(self):
        self.reviewed()
        self.add_change()
        with self.assertRaises(WishError):
            close_changes(self.project(), ["C-001", "C-002"], "human")
        self.assertEqual(self.project()["changes"]["C-001"]["meta"]["status"], "review")

    def test_batch_closure_preflights_rendered_artifact_budget(self):
        self.reviewed()
        self.add_change()
        path = self.root / "openwish/changes/C-002/change.md"
        text = path.read_text()
        path.write_text(text + "Working detail.\n" * (498 - len(text.splitlines())), encoding="utf-8")
        self.review("C-002")
        self.assertEqual(len(path.read_text().splitlines()), 498)
        with self.assertRaisesRegex(WishError, "under 500"):
            close_changes(self.project(), ["C-001", "C-002"], "human")
        for change in self.project()["changes"].values():
            self.assertEqual(change["meta"]["status"], "review")

    def test_cleanup_disposes_work_and_leaves_intent_and_product_byte_identical(self):
        self.reviewed()
        close_changes(self.project(), ["C-001"], "human")
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*")
                  if p.is_file() and "changes" not in p.parts}
        clean_changes(self.project(), ["C-001"])
        self.assertFalse((self.root / "openwish/changes/C-001").exists())
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*")
                 if p.is_file() and "changes" not in p.parts}
        self.assertEqual(before, after)
        self.assertEqual(self.project()["tasks"], [])
        self.assertEqual(status_data(self.project())["needs"][0]["changes"], [])
        self.assertIn("N-001", needs_context(self.project()))

    def test_cleanup_rejects_unclosed_changes_and_unknown_files_without_partial_deletion(self):
        self.reviewed()
        with self.assertRaisesRegex(WishError, "only closed"):
            clean_changes(self.project(), ["C-001"])
        close_changes(self.project(), ["C-001"], "human")
        self.add_change()
        self.review("C-002")
        close_changes(self.project(), ["C-002"], "human")
        path = self.root / "openwish/changes/C-002/important.md"
        path.write_text("Irreplaceable knowledge\n", encoding="utf-8")
        with self.assertRaisesRegex(WishError, "Unknown file preserved"):
            clean_changes(self.project(), ["C-001", "C-002"])
        self.assertTrue((self.root / "openwish/changes/C-001/change.md").exists())
        self.assertEqual(path.read_text(), "Irreplaceable knowledge\n")

    def test_cleanup_rejects_symlinks_without_touching_their_targets(self):
        self.reviewed()
        close_changes(self.project(), ["C-001"], "human")
        path = self.root / "openwish/changes/C-001/notes.md"
        path.symlink_to(self.root / "app.py")
        with self.assertRaisesRegex(WishError, "symlink"):
            clean_changes(self.project(), ["C-001"])
        self.assertTrue((self.root / "app.py").exists())
        self.assertTrue((path.parent / "change.md").exists())

    def test_closed_results_are_historical_and_can_be_cleaned_after_later_code_changes(self):
        self.reviewed()
        close_changes(self.project(), ["C-001"], "human")
        (self.root / "app.py").write_text("# later implementation\n", encoding="utf-8")
        self.assertEqual(status_data(self.project())["changes"][0]["review"], "historical")
        self.assertIn("Historical check", summary(self.project(), ["C-001"]))
        with self.assertRaisesRegex(WishError, "closed"):
            self.review()
        clean_changes(self.project(), ["C-001"])

    def test_malformed_review_is_actionable_and_prevents_closure(self):
        self.reviewed()
        path = self.root / "openwish/changes/C-001/review.json"
        review = read_json(path)
        for field, value in (("checks", []), ("needs", None), ("at", "not-a-date")):
            with self.subTest(field=field):
                write_json(path, {**review, field: value})
                with self.assertRaises(WishError):
                    close_changes(self.project(), ["C-001"], "human")
