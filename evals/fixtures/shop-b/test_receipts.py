import io
import json
import unittest

from pricing import price
from receipts import record


class ReceiptTests(unittest.TestCase):
    def test_observable_amounts(self):
        self.assertEqual(price([{"price": 105, "quantity": 3}], 1000),
                         {"subtotal": 315, "tax": 32, "total": 347})

    def test_empty_basket(self):
        self.assertEqual(price([], 1000), {"subtotal": 0, "tax": 0, "total": 0})

    def test_record_contains_amount_and_time(self):
        output = io.StringIO()
        record([{"price": 200, "quantity": 1}], 500, 123, output)
        self.assertEqual(json.loads(output.getvalue()),
                         {"subtotal": 200, "tax": 10, "total": 210, "at": 123})
