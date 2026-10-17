---
name: ow-consolidate
description: Dispose closed OW changes while preserving needs and useful repository knowledge, and compact needs on request or when size or overlap warrants it. Honor OW opt-outs.
---

# Consolidate

Load `ow-core`, read `openwish/policy.md` and run `ow status` and `ow context`. Size warnings mean
"inspect relevance and duplication", never "delete meaning".

## Dispose closed changes

1. **Find candidates** in `ow status` retention groups: closed changes, results
   awaiting acceptance (refresh stale reviews first), blocked or manual work, and
   retired needs. Age and volume never prove work finished or abandoned; ask.
2. **Check what survives.** Intent in needs, behavior in source, checks in tests,
   non-obvious rationale in nearby comments or ordinary docs, and future work in
   its own open changes. Inspect the review's handoff (Safe to forget in
   `ow-review`). Rewrite successor prerequisites as delivered code, not the disposed
   change's plan or files. Do not copy whole plans into docs.
3. **Preview, then clean:** `ow clean C-001 --dry-run`, then `ow clean C-001`. Resolve
   what preflight reports: move useful unknown files deliberately; reconcile
   reviews that cite the batch and retained mentions of the change ID; replace a
   cited closed successor with its delivered product files. If a destination moved
   after closure, update only that review's handoff paths and evidence.
4. Knowledge that needs new edits after review belongs before closure; refresh the
   review. After closure, new implementation is a new change.
5. Run `ow check` and report what was disposed and where knowledge now lives.
6. **Continue the sequence.** For each `PLAN` change in `ow ready`, apply Plan a
   candidate in `ow-plan`, and take ready investigations (Discover ahead of
   delivery); planning needs no approval. Present `ASK` questions as one batch.
   Implement only within authorized scope; otherwise present them as the next step.

## Compact needs

Compact when asked, when `ow check` warns near the needs target, or when you notice
overlap. Size is a prompt to look, not a cap.

- Use Right-size intent in `ow-propose`: resolve duplicates, mechanism-sized needs,
  broad bundles and drift before shortening prose. Keep every acceptance criterion,
  constraint and meaningful exception.
- Clarity is valid compaction even when it adds words: apply Right-size intent's
  sentence, calibration, setup and `open` rules, and replace restated rules with
  links to their one home. A value moved into a referenced rule is kept, not weakened.
- Merging, splitting or retiring changes intent: get a decision (A/B/C) and
  keep stable IDs where possible. Check `ow graph --json` and
  `ow trace` and reconcile relations, change references and need IDs mentioned in
  tests when IDs change. Never retire current intent to meet a budget.
- Delete retired needs or drop `open` items only by human decision, reconciling a
  retired need's references and rationale first. Ask about open items delivered
  work made decidable.

**Size targets.** Current needs: 24,000 estimated tokens by default (configurable),
with no line cap. Each OW artifact warns at 8,000. These cover retained knowledge,
not your working context: on a 1M-token harness, 150k–200k tokens of relevant
working context is a starting point to evaluate, not a quota, and small tasks need
far less.

**Tests.** Keep small regression checks of lasting outcomes and consequential
boundaries; delete temporary probes; merge redundant or brittle tests only when
their protection is preserved.
