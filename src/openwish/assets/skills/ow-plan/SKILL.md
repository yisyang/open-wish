---
name: ow-plan
description: Plan substantive OW work after alignment or repair a structured execution plan. Routine changes need no epics or gates. Honor OW opt-outs and plan-only requests.
---

# Plan

Read `openwish/policy.md`, `ow context N-001 ...`, and affected spec designs.
Preparation does not require separate alignment receipts. The combined authority
below replaces legacy generated per-stage prompts; honor deliberate project controls.

1. Inspect current code, conventions, verification commands, and operational
   constraints. Determine what remains for the needs; reuse working behavior.
2. Create/update bounded epic designs referencing specs. Preserve the complete
   need → spec design → epic → task relationship. Do not create a separate work
   container or stored ask. Split large epics into useful task groups.
   Set each epic's `needs` to the outcomes it actually implements, a nonempty
   subset of its spec designs' need references. Shared specs retain all regression
   constraints without requiring unrelated needs' implementation authorization.
3. Give tasks concrete acceptance, likely files, kind, prerequisites, and increasing
   `(group, order)` pairs across all work for a need. Cross-epic prerequisites are
   explicit; no lower ordinal can depend on a higher one. Inspect the actual DAG.
4. Prefer minimal coherent increments and functional cores. Put indispensable
   manual observations late, keeping independent agent work executable. Target
   meaningful routine verification under five minutes; identify necessary slower checks.
5. Repair technical inconsistencies against approved designs and all affected
   needs. Material intent/design revisions return to the relevant earlier phase.
   Reopened needs may retain old done tasks; plan only what now remains.
6. Run `ow check`. If asked only to plan, present the plan and stop. Otherwise,
   use the existing instruction when it clearly authorizes this scope, including
   delegated technical details. If it does not, ask once for the combined outcome,
   approach, and implementation scope. Use a numbered question and meaningful
   A/B/C choices with `(Recommended)` before the preferred text. Do not ask again
   for a previously authorized scope merely because artifacts were relinked.
7. Record `ow authorize N-001 ... --by human` from actual conversation authority,
   or `--by fast-forward` in explicitly selected fast-forward mode. This records
   needs/alignment/implementation together; final acceptance is separate. Continue
   to `ow-implement`. Authority covers each epic's execution needs, not every
   regression constraint linked through its specs.
