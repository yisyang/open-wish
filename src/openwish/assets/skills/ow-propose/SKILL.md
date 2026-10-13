---
name: ow-propose
description: Interpret a substantive software ask in an OW-managed project, or an explicit OW request. Reuse or revise durable needs and scope reviewable changes. Routine coding does not require this skill; honor OW opt-outs.
---

# Propose

Read `openwish/policy.md`, run `ow context`, and inspect the relevant code and tests.

1. **Interpret the ask.** Identify the actor, the valuable outcome, how to observe
   it, and genuine constraints. Keep every condition, exception, unit and boundary
   that distinguishes acceptable behavior; a shorter outcome must not erase one.
   Mark which rules the human stated or approved, which are engineering choices,
   and which are open proposals.
2. **Match existing intent** using Right-size intent below. If the outcome already
   exists, explain it. Revise a need in place, keeping its ID, when intent evolves.
   Leave `confirmed_at` empty for inferred intent.
3. **Choose the path.** Routine work goes straight to inspect → implement → verify →
   report, with no records. Respect plan-only requests.
4. **Scope changes** using Right-size delivery below. For each selected increment:
   `ow new change C-001 --title "..." --need N-001`, then fill in purpose, scope,
   approach and verification (formats in `openwish/artifacts.md`).
5. **Clarify** only consequential uncertainty or conflict, in one numbered A/B/C
   question set with `(Recommended)`. Keep current constraints until a human decides.
6. **Continue** to `ow-align` and `ow-plan`. Preparing a plan needs no approval;
   plan-only requests stop after planning.

If nothing needs to change, explain the existing outcome and stop.

## Right-size intent

A need is one coherent valuable outcome, independent of mechanism and effort.

- **Too small:** a format, button, module or task with no separate value. SMS and
  email reminders for the same appointment workflow reuse one need.
- **Too broad:** acceptance bundles outcomes that could be accepted, changed or
  retired separately. Booking appointments and letting clinicians audit who
  changed a booking may be separate needs.
- Test a candidate: does the outcome survive replacing the implementation? Does each
  acceptance criterion explain that outcome? Could part of it stop mattering while
  the rest remains?
- Merge duplicates and split independent outcomes without losing acceptance or
  constraints. Get a human decision when meaning changes, and reconcile relations
  and change references when an ID is replaced.
- Detailed rules can live in code, domain data or a referenced doc
  (`references = [...]`); the need keeps the binding outcome and important
  constraints. Approved but deferred rules need a retained home now: another open
  change or domain data.

## Right-size delivery

A change is sized by a reviewable delivery boundary, not by needs or effort. Before
planning tasks, answer:

- What concrete capability will exist after this change?
- What evidence would let someone accept it, keep it, and postpone later work
  without leaving this increment broken?
- Does any task hide a separately useful subsystem or workflow?
- Which unknowns could change the approach? Investigate them early with an
  observable result.

Split independently acceptable improvements. Combine work that needs joint
acceptance, such as a contract and its only consumer. Shared code or a later
feature using an earlier one is a sequence, not a reason to merge. Prefer narrow
end-to-end slices (interface, logic, persistence and checks) over building every
layer first. One narrow cross-cutting fix may reasonably reference many needs.

Write each change's **delivers now**, **preserves**, **defers** and **exit evidence**.
A need reference means "contributes to", not "fully delivers". Deferral never
excuses violating a current constraint or dropping an agreed result.

For a broad build, propose a sequence. For example, a clinic scheduling product might
start with one clinician's bookable calendar that a patient can book end to end, then
reminders, then multi-site staffing. Detail the next executable increment. If the
human wants a resumable plan, record later increments as open changes with scope,
prerequisite capabilities, uncertainties and exit evidence, and empty task lists
until selected; say that their planning is incomplete. Prerequisites name
capabilities to verify in code and tests, not tasks in other changes.

When new requirements arrive, ask these questions again. Repair tasks within the
current boundary; scope separately acceptable additions as new changes (see
Reconcile the plan in `ow-plan` when splitting). New changes default to human
review, even when split from a fast-forward change.

## Relationships

Record a relation on a need only for a durable semantic fact, with a concrete
reason: `requires` (the source outcome needs the target) or `constrains` (the
source limits acceptable solutions for the target). Do not derive relations from
shared code, task order or co-occurring changes. Use `ow graph --json` to focus
investigation; unlinked current needs still bind. On intent edits, check incoming
and outgoing links and possible new interactions rather than reassessing all pairs.
