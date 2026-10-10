# OpenWish (OW)

**Need-Driven Development for humans and coding agents.**

Humans ask. AI identifies needs, aligns solutions, plans, implements, and reviews.
Humans review the results. Current needs remain binding after implementation,
so the next feature does not quietly undo what the previous one accomplished.
**OW operates on needs.** Asks stay in conversation; existing needs are revised
or reopened, and distinct outcomes become new needs. There are no change records.

OpenWish takes inspiration from [Spec Kit](https://github.com/github/spec-kit)
and [OpenSpec](https://github.com/Fission-AI/OpenSpec), with durable needs and
bounded agent context at the center of the workflow.

## Get started

Requires Python 3.11+. The runtime has **no third-party dependencies**.
After the first PyPI release, install the CLI with [uv](https://docs.astral.sh/uv/):

```sh
uv tool install openwish
cd /path/to/your/product
ow init
```

Until that first publication, install from a checkout using `uv tool install .`.
The package name is **openwish** and the installed command is **ow**. If your
shell cannot find `ow`, run `uv tool update-shell` and open a new terminal.

`ow init` opens a terminal multi-select for **OpenCode, Claude Code, Codex, and
generic Agent Skills**. Move with the arrow keys, toggle with Space, and press
Enter to initialize all selected harnesses. Press A to toggle all or Q/Esc to
cancel. Installed harnesses are preselected on subsequent runs. Basic or narrow
terminals use a numbered multi-select instead.

To select harnesses directly, including in scripts:

```sh
ow init --harness opencode claude codex
# Equivalent: ow init --harness opencode --harness claude --harness codex
```

Without an interactive terminal, specify `--harness`. Codex and generic Agent
Skills share `.agents/skills`, so selecting both installs one copy. One
product/domain in one repository, including a monorepo, is the default.

### Updating installed skills

Upgrade the CLI, then run `ow init` again in your project:

```sh
uv tool upgrade openwish
ow init
```

Initialization installs missing integrations and compares each selected file's
installed version with the CLI's bundled version:

| Installed version | Behavior |
| --- | --- |
| Older | Overwrite with the bundled version, including any local edits |
| Same | Leave the file untouched, including local edits and timestamps |
| Newer | Ask before downgrading; keeping the newer files is the default |

Downgrades require explicit terminal confirmation; scripts fail before writing
if confirmation is needed. Declining keeps newer files while other selected
installs/upgrades proceed. Deselection does not uninstall existing integrations.

Version stamps and `openwish/installation.json` track installed skills and command
adapters. Exact unversioned v0.2 templates are recognized and upgraded; unknown
unversioned files are preserved with an actionable error. Existing needs, specs,
project configuration, policy, and knowledge are preserved when reinitializing.

In **OpenCode**, start with:

```text
/onboard
/ow-propose Let operations reconcile this month's transactions without copying rows.
```

Or explicitly choose the uninterrupted workflow:

```text
/fast-forward Let operations reconcile this month's transactions without copying rows.
```

`/fast-forward` skips **all OW confirmations and approvals**, including final
acceptance, for the selected needs' current implementation revisions. It still performs alignment, planning, implementation,
verification, and AI review. It asks only for genuinely blocking clarification,
access, or manual observations, after continuing any independent ready work.

## The workflow

```text
Ask → Propose → Align → Plan → Implement ↔ Review → Accepted results
         │        │       │                    │
       confirm  approve authorize         explicit acceptance
        needs    design implementation       in default mode
```

Propose automatically enters Align after need confirmation. Align enters Plan
after design approval. Plan asks whether to implement. Implementation continues
through ready work and AI review/remediation; it does not stop for approval of
each task or epic. Human acceptance is requested once available work is finished.

| Skill | Responsibility |
| --- | --- |
| `ow-propose` | Distill an ask into new or revised needs; clarify material intent |
| `ow-align` | Reconcile all current needs and affected implementations; update specs/designs |
| `ow-plan` | Inspect code and plan minimal epics and correctly ordered task groups |
| `ow-implement` | Execute ready work until completion or an actual human blocker |
| `ow-review` | Check needs and regressions, remediate, and present compact results |
| `ow-consolidate` | Promote durable knowledge and remove completed execution detail |
| `ow-fast-forward` | Run the full workflow without confirmation/approval prompts |
| `ow-onboard` | Infer candidate needs and map an existing codebase for confirmation |

### Harness invocation

| Harness | Initialization | Invocation |
| --- | --- | --- |
| OpenCode V2 | `ow init --harness opencode` | `/ow-propose`, `/fast-forward`, `/onboard` |
| Claude Code | `ow init --harness claude` | `/ow-propose`, `/fast-forward`, `/onboard` |
| Codex | `ow init --harness codex` | `$ow-propose`, `$ow-fast-forward`, `$ow-onboard` |
| Other Agent Skills hosts | `ow init --harness generic` | Host-specific skill selection |

Add or update integrations later with `ow init`, or `ow skills --harness NAME ...`.
Both commands use the same version-aware installer. The same workflow is used
everywhere; command adapters do not contain divergent process logic.

## Needs are first-class

Each need records its actor, desired outcome, observable
acceptance, human confirmation date, and latest verified implementation date.

Two independent state dimensions avoid confusing delivery with relevance:

- **Currency:** `current`, `retired`.
- **Implementation:** `open`, `in-progress`, `review`, `approved`.

A `current/approved` need still constrains every future design. Fast-forward
acceptance records its origin; it is not mislabeled as human confirmation.
An inferred need starts unconfirmed, and existing code is not assumed verified.

Spec designs contain authoritative many-to-many references to needs. Specs describe
entities, UI modules, or cross-cutting capabilities; epics/tasks organize bounded
implementation. Containment and prerequisite relationships are distinct.

`ow reopen N-001` resumes work under the same ID and resets authority to default.
Only an explicit new fast-forward request enables it for the reopened revision.

### Human-facing communication

Propose confirms only the need interpretation. Later approvals are discussed when
their stage is reached. Clarifications use numbered questions and two or three
lettered choices, with `(Recommended)` before the preferred choice text:

```text
1. N-001 already provides local monthly trends. Uploading raw records would
conflict with its local-only constraint. What should I do?
  A. (Recommended) Keep N-001 as-is. No new need or product modification.
  B. Add third-party upload and keep trends local. Revise N-001's allowed-domain exception.
  C. Add third-party upload and computation with local viewing. Revise N-001's constraint.
```

Final updates lead with need → spec → outcome, followed by verification and any
blocker. `ow summary N-001` provides that context; reporting only task IDs is insufficient.

## Small artifacts, complete intent

- OW-managed knowledge and planning: **under 500 lines per artifact**.
- All current needs together: **under 500 lines**, default **6,000 estimated tokens**.
- Source: **under 500 LOC soft target**, **under 1000 LOC hard maximum**.
- Data formats are exempt from source limits. Low-complexity source exceptions
  are exact paths with a rationale; they do not exempt OW knowledge artifacts.
- Routine verification should finish within **five minutes**. Necessary slower
  checks are explicit, and missing verification never counts as success.
- Latest summaries replace earlier ones. Git holds history; there is no required
  append-only journal, growing evidence archive, or duplicate needs ledger.

`ow context` derives the needs register and related spec statuses from authoritative
records. `ow context N-001` also lists affected contracts and work to retrieve.
Agents read detailed designs only for the work at hand.

## CLI

The CLI handles deterministic operations. The coding harness supplies reasoning,
code execution, and semantic review; OW does not make model-provider API calls.

```sh
ow status                           # needs, linked specs, implementation progress
ow context                          # all current needs, including approved ones
ow context N-001 N-002              # plus affected spec/epic IDs
ow check                            # schema, links, cycles, ordering, size budgets
ow ready N-001 N-002                # ready work with spec/need context and blockers
ow summary N-001                    # outcomes, specs, work, and verification
```

Artifact scaffolding and decision recording are available to agents and humans:

```sh
ow new need N-001 --title "Monthly reconciliation"
ow new spec S-001 --title "Transaction export"
ow new epic E-001 --title "Export implementation"
# Fill templates and references before checks or gates.
ow gate needs N-001 --by human
ow reopen N-001                     # reuse a need when further work is necessary
```

Gates are revision-bound: changed need intent invalidates downstream authority,
while updating task progress does not. Reviews are bound to the plan and repository
content. The CLI records human decisions supplied by the harness; it does not
authenticate a conversation or establish semantic correctness on its own.

`--root PATH` works before the subcommand; otherwise the project root is discovered
from the current directory and its parents. `check`, `status`, and `ready` support
`--json`. See `ow --help` and the installed `openwish/artifacts.md` for all commands.

## Design and contribution

- [Framework design](docs/design.md)
- [OpenWish's own current needs](openwish/needs/)
- [Artifact format](src/openwish/assets/artifacts.md)
- [Workflow policy](src/openwish/assets/policy.md)
- [Contributing and verification](CONTRIBUTING.md)
- [Publishing releases to PyPI](docs/releases.md)

Run directly from a source checkout without installing:

```sh
PYTHONPATH=src python3 -m openwish --help
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

OpenWish is an initial `0.3.1` implementation using artifact schema 2. The v0.1
prototype's change records are superseded; see [migration guidance](docs/migration.md).
Integration files follow current
host documentation; deterministic checks do not substitute for hands-on harness
workflow validation. Licensed under [MIT](LICENSE).
