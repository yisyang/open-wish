+++
id = "S-003"
title = "CLI and portable harness workflows"
depends_on = ["S-001", "S-002"]
parent = ""
implementation = "review"
+++

## Contract

- A Python 3.11+ CLI initializes, scaffolds, validates, reports context/status,
  schedules ready work, and records revision-bound decisions/reviews.
- The `openwish` PyPI distribution exposes `ow` through `uv tool install openwish`.
  Stable GitHub releases publish tested wheel/source artifacts after matching the
  release tag, package version, and CLI version. Manual rehearsals use TestPyPI.
- Eight skills cover propose, align, plan, implement, review, consolidate,
  fast-forward, and onboarding using one canonical workflow.
- OpenCode and Claude Code expose `/fast-forward` and `/onboard`; Codex uses
  portable skill invocation.
- `ow init` offers terminal multi-selection of supported harnesses and explicit
  multiple-harness flags for scripts. Existing selections are preselected.
- Initialization also updates integrations: older OW versions are overwritten,
  equal versions receive no writes, and downgrades require explicit confirmation.
  Declining retains newer files while other selected installs/upgrades proceed.
- Existing project artifacts are preserved on reinitialization. Unknown
  unversioned files produce a conflict before any selected integration is written.
- Skills clarify real intent, classify conflicts, inspect code before planning,
  continue authorized work, and present compact review outcomes.
- Confirmations show only the current decision. Clarifications use numbered
  questions and two or three A/B/C choices, with `(Recommended)` before the
  preferred text and concise effect clauses where useful.
- Final summaries explain needs and spec outcomes; task output carries lineage
  through the need references in spec designs.
- Onboarding labels inference; consolidation promotes current operational facts
  before removing completed execution details.

## Scenarios

Selecting OpenCode and Claude Code initializes both. Reinitializing at the same
version preserves edited skills and their timestamps. A newer CLI overwrites older
OW skills and adapters; an older CLI asks before replacing newer files. Cancelling
selection writes nothing. Downgrading without a terminal fails before writing.
Fast-forward reaches final acceptance without a human approval prompt; default
mode explicitly asks at that point.
