{{ config(materialized='table', schema='gold') }}

with bounds as (
    select
        min(date_created::timestamp)::date                              as min_dt,
        (max(date_created::timestamp)::date + interval '30 days')::date as max_dt
    from {{ ref('raw_311_requests') }}
),
spine as (
    select unnest(generate_series(b.min_dt, b.max_dt, interval '1 day'))::date as date_dt
    from bounds b
)
select
    date_dt,
    extract(year    from date_dt)::integer  as year,
    extract(quarter from date_dt)::integer  as quarter,
    extract(month   from date_dt)::integer  as month,
    strftime(date_dt, '%B')                 as month_name,
    extract(day     from date_dt)::integer  as day,
    extract(dow     from date_dt)::integer  as day_of_week,
    strftime(date_dt, '%A')                 as day_name,
    extract(week    from date_dt)::integer  as week_of_year,
    case when extract(dow from date_dt) in (0, 6) then true else false end as is_weekend,
    extract(year from date_dt)::integer     as fiscal_year
from spine
