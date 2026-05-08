---
id: 2024-survey-columns-sparse
title: Customer survey columns populated for <1% of rows
severity: warning
affects:
  - requests
since: 2026-05-08
status: active
---

# Customer survey columns populated for <1% of rows

The `accuracy`, `courtesy`, `ease`, and `overallexperience` columns in the
Somerville 311 source feed are post-resolution survey fields. They are only
populated when a citizen completes the optional post-ticket survey, which
fewer than 1% of resolved tickets do.

## Impact

Any aggregate over these fields (averages, distributions, satisfaction
trends) is biased: it reflects the small self-selecting slice of citizens
who responded to the survey, not the population of all 311 interactions.
Treating these fields as representative will mislead decisions.

## Workaround

When using these fields:

- Always report the responding-row count alongside the metric
- Frame results as "of the surveyed subset" rather than "of all tickets"
- Avoid time-series comparisons unless the response volume itself is
  reported in parallel

## Resolution path

None planned. The data shape is upstream and unlikely to change. The
Answer Agent should reference this limitation whenever a query touches
these columns.
