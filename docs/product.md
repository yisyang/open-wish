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
- Inferred intent stays distinguishable from human confirmation, at statement level:
  `confirmed_at` covers every acceptance criterion; undecided product questions and
  proposals wait in a need's `open` list, which status surfaces until they are decided
  and context marks not binding; engineering unknowns wait in the change that depends
  on them. Rule docs tag each rule confirmed, approved-initial, inferred, engineering,
  proposed or open. A choice users would notice that intent leaves open is proposed, never
  engineering, and results lead with such choices so the human can overrule them.
  Translation preserves material conditions, exceptions, units and consequences.
- Needs stay true while the product is tuned and rebuilt: acceptance holds the
  guarantees actors rely on and structural rules in readable sentences. How a rule is
  computed is designed in the change, then carried by code and tests; referenced rule
  docs keep tagged rules, calibration and worked examples, and ordinary docs keep
  setup. Each fact has one home that other artifacts link to, and a rule several needs
  depend on lives in one of them; a doc view generated from domain data and kept
  current by a check is not a second home. Needs never depend on files a fresh clone
  lacks.
- Needs are sized by outcome independence, not effort; mechanisms reuse existing
  needs; duplicates merge and bundles split with stable IDs where possible. How the
  product is built is not a need: project-wide engineering requirements (setup,
  checks, releases) live in an ordinary doc the project policy links, and reviews check them.
- Optional need references point to retained files with detailed rules or data.
  Optional reasoned relations (`requires`, `constrains`) live on needs; the graph is
  derived on demand. Unlinked current needs still bind.

## Disposable execution

- Changes reference the needs whose outcomes they advance, many-to-many; needs they
  only respect still bind through review. A change holds one reviewable increment's purpose,
  scope (delivers now, preserves, defers), approach, exit evidence and tasks.
- Changes are bounded by results that stay useful if later work is postponed. Broad
  asks become sequences; only ready increments (prerequisites delivered, decisions
  made) get tasks, and the rest stay open changes with empty task lists that are
  planned against delivered code when they are about to start. Changes name predecessors in
  `after`; successors may start once predecessors pass review (configurable to wait
  for acceptance), acceptance follows the sequence, and `ow ready` surfaces what
  can be planned next.
- A proposed sequence is complete: each prerequisite has a provider among existing
  code or predecessors, each deferral has a destination change, and each acceptance
  criterion of the needs the ask covers is met, planned or held by an unplanned
  change. Uncovered intent is surfaced as an omission, never left implicit.
- Commitment is progressive: uncertainty is settled before the commitment it could
  disrupt (persisted data shapes, money and permission rules, public interfaces,
  deploys), not before all work. Investigations run ahead of their change's
  predecessors, ranked by the cost of learning late; reversible choices proceed on
  a labeled assumption that stays open; questions reach humans in bounded batches.
  A surface people will work in that the human has not seen gets a quick preview
  before it is built out.
- Foundational designs are tested against already-known later needs: the
  constraint is preserved now, resolved first, or given an affordable evolution
  path. Prerequisites name their provider and how they are verified, and resolve to
  retained code and checks once the providing change is disposed.
- Long sequences get a readiness assessment against a declared horizon: rated
  evidence, a pre-mortem, a discovery queue, a stated confidence and ranked
  recommendations. Reviews name plan misses; a lesson that will recur in the
  product is proposed for the project's policy, which later planning reads.
- Tasks have checkable acceptance and direct completion evidence; dependencies stay
  within their change. Independent work continues around manual blockers.
- Executable tasks do not require inventing product policy; consequential unknowns
  get a worked example and a decision first.
- A change is safe to forget before it passes review: each material requirement has a
  retained destination and evidence, or an explicit disposition. Approved unfinished
  detail gets a retained home immediately.
- After acceptance, the change, tasks and review are deleted together; after
  delegated acceptance, once the human has responded to the result. Cleanup
  preflights the whole batch, preserves unknown files, and rejects missing or
  dependent destinations. Git holds history; a disposal commit carries the change's
  need → outcome summary.

## Proportionate collaboration

- Adoption is explicit; installed skills do not mandate use and opt-outs win.
- Every product change recovers and reconciles intent, designs, verifies and reviews
  in proportion. Direct delivery (one result finished in one session, nothing deferred
  or undecided) keeps no execution records; managed delivery uses changes, including
  for plan-only requests whose result is finished later.
- Confirmation of written intent is provenance, not a gate; open questions block only
  the work that depends on them.
- Conversation instructions authorize scope; only material questions are asked;
  plan-only requests stop at the plan; technical repairs need no new permission.
- Humans accept managed results by default. Explicit fast-forward delegates
  acceptance for one change only and never invents confirmation, observations or checks.
- Coordinated rounds run named changes in isolated worktrees under one record kept
  outside the repository, which the coordinator rereads instead of asking the human
  to resend the brief; consequential results get an independent review, and
  integration is serial. Workers stop at submission, the coordinator acts on each
  result as it arrives, and the round's evidence survives restarts.
- Workflow guidance is concise, with one owner per rule, so agents spend their context
  on the product rather than on the framework. Agents read only what each step needs
  and hand off to a fresh session rather than working in a very large one.
- Reports use the human's vocabulary and answer their direct questions. Retained
  records hold decisions and their homes, never run logs, resource names or session
  details.

## Implementation and verification

- Code expresses behavior; needs supply independent intent; tests check the connection.
- Use the smallest set of fast, independent checks that protects affected needs and
  costly failures. Avoid incidental snapshots, private-call assertions and speculative
  matrices; honor explicit coverage requirements without equating them with correctness.
- A rule doc's worked examples are recomputed by one retained check that reads the
  doc and runs when its inputs change. Once product tests replay an example, only a
  text check that the doc still states their values remains; agents cite a current
  passing run rather than recomputing by hand.
- The code-to-intent link is derived from the code: tests mention the need IDs they
  protect, and `ow trace` reports them. No separate traceability record is kept.
- Modules carry short responsibility headers and major boundaries a README; neither
  holds IDs, statuses or dates.
- Prefer functional cores, effects at boundaries, cohesive modules and explicit
  dependencies, assessed with an evidence-based architecture rubric.
- Greenfield work starts with a minimal structure and an end-to-end slice. Brownfield
  onboarding proposes refactoring only when it earns its cost, with human approval.
- A change's final review assesses every current need: linked and other affected
  needs with direct evidence, the rest recorded as assessed and unaffected. Reviews of
  a single task or a correction cover its diff, its acceptance and the needs it
  affects. Any change to a pending review's inputs makes it stale, and the CLI names
  what changed.
- A blocked review returns one complete list of blockers, each with the check that
  settles it. Re-reviews add a blocker only for a regression the correction introduced
  or a defect those checks reveal. Only product risk blocks, a failure that
  reproduces on the base revision is pre-existing, and correction of one task is
  bounded before it is re-planned or escalated. A check that fails on its own setup
  is rerun, not counted against the work, and a blocker only a rule change can
  resolve goes straight to the human.
- Evidence is a short record: command, revision, result and where the log is. Runs
  recorded at the reviewed revision are reused, and provenance machinery is built only
  when a result's integrity is in doubt.
- Review freshness includes recursive submodule checkouts and content; pinning the
  reviewed checkout afterwards keeps a review fresh, a differing pin is warned about,
  and uninspectable components prevent fresh acceptance. Routine verification stays under five minutes.

## Bounded knowledge

- All current need content enters context without truncation. A configurable 24,000
  estimated-token soft target warns at 80% and never blocks inspection.
- OW artifacts, and text docs that current needs reference, warn at 8,000 estimated
  tokens and source at 500 nonblank lines; a source hard limit is opt-in with
  justified exact-path exceptions.
- Context reports sized retrieval entries rather than loading referenced files.
- Status exposes cleanup candidates, pending acceptance, blocked work and retired needs.

## Adoption, distribution and evaluation

- Python 3.11+, no third-party runtime dependencies, no model API calls.
- Published as `openwish` with identical `ow` and `openwish` commands; package, module
  and bundled skill versions advance together.
- Eleven canonical skills with thin OpenCode, Claude Code, Codex and generic adapters;
  interactive and explicit harness selection; preserving, version-aware reinstall.
- Ownership is by location: OW owns what it installs as skills, including its policy
  and artifact reference in `ow-core`; everything under `openwish/` is the project's.
  Project policy adds to OW's rules and overrides one only by naming it.
- Upgrades keep existing projects working: artifact format changes ship with a
  migration that `ow init` applies after preflighting the whole project. Projects on
  an older schema are told to run `ow init`; unknown schemas are rejected before any
  write.
  A CLI older than a project's installed integrations refuses to use it and asks for
  an upgrade instead of misreporting newer records as invalid.
- Skill evaluations compare OW against a no-OW baseline on executable, multi-session
  scenarios, grade behavior mechanically where possible (acceptance checks, seeded
  mutants against retained tests), and record time and token cost.
