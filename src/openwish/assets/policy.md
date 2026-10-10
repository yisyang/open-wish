# OpenWish policy

OpenWish (OW) practices Need-Driven Development (NDD). Its durable unit is a
need. Humans express asks in conversation; OW creates, revises, or reopens needs.
Do not persist asks, ask summaries, request logs, or separate change records.
Default scope is one product/domain in one repository, including a monorepo.

OW is opt-in. An installed skill, source tree, or mention of OpenWish is not a
request to run its workflow. Respect instructions to work directly without OW.
Do not initialize a repository merely because a software change was requested.

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
- For structured work, reopen an existing need when it requires further implementation.
  Preserve its ID. Create a new need only for a distinct durable outcome.
- Compare actor, outcome, and acceptance, not titles or implementation surfaces.
  An alias, another platform, a bug fix, or a different mechanism usually belongs
  to an existing outcome. Put solution details in specs, not new needs. Before
  creating a need, explain what independently valuable outcome existing needs
  cannot cover without conflating different goals. Shared spec links alone are
  not evidence of duplicate needs.
- `confirmed_at` records human confirmation of intent; `verified_at` records the
  latest accepted implementation check. Reading a file does not advance either.
- Existing behavior is evidence of what exists, not proof of what humans want.
  Passing tests establish delivery evidence, not automatically real-world benefit.

## Human communication

Ask only questions whose answers can change the work. An unambiguous instruction
is already authority for its stated scope; do not ask the human to repeat it as
a confirmation. Keep process instructions internal unless asked. Respect requests
to discuss, propose, or plan only; those do not authorize implementation.

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

Structured final updates lead with **need → spec → outcome**, followed by direct verification
and any remaining blocker. Read the spec design's need references; do not report
only epic/task IDs or assume that humans remember why a task matters. For example:

> N-001 — Local monthly insights, through S-001 — Trend analysis: monthly trends
> now compute locally. Regression checks passed; financial records stay on-device.

## Workflow and authority

Scale the process to the decision, not the number of phases:

- **Routine path (default for small, clear changes):** inspect relevant current
  needs and code, implement, verify, and report. Examples include an exact CLI
  alias, a focused bug fix, documentation, and small refactors that preserve intent.
  Use this path when the change is localized, reversible, and within clear intent,
  with no unresolved product trade-off or consequential compatibility, data,
  security, or migration decision. No new needs, revision/reopen, epics, gate
  receipts, or final acceptance prompt are required. Update an existing spec only
  when its contract/design would otherwise become inaccurate. Do not advance need
  lifecycle or confirmation/verification dates as a side effect.
  Work already tracked in an active structured plan stays in that plan; do not
  relabel it routine to bypass missing authority or unfinished manual checks.
- **Structured path:** use for a new durable outcome, changed constraints,
  consequential trade-offs, or substantial/coordinated work. Propose, Align, and
  Plan prepare one coherent scope. Clarify material ambiguity early; otherwise
  proceed through preparation without stage-by-stage confirmation. Obtain at most
  one combined scope/design/implementation decision if the conversation has not
  already authorized that scope. A clear instruction to implement can supply this
  authority when the prepared solution stays within it; a speculative suggestion
  or plan-only request cannot. Record it with `ow authorize N-001 ... --by human`.
  Implement, verify, and remediate continuously. Ask once for final acceptance
  after available work is complete, unless explicitly fast-forwarded.

Preparation phases are quality checks, not separate permission boundaries.
The lower-level `ow gate` commands remain for deliberate staged collaboration.
Record only actual human authority, not an agent's own assessment. Technical
plan repairs and artifact relinking within the authorized scope need refreshed
receipts, not renewed human permission. Material changes to outcomes, constraints,
or consequential trade-offs need a new decision. The CLI detects changed inputs;
the agent judges whether the existing conversation authority still covers them.

An explicit `/fast-forward` enables that mode on the selected needs' current
implementation revisions. For structured work, follow all phases and checks,
using `ow authorize ... --by fast-forward` and final `ow gate review ... --by
fast-forward` without approval or confirmation prompts, including final
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
- Epics reference specs; tasks belong to epics. An epic's optional `needs` array
  selects the outcomes this increment implements from its spec designs' need
  references. Other linked needs remain regression constraints, not additional
  authorization requirements. Legacy epics without this field select all linked
  needs. Do not split specs or invent needs just to bypass an authority blocker.
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
