---
name: ow-coordinate
description: Coordinate several authorized OW changes or investigations at once through worker sessions in isolated worktrees, with one round record, independent review, serialized integration and close-out. Use when the human asks for parallel or coordinated work. Honor OW opt-outs.
---

# Coordinate

Load `ow-core` and read `openwish/policy.md`. A round runs named changes side by
side; each still follows the ordinary skills. Coordination adds isolation,
integration and a record, never authority.

1. **Propose the round.** From `ow ready`, name each change and the tasks in scope
   (delivery, or investigations only), what can run concurrently, the base
   revisions and the integration targets. Ask only material questions, then wait for
   an explicit instruction to begin. That authority covers the named scope only;
   fast-forward applies per named change (`ow mode fast-forward C-001`).
2. **Keep one round record** outside the repository, for example beside the
   worktrees: the human's brief verbatim, agreed scope and authority, bases, each
   worker's session, worktree and branch, integration order and current state.
   Re-read the record and brief after compaction, interruption or resumption, before
   acting; never ask the human to resend them. Session and resource details stay in
   this record, not in changes or docs.
3. **Set up workers.** One worktree and branch per change, and per component in a
   submodule project, from the agreed base; one writer each. Verify directories,
   roots, branches and bases before sending work. Brief each worker with the change,
   its needs and rule files, interfaces to preserve, checks to run, and the duty to
   report every choice made on the human's behalf.
4. **Run and review.** Keep independent work moving; serialize shared-interface and
   migration conflicts. Each consequential result gets an independent review in a
   fresh session that did not implement it; blocking findings go back to the worker,
   then to re-review. Keep your context for coordination: corrections, including
   those the human asks for after the round, also go to workers and reviewers.
5. **Integrate one change at a time** on an integration branch: reconcile it with
   the current target, rerun affected checks, commit component revisions and their
   pins, record or refresh the review (`ow-review`), then publish. Hold effects that
   could disturb running checks (deploys, restarts, large transfers on a shared host)
   until those checks finish.
6. **Report and close out.** Report each change as in `ow-review` step 7, choices
   made on the human's behalf first. Closed changes wait for the human's response
   (Dispose closed changes in `ow-consolidate`). Once integrated work is published,
   update local default branches, remove each worktree and branch after confirming
   its content is integrated, remove disposable resources, and mark the record
   complete.
