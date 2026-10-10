---
name: ow-align
description: Reconcile OpenWish needs with all current intent and affected implementations, then update spec contracts and designs. Use before planning or when approved intent evolves.
metadata:
  openwish-version: "0.3.1"
---

# Align

Read `openwish/policy.md` and `ow context N-001 ...` for the selected needs.
Check their need-confirmation receipts using `ow status --json`. Return to
Propose when material intent lacks required confirmation in default mode.

1. Review all current needs, including approved implementations. Retrieve relevant
   retired needs without making them binding again. Read affected prerequisite
   and consumer contracts, designs, and code; expand semantic adjacency as needed.
2. Distinguish incompatible needs from an implementation that cannot yet satisfy
   compatible ones. Adapt solutions within intent. For real human decisions,
   present numbered questions with two or three A/B/C choices, prefix the preferred
   choice text with `(Recommended)`, and explain effects concisely.
3. Update behavioral specs and designs. Each design contains authoritative
   `needs = ["N-001", ...]` references and explains how its approach satisfies them.
   Keep entity/module/cross-cutting ownership, containment, and dependencies clear.
4. Explain the proposed solution using need → spec → outcome and affected adjacent
   needs. Record only consequential trade-offs. For a need requiring verification
   but no implementation, set its state's `no_work_reason` before alignment.
5. Run `ow check`. In default mode, ask for this design's approval using the
   numbered-choice format; after approval record `ow gate align N-001 ... --by
   human`. In fast-forward mode use `--by fast-forward` without confirmation.
6. Continue internally to `ow-plan`. A material need revision returns to Propose;
   never silently rewrite an earlier human decision or create a change record.
