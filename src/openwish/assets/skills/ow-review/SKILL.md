---
name: ow-review
description: Review an OW change against needs, code, tests, and regressions; present results and close accepted work. Routine changes receive concise verified results without a closure ceremony. Honor OW opt-outs.
---

# Review

Read `openwish/policy.md`, `ow context C-001`, the working approach/tasks, and
the actual code diff. Review from intent. For routine work, verify, remediate,
report, and stop without creating records or asking final acceptance.

1. Assess the change against all current needs and its linked needs. Inspect
   relevant error paths, compatibility, reliability, security, and maintainability.
   Determine affected checks and explain unaffected constraints briefly. Passing
   tests alone do not prove user benefit or excuse tests that repeat a code mistake.
2. Remediate within authorized intent and rerun affected checks. Continue available
   work before requesting human input. Retain unresolved manual observations and
   limitations honestly. Material intent changes require an actual decision.
3. Ensure the repository will remain understandable after disposal: preserve
   lasting behavior/tests, updated needs, and useful rationale before final review.
4. Run `ow check`, then `ow record-review C-001 --summary "user outcome" --check
   "command/observation: result" --covered-need N-001 ...`. Include every
   `review_needs` ID from the context manifest. Unresolved findings use
   `--verdict blocked`. Each change retains one latest review, not a history.
5. Passing review requires all tasks done. Later changes to needs, approach,
   evidence, policy/config, or repository content require refreshed verification
   and review before closure. `ow summary C-001` shows whether results are fresh.
6. Present **need → outcome → evidence**, plus limitations. In default mode, ask
   once for final human review/acceptance after available work is complete. Use a
   numbered question and meaningful A/B/C choices with `(Recommended)` before the
   preferred text. Only after actual acceptance run `ow close C-001 --by human`.
7. In explicitly selected fast-forward mode, close with `--by fast-forward`
   after the same checks, without an acceptance question. Attribute delegation
   honestly; never claim a human reviewed or confirmed inferred needs.
8. After closure, follow `ow-consolidate` and `ow clean C-001` to dispose the
   change, tasks, and review once useful knowledge is preserved. Needs remain
   current. Further implementation uses a new change with default mode unless
   explicitly delegated again; closing one increment does not complete a need forever.
