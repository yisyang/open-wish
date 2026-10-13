# OW artifact reference — schema 4

Formats and commands. Workflow guidance lives in `openwish/policy.md` and the skills.
Markdown files use TOML frontmatter between `+++` lines.

```text
openwish/
  config.json                 # schema 4, product name, size targets
  installation.json           # installer bookkeeping
  policy.md                   # project-owned workflow policy
  artifacts.md                # this reference
  needs/N-001.md              # durable intent
  changes/C-001/change.md     # disposable purpose, scope, approach, verification
  changes/C-001/tasks.json    # disposable task list
  changes/C-001/review.json   # latest review, written by ow record-review
```

## Needs

`ow new need N-001 --title "Monthly reconciliation"`, then fill in:

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

Genuine constraints and essential rationale go in the body.
```

- `currency` is `current` or `retired`. All current need content, including relation
  reasons, enters `ow context` and review freshness.
- `confirmed_at` is empty for inferred intent and an ISO date after actual human
  confirmation.
- Optional `references = ["docs/rules.md", "data/catalog.json"]` name existing,
  non-ignored repository files holding detailed rules or data. No symlinks, `..`
  or paths inside `openwish/changes/`. `ow context` lists and sizes them; it does
  not include their content.
- Optional `relations` sit on the source need, one inline table per line:

  ```toml
  relations = [
    {kind = "constrains", need = "N-001", reason = "Raw records must stay on-device."},
  ]
  ```

  `requires`: the source outcome needs the target outcome. `constrains`: the source
  limits acceptable solutions for the target. Each table has exactly `kind`, `need`
  and a nonempty `reason`. Targets must exist; no self-links or duplicate kind/target
  pairs; current needs may only target current needs. Cycles are allowed.

## Changes

```sh
ow new change C-001 --title "Local transaction export" --need N-001 --need N-002
```

```toml
+++
id = "C-001"
title = "Local transaction export"
needs = ["N-001", "N-002"]
status = "open"
mode = "default"
+++
```

The body's template headings (Purpose, Scope, Approach, Verification, Handoff) are
guidance, not a required schema. Scope states **delivers now**, **preserves** and
**defers**; Verification states **exit evidence**.

- `status`: `open | in-progress | review | closed`. `ow task` moves an open or
  reviewed change to `in-progress`; `record-review` sets `review` (pass) or
  `in-progress` (blocked); `close` sets `closed`, `closed_by` and `closed_at`.
- `mode`: `default | fast-forward`. Changing mode makes a pending review stale.
- Use a fresh ID for follow-up work.

## Tasks

`changes/C-001/tasks.json`:

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

Required: `id` (qualified by its change), `title`, `status`, `acceptance`. Optional
with defaults: `depends_on = []`, `kind = "agent"` (or `manual`), `files = []`,
`evidence = ""`. Status is `open | in-progress | blocked | done`; `done` requires
evidence and finished prerequisites. Dependencies stay within the change and form
an acyclic graph; list order is the scheduling preference. An empty list is valid
for verification-only work or a future candidate not yet planned.

```sh
ow task C-001/T-001 in-progress
ow task C-001/T-001 done --evidence "tests/test_export.py: 4 passed; two-month fixture exact"
```

## Review, closure and disposal

```sh
ow record-review C-001 --summary "Monthly reconciliation no longer needs row copying" \
  --check "python -m unittest tests.test_export: 6 passed in 0.4s" \
  --affected N-003 --handoff /tmp/ow-handoff.json      # or --handoff - to read stdin
ow summary C-001
ow close C-001 --by human                              # after actual human acceptance
ow clean C-001 --dry-run
ow clean C-001
```

- `--affected` names needs whose behavior the change touches beyond its linked needs
  (which are always affected). Every other current need is recorded as **assessed
  and unaffected**; the reviewer must actually make that judgment.
- `--verdict blocked` records unresolved findings. A passing review needs all tasks
  done, at least one check, and a handoff with no `unresolved` items.
- The handoff input is temporary JSON outside the repository. It is copied into
  `review.json`:

  ```json
  {"handoff": [{
    "requirement": "Export exactly the selected month without uploading raw records",
    "disposition": "implemented",
    "destinations": ["src/transactions/export.py", "tests/test_export.py"],
    "evidence": "Independent two-month fixture and local-only boundary check pass."
  }]}
  ```

  Each item has exactly these four fields. Destinations are existing, non-ignored,
  repository-relative files.

  | Disposition | Destination |
  | --- | --- |
  | `implemented` | Product files and independent checks (not `openwish/` records) |
  | `retained` | A need or ordinary repository doc/data holding intent or rationale |
  | `deferred` | Another active change or retained domain data holding approved unfinished detail |
  | `superseded` | Where the replacement intent and the human decision are recorded |
  | `unresolved` | Missing work or evidence; blocks a passing review |

**Freshness.** A passing review records digests of its inputs: the change, its tasks,
every current and linked need, the handoff and its destinations, config, policy,
each product file outside `openwish/` (Git tracked and unignored files, recursively
including submodules; filesystem walk without Git), and submodule revisions. Any
difference makes the review stale, and `ow summary`/`ow close` name what changed.
Missing or conflicted submodule checkouts prevent a fresh passing review.

**Cleanup.** `ow clean` removes only `change.md`, `tasks.json` and `review.json` of
closed changes, after preflighting the whole batch. It refuses unknown files,
symlinks, missing or ignored handoff destinations, destinations inside the batch,
and other retained reviews that cite the batch. It warns about retained files that
still mention a removed change ID. A closed review is historical: later code edits
do not block cleanup. If a destination moved after closure, update only that
review's handoff paths and evidence.

## Inspection

```sh
ow status --json            # needs, changes, task progress, review state, retention groups
ow context [IDS] [--json]   # all current needs, plus a sized retrieval manifest for selected work
ow graph [N-001] [--json]   # recorded need relations and their endpoints
ow trace [N-001] [--json]   # need → files and tests that mention the need ID
ow ready [IDS] [--json]     # ready tasks and blockers across active changes
ow summary IDS              # need → outcome → evidence, freshness and why a review is stale
ow check [--json] [--artifacts-only]
```

`--root PATH` goes before the subcommand; otherwise the project root is found from
the current directory upward. Status retention groups: `cleanup_candidates`,
`awaiting_acceptance`, `blocked_changes`, `retired_needs`.

**Trace.** `ow trace` scans code, tests and docs (not `openwish/` or installed
guidance) for need IDs, and lists test locations separately. Mentioning a need ID
in a test's name, docstring or comment links that check to the need. `ow check`
warns about mentions of unknown or retired needs. Missing traces do not prove a
need is unprotected.

## Configuration and installation

`config.json`: `version: 4`, `product`, `needs_token_budget` (default 24000, a soft
target that warns at 80%), `source_hard_limit` (default 0 = off), and
`code_exceptions` (each with exact `path`, `kind` of `data` or `low-complexity`, and
`reason`). OW artifacts warn at 8,000 estimated tokens (UTF-8 bytes/3); source warns
at 500 nonblank lines. Only a configured `source_hard_limit` makes size an error.

`ow init` offers a harness multi-select, or use `ow init --harness opencode claude`.
Reinitializing preserves project knowledge and policy, upgrades older integration
files, leaves equal versions untouched and asks before downgrades.
`ow skills --harness NAME` uses the same installer. Only schema 4 is supported.
