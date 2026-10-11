---
name: ow-plan
description: Decompose substantive OW work into reviewable changes, executable tasks, and proportionate verification. Reconcile growing scope or stale plans before execution. Routine changes need no records; respect plan-only requests and OW opt-outs.
---

# Plan

Read `openwish/policy.md`, `openwish/artifacts.md`, `ow context C-001`, the working
approach, and affected source/tests. Prepare only work that remains useful.

1. Apply Right-size delivery in `../ow-propose/SKILL.md`. State the change's delivers
   now, preserves, defers, and exit evidence. A broad ask may require several changes;
   prepare the next executable increments rather than compressing the whole program.
   Reconcile the plan below before relying on an existing task list.
2. Use enough tasks in `changes/C-001/tasks.json` to expose meaningful work and
   verification boundaries. Each has an ID such as `C-001/T-001`, title, status,
   and verifiable acceptance. Apply Task sizing below. Add files, kind, and
   prerequisites only when useful. Completed tasks need direct evidence.
3. Order tasks for sensible execution. Optional dependencies reference tasks in
   the same change and form a DAG; there are no global group/order pairs.
   Combine work only when it needs a joint acceptance boundary. Sequence other
   changes against delivered capabilities rather than cross-change task links;
   verify those capabilities before making dependent work executable.
4. Keep independent work executable around indispensable manual observations.
   Apply Strategic verification below: reuse useful checks and fill genuine gaps.
   Keep routine verification under five minutes; identify necessary slower checks.
   For an approved refactor, plan small behavior-preserving steps with baseline
   outcome checks, clear dependency/effect boundaries, and relevant boundary checks.
   Establish missing checks before relying on them; do not enshrine known bugs as intent.
5. Include lasting code/tests and essential rationale placement in the work so
   the result remains maintainable after the change disappears. An existing
   implementation may need verification only, with no implementation tasks.
6. Check the scope-to-task coverage and reconciliation below, then run `ow check`.
   Structural success does not establish a feasible or complete plan. If asked only
   to plan, present the increments, next approach/tasks, and uncertainties, then stop.
   Otherwise use actual conversation authority for the prepared scope. Ask one
   meaningful combined decision only if authority or a consequential choice is
   missing; use numbered A/B/C choices with `(Recommended)` before preferred text.
7. Continue to `ow-implement`. There are no authorization commands or stage
   receipts to record. `ow ready` reports prerequisites, not permission. Technical
   plan repairs within authorized intent do not require another human decision.

## Task sizing

A task is a concrete unit of implementation or investigation with a result that can
be checked directly. Its acceptance describes behavior/evidence, not "implement the
subsystem and test it." An investigation ends with findings and a decision/proposal;
it does not claim the investigated feature is delivered.

- Split when completion would require unrelated evidence, substantial hidden design,
  or separately blockable work. Promote an independently acceptable deliverable to
  its own change rather than burying it in a task.
- Keep coherent implementation and its focused checks together. Do not create a
  task per file/function or require a new test for every task. A short list is not a
  goal if each item hides a project; a long list may signal an oversized change.
- Ensure every delivers-now result and consequential constraint has planned work
  or existing direct evidence, and every task serves that scope. A brief mapping in
  the change is enough when non-obvious; no separate traceability ledger is needed.
- Integrate and verify representative behavior early. Avoid a final "integrate and
  test everything" task that is the first evidence the components work together.

## Reconcile the plan

On initial planning, resumption, or changed requirements/decisions, compare the
conversation, needs, change scope, tasks/evidence, and actual repository state:

1. Resolve contradictions before trusting readiness. If a policy choice is recorded
   as resolved but its task still waits for that choice, reconcile the task and all
   affected prerequisites. Mark it done only with evidence that its full acceptance
   is met; preserve any remaining observation or application work explicitly.
2. Reassess scope using Right-size delivery. For a split, assign each unfinished
   obligation to a specific retained change/task, repair local dependencies and
   qualified IDs, and preserve useful completed evidence with the work it supports.
   Do not mark moved work done, delete manual blockers, or claim the original broad
   outcome was delivered. Update scope and refresh any pending review after edits.
3. Keep future work discoverable in its own open changes when a resumable plan is
   requested. Before disposing an earlier change, replace successor references to
   its temporary tasks/design with the delivered code, interfaces, and checks. An
   empty future task list means unplanned work, not verified completion.
4. Recompute readiness after reconciliation. Continue independent authorized work;
   ask only for genuine missing evidence, authority, or material intent/scope choices.

## Strategic verification

Choose the smallest set of fast, independent checks that protects affected needs
and consequential failure modes. Preserve stable obligations while allowing the
implementation to evolve. Test count and coverage percentage are not quality goals.

- Ask proportionately: what important behavior could break, which existing checks
  protect it, what smallest additional check closes a real gap, and what remains
  unverified? Reuse coverage before adding tests; each task need not invent a test.
- Place checks at useful boundaries: a few representative need-level outcomes,
  important decisions/invariants in the functional core, and consequential I/O or
  integration contracts. Choose only the levels that add distinct evidence.
- Derive expected results independently of implementation. A harmless refactor
  should normally leave tests passing; a meaningful violation of a need should fail.
  Complicated mocking for a simple rule may reveal a poor design boundary.
- Avoid freezing incidental wording, whitespace, layout, helper names, private call
  order, or large snapshots. Assert exact text/schema/layout when it is an actual
  public or human-specified contract, and keep that assertion narrow.
- Cover credible failures with meaningful consequences, such as data loss, wrong
  charges, or a privacy violation, even without a coverage request. Prefer a small
  representative check over speculative edge-case matrices and elaborate negative
  suites. Expand when risk, uncertainty, observed failures, or explicit requirements
  justify it. Honor requested coverage targets without treating 100% as correctness
  or exhaustive input coverage; do not invent targets when none were requested.
- Keep durable regression tests for lasting obligations. Temporary experiments and
  debugging probes can be discarded after their useful findings are preserved.
  Consolidate redundant or brittle tests only while preserving meaningful protection.
  Routine prose/presentation edits may need inspection or a focused smoke check
  rather than a new permanent test.

Record concise current results and limitations. Retained runnable tests provide
fresh verification; they need no permanent archive of each development-stage run.
