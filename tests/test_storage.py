from pathlib import Path

from openwish.scaffold import initialize, install_skills, new_artifact
from openwish.storage import WishError, contained, project_root, read_document

from tests.support import ProjectCase


class StorageTests(ProjectCase):
    def test_initialization_preserves_existing_project_and_local_edits(self):
        marker = self.root / "README.md"
        marker.write_text("my project\n", encoding="utf-8")
        result = initialize(self.root)
        self.assertFalse(result["initialized"])
        self.assertEqual(marker.read_text(), "my project\n")
        path = self.root / ".agents/skills/ow-propose/SKILL.md"
        path.write_text("custom workflow\n", encoding="utf-8")
        result = install_skills(self.root, "generic")
        self.assertEqual(result["unchanged"], 9)
        self.assertEqual(path.read_text(), "custom workflow\n")

    def test_integration_preflight_avoids_partial_overwrite(self):
        conflict = self.root / ".opencode/commands/onboard.md"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("my onboarding\n", encoding="utf-8")
        with self.assertRaisesRegex(WishError, "preserved"):
            install_skills(self.root, "opencode")
        self.assertFalse((self.root / ".opencode/skills").exists())
        self.assertEqual(conflict.read_text(), "my onboarding\n")

    def test_each_integration_installs_idempotently_with_required_shortcuts(self):
        for harness in ("opencode", "claude", "codex", "generic"):
            install_skills(self.root, harness)
            install_skills(self.root, harness)
        self.assertTrue((self.root / ".opencode/commands/fast-forward.md").is_file())
        self.assertTrue((self.root / ".opencode/commands/onboard.md").is_file())
        self.assertTrue((self.root / ".claude/skills/fast-forward/SKILL.md").is_file())
        self.assertTrue((self.root / ".agents/skills/ow-fast-forward/agents/openai.yaml").is_file())

    def test_discovery_from_nested_monorepo_directory(self):
        nested = self.root / "packages/api/src"
        nested.mkdir(parents=True)
        self.assertEqual(project_root(nested), self.root)

    def test_ids_cannot_escape_artifact_directories(self):
        with self.assertRaisesRegex(WishError, "Invalid identifier"):
            new_artifact(self.root, "need", "../../elsewhere", "Bad")
        with self.assertRaisesRegex(WishError, "escapes"):
            contained(self.root, "../outside.md")

    def test_symlinked_knowledge_cannot_redirect_reads_or_writes(self):
        outside = self.root / "elsewhere"
        outside.mkdir()
        target = self.root / "openwish/needs"
        try:
            target.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(WishError, "symlink"):
            new_artifact(self.root, "need", "N-001", "Test")
        self.assertFalse((outside / "N-001.md").exists())

    def test_malformed_frontmatter_has_an_actionable_error(self):
        path = self.root / "broken.md"
        path.write_text("+++\nid = [\n+++\n", encoding="utf-8")
        with self.assertRaisesRegex(WishError, "Cannot read"):
            read_document(path)

    def test_existing_artifact_is_never_overwritten(self):
        new_artifact(self.root, "need", "N-001", "Original")
        with self.assertRaisesRegex(WishError, "preserved"):
            new_artifact(self.root, "need", "N-001", "Replacement")
        meta, _ = read_document(self.root / "openwish/needs/N-001.md")
        self.assertEqual(meta["title"], "Original")

    def test_needs_have_no_execution_sidecars_and_changes_require_known_needs(self):
        new_artifact(self.root, "need", "N-001", "An outcome")
        meta, _ = read_document(self.root / "openwish/needs/N-001.md")
        self.assertNotIn("ask", meta)
        self.assertFalse((self.root / "openwish/needs/N-001.state.json").exists())
        self.assertFalse((self.root / "openwish/changes").exists())
        with self.assertRaisesRegex(WishError, "nonempty"):
            new_artifact(self.root, "change", "C-001", "An improvement")
        with self.assertRaisesRegex(WishError, "Unknown need"):
            new_artifact(self.root, "change", "C-001", "An improvement", needs=["N-999"])
        self.assertFalse((self.root / "openwish/changes").exists())
        new_artifact(self.root, "change", "C-001", "An improvement", needs=["N-001"])
        self.assertTrue((self.root / "openwish/changes/C-001/tasks.json").is_file())

    def test_change_scaffolding_preserves_preexisting_unknown_files(self):
        self.fixture()
        directory = self.root / "openwish/changes/C-002"
        directory.mkdir()
        (directory / "notes.md").write_text("Keep me", encoding="utf-8")
        with self.assertRaisesRegex(WishError, "preserved"):
            self.add_change()
        self.assertFalse((directory / "change.md").exists())

    def test_missing_config_does_not_reinitialize_existing_knowledge(self):
        self.fixture()
        (self.root / "openwish/config.json").unlink()
        with self.assertRaisesRegex(WishError, "preserved"):
            initialize(self.root)
        self.assertFalse((self.root / "openwish/config.json").exists())
