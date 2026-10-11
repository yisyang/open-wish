---
name: ow-align
description: Establish or reassess architecture for substantive OW work, from a greenfield first slice to evolving an existing product. Align design with current needs using code-grounded trade-offs. Honor OW opt-outs and plan-only scope.
---

# Align

Read `openwish/policy.md`, `ow context C-001`, the change, and relevant code/tests.
Routine work follows the lightweight path without creating design records.

1. Review all current needs, including delivered outcomes. Retrieve retired needs
   when useful for history without making them binding again. Inspect affected
   modules, interfaces, consumers, tests, and operational constraints.
2. Distinguish incompatible intent from an implementation that cannot yet satisfy
   compatible needs. Adapt the solution; never silently weaken acceptance.
   Clarify actual decisions with numbered A/B/C options and `(Recommended)` before
   the preferred text. Technical repairs within authorized intent need no new permission.
3. Apply the architecture rubric below to representative behavior and the affected
   dependency paths. Compare retaining the current structure with the smallest
   useful improvement. Cite actual code, tests, or operational constraints for
   consequential trade-offs; do not infer quality from file size or pattern names.
4. Put the working design in the change's approach: responsibility/data ownership,
   dependency direction, effects, meaningful alternatives, and verification of
   preserved constraints. For greenfield work, start with a representative end-to-end
   slice and conventional layout; introduce boundaries for demonstrated needs.
   For later asks, look for duplicated rules, responsibility spread, and effects
   leaking into decisions. Evolve the affected structure rather than redesigning
   the whole product or anticipating hypothetical platforms.
5. Plan to preserve only otherwise unrecoverable rationale near code or in ordinary
   repository docs. The approach remains disposable; do not create a parallel
   persistent spec, design registry, or another artifact tier.
6. Continue to `ow-plan` without a stage approval. A material intent revision
   returns to Propose. Verification-only work can use an empty task list and an
   honest verification plan rather than invented implementation.

## Architecture rubric

Use these questions proportionately in alignment, onboarding, and review. A useful
finding connects **observation → consequence → improvement → verification**.
Keep assessments in conversation or the active change, not a permanent scorecard.

| Question | Useful evidence | Friction to investigate |
| --- | --- | --- |
| Can a maintainer find behavior? | Domain/responsibility names, clear entry points and interfaces | Generic helpers or hidden dispatch obscure the path |
| Does a rule have one owner? | Changes to one rule stay reasonably local | Duplicated decisions or one responsibility scattered across modules |
| Are dependencies explicit? | Understandable direction, clear data ownership and contracts | Cycles, hidden globals, leaking implementation details |
| Can decisions run independently? | Explicit inputs and outputs, pure calculations and transitions | Business decisions require network, database, clock, or environment access |
| Do tests check intent? | Small, fast checks of stable outcomes, invariants, and consequential failures | Incidental snapshots, private-call assertions, duplicated or speculative cases |
| Is complexity earning its cost? | Boundaries serve current behavior and constraints | Speculative frameworks, unnecessary layers, arbitrary file splitting |
| Will disposal preserve understanding? | Code/tests explain behavior; nearby rationale explains non-obvious choices | The working plan is the only map or explanation |

Prefer pure functions for decisions, validation, transformations, and state
transitions. Pass time, randomness, configuration, and external results explicitly
when they affect decisions. Keep I/O and mutation at identifiable boundaries;
use direct core and focused integration checks where each adds evidence. An application
needs effects; do not add elaborate wrappers merely to claim purity.

Use Strategic verification in `../ow-plan/SKILL.md` to choose checks that protect
the affected needs without freezing the design. Existing outcome checks may already
cover the work; do not require a new test for every module or architecture boundary.

Use `ow graph N-001 --json` when investigating established intent relationships.
Relations narrow investigation, not regression obligations: all current needs
still matter, and missing edges do not prove independence. Reuse the working
assessment while its inputs hold; revisit changed needs, their neighbors, possible
new interactions, and affected code rather than repeating an all-pairs analysis.
