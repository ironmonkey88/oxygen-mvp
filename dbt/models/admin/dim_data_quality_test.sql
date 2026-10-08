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
-- Four sources of test_ids:
--   1. baseline.raw_311_requests.year_<YYYY>.row_count   -- bronze yearly, frozen
--   2. rolling.<table>.all.row_count                     -- total per table vs
--      rolling average of recent runs (computed in fct_test_run)
--   3. fixed.<table>.<slice>.row_count                   -- closed-period slice
--      that must keep its first recorded value (computed in fct_test_run)
--   4. dbt_test.<node_name>                              -- every dbt test
--
-- 2026-10-08: the frozen per-table totals (baseline.<table>.all.row_count)
-- are no longer emitted. They compared a growing dataset against
-- 2026-05-08 counts and failed every run from 2026-06-23. Rows already in
-- this append-only table stay as history; fct_test_run no longer
-- evaluates them.

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

rolling_checks as (
    -- expected_value is computed per run in fct_test_run (rolling average),
    -- so it is NULL here. tolerance_pct documents the default; the live
    -- value is the dq_rolling_tolerance var.
    select
        'rolling.' || t || '.all.row_count'   as test_id,
        'rolling'                             as test_type,
        t                                     as table_name,
        cast(null as varchar)                 as column_name,
        'row_count'                           as metric,
        'all'                                 as grain,
        cast(null as varchar)                 as expected_value,
        0.05                                  as tolerance_pct,
        true                                  as is_active,
        now()                                 as certified_at,
        'system'                              as certified_by
    from (values ('raw_311_requests'), ('dim_date'), ('dim_request_type'),
                 ('dim_status'), ('fct_311_requests')) as v(t)
),

fixed_checks as (
    -- expected_value is each slice's first recorded actual, held in
    -- fct_test_run history, so it is NULL here. Closed years are added
    -- as each calendar year ends.
    select
        'fixed.fct_311_requests.year_' || y::varchar || '.row_count' as test_id,
        'fixed' as test_type, 'fct_311_requests' as table_name,
        cast(null as varchar) as column_name, 'row_count' as metric,
        'year=' || y::varchar as grain, cast(null as varchar) as expected_value,
        0.0 as tolerance_pct, true as is_active, now() as certified_at, 'system' as certified_by
    from (
        select distinct year(date_created_dt) as y
        from main_gold.fct_311_requests
        where date_created_dt >= date '2015-01-01'
          and year(date_created_dt) < year(current_date)
    ) years
    union all
    select s.test_id, 'fixed', s.table_name, cast(null as varchar), 'row_count', s.grain,
           cast(null as varchar), 0.0, true, now(), 'system'
    from (values
        ('fixed.fct_311_requests.year_2024.ward_3.row_count',          'fct_311_requests',    'year=2024,ward=3'),
        ('fixed.fct_crime_incidents.year_2024.row_count',              'fct_crime_incidents', 'year=2024'),
        ('fixed.fct_citations.year_2024.row_count',                    'fct_citations',       'year=2024'),
        ('fixed.fct_permits.issue_year_2021.building_issued.row_count', 'fct_permits',        'issue_year=2021,building,issued')
    ) as s(test_id, table_name, grain)
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
    select * from rolling_checks
    union all
    select * from fixed_checks
    union all
    select * from dbt_tests
)

select * from all_tests
{% if is_incremental() %}
where test_id not in (select test_id from {{ this }})
{% endif %}
