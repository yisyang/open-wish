import subprocess
import shutil

from openwish.repository import pin_mismatches, project_files, repository_snapshot
from openwish.validation import validate
from openwish.storage import WishError, read_json, write_json
from openwish.workflow import (clean_changes, close_changes, digest, record_review, source_inputs,
                               validate_review)

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

    def test_checkout_revisions_are_fingerprinted_but_a_matching_pin_is_not(self):
        original = source_inputs(self.project())
        self.git(self.component, "commit", "--allow-empty", "-m", "New revision, same files")
        checkout = source_inputs(self.project())
        self.assertNotEqual(original, checkout)
        self.git(self.root, "add", "component")
        self.assertEqual(checkout, source_inputs(self.project()))

    def test_pinning_the_reviewed_checkout_after_review_keeps_it_fresh(self):
        self.git(self.component, "commit", "--allow-empty", "-m", "Reviewed revision")
        self.review()
        self.assertIn("stage or commit the reviewed pin", " ".join(pin_mismatches(repository_snapshot(self.root))))
        self.git(self.root, "add", "component")
        self.git(self.root, "commit", "-m", "Pin the reviewed component")
        validate_review(self.project(), "C-001")
        self.assertEqual(close_changes(self.project(), ["C-001"], "human"), [])

    def test_unpinned_checkout_closes_with_a_warning(self):
        self.git(self.component, "commit", "--allow-empty", "-m", "Reviewed revision")
        self.review()
        warnings = close_changes(self.project(), ["C-001"], "human")
        self.assertEqual(len(warnings), 1)
        self.assertIn("component", warnings[0])

    def test_reviews_from_earlier_versions_stay_fresh_until_components_change(self):
        self.review()
        path = self.root / "openwish/changes/C-001/review.json"
        record = read_json(path)
        # Before 1.0.0-rc.3 the digest covered staged gitlinks as well as checkouts.
        record["inputs"]["source"]["components"] = digest(repository_snapshot(self.root)["components"])
        write_json(path, record)
        validate_review(self.project(), "C-001")
        self.git(self.component, "commit", "--allow-empty", "-m", "Unreviewed revision")
        with self.assertRaisesRegex(WishError, "submodule revisions"):
            validate_review(self.project(), "C-001")

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


class SandboxPlaceholderTests(ProjectCase):
    def test_an_empty_git_placeholder_is_not_a_repository(self):
        # Codex's sandbox mounts an empty read-only `.git` into plain directories.
        self.fixture()
        (self.root / ".git").mkdir()
        snapshot = repository_snapshot(self.root)
        self.assertEqual(snapshot["warnings"], [])
        self.assertIn(self.root / "app.py", snapshot["files"])
        self.assertIn("PASS", self.cli("check").stdout)
