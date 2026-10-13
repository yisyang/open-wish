---
name: ow-plan
description: Turn an aligned OW change into executable tasks and proportionate verification. Reconcile grown scope or stale plans before execution. Routine changes need no records; respect plan-only requests and OW opt-outs.
---

# Plan

Read `openwish/policy.md`, `ow context C-001`, the change's approach, and the
affected source and tests.

1. **Confirm the boundary** (Right-size delivery in `ow-propose`): delivers now,
   preserves, defers, exit evidence. If the plan already exists, apply Reconcile the
   plan below before trusting it.
2. **Write tasks** in `changes/C-001/tasks.json` (format in `openwish/artifacts.md`)
   using Task sizing below. Add `depends_on` only for real prerequisites within the
   change; order the list sensibly. Mark observations only a human can make as
   `kind: "manual"`.
3. **Plan verification** using Strategic verification below.
4. **Check coverage.** Every delivers-now result and consequential constraint has
   planned work or existing direct evidence; every task serves the scope. Note the
   mapping in the change when it is not obvious. Run `ow check`; passing structure
   does not make a plan feasible.
5. **Stop or continue.** Plan-only requests present the increments, approach, tasks
   and open questions, then stop. Otherwise, if authority or a consequential choice
   is missing, ask once (numbered A/B/C, `(Recommended)`); then continue to
   `ow-implement`.

## Task sizing

A task is a concrete unit of implementation or investigation whose result can be
checked directly. Its acceptance describes behavior or evidence, not "build the
subsystem and test it".

**No invented policy.** Before calling a task executable, ask whether an implementer
could finish it without inventing a material product rule. Write the needed
behavior, actors, exceptions, units, boundaries and consequences (money,
permission, recovery) into the approach. For example, "late fees start after 14
days" does not say whether day 14 itself is late, whether closed days count, or
which timezone applies. Work a boundary example and get a decision before
implementing. An investigation task ends with findings and a decision or proposal,
never with the feature claimed as delivered.

- Split when completion needs unrelated evidence, hidden design, or separately
  blockable work. Promote an independently acceptable deliverable to its own change.
- Keep coherent implementation and its focused checks in one task. No task per file
  or function. A short list that hides projects is worse than a longer honest one.
- Integrate representative behavior early; avoid a final "integrate and test
  everything" task that first proves the parts work together.
- Decide early where each material rule and check will be retained. Approved
  deferred detail goes into its own open change or domain data now.

## Reconcile the plan

On resumption, new requirements or changed decisions, compare the conversation,
needs, scope, tasks, evidence and the actual repository:

1. Resolve contradictions first. If a decision is recorded but its task still waits
   on it, update the task and its dependents. Mark a task done only with evidence
   that its whole acceptance is met; keep remaining application or observation
   work visible.
2. Recheck scope with Right-size delivery. When splitting, give each unfinished
   obligation to a specific change or task, repair qualified IDs and dependencies,
   and keep useful evidence with the work it supports. Moved work is not done work,
   manual checks stay, and pending reviews must be refreshed.
3. Before an earlier change is disposed, rewrite successors' prerequisites in terms
   of delivered code, interfaces and checks.
4. Recompute `ow ready`, continue independent authorized work, and ask only for
   missing evidence, authority, or material scope decisions.

## Strategic verification

Choose the smallest set of fast, independent checks that protects the affected
needs and the failures that would matter. Test count and coverage percentage are
not goals.

- Ask: what important behavior could break, which existing checks already protect
  it, what is the smallest check that closes a real gap, and what stays unverified?
- Check at the levels that add distinct evidence: a few need-level outcomes,
  important pure decisions and invariants, and consequential integration contracts.
- Derive expected results from intent, not from the implementation. A harmless
  refactor should leave tests passing; violating a need should fail one.
- Avoid asserting incidental wording, layout, helper names or private call order.
  Assert exact text, schema or layout narrowly when it is a real contract.
- Cover credible costly failures (data loss, wrong charges, privacy leaks) even
  unrequested. Expand for risk, observed failures or explicit requirements; honor
  requested coverage targets without treating 100% as correctness.
- **Link checks to needs.** When a retained test protects a need-level outcome,
  mention the need ID in its name, docstring or comment so `ow trace` finds it.
  Do not tag source modules or helpers.
- Keep routine verification under five minutes and name any slower checks needed.
  Delete temporary probes once their findings are preserved.
