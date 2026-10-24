---
name: ow-review
description: Review OW work against all current needs, code, tests and regressions; for a change, record the result, present it, and close accepted work. Direct work gets the same review without records. Honor OW opt-outs.
---

# Review

Load `ow-core`, then read `openwish/policy.md` and the actual diff.

- **Direct:** run `ow context`; apply steps 1–4, preserve lasting knowledge (every
  material decision of the session has a retained home), then report as in
  step 7. Run no record, close or clean commands.
- **Managed:** run `ow context C-001`, read the change and its tasks, and apply
  every step.
- **Task or correction review** (a task reviewed before its change is complete, or a
  re-review of a correction): apply steps 2–4 to the diff against the task's
  acceptance and the needs it affects, and return Blocking findings below. The full
  need assessment, Safe to forget and the record wait for the change's final review.

1. **Assess the needs.** Run `ow trace` and compare the traced checks and files
   with the diff.
   - **Affected needs:** the linked needs plus any whose behavior the diff touches.
     Check each with direct evidence.
   - **Unaffected needs:** every other current need. Confirm briefly why the change
     cannot violate it. If you cannot, treat it as affected.
   - **Engineering requirements** the project policy links: check the diff against them.
   Compare results with delivers-now scope and exit evidence, not ticked tasks.
   Explain partial contributions and deferrals; an empty task list is not completion.
2. **Judge the checks** (Strategic verification in `ow-plan`): would they catch a
   need violation, survive a harmless refactor, and test intent rather than repeat
   the code's own logic, and settle one outcome where outcomes differ in money,
   rights or data? Ask what plausible wrong implementation would still pass,
   and what is the strongest plausible reason the result would fail in real use;
   check it, or report it as a limitation.
3. **Judge the structure** with the Architecture rubric in `ow-align` on the changed
   paths, including whether module headers and boundary READMEs still describe them.
4. **Fix** within authorized intent and rerun affected checks, or, when another
   session will correct the work, return Blocking findings below. Keep unresolved
   manual observations and limitations visible.
5. **Make it safe to forget** (below) before recording the result.
6. **Record:** run `ow check`, then
   `ow record-review C-001 --summary "user-visible outcome" --check "command: result"
   [--affected N-003] --handoff FILE` (or `--handoff -` with JSON on stdin; format
   in the `ow-core` artifact reference). Unresolved findings use `--verdict blocked`.
   Passing needs every task done. If anything changes afterwards (successor work
   often does), `ow summary C-001` names what made the review stale: rerun the
   affected checks, confirm the outcome still holds, and record again.
7. **Present need → outcome → evidence**, how other current needs were ruled
   out, limitations, any `open` items this result makes decidable, and any
   assumptions it proceeded on (Commit progressively in `ow-plan`). Lead with the
   choices made on the human's behalf that users would notice, each a plain
   statement they can overrule (`proposed` in its home, Rule status in
   `ow-propose`), and engineering choices with recurring cost (polling or tick
   cadence, payload size, log volume, retention), each with its rate. Name plan
   misses: gaps that surfaced during implementation or review but planning should
   have caught (a missing provider, a late decision, a foundational design
   reworked), each with its cause. Propose recording a lesson that will recur in
   this product, such as "verify host access before planning deploys", in the
   project's policy, for the human to accept. Report one that shows a gap in
   OW's own guidance to OW's maintainers.
   - Default mode: ask once for human acceptance (A/B/C),
     after all available work is done. Only after actual acceptance:
     `ow close C-001 --by human`.
   - Explicit fast-forward: `ow close C-001 --by fast-forward` after the same checks,
     attributed to delegation, never to a human.
8. **Dispose and continue** via `ow-consolidate`. Needs stay current; further work
   uses a new change in default mode unless delegated again.

## Blocking findings

- **One complete list.** A blocked review lists every blocker against the whole
  acceptance at once. Each blocker comes with the check that settles it (a command
  or procedure, with its expected result or threshold) and its evidence. Corrections
  work against that list. A re-review checks the list, the correction's diff and its
  affected checks. It adds a blocker only for a regression the correction introduced
  or for a defect a listed check reveals, and it says which.
- **What blocks.** A finding blocks when it shows behavior that violates the
  acceptance or a current need, a risk to money, data, permissions, security or a
  policy tenet, or a missing or wrong check for the acceptance. Check style,
  harnesses, evidence format and wording are observations unless they hide such a
  failure.
- **Pre-existing failures.** A check that fails the same way on the base revision is
  not this work's blocker. Record it with an owner (an open change or task) and
  continue.
- **Setup failures.** A check that fails before it exercises the work, because of its
  setup, environment or its own tooling, is not a finding against the work and uses
  up no correction. Fix the setup and run the check again.
- **Rule contradictions.** A blocker that only a change to a rule can resolve goes to
  the human at once, as a decision with its options (Ask through cases in `ow-plan`),
  without a correction first.
- **Bounded correction.** After two blocked re-reviews of one task, stop correcting
  it. Split or re-plan it (Reconcile the plan in `ow-plan`), or present the recurring
  finding to the human as a blocker.

## Safe to forget

Before passing, every material requirement or decision this change introduced has
a retained home and evidence, so nobody needs the change or conversation later.
Group related rules and reuse task evidence; this is a short assessment, not a
per-function matrix.

- `implemented`: behavior in product files, with independently expected checks or
  a repeatable manual procedure.
- `retained`: intent or rationale in a need or ordinary doc/data.
- `deferred`: approved unfinished detail in another open change or domain data,
  with its limits explicit. A destination change lists it in delivers now, and
  successors relying on it come after that change. Deferral cannot drop a
  promised result.
- `superseded`: the replacement intent and the actual human decision.
- `unresolved`: anything missing; the review stays blocked.

Read both directions: requirements → code and checks, and consequential code
choices → the intent that justifies them. Copies of a rule the change added to
needs, READMEs or other changes become links (One home per fact in `ow-core`).
Could a maintainer find, explain, verify and safely change this behavior with only
the repository? The CLI checks that
destinations exist and are fresh, not that they say the right thing. In submodule
projects, inspect component diffs too.
