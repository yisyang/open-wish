# OpenWish policy

OpenWish (OW) practices Need-Driven Development (NDD). Its durable unit is a
need. Humans express asks in conversation; OW creates, revises, or reopens needs.
Do not persist asks, ask summaries, request logs, or separate change records.
Default scope is one product/domain in one repository, including a monorepo.

## Needs and current truth

- Capture actor, desired outcome, pain reduced/gain delivered, and observable
  acceptance. Distinguish suggested solutions from genuine constraints.
- Currency is `current | retired`. Implementation is
  `open | in-progress | review | approved`. These dimensions are independent.
- An approved implementation does not retire its need. Load **all current needs**,
  including approved ones, with `ow context`. Retrieve relevant retired needs
  when interpreting history. Never silently retire or weaken a need.
- Match existing intent before creating a need. If the outcome is already met,
  explain that; do not invent work or create a duplicate need to represent an ask.
- Reopen an existing need when its outcome requires further implementation.
  Preserve its ID. Create a new need only for a distinct durable outcome.
- `confirmed_at` records human confirmation of intent; `verified_at` records the
  latest accepted implementation check. Reading a file does not advance either.
- Existing behavior is evidence of what exists, not proof of what humans want.
  Passing tests establish delivery evidence, not automatically real-world benefit.

## Human communication

Show only the decision relevant to the current stage. In Propose, confirm the
need interpretation without announcing later approval gates or asking about Plan.
Keep process instructions internal unless the human asks how the workflow works.

For every clarification or confirmation:

1. Number questions `1.`, `2.`, `3.` and state the relevant need IDs and conflict.
2. Offer the best two or three meaningful choices labeled `A.`, `B.`, `C.`.
   In documentation, indent these choice lines by two spaces.
3. Put `(Recommended)` **before the preferred choice text**, after its letter.
4. Add a concise effect clause when it helps explain what will happen to needs
   or the product. Do not invent an option just to fill three slots.
5. Prefer preserving existing intent when it already delivers the desired outcome.
   Recommendations follow the evidence, rather than automatically rejecting asks.

Example when N-001 already provides local monthly trends:

> 1. N-001 already provides monthly trends and requires data to remain local.
> Uploading transactions conflicts with that requirement. What should I do?
>   A. (Recommended) Keep N-001 as-is. No new need or product modification.
>   B. Add third-party upload while keeping trends local. Revise N-001 to allow
>   uploads only to approved third-party domains.
>   C. Add third-party upload and trend computation with local viewing. Revise
>   N-001's local-only constraint for approved third-party domains.

Final updates lead with **need → spec → outcome**, followed by direct verification
and any remaining blocker. Read the spec design's need references; do not report
only epic/task IDs or assume that humans remember why a task matters. For example:

> N-001 — Local monthly insights, through S-001 — Trend analysis: monthly trends
> now compute locally. Regression checks passed; financial records stay on-device.

## Workflow and authority

1. Propose: confirm the need interpretation; automatically enter Align afterward.
2. Align: reconcile current needs, code, contracts, and designs; get design approval.
3. Plan: inspect code, update epics/tasks, and obtain implementation authority.
4. Implement: execute ready work, verify, repair, and continue independent work.
5. Review: AI reviews outcomes; humans explicitly accept final results by default.

Record decisions against need IDs, e.g. `ow gate needs N-001 N-002 --by human`,
only after the human actually made that decision for the current definitions.
The CLI records conversation authority; it does not authenticate the speaker.

An explicit `/fast-forward` enables that mode on the selected needs' current
implementation revisions. Follow all phases and checks, recording gates with
`--by fast-forward` without approval or confirmation prompts, including final
acceptance. Never invent human confirmation dates, test results, or manual actions.
Reopening a need resets authority to default unless fast-forward is explicitly
requested again. Mode applies to need revisions, not subsequent unrelated asks.

Ask only for genuinely blocking ambiguity, conflicting needs, missing access, or
manual verification. Use the numbered choices above. Continue independent ready
work before presenting human blockers; pending acceptance of one result is not
a reason to stop other authorized work. Do not ask to run AI review.

## Design and execution

- Classify conflicts: need/need, need/implementation, spec/spec, or task/design.
  Show concrete scenarios and adjacent needs. Compatible needs require adapting
  the solution rather than silently discarding a constraint.
- Spec **designs** own the authoritative need references. Specs may address API
  entities, UI modules, or cross-cutting capabilities. Need/spec links are many-to-many.
  Keep `parent` containment separate from prerequisite `depends_on` links.
- Epics reference specs; tasks belong to epics. Work is derived through these
  links from selected needs, without a separate persistent work container.
- Tasks have explicit prerequisites and increasing `(group, order)` pairs across
  the work for a need. No lower ordinal depends on a higher one. Execute the
  earliest authorized ready task; independent later work can pass a manual blocker.
- Preserve approved intent when resolving technical inconsistencies. Material
  intent/design revisions return to the relevant phase; stale receipts cannot
  authorize newer work. Task progress itself does not invalidate a plan.
- Prefer the smallest coherent implementation, security, reliability,
  maintainability, functional cores, and established dependencies.
- Use meaningful verification with a routine feedback loop under five minutes.
  Identify necessary slower checks explicitly. Missing observations are not passes.
- Keep direct results and useful pointers, not evidence chains or repeated reviews
  of reviews. Review the implementation and adjacent needs, not just checkboxes.

## Bounds and consolidation

- Every OW knowledge/planning artifact is **under 500 lines**, including JSON.
- All current needs together stay under 500 lines and the configured estimated
  token budget (default 6,000). `ow context` derives a complete view without truncation.
- Code has an **under 500 LOC soft target** and **under 1000 LOC hard maximum**.
  Source data formats are exempt; low-complexity source exceptions need exact
  paths and reasons. These exemptions never bypass OW artifact limits.
- LOC uses nonblank physical lines; estimated tokens use UTF-8 bytes/3. They are
  budgeting proxies, not proofs of low complexity or model-specific token counts.
- Overwrite latest summaries, compact before 400 lines, and bound retained epics
  (default eight). Git stores history. Do not build append-only journals or archives.
- Promote current contracts, environment profiles, and secret references before
  removing completed execution detail. Retain unresolved limitations and checks.
- Tighten wording without losing acceptance conditions. Retiring or semantically
  merging needs requires intent confirmation under the selected workflow.

Read `openwish/artifacts.md` when editing artifacts. Run `ow check` before gates
or final review. Structural validation complements semantic alignment and review.
