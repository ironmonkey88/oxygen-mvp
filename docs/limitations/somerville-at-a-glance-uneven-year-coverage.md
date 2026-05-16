---
id: somerville-at-a-glance-uneven-year-coverage
title: At-a-Glance KPI year coverage is uneven — most topics are 2010-2024, a few are 2024-only
severity: warning
affects:
  - main_bronze.raw_somerville_at_a_glance
  - main_gold.fct_somerville_kpi
  - main_gold.dim_kpi_topic
  - somerville_kpis
since: 2026-05-15
status: active
---

# Year coverage on the "Somerville at a Glance" compendium is uneven by topic

## The finding

Probed 2026-05-15: 749 rows across 25 distinct topics. Year range
1850-2024. Distribution:

| Era | Rows | Topics covered |
|---|---|---|
| 1850-2000 (decadal) | 16 | Population only (decadal back-history) |
| 2010-2021 | 506 | ~16 core topics with consistent annual updates |
| 2022 | 51 | core topics + 10 rows of "Commute Time" (this year only) |
| 2023 | 37 | core topics; some annual KPIs skipped this year |
| 2024 | 171 | core topics + 6 categorical breakdowns added (Age Group, Race & Ethnicity, etc.) |

The 25 topics split into two analytical shapes:

- **Time-series topics** with one observation per year per geography
  (Population, Median Home Value, Median Household Income, Median
  Rent, Rent Burdened Households, Vacancy Rate, Poverty, etc.). Most
  carry both Somerville and Massachusetts series for benchmarking.
- **Categorical topics** with multiple values per year per geography
  (Age Group, Percent Age Group, Household by Income Category, Median
  Rent by Year Moved In, Disability Characteristics, Race & Ethnicity,
  Commute Time, Language Speakers, Age of Housing Stock). The source
  publishes a Somerville breakdown + a Massachusetts benchmark
  breakdown at the same year, differentiated by `description` (the
  category name) and `geography`. Most appear only in 2024.

`dim_kpi_topic.geography_count` (1 vs 2) and
`has_massachusetts_benchmark` flag the geography shape per topic.

**Surrogate key implication.** kpi_id is
`md5(topic + year + description + geography)` — all four columns are
needed for uniqueness. Two iterative test failures during Phase C
built up to this finding: first only `topic + year` (collided on
categorical breakdowns), then `topic + year + description` (still
collided on Somerville-vs-MA pairs). The final four-column SK
matches the source's full natural key.

## Impact

- **Cross-year analysis is reliable for the 16 time-series topics
  back to 2010** (Population to 1850 for the back-history). Line
  charts, trend math, year-over-year deltas all work.
- **Categorical topics don't support cross-year analysis** at all
  (most only have 2024 observations). They're snapshots, not series.
- **`dim_kpi_topic.latest_value` is NULL for categorical topics** by
  design — averaging or maxing across categories within a year
  doesn't give a meaningful "latest value." Analysts asking
  category-breakdown questions should query the fact directly.

## Workaround

- **Use `dim_kpi_topic.is_time_series = TRUE`** as the filter when
  the analyst question implies a single-value-per-year shape.
- **Use `dim_kpi_topic.observation_count` as a reliability heuristic**:
  topics with 30+ observations have consistent annual coverage
  2010-2024. Topics with <30 observations are partial or 2024-only.
- **`latest_value_for_topic` measure** in the semantic view uses
  `max(value)` and is most reliable when filtered to a single
  time-series topic. For categorical topics, query the fact directly
  with a year filter.

## Status

- Bronze: as-is.
- Gold: as-is. The shape is documented; analysts and the chat agent
  navigate it via `is_time_series` and `observation_count`.
- Silver: nothing planned. The dataset's analytical value is the
  long-tidy structure itself; flattening to wide format would lose
  topic semantics.
