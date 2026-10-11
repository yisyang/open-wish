---
name: ow-implement
description: Execute or resume an authorized OW change using local tasks. Continue independent work through verification and review. Honor OW opt-outs and keep routine changes lightweight.
---

# Implement

Read `openwish/policy.md`, `ow context C-001`, the change approach, and
`ow ready C-001`. Verify conversation authority before implementation; readiness
does not grant it. For routine work, implement and verify directly, then report.

1. On resumption or changed decisions/scope, apply Reconcile the plan in
   `../ow-plan/SKILL.md` before trusting `ow ready`. Verify prerequisite capabilities
   from earlier increments in the repository; reconcile stale blockers with actual
   evidence. Expand an unplanned candidate's tasks before executing it.
   Select ready work in listed order, subject to local prerequisites. Read its
   acceptance and the motivating needs, then inspect relevant code and tests.
   Set the change and task in-progress as work begins.
2. Implement the smallest coherent solution. Preserve current needs and existing
   user work. Prefer functional cores, explicit effects, and discoverable module
   boundaries consistent with the repository. Keep checks independent of the code's assumptions.
   Use the Architecture rubric in `../ow-align/SKILL.md` when a new ask changes
   boundaries. Keep decisions and transformations pure where practical, passing
   external results/time/configuration explicitly; isolate I/O at the edges.
   Verify core behavior and relevant integration contracts where each adds useful
   evidence. Avoid speculative abstractions.
3. Follow Strategic verification in `../ow-plan/SKILL.md`. Run existing affected
   checks and add only the smallest checks for genuine gaps. Assert stable outcomes,
   not incidental wording/layout or private call sequences. Keep credible,
   consequential failure checks; expand only when the work justifies their cost.
   Record concise direct evidence before marking a task done. Retain completed
   tasks for integration review. Manual observations
   require real evidence; fast-forward cannot invent them.
4. Continue independent ready work around blocked/manual tasks. A task's list
   position alone does not block later work. Repair the approach and remaining
   tasks as the implementation teaches you more; keep technical decisions within
   existing authority. Reassess growing scope with Right-size delivery in
   `../ow-propose/SKILL.md`; preserve unfinished work/evidence when splitting changes.
   Material intent/scope changes return to the relevant decision.
5. Put enduring behavior in code, regression checks in tests, and otherwise
   unrecoverable rationale near code or in ordinary repository documentation.
   Retain tests protecting lasting obligations; temporary probes need not become
   permanent tests. Report current verification and limitations without a run archive.
   Never establish another permanent spec or execution ledger.
6. When only genuine human blockers remain, explain the need and desired outcome,
   then ask numbered questions with useful A/B/C choices and `(Recommended)` before
   the preferred text. Do not discard unfinished work to manufacture completion.
7. When the work is complete, enter `ow-review` automatically. Continue remediation
   and rechecking within scope without an intermediate permission prompt.

Updates lead with **need → outcome → evidence**, then limitations or human input.
Use `ow summary C-001` when useful. Task IDs support rather than replace purpose.
