---
name: ow-align
description: Establish or reassess architecture for substantive OW work, from a greenfield first slice to evolving an existing product. Align the working design with all current needs using code-grounded trade-offs. Honor OW opt-outs and plan-only scope.
---

# Align

Load `ow-core`, then read `openwish/policy.md` and the affected code and tests.

- **Direct:** run `ow context`; apply steps 1–4, 6 and 7 in the session. Write no
  Approach.
- **Managed:** run `ow context C-001` and read the change; apply every step.

1. **Know the constraints.** Every current need binds, including delivered ones,
   as do the engineering requirements the project policy links. Inspect affected modules, interfaces, consumers, tests and operational limits.
   Use `ow graph N-001 --json` and `ow trace N-001` to find related intent and the
   checks protecting it; neither proves that unlinked needs are unaffected.
2. **Separate conflict from difficulty.** Distinguish intent that truly conflicts
   from an implementation that cannot yet satisfy compatible needs. Adapt the
   solution; never quietly weaken acceptance. Ask for a decision (A/B/C) only for a
   real conflict.
3. **Assess** the affected paths with the Architecture rubric below. Compare keeping
   the current structure with the smallest useful improvement, citing actual code,
   tests or operational constraints.
4. **Test against future constraints** (below) whenever the work creates or reshapes
   something hard to change later.
5. **Write the working design** in the change's Approach: responsibilities and data
   ownership, dependency direction, where effects happen, alternatives that matter,
   and how each preserved constraint will be verified. Check the boundary against
   Right-size delivery in `ow-propose`.
   - Greenfield: a conventional minimal layout and one representative end-to-end
     slice; add boundaries when behavior demands them.
   - Later asks: look for duplicated rules, scattered responsibilities and effects
     leaking into decisions; evolve only the affected structure.
6. **Plan what survives.** Decide where non-obvious rationale will live (a module
   header, a boundary README, a nearby comment) so the change can be deleted later.
7. **Continue** to `ow-plan`. A material intent revision returns to `ow-propose`.

## Architecture rubric

Use these questions proportionately in alignment, onboarding and review. A useful
finding connects **observation → consequence → improvement → verification**.

| Question | Good signs | Friction to investigate |
| --- | --- | --- |
| Can a maintainer find behavior? | Domain names, clear entry points, a one-line responsibility header per module, a README at major boundaries | Generic helpers, hidden dispatch, headers that no longer match the code |
| Does each rule have one owner? | Changing a rule stays local, in code and in docs | Duplicated decisions; one responsibility spread across modules; docs restating rule values by hand |
| Are dependencies explicit? | Clear direction, data ownership and contracts | Cycles, hidden globals, leaking internals |
| Can decisions run without effects? | Pure calculations and transitions with explicit inputs | Business rules that need network, database, clock or environment |
| Do tests check intent? | Small, fast checks of outcomes and invariants | Snapshots of incidental output, private-call assertions |
| Does complexity earn its cost? | Boundaries serve current behavior | Speculative frameworks, layers, arbitrary file splits |
| Will deleting the change lose understanding? | Code, tests and nearby rationale explain the behavior | The change's plan is the only map |
| Is running cost proportionate? | Idle work near zero; reads use snapshots, not writers' locks; payloads sized to the view; logs record changes | Fixed-interval full-state polling, locks on read paths, unbounded payloads, a log line per idle poll or tick |
| Can dense rules be checked before they are wired? | Rule-heavy logic (money, scheduling, scoring) runs as pure functions whose tests replay the rule doc's worked examples | Rules first exercised through UI or database; worked examples nobody recomputed |

## Future constraints

Foundational designs (persisted data models, identities and ownership, money and
permission rules, public or cross-component interfaces) are built early and carry
every later need. Read the current needs this work does not deliver, including
those no change covers yet, and ask of each relevant one: **what would we have to
change when it arrives, and what happens to existing data?** For each material
answer choose one, and say which in the Approach:

- **Preserve the constraint now** when that is cheap: a seam, a field, an owner
  list instead of a single owner. Do not build the later feature.
- **Resolve it first** when the answer changes this shape: ask, or add an
  investigation, before the commitment (Commit progressively in `ow-plan`).
- **Record an affordable evolution path** when changing later is cheap: the
  migration or extension it would take, and why existing data survives it.

**Effects.** Prefer pure functions for decisions, validation, transformations and
state transitions. Pass time, randomness, configuration and external results in
explicitly. Keep I/O and mutation at identifiable boundaries. Do not wrap effects
elaborately just to look functional.

**Orientation comments.** A module header states, in a line or two, what the module
owns and any non-obvious rule or boundary. A README belongs only at major boundaries
(top-level packages, services, plugin roots): responsibilities, entry points,
dependency direction, invariants and how to run its checks. Keep IDs, statuses and
dates out of both; they go stale. A wrong header is worse than none.
