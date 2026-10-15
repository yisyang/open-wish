"""N-004: cleaned, uninspected rooms are ready for inspection."""

import unittest

from housekeeping.inspection import ready_for_inspection


class Inspection(unittest.TestCase):
    def test_cleaned_rooms_are_ready(self):
        self.assertTrue(ready_for_inspection({"cleaned": True}))
        self.assertFalse(ready_for_inspection({"cleaned": True, "inspected": True}))
        self.assertFalse(ready_for_inspection({"cleaned": False}))
