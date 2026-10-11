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
   Apply the sizing questions below before creating, splitting, or merging needs.
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

## Right-size intent

- A need describes one coherent valuable outcome, independent of its mechanism or
  implementation effort. Several changes may serve one need.
- Too small: a format, button, module, or task with no separate value. CSV and XLSX
  for the same reconciliation workflow normally reuse the same need.
- Too broad: acceptance combines outcomes that could be accepted, changed, or
  retired independently. Reconciliation and auditor accountability may be separate.
- Ask whether the outcome survives replacing the implementation, whether each
  acceptance criterion explains that outcome, and whether part could cease to be
  needed while the rest remains. Compare meaning, not merely wording or shared code.
- Consolidate duplicate intent; split genuinely independent outcomes. Preserve
  acceptance and constraints and seek a decision when meaning changes. Stable IDs
  support continuity but do not prohibit justified splits/merges. Reconcile incoming
  need relations and retained change links when replacing an ID.

## Preserve useful relationships

Use `ow graph --json` to retrieve established relationships, then assess changed
intent and possible new interactions. Store only useful durable facts on the source
need, as optional TOML `relations = [{kind = "constrains", need = "N-001", reason =
"Raw records must stay local in reconciliation."}]` (keep each inline table on one
line). `requires` means the source outcome needs the target outcome; `constrains`
means the source limits acceptable solutions for the target. Include a concrete
reason. These are semantic links, not task order, shared-code links, or inferred
conflicts caused by today's implementation. Cycles can be meaningful.

Do not construct a complete pairwise graph. Review incoming/outgoing links when
intent changes, including retirement; current relations must target current needs.
All current intent remains binding even when no relationship was recorded. Keep
temporary code-impact analysis in the change and reconstruct it from source/tests.

If no intent revision or useful work remains, explain the existing outcome and
finish without generating records.
