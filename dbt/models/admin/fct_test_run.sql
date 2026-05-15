{{ config(
    materialized='incremental',
    schema='admin',
    incremental_strategy='append'
) }}

-- One row per test per run. Two row sources:
--   (a) baseline comparisons -- compare current row counts (yearly +
--       per-table totals) against the frozen expected_value in
--       dim_data_quality_test, compute variance, set status.
--   (b) dbt test results -- parsed from raw_dbt_results_raw for the
--       latest run_id; status mapped from dbt's status field.
--
-- Append-only with `is_incremental()` filter on run_id so we never
-- duplicate a run's results.

with latest_run as (
    select
        run_id,
        max(loaded_at)        as run_at,
        max(run_started_at)   as run_started_at
    from main_bronze.raw_dbt_results_raw
    group by run_id
    order by run_at desc
    limit 1
),

yearly_actuals as (
    select
        'baseline.raw_311_requests.year_' || year::varchar || '.row_count' as test_id,
        count(*)::varchar                                                  as actual_value
    from (
        select extract(year from date_created::timestamp) as year
        from main_bronze.raw_311_requests
        where date_created::timestamp >= timestamp '2015-01-01'
          and date_created::timestamp <  timestamp '2027-01-01'
    ) y
    group by year
),

total_actuals as (
    select 'baseline.raw_311_requests.all.row_count' as test_id, count(*)::varchar as actual_value
    from main_bronze.raw_311_requests
    union all select 'baseline.dim_date.all.row_count',          count(*)::varchar from main_gold.dim_date
    union all select 'baseline.dim_request_type.all.row_count',  count(*)::varchar from main_gold.dim_request_type
    union all select 'baseline.dim_status.all.row_count',        count(*)::varchar from main_gold.dim_status
    union all select 'baseline.fct_311_requests.all.row_count',  count(*)::varchar from main_gold.fct_311_requests
),

all_actuals as (
    select * from yearly_actuals
    union all
    select * from total_actuals
),

baseline_runs as (
    -- Prompt 10 Item 3: the join no longer filters on `is_active = true`
    -- so we can distinguish three cases by the dim columns:
    --   (a) dim row missing entirely     -> truly unregistered test -> warn
    --   (b) dim row exists, is_active=F  -> intentionally inactive  -> warn
    --   (c) dim row exists, is_active=T  -> active baseline         -> compare
    -- The drift-fail guardrail (downstream dbt test) keys on status='fail',
    -- so warns in both (a) and (b) stay silent to it.
    select
        lr.run_id                                                                                   as run_id,
        a.test_id                                                                                   as test_id,
        lr.run_at                                                                                   as run_at,
        a.actual_value                                                                              as actual_value,
        case
            when d.is_active is distinct from true then null
            else d.expected_value
        end                                                                                         as expected_value,
        case
            when d.is_active is distinct from true then null
            when cast(d.expected_value as double) = 0 then null
            else (cast(a.actual_value as double) - cast(d.expected_value as double))
                 / cast(d.expected_value as double)
        end                                                                                         as variance_pct,
        case
            when d.test_id is null                        then 'warn'
            when d.is_active = false                      then 'warn'
            when cast(d.expected_value as double) = 0
                 and cast(a.actual_value as double) = 0   then 'pass'
            when cast(d.expected_value as double) = 0     then 'fail'
            when abs( (cast(a.actual_value as double) - cast(d.expected_value as double))
                       / nullif(cast(d.expected_value as double), 0) ) <= d.tolerance_pct
                 then 'pass'
            else 'fail'
        end                                                                                         as status,
        case
            when d.test_id is null
                 then 'no baseline registered for this test_id'
            when d.is_active = false
                 then 'baseline intentionally inactive -- current-year row count is unstable by design (see drift-fail-current-year-baseline-unstable)'
            when cast(d.expected_value as double) = 0 and cast(a.actual_value as double) <> 0
                 then 'expected 0 rows, got ' || a.actual_value
            when abs( (cast(a.actual_value as double) - cast(d.expected_value as double))
                       / nullif(cast(d.expected_value as double), 0) ) > d.tolerance_pct
                 then 'variance ' || round(
                          (cast(a.actual_value as double) - cast(d.expected_value as double))
                          / nullif(cast(d.expected_value as double), 0) * 100, 2
                      )::varchar || '% exceeds tolerance ' || (d.tolerance_pct*100)::varchar || '%'
            else null
        end                                                                                         as failure_message
    from latest_run lr
    cross join all_actuals a
    left join {{ ref('dim_data_quality_test') }} d
      on d.test_id = a.test_id
),

dbt_test_runs as (
    select
        r.run_id                                              as run_id,
        'dbt_test.' || r.node_name                            as test_id,
        r.loaded_at                                           as run_at,
        cast(r.failures as varchar)                           as actual_value,
        '0'                                                   as expected_value,
        cast(null as double)                                  as variance_pct,
        case r.status
            when 'pass'    then 'pass'
            when 'success' then 'pass'
            when 'warn'    then 'warn'
            when 'error'   then 'fail'
            when 'fail'    then 'fail'
            else r.status
        end                                                   as status,
        r.message                                             as failure_message
    from main_bronze.raw_dbt_results_raw r
    inner join latest_run lr on r.run_id = lr.run_id
    where r.node_id like 'test.%'
),

all_runs as (
    select * from baseline_runs
    union all
    select * from dbt_test_runs
)

select * from all_runs
{% if is_incremental() %}
where run_id not in (select distinct run_id from {{ this }})
{% endif %}
