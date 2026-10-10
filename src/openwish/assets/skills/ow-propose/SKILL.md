---
name: ow-propose
description: Interpret a software ask against existing OpenWish needs, creating or reopening needs only when necessary. Use to clarify desired outcomes or revise NDD intent.
---

# Propose

Read `openwish/policy.md` and `ow context` from the project root. Initialize OW
if needed. Load all current needs, including approved ones, and inspect relevant
spec designs/code to distinguish a new need from an already-satisfied outcome.

1. Identify actor, desired gains/pains, observable acceptance, and genuine
   constraints. Treat a requested mechanism as a candidate solution.
2. First check whether an existing need already covers the outcome. If it is met,
   recommend keeping the need/product as-is where appropriate. Do not create a
   duplicate need, reopen working behavior, or persist the ask merely to track it.
3. If work is needed for the same outcome, revise/reopen the existing need under
   its stable ID. Create a new need only for a distinct durable outcome. Present
   material conflicts and affected adjacent needs before modifying constraints.
4. Ask numbered questions with two or three choices, `A.`, `B.`, `C.`. Put
   `(Recommended)` before the preferred choice text. Add concise effects on needs
   and implementation when useful. Recommendations depend on existing intent and
   evidence; do not automatically ignore a request for an unmet outcome.
5. In default mode, confirm only the proposed need interpretation and acceptance.
   Do not mention later approvals, Plan gates, or implementation authorization in
   this confirmation. In explicitly selected fast-forward mode, skip confirmation
   and clarify only genuinely blocking ambiguity using the same question format.
6. Create/revise/reopen the agreed needs using `openwish/artifacts.md`. Store their
   durable definitions, not the original ask or an ask summary. Reopening resets
   authority; explicitly set fast-forward again only when requested.
7. Run `ow check`, then `ow gate needs N-001 ... --by human` after actual
   confirmation, or `--by fast-forward` when authorized. Continue internally to
   `ow-align`; do not add another permission question or preview its gates.

If there is no need revision or unfinished work, provide a concise explanation
using the existing need and spec, then finish without generating artifacts.
