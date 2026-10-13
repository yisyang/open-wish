---
name: ow-implement
description: Execute or resume an authorized OW change using its tasks, continuing independent work through verification and review. Honor OW opt-outs and keep routine changes lightweight.
---

# Implement

Read `openwish/policy.md`, `ow context C-001`, the change's approach and
`ow ready C-001`. Confirm the conversation authorizes implementation; readiness
does not. Routine work: implement, verify, report.

1. **Resume safely.** On resumption or changed scope, apply Reconcile the plan in
   `ow-plan` first. Verify prerequisite capabilities from earlier increments in
   the repository. Plan an unplanned candidate's tasks before executing it.
2. **Pick ready work** in list order. Read its acceptance and motivating needs,
   retrieve rule files listed by `ow context` (they are not loaded automatically),
   and inspect the code. If finishing would require inventing product policy,
   resolve that first (Task sizing in `ow-plan`). Run `ow task C-001/T-001
   in-progress`.
3. **Implement** the smallest coherent solution that preserves current needs and
   existing user work. Follow the repository's structure and the Architecture
   rubric in `ow-align`: pure decisions, effects at the edges, no speculative
   abstractions. Keep module headers and boundary READMEs accurate where you
   change responsibilities.
4. **Verify** with Strategic verification in `ow-plan`: run affected checks, add the
   smallest checks for real gaps, mention need IDs in need-level tests. Then
   `ow task C-001/T-001 done --evidence "what ran and what it showed"`. Manual
   observations need real evidence; fast-forward cannot supply them.
5. **Keep going.** Continue independent ready tasks around blocked or manual ones.
   Update the approach and remaining tasks as you learn; technical repairs within
   scope need no permission. If scope grows, apply Right-size delivery in
   `ow-propose`. Material intent changes need a decision.
6. **Preserve as you go.** Behavior goes in code, checks in tests, non-obvious
   rationale nearby. Keep material conditions, exceptions and units intact. Put
   approved unfinished detail in its retained home now. Note in the change where
   each material rule landed; the review's handoff will reuse it.
7. **Ask only when blocked.** When only human blockers remain, explain the need and
   outcome, then ask numbered A/B/C questions with `(Recommended)`. Never discard
   unfinished work to look complete.
8. **Review.** When work is complete, continue into `ow-review` without asking.

Lead updates with **need → outcome → evidence**; task IDs support, not replace, that.
