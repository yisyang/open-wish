# OpenWish workflows

Humans ask. AI identifies needs, aligns design and engineering, implements, and
reviews. Humans review the results.

OpenWish (OW) uses **Needs → Changes → Tasks**. Needs preserve durable intent;
changes hold a bounded improvement's working design and verification plan; tasks
organize its execution. Code and tests carry the implemented solution after the
accepted change is disposed.

This guide covers:

- [Greenfield onboarding](#greenfield-onboarding): establish intent and choose a
  first useful slice for a new product.
- [Brownfield onboarding](#brownfield-onboarding): recover intent and assess the
  architecture of an existing product.
- [Planning large work](#planning-large-work): turn broad asks into reviewable increments.
- [The change workflow](#the-change-workflow): take an ask through proportionate
  planning, implementation, verification, review, and disposal.

The diagrams show activities and decisions, not mandatory approval gates between
skills. A clear instruction to implement authorizes that scope. Plan-only requests
stop before implementation; material intent or scope decisions need human input.

## Starting onboarding

Adoption is explicit. Ask the agent to adopt OW for the product, or initialize it
in the product repository and invoke onboarding. The default is one product/domain
per repository, including a monorepo.

```sh
ow init
# Or select the harness explicitly:
ow init --harness opencode
```

`ow init` installs project support files and harness integrations. The `ow-onboard`
skill performs the assessment and proposes needs. OpenCode and Claude Code expose
it as `/onboard`; Codex uses `$ow-onboard`. See the
[harness table](../README.md#harness-invocation) for other invocation details.

Onboarding establishes a useful starting point. Product implementation or
refactoring proceeds when that work is also requested. Create changes/tasks only
when planning, substantive implementation, or verification is requested.

## Greenfield onboarding

Use this path when the product has little or no implementation. Start with the
human's desired outcomes and constraints, then learn about architecture by
delivering a small representative end-to-end slice.

```mermaid
flowchart TD
    A["Human requests OW adoption for a new product"] --> B["Initialize OW and inspect available context"]
    B --> C["Identify actors, valuable outcomes, acceptance, and constraints"]
    C --> D["Resolve material questions and confirm inferred intent"]
    D --> E["Record a small set of current needs"]
    E --> F["Propose the first representative end-to-end slice"]
    F --> G{"Planning or implementation requested?"}
    G -->|No| H["Present needs and the recommended next step"]
    G -->|Yes| I["Enter the change workflow for the requested scope"]
    I -->|After delivery| J["Use the delivered slice to inform the next ask"]
```

### Establish intent

1. **Understand the product.** Identify who needs it, what outcome matters, how
   that outcome can be observed, and which constraints genuinely limit solutions.
   Use any existing sketches, prototypes, interfaces, or repository conventions.
2. **Right-size needs.** Record independently valuable outcomes. A command, screen,
   export format, or module usually implements an outcome rather than warranting
   its own need. Separate outcomes that can be accepted or retired independently.
3. **Resolve meaningful uncertainty.** In default onboarding, confirm inferred
   intent in one useful batch. Preserve actual human decisions in the needs;
   leave inferred intent's `confirmed_at` empty until the human confirms it.

### Choose the first slice

Pick a narrow path that reaches an observable user outcome through real product
boundaries. Establish a conventional, minimal layout with clear responsibility and
data ownership. Keep decisions and transformations pure where practical and put
file, network, database, and other effects at identifiable boundaries.

For example, “finance staff reconcile monthly category totals without copying
rows” can begin with a local CSV input and a usable monthly report. That first
slice exercises input handling, aggregation, and presentation. A later request for
another output format can reuse the same need and aggregation rules.

If implementation is requested, use the [change workflow](#the-change-workflow)
to align the design, implement, verify, and review that slice. On each later ask,
reassess affected boundaries for duplicated rules, scattered responsibilities, or
effects leaking into decisions. Evolve the structure when those observations
justify it. Current needs continue to constrain every subsequent increment.

**Onboarding result:** a small set of current needs, explicit uncertainties, and a
recommended first slice. Once that slice is implemented and accepted, its useful
behavior, checks, and rationale remain in the repository.

## Brownfield onboarding

Use this path for an existing product. The goal is to establish useful durable
intent, understand the actual architecture, and identify whether targeted
improvements would earn their cost.

```mermaid
flowchart TD
    A["Human requests OW adoption for an existing product"] --> B["Initialize OW and inspect product context"]
    B --> C["Trace representative behavior through code, tests, and operations"]
    C --> D["Infer or reuse needs and identify verification gaps"]
    D --> E["Assess architecture using concrete observations"]
    E --> F{"Does refactoring earn its cost?"}
    F -->|No| G["Explain why the existing structure is worth retaining"]
    F -->|Yes| H["Propose bounded steps, baseline checks, risks, and rollback"]
    G --> I["Resolve inferred intent and any proposed scope with the human"]
    H --> I
    I --> J["Record current needs and present the assessment"]
    J --> K{"Further work requested?"}
    K -->|No| L["Finish onboarding with gaps and next steps visible"]
    K -->|Yes| M["Enter the change workflow for authorized scope"]
```

### Recover intent from evidence

Inspect product descriptions, public interfaces, representative user paths,
source, tests, deployment configuration, and operational constraints. Follow a
behavior through its dependencies rather than assessing architecture from the
file tree alone.

Existing code demonstrates behavior; it does not establish confirmed intent or
prove that the desired outcome works. Distinguish inspected behavior, checks
actually run, assumptions, and unverified observations. Reuse meaningful existing
outcome checks and identify consequential gaps without enshrining known bugs as
requirements.

Propose a small set of needs and label inference. On repeated onboarding, compare
actor, outcome, acceptance, and constraints with existing needs and reuse their
IDs. Consolidate duplicates or split independent outcomes while preserving intent
and reconciling references. Store useful, reasoned `requires` or `constrains`
relationships on needs; all current needs remain relevant even without links.

### Assess architecture and propose useful work

Apply the [shared architecture rubric](../src/openwish/assets/skills/ow-align/SKILL.md#architecture-rubric):
can behavior be found, do rules have clear owners, are dependencies and data
ownership explicit, can decisions run independently of effects, do tests check
outcomes, and does complexity serve a demonstrated need?

Report each consequential finding as **observation → consequence → recommendation**,
with code/test references. Compare retaining the current structure with the
smallest useful improvement. A satisfactory architecture is a valid result.

A useful refactor proposal explains:

- The affected scope and behavior or constraints to preserve.
- Existing baseline checks and small additions needed for meaningful gaps.
- Incremental steps and the responsibility, dependency, or effect boundaries they improve.
- Expected benefit, cost, risk, and how each step will be verified or rolled back.

Obtain human approval for additional refactoring scope before product edits.
Combine this decision with inferred-intent confirmation when useful. Onboarding
or delegated intent inference alone does not authorize a rewrite. If the human
defers the proposal, retain the existing structure and make the decision visible.

**Onboarding result:** current needs, a code-grounded assessment, useful operational
knowledge, and visible gaps or proposals. Keep the assessment in conversation or
an appropriate disposable change. Preserve selected operational facts and
otherwise unrecoverable rationale in ordinary repository docs or nearby comments.
A requested verification-only change may have no implementation tasks, but still
needs actual checks and review.

## Planning large work

A need describes durable value; a change describes an independently reviewable
improvement. A modernization may justify dozens of needs and many changes. Calling
the whole first release a "pilot" does not make it one manageable change.

Use [Right-size delivery](../src/openwish/assets/skills/ow-propose/SKILL.md#right-size-delivery)
before making tasks. Ask what concrete result can be accepted and retained if later
work is postponed. Split separately acceptable improvements; combine work that needs
joint acceptance. A shared database or sequential dependency does not imply a single
change. Many need references can still be appropriate for one narrow improvement.

For each candidate, identify:

| Boundary | Question |
| --- | --- |
| Delivers now | Which observable results does this increment contribute to its needs? |
| Preserves | Which existing behavior and applicable constraints must hold? |
| Defers | Which remaining outcomes belong to later work? |
| Prerequisites | Which delivered capabilities must be checked before execution? |
| Exit evidence | What would let someone accept this result independently? |

For a requested resumable plan, retain later candidates as concise ordinary open
changes. Detail tasks for the next executable increments; later task lists can
remain empty with an explicit explanation that planning is incomplete. On selection,
inspect delivered code/tests, resolve relevant uncertainty, and prepare concrete tasks.
Assessment-only sequences can stay in conversation. No parent implementation change,
permanent roadmap tier, or cross-change task graph is necessary.

For example, an online economy could progress through reproducible player access,
an isolated starter, one durable production recipe, and a first sale. Each increment
includes the interface, persistence and checks needed to demonstrate it. Regional
freight and native clients follow as separately scoped work. A task called "implement
all production, commerce, logistics and UI" would conceal most of that delivery plan.

Use enough tasks to expose meaningful completion and blocking boundaries. Keep
coherent implementation and focused checks together; do not optimize for a short
list or create a task per file. Map every promised result to work or existing evidence.
Integrate representative behavior early instead of postponing all integration.

When requirements grow or work resumes, reconcile decisions, scope, task state and
dependencies before trusting `ow ready`. A resolved policy task needs actual evidence
and any remaining application work must stay visible. If the change has grown beyond
one acceptance boundary, move unfinished obligations into specific retained changes,
repair local IDs/dependencies, preserve useful evidence, and refresh pending review.
Decomposition within authorized scope needs no new permission; material changes do.
New changes retain normal review unless explicitly delegated.

Before disposing an increment, ensure successors describe prerequisites in terms of
delivered code/interfaces/checks. Deferred obligations must not disappear with the
earlier change. An empty future task list is not completion; final review checks the
delivered scope and exit evidence, not only task status. Considering all current needs
does not mean every future capability must ship in every increment.

## The change workflow

This workflow applies to the first greenfield slice, approved brownfield
improvements, and later product asks. Start by reading current intent and the
affected code/tests. Reuse an existing need when the ask introduces another
mechanism for the same outcome; revise or add needs when intent genuinely changes.

### Choose the proportionate path

**Routine work** is clear, localized, reversible, and within existing intent:
inspect → implement → verify → report. It needs no change file, new need, or final
acceptance ceremony. Honor plan-only requests here too. Work already tracked in an
active change must be reconciled before moving it, including unresolved manual checks.

**Structured work** is substantive, involves consequential choices, or needs
resumable coordination. Scope one or more reviewable changes referencing motivating
needs, then follow this flow for each selected increment:

```mermaid
flowchart TD
    A["Human asks for an improvement"] --> B["Propose: reuse or revise needs and scope a change"]
    B --> C["Align and plan: working design, verification, and local tasks"]
    C --> D{"Implementation authorized and requested now?"}
    D -->|No| E["Present the plan or request the missing decision"]
    D -->|Yes| F["Implement ready tasks and verify outcomes"]
    F --> G["Preserve lasting knowledge and review all current needs"]
    G --> H{"Tasks complete and review fresh and passing?"}
    H -->|No| I["Remediate, continue independent work, or obtain missing input"]
    I --> F
    H -->|Yes| J{"Acceptance explicitly delegated for this change?"}
    J -->|Yes| K["Close with fast-forward provenance"]
    J -->|No| L["Present results for human review"]
    L --> M{"Human accepts?"}
    M -->|Revisions requested| F
    M -->|Yes| N["Close with human acceptance provenance"]
    K --> O["Consolidate and dispose the closed change, tasks, and review"]
    N --> O
    O --> P["Current needs, useful code, tests, and rationale remain"]
```

While awaiting a human decision or manual observation, retain the work and report
the blocker. The loop represents progress when work or input is available. If a
revision materially changes intent or scope, return to alignment and the relevant
human decision before implementing it.

### 1. Propose, align, and plan

Use `ow-propose`, `ow-align`, and `ow-plan` to prepare needs, design, and tasks
together. A change holds its purpose, delivery scope, approach, and exit evidence.
Tasks have concrete acceptance; optional prerequisites form an acyclic graph within
that change. A small change may have one task. Verification-only work or future candidates
awaiting detailed planning may have none; actual completion still needs direct evidence.

Load all current needs with `ow context`; inspect affected interfaces, consumers,
and tests. Resolve genuine intent conflicts without silently weakening constraints.
`ow graph` can focus investigation on established relationships, but unlinked
current needs still constrain the result.

Choose the smallest set of fast, independent checks protecting affected outcomes
and consequential failures. Reuse useful checks before adding tests. Check exact
details when they are real contracts; avoid freezing incidental wording, layout,
or private call order. Honor explicit coverage targets and keep routine checks
under five minutes, identifying necessary slower checks.

A clear implementation request supplies authority for its scope. Technical plan
repairs within that scope need no repeated permission. If only planning was
requested, present the prepared change and stop.

### 2. Implement and verify

Use `ow-implement` and `ow ready C-001` to select work subject to local
prerequisites. Readiness describes scheduling, not permission. Implement the
smallest coherent solution, preserving current needs and useful existing structure.

Verify before marking a task done and record concise direct evidence. Retain
completed tasks through integration review. Continue independent tasks around
blocked or manual work; report indispensable human input with its purpose. Update
the working approach as the implementation teaches you more.

### 3. Review and accept

Use `ow-review` to assess actual outcomes and the diff against **all current
needs**, including delivered outcomes. Check affected behavior and explain
unaffected constraints briefly. Before final review, put lasting behavior in code,
regression checks in tests, updated intent in needs, and useful rationale nearby.

Run the relevant checks and `ow check`, then record the latest result with
`ow record-review`. Cover every `review_needs` ID from `ow context C-001`.
Unresolved findings require a blocked review; passing requires all tasks done.
`ow check` validates structure and budgets; it does not establish user benefit.

Present **need → outcome → evidence**, with remaining limitations. In default
mode, retain the change and tasks until the human actually accepts the results.
If needs, approach, task evidence, policy/configuration, or repository content
changes while acceptance is pending, refresh verification and review before closure.

**Explicit fast-forward** delegates acceptance for the selected change. It retains
the same implementation, verification, and AI review obligations, and closes with
delegation provenance. It does not fabricate observations or human confirmation,
override plan-only scope, or apply to unrelated future changes. When onboarding
under explicit fast-forward, inferred intent remains unconfirmed; proposed
additional refactoring still needs scope authorization.

### 4. Close and dispose

After acceptance, close with the correct provenance and use `ow-consolidate` to
preserve useful knowledge and clean the closed change:

| Command | When to use it |
| --- | --- |
| `ow summary C-001` | Inspect the outcome, evidence, and review freshness |
| `ow close C-001 --by human` | After actual human acceptance and a fresh passing review |
| `ow close C-001 --by fast-forward` | After a fresh passing review under explicit change-scoped delegation |
| `ow clean C-001` | Dispose the closed change after useful knowledge is preserved |

`ow clean` removes the known change, task, and review files together after
preflight. Unknown files cause refusal and remain available for deliberate
handling. Report any reason for deferring disposal. Use `ow status` to find
cleanup candidates, results awaiting acceptance, blocked/manual work, and retired
needs.

## What survives each completed change

| Knowledge | Durable home |
| --- | --- |
| Actors, outcomes, acceptance, and constraints | Current needs |
| Implemented behavior and interfaces | Source, types, and schemas |
| Repeatable outcome and regression checks | Tests and useful manual procedures |
| Essential rationale and operational facts | Nearby comments or ordinary repository docs |

Needs remain current after delivery and can serve later changes. Retirement,
merging, splitting, or removal is an intent/retention decision that preserves
meaning and reconciles references. New changes default to human review unless
explicitly delegated again.

Retained tests enable fresh verification. Temporary probes and execution results
can disappear after useful findings are preserved. Keep historical proof as
product data when a genuine need requires it; OW requires no execution archive or
permanent satisfaction ledger. Completion does not require an automatic commit.

For details, see the [product requirements](product.md),
[framework design](design.md), [workflow policy](../src/openwish/assets/policy.md),
and [artifact reference](../src/openwish/assets/artifacts.md).
