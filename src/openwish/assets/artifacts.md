# OW artifact reference — schema 3

Needs are the only mandatory durable product knowledge. Changes and their tasks
are temporary execution context. Markdown uses TOML frontmatter between `+++`
lines. Routine work within clear intent may proceed without execution records.

```text
openwish/
  config.json                 # schema 3, product, context/source budgets
  installation.json           # harness installer bookkeeping
  policy.md                   # project-owned workflow guidance
  artifacts.md                # this reference
  needs/N-001.md              # durable intent
  changes/C-001/change.md     # temporary purpose, approach, verification plan
  changes/C-001/tasks.json    # local work checklist and optional dependencies
  changes/C-001/review.json   # one latest result; created by record-review
src/                         # implementation and discoverable module boundaries
tests/                       # executable checks against expected outcomes
docs/                        # optional useful rationale and operational guidance
```

Configuration and installed guidance support the tool; they are not additional
product artifact layers. There are no specs, epics, need state sidecars, or gates.

## Needs

Create with `ow new need N-001 --title "Monthly reconciliation"`, then fill in:

```toml
+++
id = "N-001"
title = "Monthly reconciliation"
currency = "current"
actor = "Operations staff"
outcome = "Reconcile monthly transactions without copying records."
acceptance = ["Representative reconciliation completes without retyping rows."]
confirmed_at = ""
+++
```

Use the body for genuine constraints and essential intent rationale. All current
need content enters global context. `confirmed_at` is empty for inferred intent
and an ISO date only after actual human confirmation.
Currency is `current | retired`. Needs have no implementation status, mode,
reopen cycle, copied change links, or approval state. Retiring a need changes intent.

Optional reasoned links live on their source need, in the same TOML header:

```toml
# On N-002, the local-only privacy need:
relations = [
  {kind = "constrains", need = "N-001", reason = "Reconciliation must keep raw records on-device."},
]
```

Each inline table has exactly `kind`, `need`, and nonempty `reason`. `requires`
means the source outcome needs the target outcome; `constrains` means the source
limits acceptable solutions for the target. Targets must exist; self-links and
duplicate kind/target pairs are invalid. Current sources must target current needs;
retired sources may retain historical links. Semantic cycles are allowed and have
no effect on task scheduling. Do not infer links from shared modules or changes.

`ow graph --json` derives all retained nodes (with currency) and recorded edges.
`ow graph N-001 --json` returns incoming/outgoing edges and their endpoints, not
transitive impact. There is no graph file or semantic analysis cache. All current
need content, including relation reasons, enters context and review freshness.
Reassess links on intent revisions and consider possible new relationships; missing
edges never exempt current needs from review. Reconcile links before deleting IDs.

Use one coherent valuable outcome per need. Formats/modules/tasks are usually too
small; bundles that can be accepted or retired independently are too broad. Compare
actor/outcome/acceptance before adding a need; preserve constraints during consolidation.

## Changes

```sh
ow new change C-001 --title "Local transaction export" --need N-001 --need N-002
```

Each `--need` references an existing need motivating the change. One change can
serve many needs; one need can have many changes. Other current needs remain
regression constraints. Use a fresh change ID for follow-up work; IDs need only be
unique in the working tree, but avoiding historical reuse makes Git easier to read.

```toml
+++
id = "C-001"
title = "Local transaction export"
needs = ["N-001", "N-002"]
status = "open"
mode = "default"
+++
```

The body explains **purpose**, **approach**, and **verification** for this bounded
improvement. Keep it concise and revise it when the working design changes. Source
and tests carry the resulting implementation; the change need not survive delivery.

Status is `open | in-progress | review | closed`. Edit `in-progress` when work
starts. `record-review` sets `review` for a pass and `in-progress` for blocked
findings. `close` records `closed`, `closed_by`, and an ISO `closed_at` timestamp.
Closed changes are historical, not live claims about subsequent code revisions.

Mode is `default | fast-forward`. Explicitly requested delegation can use
`--fast-forward` at creation or `ow mode fast-forward C-001`. Mode changes stale
the pending review. Each new change defaults to normal human review independently.
There is no command granting implementation authority: use actual conversation
instructions, honor plan-only scope, and clarify material decisions when needed.

## Tasks

Edit `changes/C-001/tasks.json`:

```json
{
  "tasks": [
    {
      "id": "C-001/T-001",
      "title": "Export the selected month's transactions",
      "status": "open",
      "acceptance": "Export contains exactly the selected month's records.",
      "depends_on": [],
      "kind": "agent",
      "files": ["src/transactions/export.py"],
      "evidence": ""
    }
  ]
}
```

Required fields: `id`, `title`, `status`, `acceptance`. Optional fields default to
`depends_on = []`, `kind = "agent"`, `files = []`, and `evidence = ""`.
`done` requires nonempty direct evidence. Status is
`open | in-progress | blocked | done`; kind is `agent | manual`.

Task IDs are qualified by their owning change. Dependencies must reference tasks
within that same change and form an acyclic graph. List order is the scheduling
preference; prerequisites control readiness. There are no global group/order
pairs. Independent work continues while a manual observation or blocked task waits.
For tightly coupled cross-change work, combine the tasks into one bounded change.
Otherwise coordinate changes against already delivered code and interfaces.

Keep completed task results until the change closes. An empty tasks array is valid
for verification-only work; it does not excuse missing review or actual checks.

## Review, closure, and disposal

```sh
ow context C-001
ow ready C-001
ow check
ow record-review C-001 --summary "Monthly reconciliation no longer needs row copying" \
  --check "python -m unittest tests.test_export: 6 passed in 0.4s" \
  --covered-need N-001 --covered-need N-002
ow summary C-001
# After the human actually reviews and accepts the results:
ow close C-001 --by human
# After ensuring useful knowledge lives in needs, code, tests, or ordinary docs:
ow clean C-001
```

Include all `review_needs` from the context manifest, including current needs
outside the change's purpose. Coverage means assessing intent and regressions;
record actual relevant checks and explain why unaffected constraints remain safe.
The CLI checks structure, not whether an agent's reasoning or evidence is truthful.

Use `--verdict blocked` for unresolved findings. A passing review requires all
tasks done and direct results. Its fingerprint covers current/linked needs, the
working approach, task definitions/results, policy/config, and Git-visible
repository content outside `openwish/`. Non-Git projects use filesystem discovery.
Ignored/generated content is outside that snapshot; record relevant external
observations honestly. Changed inputs require refreshed verification before closure.

Default closure requires actual human acceptance. Explicit fast-forward uses
`ow close C-001 --by fast-forward` after the same checks; it does not claim human
review. Neither form edits needs or confirms that an entire need is fully delivered.

`ow clean` only removes closed changes' known files (`change.md`, `tasks.json`,
`review.json`). It preflights all selected changes and preserves unknown files and
symlinks. Git may hold history; there is no OW archive or permanent review ledger.
Retain unresolved work. A closed change remains removable after later repository
edits because its accepted review is historical.

## Inspection and installation

```sh
ow status --json
ow graph N-001 --json              # recorded incident intent links and their reasons
ow context                        # every current need, without truncation
ow context N-001                   # plus linked changes and review scope
ow ready                          # all active changes; accepts need/change IDs
ow summary N-001                  # outcome and any retained execution evidence
ow check --json
ow check --artifacts-only
```

`--root PATH` works before the subcommand; otherwise OW discovers project roots
from the current directory and parents. `check`, `status`, and `ready` support JSON.
Schema mismatches fail before writes. Only the current schema is supported.

Run `ow init` for a harness multi-select, or `ow init --harness opencode claude`
for explicit selection. Reinitialization preserves project-owned knowledge and
policy, upgrades older integrations, leaves equal versions untouched, and asks
before downgrades. `ow skills --harness NAME` uses the same version-aware installer.

Config contains `version: 3`, `product`, `needs_token_budget` (default 6000), and
`code_exceptions`. Each exception has an exact `path`, a `kind` of `data` or
`low-complexity`, and a meaningful `reason`. OW artifacts stay under 500 lines;
source exceptions do not relax artifact or global current-needs limits. Closed
changes produce a cleanup reminder rather than an arbitrary working-set limit.

Status includes `retention`: `cleanup_candidates` (closed), `awaiting_acceptance`
(review-state; check freshness), `blocked_changes` (blocked or pending manual tasks),
and `retired_needs`. These are derived attention groups, not deletion permissions.
Near-budget context warnings prompt semantic consolidation before a hard failure.
Per-file limits do not cap total retained material; normal completion includes
disposal or explaining its deferral. Retired needs require a deliberate retention
decision and reconciliation of incoming relations and retained change references.

## Durable knowledge and evidence

Retain strategically placed, fast tests of stable outcomes, important decisions,
and consequential boundary contracts. Reuse existing protection before adding
checks; temporary experiments need not become permanent regression tests. Avoid
incidental text/layout snapshots or private-call assertions unless the asserted
detail is itself a real contract. Credible costly failures still merit focused
checks; test counts, speculative edge matrices, and unrequested coverage percentages
are not substitutes for meaningful evidence. See the installed `ow-plan` skill's
Strategic verification guidance.

Only needs are mandatory durable OW product knowledge. Source, types, schemas,
tests, and selective comments/docs explain the implemented solution. Keep useful
manual verification procedures and expected outcomes where maintainers can find
them. Run-specific results, working assessments, and closure provenance disappear
with a cleaned change; tests enable fresh evidence rather than certify a past run.
Git history is optional. Historical proof belongs in product data when a genuine
need requires it, not in a framework-wide evidence ledger.

Config, policy, this reference, installed skills/adapters, and the installation
manifest support the tool. They are not delivery evidence. Docs are for selected
lasting facts/rationale, not copies of every discarded approach or review.
