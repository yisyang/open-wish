# OpenWish policy

Humans ask. AI identifies needs, aligns design and engineering, implements, and
reviews. Humans review the results.

**Durable intent. Disposable plans. Code and tests carry the solution.**

- **Needs** (`openwish/needs/N-001.md`) record who needs what outcome, how to
  observe it, and genuine constraints. They stay binding after delivery.
- **Changes** (`openwish/changes/C-001/`) hold one reviewable increment's purpose,
  scope, working design, verification plan, tasks and latest review. They are
  deleted after acceptance once their useful knowledge lives elsewhere.
- **Code, tests and ordinary docs** carry what was built, how it is checked, and
  rationale that the code cannot express.

Default to one product/domain per repository, including a monorepo. This file is
project-owned: adapt it to the product.

## Adoption and proportion

OW is opt-in. Installed skills do not mandate using it; requests to work without
OW win. Initialize only when asked to adopt OW.

**Routine work** is clear, localized, reversible and within existing intent:
inspect → implement → verify → report. Create no need, change or acceptance step.

**Structured work** is substantive, involves consequential choices, or needs
resumable coordination. It uses one or more changes, each referencing the needs
it serves, and follows the skills: propose → align → plan → implement → review →
consolidate.

## Where knowledge lives

| Knowledge | Home |
| --- | --- |
| Actors, outcomes, acceptance, constraints | Current needs |
| Implemented behavior and interfaces | Source, types, schemas |
| Repeatable checks of intent | Tests and documented manual procedures |
| What a module or area is responsible for | A short header comment per module; a README at major boundaries |
| Non-obvious rationale and operational facts | Nearby comments or ordinary docs |
| Approved but unfinished detail | Another open change or retained domain data |
| Working design, tasks, review | The change, until disposal |

Needs hold no execution status: closing a change neither retires a need nor
proves it fully satisfied. `confirmed_at` records actual human confirmation only;
code shows behavior, not confirmed intent. Git holds history.

## Authority and communication

- A clear instruction to implement authorizes that scope. Plan-only and
  discussion-only requests stop before implementation.
- Technical repairs within authorized intent need no new permission. Material
  intent or scope changes need a real human decision.
- `ow ready` reports scheduling, not permission. Loading a skill grants nothing.
- Ask only questions that can materially change the work. Use numbered questions
  with two or three A/B/C options, put `(Recommended)` before the preferred option,
  and state each option's effect.
- Report as **need → outcome → evidence**, then limitations. Separate what you
  observed from assumptions and checks you did not run.

**Acceptance.** By default a human reviews structured results, then the agent runs
`ow close C-001 --by human`. Explicit fast-forward delegates acceptance for one
named change only (`--fast-forward` or `ow mode fast-forward C-001`, then `--by
fast-forward`). It never supplies missing manual observations, access, passing
checks or confirmation of inferred needs, and new changes default to human review.

## Skill map

Each rule has one owner. Read the owning section when a step calls for it.

| Guidance | Owner |
| --- | --- |
| Right-size intent, Right-size delivery, relationships | `ow-propose` |
| Architecture rubric | `ow-align` |
| Task sizing, Reconcile the plan, Strategic verification | `ow-plan` |
| Need assessment, Safe to forget | `ow-review` |
| Disposal, compaction, size targets | `ow-consolidate` |
| Delegated acceptance | `ow-fast-forward` |
| Adoption for an existing or new product | `ow-onboard` |

`openwish/artifacts.md` documents file formats and commands.
