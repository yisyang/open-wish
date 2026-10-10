+++
id = "S-002"
needs = ["N-002", "N-004", "N-005"]
+++

# Revision-aware workflow design

`validation.py` validates artifact types, links, graph integrity, and ordinal
consistency. `model.py` selects the earliest dependency-ready agent work while
retaining waiting/manual tasks separately.

`workflow.py` computes cumulative semantic fingerprints for needs, alignment,
implementation, and review. Operational status/date fields are excluded from
intent hashes. Review records bind direct results to plan, task outcomes, and
repository content. Gate records are fixed slots, replaced on renewed decisions.

Decision provenance is explicit: human or fast-forward. The CLI trusts the
harness to record actual conversation decisions; it does not authenticate humans.
Need approval preserves currency and records the review's verification date.
Reopening increments that need's revision and resets authority to default unless
explicitly fast-forwarded again. Relevant specs and epics are derived from links;
there is no stored execution container. Shared tasks require authority for all
affected open needs, and unrelated authorized tasks remain executable.
