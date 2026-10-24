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
   this record, not in changes or docs. Keep the round's evidence where it survives
   a restart. Until the record says the round is complete, restart nothing its
   sessions depend on.
3. **Set up workers.** One worktree and branch per change, and per component in a
   submodule project, from the agreed base; one writer each. Verify directories,
   roots, branches and bases before sending work. Brief each worker with the change,
   its needs and rule files, the files and interfaces to start from, the checks to
   run, and the duty to report every choice made on the human's behalf. A worker
   submits its result and stops: it does not continue into `ow-review` or record
   reviews, which the coordinator does at integration (step 5).
4. **Run and review.** Keep independent work moving; serialize shared-interface and
   migration conflicts. Wait for whichever session finishes first and act on its
   result; never let one slow session hold finished results. Each consequential
   result gets an independent review from a session that did not implement or
   correct it. A re-review may continue in the reviewer's own session while that
   session stays small (Keep context small in `ow-core`). Blocking findings
   (`ow-review`) go back to a worker, then to re-review. Keep your context for
   coordination: corrections, including those the human asks for after the round,
   also go to workers and reviewers.
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
