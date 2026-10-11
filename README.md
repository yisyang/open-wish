# OpenWish (OW)

**Need-Driven Development for humans and coding agents.**

Humans ask. AI identifies needs, aligns design and engineering, implements, and
reviews. Humans review the results.

**Durable intent. Disposable plans. Code and tests carry the solution.**

```text
Needs ← referenced by → Changes → contain Tasks
durable                 disposable on completion and review
```

Needs preserve actors, desired outcomes, observable acceptance, and genuine
constraints. Changes hold temporary design and coordination; tasks organize their
execution. After review, useful knowledge lives in needs and the repository, and
the change can disappear. Current needs remain binding after delivery so the next
feature does not quietly undo what the previous one accomplished.

OW takes inspiration from [Spec Kit](https://github.com/github/spec-kit) and
[OpenSpec](https://github.com/Fission-AI/OpenSpec), centering durable needs and
bounded agent context. OpenWish **0.6.1** uses **artifact schema 3**.

## Get started

Requires Python 3.11+. The runtime has **no third-party dependencies**.

```sh
uv tool install openwish
cd /path/to/your/product
ow init
```

If previously installed and attempting to upgrade, use `uv tool upgrade`.

```sh
uv tool upgrade openwish
```

For a source checkout, use `uv tool install .`. Both `ow` and `openwish` invoke
the same CLI; `ow` is canonical in examples. Run `uv tool update-shell` if needed.

`ow init` offers a terminal multi-select for **OpenCode, Claude Code, Codex, and
generic Agent Skills**. Arrow keys move, Space toggles, Enter applies, A toggles
all, and Q/Esc cancels. Existing harnesses are preselected. Basic terminals use
numbered selection. Automation uses explicit selections:

```sh
ow init --harness opencode claude codex
# Equivalent: ow init --harness opencode --harness claude --harness codex
```

Codex and generic Agent Skills share `.agents/skills`; selecting both installs
one copy. One product/domain per repository, including a monorepo, is the default.

In OpenCode or Claude Code:

```text
/onboard
/ow-propose Let operations reconcile this month's transactions without copying rows.
```

Or explicitly delegate final acceptance for this work:

```text
/fast-forward Let operations reconcile this month's transactions without copying rows.
```

Fast-forward performs the same design, implementation, verification, and AI review
without approval prompts. It still requires genuine blocking clarification, access,
or manual observations, and does not apply to unrelated future changes.

## The workflow

OW is opt-in. Installing skills does not require using them for every edit.
See [Workflows](docs/workflows.md) for greenfield onboarding, brownfield onboarding,
and the change lifecycle, with step-by-step guidance and vertical diagrams.

**Routine work:** inspect → implement → verify → report. Clear, localized,
reversible work within existing intent needs no change file, new need, or final
acceptance ceremony.

**Substantive work:** scope reviewable increments, then prepare design and tasks for
each selected change:

```text
Ask → Identify needs → Align design and engineering → Plan
                                                       ↓
                        Human reviews ← Implement ↔ AI review
                              ↓
                     Close and dispose change/tasks
```

A clear instruction to implement already authorizes its scope. Clarify material
uncertainty and consequential choices; respect plan-only requests. Technical plan
repairs within that scope require no repeated permission. Execution continues
through verification and remediation, including independent tasks around manual
blockers. Readiness reports prerequisites, not permission.

Default structured work retains final human review. Explicit fast-forward
delegates acceptance for the selected change. There are no stage gates or
authorization receipts.

**Large work:** one ask may need many changes. Define what each increment delivers
now, preserves, defers, and how its result can be accepted while later work waits.
Detail the next executable increments; retain future candidates as concise open
changes when a resumable plan is requested. Shared code and sequential dependencies
do not by themselves require one change. Tasks expose real completion boundaries;
a short list must not hide whole subsystems. Reconcile growing scope and stale
blockers before resuming. See [Planning large work](docs/workflows.md#planning-large-work).

| Skill | Responsibility |
| --- | --- |
| `ow-propose` | Reuse or revise durable needs; scope useful changes |
| `ow-align` | Inspect code/tests and align working design with all current needs |
| `ow-plan` | Prepare lightweight tasks within a disposable change |
| `ow-implement` | Execute, verify, and continue independent work around blockers |
| `ow-review` | Review outcomes and regressions; present results and close accepted work |
| `ow-consolidate` | Preserve useful knowledge and dispose closed changes/tasks |
| `ow-fast-forward` | Run through review and disposal under explicit delegation |
| `ow-onboard` | Infer right-sized needs, assess architecture, and propose useful refactoring for approval |

### Harness invocation

| Harness | Initialization | Invocation |
| --- | --- | --- |
| OpenCode | `ow init --harness opencode` | `/ow-propose`, `/fast-forward`, `/onboard` |
| Claude Code | `ow init --harness claude` | `/ow-propose`, `/fast-forward`, `/onboard` |
| Codex | `ow init --harness codex` | `$ow-propose`, `$ow-fast-forward`, `$ow-onboard` |
| Other Agent Skills hosts | `ow init --harness generic` | Host-specific selection |

Canonical skills are shared across hosts; adapters contain no separate process logic.

## What persists

| Information | Home and lifetime |
| --- | --- |
| Actors, outcomes, acceptance, constraints | Durable `openwish/needs/N-001.md` |
| Implemented behavior | Source code |
| Executable contracts and regression checks | Tests, types, schemas |
| Responsibilities and dependencies | Repository layout and interfaces |
| Useful rationale and operational knowledge | Nearby comments or ordinary repository docs |
| Working purpose, approach, verification plan | Disposable `openwish/changes/C-001/change.md` |
| Task progress and latest review | Disposable files inside the same change |

Needs are the only mandatory durable OW product knowledge. Tool configuration,
policy, and integration bookkeeping support the workflow. No persistent spec/epic
hierarchy, need execution sidecars, or OW archive is required.

Need currency is `current` or `retired`. Needs have no execution status: several
changes can improve the same outcome, and one change can serve several needs.
Closing a change neither retires a need nor proves its complete satisfaction.
`confirmed_at` records actual human confirmation; inferred intent stays unconfirmed.

Keep implementation detail out of needs. For example, another export format
usually improves an existing reconciliation outcome; auditor accountability may
justify a separate need. Compare actor, outcome, and acceptance before adding one.

Prefer functional cores, explicit effects, cohesive modules, and clear dependency
direction. Code explains what is implemented; needs supply the independent intent
against which code and tests are reviewed.

OW's shared architecture rubric asks whether behavior is discoverable, rules have
clear owners, dependencies and effects are explicit, tests check outcomes, and
complexity earns its cost. Greenfield work starts with a representative end-to-end
slice. New asks reassess affected boundaries. Brownfield onboarding recommends
retaining satisfactory structure or proposes a bounded refactor with evidence,
cost/risk, and verification, seeking approval before that additional scope.

Need size follows independent value, not implementation effort. Split outcomes
that can be accepted or retired separately; merge duplicate intent without losing
constraints. Optional reasoned `requires`/`constrains` relations live on needs;
`ow graph` derives their links without another durable registry. All current needs
remain binding, including those with no recorded relationships.

Tests and manual procedures enable fresh evidence rather than certify historical
runs. OW retains no permanent delivery ledger. Keep selected rationale and useful
operational facts, rather than copying disposed plans/reviews into documentation.

Verification is strategic: reuse small, fast checks of stable outcomes, important
decisions, and consequential boundaries. Add tests for real gaps, rather than every
function or incidental wording/layout change. Test exact details when they are
actual contracts; cover credible costly failures without pursuing speculative edge
matrices or unrequested coverage percentages. Retain tests for lasting obligations
and discard temporary probes after preserving useful findings. Report what was
checked and what remains uncertain.

## CLI

The CLI handles deterministic storage, validation, scheduling, and cleanup. The
coding harness supplies reasoning and code execution; OW makes no model API calls.

```sh
ow new need N-001 --title "Monthly reconciliation"
# Fill actor, outcome, acceptance, and genuine constraints in the need.
ow new change C-001 --title "Local export" --need N-001
# Fill the working approach and tasks; no separate spec or epic.
ow context C-001
ow ready C-001 --json
ow check
```

Tasks have concrete acceptance, local status, and optional prerequisites within
their change. List order guides execution; dependencies determine readiness.
Completed task evidence stays until the parent change closes.

After implementation and actual verification:

```sh
ow record-review C-001 --summary "Monthly reconciliation no longer requires copying rows" \
  --check "Representative export/import: passed" --covered-need N-001
ow summary C-001
# After human review and acceptance:
ow close C-001 --by human
# Once useful knowledge is preserved in needs, code, tests, or ordinary docs:
ow clean C-001
```

Include all `review_needs` from `ow context C-001` with repeated `--covered-need`
flags. Assess every current need; run relevant checks and explain unaffected
constraints. A passing review requires completed tasks. Changes to its inputs
make it stale and require refreshed verification before closure. The CLI cannot
establish semantic correctness or authenticate a human conversation.

Explicit delegation uses `--fast-forward` when creating the change, or
`ow mode fast-forward C-001`; close with `--by fast-forward`. It preserves evidence
requirements and does not manufacture human confirmation.

`ow clean` removes only known files of closed changes after preflighting the full
selection. Unknown files are preserved. Git can hold history; future maintenance
should work from needs and the repository without resurrecting old plans.

```sh
ow status --json                    # needs, changes, task progress, review freshness
ow graph N-001 --json               # recorded incoming/outgoing intent relationships
ow context                          # all current intent, without truncation
ow context N-001                    # plus related changes
ow ready                            # ready tasks and blockers across active changes
ow summary N-001                    # desired outcome and retained work/results
ow check --json                     # schema, references, dependencies, size budgets
```

`--root PATH` works before the subcommand; otherwise roots are discovered from the
current directory and parents. See `ow --help` and the installed `openwish/artifacts.md`.

## Small artifacts, complete intent

- OW artifacts: **under 500 lines each**.
- All current needs together: **under 500 lines**, default **6,000 estimated tokens**.
- Source: **under 500 nonblank LOC soft target**, **under 1000 LOC hard maximum**.
- Exact-path data/low-complexity exceptions never relax OW artifact limits.
- Routine verification should finish within **five minutes**; identify necessary
  slower checks and report missing observations honestly.
- Replace latest summaries and dispose completed work rather than growing journals.

The CLI warns near current-needs budgets. Consolidate on semantic overlap and
poor granularity too, not just size. Status exposes cleanup candidates, pending
acceptance, blocked/manual work, and retired needs. Disposal is normal completion;
report deferrals and reconcile abandoned-looking work explicitly. These lifecycle
controls do not impose a total-file cap or permit deleting unfinished work.

## Updating integrations

For schema-3 projects:

```sh
uv tool upgrade openwish
ow init
```

Before v1.0.0, OW supports only its current schema and keeps breaking changes
simple, without migration tooling or legacy compatibility.

Installation upgrades older integration files, preserves equal versions and local
edits, and asks before downgrades. Noninteractive downgrades fail before writes.
Version stamps and `openwish/installation.json` track ownership. Unversioned files
without an installation record are preserved with an error.
Reinitialization preserves project-owned configuration, policy, needs, and work.
Deselected harnesses are not uninstalled.

## Design and contribution

- [Product requirements](docs/product.md)
- [Framework design](docs/design.md)
- [Artifact reference](src/openwish/assets/artifacts.md) and [workflow policy](src/openwish/assets/policy.md)
- [Changelog](CHANGELOG.md) and [release procedure](docs/releases.md)
- [Contributing](CONTRIBUTING.md)

```sh
PYTHONPATH=src python3 -m openwish --help
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

This repository is developed directly. Shipped skills live in
`src/openwish/assets/skills/`; tests exercise OW in temporary projects. Structural
checks complement semantic skill evaluation and hands-on harness use. MIT licensed.
