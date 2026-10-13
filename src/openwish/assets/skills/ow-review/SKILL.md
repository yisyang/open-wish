---
name: ow-review
description: Review an OW change against all current needs, code, tests and regressions; record the result, present it, and close accepted work. Routine changes get concise verified results without a closure step. Honor OW opt-outs.
---

# Review

Read `openwish/policy.md`, `ow context C-001`, the change and its tasks, and the
actual diff. Routine work: verify, fix, report, stop.

1. **Assess the needs.** Run `ow trace` and compare the traced checks and files
   with the diff.
   - **Affected needs:** the linked needs plus any whose behavior the diff touches.
     Check each with direct evidence.
   - **Unaffected needs:** every other current need. Confirm briefly why the change
     cannot violate it. If you cannot, treat it as affected.
   Compare results with the change's delivers-now scope and exit evidence, not just
   ticked tasks. Explain partial contributions and deferrals; an empty task list in
   a candidate change is not completion.
2. **Judge the checks** (Strategic verification in `ow-plan`): would they catch a
   need violation, survive a harmless refactor, and test intent rather than repeat
   the code's own logic? Ask what plausible wrong implementation would still pass.
3. **Judge the structure** with the Architecture rubric in `ow-align` on the changed
   paths, including whether module headers and boundary READMEs still describe them.
4. **Fix** within authorized intent and rerun affected checks. Keep unresolved
   manual observations and limitations visible.
5. **Make it safe to forget** (below) before recording the result.
6. **Record:** run `ow check`, then
   `ow record-review C-001 --summary "user-visible outcome" --check "command: result"
   [--affected N-003] --handoff FILE` (or `--handoff -` with JSON on stdin; format
   in `openwish/artifacts.md`). Unresolved findings use `--verdict blocked`.
   Passing needs every task done. If anything changes afterwards, `ow summary C-001`
   names what made the review stale; refresh the affected verification and record
   again.
7. **Present need → outcome → evidence**, plus limitations.
   - Default mode: ask once for human acceptance (numbered A/B/C, `(Recommended)`),
     after all available work is done. Only after actual acceptance:
     `ow close C-001 --by human`.
   - Explicit fast-forward: `ow close C-001 --by fast-forward` after the same checks,
     attributed to delegation, never to a human.
8. **Dispose** via `ow-consolidate`. Needs stay current; further work uses a new
   change in default mode unless delegated again.

## Safe to forget

Before passing, every material requirement or decision this change introduced has
a retained home and evidence, so nobody needs the change or conversation later.
Group related rules and reuse task evidence; this is a short assessment, not a
per-function matrix.

- `implemented`: behavior in product files, with independently expected checks or
  a repeatable manual procedure.
- `retained`: intent or rationale in a need or ordinary doc/data.
- `deferred`: approved unfinished detail in another open change or domain data,
  with its limits explicit. Deferral cannot drop a promised result.
- `superseded`: the replacement intent and the actual human decision.
- `unresolved`: anything missing; the review stays blocked.

Read both directions: requirements → code and checks, and consequential code
choices → the intent that justifies them. Could a maintainer find, explain, verify
and safely change this behavior with only the repository? The CLI checks that
destinations exist and are fresh, not that they say the right thing. In submodule
projects, inspect component diffs too.
