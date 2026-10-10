from pathlib import Path
import tempfile
import unittest

from scripts.check_release import check_version


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "src/openwish").mkdir(parents=True)
        self.metadata = self.root / "pyproject.toml"
        self.metadata.write_text('[project]\nname = "openwish"\nversion = "0.3.1"\n', encoding="utf-8")
        self.module = self.root / "src/openwish/__init__.py"
        self.module.write_text('__version__ = "0.3.1"\n', encoding="utf-8")

    def test_matching_package_cli_and_tag_pass(self):
        self.assertEqual(check_version(self.root, "v0.3.1"), "0.3.1")
        self.assertEqual(check_version(self.root), "0.3.1")

    def test_wrong_or_unprefixed_release_tag_is_rejected(self):
        for tag in ("v0.3.0", "0.3.1", "v0.3.1-extra"):
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, "must be v0.3.1"):
                check_version(self.root, tag)

    def test_mismatched_cli_version_is_rejected(self):
        self.module.write_text('__version__ = "0.3.0"\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "does not match"):
            check_version(self.root, "v0.3.1")

    def test_unexpected_distribution_name_is_rejected(self):
        self.metadata.write_text('[project]\nname = "open-wish"\nversion = "0.3.1"\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "must be openwish"):
            check_version(self.root)

    def test_nonstable_or_ambiguous_versions_are_rejected(self):
        for version in ("0.3.1rc1", "0.3.1-rc.1", "03.1.0", "latest"):
            with self.subTest(version=version):
                self.metadata.write_text(f'[project]\nname = "openwish"\nversion = "{version}"\n', encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "stable MAJOR.MINOR.PATCH"):
                    check_version(self.root)
