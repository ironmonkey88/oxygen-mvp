{{ config(materialized='table', schema='gold') }}

-- Gold: dim_kpi_topic -- one row per distinct topic on fct_somerville_kpi.
-- 25 rows. Sources from the fact so any topic-name cleanup flows
-- through one place (the dim_offense_code pattern).
--
-- The source compares Somerville against Massachusetts benchmarks for
-- most topics. `has_massachusetts_benchmark` flags topics where the
-- compendium publishes both geographies. Use the fact's `geography`
-- column to filter to a specific series for analysis.
select
    topic,
    min(year)                                                                 as first_year,
    max(year)                                                                 as latest_year,
    count(*)                                                                  as observation_count,
    count(distinct geography)                                                 as geography_count,
    bool_or(geography = 'Massachusetts')                                      as has_massachusetts_benchmark,
    bool_or(geography = 'Somerville')                                         as has_somerville_data
from {{ ref('fct_somerville_kpi') }}
group by topic
order by topic
