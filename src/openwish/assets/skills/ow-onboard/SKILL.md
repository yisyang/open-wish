---
name: ow-onboard
description: Adopt OpenWish when explicitly requested for a product or monorepo. Infer a compact set of durable needs from code and product context, distinguishing inference from confirmed intent. Never onboard merely to handle a code change.
---

# Onboard

Initialize with `ow init --harness HARNESS` if adoption was requested. Read
`openwish/policy.md` and `openwish/artifacts.md` for the current format. Default to
one product/domain per repository.

1. Inspect product descriptions, interfaces, user journeys, code, tests, and
   deployment configuration deliberately. Use repository structure as the design
   map rather than generating a parallel collection of specs and designs.
2. Propose a small set of needs with actors, independently valuable outcomes,
   observable acceptance, genuine constraints, and uncertainties. Existing code
   reveals behavior, not confirmed intent or verified delivery. Label inference.
3. Reuse established IDs and confirmed definitions on repeated onboarding. Compare
   actor/outcome/acceptance, not modules, commands, platforms, or shared code.
   Keep needs free of execution state and internal implementation plans.
4. In default mode, confirm inferred intent in one useful batch decision, using
   numbered A/B/C choices with `(Recommended)` before preferred text. Actual human
   confirmation may set `confirmed_at`. Explicit fast-forward leaves inference
   unconfirmed and skips that confirmation; it does not invent verification.
5. Preserve useful operational knowledge in ordinary repo docs and secrets as
   references, never values. Identify gaps and manual observations without
   inventing work to rewrite an already satisfactory implementation.
6. Create disposable changes/tasks only when substantive implementation or
   verification was requested. Onboarding alone does not authorize product edits.
   Verification-only changes may have no implementation tasks but still require
   actual checks and review. New changes default to human review unless explicitly
   delegated. Explain the needs and observed outcomes, plus the next useful action.
