---
name: ow-consolidate
description: Compact OpenWish epics and knowledge while preserving durable needs, current spec designs, and acceptance conditions. Use after implementation or when context budgets approach their limits.
metadata:
  openwish-version: "0.3.1"
---

# Consolidate

Read `openwish/policy.md`, `ow status`, and `ow context`. If budgets already fail,
inspect reported files directly before requesting full context.

1. Identify completed epics/tasks, duplicate wording, stale facts, and near-limit
   files. Do not scan all Git history or preserve conversation asks as artifacts.
2. Promote current contracts/rationale to spec designs, operational profiles and
   secret references to knowledge, and lasting outcome constraints to their needs.
   Keep spec design need references intact so later updates retain their purpose.
3. Remove completed ephemeral instructions once relevant resulting truth is
   preserved. Keep unresolved limitations, manual checks, and prerequisites visible.
4. Tighten wording while preserving IDs and acceptance. Merging distinct outcomes
   or retiring a need changes intent: use Propose under the selected workflow.
   Clarifications use numbered questions, two or three A/B/C choices, and
   `(Recommended)` before the preferred choice text, with concise useful effects.
5. Preserve the only historical copy in Git before removing completed epics.
   Resolve live references first. Keep one current state and latest review per
   need; do not accumulate asks, execution containers, histories, or archive indexes.
6. Keep all current needs globally complete. Splitting files does not solve an
   oversized register. If safe compaction cannot fit, clarify product boundaries
   or genuinely redundant needs without silently weakening intent.
7. Run `ow check`; inspect stale approvals after semantic edits. Report a compact
   size summary plus the affected needs/specs and any current decision required.

Routine bounds and replacing latest summaries apply in every phase even when
this optional semantic maintenance skill is never invoked.
