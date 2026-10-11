# OpenWish framework design — 0.6

## Core invariant

Every solution is evaluated against all current needs, including delivered
outcomes. Needs preserve durable intent. Code expresses implemented behavior;
tests check expected behavior. Working design and coordination are disposable.

```text
Needs ← referenced by → Changes → contain Tasks
```

Need/change references are many-to-many. Task dependencies are local to a change,
so disposal cannot break another change's execution graph. Asks stay in conversation.
Changes describe bounded improvements, rather than building a permanent ask ledger.

## Repository architecture

Python 3.11+ and the standard library provide the CLI. Markdown with TOML
frontmatter holds needs and temporary changes. JSON holds task lists, latest
reviews, configuration, and installer bookkeeping. `tomllib` handles TOML.

| Module | Responsibility |
| --- | --- |
| `storage.py` | Root discovery, safe paths, bounded atomic writes, schema-3 loading |
| `model.py` | Pure selection, sparse need graph, retention groups, context, task readiness |
| `validation.py` | Typed records, references, local acyclic prerequisites |
| `budgets.py` | Context/artifact limits, Git-aware source discovery, source-size checks |
| `workflow.py` | Latest review, one result fingerprint, closure, conservative cleanup |
| `views.py` | Derived status and need → outcome → evidence summaries |
| `scaffold.py` | Initialization and need/change creation |
| `integrations.py` | Version-aware canonical skill installation and thin host adapters |
| `versions.py` | OW version stamps and SemVer precedence |
| `terminal.py` | Harness multi-select and downgrade confirmation |
| `cli.py` | Command parsing and concise human/machine output |

Keep functional model operations separate from filesystem effects. Favor cohesive
modules and explicit dependencies; there is no need for a class hierarchy or a
second persistent design model. The harness supplies reasoning and code execution.

## Durable needs

`needs/N-001.md` records title, actor, outcome, observable acceptance, currency,
human confirmation date, and optional body constraints/rationale. Currency is
`current | retired`. Need IDs survive intent revisions. `confirmed_at` is empty
for inference and changes only on actual human confirmation.

Needs have no implementation status, mode, gate receipts, review sidecars, or
reopen lifecycle. Changes derive their need links directly. Closing one change
does not claim the entirety of a need is delivered or erase its future relevance.
Closure does not infer human confirmation of intent.

Optional `relations` are inline TOML tables on the source need, each with `kind`,
target `need`, and `reason`. `requires` expresses an outcome prerequisite;
`constrains` expresses a limit on the target's acceptable solutions. Validation
rejects missing targets, self-links, duplicate kind/target pairs, empty reasons,
and current-to-retired links. Semantic cycles are valid; this is not a task DAG.
Incoming links and retained change references must be reconciled on deletion.

`graph [N-001 ...] [--json]` constructs an edge list in one pass over the validated
need snapshot. Selection includes incident edges and endpoints, with currency,
not transitive impact or an inferred complete graph. Relations survive change
disposal and are included in complete need context and review freshness. There
is no graph sidecar, all-pairs inference, persistent cache, or need-to-code ledger.
Agents preserve established intent facts, reuse valid working assessments, and
revisit changed inputs/neighbors and possible new interactions. Code dependencies
are reconstructed from source/tests as needed. All current needs remain binding.

## Architectural reasoning

The `ow-align` skill owns a shared rubric used by onboarding, implementation, and
review: discoverability, rule ownership/locality, explicit dependencies/data ownership,
isolated effects, independent tests, justified complexity, and understanding after
disposal. Findings connect code-grounded observations to consequences, proposed
improvements, and verification. Small files alone do not establish good architecture.

Pure decisions, validation, transformations, and transitions accept explicit data.
Time/randomness/configuration and external results enter at identifiable effect
boundaries; core and integration checks have distinct purposes. Avoid abstractions
added solely to appear functional. Greenfield work starts with a minimal conventional
layout and an end-to-end slice; subsequent asks reassess affected boundaries.

Onboarding inspects actual paths and compares retaining satisfactory structure with
targeted improvements. Useful refactor proposals include scope, behavior baseline,
incremental steps, cost/risk, and verification/rollback. The human authorizes that
scope before edits. Assessments live in conversation or disposable changes; only
otherwise unrecoverable rationale survives near the implementation.

Need-sizing guidance distinguishes coherent outcomes from mechanism-sized records
and broad bundles. Acceptance/retirement independence justifies a split; matching
intent justifies reuse/merge. Scope/meaning changes require a decision. Stable IDs
aid continuity, not permanent immutability.

## Temporary changes and tasks

`changes/C-001/change.md` references its motivating needs and holds purpose,
approach, and verification. Status is `open | in-progress | review | closed`;
mode is `default | fast-forward`. Implementation choices evolve here while work
is active, then survive in code, types, schemas, tests, and useful nearby rationale.

`tasks.json` contains a list with required ID, title, status, and acceptance.
Optional prerequisites, kind, files, and evidence keep simple tasks small. Task
status is `open | in-progress | blocked | done`. Done tasks require direct evidence.
IDs are qualified by their change; dependencies are within-change and acyclic.
List order is a preference, not an implicit dependency. There are no group/order
constraints or global task ordinals. An empty list supports verification-only work.

`ready` accepts need/change selections or defaults to all active changes. It lists
agent-ready tasks and explains waiting prerequisites, manual observations, and
explicit blockers. Continue independent work while human input is unavailable.
Readiness never supplies authority. Interdependent work belongs in one bounded
change; independent changes coordinate through delivered code/interfaces.

## Authority and result review

OW adoption is opt-in. Routine changes use direct implementation and verification.
Substantive changes prepare intent, approach, and tasks together. Conversation
instructions authorize scope; plan-only requests stop before implementation.
Consequential uncertainty requires a decision. Technical repairs within scope
require no repeated permission. There are no stage authorization records.

Default work presents results for human review. After actual acceptance, `close
C-001 --by human` records closure provenance and time. Explicit fast-forward
delegates acceptance only for this change, recorded with `--by fast-forward`.
It does not confirm inferred needs, invent checks, or waive manual observations.
New changes default to normal review, even when their needs were previously
served by fast-forwarded work. The CLI records supplied provenance, not proof
that a human conversation occurred.

Each change has one disposable `review.json`, replaced on review. Passing review
requires completed tasks, direct checks, an outcome summary, and coverage of all
current needs plus linked retired needs when applicable. Coverage means semantic
assessment of constraints and relevant regressions; the agent explains unaffected
needs and checks affected behavior. Structural validation cannot prove correctness.

One fingerprint protects review freshness while results await acceptance. It covers:

- Current and directly linked need content.
- The change's purpose/approach, need references, and mode.
- Local task definitions and results.
- Project config/policy and repository content outside `openwish/`.

Repository discovery uses Git tracked and unignored untracked files; non-Git
projects use filesystem traversal. Build/dependency directories and symlinks are
excluded. External/manual observations remain explicit reported evidence. Source
hashing is intentionally conservative; code changes require refreshed review.
Executable permission changes also invalidate review. Status/summary lazily reuse
one repository fingerprint within the command; batch closure also shares one
snapshot. Subsequent commands read fresh inputs. Need-to-change reverse lookup
is built once per status projection. No persistent cache can mask later edits.
Other changes' temporary plans and runtime status/closure metadata are excluded.
This is one pending-result check, not a receipt chain. Closed reviews are historical.

## Closure and disposal

Before final review, lasting behavior/checks belong in source/tests, changed
intent in needs, and unrecoverable rationale in ordinary repo docs or comments.
Keep unresolved limitations visible. Completed task evidence stays until closure.

`close` preflights every selected change, then records status, timestamp, and
acceptance provenance. It never writes needs. `clean` preflights closed changes
and removes only `change.md`, `tasks.json`, and `review.json`. Unknown files,
directories, or symlinks cause refusal before deletion. Needs, code, tests, other
changes, and project policy are retained. There is no archive or history ledger.
Git may retain useful history; cleanup does not require an automatic commit.

Closed changes may be cleaned after subsequent code edits: their review records
past acceptance, not a live guarantee. Follow-up implementation uses a new change.
Batch semantic preflight prevents known conflicts from causing partial operations;
individual file replacements are atomic. Multi-file operations are not filesystem
transactions and OS failures can require inspecting the remaining files.

## Context and bounds

All current need content enters context. Global limits are under 500 lines and a
configurable estimated-token budget, default 6,000 using UTF-8 bytes/3. Detailed
changes are loaded only for relevant work. Each OW artifact remains under 500 lines.

Source size uses nonblank physical lines as a cross-language proxy: under 500 is
the soft target, under 1000 the hard maximum. Data formats are exempt. Exact-path
low-complexity exceptions require rationale and do not exempt OW artifacts.
Closed changes prompt cleanup rather than failing an arbitrary working-set count.

At 80% of the token budget or 400 current-context lines, warn before failure.
Status derives retention groups for closed changes, review-state changes (which
may need refreshed checks), blocked/manual work, and retired needs. Agents also
look for duplicates, broad bundles, mechanism-sized needs, and drift. Total file
count has no hard cap: disposal is normal completion, deferrals are reported,
and abandoned-looking work is reconciled rather than silently discarded. Retired
needs can be removed after a retention decision and reference reconciliation.

Tests/manual procedures enable new evidence. Run results and closure provenance
are disposable; OW has no durable delivery ledger or satisfaction certification.
Only selected operational facts and non-obvious rationale survive in docs/comments.
Historical proof is product data when a need explicitly calls for it. Tool config,
policy, reference, skills/adapters, and installer bookkeeping are not evidence.

## Integration and compatibility

Eight canonical skills describe activities, not eight artifact tiers. They are
packaged once, with thin adapters for OpenCode, Claude Code, Codex, and generic
Agent Skills. Explicit-only fast-forward controls and body checks travel with
the integration. Existing installer behavior is retained:

- Interactive multi-selection; repeatable explicit harness flags for automation.
- Codex/generic shared paths deduplicated.
- Per-file version stamps and a bounded installation manifest.
- Older integrations upgraded, equal versions untouched, downgrades confirmed.
- Unversioned files without an installation record preserved.
- All selected integrations preflighted before writes; deselection does not uninstall.
- Package/module/skill versions advance together.

Only the current schema (3) is supported. Before v1.0.0, breaking changes require
no migration tooling or legacy compatibility. `init`, `skills`, and normal project
commands reject unsupported schemas before writing. Reinitialization preserves
local config, policy, needs, and work in current-schema projects.

## Verification

The `ow-plan` skill owns Strategic verification guidance, shared by alignment,
implementation, onboarding, review, and consolidation. Select a small, fast set of
checks for stable outcomes, important decisions/invariants, and consequential
boundaries. Reuse existing coverage, add checks for real gaps, and state remaining
uncertainty. Not every task, function, or layer warrants its own test. Large mock
setups for simple rules can expose poor boundaries rather than demand more scaffolding.

Tests should withstand harmless refactors and detect meaningful violations of needs.
Avoid incidental text/layout snapshots, private-call assertions, and speculative
negative matrices. Narrow exact assertions suit actual contracts; credible failures
with serious consequences deserve checks even without a coverage target. Explicit
human/project coverage requirements are honored without treating 100% as correctness.
Temporary probes may disappear; lasting tests enable fresh verification after
change disposal, without a permanent archive of stage-by-stage execution evidence.

Tests cover many-to-many need links, local task readiness, manual blockers, cycles,
malformed artifacts, complete context, safe cleanup, provenance, stale reviews,
and schema refusal without writes. CLI scenarios execute default and fast-forward
flows in temporary projects and verify that disposal retains intent and product files.
Installer/terminal tests protect preservation, multi-harness preflight, upgrades,
downgrades, and terminal restoration. Distribution checks exercise installed wheel
and source packages, both CLI aliases, assets, and the change lifecycle.

Semantic skill scenarios cover intent reuse, conflicts, plan-only scope, opt-outs,
routine work, manual blockers, change-scoped delegation, and disposal. They
complement deterministic tests and do not prove behavior across every model/harness.
The greenfield evaluation reruns retained tests and checks their useful protection
and cost against current needs. Final artifacts do not establish historical run
order; evaluating that would require separate harness-captured checkpoints outside
the product. Test-count growth alone earns no evaluation credit.
