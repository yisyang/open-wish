# Changelog

Release notes for OpenWish, newest first. Update this file for every release.

## v1.0.0rc1

Release candidate for v1.0.0, with the changes listed there. Its CLI and installed
skills report `1.0.0-rc.1`, which sorts below `1.0.0`, so the final release upgrades
candidate installations. Release candidates publish only to TestPyPI.

## v1.0.0

First stable release. OW's own guidance moves out of `openwish/` into skills, so
everything under `openwish/` belongs to the project; `ow init` migrates schema 4 to 5.

### Added

- Rule status (`ow-propose`): rule docs tag each section and differing sentence
  `confirmed`, `approved-initial`, `inferred`, `engineering`, `proposed` or `open`,
  matching the distinction needs already make with `confirmed_at` and `open`.
  Assumptions made under Commit progressively and inferences from onboarding use
  these tags; only a recorded human decision makes a rule `confirmed` or
  `approved-initial`, and fast-forward never does.
- Strategic verification (`ow-plan`): a rule doc's worked examples get one retained
  check that reads the doc, runs only when its inputs change and carries no need
  IDs. Once product tests replay an example, only its cheap quote check remains.
  Assessments cite a current passing run instead of recomputing by hand.
- Direct delivery (`ow-core`): a plan-only request is never direct, since its result
  is finished in a later session; the plan is recorded as a change with its tasks.
  Evaluations showed agents sometimes planned such requests in the session only.
- One home per fact (policy): large tables live in domain data; a doc may show a
  generated view that a check keeps current. The Architecture rubric's friction is
  rule values restated by hand.

### Changed

- Ownership by location: OW owns what it installs as skills; everything under
  `openwish/` is the project's. A new `ow-core` skill carries OW's policy and the
  artifact reference, and every other skill loads it first. `openwish/policy.md` is
  now a short project starter that OW never edits; its rules add to `ow-core` and
  override one only by naming it.
- Schema 5. `ow init` migrates schema-4 projects after preflighting them: policy
  text and references OW shipped under schema 4 are recognized by digest and removed
  from `openwish/`, while project text, adapted OW text and an edited reference are
  kept and reported. The schema version is written last, so an interrupted migration
  resumes. Other commands on schema 4 ask you to run `ow init`.
- Compatibility policy: existing projects keep working across upgrades. Artifact
  format changes now require a schema bump and a migration from every earlier
  schema, applied by `ow init` after a whole-project preflight and tested from each
  earlier schema; changes that break existing projects need a major version. This
  replaces the pre-1.0 guidance that preferred breaking changes over migrations.
- Package metadata marks OpenWish as production/stable.

## v0.9.1

The `v0.9.0` tag was never published: its release check failed because the package
version had not been bumped. This release contains everything intended for 0.9.0.

### Added

- Tasks may have `kind = "investigate"`: findings and a decision or proposal,
  never delivered behavior. Investigations ignore their change's `after` gate, so a
  decision a later change depends on can be settled while earlier changes are
  built. Starting one leaves an open change open, a change holding only
  investigations is still listed as unplanned, and `ow ready` marks them
  `[investigate]`. A blocked investigation is a question awaiting a human: `ow ready`
  and `ow context` list it as `ASK` (`"ask": true` in JSON) and count investigations
  in flight. `ow context --json` reports each task's `kind` and `status`.
- The policy treats investigations as planning: reading, worked examples and
  throwaway probes outside product files need no implementation authority.
  `ow-implement` takes ready investigations from other changes within the in-flight
  limit, and `ow-consolidate` surfaces them and `ASK` batches when continuing a
  sequence.
- New `ow-assess` skill: against a declared horizon, rate intent, coverage, rule
  consistency, sequence, decisions, execution readiness and verification with
  evidence; run a pre-mortem; rank unknowns by the cost of learning late; state a
  confidence; recommend in order of leverage; and, when planning is authorized,
  record investigations and one question batch. `ow-propose` runs it before
  presenting a long sequence.

### Changed

- Progressive commitment organizes planning. The policy and `ow-plan` add **Commit
  progressively** (commitment points wait for their decisions; reversible choices
  proceed on a labeled assumption; questions through cases, in batches,
  hardest-to-reverse first; self-directed loops stop once a pass adds no evidence)
  and **Discover ahead of delivery** (unknowns across the whole sequence, ranked by
  the cost of learning late, investigated early with a small work-in-progress
  limit). `ow-plan` adds a challenge step before stopping.
- `ow-align` adds **Future constraints**: foundational designs are checked against
  already-known later needs and either preserve the constraint, resolve it first, or
  record an affordable evolution path. Its rubric asks whether dense rules run as
  pure functions that replay the rule doc's worked examples.
- `ow-propose` prerequisites state the behavior, provider and how it is verified,
  and resolve to delivered code once the provider is disposed; coverage counts
  retained checks for delivered work; a new **Pressure** check sends foundational
  changes to Future constraints. `ow-review` presents assumptions the result
  proceeded on, challenges the result with its strongest plausible failure, and
  names plan misses with their causes, proposing recurring lessons for the
  project's policy. `ow-plan` states that an assumption only stands in for an
  undecided product rule as a labeled placeholder and never decides it.
- `ow-propose`'s Clarify step restates the policy's question format: one numbered
  A/B/C set with `(Recommended)` before the preferred option.
- Evaluations 31–35 (dry runs) cover future constraints on a foundational schema, a
  capability gap behind a valid `after` order, investigation ahead of blocked
  delivery, an answer that invalidates planned work, and coverage after disposal.
  Seeded evaluation 36 checks that `ow-assess` finds planted planning defects.

## v0.8.2

### Fixed

- A CLI older than a project's installed integrations now refuses to run there and
  asks for an upgrade. Previously it reported records written for the newer version,
  such as `generated` code exceptions, as invalid configuration. `ow skills` keeps
  its explicit downgrade prompt.

- An empty `.git` directory, such as the read-only placeholder Codex's sandbox mounts
  into plain directories, is no longer treated as an unreadable repository, so
  `ow check`, `ow trace` and reviews work there instead of reporting an incomplete
  inspection.

### Changed

- `ow-propose` adds **Check the sequence**: before a sequence is presented or revised,
  every prerequisite names its provider (existing code or a transitive predecessor),
  every deferral names the change that takes it, and every acceptance criterion of
  the covered needs is met, planned, or held by an unplanned change. Uncovered needs
  are reported as omissions. `ow-plan` rechecks after reconciling, `ow-review`
  requires deferral destinations to list the work, and the change template and
  artifact reference ask for prerequisite providers and deferral destinations.

- Evaluation presets run each agent with an isolated `HOME`, so login shells (which
  Codex uses) cannot reread the user's profile and pick up an installed `ow` instead
  of the checkout. A preflight resolves `ow` exactly as agent shells do and refuses to
  run on a mismatch, and baseline arms get failing `ow` and `openwish` stubs.
- Evaluations run a 6-eval core suite by default (30, 1, 7, 20, 25, 26: 11 agent
  sessions), with arms in parallel (`--jobs`); `--full` runs everything. Evaluations
  9, 28 and 29 are removed because executable scenario 30 now grades direct delivery
  and promotion mechanically.

## v0.8.1

### Fixed

- The release smoke test expects `ow ready --json` to list a verification-only change
  as unplanned (with no tasks) instead of failing on the new `unplanned` key. The
  v0.8.0 release build stopped at this check; 0.8.1 ships the same product.

### Added

- Evaluation seeds materialize the needs, changes, code and passing reviews that
  dry-run cases 7, 20, 21 and 25–29 describe, validated by a unit test, so `ow context`
  agrees with each scenario.
- Executable evaluation 30 checks direct delivery, managed work with deferral and
  delayed acceptance, and continuing that change, mechanically for both arms.
- The evaluation `ow` shim logs every invocation per stage (`ow_calls`), so graders
  and cost comparisons can see the workflow an agent used.

## v0.8.0

### Changed

- **Direct or managed delivery replaces routine or structured work.** Every product
  change recovers intent, clarifies only what matters, designs, verifies and reviews in
  proportion. Direct delivery (one result finished in one session, nothing deferred or
  undecided, no covering change) keeps no change records; managed delivery uses
  changes and is promoted to as soon as coordination needs appear. Single-session
  increments no longer pay for changes, tasks, reviews and cleanup.
- Confirmation is provenance, never a gate: faithful recording of explicit
  instructions needs no approval round, and moving unapproved items to `open` keeps
  `confirmed_at`. Open questions and unsettled values block only dependent work; an
  unsettled value gets a labeled placeholder in its home.
- Architecture and maintainability mechanisms are engineering duties, not needs; a
  requested extension property is protected by a test. Project-wide engineering
  requirements (setup, checks, releases) get a home in an ordinary doc linked from
  the policy's knowledge table, and alignment and review check them.
- Changes link the needs whose outcomes they advance, not every need they must
  respect; constraining needs still bind through review. Rules shared by several kinds
  are stated once, with per-kind values in their table.
- Each skill states its direct and managed paths explicitly (`ow context` without a
  change ID, no task, review-record, close or clean commands for direct work). A skill
  entered before intake first reconciles needs and chooses delivery, and `ow-plan`
  defines how to promote direct work: one change for the whole result, completed work
  as evidence-backed done tasks, the remainder as open, blocked or manual tasks.
- A placeholder for an unsettled value may back schemas, interfaces and test fixtures,
  never shipped behavior that depends on the value.
- Skills load when their step begins, and agents read the artifact reference only when
  writing or repairing records.
- Needs separate structural rules from calibration: tunable values (prices, rates,
  thresholds) live once in referenced rule docs or data, and acceptance says behavior
  follows them, so tuning does not rewrite intent.
- Acceptance is written as readable sentences, one criterion each. Hosts, tools, sibling
  repositories and test accounts belong in ordinary docs, not needs.
- `confirmed_at` means every acceptance criterion is confirmed; undecided questions
  and proposed criteria go in a need's new optional `open` list, which `ow status`
  counts until they are decided.
- One home per fact: changes link to retained rules instead of restating them, plans
  state current decisions without supersession notes, and READMEs and architecture
  docs orient instead of copying rule values. The change template's Approach follows suit.
- Task guidance: one checkable result per task, specific `files`, and no final task
  that repeats earlier checks. Compaction may expand shorthand into sentences.
- Tasks are written for **ready** increments (prerequisites in the repository, no open
  material decision), not just the next one in sequence. A new *Plan a candidate*
  procedure verifies prerequisites in code and refreshes the approach before tasking;
  `ow-consolidate` continues the sequence by planning what a disposed change unblocked,
  and fast-forward does the same across named changes.

- Guidance keeps one owner per rule: sequencing, open items and one-home rules are
  stated once and referenced elsewhere, the artifact reference holds formats and CLI
  behavior only, and skills cite the policy's A/B/C question format.

### Added

- `code_exceptions` accepts `kind: "generated"` for tool output such as lockfile
  loaders and vendored releases; those files stay silent, even under a hard limit,
  until they disappear.
- `ow check` warns when a current need cites a path Git ignores, and when a change
  links to another change's files.
- `ow context` also returns work state (changes with review freshness, ready and
  waiting tasks, unplanned changes, repository, budget and knowledge warnings), so one
  call starts a session.
- `ow ready` lists active changes without tasks as unplanned (`PLAN`), so the next
  increments stay visible after their predecessor is disposed.
- Change sequences: optional `after = ["C-001"]` (`ow new change --after`). Successors
  become plannable once predecessors pass review, or once accepted when config sets
  `successors_wait_for = "acceptance"`; tasks of a waiting change are never ready.
  `ow close` accepts a change only after or with its predecessors, `ow clean` removes
  disposed IDs from successors, and review freshness ignores `after`.

- Skill evaluations 25–27 cover needs that keep rules but not calibration or setup,
  sequences that continue on a reviewed predecessor, and open items staying
  non-binding until decided; 28–29 cover direct delivery of bounded cross-file work and
  promotion to a change. Evaluation 19 expects tasks only for ready work, 24 accepts
  direct delivery and expects no architecture needs, and dry-run prompts state that
  the described project is given rather than present in the working directory.
- Evaluation grading runs each retained test separately: mutants are graded only by
  tests that pass on the reference, a mutant counts as killed only by an assertion
  failure, per-mutant diagnostics are kept, and the product's own suite is always run;
  mutation is graded only when that suite passes.
- Evaluations use agent presets pinned to a flagship model at planning-level
  reasoning: `codex` (default; Codex CLI, `gpt-6.1-sol`, high) and `claude` (Claude
  Code, `claude-opus-5-5`, high). Presets run in an isolated agent home that links only
  the user's credentials, so personal instructions and settings cannot leak into
  results, and a workspace refuses a second agent. Codex JSONL token usage is recorded.

### Fixed

- `ow init` now upgrades `openwish/artifacts.md` with the skills; it was previously
  written once and went stale. **Breaking:** an existing unstamped reference is refused
  with guidance; delete it and rerun `ow init`. Project policy is still preserved.
- Recording a need's `open` items no longer stales pending reviews; they do not bind.
- Evaluation acceptance checks import the product as its own modules would, so sibling
  imports and dataclasses no longer fail spuriously; lending checks now cover DVD holds.

## v0.7.0

### Added

- A safe-to-forget handoff assessment inside the single disposable review: material
  obligations, actual retained destinations, independent evidence and explicit disposition.
- Cleanup preview (`--dry-run`, optional JSON), batch destination checks, incoming
  handoff dependency protection, and warnings for retained files that still mention
  a removed change ID.
- `ow trace`: need → test/file links derived from need IDs mentioned in code, tests and
  docs. `ow check` warns about mentions of unknown or retired needs.
- `ow task C-001/T-001 STATUS [--evidence ...]` updates one task, enforcing evidence and
  prerequisites and moving the change to in-progress.
- `record-review --handoff -` reads the handoff from stdin.
- Complete JSON context with sized retrieval manifests and optional durable need
  references to detailed rule documents/data; referenced content is explicitly not loaded.
- Recursive submodule discovery and review freshness for gitlink revisions, checked-out
  revisions and unignored working content, with explicit incomplete-inspection reporting.
- An evaluation runner (`evals/run.py`) with OW and no-OW baseline arms, fresh-session
  stages, acceptance checks, seeded-mutant grading of retained tests, and time/token
  capture; a four-stage long-horizon scenario with a revision and a rewrite.

### Changed

- **Breaking:** `record-review --covered-need` is replaced by `--affected`. Linked needs
  are always affected; every other current need is recorded as assessed and unaffected.
  Reviews store `affected`/`unaffected` and per-input digests instead of one fingerprint.
- Stale reviews name what changed (needs, approach, tasks, policy, specific files).
- Recording a review, closing or cleaning a batch, and each status/summary projection
  take one repository snapshot per command.
- Policy, artifact reference and skills are rewritten to give each rule one owner, cut
  their size by about half, drop references to concepts OW does not have, and use
  worked examples from domains no evaluation scenario uses. Skills add short module
  headers and boundary READMEs as the orientation convention and need IDs in tests.
- Needs default to a 24,000 estimated-token soft target. OW artifact/global-context
  line caps are removed; individual artifacts warn at 8,000 estimated tokens
  (machine-written reviews and installer records are exempt).
- Source retains a 500-LOC warning; hard enforcement is an explicit project option
  (`source_hard_limit`, default 0). Size warnings do not block inspection.
- Evaluation assertions no longer check for concepts the guidance never mentions;
  scenarios are sorted by ID.
- Package and bundled integrations advance together to 0.7.0. **Schema 4** requires
  handoff assessments for passing reviews; only the current schema is supported.

## v0.6.1

### Changed

- Changes are sized by independently reviewable results, with explicit delivers-now,
  preserved constraints, deferrals, and exit evidence in the creation template.
- Broad planning requests produce multiple candidate increments; future work uses
  concise ordinary open changes and is detailed against delivered capabilities when
  selected. Shared modules or sequential dependencies alone do not require one change.
- Task guidance exposes concrete completion/blocking boundaries instead of favoring
  short lists that can conceal whole subsystems. Representative integration happens early.
- Planning and resumption reconcile scope growth, resolved decisions, stale blockers,
  and outcome-to-work coverage. Splits preserve unfinished obligations and evidence;
  successor plans remain usable after earlier changes are disposed.
- Review checks the promised increment and exit evidence as well as task completion,
  distinguishing partial need contributions from complete delivery. Empty future task
  lists do not establish completion, and split changes do not inherit delegation.
- CLI check summaries identify structural/budget validation; an empty ready list
  directs attention to scope and evidence rather than implying the work is complete.
- Added semantic regressions for large modernization, growing plans with stale state,
  and a narrow cross-cutting change serving many needs.
- Package and bundled integrations advance together to 0.6.1; artifact schema remains 3.
  Existing project-owned policy/reference files are preserved during integration updates.

## v0.6.0

### Added

- A shared, code-grounded architecture rubric covering discoverability, rule
  ownership, dependencies, effects, independent checks, and justified complexity.
- Greenfield first-slice/evolution guidance and brownfield architecture assessment
  with bounded refactor proposals and human approval of additional scope.
- Need-sizing and consolidation criteria for mechanisms, independent outcomes,
  duplicates, broad bundles, and evolving intent.
- Optional reasoned `requires`/`constrains` relations on needs and a derived
  `ow graph [N-001 ...] --json` view. Semantic cycles are allowed; links do not
  replace all-current-needs review or create a permanent analysis registry.
- Retention attention groups in status, early context-budget warnings, and explicit
  guidance for disposal, retired needs, manual procedures, and durable evidence.
- Repository-grounded skill evaluations for architecture discovery and evolution.
- Strategic verification guidance: small, fast checks of stable outcomes and
  consequential failures, reuse of existing coverage, and deliberate test retention.

### Changed

- The greenfield skill evaluation assesses independently rerunnable current tests,
  proportionate protection, and useful retained artifacts instead of requiring
  historical first-slice execution evidence after disposal.
- Status/summary and batch closure share a repository fingerprint within one command;
  subsequent commands read a fresh snapshot. Status builds reverse change links once.
- Bundled integrations and package version advance together to 0.6.0. Artifact
  schema remains 3; optional relation tables live in the existing need records.

### Fixed

- Misplaced/nested need artifacts produce a validation error instead of silently
  disappearing from current intent.
- Executable-permission changes invalidate pending result reviews.

## v0.5.0

OW now preserves durable needs and uses disposable changes/tasks for execution.
Humans ask. AI identifies needs, aligns design and engineering, implements, and
reviews. Humans review the results.

### Changed

- Artifact **schema 3** replaces Needs → Specs → Epics → Tasks with many-to-many
  Needs → Changes and change-local Tasks. Working design lives in the change;
  implemented behavior and executable checks live in the repository.
- Needs retain intent, currency, and actual confirmation provenance. Execution
  status and delegation belong to changes. Closing an increment does not retire,
  confirm, or permanently approve an entire need.
- Task lists use local optional prerequisites and list order, without global
  group/order pairs. Independent work continues around manual blockers.
- One disposable review per change checks current/linked needs and relevant
  regressions. Its freshness binds intent, working approach, tasks/evidence,
  policy/config, and repository content while awaiting result acceptance.
- All eight bundled skills, documentation, and semantic scenarios follow the new
  model, with functional cores and discoverable repository design as defaults.

### Added

- `ow new change C-001 --title ... --need N-001` scopes bounded work directly to needs.
- `ow close C-001 --by human` records actual result acceptance; `--by fast-forward`
  uses explicitly delegated change mode after the same verification requirements.
- `ow clean C-001` disposes closed changes, tasks, and reviews. It preflights the
  full selection and preserves unknown files, symlinks, needs, and product code.
- `context`, `ready`, and `summary` accept need/change selections. Status derives
  active work from changes and treats retained closed reviews as historical.

### Removed

- Persistent specs/epics, need-owned execution/review sidecars, stage gates,
  `authorize`, `approve`, and `reopen`. Conversation authority governs scope;
  substantive results still receive human review unless explicitly delegated.
- Mandatory operational knowledge scaffolding and arbitrary retained-epic limits.
  Useful rationale belongs near code or in ordinary repository documentation.

### Compatibility

Before v1.0.0, OW supports only the current schema, with no migration tooling or
legacy compatibility. Unversioned-template recognition and historical need-field
handling have been removed. Unsupported schemas are rejected before writes.
Schema-3 reinitialization keeps project-owned knowledge and local policy.
Package and bundled integrations are 0.5.0.

## v0.4.0

Workflow overhead is now proportional to the work, with execution authorization
separate from regression coverage.

### Added

- `ow authorize N-001 ... --by human` records one combined authorization for
  needs, design, and implementation after preflighting the full selection.
  `--by fast-forward` records explicitly delegated authority. Separate staged
  gates remain available; default-mode final acceptance is still separate.
- An optional epic `needs` array selects a nonempty subset of its specs' needs
  for execution. Other linked needs remain regression constraints without
  requiring unrelated implementation authorization.
- The `openwish` executable is an exact alias of `ow`, using the same entry point.
  `ow` remains the canonical short form in examples.
- Python 3.14 joins the Python 3.11–3.13 test matrix. Distribution smoke tests
  exercise both CLI aliases, all harness assets, and no-op reinitialization.

### Changed

- Clear, localized, reversible changes within existing intent use a routine
  inspect → implement → verify → report path, without new needs, epics, gate
  receipts, or final acceptance prompts.
- Structured Propose, Align, and Plan prepare together. Existing conversation
  authority can cover the scope; otherwise, one combined decision authorizes it.
  Technical plan repairs within that scope do not require renewed permission.
- Skills respect explicit OW opt-outs and plan-only requests, reuse durable
  outcomes, and distinguish needs from mechanisms, commands, platforms, and tasks.
  Shared specs do not need to be split solely to isolate authorization.
- The source repository uses ordinary contributor documentation and product
  requirements instead of an active self-hosted OW workflow. Workflow tests run
  in disposable projects.

### Fixed

- Scoped-epic review coverage includes every linked spec and its connected
  contracts, including specs that do not directly reference an execution need.
  Changes to those contracts invalidate authorization and review freshness.
- Routine fast-forward changes stop after verification and reporting rather than
  entering structured lifecycle steps. Loading the skill alone grants no authority.
- Installation documentation reflects the existing PyPI publication, and release
  documentation matches the supported Python test matrix.

### Upgrade

```sh
uv tool upgrade openwish
ow init
```

Run `ow init` in each project to update its selected skills and adapters. Artifact
schema remains **2**; epics without a `needs` header retain their all-linked-needs
execution scope. Adding or changing that header invalidates affected authority
and reviews; reconcile the plan and refresh receipts under the applicable
conversation authority.

Project-owned policy and artifact-reference files were preserved, with guidance
for merging the proportional workflow and execution scope into local policy.

## v0.3.1

First published PyPI release of OpenWish: a dependency-free Python 3.11+ CLI and
bundled skills for need-driven development with coding agents.

### Added

- The `openwish` Python distribution and `ow` executable, installable with
  `uv tool install openwish`.
- Eight canonical skills covering Propose, Align, Plan, Implement, Review,
  Consolidate, Fast-forward, and Onboard, with integrations for OpenCode,
  Claude Code, Codex, and generic Agent Skills hosts.
- Interactive harness multi-selection, explicit flags for automation, and
  deduplicated installation for harnesses sharing the same skill directory.
- Version-aware integration updates: upgrade older files, preserve same-version
  files and local edits, require confirmation for downgrades, and recognize exact
  legacy v0.2 templates. Reinitialization preserves project knowledge and policy.
- Artifact schema 2 with stable need IDs, separate currency and implementation
  states, spec-owned need references, and bounded epic/task execution plans.
  Current needs continue to constrain future work after their implementation is
  approved; asks remain in conversation rather than stored change records.
- CLI scaffolding, validation, context, status, ready-work, and outcome summaries;
  revision-bound stage gates, explicit fast-forward authority, and reviews tied
  to the plan, repository content, and task evidence.
- Dependency-aware task scheduling, continued independent work around manual
  blockers, artifact/context budgets, and source-size checks.
- Tested wheel and source distributions, package/tag version checks, strict
  metadata validation, and clean-install smoke tests. GitHub release publishing
  uses PyPI Trusted Publishing, with manual TestPyPI rehearsals.

### Fixed

- Updated the CI/CD workflows and pinned build/check actions for the initial
  published release.
