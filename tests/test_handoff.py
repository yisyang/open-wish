from openwish.storage import WishError, read_json, write_json
from openwish.workflow import clean_changes, close_changes, validate_review

from tests.support import ProjectCase


class HandoffTests(ProjectCase):
    def setUp(self):
        super().setUp()
        self.fixture()
        self.finish_tasks()

    def test_passing_review_needs_resolved_material_obligations(self):
        for handoff in ([], [self.handoff(disposition="unresolved", destinations=[])],
                        [self.handoff(destinations=[])], [self.handoff(evidence="")]):
            with self.subTest(handoff=handoff), self.assertRaises(WishError):
                self.review(handoff=handoff)
        self.assertFalse((self.root / "openwish/changes/C-001/review.json").exists())

    def test_destinations_are_real_retained_files_not_self_receipts(self):
        for destination in ("missing.py", "../outside.md", str(self.root / "app.py"),
                            "openwish/needs", "openwish/changes/C-001/tasks.json", "openwish/needs/N-001.md"):
            with self.subTest(destination=destination), self.assertRaises(WishError):
                self.review(handoff=[self.handoff(destinations=[destination])])
        (self.root / "link.py").symlink_to(self.root / "app.py")
        with self.assertRaisesRegex(WishError, "symlink"):
            self.review(handoff=[self.handoff(destinations=["link.py"])])

    def test_deferred_work_survives_predecessor_disposal(self):
        self.add_change()
        handoff = [self.handoff(), self.handoff(requirement="Later exact calibration",
                   disposition="deferred", destinations=["openwish/changes/C-002/change.md"],
                   evidence="Approved values retained in the successor; implementation remains pending")]
        self.review(handoff=handoff)
        close_changes(self.project(), ["C-001"], "human")
        preview = clean_changes(self.project(), ["C-001"], dry_run=True)
        self.assertTrue((self.root / "openwish/changes/C-001/change.md").exists())
        self.assertEqual(preview["handoff"]["C-001"], handoff)
        self.assertEqual(len(preview["remove"]), 3)
        clean_changes(self.project(), ["C-001"])
        self.assertTrue((self.root / "openwish/changes/C-002/change.md").exists())

    def test_changed_handoff_and_cited_successor_invalidate_pending_review(self):
        self.add_change()
        self.review(handoff=[self.handoff(disposition="deferred", destinations=["openwish/changes/C-002/change.md"])])
        path = self.root / "openwish/changes/C-002/change.md"
        path.write_text(path.read_text() + "\nChanged future calibration.\n")
        with self.assertRaisesRegex(WishError, "stale"):
            validate_review(self.project(), "C-001")
        self.review()
        review_path = self.root / "openwish/changes/C-001/review.json"
        review = read_json(review_path)
        review["handoff"][0]["evidence"] = "Different interpretation"
        write_json(review_path, review)
        with self.assertRaisesRegex(WishError, "stale"):
            validate_review(self.project(), "C-001")

    def test_batch_cleanup_cannot_dispose_its_retained_destinations(self):
        self.add_change()
        self.review(handoff=[self.handoff(disposition="deferred", destinations=["openwish/changes/C-002/change.md"])])
        close_changes(self.project(), ["C-001"], "human")
        self.finish_tasks("C-002")
        self.review("C-002")
        close_changes(self.project(), ["C-002"], "human")
        with self.assertRaises(WishError):
            clean_changes(self.project(), ["C-001", "C-002"])
        with self.assertRaisesRegex(WishError, "Retained handoff"):
            clean_changes(self.project(), ["C-002"])
        self.assertTrue((self.root / "openwish/changes/C-001/change.md").exists())
        self.assertTrue((self.root / "openwish/changes/C-002/change.md").exists())

    def test_missing_destination_blocks_cleanup_and_prose_references_are_reported(self):
        self.review()
        close_changes(self.project(), ["C-001"], "human")
        (self.root / "app.py").unlink()
        with self.assertRaisesRegex(WishError, "does not exist"):
            clean_changes(self.project(), ["C-001"])
        (self.root / "app.py").write_text("# Retained implementation\n")
        (self.root / "README.md").write_text("See openwish/changes/C-001/change.md for the former approach.")
        report = clean_changes(self.project(), ["C-001"], dry_run=True)
        self.assertIn("README.md", report["warnings"][0])
