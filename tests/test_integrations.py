from unittest.mock import Mock, patch

from openwish import __version__
from openwish.integrations import (HARNESSES, installed_harnesses, install_skills,
                                   integration_files, load_manifest)
from openwish.scaffold import initialize
from openwish.storage import WishError
from openwish.versions import declared_version, version_key

from tests.support import ProjectCase


class IntegrationTests(ProjectCase):
    def seed_version(self, harnesses, version):
        with patch("openwish.integrations.__version__", version):
            return install_skills(self.root, harnesses)

    def snapshot(self):
        return {str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.root.rglob("*") if path.is_file()}

    def test_multiple_harnesses_deduplicate_shared_skills(self):
        report = install_skills(self.root, HARNESSES)
        self.assertEqual(report["installed"], 28)
        self.assertEqual(report["unchanged"], 9)  # generic from setUp, shared with Codex
        self.assertEqual(installed_harnesses(self.root), list(HARNESSES))
        for relative in integration_files(HARNESSES, __version__):
            self.assertEqual(declared_version((self.root / relative).read_text()), __version__)

    def test_same_version_preserves_customized_files_and_all_mtimes(self):
        install_skills(self.root, HARNESSES)
        path = self.root / ".opencode/skills/ow-propose/SKILL.md"
        path.write_text(path.read_text() + "\nA local customization.\n", encoding="utf-8")
        before = self.snapshot()
        with patch("openwish.integrations.write_text") as write, patch("openwish.integrations.write_json") as manifest:
            report = install_skills(self.root, HARNESSES)
            write.assert_not_called()
            manifest.assert_not_called()
        self.assertEqual(report["unchanged"], 37)
        self.assertEqual(self.snapshot(), before)

    def test_upgrade_overwrites_older_skills_and_adapters_even_with_local_edits(self):
        self.seed_version(["opencode", "claude"], "0.2.9")
        path = self.root / ".opencode/skills/ow-propose/SKILL.md"
        path.write_text(path.read_text() + "\nOld customized content\n", encoding="utf-8")
        callback = Mock(side_effect=AssertionError("Upgrades must not prompt"))
        report = install_skills(self.root, ["opencode", "claude"], confirm_downgrade=callback)
        self.assertEqual(report["upgraded"], 28)
        for relative, text in integration_files(["opencode", "claude"], __version__).items():
            self.assertEqual((self.root / relative).read_text(), text)

    def test_downgrade_requires_explicit_confirmation_before_any_writes(self):
        self.seed_version("opencode", "1.0.0")
        before = self.snapshot()
        with self.assertRaisesRegex(WishError, "requires confirmation"):
            install_skills(self.root, ["opencode", "claude"])
        self.assertEqual(self.snapshot(), before)

    def test_downgrade_decline_keeps_newer_files_and_installs_other_selection(self):
        self.seed_version("opencode", "1.0.0")
        before = {key: value for key, value in self.snapshot().items() if key.startswith(".opencode/")}
        callback = Mock(return_value=False)
        report = install_skills(self.root, ["opencode", "claude"], confirm_downgrade=callback)
        callback.assert_called_once()
        self.assertEqual(len(callback.call_args.args[0]), 18)
        self.assertEqual(report["kept_newer"], 18)
        self.assertEqual(report["installed"], 10)
        after = {key: value for key, value in self.snapshot().items() if key.startswith(".opencode/")}
        self.assertEqual(after, before)
        self.assertEqual(load_manifest(self.root)["files"][".opencode/commands/onboard.md"], "1.0.0")

    def test_downgrade_acceptance_replaces_files_and_updates_versions(self):
        self.seed_version("opencode", "1.0.0")
        callback = Mock(return_value=True)
        report = install_skills(self.root, "opencode", confirm_downgrade=callback)
        self.assertEqual(report["downgraded"], 18)
        for relative, text in integration_files(["opencode"], __version__).items():
            self.assertEqual((self.root / relative).read_text(), text)
            self.assertEqual(load_manifest(self.root)["files"][relative], __version__)

    def test_mixed_versions_are_handled_per_file(self):
        install_skills(self.root, "opencode")
        old = self.root / ".opencode/skills/ow-propose/SKILL.md"
        old.write_text(old.read_text().replace(__version__, "0.2.10"), encoding="utf-8")
        new = self.root / ".opencode/skills/ow-review/SKILL.md"
        new.write_text(new.read_text().replace(__version__, "1.0.0"), encoding="utf-8")
        retained = {key: value for key, value in self.snapshot().items()
                    if key.startswith(".opencode/") and key != str(old.relative_to(self.root))}
        callback = Mock(return_value=False)
        report = install_skills(self.root, "opencode", confirm_downgrade=callback)
        self.assertEqual((report["upgraded"], report["unchanged"], report["kept_newer"]), (1, 16, 1))
        self.assertEqual(callback.call_args.args[0], [{"path": str(new.relative_to(self.root)),
                                                      "installed": "1.0.0", "available": __version__}])
        self.assertEqual({key: value for key, value in self.snapshot().items() if key in retained}, retained)
        self.assertEqual(declared_version(old.read_text()), __version__)

    def test_declared_newer_version_takes_precedence_over_manifest(self):
        install_skills(self.root, "opencode")
        path = self.root / ".opencode/skills/ow-propose/SKILL.md"
        path.write_text(path.read_text().replace(__version__, "2.0.0"), encoding="utf-8")
        with self.assertRaisesRegex(WishError, "requires confirmation"):
            install_skills(self.root, "opencode")

    def test_all_harnesses_are_preflighted_before_initializing_project(self):
        root = self.root / "new-project"
        path = root / ".claude/skills/ow-review/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("Unrelated user skill", encoding="utf-8")
        with self.assertRaisesRegex(WishError, "preserved"):
            initialize(root, ["opencode", "claude"])
        self.assertFalse((root / "openwish").exists())
        self.assertFalse((root / ".opencode").exists())
        self.assertEqual(path.read_text(), "Unrelated user skill")

    def test_reinitializing_preserves_all_knowledge_and_custom_config(self):
        self.fixture()
        path = self.root / "openwish/policy.md"
        path.write_text("# Custom environment\n", encoding="utf-8")
        before = {key: value for key, value in self.snapshot().items()
                  if key.startswith("openwish/") and key != "openwish/installation.json"}
        result = initialize(self.root, ["opencode", "claude"])
        self.assertFalse(result["initialized"])
        after = {key: value for key, value in self.snapshot().items()
                 if key.startswith("openwish/") and key != "openwish/installation.json"}
        self.assertEqual(after, before)

    def test_version_precedence_is_numeric_and_understands_prereleases(self):
        ordered = ["0.2.9", "0.2.10", "0.3.0-alpha", "0.3.0-alpha.2", "0.3.0-alpha.10",
                   "0.3.0-beta", "0.3.0-rc.1", "0.3.0", "1.0.0"]
        self.assertEqual(sorted(reversed(ordered), key=version_key), ordered)
        self.assertEqual(version_key("1.0.0+build.1"), version_key("1.0.0+build.2"))
        for invalid in ("old", "01.0.0", "1.0.0-alpha.01", "1.0.0-a..b"):
            with self.subTest(version=invalid), self.assertRaises(WishError):
                version_key(invalid)

    def test_invalid_version_preserves_all_files(self):
        install_skills(self.root, "opencode")
        path = self.root / ".opencode/skills/ow-review/SKILL.md"
        path.write_text(path.read_text().replace(__version__, "invalid"), encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(WishError, "Invalid OW version"):
            install_skills(self.root, ["opencode", "claude"])
        self.assertEqual(before, self.snapshot())
