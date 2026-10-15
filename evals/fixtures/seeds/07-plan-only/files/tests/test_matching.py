"""N-001: unmatched rows are reported from both sources, matching exact cents."""

import unittest

from reconcile.matching import unmatched


class Matching(unittest.TestCase):
    def test_exact_cents_and_both_sources(self):
        statement = [{"date": "2026-09-01", "amount_cents": 1000, "memo": "a"}]
        ledger = [{"date": "2026-09-01", "amount_cents": 1001, "memo": "a"}]
        self.assertEqual([row["source"] for row in unmatched(statement, ledger)], ["statement", "ledger"])
