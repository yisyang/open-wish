"""Exact money parsing and serializer round trips."""

import unittest

from money.parse import parse
from money.serialize import serialize


class Money(unittest.TestCase):
    def test_round_trip(self):
        for cents in (0, 5, -5, 123456):
            self.assertEqual(parse(serialize(cents)), cents)
