---
name: ow-plan
description: Plan the remaining work for OpenWish needs through spec designs, small epics, and dependency-ordered tasks. Use after alignment or to repair a stale execution plan.
metadata:
  openwish-version: "0.3.1"
---

# Plan

Read `openwish/policy.md`, `ow context N-001 ...`, and affected spec designs.
Verify fresh alignment receipts for the selected needs with `ow status --json`.

1. Inspect current code, conventions, verification commands, and operational
   constraints. Determine what remains for the needs; reuse working behavior.
2. Create/update bounded epic designs referencing specs. Preserve the complete
   need → spec design → epic → task relationship. Do not create a separate work
   container or stored ask. Split large epics into useful task groups.
3. Give tasks concrete acceptance, likely files, kind, prerequisites, and increasing
   `(group, order)` pairs across all work for a need. Cross-epic prerequisites are
   explicit; no lower ordinal can depend on a higher one. Inspect the actual DAG.
4. Prefer minimal coherent increments and functional cores. Put indispensable
   manual observations late, keeping independent agent work executable. Target
   meaningful routine verification under five minutes; identify necessary slower checks.
5. Repair technical inconsistencies against approved designs and all affected
   needs. Material intent/design revisions return to the relevant earlier phase.
   Reopened needs may retain old done tasks; plan only what now remains.
6. Run `ow check`. Explain the remaining work by need and spec. In default mode,
   ask for implementation authority with a numbered question and two or three
   A/B/C choices, marking the preferred choice `(Recommended)` before its text.
7. Record `ow gate implement N-001 ... --by human` after authorization, or
   `--by fast-forward` without asking in that mode. Continue to `ow-implement`.
   Execution authority for shared work must cover all affected open needs.
