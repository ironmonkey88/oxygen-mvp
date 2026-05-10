---
id: current-year-partial
title: Year-to-date counts are partial, not full-year
severity: warning
affects:
  - current_date
since: 2026-05-08
status: active
---

# Year-to-date counts are partial, not full-year

When the agent answers "this year" questions, it filters by
`year(date_created_dt) = year(current_date)`. The DuckDB function
`current_date` resolves to today's date, so the resulting count
covers Jan 1 → today only, not the full calendar year.

## Impact

- "This year" counts will not equal a prior-year count of similar
  framing. A naive analyst comparing "this year" to "last year"
  without accounting for elapsed days will under-count the current
  year by the fraction of the year remaining.
- Time-series charts showing year-over-year totals must annotate or
  truncate the current year, or compare YTD vs. equivalent prior YTD.

## Workaround

For YTD comparisons, use a same-day cutoff in both years:
```sql
WHERE date_created_dt
  BETWEEN date_trunc('year', date_created_dt) AND current_date
```
Or compute a "fraction of year elapsed" and scale the prior-year
count down proportionally for sanity checks.

## Resolution path

None planned. The semantics of `current_date` are correct; the
limitation is about analyst interpretation. The agent surfaces this
note whenever it uses `current_date` so the framing is not implicit.
