{{ config(
    materialized='incremental',
    schema='admin',
    incremental_strategy='append'
) }}

-- One row per test per run. Four row sources:
--   (a) frozen baselines -- closed-year raw_311_requests row counts
--       compared against the expected_value frozen in
--       dim_data_quality_test (1% tolerance).
--   (b) rolling checks -- table totals compared against the average of
--       the same count over the previous N runs (2026-10-08). Replaces
--       the frozen per-table total baselines, which compared a growing
--       dataset against 2026-05-08 counts and failed every run from
--       2026-06-23 on, keeping pipeline-refresh red for normal growth.
--   (c) fixed subsets -- closed-period slices with a known answer
--       (e.g. 311 requests created in 2024). Each must equal its FIRST
--       recorded value exactly; any change means history was restated
--       or a load went wrong. Comparing to the first value (not the
--       previous run) keeps a change red until someone re-baselines it,
--       instead of self-clearing on the next run. Closed years join
--       automatically as each calendar year ends.
--   (d) dbt test results -- parsed from raw_dbt_results_raw for the
--       latest run_id; status mapped from dbt's status field.
--
-- Append-only with `is_incremental()` filter on run_id so we never
-- duplicate a run's results. History for (b) and (c) is read from this
-- table's own earlier rows, so on a full refresh they warn until enough
-- runs accumulate.

{% set rolling_window = var('dq_rolling_window', 7) %}
{% set rolling_min_runs = var('dq_rolling_min_runs', 3) %}
{% set rolling_tolerance = var('dq_rolling_tolerance', 0.05) %}

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

-- (a) ---------------------------------------------------------------
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
    cross join yearly_actuals a
    left join {{ ref('dim_data_quality_test') }} d
      on d.test_id = a.test_id
),

-- (b) ---------------------------------------------------------------
rolling_actuals as (
    select 'rolling.raw_311_requests.all.row_count' as test_id, count(*)::varchar as actual_value
    from main_bronze.raw_311_requests
    union all select 'rolling.dim_date.all.row_count',          count(*)::varchar from main_gold.dim_date
    union all select 'rolling.dim_request_type.all.row_count',  count(*)::varchar from main_gold.dim_request_type
    union all select 'rolling.dim_status.all.row_count',        count(*)::varchar from main_gold.dim_status
    union all select 'rolling.fct_311_requests.all.row_count',  count(*)::varchar from main_gold.fct_311_requests
),

-- (c) ---------------------------------------------------------------
fixed_actuals as (
    -- Every closed calendar year of gold 311 requests. Proven stable:
    -- each closed year had exactly one value across all 105 runs from
    -- 2026-05-08 to 2026-10-07.
    select
        'fixed.fct_311_requests.year_' || year(date_created_dt)::varchar || '.row_count' as test_id,
        count(*)::varchar                                                              as actual_value
    from main_gold.fct_311_requests
    where date_created_dt >= date '2015-01-01'
      and year(date_created_dt) < year(current_date)
    group by year(date_created_dt)
    union all
    select 'fixed.fct_311_requests.year_2024.ward_3.row_count', count(*)::varchar
    from main_gold.fct_311_requests
    where year(date_created_dt) = 2024 and ward = '3'
    union all
    select 'fixed.fct_crime_incidents.year_2024.row_count', count(*)::varchar
    from main_gold.fct_crime_incidents
    where incident_year = 2024
    union all
    select 'fixed.fct_citations.year_2024.row_count', count(*)::varchar
    from main_gold.fct_citations
    where citation_year = 2024
    union all
    select 'fixed.fct_permits.issue_year_2021.building_issued.row_count', count(*)::varchar
    from main_gold.fct_permits
    where permit_type ilike '%building%' and permit_status = 'Issued' and issue_year = 2021
),

-- History for (b) and (c): earlier rows of this table. The retired
-- frozen per-table total baselines recorded the same counts, so their
-- actual_values seed the rolling window (mapped baseline.* -> rolling.*).
history as (
{% if is_incremental() %}
    select
        case
            when test_id like 'baseline.%.all.row_count'
                then replace(test_id, 'baseline.', 'rolling.')
            else test_id
        end                 as test_id,
        run_id,
        run_at,
        actual_value
    from {{ this }}
    where actual_value is not null
      and (test_id like 'rolling.%'
           or test_id like 'fixed.%'
           or test_id like 'baseline.%.all.row_count')
      and run_id not in (select run_id from latest_run)
{% else %}
    select
        cast(null as varchar)                  as test_id,
        cast(null as varchar)                  as run_id,
        cast(null as timestamp with time zone) as run_at,
        cast(null as varchar)                  as actual_value
    where false
{% endif %}
),

rolling_stats as (
    select
        test_id,
        avg(cast(actual_value as double)) as rolling_avg,
        count(*)                          as n_runs
    from (
        select
            test_id,
            actual_value,
            row_number() over (partition by test_id order by run_at desc) as rn
        from history
        where test_id like 'rolling.%'
    ) ranked
    where rn <= {{ rolling_window }}
    group by test_id
),

rolling_runs as (
    select
        lr.run_id                                                   as run_id,
        a.test_id                                                   as test_id,
        lr.run_at                                                   as run_at,
        a.actual_value                                              as actual_value,
        case when coalesce(s.n_runs, 0) >= {{ rolling_min_runs }}
             then round(s.rolling_avg)::bigint::varchar end         as expected_value,
        case when coalesce(s.n_runs, 0) >= {{ rolling_min_runs }} and s.rolling_avg > 0
             then (cast(a.actual_value as double) - s.rolling_avg) / s.rolling_avg
        end                                                         as variance_pct,
        case
            when coalesce(s.n_runs, 0) < {{ rolling_min_runs }} then 'warn'
            when s.rolling_avg = 0
                 then case when cast(a.actual_value as double) = 0 then 'pass' else 'fail' end
            when abs((cast(a.actual_value as double) - s.rolling_avg) / s.rolling_avg)
                 <= {{ rolling_tolerance }} then 'pass'
            else 'fail'
        end                                                         as status,
        case
            when coalesce(s.n_runs, 0) < {{ rolling_min_runs }}
                 then 'only ' || coalesce(s.n_runs, 0)::varchar || ' prior runs; rolling check needs '
                      || '{{ rolling_min_runs }}'
            when s.rolling_avg = 0 and cast(a.actual_value as double) <> 0
                 then 'rolling average is 0, got ' || a.actual_value
            when s.rolling_avg > 0
                 and abs((cast(a.actual_value as double) - s.rolling_avg) / s.rolling_avg)
                     > {{ rolling_tolerance }}
                 then 'variance ' || round((cast(a.actual_value as double) - s.rolling_avg)
                                           / s.rolling_avg * 100, 2)::varchar
                      || '% vs ' || s.n_runs::varchar || '-run rolling average '
                      || round(s.rolling_avg)::bigint::varchar || ' exceeds tolerance '
                      || ({{ rolling_tolerance }} * 100)::varchar || '%'
            else null
        end                                                         as failure_message
    from latest_run lr
    cross join rolling_actuals a
    left join rolling_stats s on s.test_id = a.test_id
),

fixed_first as (
    select test_id, actual_value as first_value, run_at as first_run_at
    from (
        select
            test_id,
            actual_value,
            run_at,
            row_number() over (partition by test_id order by run_at asc) as rn
        from history
        where test_id like 'fixed.%'
    ) ranked
    where rn = 1
),

fixed_runs as (
    select
        lr.run_id                                                   as run_id,
        a.test_id                                                   as test_id,
        lr.run_at                                                   as run_at,
        a.actual_value                                              as actual_value,
        f.first_value                                               as expected_value,
        case when cast(f.first_value as double) > 0
             then (cast(a.actual_value as double) - cast(f.first_value as double))
                  / cast(f.first_value as double)
        end                                                         as variance_pct,
        case
            when f.first_value is null           then 'warn'
            when a.actual_value = f.first_value  then 'pass'
            else 'fail'
        end                                                         as status,
        case
            when f.first_value is null
                 then 'first run for this fixed subset; recording its answer'
            when a.actual_value <> f.first_value
                 then 'closed-period count changed: first recorded ' || f.first_value
                      || ' at ' || strftime(f.first_run_at, '%Y-%m-%d') || ', now ' || a.actual_value
            else null
        end                                                         as failure_message
    from latest_run lr
    cross join fixed_actuals a
    left join fixed_first f on f.test_id = a.test_id
),

-- (d) ---------------------------------------------------------------
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
    select * from rolling_runs
    union all
    select * from fixed_runs
    union all
    select * from dbt_test_runs
)

select * from all_runs
{% if is_incremental() %}
where run_id not in (select distinct run_id from {{ this }})
{% endif %}
