---
id: crime-incidents-missing-offense
title: A few crime incidents arrive with no offense fields
severity: info
affects:
  - main_gold.fct_crime_incidents
  - offense_code
  - offense
  - offense_type
  - offense_category
  - multi_offense_flag
since: 2026-10-21
status: active
---

# A few crime incidents arrive with no offense fields

Somerville's crime dataset (Socrata `aghs-hqvg`) sometimes publishes an
incident with its date, shift, ward and block but no `offensecode`, `offense`,
`offensetype` or `category`. The first was case `26066325` (2026-09-17, ward 3),
loaded 2026-10-21; it was the only such row in the source on 2026-10-23
(`$where=offensecode IS NULL` returns 1).

The row is kept: it is a real incident, and dropping it would undercount
incidents by ward and date. Its `offense_code`, `offense`, `offense_type` and
`offense_category` are NULL, and so is `multi_offense_flag` (derived from the
code). Counts by offense or category leave it out; counts of all incidents
include it.

The `not_null` tests on those columns warn for 1 to 10 such rows and fail
above 10, so a source regression still stops the pipeline being green.
