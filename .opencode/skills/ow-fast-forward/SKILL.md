---
name: ow-fast-forward
description: Run OpenWish needs through NDD without approval prompts, including final acceptance. Use only for an explicit human fast-forward request or explicit instruction to skip OW approvals.
disable-model-invocation: true
metadata:
  openwish-version: "0.3.1"
---

# Fast-forward

Read `openwish/policy.md`. This grants explicit authority for the selected needs'
current implementation revisions. Follow the same quality phases without asking
for confirmation, design approval, implementation permission, or final acceptance.

1. Interpret the ask against existing needs. Keep the ask in conversation; do not
   create a request/change record, ask summary, or independent execution container.
2. Reuse existing needs. If implementation must resume, use `ow reopen N-001 ...
   --fast-forward`. For open needs use `ow mode fast-forward N-001 ...`. Create a
   distinct new need only when necessary with `ow new need ... --fast-forward`.
   If current outcomes already satisfy the request, explain that and do no extra work.
3. Follow Propose, Align, Plan, Implement, and Review, reading each skill on entry.
   Record gates with `ow gate STAGE N-001 ... --by fast-forward`. Skip all approval
   questions; do not fabricate human confirmation or verification dates.
4. Resolve routine decisions from all current needs and minimal coherent work.
   For genuine blocking ambiguity or contradictory intent, first exhaust
   independent work, then use numbered questions and the best two or three A/B/C
   choices, with `(Recommended)` before the preferred text and concise effects.
5. Complete actual verification and review. This mode does not manufacture access,
   manual observations, or passing checks. Never mark unfinished tasks done.
6. After a passing review, record fast-forward acceptance and approve the needs.
   Report need → spec → outcome and direct evidence without another approval prompt.

Future reopening defaults to normal human-controlled workflow unless explicitly
fast-forwarded again. This mode is not authority for unrelated future needs.
