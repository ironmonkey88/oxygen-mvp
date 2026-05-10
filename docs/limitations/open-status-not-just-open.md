---
id: open-status-not-just-open
title: open_requests measure includes On Hold and In Progress, not just Open
severity: warning
affects:
  - open_requests
since: 2026-05-07
status: active
---

# open_requests measure includes On Hold and In Progress

The `requests.open_requests` measure (Airlayer) and the equivalent
hand-written filter `status != 'Closed'` count any request that is
not in the `Closed` terminal state. The Somerville 311 feed has four
status values: `Open`, `In Progress`, `On Hold`, `Closed`. The first
three are all counted by `open_requests`.

## Impact

- "How many open requests are there?" returns a number that includes
  requests an analyst might consider partly-resolved (`In Progress`)
  or stuck (`On Hold`). The number is larger than what a strict
  `status = 'Open'` filter returns.
- Time-to-close metrics derived from `open_requests` populations
  include in-progress requests, biasing average duration upward.
- Comparisons against external systems that define "open" differently
  will mismatch.

## Workaround

For strict-Open counts, filter explicitly:
```sql
WHERE status = 'Open'
```
For just-not-closed counts, the existing measure is correct:
```sql
WHERE status != 'Closed'
```
For separating workflow stages:
```sql
GROUP BY status
```

## Resolution path

None planned. The measure semantics are documented; analysts are
expected to query `status` directly when they need finer granularity.
