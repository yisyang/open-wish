---
name: ow-propose
description: Interpret substantive software asks in an OW-managed project or an explicit OW request. Reuse durable needs and scope disposable changes. Respect OW opt-outs; routine coding does not require this skill.
---

# Propose

Respect OW opt-outs. Initialize only when adoption was requested. Read
`openwish/policy.md`, `ow context`, and relevant code/tests. Needs are durable;
changes and tasks are temporary working context. Respect deliberate local controls.

1. Identify actor, valuable outcome, observable acceptance, and genuine constraints.
   Compare with existing needs before adding one. Formats, commands, interfaces,
   and mechanisms usually serve existing intent. A new need requires an
   independently valuable difference; preserve IDs when revising intent.
2. If the outcome already exists, explain it. If a different mechanism is still
   useful, scope that improvement under the existing need. Keep asks in conversation.
3. Clear, localized, reversible work within intent goes straight to inspection,
   implementation, meaningful verification, and reporting. Create no change file
   or need just to track it; request no final acceptance ceremony. Keep work already
   in an active change there, including manual checks. Honor plan-only requests.
4. For substantive work, create/reuse a bounded change referencing the motivating
   needs directly: `ow new change C-001 --title "Improvement" --need N-001`.
   Follow `openwish/artifacts.md`. Needs store outcomes and constraints; the change
   stores purpose, working approach, verification, and tasks. Do not create specs,
   epics, need-owned execution state, or stage receipts.
5. Clarify consequential uncertainty or conflict rather than restating clear
   instructions. Use numbered questions with two or three A/B/C choices and
   `(Recommended)` before the preferred text. Preserve current constraints pending
   an actual intent decision. Leave inferred needs' `confirmed_at` empty.
6. Continue to `ow-align` and `ow-plan` to prepare coherent work. Conversation
   authority covers implementation; preparation requires no stage approvals.
   Explicit fast-forward applies only to its change, never to the durable need.

If no intent revision or useful work remains, explain the existing outcome and
finish without generating records.
