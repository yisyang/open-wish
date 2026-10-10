# OpenWish framework design

## Core invariant

Every proposed solution is evaluated against all current needs, including those
with approved implementations. Needs define durable outcomes; specs are revisable
contracts; designs select solutions; epics and tasks organize bounded execution.

Asks are transient conversation input. They do not become stored asks, summaries,
or change records. OW creates, revises, and reopens durable needs under stable IDs.
Need selections passed to a command are temporary arguments, not persisted groups.

The framework optimizes for useful software, low regression risk, small context,
and fast remediation. Documentation and automation have to earn their overhead.

## Architecture

The Python 3.11+ CLI uses the standard library. Functional graph/context/validation
operations are separated from filesystem effects. Markdown with TOML frontmatter
holds human-readable intent and contracts. JSON holds small operational records.
TOML parsing uses `tomllib`; there is no bespoke YAML parser or runtime dependency.

| Module | Responsibility |
| --- | --- |
| `storage.py` | Root discovery, safe paths, bounded atomic writes, artifact loading |
| `model.py` | Derived needs view, dependency impact, topological order, ready tasks |
| `validation.py` | Typed artifact contracts, link integrity, cycles, forward dependencies |
| `budgets.py` | Artifact/context limits, Git-aware source discovery, source-size checks |
| `workflow.py` | Need revisions, semantic fingerprints, approvals, review freshness |
| `views.py` | Need → spec → outcome summaries and current implementation status |
| `scaffold.py` | Project initialization and artifact creation |
| `integrations.py` | Version-aware skill installation, manifest, host adapters |
| `versions.py` | OW version stamps and SemVer precedence |
| `terminal.py` | Harness multi-select and downgrade confirmation |
| `cli.py` | Command parsing and concise human/machine output |

Skills handle interpretation, conflict discovery, design, implementation, and
review inside an existing coding harness. The CLI does not dispatch models or
pretend a structural validation pass establishes satisfaction of user needs.

## Authority and modes

Four revision-bound gates represent different human decisions: needs, alignment,
implementation, and final review. Default mode requires explicit decisions.
`fast-forward` records bypass authority for selected need revisions and skips all four
prompts while retaining all four phases and their quality checks.

The CLI records `by=human` or `by=fast-forward`, timestamp, and input fingerprint.
Skills record human authority only after the corresponding explicit decision.
Only human need confirmation advances `confirmed_at`; accepted implementation
verification advances `verified_at`. No process infers confirmation from file reads.

Approval records are bounded slots in each need's state, not an event stream. Replacing an earlier
gate removes downstream gate records. Semantic changes make existing records
stale even when someone edits artifacts directly. Git retains prior decisions.

`ow reopen` preserves the need ID and increments its implementation revision.
It resets authority to default unless fast-forward is explicitly requested again.
State contains only revision, mode, a possible no-work rationale, and gate receipts.
Spec/epic/task associations are derived rather than copied into state.

## Communication

Propose asks only about the current need interpretation, without previewing
later approval gates. Clarifications and confirmations use numbered questions,
two or three A/B/C choices, and `(Recommended)` before the preferred choice text.
Concise effect clauses explain consequences for needs and the product.

Final updates explain the need, the delivering spec, the outcome, and verification.
Spec designs own the authoritative need references. Epics reference specs, and
task lineage is derived from these links so task-level work retains its purpose.

## Revision model

- Needs gate: need ID/revision, mode, project policy/config, all current need
  definitions, and the selected need (including retirement when applicable).
- Alignment gate: needs inputs plus scoped/adjacent specs, designs, and durable
  operational knowledge.
- Implementation gate: alignment inputs plus epic designs and task definitions.
- Review: implementation inputs, task results, latest review, and repository
  content outside the OW knowledge tree.

Implementation statuses, progress evidence, and confirmation/check dates do not
invalidate earlier intent/design authority. Plan changes do. Repository changes
after AI review invalidate review freshness; verification must be refreshed.

Fingerprints are intentionally conservative. Unrelated current-need edits can
invalidate an alignment because all current needs constrain a solution. Accepted
implementation decisions are historical, not evergreen approvals of later code.

## State and execution

Need currency and implementation are independent. Opening a new implementation
does not erase need currency. A regression returns implementation to open or
in-progress. Retiring a need is an intent change, not a task completion action.

Spec prerequisites and containment are separate acyclic graphs. The impact view
includes prerequisites and consumers; semantic adjacency still needs AI review.
Task dependencies form a DAG with explicit global task IDs and unique increasing
`(group, order)` pairs within work supporting each need. Independent needs can
reuse ordinal pairs. The lowest authorized ready task executes first.
A blocked manual task does not prevent an independent later task from executing.

Shared work requires implementation authority for all linked current open needs.
Missing authority is a task-level blocker, so other authorized work still proceeds.
A spec becomes approved only when all linked current needs are approved.

Task states include blocked/done because task execution and need implementation
are different concepts. No implicit skipped or waived task state exists. A manual
observation cannot be completed by changing approval mode.

The agent continues until no authorized ready work remains. It then either
presents indispensable human blockers or the final compact review package.
Review remediation loops back into implementation without an intermediate approval
prompt. Material intent changes return to the appropriate earlier decision.

## Bounded knowledge

Per-artifact hard limits and a global current-needs budget address different
failure modes. All current need content is included; no hidden summary truncation
can remove constraints from global reasoning. The default 6,000-token estimate
uses UTF-8 bytes/3 and is configurable rather than tied to a particular model.

Code uses nonblank physical lines as a conservative cross-language LOC proxy.
Data formats are exempt; exceptional low-complexity source requires an exact
path and rationale. OW knowledge/planning artifacts never inherit source exemptions.

Each need's latest review replaces its previous result. Completed epics
are consolidated after current truths are promoted and live references resolved.
The working set defaults to eight retained epics; Git stores historical detail.

## Integrations

Canonical skill bodies are packaged once, then copied to the selected host's
documented skill directory. OpenCode receives thin command adapters; Claude Code
uses skill commands; Codex uses standard `.agents/skills` discovery. Fast-forward
is explicit-only in hosts that expose invocation control. Its body also checks
explicit authorization so the policy travels across hosts.

`ow init` presents a terminal multi-select when no harness flags are supplied.
Arrow keys move, Space toggles, Enter applies, and Q/Esc cancels before writes.
Previously selected harnesses are preselected. Basic/narrow terminals fall back
to numbered selection. Explicit repeatable `--harness` flags support scripts.
Codex and generic selections share one set of files in `.agents`.

Generated skills carry `metadata.openwish-version`; command adapters and Codex
policy files carry version comments. A bounded `openwish/installation.json`
records harnesses and per-file versions, preserving ownership/version knowledge
if a local edit removes its stamp. A valid file stamp takes precedence over the
manifest. Exact v0.2 templates are recognized by bundled hashes; unknown
unversioned files produce a conflict without partial installation.

The installer preflights every selected harness before writing. SemVer precedence
determines replacement: older files are overwritten, equal versions receive no
writes, and newer files require explicit downgrade confirmation. Build metadata
does not affect precedence. Declining preserves newer files while independent
installs/upgrades proceed. Without a terminal, necessary confirmation fails before
any writes. The manifest retains each file's actual version after mixed outcomes.

Initialization can run again on existing schema-2 projects without rewriting
configuration, needs, specs, policy, or knowledge. It updates selected integration
files only; deselected harnesses are not uninstalled. The CLI and bundled skill
version advance together. Canonical skill content edits require a version bump
to deploy automatically into existing projects.

## Verification strategy

Behavior tests focus on state transitions, stale decisions/reviews, scheduler
dependencies, manual blockers, format budgets, malformed artifacts, and preservation
of user files. End-to-end CLI scenarios exercise both default and fast-forward
workflows in temporary projects. Packaging checks verify skills ship with the CLI.
Pseudo-terminal tests exercise real key input, multiple selections, cancellation,
terminal restoration, and both downgrade decisions. Installer tests check equal
version no-write behavior, upgrades, legacy detection, and multi-harness preflight.

Semantic skill scenarios cover current-stage-only clarification, preserving an
existing need, numbered choices, need/spec final updates, fast-forward approval,
and continuing around human blockers. These
complement deterministic tests; they cannot prove every model will follow a skill.

## Reference influences

- [Spec Kit](https://github.com/github/spec-kit): repeatable process templates,
  principles, phase guidance, and harness integrations.
- [OpenSpec](https://github.com/Fission-AI/OpenSpec): approachable commands,
  lightweight artifacts, and brownfield adoption.
- [OpenCode V2 commands](https://opencode.ai/v2/docs/commands) and
  [skills](https://opencode.ai/v2/docs/skills).
- [Claude Code skills](https://code.claude.com/docs/en/skills).
- [Codex skills](https://developers.openai.com/codex/build-skills).
