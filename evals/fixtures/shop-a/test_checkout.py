import unittest
from unittest.mock import mock_open, patch

from checkout import checkout


class CheckoutTests(unittest.TestCase):
    def test_receipt_is_written(self):
        with patch("pathlib.Path.open", mock_open()) as output:
            checkout([{"price": 100, "quantity": 2}])
            output.assert_called_once_with("a")
            output().write.assert_called_once()
