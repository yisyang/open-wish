+++
id = "C-001"
title = "Member accounts and shares"
needs = ["N-001"]
status = "open"
mode = "default"
+++

## Purpose

Members sign up, buy a share and see it.

## Scope

- Delivers now: sign-up, share purchase within capacity, account page (N-001).
- Preserves: nothing yet; greenfield.
- Defers: nothing.
- Prerequisites: none.

## Approach

`accounts` table with one `holder_email` per account; `shares` rows reference
`account_id`. Capacity check is a pure function over existing shares.

## Verification

Capacity boundary test (exactly full, one watt over); sign-up to account page
end to end.
