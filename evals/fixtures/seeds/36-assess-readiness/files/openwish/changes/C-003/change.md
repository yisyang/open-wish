+++
id = "C-003"
title = "Monthly bill credits"
needs = ["N-002"]
status = "open"
mode = "default"
after = ["C-001"]
+++

## Purpose

Credit each member monthly for their share of production.

## Scope

- Delivers now: monthly credit run and per-member credit breakdown (N-002).
- Defers: nothing.
- Prerequisites: shares (C-001); each share's metered monthly production.

## Approach

Credit = share kW / array kW × metered kWh × credit rate, per docs/credits.md.

## Verification

Worked examples in docs/credits.md as tests; a month with a mid-month share
purchase.
