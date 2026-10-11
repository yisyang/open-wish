# OpenWish policy

Humans ask. AI identifies needs, aligns design and engineering, implements, and
reviews. Humans review the results.

Needs preserve durable intent. Changes hold temporary purpose, design, and
verification plans. Tasks organize work within a change. Dispose changes and
tasks after completion and review; code and tests carry the implemented solution.
Default to one product/domain per repository, including a monorepo.

## Adoption and proportion

OW is opt-in. Installed skills and source templates do not mandate adoption.
Respect requests to work directly without OW. Initialize only when asked to adopt it.

Clear, localized, reversible work within existing intent follows inspect →
implement → verify → report. It needs no change file, new need, or acceptance
ceremony. Substantial work, consequential choices, and work that needs resumable
coordination use reviewable changes. Reconcile tracked work before moving it between
changes, preserving unresolved manual checks and useful completed evidence. A small
change may have one task; verification-only work may have none.

## Durable needs

- Capture actor, independently valuable outcome, observable acceptance, and
  genuine constraints. Keep internal designs, algorithms, and task lists in the
  working change or implementation rather than expanding needs into specs.
- Match actor/outcome/acceptance before adding a need. A new format, command,
  platform, or mechanism often serves an existing outcome. Create a new need
  only for a separately valuable outcome; preserve stable IDs when intent evolves.
- Currency is `current | retired`. Load all current needs with `ow context` before
  alignment and review. Delivered outcomes still constrain future work. Retiring
  or weakening a need requires an actual intent decision, not implementation convenience.
- Needs have no execution lifecycle. Closing a change neither retires its needs
  nor proves their complete satisfaction. Multiple changes can serve the same need.
- `confirmed_at` records actual human confirmation of intent. Leave inference
  unconfirmed. Existing code establishes behavior, not human intent.
- Keep asks in conversation. Store interpreted durable intent and a bounded
  working improvement, rather than conversation transcripts or request journals.

### Sizing and relationships

One need expresses a coherent valuable outcome, independent of its implementation
effort. Reuse it for different mechanisms. Split a broad bundle when outcomes can
be accepted, changed, or retired independently. Merge duplicate intent without
losing acceptance or constraints. Stable IDs support continuity, not artificial
resistance to necessary splits/merges. Confirm material meaning changes.

Keep optional, sparse `relations` on needs, with `kind`, target `need`, and a
concrete `reason`. `requires` means the source outcome needs the target outcome;
`constrains` means the source limits acceptable solutions for the target. These
are semantic facts, not scheduling, shared-code links, or a complete pairwise map.
Cycles can be meaningful. `ow graph [N-001 ...] --json` derives incident links
and endpoints from the current records; nothing is stored in a second registry.
Reconcile incoming/outgoing links and retained change references on intent edits,
splits/merges, retirement, or deletion. Current links target current needs.

Use relationships to focus investigation, while considering all current needs and
possible new interactions. Reuse established facts and valid working assessments;
reconstruct code/test dependencies from the repository when relevant inputs change.
Absent links do not prove independence. Do not regenerate all pairs on every ask.

## Design and engineering

Inspect code, tests, interfaces, and repository conventions to reconstruct the
current design. Needs define expected outcomes; code defines implemented behavior;
tests check the connection. Review tests against intent so a passing suite does
not merely repeat an implementation mistake.

Keep temporary design in the change's approach: affected modules, alternatives
that matter, compatibility, effects, and how current constraints are preserved.
Use cohesive modules, explicit dependencies, functional cores, and effects at
boundaries where appropriate. Prefer the smallest coherent implementation and
established dependencies. Repository layout and public interfaces should make
responsibilities discoverable. Preserve rationale that cannot be recovered from
code in a nearby comment or ordinary repository document when useful.

Use the shared Architecture rubric in the installed `ow-align` skill: discoverable
behavior, rule ownership/change locality, explicit dependencies/data ownership,
isolated effects, independent outcome tests, justified complexity, and maintainability
after disposal. Ground findings in actual paths and consequences, not pattern names
or line counts. Prefer pure decisions/transformations with explicit inputs and
outputs; supply time, randomness, config, and external results at effect boundaries.

Greenfield work starts with a conventional, minimal structure and a representative
end-to-end slice. As asks arrive, inspect the affected boundaries for duplicated
rules, scattered responsibilities, and effects leaking into decisions. Keep useful
structure and evolve only what the evidence justifies.

Brownfield onboarding includes a proportionate architecture assessment. Explain
observed friction, consequences, and whether refactoring earns its cost. When it
does, propose bounded, incremental steps, preserved behavior, baseline checks,
risks, and verification/rollback. Seek human approval for that additional scope
before edits; onboarding alone authorizes no product rewrite. A satisfactory
architecture needs an explanation, not invented refactoring work.

Changes reference needs directly, many-to-many. All current needs are regression
constraints, including those outside a change's motivating scope. Distinguish
incompatible intent from an implementation that does not yet satisfy compatible
needs; adapt the implementation when possible.

### Reviewable delivery

Use Right-size delivery in the installed `ow-propose` skill. A change delivers a
concrete improvement that can be accepted and retained while later work is postponed.
Describe delivers now, preserves, defers, and exit evidence. Need links express
contribution, not complete satisfaction. Deferral cannot weaken applicable constraints
or silently remove agreed results. Broad asks usually need a sequence of changes.

Split separately acceptable capabilities; combine work needing joint acceptance.
Shared modules/databases or later work using earlier work do not alone require one
change. Integrate representative end-to-end behavior early. Enabling work should prove
a useful capability rather than merely construct speculative layers.

For requested resumable plans, retain later candidates as concise ordinary open
changes with scope, prerequisite capabilities, uncertainties, and exit evidence.
Detail tasks for the next executable increments; an empty future task list is
unplanned work, not completion. Verify prerequisites against delivered code/tests.
Reconcile successor references before disposal; no permanent roadmap tier is required.

Use Task sizing and Reconcile the plan in the installed `ow-plan` skill. Task count
follows meaningful completion and blocking boundaries, not a fixed quota. Do not
compress subsystems into tasks to keep a list short. Connect promised outcomes to
work or existing evidence. On new requirements or resumption, reconcile scope,
resolved decisions, blockers and dependencies; preserve unfinished work and evidence
when splitting changes. Decomposition within authorized scope needs no reauthorization.

### Strategic verification

Use the smallest set of fast, independent checks that protects affected needs and
consequential failure modes. Prefer stable outcomes, business invariants, and
boundary contracts. Ask what could meaningfully break, which existing checks
already protect it, what small additional check closes a real gap, and what remains
unverified. A task or module does not automatically require a new test.

Place representative checks at need-level outcomes, important pure decisions, and
consequential integrations where each contributes distinct evidence. Expectations
come from intent, not the implementation's own calculation. Tests should normally
survive harmless refactors while detecting meaningful need violations.

Avoid brittle assertions about incidental wording, whitespace, layout, private
helpers/call order, or broad snapshots. Exact text, schemas, or layout are worth
checking narrowly when they are actual contracts. Cover credible failures with
meaningful consequences even without a coverage request; avoid speculative input
matrices and elaborate negative suites without corresponding risk or requirements.
Expand for risk, uncertainty, observed failures, or explicit requirements. Honor
requested coverage targets; do not impose unrequested percentages or mistake 100%
coverage for correctness. Test count is not a quality target either.

The installed `ow-plan` skill owns the shared Strategic verification guidance.
Retain regression tests for lasting obligations; temporary experiments can disappear
after useful findings are preserved. Reuse or consolidate checks without losing
meaningful protection. Routine prose/presentation edits may need inspection or a
focused smoke check rather than new permanent tests. Record concise current results
and limitations; tests enable fresh evidence without a history of every stage's run.

## Authority and communication

An unambiguous instruction to implement supplies authority for that scope.
Clarify only uncertainty or conflict that can materially change the work. Respect
discussion-only and plan-only requests. Technical plan repairs within authorized
intent need no renewed permission. A consequential intent or scope change needs
a real decision. Readiness is a scheduling result, not permission to implement.
Authority lives in conversation; there are no stage gates or authorization receipts.

For meaningful choices, use numbered questions with two or three A/B/C options,
put `(Recommended)` before the preferred choice text, and briefly explain effects.
Do not restate clear instructions as confirmation questions.

Explain results as **need → outcome → evidence**, with change/task IDs only when
useful. Distinguish observed results from assumptions and unperformed checks.

Default structured work presents results for human review. Record closure with
`ow close C-001 --by human` only after actual acceptance of those results.
Explicit fast-forward delegates this final acceptance for that change alone:
use `ow new change ... --fast-forward` or `ow mode fast-forward C-001`, then
`ow close C-001 --by fast-forward`. Loading a skill or reading a file grants no
authority. New changes default to normal human review; delegation is never
inherited through shared needs. Fast-forward does not supply missing manual
observations, access, or passing checks, and does not override a plan-only request.

## Execution and review

1. Prepare needs, increment boundaries, approach, and tasks together. Continue to
   implementation when authorized; a plan-only request stops at the prepared plan.
2. Run `ow ready C-001` and work in listed order subject to local prerequisites.
   Tasks use `open | in-progress | blocked | done`. Optional dependencies stay
   within the change so completed changes can be removed independently. Coordinate
   separate changes through delivered code/interfaces; combine work needing joint
   acceptance. Reconcile stale task states and prerequisite capabilities first.
3. Verify each task before marking it done. Record concise direct evidence.
   Retain completed tasks until change closure. Continue independent work around
   manual blockers, then present indispensable human input with its purpose.
4. Review delivered scope and exit evidence as well as task completion. Assess the
   actual diff and outcomes against all current needs without claiming all future
   outcomes are implemented. Assess which
   need checks are affected and explain unaffected constraints briefly. Run
   meaningful regression checks and `ow check`; routine verification should take
   under five minutes, with necessary slower checks identified explicitly.
5. Remediate and recheck without asking permission for AI review. Record one latest
   review per change using `ow record-review`, covering all IDs listed by
   `ow context C-001` under `review_needs`. Unresolved findings use `--verdict blocked`.
6. A passing review requires completed tasks. Changes to needs, approach, task
   evidence, policy/config, or repository content make pending review stale.
   Refresh the relevant verification and review before closure. This is one result
   freshness check, not a chain of stage approvals.

## Completion and disposal

Before final review, put lasting behavior and regression checks in code/tests,
intent changes in needs, and essential rationale/environment references in ordinary
repository documentation. Preserve unresolved limitations visibly; never conceal
unfinished work by deleting a task or calling it routine.

After results are accepted, close the change and use `ow clean C-001` to remove
its change document, tasks, and review. Keep history in Git when history is useful;
do not create an OW archive, execution ledger, or need-owned review sidecar.
No automatic commit is required. Cleanup preserves unknown files and refuses
unfinished changes. If preserving knowledge requires new edits after review,
refresh the review before closing; after closure treat new implementation work
as a new change. Future maintainers should be able to work from needs and the
repository without recovering a deleted change.

Disposal is a normal completion action; report any reason for deferring it. Use
`ow status` retention groups to find closed work, pending acceptance (refresh stale
reviews first), blocked/manual work, and retired needs. Reconcile abandoned-looking
work explicitly; age or quantity never establishes completion. Retired needs may
be removed after a retention decision and reference/rationale reconciliation.

Preserve useful manual verification procedures and expectations, not every run's
output. Tests enable new evidence; they do not certify historical runs. OW retains
no permanent satisfaction claim or execution/evidence ledger. Historical evidence
is product data only when an actual need calls for it. Docs/comments retain selected
facts and non-obvious rationale, replacing obsolete guidance rather than archiving
whole changes, assessments, or reviews.

## Bounds

- Each OW artifact is under 500 lines. Compact near 400 lines.
- All current needs together stay under 500 lines and the configured estimated
  token budget (default 6,000). Include their complete content without truncation.
- Source has an under-500 nonblank LOC soft target and under-1000 hard maximum.
  Exact-path, justified data/low-complexity exceptions never exempt OW artifacts.
- Token estimation uses UTF-8 bytes/3; these limits are proxies for manageable
  context, not substitutes for thoughtful design.
- Review need granularity and duplication before budgets fail; the CLI warns at
  80% of the current-needs token budget and at 400 context lines. Outcome overlap,
  mechanism-sized needs, broad bundles, and intent drift also prompt consolidation.
- Replace latest working summaries rather than accumulating journals. Compact
  wording without silently losing acceptance, constraints, or independent outcomes.
- Per-file and current-context limits do not cap total retained files. Keep total
  working material manageable through completion/disposal and explicit reconciliation,
  never through silently deleting unfinished work or moving journals into docs.

Read `openwish/artifacts.md` for schema 3 and command examples.
