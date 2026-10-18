---
name: ow-assess
description: Assess whether an OW product's needs and change sequence are ready to deliver what was asked, find the uncertainty most costly to learn late, and turn it into investigations and one question batch. Use before a long sequence, when asked how ready or risky a plan is, or after a batch of decisions lands. Honor OW opt-outs and assessment-only requests.
---

# Assess

Load `ow-core`, read `openwish/policy.md` and run `ow context`, `ow ready` and `ow trace`; use
`ow graph --json` to find related needs. Read the referenced rule docs and the
code, checks and setup that already exist. A passing `ow check` is structure, not
readiness. Scale the pass to the plan: a three-change sequence needs minutes.

1. **Fix the horizon.** What should be deliverable: the next change, a pilot, the
   whole ask? Use the human's statement, or assume the nearest milestone the
   needs or sequence name and say so. Needs beyond the horizon do not count against
   coverage, but still constrain foundational designs (Future constraints in
   `ow-align`).
2. **Rate each item 1–5** with cited evidence (1 missing, 3 workable with known
   gaps, 5 nothing material left), labelling what you checked versus inferred:

   | Item | Question |
   | --- | --- |
   | Intent | Are actors, outcomes and acceptance clear, with undecided rules in `open` and rule docs marked (Rule status in `ow-propose`)? |
   | Coverage | Is every criterion in the horizon met, planned or held with a reason (Check the sequence in `ow-propose`)? |
   | Rules | Do rule docs agree with needs and each other, and do their worked examples recompute? A passing recompute check at this revision is the evidence (Strategic verification in `ow-plan`). |
   | Sequence | Does each prerequisite have a provider and a check, and do early foundational designs survive later needs? |
   | Decisions | Which open items sit on the path to the horizon, and which commitment points do they hold? |
   | Execution | Do the toolchain, environments and access the next changes need actually work? Check what is cheap to check. |
   | Verification | Would each change's exit evidence catch a violation of its needs? |

3. **Pre-mortem.** Assume the horizon was missed or needed major rework. Give the
   three most plausible causes, each traced to a finding. Prefer causes that
   structural checks cannot see, such as the human rejecting the first look at a
   surface nobody previewed (Unseen surfaces in `ow-plan`), or an expensive
   investigation built on a question nobody asked (Costly investigations).
4. **Queue discovery** (Discover ahead of delivery in `ow-plan`): each consequential
   unknown with what depends on it, its commitment point, whether it is reversible,
   and the last point it can be learned. Rank by the cost of learning late.
5. **State confidence** for the horizon, and for nearer milestones when useful, as a
   rough chance the plan as written delivers without major rework. Name the two or
   three findings that move it most. It is a judgment, not a computed score.
6. **Recommend** in order of leverage, each as finding → consequence → action →
   who acts (agent, human decision, access) → evidence that it worked. Separate what
   the agent can do now from what waits on a human.
7. **Record or stop.** Assessment-only requests present the result and stop. When
   planning is requested or authorized, record the queue as `investigate` tasks,
   new questions in needs' `open`, sequence repairs (Check the sequence), and one
   question batch (Commit progressively in `ow-plan`).

Assess again when the horizon or a foundational design changes, after a batch of
answers lands, or when reviews keep reporting plan misses. Lessons recorded in the
project's policy are part of what you check.
