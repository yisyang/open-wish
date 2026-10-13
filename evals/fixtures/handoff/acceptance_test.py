"""External checks: PROJECT_DIR=... STAGE=1|2 python acceptance_test.py -v."""

import importlib.util
import os
from pathlib import Path
import unittest

ROOT = Path(os.environ["PROJECT_DIR"])
STAGE = int(os.environ.get("STAGE", "2"))
spec = importlib.util.spec_from_file_location("evaluated_rules", ROOT / "rules.py")
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)


class PublicContract(unittest.TestCase):
    def test_plain_and_organic_keep_input_basis_unchanged(self):
        self.assertEqual(rules.quote(100, 500, 100, 20, []),
                         {"cash": 600, "quality": 100, "freight": 20})
        self.assertEqual(rules.quote(100, 500, 100, 20, ["organic"]),
                         {"cash": 650, "quality": 200, "freight": 30})

    def test_round_components_once_half_up(self):
        self.assertEqual(rules.quote(1, 100, 1, 1, ["organic"]),
                         {"cash": 102, "quality": 2, "freight": 2})

    def test_invalid_selection_is_rejected(self):
        for skills in (["organic", "organic"], ["missing"], ["a", "b", "c", "d"]):
            with self.subTest(skills=skills), self.assertRaises(ValueError):
                rules.quote(100, 500, 100, 20, skills)

    @unittest.skipUnless(STAGE == 1, "first increment only")
    def test_deferred_skill_is_not_claimed_delivered(self):
        with self.assertRaises(ValueError):
            rules.quote(100, 500, 100, 20, ["efficiency"])

    @unittest.skipUnless(STAGE == 2, "second increment only")
    def test_efficiency_uses_approved_values_and_additive_stacking(self):
        self.assertEqual(rules.quote(100, 500, 100, 20, ["efficiency"]),
                         {"cash": 580, "quality": 110, "freight": 18})
        for skills in (["organic", "efficiency"], ["efficiency", "organic"]):
            self.assertEqual(rules.quote(100, 500, 100, 20, skills),
                             {"cash": 630, "quality": 210, "freight": 28})

    def test_completed_plans_are_disposed(self):
        import tomllib
        for path in (ROOT / "openwish/changes").glob("*/change.md"):
            metadata = tomllib.loads(path.read_text().split("+++")[1])
            self.assertNotEqual(metadata["status"], "closed", f"Undisposed change: {path}")


if __name__ == "__main__":
    unittest.main()
