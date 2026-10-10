---
name: ow-align
description: Align product design and engineering with all current needs for a substantive OW change. Inspect code and tests and keep working design in the change. Honor OW opt-outs and plan-only scope.
---

# Align

Read `openwish/policy.md`, `ow context C-001`, the change, and relevant code/tests.
Routine work follows the lightweight path without creating design records.

1. Review all current needs, including delivered outcomes. Retrieve retired needs
   when useful for history without making them binding again. Inspect affected
   modules, interfaces, consumers, tests, and operational constraints.
2. Distinguish incompatible intent from an implementation that cannot yet satisfy
   compatible needs. Adapt the solution; never silently weaken acceptance.
   Clarify actual decisions with numbered A/B/C options and `(Recommended)` before
   the preferred text. Technical repairs within authorized intent need no new permission.
3. Compare meaningful approaches. Put the selected working design in the change's
   approach section: boundaries, compatibility, effects, relevant trade-offs, and
   how all current constraints are preserved. Keep need references on the change.
4. Prefer cohesive modules, explicit dependency direction, functional cores, and
   effects at boundaries. Use repository structure and interfaces as the design
   map. Tests should check outcomes independently of implementation details.
5. Plan to preserve only otherwise unrecoverable rationale near code or in ordinary
   repository docs. The approach remains disposable; do not create a parallel
   persistent spec, design registry, or another artifact tier.
6. Continue to `ow-plan` without a stage approval. A material intent revision
   returns to Propose. Verification-only work can use an empty task list and an
   honest verification plan rather than invented implementation.
