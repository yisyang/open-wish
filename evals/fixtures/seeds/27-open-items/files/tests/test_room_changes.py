"""N-003: room changes reach the affected class."""

import unittest

from timetable.room_changes import channels_for


class RoomChanges(unittest.TestCase):
    def test_only_affected_classes(self):
        self.assertEqual(channels_for({"room_from": "B2"}, {"7A": {"B2"}, "7B": {"C1"}}), ["class:7A"])
