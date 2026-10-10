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
coordination use a change. Keep work already tracked in a change there, including
unresolved manual checks. A small change may have one task; a verification-only
change may have none.

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

Changes reference needs directly, many-to-many. All current needs are regression
constraints, including those outside a change's motivating scope. Distinguish
incompatible intent from an implementation that does not yet satisfy compatible
needs; adapt the implementation when possible.

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

1. Prepare needs, approach, and tasks together. Continue to implementation when
   authorized; a plan-only request stops at the prepared change.
2. Run `ow ready C-001` and work in listed order subject to local prerequisites.
   Tasks use `open | in-progress | blocked | done`. Optional dependencies stay
   within the change so completed changes can be removed independently. Coordinate
   separate changes through delivered code/interfaces; combine tightly coupled work.
3. Verify each task before marking it done. Record concise direct evidence.
   Retain completed tasks until change closure. Continue independent work around
   manual blockers, then present indispensable human input with its purpose.
4. Review the actual diff and outcomes against all current needs. Assess which
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

## Bounds

- Each OW artifact is under 500 lines. Compact near 400 lines.
- All current needs together stay under 500 lines and the configured estimated
  token budget (default 6,000). Include their complete content without truncation.
- Source has an under-500 nonblank LOC soft target and under-1000 hard maximum.
  Exact-path, justified data/low-complexity exceptions never exempt OW artifacts.
- Token estimation uses UTF-8 bytes/3; these limits are proxies for manageable
  context, not substitutes for thoughtful design.
- Replace latest working summaries rather than accumulating journals. Compact
  wording without silently losing acceptance, constraints, or independent outcomes.

Read `openwish/artifacts.md` for schema 3 and command examples.
