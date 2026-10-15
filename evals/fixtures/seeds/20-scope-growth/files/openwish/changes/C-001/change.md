+++
id = "C-001"
title = "Complete one production recipe in the browser"
needs = ["N-001", "N-002", "N-003", "N-004", "N-005"]
status = "in-progress"
mode = "fast-forward"
+++

## Purpose

One player completes one production recipe in the browser and receives its goods.

## Scope

- **Delivers now:** one recipe, its completion rule and its browser controls.
- **Preserves:** inputs are consumed exactly once.
- **Defers:** other recipes.

## Approach

Owner decision (2026-10-10): recipes complete on a timer, not immediately.

Tooling is installed and builds (T-001).

## Verification

Exit evidence: the recipe completes on its timer and delivers goods once; the owner checks the controls on a phone.

## Handoff

Recipe rules in the recipe module and its tests.
