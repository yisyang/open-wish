---
name: ow-onboard
description: Adopt OpenWish by mapping an existing repository to a short set of candidate needs and spec designs, distinguishing inference from confirmed intent. Use to onboard a product or monorepo into NDD.
---

# Onboard

Initialize with `ow init --harness HARNESS` if needed. Read `openwish/policy.md`
and `openwish/artifacts.md`. Default to one product/domain in this repository.

1. Inspect product descriptions, interfaces, important user journeys, code, tests,
   and deployment configuration deliberately; avoid loading the whole repository.
2. Propose a short set of candidate needs with actors, outcomes, gains/pains,
   acceptance, and uncertainties. Label inference. Do not persist asks or turn
   onboarding into a change record. Existing behavior does not establish intent.
3. Reuse established need IDs and confirmed definitions on repeated onboarding.
   Reopen needs requiring work; preserve approved needs whose outcomes remain met.
4. In default mode, confirm the candidate needs with numbered questions and two
   or three A/B/C choices. Prefix the preferred text with `(Recommended)` and
   explain effects briefly. Discuss only current need confirmation, not later gates.
   Explicit fast-forward skips confirmation and leaves inferred intent unconfirmed.
5. Map contracts and technical designs to needs; put authoritative need references
   in spec designs. Use open for unverified implementation, in-progress for active
   work, review for verified candidates, and approved only after accepted results.
6. Capture verified environment profiles and secret references in durable knowledge.
   Identify gaps/manual observations without inventing tasks to rewrite working code.
7. Continue through the workflow for those needs. Set `no_work_reason` when only
   verification remains. Explain results by need and spec, with the next current
   action or required decision. Keep every artifact and global intent bounded.
