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
- Favor functional cores, effects at boundaries, cohesive modules, explicit
  dependencies, thoughtful layout, and established dependencies. Preserve useful
  rationale that cannot be recovered from code near the implementation.
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
