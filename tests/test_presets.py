import json

from openwish.context import context_data
from openwish.integrations import install_skills
from openwish.presets import DEFAULTS, available_presets, overridden, preset_text
from openwish.validation import validate
from tests.support import ProjectCase


class PresetTests(ProjectCase):
    def configure(self, **values):
        path = self.root / "openwish/config.json"
        path.write_text(json.dumps({**json.loads(path.read_text()), **values}), encoding="utf-8")

    def policy(self, text):
        (self.root / "openwish/policy.md").write_text(text, encoding="utf-8")

    def test_each_shipped_preset_replaces_only_defaults_a_project_may_change(self):
        for name in available_presets():
            names = overridden(preset_text(name))
            self.assertTrue(names, f"{name} names no default it replaces")
            self.assertLessEqual(set(names), set(DEFAULTS), name)

    def test_selected_presets_validate_and_are_listed_in_context(self):
        self.configure(presets=["prerelease", "game-balance"])
        self.assertEqual(validate(self.project()), [])
        rows = context_data(self.project())["presets"]
        self.assertEqual([(row["name"], row["overrides"]) for row in rows],
                         [("prerelease", ["stage"]), ("game-balance", ["calibration"])])

    def test_unknown_or_repeated_presets_are_rejected(self):
        self.configure(presets=["prerelease", "prerelease", "move-fast"])
        errors = "\n".join(validate(self.project()))
        self.assertIn("duplicate presets", errors)
        self.assertIn("unknown preset move-fast", errors)

    def test_policy_may_override_a_listed_default_but_no_other_rule(self):
        self.policy("# Project policy\n\n## Test tiers\n\nOverrides: `verification`\n\nUnit runs stay under 30 s.\n")
        self.assertEqual(validate(self.project()), [])
        self.policy("# Project policy\n\n## Speed\n\nOverrides: `independent-review`\n\nShip unreviewed.\n")
        self.assertIn("'independent-review' is not a default a project may override",
                      "\n".join(validate(self.project())))

    def test_every_preset_is_installed_beside_the_core_skill(self):
        install_skills(self.root, "claude")
        for name in available_presets():
            self.assertTrue((self.root / f".claude/skills/ow-core/presets/{name}.md").is_file())
