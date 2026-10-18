---
name: ow-implement
description: Implement authorized OW work, directly or by executing or resuming a change's tasks, continuing independent work through verification and review. Honor OW opt-outs.
---

# Implement

Load `ow-core` and read `openwish/policy.md`. Confirm the conversation authorizes implementation;
readiness does not, and an empty `confirmed_at` does not withhold it. Use an active
change that covers the ask.

- **Direct:** run `ow context`; apply steps 3, 4, 6, 7 and 8 without `ow task`
  commands or change notes. If coordination needs appear, apply Promote direct
  work in `ow-plan`.
- **Managed:** run `ow context C-001` (needs, readiness, warnings), read the
  change's approach, and apply every step.

1. **Resume safely.** Verify prerequisite capabilities in the repository. On
   resumption, changed scope or a revised predecessor, apply Reconcile the plan in
   `ow-plan`; plan a change without tasks first (Plan a candidate).
2. **Pick ready work** in list order. Read its acceptance and motivating needs,
   retrieve rule files listed by `ow context` (they are not loaded automatically),
   and inspect the code. If finishing would require inventing product policy,
   resolve that first (Task sizing in `ow-plan`). Run `ow task C-001/T-001
   in-progress`. Ready investigations in other changes are planning (`ow-core`):
   take them too, within the in-flight limit of Discover ahead of delivery in
   `ow-plan`. Each ends with findings in their retained home, or `blocked` with
   its question for the next batch.
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
   each material rule landed; the review's handoff will reuse it. Change notes hold
   decisions and their homes, not progress logs, run transcripts or failure history.
7. **Ask only when blocked.** When only human blockers remain, explain the need and
   outcome, then ask A/B/C questions. Never discard
   unfinished work to look complete.
8. **Review.** When work is complete, continue into `ow-review` without asking.

Lead updates with **need → outcome → evidence**; task IDs support, not replace, that.
