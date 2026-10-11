---
name: ow-consolidate
description: Dispose closed OW changes and tasks, preserving durable needs and useful repository knowledge. Compact intent on request or in an active OW workflow. Honor OW opt-outs.
---

# Consolidate

Read `openwish/policy.md`, `ow status`, and `ow context`. If budgets fail, inspect
the reported files directly before requesting full context.

1. Identify closed changes eligible for disposal and redundant wording. Keep
   active work and unresolved manual checks visible; task completion alone is
   insufficient to remove its parent change.
   Use status's retention summary to distinguish cleanup candidates, results awaiting
   acceptance, manual/blocked work, and retired needs. Investigate abandoned-looking
   work with the human; age or volume alone never establishes completion or withdrawal.
2. Check that durable intent is in needs, behavior in source, executable checks
   in tests, and useful rationale/environment references in ordinary repository
   docs or nearby comments. Do not copy the entire temporary approach into docs.
   Future maintenance should not require resurrecting a deleted change.
3. Prefer preserving that knowledge before final review. If an active change needs
   new edits, refresh checks and review before closure. Already-closed results are
   historical; substantive follow-up work belongs to a new change.
4. Run `ow clean C-001 ...` for closed changes. It removes their known change,
   task, and review files together, preserves unknown files, and preflights the
   selection. Move useful unknown content deliberately before retrying. Use Git
   for history when useful; do not automatically commit or build an OW archive,
   permanent execution register, or need review sidecars.
5. Compact needs without losing acceptance or constraints. Shared code or shared
   changes do not imply duplicate outcomes. Merging or retiring needs changes
   intent; obtain a decision when needed, with numbered A/B/C options and
   `(Recommended)` before the preferred text. Preserve stable IDs where possible.
   Use the sizing questions in `../ow-propose/SKILL.md`: resolve duplicates,
   mechanism-sized needs, broad outcome bundles, and drift before merely shortening
   prose. Inspect `ow graph --json`; reconcile incoming/outgoing relations and retained
   change references when merging, splitting, or removing retired IDs. Remove retired
   needs only by an actual retention decision once useful rationale and references
   have been reconciled. Never retire current intent just to meet a budget.
6. Keep all current intent complete within its line/token budget. Splitting files
   does not solve an oversized register. Clarify boundaries if safe compaction
   cannot fit, rather than silently truncating constraints.
7. Run `ow check` and report what was disposed and where useful knowledge lives.
   Routine work needs no change record merely to perform cleanup.

Keep executable checks and useful manual verification procedures, not every run's
output. Retain small regression checks for lasting outcomes, invariants, and
consequential boundaries. Discard temporary probes and consolidate redundant or
brittle tests when their meaningful protection is preserved; low test count is not
itself a goal. Tests enable fresh evidence; they do not prove a past run. Preserve only
non-obvious rationale and operational facts in docs/comments, replacing obsolete
guidance instead of copying whole plans or reviews. Historical evidence is retained
as product data only when an actual need requires it. OW stores no permanent
satisfaction claim, delivery ledger, or architecture report. Cleanup is a normal
completion action; active work stays honest rather than being deleted to meet a cap.
