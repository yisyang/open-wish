---
name: ow-fast-forward
description: Run OpenWish work through implementation, review, closure and disposal without approval prompts, including final acceptance. Use only after the human explicitly delegates OW acceptance or says fast-forward.
disable-model-invocation: true
---

# Fast-forward

Use only after explicit delegation; loading this skill grants nothing. Load
`ow-core` and read `openwish/policy.md`. Respect opt-outs and plan-only requests.

1. **Direct work** stays direct (`ow-core`): no records, no mode, no acceptance
   question.
2. **Managed work** follows `ow-propose` → `ow-align` → `ow-plan` →
   `ow-implement` → `ow-review` → `ow-consolidate`, reading each skill on entry and
   skipping only confirmations the delegation already answers.
3. **Delegation covers named changes only.** Create them with
   `ow new change C-001 --title "..." --need N-001 --fast-forward`, or run
   `ow mode fast-forward C-001` for an active change this request covers. Delegation
   does not justify one oversized change, and split or later changes start in
   default mode. Across several named changes, follow `ow ready` and close in
   sequence order.
4. **Decide routine choices** from current intent. Finish independent work first,
   then present only genuine blockers (conflicting intent, missing access, manual
   observations) as A/B/C questions.
5. **Stay honest.** Never invent checks, mark manual work done, set
   `confirmed_at` on inferred needs, or tag a rule `confirmed` or
   `approved-initial`. After a fresh passing review: `ow close C-001 --by
   fast-forward`; dispose via `ow-consolidate` once the human has seen the result.
6. **Report as in `ow-review` step 7**, including the choices made on the human's
   behalf, and attribute acceptance to delegation rather than human review.
