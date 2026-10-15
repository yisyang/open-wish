+++
id = "C-007"
title = "Fix the shared exact-money parser"
needs = ["N-001", "N-002", "N-003", "N-004", "N-005", "N-006", "N-007", "N-008", "N-009", "N-010", "N-011", "N-012", "N-013", "N-014", "N-015", "N-016", "N-017", "N-018"]
status = "in-progress"
mode = "default"
+++

## Purpose

Parse money strings into exact cents everywhere, and keep the serializer contract that depends on it.

## Scope

- **Delivers now:** the parser fix and its inseparable serializer contract.
- **Preserves:** every existing consumer's results.
- **Defers:** nothing; future features reuse the parser when built.

## Approach

One shared parser in `money/parse.py`; the serializer in `money/serialize.py` emits the same exact form.

## Verification

Exit evidence: parser property checks and regression checks of existing consumers.

## Handoff

Parser and serializer in `money/`; checks in `tests/test_money.py`.
