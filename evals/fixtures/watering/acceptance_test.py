"""External checks: PROJECT_DIR=... STAGE=1|2|3 [ARM=skills OW_CALLS=... OW=...] python acceptance_test.py -v.

Behavior is checked for both arms. For the OW arm the workflow is checked too: stage 1 is
one bounded result, so it is delivered directly with no change records; stage 2 needs
deferral and delayed acceptance, so a managed change must hold evidence-backed done work,
an open manual check and the open question; stage 3 continues that same change.
"""

from datetime import date
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest

ROOT = Path(os.environ["PROJECT_DIR"]).resolve()
STAGE = int(os.environ.get("STAGE", "3"))
OW_ARM = os.environ.get("ARM", "skills") == "skills"
sys.path.insert(0, str(ROOT))  # import the product as its own modules would
watering = importlib.import_module("watering")
LAST, TWO_DAYS_LATER = date(2026, 5, 1), date(2026, 5, 3)


def calls():
    path = Path(os.environ.get("OW_CALLS", "/nonexistent"))
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def changes():
    found = []
    for path in sorted((ROOT / "openwish/changes").glob("*/change.md")):
        meta = tomllib.loads(path.read_text(encoding="utf-8").split("+++")[1])
        tasks = json.loads(path.with_name("tasks.json").read_text(encoding="utf-8"))["tasks"]
        found.append((meta, tasks))
    return found


def need():
    return tomllib.loads((ROOT / "openwish/needs/N-001.md").read_text(encoding="utf-8").split("+++")[1])


class Behavior(unittest.TestCase):
    def test_interval_rule_is_preserved(self):
        self.assertFalse(watering.due_today("basil", LAST, date(2026, 5, 2)))
        self.assertTrue(watering.due_today("basil", LAST, TWO_DAYS_LATER))
        with self.assertRaises(ValueError):
            watering.due_today("cactus", LAST, TWO_DAYS_LATER)

    def test_rain_skip(self):
        self.assertFalse(watering.due_today("basil", LAST, TWO_DAYS_LATER, rain_mm=10))
        self.assertTrue(watering.due_today("basil", LAST, TWO_DAYS_LATER, rain_mm=9.9))

    @unittest.skipUnless(STAGE >= 2, "the frost hold arrives in stage 2")
    def test_frost_hold_for_tender_species(self):
        self.assertFalse(watering.due_today("basil", LAST, TWO_DAYS_LATER, frost=True))
        self.assertTrue(watering.due_today("basil", LAST, TWO_DAYS_LATER, frost=False))

    @unittest.skipUnless(STAGE >= 3, "the hardy exemption is decided in stage 3")
    def test_hardy_species_ignore_frost(self):
        self.assertTrue(watering.due_today("rosemary", LAST, date(2026, 5, 8), frost=True))
        self.assertFalse(watering.due_today("tomato", LAST, date(2026, 5, 8), frost=True))


@unittest.skipUnless(OW_ARM, "workflow records apply to the OW arm")
class Workflow(unittest.TestCase):
    def test_project_still_validates(self):
        result = subprocess.run([os.environ["OW"], "--root", str(ROOT), "check", "--artifacts-only"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(STAGE == 1, "stage 1 is direct")
    def test_bounded_work_is_delivered_directly(self):
        self.assertEqual(changes(), [], "direct delivery leaves no change")
        managed = [call for call in calls() if call.split()[:2] in (["new", "change"], ["record-review"])
                   or call.split()[:1] in (["task"], ["close"], ["clean"])]
        self.assertEqual(managed, [], "direct delivery runs no change, task, review or cleanup commands")

    @unittest.skipUnless(STAGE >= 2, "coordination appears in stage 2")
    def test_deferred_work_is_managed_with_evidence(self):
        active = [(meta, tasks) for meta, tasks in changes() if meta["status"] != "closed"]
        self.assertEqual(len(active), 1, "one active change holds the frost work")
        meta, tasks = active[0]
        self.assertIn("N-001", meta["needs"])
        done = [task for task in tasks if task["status"] == "done"]
        self.assertTrue(done and all(task["evidence"].strip() for task in done), "done work carries evidence")
        manual = [task for task in tasks if task.get("kind") == "manual" and task["status"] != "done"]
        self.assertTrue(manual, "the owner's tablet check stays an open manual task")

    @unittest.skipUnless(STAGE == 2, "the hardy question is open in stage 2")
    def test_undecided_rule_is_recorded_as_open(self):
        self.assertTrue(any("hardy" in item.lower() for item in need().get("open", [])))

    @unittest.skipUnless(STAGE == 3, "stage 3 continues the change")
    def test_decision_continues_the_same_change(self):
        self.assertFalse([call for call in calls() if call.split()[:2] == ["new", "change"]],
                         "the decided rule belongs to the active change")
        self.assertFalse([item for item in need().get("open", []) if "hardy" in item.lower()],
                         "the decided question leaves the open list")


if __name__ == "__main__":
    unittest.main()
