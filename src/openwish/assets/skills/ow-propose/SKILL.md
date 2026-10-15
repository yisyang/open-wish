---
name: ow-propose
description: Interpret an ask that changes product behavior in an OW project, or an explicit OW request. Reuse or revise durable needs, choose direct or managed delivery, and scope reviewable changes. Trivial edits within existing intent need no skill; honor OW opt-outs.
---

# Propose

Read `openwish/policy.md`, run `ow context` (needs and work state), and inspect the
relevant code and tests.

1. **Interpret the ask.** Identify the actor, the valuable outcome, how to observe
   it, and genuine constraints. Keep every condition, exception, unit and boundary
   that distinguishes acceptable behavior, in the need or its referenced rules; a
   shorter outcome must not erase one. Mark which rules the human stated or
   approved, which are engineering choices, and which are open proposals.
2. **Match existing intent** using Right-size intent below. If the outcome already
   exists, explain it. Revise a need in place, keeping its ID, when intent evolves.
   Leave `confirmed_at` empty for inferred intent. If an active change already
   covers the ask, continue it.
3. **Choose delivery** (policy). Direct work continues through `ow-align` and
   `ow-plan` in the session, with no change records. Respect plan-only requests.
4. **Scope changes** for managed work using Right-size delivery below. For each increment:
   `ow new change C-001 --title "..." --need N-001`, then fill in purpose, scope,
   approach and verification (formats in `openwish/artifacts.md`).
5. **Clarify** only consequential uncertainty or conflict, in one A/B/C question
   set. Keep current constraints until a human decides.
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
- **Not a need:** how the code is built (data-driven dispatch, module splits,
  dependency direction, testability). These are engineering duties (`ow-align`)
  kept in code, tests and module headers; project-wide ones, such as reproducible
  setup or release controls, are engineering requirements (policy). A requested
  extension property, such as "a new kind needs only data", is protected by a test
  that adds one. It becomes a need only when someone other than a developer gains
  the capability, such as staff adding kinds without a release.
- Test a candidate: does the outcome survive replacing the implementation? Does each
  acceptance criterion explain that outcome? Could part of it stop mattering while
  the rest remains?
- Merge duplicates and split independent outcomes without losing acceptance or
  constraints. Get a human decision when meaning changes, and reconcile relations
  and change references when an ID is replaced.

Keep needs true as the product is tuned and rebuilt, and readable after a break:

- **Rules, not calibration.** Acceptance holds structural rules: what exists, who
  may do what, limits, exceptions, consequences. Detailed rules and tunable values
  (prices, rates, durations, thresholds) live once in code, domain data or a
  referenced doc (`references = [...]`). Would
  retuning the value after a pilot change what the human wants? If not, it is
  calibration. A boundary's meaning (is day 14 late?) stays with its rule. State a
  rule shared by several kinds once, with each kind's values in its table row.
  An unsettled value does not block its mechanism: a labeled placeholder in its
  home may back schemas, interfaces and test fixtures, never shipped behavior that
  depends on the value. Record the question in `open`.
- **Outcomes, not setup.** Hosts, tools, sibling repositories and test accounts
  belong in ordinary docs; the need states only the requirement.
- **Sentences.** One observable criterion per acceptance item, in plain sentences
  its owner understands without the change; no slash-lists or shorthand.
- **Confirmed means all of it.** Undecided questions and proposed criteria go in
  `open`, one sentence each, and do not bind. Raise open items an ask touches in the
  clarifying questions; once decided, move each into acceptance, a rule or the body,
  or drop it. Moving unapproved items into `open`, or rewording without changing
  meaning, keeps `confirmed_at`.

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
A need reference means "contributes to", not "fully delivers": link the needs whose
outcome the change advances. Needs it only has to respect, such as consistency or
interface conventions, bind through review anyway; linking them adds noise. Deferral
never excuses violating a current constraint or dropping an agreed result.

For a broad build, propose a sequence. For example, a clinic scheduling product might
start with one clinician's bookable calendar that a patient can book end to end, then
reminders, then multi-site staffing.

Write tasks only for **ready** increments expected to start soon: their prerequisite
capabilities exist in the repository and no material decision is open. For a
resumable plan, record the rest as open changes with scope, prerequisites,
uncertainties, exit evidence and empty task lists, and say their planning is
incomplete; plan or split out investigations that can run now. Name each change's
predecessors with `--after`: the changes whose delivered results it builds on, not
merely earlier ones. It is planned once they pass (Plan a candidate in `ow-plan`).
Prerequisites describe capabilities to verify in code and tests, never another
change's tasks or files. If a human wants detailed tasks everywhere, note once that
blocked ones will need re-planning, then comply.

When new requirements arrive, ask these questions again. Repair tasks within the
current boundary; scope separately acceptable additions as new changes (Reconcile
the plan in `ow-plan`).

## Relationships

Record a relation on a need only for a durable semantic fact, with a concrete
reason: `requires` (the source outcome needs the target) or `constrains` (the
source limits acceptable solutions for the target), never from shared code, task
order or co-occurring changes. `ow graph --json` focuses investigation; unlinked
current needs still bind. On intent edits, check incoming and outgoing links and
possible new interactions rather than reassessing all pairs.
