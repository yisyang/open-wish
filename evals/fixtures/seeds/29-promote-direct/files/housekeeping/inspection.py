"""Decides whether a room is ready for inspection (pure)."""


def ready_for_inspection(room):
    return room["cleaned"] and not room.get("inspected", False)
