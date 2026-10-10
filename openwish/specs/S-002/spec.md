+++
id = "S-002"
title = "Revision-aware workflow and executable plans"
depends_on = ["S-001"]
parent = ""
implementation = "review"
+++

## Contract

- The default workflow records four distinct explicit human decisions.
- Selected fast-forward need revisions record all four decisions as bypasses and
  proceeds without approval prompts, retaining every quality phase.
- Changed semantic inputs invalidate affected gates. Ordinary task progress does
  not invalidate implementation authority.
- Specs, epics, and tasks retain traceable links. Task dependencies are acyclic,
  reference existing tasks, and point to lower `(group, order)` pairs.
- Independent agent work proceeds while manual observations wait. Review and
  approval require complete relevant work, need coverage, and direct results.
- Changes to reviewed repository content or task evidence invalidate review.
- Reopening resets revision authority on the same need ID; shared specs are only
  approved when all linked current needs are approved.

## Scenarios

A plan edit invalidates implementation authority without invalidating unchanged
alignment. A pending manual task does not block a later independent task. A code
edit after review prevents acceptance until verification is refreshed.
