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
6. Keep all current intent complete within its line/token budget. Splitting files
   does not solve an oversized register. Clarify boundaries if safe compaction
   cannot fit, rather than silently truncating constraints.
7. Run `ow check` and report what was disposed and where useful knowledge lives.
   Routine work needs no change record merely to perform cleanup.
