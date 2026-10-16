+++
id = "C-004"
title = "Meter data ingestion"
needs = ["N-002", "N-003"]
status = "open"
mode = "default"
after = ["C-001"]
+++

## Purpose

Store the array's production readings from the inverter's export.

## Scope

- Delivers now: daily import of inverter readings into a readings table.
- Defers: nothing.
- Prerequisites: none beyond C-001's database.

## Verification

Importing a fixture export twice stores each reading once.
