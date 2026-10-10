# OpenWish product requirements

OpenWish helps humans and coding agents preserve product intent while delivering
software with proportionate process overhead. These requirements describe the
product; they do not impose an OW workflow on contributors to this repository.
Architecture and implementation contracts are in [design.md](design.md).

## Durable intent

- Record actors, independently valuable outcomes, observable acceptance, and
  genuine constraints. Keep requested mechanisms in specs rather than inventing
  a need for each feature, interface, command, or implementation task.
- Match existing actor/outcome/acceptance before adding a need. Preserve stable
  IDs when revising or reopening structured work. Asks remain in conversation;
  there is no request log or replacement change-record hierarchy.
- Current needs constrain subsequent work even after delivery. Currency
  (`current`, `retired`) and implementation (`open`, `in-progress`, `review`,
  `approved`) are independent. Surface real conflicts without silently weakening
  acceptance or retiring inconvenient constraints.

## Proportionate collaboration

- OW adoption is explicit. Installed/source skills do not mandate their use, and
  user opt-outs take precedence over the product's workflow defaults.
- Clear, small, reversible changes within intent proceed through inspection,
  implementation, meaningful verification, and a concise result. They require
  no needs/epics, gate receipts, reopen cycle, or acceptance ceremony.
- Substantive work prepares intent, design, and a plan together. Use existing
  conversation authority or one combined decision to authorize that scope.
  Respect plan-only requests and clarify consequential uncertainty. Technical
  plan repairs within authorized intent do not require renewed permission.
- Structured default work retains final human acceptance. Explicit fast-forward
  delegates that acceptance too, with honest provenance and revision-limited scope.
  Never invent human confirmation, manual observations, or passing checks.

## Executable, regression-aware work

- Spec designs own many-to-many need references. Keep containment separate from
  prerequisite relationships. Reuse capability specs rather than splitting them
  to manipulate authorization.
- Epics may select a nonempty subset of their specs' needs as execution scope.
  Other linked needs remain regression constraints without blocking unrelated work.
- Tasks have verifiable acceptance and explicit prerequisites with increasing
  group/order pairs. Detect cycles, missing references, and forward dependencies.
  Continue independent agent work while manual observations or other authority wait.
- Reviews cover selected outcomes and affected current needs with direct evidence.
  Changed plans, code, or task evidence invalidate review freshness. Lifecycle
  dates distinguish confirmed intent from accepted implementation verification.
- Routine verification stays under five minutes; identify necessary slower checks.
  Final updates explain purpose, outcome, verification, and unresolved limitations.

## Bounded, maintainable knowledge

- Include all current needs in context without silent truncation: under 500 lines
  and a configurable estimated-token budget (6,000 by default).
- Keep each OW artifact under 500 lines. Source has an under-500 nonblank LOC soft
  target and under-1000 hard maximum; exact-path data/low-complexity exceptions do
  not exempt OW artifacts. Prefer functional cores and established dependencies.
- Replace latest summaries rather than accumulating journals. Promote current
  contracts and environment/secret references before removing completed execution
  detail. Preserve unresolved limitations and acceptance; Git holds history.

## Adoption and distribution

- Support Python 3.11+ without third-party runtime dependencies. Model reasoning
  runs in the user's harness, not through provider SDKs in OW.
- Publish tested wheel/source distributions as `openwish`. Install exact `ow` and
  `openwish` aliases to the same CLI entry point, with `ow` canonical in examples.
  Release tags, package metadata, and CLI versions agree; GitHub releases publish
  tested artifacts through Trusted Publishing, with TestPyPI for rehearsals.
- Ship eight canonical skills and thin adapters for OpenCode, Claude Code, Codex,
  and generic Agent Skills. Support interactive harness multi-selection and
  explicit flags for automation; shared integration paths are deduplicated.
- Reinitialization preserves project knowledge and local policy. Upgrade older
  integrations, leave same-version files untouched, and confirm downgrades.
  Preserve unknown unversioned files with an actionable conflict before writes.
- Onboarding distinguishes inferred intent from confirmed needs and unverified
  behavior from accepted delivery. Default to one product/domain per repository.

## Repository practice

The former self-hosted OW tree contained six broadly distinct outcome areas:
intent preservation, collaboration, bounded context, execution, review, and
adoption. Shared spec references were not evidence of duplicate needs. However,
adoption mixed packaging, onboarding, and cleanup details, and a separate alias
spec was introduced solely to escape shared-spec authorization. Those details
belong in capability contracts and tests, not additional approval boundaries.

These requirements preserve the useful intent from that tree. Generated harness
copies, operational gate/review state, and the completed alias epic have been
removed from the active checkout. OW is tested in disposable projects; ordinary
development here uses `CONTRIBUTING.md` without self-imposed OW gates.
