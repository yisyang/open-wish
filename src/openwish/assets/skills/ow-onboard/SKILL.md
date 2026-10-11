---
name: ow-onboard
description: Adopt OpenWish when explicitly requested for a product or monorepo. Infer right-sized needs, assess the existing architecture, and propose beneficial refactoring for human approval. Never onboard merely to handle a code change.
---

# Onboard

Initialize with `ow init --harness HARNESS` if adoption was requested. Read
`openwish/policy.md` and `openwish/artifacts.md` for the current format. Default to
one product/domain per repository.

1. Inspect product descriptions, interfaces, representative user paths, code, tests,
   and deployment configuration. Follow behavior through its dependencies instead
   of judging architecture from the file tree. Use the Architecture rubric in
   `../ow-align/SKILL.md` for assessment, without starting its execution workflow.
2. Propose a small set of needs with actors, independently valuable outcomes,
   observable acceptance, genuine constraints, and uncertainties. Existing code
   reveals behavior, not confirmed intent or verified delivery. Label inference.
   Apply the Right-size intent questions in `../ow-propose/SKILL.md`. Compare broad
   bundles and mechanism-sized candidates; preserve useful semantic relationships
   in needs rather than deriving them from module or change co-occurrence.
3. Reuse established IDs and confirmed definitions on repeated onboarding. Compare
   actor/outcome/acceptance, not modules, commands, platforms, or shared code.
   Keep needs free of execution state and internal implementation plans.
4. In default mode, confirm inferred intent in one useful batch decision, using
   numbered A/B/C choices with `(Recommended)` before preferred text. Actual human
   confirmation may set `confirmed_at`. Explicit fast-forward leaves inference
   unconfirmed and skips that confirmation; it does not invent verification.
5. Report architecture findings as observation (with code/test references), practical
   consequence, and whether improvement is worthwhile. Compare retaining satisfactory
   structure with targeted refactoring; broader restructuring needs stronger evidence.
   If helpful, propose a sequence of independently reviewable changes with preserved
   behavior, baseline checks, dependency/effect boundaries, cost/risk, and incremental
   verification or rollback. Apply Right-size delivery in `../ow-propose/SKILL.md`;
   a whole modernization or pilot is not bounded merely because it has a short list.
   Seek one human decision on that refactor scope before product edits; onboarding
   or delegated intent inference alone does not authorize a rewrite. Present this
   alongside intent confirmation when useful. If no refactor earns its cost, say why.
   Use Strategic verification in `../ow-plan/SKILL.md` for the proposed baseline:
   reuse meaningful outcome checks, add small tests for consequential gaps, and
   avoid freezing incidental text/layout or proposing blanket coverage expansion.
6. Preserve useful operational knowledge in ordinary repo docs and secrets as
   references, never values. Identify gaps and manual observations without
   inventing work to rewrite an already satisfactory implementation.
7. Present the assessment/proposal in conversation. Create disposable changes/tasks
   only when planning, substantive implementation, or verification was requested.
   For broad requested plans, record concise candidate changes and detail the next
   executable increments; do not put the whole delivery program into one change.
   Onboarding alone does not authorize product edits.
   Verification-only changes may have no implementation tasks but still require
   actual checks and review. New changes default to human review unless explicitly
   delegated. Explain the needs and observed outcomes, plus the next useful action.
