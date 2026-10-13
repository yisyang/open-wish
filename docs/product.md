# OpenWish product requirements

Humans ask. AI identifies needs, aligns design and engineering, implements, and
reviews. Humans review the results. OpenWish preserves product intent with
proportionate process overhead. These are product requirements, not a workflow for
contributors; architecture is in [design.md](design.md).

## Durable intent

- Needs are the only mandatory durable OW product knowledge: actor, independently
  valuable outcome, observable acceptance, genuine constraints. Implementation detail
  lives in code, tests or the disposable change.
- Current needs bind all later work after delivery. Currency is `current | retired`;
  needs carry no execution state, and closing a change never retires or completes one.
- Inferred intent stays distinguishable from human confirmation, at statement level.
  Translation preserves material conditions, exceptions, units and consequences.
- Needs are sized by outcome independence, not effort; mechanisms reuse existing
  needs; duplicates merge and bundles split with stable IDs where possible.
- Optional need references point to retained files with detailed rules or data.
  Optional reasoned relations (`requires`, `constrains`) live on needs; the graph is
  derived on demand. Unlinked current needs still bind.

## Disposable execution

- Changes reference needs many-to-many and hold one reviewable increment's purpose,
  scope (delivers now, preserves, defers), approach, exit evidence and tasks.
- Changes are bounded by results that stay useful if later work is postponed. Broad
  asks become sequences; future candidates can be open changes with empty task lists.
- Tasks have checkable acceptance and direct completion evidence; dependencies stay
  within their change. Independent work continues around manual blockers.
- Executable tasks do not require inventing product policy; consequential unknowns
  get a worked example and a decision first.
- A change is safe to forget before it passes review: each material requirement has a
  retained destination and evidence, or an explicit disposition. Approved unfinished
  detail gets a retained home immediately.
- After acceptance, the change, tasks and review are deleted together. Cleanup
  preflights the whole batch, preserves unknown files, and rejects missing or
  dependent destinations. Git holds history.

## Proportionate collaboration

- Adoption is explicit; installed skills do not mandate use and opt-outs win.
- Routine work goes inspect → implement → verify → report, with no records.
- Conversation instructions authorize scope; only material questions are asked;
  plan-only requests stop at the plan; technical repairs need no new permission.
- Humans accept structured results by default. Explicit fast-forward delegates
  acceptance for one change only and never invents confirmation, observations or checks.
- Workflow guidance is concise, with one owner per rule, so agents spend their context
  on the product rather than on the framework.

## Implementation and verification

- Code expresses behavior; needs supply independent intent; tests check the connection.
- Use the smallest set of fast, independent checks that protects affected needs and
  costly failures. Avoid incidental snapshots, private-call assertions and speculative
  matrices; honor explicit coverage requirements without equating them with correctness.
- The code-to-intent link is derived from the code: tests mention the need IDs they
  protect, and `ow trace` reports them. No separate traceability record is kept.
- Modules carry short responsibility headers and major boundaries a README; neither
  holds IDs, statuses or dates.
- Prefer functional cores, effects at boundaries, cohesive modules and explicit
  dependencies, assessed with an evidence-based architecture rubric.
- Greenfield work starts with a minimal structure and an end-to-end slice. Brownfield
  onboarding proposes refactoring only when it earns its cost, with human approval.
- Reviews assess every current need: linked and other affected needs with direct
  evidence, the rest recorded as assessed and unaffected. Any change to a pending
  review's inputs makes it stale, and the CLI names what changed.
- Review freshness includes recursive submodule revisions and content; uninspectable
  components prevent fresh acceptance. Routine verification stays under five minutes.

## Bounded knowledge

- All current need content enters context without truncation. A configurable 24,000
  estimated-token soft target warns at 80% and never blocks inspection.
- OW artifacts warn at 8,000 estimated tokens and source at 500 nonblank lines; a source
  hard limit is opt-in with justified exact-path exceptions.
- Context reports sized retrieval entries rather than loading referenced files.
- Status exposes cleanup candidates, pending acceptance, blocked work and retired needs.

## Adoption, distribution and evaluation

- Python 3.11+, no third-party runtime dependencies, no model API calls.
- Published as `openwish` with identical `ow` and `openwish` commands; package, module
  and bundled skill versions advance together.
- Eight canonical skills with thin OpenCode, Claude Code, Codex and generic adapters;
  interactive and explicit harness selection; preserving, version-aware reinstall.
- Only the current schema is supported before v1.0.0, rejected before any write.
- Skill evaluations compare OW against a no-OW baseline on executable, multi-session
  scenarios, grade behavior mechanically where possible (acceptance checks, seeded
  mutants against retained tests), and record time and token cost.
