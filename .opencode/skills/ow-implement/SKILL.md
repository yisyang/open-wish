---
name: ow-implement
description: Implement authorized OpenWish needs in dependency order, continuing independent ready work until completion or genuine human blockers. Use to implement or resume NDD work.
metadata:
  openwish-version: "0.3.1"
---

# Implement

Read `openwish/policy.md`, `ow context N-001 ...`, and `ow ready N-001 ...`.
Authority and progress belong to needs. Follow each need's explicit mode and
revision; missing authority blocks only affected work, not other authorized tasks.

1. Select the lowest ready `(group, order)` task. Load its epic and spec designs,
   including the spec's need references, relevant code, and acceptance conditions.
2. Mark it in-progress, implement the smallest coherent solution, and preserve all
   current needs and existing user work. Respect code and artifact budgets.
3. Run meaningful checks, inspect results, and record concise direct evidence
   before marking the task done. Never invent a human observation.
4. Continue using `ow ready` while authorized work remains. A pending review,
   completed epic, or independent manual blocker does not justify stopping.
   Task prerequisites, not merely earlier ordinals, determine blocking.
5. Repair defects within approved intent. Material need/design revisions return
   to the relevant earlier phase; refresh stale authority under the selected mode.
6. When only genuine human blockers remain, explain the affected need and spec,
   then ask numbered questions with two or three A/B/C choices. Prefix the
   preferred choice text with `(Recommended)` and describe useful effects briefly.
7. When all relevant work is done, automatically enter `ow-review`. Continue
   remediation and appropriate checks without asking permission for AI review.

Updates and handoffs lead with the need's purpose and the spec delivering it,
then the result, verification, and remaining blocker. Use `ow summary N-001 ...`.
Epic/task IDs may support the explanation but never replace need/spec context.
