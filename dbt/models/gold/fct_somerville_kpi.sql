{{ config(materialized='table', schema='gold') }}

-- Gold: fct_somerville_kpi -- one row per (topic, year, value) from the
-- "Somerville at a Glance" KPI compendium (Socrata `jnde-mi6j`).
-- 749 rows across 25 distinct topics; year range 1850-2024 (Population
-- carries the back-history; most KPIs are 2010-2024 with uneven
-- per-topic coverage). Long-tidy shape preserved.
--
-- Source-quality realities passed through:
--   - All 749 values are castable to DOUBLE (pre-flight 2026-05-15
--     confirmed no NULLs, no text sentinels). TRY_CAST kept as a
--     safety net for future source publications.
--   - Year coverage is uneven per topic. See limitation
--     somerville-at-a-glance-uneven-year-coverage. The dataset's
--     value is the latest-observation-per-topic surface; per-topic
--     full time series are available for the 16 topics with 30+
--     observations (Median Home Value, Median Household Income,
--     Median Rent, Population, etc.), not for the 9 topics with
--     <30 observations (Age Group, Race & Ethnicity, etc.).
--
-- Surrogate PK `kpi_id` = md5(topic || year). Composite natural key
-- (topic, year) is preserved on the row for cross-topic time-series
-- queries.
-- Surrogate PK includes description because categorical topics
-- (Age Group, Race & Ethnicity, Household by Income Category, etc.)
-- have multiple rows per (topic, year) with different `description`
-- values for the category breakdown. (topic, year, description) is
-- the natural primary key. Test caught this -- honest finding,
-- recorded in the limitations entry.
select
    md5(topic || '|' || year || '|' || coalesce(description, ''))             as kpi_id,
    topic,
    cast(try_cast(year as integer) as smallint)                               as year,
    try_cast(value as double)                                                 as value,
    description                                                               as kpi_description,
    units,
    geography,
    _extracted_at,
    _extracted_run_id,
    _source_endpoint
from {{ ref('raw_somerville_at_a_glance') }}
where topic is not null and year is not null
