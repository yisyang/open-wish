import subprocess
import shutil

from openwish.repository import project_files, repository_snapshot
from openwish.validation import validate
from openwish.storage import WishError
from openwish.workflow import clean_changes, close_changes, record_review, source_inputs, validate_review

from tests.support import ProjectCase


class RepositoryTests(ProjectCase):
    def git(self, root, *args):
        return subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                               "-c", "protocol.file.allow=always", *args], cwd=root,
                              check=True, capture_output=True, text=True).stdout.strip()

    def setUp(self):
        super().setUp()
        self.fixture()
        self.git(self.root, "init")
        origin = self.root.parent / (self.root.name + "-component")
        origin.mkdir()
        self.addCleanup(shutil.rmtree, origin)
        self.git(origin, "init")
        (origin / "code.py").write_text("value = 1\n")
        (origin / ".gitignore").write_text("cache/\n")
        self.git(origin, "add", ".")
        self.git(origin, "commit", "-m", "Initial component")
        self.git(self.root, "submodule", "add", str(origin), "component")
        self.component = self.root / "component"
        self.finish_tasks()

    def test_nested_product_changes_invalidate_acceptance(self):
        self.review()
        (self.component / "code.py").write_text("value = 2\n")
        self.assertIn(self.component / "code.py", project_files(self.root))
        with self.assertRaisesRegex(WishError, "stale"):
            close_changes(self.project(), ["C-001"], "human")
        self.review()
        (self.component / "new.py").write_text("value = 3\n")
        with self.assertRaisesRegex(WishError, "stale"):
            validate_review(self.project(), "C-001")
        self.review()
        (self.component / "new.py").unlink()
        with self.assertRaisesRegex(WishError, "stale"):
            validate_review(self.project(), "C-001")

    def test_checkout_and_gitlink_revisions_are_both_fingerprinted(self):
        original = source_inputs(self.project())
        self.git(self.component, "commit", "--allow-empty", "-m", "New revision, same files")
        checkout = source_inputs(self.project())
        self.assertNotEqual(original, checkout)
        self.git(self.root, "add", "component")
        self.assertNotEqual(checkout, source_inputs(self.project()))

    def test_missing_submodule_is_visible_and_blocks_review(self):
        self.git(self.root, "submodule", "deinit", "-f", "component")
        self.assertIn("initialize", " ".join(repository_snapshot(self.root)["warnings"]))
        with self.assertRaisesRegex(WishError, "inspection incomplete"):
            self.review()
        record_review(self.project(), "C-001", "Component unavailable",
                      ["Observed uninitialized component; review cannot pass"], verdict="blocked")
        self.assertEqual(self.project()["changes"]["C-001"]["meta"]["status"], "in-progress")

    def test_ignored_files_do_not_stale_review_or_qualify_as_handoff(self):
        self.review()
        (self.component / "cache").mkdir()
        (self.component / "cache/data.py").write_text("temporary = True\n")
        validate_review(self.project(), "C-001")
        with self.assertRaisesRegex(WishError, "ignored or excluded"):
            self.review(handoff=[self.handoff(destinations=["component/cache/data.py"])])
        self.edit_document("needs/N-001.md", references=["component/cache/data.py"])
        self.assertIn("ignored or excluded", "\n".join(validate(self.project())))

    def test_nested_submodules_are_inspected_recursively(self):
        source = self.git(self.root, "config", "--file", ".gitmodules", "submodule.component.url")
        self.git(self.component, "submodule", "add", source, "nested")
        self.review()
        (self.component / "nested/code.py").write_text("value = 9\n")
        with self.assertRaisesRegex(WishError, "stale"):
            validate_review(self.project(), "C-001")

    def test_ignored_managed_reviews_still_protect_incoming_handoff(self):
        self.add_change()
        (self.root / ".gitignore").write_text("openwish/changes/C-001/\n")
        self.review(handoff=[self.handoff(disposition="deferred",
                                         destinations=["openwish/changes/C-002/change.md"])])
        close_changes(self.project(), ["C-001"], "human")
        self.finish_tasks("C-002")
        self.review("C-002")
        close_changes(self.project(), ["C-002"], "human")
        with self.assertRaisesRegex(WishError, "Retained handoff"):
            clean_changes(self.project(), ["C-002"])
        self.assertTrue((self.root / "openwish/changes/C-002/change.md").exists())
