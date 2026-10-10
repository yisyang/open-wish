---
name: ow-review
description: Review structured OW implementation and regressions, then present outcomes for acceptance. Routine changes get a concise verified result without acceptance gates. Honor OW opt-outs.
---

# Review

Read `openwish/policy.md`, `ow context N-001 ...`, affected spec designs and their
need references, task evidence, and the actual code diff. Review from intent.
For the routine path, inspect the diff, run meaningful checks, remediate, and
report the result without OW records, lifecycle updates, or an acceptance prompt.
The remaining steps apply to structured work only, replacing legacy generated
blanket approval requirements while honoring deliberate project-specific controls.

1. Check selected needs and affected adjacent current needs, including previously
   approved ones. Verify contracts, error paths, security, reliability, and
   maintainability with meaningful evidence. Distinguish delivery from user outcomes.
2. Repair defects within approved intent and rerun affected checks. Material
   revisions return to the appropriate phase. Continue unfinished authorized work
   before requesting any final acceptance; never invent manual observations.
3. Run `ow check`. Record the latest direct review using `ow record-review N-001
   ... --summary "user outcome" --check "command/observation: result" --covered-need
   N-001 ...`. Include every context manifest `review_needs` ID. Use `--verdict
   blocked` for unresolved findings. Each need owns its latest bounded review.
4. Passing review requires all relevant tasks done. Repository, plan, or evidence
   edits afterward require refreshed verification and a replacement review.
5. Present a concise result using **need → spec → outcome**, then verification and
   limitations. Use `ow summary N-001 ...`; read S-001's design to identify N-001.
   Do not report only task completion or assume the human remembers the purpose.
6. In default mode, after available authorized work is exhausted, ask explicitly
   for final acceptance using a numbered question with two or three A/B/C choices
   and `(Recommended)` before the preferred choice text. After acceptance run
   `ow gate review N-001 ... --by human`, then `ow approve N-001 ...`.
7. In fast-forward mode, skip that confirmation: record the passing review,
   `ow gate review N-001 ... --by fast-forward`, and `ow approve N-001 ...`.
   Attribute acceptance to fast-forward, not explicit human review.

Needs remain current and binding. Follow-up work reopens existing needs or creates
distinct new ones; redundant asks generate no records. Keep one latest review.
