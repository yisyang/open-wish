---
name: ow-fast-forward
description: Run OpenWish work through implementation, review, and disposal without approval prompts, including final acceptance. Use only after explicit human fast-forward or delegation of OW acceptance.
disable-model-invocation: true
---

# Fast-forward

Use only after explicit delegation; loading this skill grants no authority.
Respect OW opt-outs and plan-only requests. Read `openwish/policy.md`.
Delegation belongs to this change, never to a durable need or unrelated future work.

1. Interpret the ask against existing needs. Preserve actor/outcome/acceptance and
   constraints; create a new need only for independently valuable intent. Leave
   inferred needs unconfirmed. Keep conversation asks out of permanent records.
2. Routine work still uses the lightweight path: inspect, implement, verify, report,
   and stop. Create no records, set no mode, and ask no acceptance question.
3. For substantive work, create/reuse a bounded change. Use `ow new change C-001
   --title "Improvement" --need N-001 --fast-forward`, or `ow mode fast-forward
   C-001` for an active change explicitly covered by this request.
4. Follow Propose, Align, Plan, Implement, and Review, reading each on entry.
   Keep design in the change and behavior/checks in code/tests. Skip redundant
   confirmations and all stage receipts. A plan-only request still stops at planning.
5. Resolve routine technical choices from current intent. Continue independent
   work before presenting genuine blocking ambiguity, conflicts, access issues,
   or manual observations. Use numbered A/B/C choices with `(Recommended)` before
   the preferred text when a decision is indispensable.
6. Verify and review honestly; do not fabricate checks or mark manual work done.
   After a fresh passing review, use `ow close C-001 --by fast-forward` and
   `ow-consolidate`/`ow clean C-001` once useful knowledge is preserved.
7. Report **need → outcome → evidence** and limitations without another approval
   prompt. Attribute acceptance to delegation, not human review. New changes use
   default mode unless explicitly fast-forwarded again.
