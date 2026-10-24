---
name: ow-plan
description: Turn an aligned OW change into executable tasks and proportionate verification, or plan direct work in the session. Reconcile grown scope or stale plans before execution. Respect plan-only requests and OW opt-outs.
---

# Plan

Load `ow-core`, then read `openwish/policy.md` and the affected source and tests.

- **Direct:** run `ow context`. Plan in the session: the requested result is the
  boundary; name the files, the checks (Strategic verification below) and what
  stays unverified. Write no tasks.
- **Managed:** run `ow context C-001`, read the change's approach, and follow the
  steps below.

1. **Confirm the boundary** (Right-size delivery in `ow-propose`): delivers now,
   preserves, defers, exit evidence. If the plan already exists, apply Reconcile the
   plan below before trusting it; for a change without tasks, apply Plan a candidate.
2. **Write tasks** in `changes/C-001/tasks.json` (format in the `ow-core` artifact reference)
   using Task sizing below. Add `depends_on` only for real prerequisites within the
   change; order the list sensibly. Mark observations only a human can make as
   `kind: "manual"`.
3. **Plan verification** using Strategic verification below.
4. **Check coverage.** Every delivers-now result and consequential constraint has
   planned work or existing direct evidence; every task serves the scope. Note the
   mapping in the change when it is not obvious. Run `ow check`; passing structure
   does not make a plan feasible.
5. **Challenge the plan.** Name the strongest plausible reason it would fail: a
   capability nobody provides, a known later need it would force rework for, an
   assumption nobody checked, an environment nobody has accessed, a surface the
   human has not seen. Repair the plan,
   or add an investigation (Discover ahead of delivery below).
6. **Stop or continue.** Plan-only requests present the increments, approach, tasks
   and open questions, then stop. Otherwise, if authority or a consequential choice
   is missing, ask once (Commit progressively below). A question holds only the
   tasks whose result depends on it, and authorized work needs no fresh approval:
   continue to `ow-implement`.

## Task sizing

A task is a concrete unit of implementation or investigation whose result can be
checked directly. Its acceptance states one checkable behavior or piece of evidence
in a sentence or two, not "build the subsystem and test it"; five criteria are
usually several tasks. `files` names specific paths, or stays empty.

**No invented policy.** Could an implementer finish the task without inventing a
material product rule? Record the needed behavior, actors, exceptions, units,
boundaries and consequences (money, permission, recovery) in their retained home
(need, rule doc or domain data) and link it from the approach, which keeps only
this slice's design and fixtures. "Late fees start after 14 days" does not say
whether day 14 is late, whether closed days count, or which timezone applies: work
a boundary example and get a decision first. An investigation task
(`kind: "investigate"`) ends with findings and a decision or proposal, never with the
feature claimed as delivered; delivery tasks that need its answer depend on it.

- Split when completion needs unrelated evidence, hidden design, or separately
  blockable work. Promote an independently acceptable deliverable to its own change.
- Keep coherent implementation and its focused checks in one task. No task per file
  or function. A short list that hides projects is worse than a longer honest one.
- Integrate representative behavior early; no final "integrate and test everything"
  task that first proves the parts work together or repeats earlier checks.
  Whole-increment criteria belong in the change's exit evidence.
- Decide early where each material rule and check will be retained. Approved
  deferred detail goes into its own open change or domain data now.

## Commit progressively

Resolve uncertainty before the commitment it could disrupt, not before all work.

- **Commitment points** are where a wrong answer becomes expensive: persisted data
  shapes and migrations of user data, rules that move money or grant permission,
  public or cross-component interfaces, deploys and other outward effects, and
  removing behavior people rely on. Work toward a commitment may proceed; the
  commitment itself waits for the decisions its result depends on. Block the
  smallest coherent unit: a task, not its change; a change, not the sequence.
- **Reversible choices** can be changed later within code and tests alone, with no
  stored data, published contract or outward effect to migrate. Ask with a
  recommended option. If work reaches the choice unanswered, proceed on the
  recommendation: label it `proposed` in its home (Rule status in `ow-propose`),
  keep the question in `open`, and name it in the next report. An assumption stands
  in for a product rule only as a labeled placeholder; it never decides the rule,
  and it never reaches a commitment point.
- **Unseen surfaces.** A screen, page or other layout people will work in that the
  human has not seen is costly to learn late; approved components or styles do not
  approve its composition. Before building it out, show a quick preview (sketch,
  static mock or a probe's screenshot) in an `investigate` task that awaits their
  reaction, and record the accepted composition in its retained home.
- **Costly investigations.** An investigation that will take hours of work, large
  simulations or extensive evidence is itself a commitment point. Before starting
  it, ask the open human questions whose answers would change what it measures
  (cadence, scale, which options), in one batch. If one stays unanswered, keep the
  investigation small or label every result that depends on the assumption.
- **Ask through cases.** Show an ordinary case, a boundary, competing claims, and a
  failure or recovery, each with the outcome every option produces. Humans choose
  product consequences; settle technical facts (library behavior, performance,
  access) with a bounded experiment instead of a question.
- **Batch questions.** One numbered A/B/C set per pause, hard-to-reverse first, each
  naming the work it holds. An unanswered question is an investigation marked
  `blocked` with the question as its evidence; `ow ready` lists them as `ASK`. Fold each answer into its home (need, rule doc or data),
  then apply Reconcile the plan.
- **Bounded loops.** Repeat inspect, investigate, ask only while each pass adds
  evidence, tests an alternative or resolves a contradiction. When a pass does none
  of these, stop and present what remains.

## Discover ahead of delivery

For a sequence, look for consequential unknowns across every open change, not only
the next one. Rank them by the cost of learning late: how much later work depends
on the answer, whether it shapes persisted data or a public interface, how long
finding out takes, and the last point it can arrive without disrupting work.

Give each one an `investigate` task in the change whose result depends on it.
Investigations run before that change's predecessors pass, and starting one does
not start the change. In flight means in progress or awaiting an answer (`ASK` in
`ow ready`); keep two or three, so a human gets one reviewable question batch at a
time, not a stream. Place findings in their retained home; a candidate holding
only investigations is still unplanned.

## Plan a candidate

A candidate is an open change without delivery tasks (investigations may have run);
`ow ready` shows it as `PLAN` once its `after` predecessors pass. Plan it when it is
about to start: a plan written earlier goes stale while other work lands.

1. **Verify its prerequisites in the repository** (code, interfaces, checks); a
   passing predecessor is a reason to look, not proof. If one is missing, record
   that in the change and stop; add any missed predecessor to `after`. If a material
   decision is open, task only work whose result does not depend on it, plus
   investigations that can run now. Rewrite prerequisites that cite a disposed
   change as the delivered code and checks.
2. **Refresh the approach** to what was actually delivered: real interfaces, names
   and constraints replace old assumptions. Material design differences return to
   `ow-align`, intent changes to `ow-propose`.
3. **Write tasks** as above, then continue only within authorized scope.

## Promote direct work

When direct work needs coordination (`ow-core`), create one change for the whole
requested result, not only the remainder:

1. Write scope, approach and exit evidence from the repository as it now is, not
   as a history of the session.
2. Record completed work as done tasks only with direct evidence, carrying its
   checks forward; do not redo verified work.
3. Add the remaining work as open, blocked or manual tasks, and new questions to
   the need's `open` list.
4. Continue independent work under the same authority.

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
   manual checks stay, and pending reviews must be refreshed. After splitting,
   reordering or deferring, recheck the affected sequence (Check the sequence in
   `ow-propose`).
3. Recompute `ow ready`, continue independent authorized work, and ask only for
   missing evidence, authority, or material scope decisions.

## Strategic verification

Choose the smallest set of fast, independent checks that protects the affected
needs and the failures that would matter. Test count and coverage percentage are
not goals.

- Ask what important behavior could break, which checks already protect it, what
  smallest check closes a real gap, and what stays unverified.
- Check at levels that add distinct evidence: a few need-level outcomes, important
  pure decisions and invariants, and consequential integration contracts.
- Derive expected results from intent, not from the implementation. A harmless
  refactor should leave tests passing; violating a need should fail one.
- **Settle outcomes, not alternatives.** A check that accepts several outcomes for
  one input, such as a race that may end either way, is evidence only when intent
  allows each of them. When they differ in money, rights or data, the rule is
  undecided: ask, or record it in `open`, rather than pass the check.
- Avoid asserting incidental wording, layout, helper names or private call order.
  Assert exact text, schema or layout narrowly when it is a real contract.
- Cover credible costly failures (data loss, wrong charges, privacy leaks) even
  unrequested. Expand for risk, observed failures or explicit requirements; honor
  requested coverage targets without treating 100% as correctness.
- **Link checks to needs:** a retained test protecting a need-level outcome mentions
  the need ID in its name, docstring or comment for `ow trace`; source and helpers
  stay untagged.
- **Recompute worked examples once.** A rule doc's worked examples get one retained
  check that reads their inputs and expected results from the doc; a value it must
  restate quotes the doc text, so editing either side fails it. Before product code
  exists, keep it small and outside shipped code; adding it is implementation, not
  investigation (`ow-core`). It protects no delivered outcome, so it names no need
  IDs. Once product tests replay an example (Architecture rubric in `ow-align`),
  drop its recomputation and keep only the quote check for values those tests
  restate. Run it when the doc, its data or the checked code changes; assessments
  and reviews cite its passing run at the current revision instead of recomputing by
  hand.
- **Fix the bar when planning.** Each task's acceptance names the checks that settle
  it, with commands and thresholds where running cost, timing or recovery matter.
  Reviews judge against them (Blocking findings in `ow-review`). Repeat a run only
  to settle a known-flaky result, and add mutation matrices or repeated full-suite
  runs only when the acceptance needs them.
- Keep routine verification under five minutes and name any slower checks needed.
  Delete temporary probes once their findings are preserved.
