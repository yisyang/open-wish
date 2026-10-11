---
name: ow-plan
description: Prepare or repair tasks and proportionate verification inside a disposable OW change after design alignment. Use for substantive or resumable work; routine changes need no records. Respect plan-only requests and OW opt-outs.
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
   Apply Strategic verification below: reuse useful checks and fill genuine gaps.
   Keep routine verification under five minutes; identify necessary slower checks.
   For an approved refactor, plan small behavior-preserving steps with baseline
   outcome checks, clear dependency/effect boundaries, and relevant boundary checks.
   Establish missing checks before relying on them; do not enshrine known bugs as intent.
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
