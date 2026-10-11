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
   or need just to track it; request no final acceptance ceremony. Reconcile tracked
   work before moving it between changes; preserve manual checks. Honor plan-only requests.
4. Apply Right-size delivery below before creating or extending execution records.
   For each selected increment, create/reuse a change referencing its motivating
   needs: `ow new change C-001 --title "Improvement" --need N-001`. Record its purpose,
   scope, approach, verification, and tasks using `openwish/artifacts.md`. Broad asks
   may need several changes. Keep needs free of execution state and create no specs,
   epics, or stage receipts.
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

## Right-size delivery

Need size follows independent value; change size follows a reviewable delivery
boundary. One ask may require many changes, and one need may span many increments.
Many need references can be appropriate for one narrow cross-cutting improvement.
Neither need count, task count, nor document length establishes manageable scope.

Before planning tasks, answer:

- What concrete capability or improvement will exist after this change?
- What direct evidence would let someone accept it? Can they retain that result
  and postpone later work without leaving this increment broken or unverifiable?
- Does a proposed task hide a separately useful subsystem, workflow, or delivery?
- Which unknowns could materially change the approach? Resolve consequential
  uncertainty early with a focused investigation/prototype and an observable result.

Split independently acceptable improvements. Combine work that requires a joint
acceptance boundary, such as an inseparable contract/consumer update. Shared code,
a common database, or a later feature using an earlier one is a sequential dependency,
not by itself a reason to combine changes. Prefer narrow end-to-end outcomes with
the UI/API/persistence/checks they need over doing every backend before every frontend.
An enabling change is useful when it proves a concrete capability, not just empty layers.

State each change's **delivers now**, **preserves**, **defers**, and **exit evidence**.
Associate delivered results with motivating need IDs where useful; a need reference
does not promise its entire acceptance in this increment. All current constraints
remain binding. Deferral preserves future intent; it cannot excuse violating an
applicable constraint or silently remove an agreed deliverable.

For a broad modernization or product build, propose a sequence of candidate changes
with outcomes, prerequisite capabilities, uncertainties, and exit evidence. Detail
the next executable increments; refine later ones against delivered code. If a
resumable plan is requested, keep later candidates as concise ordinary open changes
with empty task lists until selected, explaining that planning is incomplete. Do not
create a parent implementation change containing the whole program. Conversation
can hold an assessment-only sequence; no mandatory roadmap/epic tier is needed.
Prerequisites describe capabilities to verify in code/tests, not cross-change task
links or permanent completion receipts. Plan-only requests stop before implementation.

For example, rebuilding an online economy could start with reproducible player access,
an isolated starter, one durable production recipe, then a first sale. Regional freight
and multi-platform distribution are subsequent increments, not single tasks hidden
inside "deliver the pilot." Each slice integrates the behavior needed to demonstrate it.

When new requirements arrive, rerun these questions. Repair tasks within the current
boundary; scope separately acceptable additions as follow-up changes. Apply the
Reconcile the plan guidance in `../ow-plan/SKILL.md` when splitting active work so
unfinished obligations and completion evidence are preserved. Decomposition within
authorized scope needs no new permission; material scope/intent decisions still do.
New changes default to normal review; delegation is not inherited from a split parent.

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
