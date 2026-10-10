---
name: ow-align
description: Reconcile needs and designs during structured OW work or explicit OW alignment. Use before planning substantive work; honor OW opt-outs and keep routine changes on the lightweight path.
---

# Align

Read `openwish/policy.md` and `ow context N-001 ...` for selected needs. Respect
OW opt-outs and plan-only instructions. Routine work follows Propose's lightweight
path. For structured work, preparation does not require separate need-confirmation
receipts. This replaces legacy generated per-stage prompts; honor deliberate
project-specific controls.

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
   Reuse specs by capability. Do not create a child spec just to isolate authority:
   Plan can scope an epic to a subset of the existing design's needs.
4. Explain the proposed solution using need → spec → outcome and affected adjacent
   needs. Record only consequential trade-offs. For a need requiring verification
   but no implementation, set its state's `no_work_reason` before alignment.
5. Continue internally to `ow-plan` without a design-approval prompt. Plan records
   one combined authorization after preparation. Ask earlier only if an unresolved
   consequential decision prevents meaningful planning.
6. A material need revision returns to Propose;
   never silently rewrite an earlier human decision or create a change record.
