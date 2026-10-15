"""N-002: every ingredient appears once per unit with merged quantities."""

import unittest

from app.list_builder import build


class ListBuilder(unittest.TestCase):
    def test_merges_same_ingredient_and_unit(self):
        meals = [{"ingredients": [{"name": "milk", "unit": "ml", "quantity": 200}]},
                 {"ingredients": [{"name": "milk", "unit": "ml", "quantity": 300}]}]
        self.assertEqual(build(meals), [{"name": "milk", "unit": "ml", "quantity": 500}])
