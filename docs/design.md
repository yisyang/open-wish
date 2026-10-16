# OpenWish framework design — 0.8

## Core invariant

Every solution is evaluated against all current needs, including delivered outcomes.
Needs preserve durable intent; code expresses implemented behavior; tests check it;
working design and coordination are disposable.

```text
Needs ← referenced by → Changes → contain Tasks
```

Need/change references are many-to-many. Task dependencies are local to a change,
so deleting a change cannot break another change's plan.

## Repository architecture

Python 3.11+ and the standard library. Markdown with TOML frontmatter holds needs and
changes; JSON holds tasks, reviews, configuration and installer bookkeeping.

Each module in `src/openwish/` opens with a one-line responsibility docstring; read
those rather than a duplicated table here. Dependency direction:

```text
cli ─→ views ─→ workflow ─→ handoff, trace, repository ─→ storage
   └─→ scaffold, integrations, context, budgets, validation ─→ model ─→ storage
```

`model.py` holds pure projections and scheduling; filesystem effects stay in
`storage.py`, `repository.py` and the command modules. There is no class hierarchy
or persistent derived model; every command reads current files.

## Needs

`needs/N-001.md` holds title, actor, outcome, acceptance, optional `open` (undecided
questions and proposed criteria, never binding), currency, `confirmed_at`, an
optional body, optional `references` (existing, non-ignored repository files; no
symlinks, `..` or change paths) and optional `relations` (`requires | constrains`
inline tables with a reason). Validation rejects missing targets, self-links,
duplicates, empty reasons and current-to-retired links; semantic cycles are valid.
`ow graph` derives incident edges in one pass, without transitive inference.

## Changes and tasks

`changes/C-001/change.md` has `needs`, `status` (`open | in-progress | review | closed`),
`mode` (`default | fast-forward`), optional `after` (predecessor changes, acyclic) and a
prose body whose headings are conventions. `after` is the only cross-change link and
is scheduling only: `model.waiting_on` applies the configured gate (`review` or
`acceptance`), `close` refuses to accept a change before its predecessors, review
freshness ignores the field, and `clean` removes disposed IDs from successors so no
reference dangles. Whether prerequisites truly exist remains a code inspection.
`tasks.json` lists tasks with `id`, `title`, `status`, `acceptance` and optional
`depends_on`, `kind` (`agent | manual | investigate`), `files`, `evidence`. `done`
needs evidence; dependencies are local and acyclic. `ow task` updates one task
atomically, checks evidence and prerequisites, and moves a reviewed change, or an
open one starting delivery, to `in-progress`. `ready` reports readiness, never
permission. Investigations are exempt from the `after` gate, because they produce
findings rather than behavior and learning late is the cost sequencing would
otherwise impose; a blocked investigation is a question for a human and is listed
as `ASK`; a change with only investigations is still listed as unplanned,
and whether its prerequisites exist is judged from the code.

## Review and freshness

Each change has one `review.json`, replaced on every review:

- `verdict`, `summary`, `checks`, `handoff`, `at`.
- `affected`: linked needs plus `--affected` additions. `unaffected`: every other
  current need, recorded as assessed. The agent is responsible for that judgment;
  the record makes it explicit and the summary shows it.
- `inputs` (passing reviews): short digests of the change (without lifecycle fields
  or `after`), tasks, each current and linked need (without its non-binding `open`
  items), the handoff and each destination, config, policy, each product file
  outside `openwish/` (content plus executable bits), and submodule revisions.

Freshness compares recorded and current inputs. Any difference is stale, and the
error lists what changed (approach, tasks, `N-001 modified`, `src/x.py added`, and
so on), so a reviewer can refresh only the affected verification. Per-file digests
keep the check conservative: a parallel change's edits also stale a pending review,
deliberately, because the reviewer must judge whether they matter.

Repository discovery uses Git tracked and unignored untracked files (recursively into
submodules, including staged gitlinks and checked-out revisions); non-Git projects
walk the filesystem. Build and dependency directories and symlinks are excluded.
Missing, conflicted or uninspectable components produce warnings and prevent a fresh
passing review or closure. Recording a review, closing a batch, cleaning a batch and
each status/summary projection take one repository snapshot per command.

Passing requires all tasks done, at least one check, and a nonempty handoff with no
`unresolved` items. Handoff items have exactly `requirement`, `disposition`
(`implemented | retained | deferred | superseded | unresolved`), `destinations` and
`evidence`. Destinations are existing, non-ignored repository files; implemented
behavior cannot cite `openwish/` records, and only deferred work can cite another
active change. Validation establishes existence and structure, not meaning.

## Closure and cleanup

`close` preflights every selected change, then records `closed`, `closed_by`
(`human | fast-forward`, the latter only in fast-forward mode) and `closed_at`. It
never writes needs. `clean` preflights the batch, then removes only `change.md`,
`tasks.json` and `review.json`; unknown files or symlinks cause refusal. It rejects
missing or ignored destinations, destinations inside the batch, closed deferred
successors and retained reviews that cite the batch, and warns about retained text
files that still mention a removed change ID. Closed reviews are historical; later
code edits do not block cleanup. Multi-file operations are preflighted, not
transactional; each file write is atomic.

## Trace

`trace.py` scans code, test and doc files (not `openwish/` or installed guidance) for
need and change IDs. `ow trace` reports, per need, which conventional test locations
and other files mention it, plus current needs with no traced check. `ow check` warns
about mentions of unknown or retired needs. The link is derived from the repository
on demand; nothing is stored, and absence of a trace is never treated as proof.

`validation.knowledge_warnings` adds two `ow check` warnings: a current need citing an
existing path that repository inspection excludes (ignored, so a fresh clone lacks it),
and a change body linking to another change's files. Referenced docs are not scanned,
because explaining how to obtain an ignored input is their job.

## Context and bounds

`ow context` includes all current need content without truncation, plus work state for
the selection (changes with review freshness, ready and waiting tasks, unplanned
changes, and repository, budget and knowledge warnings), so one call starts a session.
`--json` adds review scope and sized retrieval entries (`included: false`) for selected changes, tasks,
linked retired needs and need references. Estimates use UTF-8 bytes/3 and exclude
other source and conversation. `needs_token_budget` (default 24,000) warns at 80%;
OW artifacts warn at 8,000 estimated tokens, except machine-written `review.json` and
`installation.json`; source warns at 500 nonblank lines and fails only under an opt-in
`source_hard_limit`. Configured exceptions keep warning with their reason, except
`generated` files, which are tool output and stay silent until they disappear. Status derives retention groups for closed, awaiting-acceptance
and blocked changes and retired needs.

## Agent guidance

Policy and skills are product assets in `src/openwish/assets/`. Each rule has one
owner: the policy holds principles and authority; each skill holds one procedure
and the shared sections it owns (Right-size intent and delivery in `ow-propose`, the
Architecture rubric in `ow-align`, Task sizing, Plan a candidate, Reconcile the plan and Strategic
verification in `ow-plan`, Safe to forget in `ow-review`). Other skills refer to these
sections by name instead of restating them. Worked examples use domains that do not
appear in the evaluation scenarios.

## Integration and compatibility

Nine canonical skills are packaged once, with thin adapters for OpenCode, Claude Code,
Codex and generic Agent Skills. `openwish/artifacts.md` documents the CLI, so the
installer manages it like the skills; `policy.md` is project-owned. The installer offers interactive multi-select and
repeatable flags, deduplicates shared paths, stamps each file with the OW version,
records ownership in `installation.json`, upgrades older files, leaves equal versions
alone, asks before downgrades, preserves unversioned unrecorded files, and preflights
every selected harness before writing. Deselection does not uninstall. Only schema 4
is supported; `init`, `skills` and project commands reject other schemas before writing.

## Verification

Deterministic tests cover need links, task readiness and updates, manual blockers,
cycles, malformed artifacts, complete context, review freshness and its explanations,
need assessment records, handoff validation, trace, safe cleanup, provenance,
submodules, schema refusal, the installer and terminal handling. CLI scenarios run
default and fast-forward lifecycles in temporary projects. Distribution checks install
built wheels and sdists and exercise both aliases and a lifecycle.

Skill behavior is evaluated separately (`evals/`): a runner executes scenarios per arm
(OW skills versus no-OW baseline), runs multi-stage scenarios as fresh sessions, grades
executable scenarios with external acceptance checks and with seeded mutants against
the product's retained tests, and records time and token usage. A unit test keeps the
evaluator references and acceptance checks consistent. Small samples do not prove
behavior across every model or harness.
