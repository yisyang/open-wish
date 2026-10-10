---
name: ow-plan
description: Prepare or repair tasks inside a disposable OW change after design alignment. Use for substantive or resumable work; routine changes need no records. Respect plan-only requests and OW opt-outs.
---

# Plan

Read `openwish/policy.md`, `openwish/artifacts.md`, `ow context C-001`, the working
approach, and affected source/tests. Prepare only work that remains useful.

1. Keep one bounded improvement in the change. It directly references one or more
   existing needs; it may preserve an outcome rather than introduce a new one.
2. Use a small task list in `changes/C-001/tasks.json`. Each task has an ID such
   as `C-001/T-001`, title, status, and verifiable acceptance. Add files, kind,
   and prerequisites only when useful. Completed tasks need direct evidence.
3. Order tasks for sensible execution. Optional dependencies reference tasks in
   the same change and form a DAG; there are no global group/order pairs.
   Combine tightly coupled work into one change. Coordinate independent changes
   against delivered interfaces rather than retaining cross-change task links.
4. Keep independent work executable around indispensable manual observations.
   Prefer functional cores and focused verification; keep routine checks under
   five minutes and identify necessary slower checks explicitly.
5. Include lasting code/tests and essential rationale placement in the work so
   the result remains maintainable after the change disappears. An existing
   implementation may need verification only, with no implementation tasks.
6. Run `ow check`. If asked only to plan, present the approach/tasks and stop.
   Otherwise use actual conversation authority for the prepared scope. Ask one
   meaningful combined decision only if authority or a consequential choice is
   missing; use numbered A/B/C choices with `(Recommended)` before preferred text.
7. Continue to `ow-implement`. There are no authorization commands or stage
   receipts to record. `ow ready` reports prerequisites, not permission. Technical
   plan repairs within authorized intent do not require another human decision.
