---
id: oxy-df-interchange-empty-result-panic
title: Oxy panics on `execute_sql` queries whose WHERE filter matches zero rows
severity: warning
affects:
  - chat
  - answer_agent
  - execute_sql
since: 2026-05-16
status: active
---

# Oxy `df-interchange` Rust panic on no-match WHERE filter

## The finding

Surfaced 2026-05-16 during Plan 23 cumulative verification (Session
50, chat agent test Q2). When the Answer Agent ran:

```sql
SELECT topic, year, value, units, geography
FROM main_gold.fct_somerville_kpi
WHERE topic = 'Median Household Income'
ORDER BY year DESC, geography
LIMIT 10;
```

…the query's WHERE filter matched **zero rows** (the actual source
topic name is `'Median Household Income Overtime'`, with the
"Overtime" suffix the source uses). Rather than returning an empty
result set, Oxy panicked:

```
panicked at /home/runner/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/df-interchange-0.3.3/src/from_arrow.rs:71:1:
index out of bounds: the len is 0 but the index is 0
```

Full stack trace surfaces through Oxy's `tools::sql::execute_sql`
path, panic origin at `df_interchange::from_arrow` line 71. The Oxy
runtime catches the panic and reports it as a tool failure
(`Failed to join task: task 17 panicked with message "index out of
bounds: the len is 0 but the index is 0"`), but the result is the
same: the query that should have returned an empty result table
returns an error instead.

## Reproduction

- Oxy version: **0.5.47** (`oxy-app version: 0.5.47`,
  rust 1.95.0, commit `3183c6e98ea1586c8c3c83320aba0153f77da0a1`).
- Mode: `oxy start --local` (single-workspace).
- Surface: Answer Agent's `execute_sql` tool path; not specific to
  any one dataset. Trigger condition is "WHERE filter matches zero
  rows" — the empty-result Arrow→DataFrame conversion is what
  panics, regardless of the upstream table or filter shape.

## Consequence for the analyst

- An analyst question whose answer is legitimately "zero rows" (a
  perfectly normal analytic outcome) errors instead of returning an
  empty set.
- The error message is less graceful than a normal exception — a
  panic, even when caught, is more disruptive than a clean
  empty-result return.
- For the Answer Agent specifically, the agent's reasoning loop
  *does* recover gracefully: when `execute_sql` errors, the agent
  tries alternative queries (DISTINCT, ILIKE-based searches) and
  often finds the right topic / filter shape on the second try.
  Session 50's Q2 ("latest median household income") landed the right
  answer ($132,572 for 2024) via this self-recovery path. So the
  user-facing impact is "agent takes an extra query to reach the
  answer" rather than "agent fails."

## Workaround

Code-side: nothing required — the Answer Agent's self-recovery
handles it. Worth noting in case it ever fails to recover: prefer
`SELECT … FROM … WHERE col IN (…)` over equality on partial
strings, and use `EXISTS` / `COUNT()` probes before specific-row
queries when uncertainty exists about whether rows will match.

## Resolution path

Upstream — file as Oxy customer feedback. Likely root cause:
`df-interchange-0.3.3/src/from_arrow.rs:71` is reading from index 0
of an Arrow array without checking length first. Empty Arrow arrays
(zero rows) make `arr[0]` out-of-bounds.

Bundled with the SPA artifact-load 404 ([spa-artifact-load-404](spa-artifact-load-404.md))
as the two Oxy backend bugs surfaced through end-to-end testing in
mid-May 2026. Both filed together in the customer-feedback bundle
prepared on 2026-05-16.

Not blocking MVP 2 — agent self-recovery handles user-facing impact.
Worth fixing upstream for two reasons: (1) zero-row results are a
normal analytic outcome and shouldn't panic; (2) for Verified
Queries (MVP 3), the empty-result path will be exercised more often
as analysts probe edges of the data.
