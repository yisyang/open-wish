# Migrating the v0.1 prototype to schema 2

Version 0.2 operates directly on needs. Schema 1 is rejected explicitly rather
than silently interpreting its change records as need state. This repository's
baseline has been updated; these steps apply to other prototype workspaces.

1. Preserve the original workspace in Git or a backup before restructuring it.
2. Review existing needs. Keep stable IDs, outcomes, acceptance, currency, and
   verified history. Remove the `ask` field after retaining any genuine durable
   constraints in the outcome/acceptance/body. Do not create a replacement ask log.
3. Move each spec's authoritative `needs` array from `spec.md` to `design.md`'s
   TOML header with matching `id`. Preserve the design body and contract links.
4. Reconcile any outstanding prototype work into the appropriate existing need
   definitions and linked specs/epics/tasks. A new need requires a distinct outcome.
5. Preserve reusable direct verification findings where relevant, then remove
   obsolete change containers from the active OW tree. Do not copy their ask logs
   or old approval fingerprints into need state; those receipts bind a different model.
6. Set config `version` to `2` and replace `working_set_limit` with `epic_limit`
   (default `8`). Retain token budgets, product name, and justified source exceptions.
7. A missing `needs/N-001.state.json` defaults to revision 1 with no approvals.
   Use `ow reopen N-001` for unfinished implementation and reconcile current
   decisions. Enable fast-forward only when explicitly requested again.
8. Refresh generated policy, artifact guidance, and skills from the new package,
   preserving local customizations. Run `ow check` and inspect `ow context`.

New commands take need IDs directly: `ow ready N-001`, `ow gate needs N-001
--by human`, and `ow approve N-001`. `ow summary N-001` shows the need, its specs,
results, and verification. There is no replacement persistent grouping object.
