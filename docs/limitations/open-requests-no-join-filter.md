---
id: open-requests-no-join-filter
title: open_requests measure uses a status filter, not a status-dim join
severity: info
affects:
  - open_requests
since: 2026-05-08
status: active
---

# open_requests measure uses a status filter, not a status-dim join

The `requests.open_requests` measure is implemented as
`COUNT(*) WHERE status != 'Closed'` rather than as a join through the
`statuses` view. This was chosen to avoid cross-view fan-out at MVP 1
scale.

## Impact

- The measure behaves correctly for the count question.
- It does not compose cleanly with future status-dim joins. If a query
  ever wants to combine `open_requests` with attributes pulled from
  the `statuses` dim (e.g. an `is_terminal` flag added later), the
  measure's filter would need to be rewritten.
- Removes one degree of freedom for the semantic layer to choose its
  own join path; analysts who want a different "open" definition
  must work outside the measure.

## Workaround

For most analyst questions, the measure as-is is what you want.
For more nuanced status logic, write the query directly against the
`requests` view and filter on `status` or `status_id` as needed.

## Resolution path

If MVP 4's expanded metric library introduces additional
status-derived measures, the implementation may be reworked to use
the `statuses` join. Out of scope for MVP 1.
