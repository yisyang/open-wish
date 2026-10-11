# OpenWish product requirements

Humans ask. AI identifies needs, aligns design and engineering, implements, and
reviews. Humans review the results. OpenWish preserves product intent with
proportionate process overhead. These requirements describe the product, not an
OW workflow imposed on contributors. Architecture is in [design.md](design.md).

## Durable intent

- Needs are the only mandatory durable OW product knowledge. Record actors,
  independently valuable outcomes, observable acceptance, and genuine constraints.
  Keep implementation detail in code/tests or disposable working design.
- Match actor/outcome/acceptance before adding a need. Preserve stable IDs when
  intent evolves. Mechanisms, formats, interfaces, and tasks rarely warrant new
  needs. Asks remain conversational input, not permanent request journals.
- Current needs constrain all subsequent work after delivery. Currency is
  `current | retired`; execution state belongs to changes. Closing an increment
  never retires a need or proves its complete satisfaction.
- Distinguish inferred intent from human confirmation. Preserve constraints and
  independently valuable outcomes; surface real conflicts rather than silently
  weakening acceptance to make implementation easier.
- Right-size needs by outcome independence, not implementation effort. Reuse intent
  across mechanisms, split separable outcome bundles, and consolidate duplicates.
  Preserve meaning and reconcile references when IDs change; seek decisions for
  material intent changes. Retired needs can be removed by a retention decision.
- Store only useful, reasoned semantic relationships on needs. Derive the sparse
  graph without another durable artifact tier; relationships focus investigation
  but never exempt unlinked current needs from consideration. Reassess changed
  intent, neighboring facts, and possible new interactions instead of all pairs.

## Disposable execution

- Changes reference one or more needs directly, many-to-many. Each holds a bounded
  improvement's purpose, working design/engineering approach, verification plan,
  and tasks. Plans may evolve without synchronizing another persistent spec tier.
- Tasks have verifiable acceptance and concise direct completion evidence. Simple
  lists suffice; optional acyclic dependencies stay within the parent change.
  Continue independent work around manual blockers. Missing observations never pass.
- Retain task results through integration and final review. After accepted closure,
  dispose the change, tasks, and review together. Preserve useful knowledge in
  needs, code, tests, or ordinary repository docs before removal.
- Keep unknown files and unfinished work safe during cleanup. Preflight batch
  operations. Use Git for useful history rather than requiring OW archives or
  permanent execution/evidence ledgers.

## Proportionate collaboration

- Adoption is explicit. Installed/source skills do not mandate use; opt-outs win.
- Clear, localized, reversible changes within intent proceed directly through
  inspection, implementation, verification, and a concise result. No new need,
  change file, stage receipt, or acceptance ceremony is required.
- Substantive work prepares intent, design, and tasks together. Actual conversation
  instructions authorize their scope; ask only material questions. Plan-only
  requests stop at the plan. Technical repairs within scope need no reauthorization.
- Humans review structured results. Explicit fast-forward delegates acceptance
  only for its change. New changes default to normal review, including changes
  serving the same needs. Never invent confirmation, observations, or passing checks.

## Implementation and verification

- Code expresses implemented behavior; needs supply independent intent; tests
  provide executable checks of that connection. Avoid prose mirrors of code.
- Use the smallest set of fast, independent checks protecting affected needs and
  consequential failure modes. Reuse existing checks before adding tests; place
  them at representative outcomes, important pure decisions, and meaningful boundary
  contracts. Harmless refactors should normally preserve tests; need violations
  should fail them. A task or module does not automatically need a new test.
- Avoid brittle incidental wording/layout snapshots, private-call assertions,
  duplicated checks, and unjustified edge-case matrices. Exact assertions are useful
  for actual public or human-specified contracts. Credible costly failures merit
  focused checks even without a coverage request. Expand for risk, uncertainty,
  observed failures, or explicit requirements; honor requested coverage targets
  without confusing percentages or test counts with correctness.
- Keep regression tests for lasting obligations; discard temporary probes after
  preserving useful findings. Report current verification and remaining limitations,
  rather than requiring a permanent history of development-stage test runs.
- Favor functional cores, effects at boundaries, cohesive modules, explicit
  dependencies, thoughtful layout, and established dependencies. Preserve useful
  rationale that cannot be recovered from code near the implementation.
- Supply operational architectural criteria: discoverability, rule ownership/change
  locality, dependency/data ownership, explicit effects, independent outcome checks,
  justified complexity, and understanding after disposal. Evidence and consequences
  matter more than file size, named patterns, or a numeric architecture score.
- Establish greenfield architecture through a minimal conventional structure and
  representative end-to-end behavior. Evolve affected boundaries as asks arrive.
- Brownfield onboarding assesses representative code paths and proposes refactoring
  only when benefits justify cost/risk. Present incremental scope, baseline behavior
  checks, and verification/rollback; obtain approval before that additional work.
  Retaining satisfactory architecture is a valid recommendation.
- Reviews assess all current needs and relevant regressions with direct evidence.
  A change's latest review is disposable. Changed intent, approach, task evidence,
  policy, or repository content makes pending review stale before acceptance.
- Routine verification stays under five minutes; identify necessary slower checks.
  Final updates explain needs, outcomes, verification, and unresolved limitations.

## Bounded knowledge

- Include complete current need content without silent truncation: under 500 lines
  globally and a configurable estimated-token budget (6,000 by default).
- Keep each OW artifact under 500 lines. Source has an under-500 nonblank LOC soft
  target and under-1000 hard maximum. Exact-path data/low-complexity exceptions
  never exempt OW artifacts. Replace latest summaries rather than accumulating logs.
- Configuration, policy, and installer bookkeeping support the tool. They do not
  create more mandatory product knowledge layers.
- Warn before current-intent budgets fail; also consolidate on semantic overlap,
  mechanism-sized needs, broad bundles, and drift. Expose retention attention groups.
  Completion includes disposal or a stated deferral; reconcile abandoned-looking
  work explicitly. Per-file limits are not a global retention cap.
- Preserve repeatable checks/manual procedures and selective rationale, not copies
  of execution history in docs. Tests enable fresh evidence, not historical proof.
  Product needs may require historical evidence as product data; OW keeps no ledger.

## Adoption and distribution

- Support Python 3.11+ without third-party runtime dependencies. Model reasoning
  runs in the user's harness; OW has no provider SDK integration.
- Publish tested wheel/source distributions as `openwish`, exposing exact `ow`
  and `openwish` CLI aliases. Keep package/module/tag versions synchronized.
- Ship eight canonical skills with thin OpenCode, Claude Code, Codex, and generic
  Agent Skills adapters. Support interactive multi-selection and explicit flags;
  deduplicate shared integration paths.
- Reinitialization preserves project knowledge and local policy. Upgrade older
  integrations, preserve equal versions, and confirm downgrades. Preserve unknown
  unversioned files with actionable conflicts before writes.
- Support only the current schema. Before v1.0.0, favor simple breaking changes
  over migration tooling and legacy compatibility. Reject incompatible schemas
  before writes. Default to one product/domain per repository.
