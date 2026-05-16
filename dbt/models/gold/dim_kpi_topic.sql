{{ config(materialized='table', schema='gold') }}

-- Gold: dim_kpi_topic -- one row per distinct topic on fct_somerville_kpi.
-- 25 rows. Sources from the fact so any topic-name cleanup flows
-- through one place (the dim_offense_code pattern).
--
-- `latest_value` is well-defined for time-series topics (Population,
-- Median Home Value, etc. -- exactly one row at latest_year). For
-- categorical topics that have multiple rows at the same year (Age
-- Group, Race & Ethnicity, etc.), `latest_value` is NULL and the
-- analyst should query the fact directly for category breakdowns.
-- The boolean `is_time_series` flags which topics support a clean
-- `latest_value` lookup.
with topic_agg as (
    select
        topic,
        min(year)                                                              as first_year,
        max(year)                                                              as latest_year,
        count(*)                                                               as observation_count
    from {{ ref('fct_somerville_kpi') }}
    group by topic
),
latest_year_value_count as (
    select
        f.topic,
        count(*)                                                               as rows_in_latest_year,
        any_value(f.value)                                                     as any_latest_value,
        any_value(f.units)                                                     as any_latest_units
    from {{ ref('fct_somerville_kpi') }} f
    join topic_agg t on f.topic = t.topic and f.year = t.latest_year
    group by f.topic
)
select
    t.topic,
    t.first_year,
    t.latest_year,
    t.observation_count,
    case when l.rows_in_latest_year = 1 then true else false end               as is_time_series,
    case when l.rows_in_latest_year = 1 then l.any_latest_value else null end  as latest_value,
    case when l.rows_in_latest_year = 1 then l.any_latest_units else null end  as latest_units
from topic_agg t
left join latest_year_value_count l on l.topic = t.topic
order by t.topic
