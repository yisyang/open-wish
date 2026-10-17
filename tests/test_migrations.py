import json
from pathlib import Path

from openwish.integrations import asset, load_manifest
from openwish.migrations import apply_migration, plan_migration
from openwish.scaffold import initialize
from openwish.storage import WishError, read_json, write_json

from tests.support import ProjectCase

SCHEMA_4 = Path(__file__).resolve().parent / "fixtures/schema-4"
ENGINEERING_ROW = ("| Engineering requirements: how the product is built, checked and released | "
                   "An ordinary doc, linked here once it exists |")
LINKED_ROW = ("| Engineering requirements: how the product is built, checked and released | "
              "[Development guide](../docs/development.md) |")


class MigrationTests(ProjectCase):
    """Schema 4 kept OW's policy and reference in openwish/; schema 5 keeps only project knowledge there."""

    def schema_4(self, *, policy=None, reference=None):
        self.fixture()
        config = self.root / "openwish/config.json"
        write_json(config, {**read_json(config), "version": 4})
        text = (SCHEMA_4 / "policy.md").read_text() if policy is None else policy
        (self.root / "openwish/policy.md").write_text(text, encoding="utf-8")
        reference_text = (SCHEMA_4 / "artifacts.md").read_text() if reference is None else reference
        (self.root / "openwish/artifacts.md").write_text(reference_text, encoding="utf-8")
        manifest = load_manifest(self.root)
        manifest["files"]["openwish/artifacts.md"] = "0.9.1"
        write_json(self.root / "openwish/installation.json", manifest)

    def adapted_policy(self):
        text = (SCHEMA_4 / "policy.md").read_text().replace(ENGINEERING_ROW, LINKED_ROW)
        return text + ("\n## Team rules\n\n- Releases wait for the support rota to confirm cover.\n"
                       "- Hotfixes name their rollback owner.\n")

    def files(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def test_new_projects_keep_only_project_knowledge_in_openwish(self):
        self.assertEqual((self.root / "openwish/policy.md").read_text(), asset("project-policy.md"))
        self.assertFalse((self.root / "openwish/artifacts.md").exists())
        self.assertTrue((self.root / ".agents/skills/ow-core/SKILL.md").is_file())
        self.assertIn("# OW artifact reference", (self.root / ".agents/skills/ow-core/artifacts.md").read_text())
        self.assertEqual(read_json(self.root / "openwish/config.json")["version"], 5)

    def test_migration_keeps_project_rules_and_drops_text_ow_now_ships(self):
        self.schema_4(policy=self.adapted_policy())
        report = initialize(self.root, "generic")
        policy = (self.root / "openwish/policy.md").read_text()
        self.assertTrue(policy.startswith(asset("project-policy.md").rstrip("\n")))
        self.assertIn("## Team rules\n\n- Releases wait for the support rota to confirm cover.\n"
                      "- Hotfixes name their rollback owner.", policy)
        # An adapted OW row stays, rebuilt as a valid table, and is reported for review.
        self.assertIn("| Knowledge | Home |\n| --- | --- |\n" + LINKED_ROW, policy)
        self.assertNotIn("Humans ask. AI identifies needs", policy)
        self.assertNotIn("| Current needs |", policy)
        notes = "\n".join(report["migration"]["notes"])
        self.assertIn("## Where knowledge lives", notes)
        self.assertIn("## Team rules", notes)
        self.assertFalse((self.root / "openwish/artifacts.md").exists())
        self.assertNotIn("openwish/artifacts.md", load_manifest(self.root)["files"])
        self.assertEqual(read_json(self.root / "openwish/config.json")["version"], 5)
        self.assertEqual(self.cli("check").returncode, 0)

    def test_unadapted_policy_becomes_the_project_template(self):
        self.schema_4()
        report = initialize(self.root, "generic")
        self.assertEqual((self.root / "openwish/policy.md").read_text(), asset("project-policy.md"))
        self.assertFalse(any("kept project text" in note for note in report["migration"]["notes"]))

    def test_edited_reference_is_kept_as_the_projects_and_reported(self):
        edited = (SCHEMA_4 / "artifacts.md").read_text() + "\nOur team's note on review handoffs.\n"
        self.schema_4(reference=edited)
        report = initialize(self.root, "generic")
        self.assertEqual((self.root / "openwish/artifacts.md").read_text(), edited)
        self.assertIn("openwish/artifacts.md: edited", "\n".join(report["migration"]["notes"]))

    def test_rerun_and_interrupted_migration_converge(self):
        self.schema_4(policy=self.adapted_policy())
        plan = plan_migration(self.root)
        # Interrupted before the schema version was written: the policy is already migrated.
        (self.root / "openwish/policy.md").write_text(plan["writes"]["openwish/policy.md"], encoding="utf-8")
        initialize(self.root, "generic")
        self.assertEqual((self.root / "openwish/policy.md").read_text(), plan["writes"]["openwish/policy.md"])
        before = self.files()
        self.assertIsNone(initialize(self.root, "generic")["migration"])
        self.assertEqual(self.files(), before)

    def test_failed_preflight_changes_nothing(self):
        self.schema_4()
        write_json(self.root / "openwish/installation.json", {"format": 1, "harnesses": [], "files": []})
        before = self.files()
        with self.assertRaises(WishError):
            initialize(self.root, "generic")
        self.assertEqual(self.files(), before)

    def test_other_commands_ask_for_init_on_an_older_schema(self):
        self.schema_4()
        before = self.files()
        for args in (("check",), ("status",), ("new", "need", "N-009", "--title", "Need")):
            self.assertIn("run 'ow init' to migrate", self.cli(*args, success=False).stderr)
        self.assertEqual(self.files(), before)
        self.assertIn("Migrated OW schema 4 to 5.", self.cli("init", "--harness", "generic").stdout)

    def test_apply_writes_the_schema_version_last(self):
        self.schema_4(policy=self.adapted_policy())
        plan = plan_migration(self.root)
        order = []
        import openwish.migrations as migrations
        original = migrations.write_text
        migrations.write_text = lambda path, text, **kw: (order.append(path.name), original(path, text, **kw))
        try:
            apply_migration(self.root, plan)
        finally:
            migrations.write_text = original
        self.assertEqual(order[-1], "config.json")
        self.assertEqual(json.loads((self.root / "openwish/config.json").read_text())["version"], 5)
