---
name: ow-fast-forward
description: Run OpenWish work through implementation, review, closure and disposal without approval prompts, including final acceptance. Use only after the human explicitly delegates OW acceptance or says fast-forward.
disable-model-invocation: true
---

# Fast-forward

Use only after explicit delegation; loading this skill grants nothing. Read
`openwish/policy.md`. Respect opt-outs and plan-only requests.

1. **Routine work** stays routine: inspect, implement, verify, report. No records,
   no mode, no acceptance question.
2. **Structured work** follows `ow-propose` → `ow-align` → `ow-plan` →
   `ow-implement` → `ow-review` → `ow-consolidate`, reading each skill on entry and
   skipping only confirmations the delegation already answers.
3. **Delegation covers named changes only.** Create them with
   `ow new change C-001 --title "..." --need N-001 --fast-forward`, or run
   `ow mode fast-forward C-001` for an active change this request covers. Delegation
   does not justify one oversized change, and split or later changes start in
   default mode.
4. **Decide routine choices** from current intent. Finish independent work first,
   then present only genuine blockers (conflicting intent, missing access, manual
   observations) as numbered A/B/C questions with `(Recommended)`.
5. **Stay honest.** Never invent checks, mark manual work done, or set
   `confirmed_at` on inferred needs. After a fresh passing review:
   `ow close C-001 --by fast-forward`, then dispose via `ow-consolidate`.
6. **Report need → outcome → evidence** and limitations, and attribute acceptance
   to delegation rather than human review.
