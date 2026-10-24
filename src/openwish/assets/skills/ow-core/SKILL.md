---
name: ow-core
description: OpenWish's own policy, shared by every ow-* skill: where knowledge lives, authority, acceptance and which skill owns each rule. Load it first, with the project's openwish/policy.md. Not a workflow by itself.
---

# Core

Humans ask. AI identifies needs, aligns design and engineering, implements, and
reviews. Humans review the results.

**Durable intent. Disposable plans. Code and tests carry the solution.**

- **Needs** (`openwish/needs/N-001.md`) record who needs what outcome, how to
  observe it, and genuine constraints. They stay binding after delivery.
- **Changes** (`openwish/changes/C-001/`) hold one reviewable increment's purpose,
  scope, working design, verification plan, tasks and latest review. They are
  deleted after acceptance once their useful knowledge lives elsewhere.
- **Code, tests and ordinary docs** carry what was built, how it is checked, and
  rationale that the code cannot express.

Default to one product/domain per repository, including a monorepo. This skill is
OW's and upgrades replace it. Also read the project's `openwish/policy.md`, which OW
never edits: its rules add to these, and one that departs from an OW rule names the
rule it overrides.

## Adoption and proportion

OW is opt-in. Installed skills do not mandate using it; requests to work without
OW win. Initialize only when asked to adopt OW.

Every product change recovers current intent (`ow context`), reconciles the ask
with it, clarifies only what could change the work, designs with the Architecture
rubric, verifies and reviews, in proportion to the ask: a typo needs a glance.
Direct or managed delivery changes what is recorded, not the care taken.

**Direct delivery** fits one coherent result finished and verified in this session,
with no material open decision, nothing deferred, and no active change covering
it. It records no change, tasks or acceptance step, though it may create or revise
a need. When the human asks for a plan and says not to implement yet, the result is
finished in a later session, so delivery is managed: record the plan as a change with
its tasks. Describing the steps of work you were asked to do does not make it plan-only.

**Managed delivery** uses changes when work needs several acceptable increments,
resumption across sessions, deferred obligations, sequencing, manual blockers or
delayed acceptance: propose → align → plan → implement → review → consolidate.
Promote direct work to a change as soon as one of these appears (`ow-plan`).

A skill entered before this intake (needs reconciled, delivery chosen) applies
`ow-propose` steps 1–3 and 5 first. Only non-product edits, such as spelling or
formatting, skip it.

## Where knowledge lives

| Knowledge | Home |
| --- | --- |
| Actors, outcomes, acceptance, structural rules, constraints | Current needs |
| Undecided product questions and proposed criteria | The need's `open` list |
| Engineering unknowns: precision, sizing, platform choices, measured limits | The change that depends on them, as an investigation or stated uncertainty; the answer goes to code or the engineering requirements doc |
| Detailed rules, tunable values and their worked examples | A referenced rule doc or domain data |
| Implemented behavior and interfaces | Source, types, schemas |
| Repeatable checks of intent | Tests and documented manual procedures |
| Engineering requirements: how the product is built, checked and released | An ordinary doc linked from the project policy |
| Module and area responsibilities | A short header per module; a README at major boundaries |
| Rationale, operations, environments, test accounts | Nearby comments or ordinary docs |
| Approved but unfinished detail | Another open change or retained domain data |
| Working design, tasks, review | The change, until disposal |
| Investigation evidence: measurements, probe results, rejected options | The change until disposal, then a dated evidence doc linked from what it supports; rule docs keep only the decisions and rules it settled |
| Run logs, resource names, ports, session IDs, temporary paths | The conversation or files outside the repository; records may point to logs by path |

**One home per fact.** Write each rule, value or decision once and link to it
elsewhere. A rule several needs depend on lives in the need whose outcome it
serves; the others cite its ID. A large table or roster lives in domain data; a doc
may show a view generated from it, which a check keeps current and which changes
only through the data. Commit what durable knowledge depends on, or document how to
obtain it. Reference secrets by location, never by value. Git holds history, so state
current decisions without supersession notes.

Needs hold no execution status: closing a change neither retires a need nor proves
it satisfied. `confirmed_at` records actual human confirmation of every acceptance
criterion; code shows behavior, not confirmed intent. Confirmation is provenance,
never a gate on planning or implementation. Recording a human's explicit
instruction faithfully needs no second approval round.

## Authority and communication

- A clear instruction to implement authorizes that scope. Plan-only and
  discussion-only requests stop before implementation.
- Investigations are planning and need no implementation authority: reading,
  worked examples, and throwaway probes kept outside product files. Experiments
  that edit product files, use shared environments or have outward effects need
  the same authority as implementation.
- Technical repairs within authorized intent need no new permission. Material
  intent or scope changes need a real human decision.
- `ow context` and `ow ready` report scheduling, not permission. Loading a skill
  grants nothing.
- An open question or unsettled value blocks only the work whose result depends
  on it; continue the rest.
- **Commit progressively.** Settle uncertainty before the commitment it could
  disrupt, not before all work: investigate early what would be costly to learn
  late, hold hard-to-reverse commitments for their decisions, and let reversible
  choices proceed on a recorded assumption (Commit progressively in `ow-plan`).
- Ask only questions that can materially change the work. Use numbered questions
  with two or three A/B/C options, put `(Recommended)` before the preferred option,
  and state each option's effect.
- Report as **need → outcome → evidence**, then limitations. Separate what you
  observed from assumptions and checks you did not run. Use the human's vocabulary:
  explain or drop internal terms, and answer their direct questions in the final
  report, not only in interim messages.

**Acceptance.** By default a human reviews managed results, then the agent runs
`ow close C-001 --by human`. Explicit fast-forward delegates acceptance for one
named change only (`--fast-forward` or `ow mode fast-forward C-001`, then `--by
fast-forward`). It never supplies missing manual observations, access, passing
checks or confirmation of inferred needs, and new changes default to human review.
A delegated closure keeps its records until the human has seen the result (Dispose
closed changes in `ow-consolidate`). Successors named with `after` may start once
their predecessors pass review (or are accepted, if `successors_wait_for` is
`acceptance`); acceptance follows the sequence.

## Evidence and context

- **Evidence is a short record.** Completion and review evidence names the command or
  procedure, the revision it ran on, its result and where its log is. A run recorded
  at the reviewed revision is evidence for the reviewer too; rerun only what is
  missing, stale or in doubt. Use the project's own check commands. Build
  provenance machinery (hash manifests, archived copies of the work, custom wrappers
  around checks) only when a result's integrity is genuinely in question, and keep
  logs a record cites where they survive a restart.
- **Keep context small.** Every step rereads the session's whole context, so a session
  past about 150k tokens works several times slower than a fresh one. Read only what
  the step needs: batch independent reads and searches, read a log's failing excerpt
  rather than all of it, and leave large binary files unread unless the work is about
  them. When a session grows that large, hand off to a fresh one with a short summary
  of state, evidence and next step.

## Skill map

Each rule has one owner. Load a skill when its step begins, not all at once, and
read the owning section when a step calls for it.

| Guidance | Owner |
| --- | --- |
| Right-size intent, Rule status, Right-size delivery, relationships | `ow-propose` |
| Architecture rubric, Future constraints | `ow-align` |
| Task sizing, Commit progressively, Discover ahead of delivery, Plan a candidate, Promote direct work, Reconcile the plan, Strategic verification | `ow-plan` |
| Need assessment, Safe to forget, Blocking findings | `ow-review` |
| Disposal, compaction, size targets | `ow-consolidate` |
| Delegated acceptance | `ow-fast-forward` |
| Adoption for an existing or new product | `ow-onboard` |
| Readiness of a sequence: horizon, pre-mortem, discovery queue | `ow-assess` |
| Coordinated rounds: round record, workers, integration, close-out | `ow-coordinate` |

`artifacts.md` beside this skill documents file formats and commands; read it when
writing or repairing a record.
