"""External checks: PROJECT_DIR=... STAGE=1|2|3|4 python acceptance_test.py -v."""

import importlib.util
import os
from pathlib import Path
import unittest

ROOT = Path(os.environ["PROJECT_DIR"])
STAGE = int(os.environ.get("STAGE", "4"))
spec = importlib.util.spec_from_file_location("evaluated_lending", ROOT / "lending.py")
lending = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lending)
BOOK_CAP = 1500 if STAGE >= 3 else 1000


class LateFees(unittest.TestCase):
    def test_on_time_and_early_returns_are_free(self):
        self.assertEqual(lending.late_fee("2026-03-10", "2026-03-10", "book"), 0)
        self.assertEqual(lending.late_fee("2026-03-10", "2026-03-01", "reference"), 0)

    def test_book_grace_then_every_late_day_is_charged(self):
        self.assertEqual(lending.late_fee("2026-03-10", "2026-03-12", "book"), 0)
        self.assertEqual(lending.late_fee("2026-03-10", "2026-03-13", "book"), 75)

    def test_reference_items_have_no_grace(self):
        self.assertEqual(lending.late_fee("2026-03-10", "2026-03-11", "reference"), 100)

    def test_caps(self):
        self.assertEqual(lending.late_fee("2026-01-01", "2026-12-31", "book"), BOOK_CAP)
        self.assertEqual(lending.late_fee("2026-01-01", "2026-12-31", "reference"), 5000)

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            lending.late_fee("2026-03-10", "2026-03-20", "map")

    @unittest.skipUnless(STAGE >= 4, "DVDs arrive in stage 4")
    def test_dvd_policy(self):
        self.assertEqual(lending.late_fee("2026-03-10", "2026-03-11", "dvd"), 0)
        self.assertEqual(lending.late_fee("2026-03-10", "2026-03-12", "dvd"), 100)
        self.assertEqual(lending.late_fee("2026-01-01", "2026-12-31", "dvd"), 2000)


@unittest.skipUnless(STAGE >= 2, "renewals arrive in stage 2")
class Renewals(unittest.TestCase):
    def test_books_renew_twice_without_holds(self):
        self.assertTrue(lending.can_renew("book", 1, 0))
        self.assertFalse(lending.can_renew("book", 2, 0))
        self.assertFalse(lending.can_renew("book", 0, 1))

    def test_reference_items_never_renew(self):
        self.assertFalse(lending.can_renew("reference", 0, 0))

    def test_invalid_counts_and_kinds_are_rejected(self):
        for args in (("book", -1, 0), ("book", 0, -1), ("map", 0, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                lending.can_renew(*args)

    @unittest.skipUnless(STAGE >= 4, "DVDs arrive in stage 4")
    def test_dvds_renew_once(self):
        self.assertTrue(lending.can_renew("dvd", 0, 0))
        self.assertFalse(lending.can_renew("dvd", 1, 0))


class Disposal(unittest.TestCase):
    def test_completed_plans_are_disposed(self):
        import tomllib
        for path in (ROOT / "openwish/changes").glob("*/change.md"):
            metadata = tomllib.loads(path.read_text().split("+++")[1])
            self.assertNotEqual(metadata["status"], "closed", f"Undisposed change: {path}")


if __name__ == "__main__":
    unittest.main()
