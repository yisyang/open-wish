---
name: ow-onboard
description: Adopt OpenWish for a product or monorepo when explicitly requested. Infer right-sized needs, assess the existing architecture, and propose worthwhile refactoring for human approval. Never onboard merely to make a code change.
---

# Onboard

If adoption was requested and OW is not initialized, run `ow init --harness HARNESS`.
Read `openwish/policy.md` and `openwish/artifacts.md`. Default to one product/domain
per repository.

1. **Inspect** product descriptions, interfaces, representative user paths, code,
   tests and deployment configuration. Follow behavior through its dependencies
   rather than judging from the file tree.
2. **Propose a small set of needs** using Right-size intent in `ow-propose`: actors,
   independently valuable outcomes, observable acceptance, genuine constraints and
   open questions (in `open`). Code shows behavior, not confirmed intent; label
   inference. On repeat onboarding, reuse existing IDs by comparing actor, outcome
   and acceptance.
3. **Confirm intent** in one batch decision (A/B/C) in default
   mode; set `confirmed_at` only for what the human actually confirms.
   Under explicit fast-forward, leave inference unconfirmed.
4. **Assess architecture** with the rubric in `ow-align`: each finding as
   observation (with file references) → consequence → whether improving it is
   worth it. Keeping a satisfactory structure is a valid result. Note missing
   module headers or boundary READMEs only where finding behavior is actually hard.
5. **Propose refactoring only when it earns its cost**, as a sequence of
   independently reviewable changes (Right-size delivery in `ow-propose`): behavior
   to preserve, baseline checks (Strategic verification in `ow-plan`), boundary
   improvements, cost and risk, verification and rollback per step. Refactoring
   needs one explicit human decision before any product edit; onboarding alone
   authorizes none.
6. **Preserve operational knowledge** (environments, hosts, accounts, setup) in
   ordinary docs rather than needs, following One home per fact in the policy.
7. **Present** the needs, assessment and proposal in conversation. Create changes
   only when planning, implementation or verification was requested; for broad
   requested plans, task only ready increments (Right-size delivery in `ow-propose`)
   and keep the rest as concise open changes. End with the next useful action.
