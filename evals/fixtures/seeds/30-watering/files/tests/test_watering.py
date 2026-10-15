"""N-001: a plant is due once its species' interval has passed since it was last watered."""

from datetime import date
import unittest

from watering import due_today


class DueToday(unittest.TestCase):
    def test_due_once_the_interval_has_passed(self):
        self.assertFalse(due_today("basil", date(2026, 5, 1), date(2026, 5, 2)))
        self.assertTrue(due_today("basil", date(2026, 5, 1), date(2026, 5, 3)))

    def test_unknown_species_is_rejected(self):
        with self.assertRaises(ValueError):
            due_today("cactus", date(2026, 5, 1), date(2026, 5, 3))


if __name__ == "__main__":
    unittest.main()
