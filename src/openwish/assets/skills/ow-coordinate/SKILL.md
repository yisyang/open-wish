---
name: ow-coordinate
description: Coordinate several authorized OW changes or investigations at once through worker sessions in isolated worktrees, with one round record, independent review, serialized integration and close-out. Use when the human asks for parallel or coordinated work. Honor OW opt-outs.
---

# Coordinate

Load `ow-core` and read `openwish/policy.md`. A round runs named changes side by
side; each still follows the ordinary skills. Coordination adds isolation,
integration and a record, never authority.

1. **Propose the round.** From `ow ready`, name each change and the tasks in scope
   (delivery; investigations and previews that settle decisions and screens before a
   later round builds them; or process improvements measured from earlier rounds),
   what can run concurrently, the base revisions and the integration targets. First
   find the questions the round would otherwise raise later (Discover ahead of
   delivery in `ow-plan`) and preview each unseen surface (Commit progressively in
   `ow-plan`). Ask only material questions, in one batch, then wait for an explicit
   instruction to begin. That authority covers the named scope only; fast-forward
   applies per named change (`ow mode fast-forward C-001`).
2. **Keep one round record** outside the repository: the human's brief verbatim,
   agreed scope and authority, bases, integration order and decisions. Read
   sessions, worktrees, branches, task states and check results from their own
   stores instead of copying them into the record, where copies go stale. Re-read
   the record and brief after compaction, interruption or resumption; never ask the
   human to resend them. Keep the round's evidence where it survives a restart, and
   restart nothing its sessions depend on until the record says the round is
   complete.
3. **Set up workers.** One worktree and branch per change, and per component in a
   submodule project, from the agreed base; one writer each. Verify directories,
   roots, branches and bases before sending work. Brief each worker with its task,
   the files and interfaces to start from, the checks to run, and the duty to report
   every choice made on the human's behalf. A brief that quotes the linked needs'
   acceptance and names the rule-doc sections replaces the worker's `ow context`. A
   worker verifies its own task (step 4 of `ow-implement`), submits its result and
   stops. Only the coordinator runs `ow mode`, `ow record-review`, `ow close` and
   `ow clean`.
4. **Run and review.** Keep independent work moving; serialize shared-interface and
   migration conflicts. A successor task may start on its predecessor's submitted
   work before review, and reconciles if review changes it. Wait for whichever
   session finishes first and act on its result; never let one slow session hold
   finished results. Each change gets one independent review, when its tasks are
   done, from a fresh session that implemented and corrected none of it. A task is
   reviewed earlier only when other work builds on a commitment point it sets
   (Commit progressively in `ow-plan`); previews, static mocks and tasks that only
   add tests or records get no review of their own. Blocking findings (`ow-review`)
   go back to a worker, then to re-review. A
   correction or re-review may continue in its own session while that session stays
   small (Keep context small in `ow-core`). Keep your context for coordination:
   corrections, including those the human asks for after the round, also go to
   workers and reviewers.
   - **Gate questions.** Answer a worker's question from needs, rule docs, recorded
     decisions or code when they settle it, and decide a reversible choice without
     asking (Reversible choices in `ow-plan`). An unseen surface found during the
     round is built on its proposal and shown as a first look; it holds no work.
     Only a commitment-point decision or a rule contradiction reaches the human, as
     one question with its cases, while work that does not depend on it continues.
5. **Integrate one change at a time** on an integration branch: reconcile it with
   the current target, rerun affected checks, commit component revisions and their
   pins, record or refresh the review (`ow-review`), then publish. Hold effects that
   could disturb running checks (deploys, restarts, large transfers on a shared host)
   until those checks finish.
6. **Report and close out.** Report each change as in `ow-review` step 7, choices
   made on the human's behalf first. Closed changes wait for the human's response
   (Dispose closed changes in `ow-consolidate`). Once integrated work is published,
   update local default branches, remove each worktree and branch after confirming
   its content is integrated, delete what only the round needed (its scripts,
   harnesses, fixtures, disposable resources and evidence nothing retained cites),
   and mark the record complete.
