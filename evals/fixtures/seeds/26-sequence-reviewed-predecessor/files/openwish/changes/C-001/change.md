+++
id = "C-001"
title = "Seat map with seat holds"
needs = ["N-001"]
status = "open"
mode = "default"
+++

## Purpose

Buyers see the seat map and hold seats.

## Scope

- **Delivers now:** the seat map and seat holds.
- **Preserves:** one holder per seat.
- **Defers:** checkout (C-002).

## Approach

Holds live in `src/seats/hold.ts`.

## Verification

Exit evidence: concurrent holds of one seat yield one holder.

## Handoff

Hold behavior in `src/seats/hold.ts` and its tests.
