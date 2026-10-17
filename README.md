# OpenWish (OW)

**Need-Driven Development for humans and coding agents.**

Humans ask. AI identifies needs, aligns design and engineering, implements, and
reviews. Humans review the results.

**Durable intent. Disposable plans. Code and tests carry the solution.**

```text
Needs ← referenced by → Changes → contain Tasks
durable                 disposable after review
```

Specs grow until nobody trusts them. OW keeps only **needs** durable: who needs
what outcome, how to observe it, and which constraints genuinely limit solutions.
Each **change** holds one increment's temporary design, tasks and review, and is
deleted once its knowledge lives in code, tests, needs or ordinary docs. Current
needs stay binding after delivery, so the next feature does not quietly undo the
last one.

OW takes inspiration from [Spec Kit](https://github.com/github/spec-kit) and
[OpenSpec](https://github.com/Fission-AI/OpenSpec). OpenWish **1.0.0-rc.1** uses
**artifact schema 5**.

## Get started

Requires Python 3.11+, with **no third-party runtime dependencies**.

```sh
uv tool install openwish     # or: uv tool upgrade openwish
cd /path/to/your/product
ow init
```

`ow init` offers a multi-select for **OpenCode, Claude Code, Codex and generic Agent
Skills** (arrows move, Space toggles, Enter applies, A toggles all, Q/Esc cancels).
For automation: `ow init --harness opencode claude codex`. Codex and generic Agent
Skills share `.agents/skills`. Both `ow` and `openwish` invoke the CLI.

Then, in your agent:

```text
/onboard
/ow-propose Let operations reconcile this month's transactions without copying rows.
/fast-forward Let operations reconcile this month's transactions without copying rows.
```

`/fast-forward` does the same design, implementation, verification and review, but
delegates final acceptance of that change to the agent. It still stops for genuine
blocking questions, missing access and manual observations.

| Harness | Invocation |
| --- | --- |
| OpenCode, Claude Code | `/ow-propose`, `/fast-forward`, `/onboard` |
| Codex | `$ow-propose`, `$ow-fast-forward`, `$ow-onboard` |
| Other Agent Skills hosts | Host-specific selection |

## The workflow

OW is opt-in; installed skills never force it on an edit.

- **Every product change** recovers current intent, clarifies only what matters,
  designs, verifies and reviews, in proportion to the ask.
- **Direct delivery** (one result, finished and verified in one session, nothing
  deferred or undecided): no change records, though needs are revised when intent changes.
- **Managed delivery** (several increments, resumption, deferred work, sequencing,
  manual blockers or delayed acceptance): propose → align → plan → implement ↔ review
  → human acceptance → dispose. A clear instruction to implement authorizes its scope;
  plan-only requests stop at the plan; only material intent or scope decisions go back
  to the human. Confirming a need's wording is never a gate.
- **Large work** becomes a sequence of independently reviewable changes, with the
  next one planned in detail.

See [Workflows](docs/workflows.md) for onboarding, large work and the change lifecycle.

| Skill | Responsibility |
| --- | --- |
| `ow-propose` | Reuse or revise needs; size reviewable changes |
| `ow-align` | Working design against all current needs; architecture rubric |
| `ow-plan` | Executable tasks; reconciling plans; strategic verification |
| `ow-implement` | Execute, verify, continue around blockers |
| `ow-review` | Assess all needs; make the change safe to forget; close |
| `ow-consolidate` | Dispose closed changes; compact needs |
| `ow-fast-forward` | Run through review and disposal under explicit delegation |
| `ow-onboard` | Infer needs, assess architecture, propose worthwhile refactoring |
| `ow-assess` | Rate a sequence's readiness, pre-mortem it, queue discovery and questions |
| `ow-core` | OW's own policy and artifact reference, loaded first by every other skill |

## What persists

| Knowledge | Home |
| --- | --- |
| Actors, outcomes, acceptance, structural rules | `openwish/needs/N-001.md` (durable) |
| Detailed rules and tunable values | Rule docs or data that needs reference |
| Implemented behavior | Source code |
| Checks of intent | Tests that mention the need ID they protect (`ow trace`) |
| Module responsibilities | A short header per module; a README at major boundaries |
| Non-obvious rationale, environments and setup | Nearby comments or ordinary docs |
| Working design, tasks, latest review | `openwish/changes/C-001/` (deleted after acceptance) |
| Project rules, engineering-requirements link, review lessons | `openwish/policy.md` (the project's; OW never edits it) |

Needs have no execution status; closing a change does not retire a need or claim it
is complete. `confirmed_at` records that a human confirmed every acceptance criterion;
undecided questions and proposals wait in the need's `open` list. Each fact has one
home, and other files link to it.

**Sequences.** A change can name predecessors with `after`. Successors become
plannable once predecessors pass review (set `successors_wait_for` to `acceptance` to
wait for acceptance instead); acceptance follows the sequence, and `ow ready` lists
what to plan next.

**Safe to forget.** Before a change passes review, every material rule it introduced
has a retained home: product files with independent checks, a need or doc, or another
open change for approved unfinished work. The CLI checks those files exist and keeps
the assessment inside the disposable review.

## CLI

The CLI does deterministic storage, validation, scheduling, freshness and cleanup;
the harness does the reasoning. OW makes no model API calls.

```sh
ow new need N-001 --title "Monthly reconciliation"
ow new change C-001 --title "Local export" --need N-001
ow new change C-002 --title "Scheduled export" --need N-001 --after C-001
ow context C-001                     # all current needs, work state, sized retrieval manifest
ow ready C-001                       # ready tasks, blockers, unplanned changes
ow task C-001/T-001 done --evidence "tests/test_export.py: 4 passed"
ow trace N-001                       # tests and files that mention N-001
ow record-review C-001 --summary "Reconciliation no longer needs row copying" \
  --check "python -m unittest: 12 passed" --handoff /tmp/ow-handoff.json
ow summary C-001                     # need → outcome → evidence; why a review is stale
ow close C-001 --by human            # after actual human acceptance
ow clean C-001 --dry-run && ow clean C-001
ow status --json                     # needs, changes, review state, retention groups
ow graph --json                      # recorded need relations
ow check --json                      # structure, references, size targets
```

Review freshness covers the change, tasks, all current needs, config, project policy, the
handoff and every product file, including submodules. Any edit makes a pending review
stale, and `ow summary` names what changed. Linked needs are always recorded as
affected; `--affected` adds others; every remaining current need is recorded as
assessed and unaffected. See the [artifact reference](src/openwish/assets/skills/ow-core/artifacts.md).

## Size guidance

- Current needs: **24,000 estimated-token soft target** (configurable), never truncated.
- Each OW artifact warns at **8,000 estimated tokens**; source warns at **500 nonblank
  lines**. A `source_hard_limit` is opt-in.
- Routine verification should finish within **five minutes**.

## Updating

```sh
uv tool upgrade openwish
ow init
```

Upgrades older integration files, keeps equal versions and local edits, and asks
before downgrades. Everything under `openwish/` is the project's: OW's own policy and
artifact reference ship in the `ow-core` skill and upgrade with it, while project
policy, needs and work are preserved. Projects use artifact schema 5; `ow init`
migrates schema 4 after a whole-project preflight, moving OW-shipped text out of
`openwish/` and reporting any edited text it keeps. Other schemas are rejected before
any write.

## Design and contribution

- [Product requirements](docs/product.md) and [framework design](docs/design.md)
- [OW policy](src/openwish/assets/skills/ow-core/SKILL.md) and [artifact reference](src/openwish/assets/skills/ow-core/artifacts.md)
- [Skill evaluations](evals/README.md), [changelog](CHANGELOG.md), [releases](docs/releases.md),
  [contributing](CONTRIBUTING.md)

```sh
PYTHONPATH=src python3 -m openwish --help
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

MIT licensed.
