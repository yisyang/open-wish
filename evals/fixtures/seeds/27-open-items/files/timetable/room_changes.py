"""Publishes room changes to the channel of each affected class."""


def channels_for(change, classes):
    return [f"class:{cls}" for cls in classes if change["room_from"] in classes[cls]]
