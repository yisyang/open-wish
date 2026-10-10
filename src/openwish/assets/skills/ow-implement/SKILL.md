---
name: ow-implement
description: Execute or resume an authorized structured OW plan in dependency order. Continue independent work until completion or genuine blockers. Honor OW opt-outs; routine coding needs no structured plan.
---

# Implement

Read `openwish/policy.md`, `ow context N-001 ...`, and `ow ready N-001 ...`.
Authority and progress belong to needs. Follow each need's explicit mode and
revision; missing authority blocks only affected work, not other authorized tasks.
Routine changes identified by Propose implement and verify directly without gate
receipts. Do not expand them into a structured workflow merely to use this skill.

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
   A technical repair or relinking within the same authorized scope can refresh
   receipts using existing conversation authority; it needs no new permission.
   Shared spec references are regression coverage. Use the epic's execution scope
   rather than splitting specs or reopening unrelated needs to satisfy `ready`.
6. When only genuine human blockers remain, explain the affected need and spec,
   then ask numbered questions with two or three A/B/C choices. Prefix the
   preferred choice text with `(Recommended)` and describe useful effects briefly.
7. When all relevant work is done, automatically enter `ow-review`. Continue
   remediation and appropriate checks without asking permission for AI review.

Updates and handoffs lead with the need's purpose and the spec delivering it,
then the result, verification, and remaining blocker. Use `ow summary N-001 ...`.
Epic/task IDs may support the explanation but never replace need/spec context.
