{{ config(
    materialized='incremental',
    schema='admin',
    incremental_strategy='append',
    unique_key='test_id'
) }}

-- One row per defined test. Append-only with an `is_incremental()`
-- filter that excludes any test_id already in the table, so baselines
-- are seeded exactly once and stay frozen. Re-certifying a baseline
-- requires a manual update (out of scope for MVP 1).
--
-- Three sources of test_ids:
--   1. baseline.raw_311_requests.year_<YYYY>.row_count   -- bronze yearly
--   2. baseline.<table>.all.row_count                    -- total per table
--   3. dbt_test.<node_name>                              -- every dbt test

with baselines_yearly as (
    -- Per-year row-count baselines. **Active baselines exclude the
    -- current calendar year** (Plan 14a, 2026-05-13): a current-year
    -- baseline certified mid-year is structurally unstable -- the row
    -- count grows daily as new 311 requests are filed, and a 1%
    -- tolerance trips after a few days of normal ingestion. We still
    -- emit the current-year row (with `is_active = false`) so the dim
    -- has coverage; once the year closes and a new current year rolls
    -- in, a future run will baseline the now-stable previous year as
    -- active. The existing `is_incremental()` filter further protects
    -- already-frozen baselines from being re-emitted.
    select
        'baseline.raw_311_requests.year_' || year::varchar || '.row_count' as test_id,
        'baseline'                                                         as test_type,
        'raw_311_requests'                                                 as table_name,
        cast(null as varchar)                                              as column_name,
        'row_count'                                                        as metric,
        'year=' || year::varchar                                           as grain,
        count(*)::varchar                                                  as expected_value,
        0.01                                                               as tolerance_pct,
        (year <> extract(year from current_date)::integer)                 as is_active,
        now()                                                              as certified_at,
        'system'                                                           as certified_by
    from (
        select extract(year from date_created::timestamp) as year
        from main_bronze.raw_311_requests
        where date_created::timestamp >= timestamp '2015-01-01'
          and date_created::timestamp <  timestamp '2027-01-01'
    ) y
    group by year
),

baselines_total as (
    select 'baseline.raw_311_requests.all.row_count' as test_id,
           'baseline' as test_type, 'raw_311_requests' as table_name,
           cast(null as varchar) as column_name, 'row_count' as metric,
           'all' as grain, count(*)::varchar as expected_value,
           0.01 as tolerance_pct, true as is_active,
           now() as certified_at, 'system' as certified_by
    from main_bronze.raw_311_requests
    union all
    select 'baseline.dim_date.all.row_count', 'baseline', 'dim_date',
           cast(null as varchar), 'row_count', 'all', count(*)::varchar,
           0.01, true, now(), 'system'
    from main_gold.dim_date
    union all
    select 'baseline.dim_request_type.all.row_count', 'baseline', 'dim_request_type',
           cast(null as varchar), 'row_count', 'all', count(*)::varchar,
           0.01, true, now(), 'system'
    from main_gold.dim_request_type
    union all
    select 'baseline.dim_status.all.row_count', 'baseline', 'dim_status',
           cast(null as varchar), 'row_count', 'all', count(*)::varchar,
           0.01, true, now(), 'system'
    from main_gold.dim_status
    union all
    select 'baseline.fct_311_requests.all.row_count', 'baseline', 'fct_311_requests',
           cast(null as varchar), 'row_count', 'all', count(*)::varchar,
           0.01, true, now(), 'system'
    from main_gold.fct_311_requests
),

dbt_tests as (
    select distinct
        'dbt_test.' || node_name                            as test_id,
        case
            when node_id like 'test.%singular%' then 'dbt_singular'
            else                                     'dbt_generic'
        end                                                 as test_type,
        cast(null as varchar)                               as table_name,
        cast(null as varchar)                               as column_name,
        node_name                                           as metric,
        'all'                                               as grain,
        '0'                                                 as expected_value,
        0.0                                                 as tolerance_pct,
        true                                                as is_active,
        now()                                               as certified_at,
        'system'                                            as certified_by
    from main_bronze.raw_dbt_results_raw
    where node_id like 'test.%'
),

all_tests as (
    select * from baselines_yearly
    union all
    select * from baselines_total
    union all
    select * from dbt_tests
)

select * from all_tests
{% if is_incremental() %}
where test_id not in (select test_id from {{ this }})
{% endif %}
