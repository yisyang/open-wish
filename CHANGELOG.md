# Changelog

Release notes for OpenWish, newest first. Update this file for every release.

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
