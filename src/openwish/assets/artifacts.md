# OW artifact reference

OW operates on need IDs. Asks stay in conversation. Stable IDs are `N-001`,
`S-001`, and `E-001`; Markdown records use TOML headers between `+++` lines.
These records support structured work. Routine, clear changes within existing
intent need no new records, reopen cycle, or gate receipts; see `policy.md`.

```text
openwish/
  config.json                 # product and budgets (schema version 2)
  installation.json           # installed harnesses and per-file OW versions
  policy.md                   # workflow and human communication
  artifacts.md                # this reference
  needs/N-001.md              # durable outcome and lifecycle
  needs/N-001.state.json      # current implementation revision and decisions
  needs/N-001.review.json     # latest direct verification results
  specs/S-001/spec.md         # behavioral contract, prerequisite/parent links
  specs/S-001/design.md       # technical design and authoritative need references
  epics/E-001/design.md       # bounded implementation increment, linked to specs
  epics/E-001/tasks.json      # ordered, verifiable work
  knowledge/environment.md    # current operational facts
```

Run `ow init` for a terminal harness multi-select or `ow init --harness opencode
claude` for explicit selection. Re-running installs missing skills, overwrites
older versions, preserves equal versions, and asks before downgrading newer ones.
Existing project knowledge is preserved. `installation.json` is a bounded current
inventory, not a history; generated skills and adapters also carry version stamps.

## Needs

Create with `ow new need N-001 --title "Monthly reconciliation"` and fill in:

```toml
+++
id = "N-001"
title = "Monthly reconciliation"
currency = "current"
implementation = "open"
actor = "Operations staff"
outcome = "Reconcile a month's transactions without manually copying records."
acceptance = ["Representative reconciliation completes without retyping rows."]
confirmed_at = ""
verified_at = ""
+++
```

Use an optional short body for essential constraints. Everything in a current
need enters the global context. Do not add an `ask` field or duplicate spec links.

If a need requires more implementation, run `ow reopen N-001`. Its ID and history
survive; implementation becomes open, revision increases, gates reset, and mode
returns to default. Reopening a retired need also reactivates it, so confirm that
intent first. Existing task results remain evidence; Plan assesses what now remains.

## Specs and need references

`ow new spec S-001 --title "Transaction export"` creates both files. The contract
header in `spec.md` contains `id`, `title`, `implementation`, `depends_on = []`,
and `parent = ""`. The body states behavior and observable acceptance scenarios.

The **design** contains the need references:

```toml
+++
id = "S-001"
needs = ["N-001"]
+++
```

Below that header, explain how the design satisfies N-001 and preserves affected
constraints. The reference is authoritative here; the CLI derives the need's spec
list and all task lineage from it. Designs can reference multiple needs.
Prerequisite and containment graphs are separate and acyclic.

## Epics and tasks

`ow new epic E-001 --title "Export implementation"` creates `design.md` with
`id`, `title`, and `specs = ["S-001"]`. Describe only this bounded increment.
Split larger work into multiple task groups or epics; retain durable design in specs.

Add `needs = ["N-001"]` to the epic header to select its execution scope. This
must be a nonempty subset of the needs referenced by its spec designs. It selects
which outcomes this increment implements; it does not replace the designs' full
regression coverage. If omitted, all linked needs are selected for compatibility.
Use this field instead of splitting a shared spec just to avoid unrelated gates.

```json
{
  "tasks": [
    {
      "id": "E-001/T-001",
      "title": "Export the selected month's transactions",
      "group": 1,
      "order": 1,
      "depends_on": [],
      "kind": "agent",
      "status": "open",
      "files": ["src/transactions/export.py"],
      "acceptance": "Export contains exactly the selected month's records.",
      "evidence": ""
    }
  ]
}
```

Task status is `open | in-progress | blocked | done`; kind is `agent | manual`.
Task IDs are globally qualified, e.g. `E-002/T-001` can depend on `E-001/T-001`.
Group/order pairs are unique within work supporting a need, including across epics.
Prerequisites must have lower pairs; independent needs may reuse ordinal pairs.
`done` needs concise direct evidence. Do not invent human observations.

## Need-owned decisions and review

A need's state contains only `revision`, `mode`, `no_work_reason`, and `gates`.
It has no title, ask, independent identity, stored need group, or copied work list.
Specs are derived from design references; epic execution scope selects tasks.
Missing state for an imported need defaults to revision 1 with no approvals.

```sh
ow context N-001 N-002
ow authorize N-001 N-002 --by human
ow ready N-001 N-002
```

`authorize` preflights needs, alignment, and implementation together before
writing receipts. Use it after preparing the scope, design, and plan, when an
actual human instruction or combined decision authorizes them. It does not record
final acceptance. Preparation itself requires no gate receipts. If authority is
missing, ask one combined question rather than three restatements of the request.
Plan-only requests do not authorize implementation. Lower-level `ow gate needs`,
`ow gate align`, and `ow gate implement` remain available for intentional staged
collaboration. Refreshing receipts for technical repairs within the authorized
scope does not require asking the same question again.

The IDs select needs for that command; they do not create a persistent grouping.

For explicit fast-forward, use `ow new need ... --fast-forward`, `ow reopen
N-001 --fast-forward`, or `ow mode fast-forward N-001 N-002` for already-open
needs. Then use `ow authorize ... --by fast-forward`. Changing mode invalidates
authority; reopening never inherits fast-forward implicitly.

If existing implementation already satisfies a need, set its state's concise
`no_work_reason` before alignment rather than inventing epics. This does not waive
existing unfinished tasks or verification. Redundant asks require no records at all.

```sh
ow record-review N-001 --summary "Monthly reconciliation no longer requires copying rows" \
  --check "python -m unittest tests.test_export: 6 passed in 0.4s" --covered-need N-001
ow summary N-001
ow gate review N-001 --by human
ow approve N-001
```

Include every ID in `ow context N-001`'s `review_needs` with repeated
`--covered-need` flags. They include affected adjacent current needs. One command
can review multiple selected needs; each keeps its own latest bounded result.
Use `--verdict blocked` for unresolved findings. Passing review requires all
relevant tasks done and is bound to plan, source content, and task evidence.

`approve` preserves currency. A shared spec becomes approved only when every
linked current need is approved. `ready` exposes missing authority per task and
continues to list other authorized work. It includes spec titles and the needs
they address. Authority is required for the epic's execution needs, while review
still covers adjacent needs. `summary` provides need → spec → outcome context.

## Bounds and consolidation

Config has `version: 2`, `product`, `needs_token_budget` (6000), `epic_limit` (8),
and `code_exceptions`. A source exception is an exact path with a reason:

```json
{"path": "src/routes.py", "kind": "low-complexity", "reason": "Flat declarative dispatch with no nested logic."}
```

Source data formats are exempt. A `data` exception must name a data-format file.
No exception permits an OW artifact of 500 or more lines.

After completion, promote durable facts and remove obsolete completed epics once
active references and prerequisites are reconciled. Preserve the only historical
copy in Git before removing it. Keep needs, one current state, and one latest
review; never append requests, episodes, or review histories. Retired needs and
their sidecars can leave the working tree once live references are reconciled.
