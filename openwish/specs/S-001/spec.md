+++
id = "S-001"
title = "Needs and bounded knowledge"
depends_on = []
parent = ""
implementation = "review"
+++

## Contract

- Need records expose actor, outcome, acceptance, independent
  currency/implementation, and separate confirmation/verification dates.
- The context view includes every current need in full, including approved ones,
  with related spec statuses derived from specs. Retired needs are retrievable.
- Artifacts remain below 500 lines. The complete needs view remains below 500
  lines and the configurable token estimate. No silent truncation is permitted.
- Source sizes enforce the agreed soft/hard bounds with exact-path exceptions.
- Durable knowledge and latest summaries replace endless operational journals.
- Need identity survives reopening. There are no stored asks or change containers.

## Scenarios

An approved current need remains visible during the next ask. A 500-line OW JSON
artifact fails validation even though source JSON data is exempt. A single long
line cannot evade the global estimated-token budget.
