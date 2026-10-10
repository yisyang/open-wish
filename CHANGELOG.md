# Changelog

Release notes for OpenWish, newest first. Update this file for every release.

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
