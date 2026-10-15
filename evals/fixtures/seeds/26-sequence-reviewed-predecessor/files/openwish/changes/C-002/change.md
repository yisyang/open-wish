+++
id = "C-002"
title = "Checkout for held seats"
needs = ["N-002"]
status = "open"
mode = "default"
after = ["C-001"]
+++

## Purpose

Buyers pay for held seats and receive tickets.

## Scope

- **Delivers now:** payment and ticket issue.
- **Preserves:** holds.
- **Defers:** refunds (C-003).

## Approach

Checkout calls `reserveSeats(eventId, seatIds)` from the seat map before charging.

## Verification

Exit evidence: one ticket per paid seat.

## Handoff

To be planned.

Planning is incomplete.
