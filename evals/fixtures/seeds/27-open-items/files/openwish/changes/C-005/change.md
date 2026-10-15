+++
id = "C-005"
title = "Live room-change updates"
needs = ["N-003"]
status = "open"
mode = "default"
+++

## Purpose

Students see room changes without reloading.

## Scope

- **Delivers now:** live room-change updates.
- **Preserves:** own-classes visibility.
- **Defers:** push notifications.

## Approach

Room changes publish to each class's channel in `timetable/room_changes.py`.

## Verification

Exit evidence: a room change reaches a subscribed student; latency measured.

## Handoff

Behavior in `timetable/room_changes.py` and `tests/test_room_changes.py`.
