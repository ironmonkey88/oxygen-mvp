---
id: crime-sensitive-incidents-no-month
title: Sensitive crime incidents have year-only — no month, day, or block
severity: warning
affects:
  - main_gold.fct_crime_incidents
  - incident_dt
  - incident_year_only
  - block_code
  - day_and_month
since: 2026-05-13
status: active
---

# Sensitive crime incidents have year-only — no month, day, or block

The Somerville Police source feed publishes 2,798 crime incidents
(12.5% of the dataset, as of 2026-05-13) with day-and-month, block,
shift, and time information **stripped at source** to protect victim
privacy. Only the year of the offense is reported for these
incidents.

At gold (`main_gold.fct_crime_incidents`), these rows surface as:

- `incident_dt` = NULL
- `incident_year` = populated (always)
- `incident_year_only` = TRUE
- `block_code` = NULL
- `police_shift` = NULL
- `case_number` uses a 9-character sentinel format (`1xxxxxxxx`)
  rather than the 8-character `YYxxxxxx` year-prefixed format of
  non-sensitive incidents

The sensitive set is identifiable structurally — analysts can
filter on `incident_year_only` to include or exclude it precisely.

## Impact

- **Sub-annual aggregation is systematically incomplete.** Any query
  that groups or filters by month, quarter, week, or day on the full
  crime dataset undercounts by 12.5%. The undercount is
  category-correlated (the source strips time/location for specific
  offense types — exact list not published).
- **Block-level aggregation is similarly bounded** — the same 2,798
  rows have NULL `block_code`.
- **Ward-keyed aggregation is partially affected.** Sensitive
  incidents retain their ward only sometimes; the breakdown for this
  set: 2,413 of the 2,798 sensitive rows have NULL ward (i.e., they
  contribute to both `crime-sensitive-incidents-no-month` and
  `crime-ward-coverage-gaps`).

## Workaround

Two analyst patterns:

1. **Include sensitive incidents at the year level.** Aggregate by
   `incident_year` rather than `incident_dt`. Use the measure
   `total_incidents` (counts everything) rather than
   `incidents_with_date` (filtered to known dates).
2. **Exclude sensitive incidents from time-series.** Add
   `WHERE NOT incident_year_only` to the query, or use the
   `incidents_with_date` measure which has the same effect via
   `COUNT(incident_dt)`.

The choice is analysis-shape-dependent and should be stated
explicitly in the answer. The Answer Agent surfaces this limitation
on any query that filters or groups by month / week / day on the
crime fact.

## Resolution path

Source-side; the Somerville Police won't (and shouldn't) publish
month-level data for sensitive cases. The MVP 3 silver layer may
expose an enriched `incident_year_only_reason` if the source ever
publishes the category breakdown, but the underlying day-stripping
is a victim-privacy decision we inherit.
