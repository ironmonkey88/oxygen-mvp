{{ config(
    materialized='incremental',
    schema='admin',
    incremental_strategy='append'
) }}

-- Column-level profile snapshot. Append-only -- every run adds a fresh
-- batch tagged with profiled_at. Query max(profiled_at) for current
-- state, or trend over time for drift detection. Observational only;
-- never generates rows in fct_test_run.
--
-- Tables profiled: bronze.raw_311_requests + four gold tables.
-- Columns introspected via information_schema.columns at compile time.
-- All min/max values cast to varchar for uniform schema. _dlt_*
-- metadata columns are skipped -- they describe the load, not the data.

{% set tables_to_profile = [
    {'schema': 'main_bronze', 'name': 'raw_311_requests'},
    {'schema': 'main_gold',   'name': 'dim_date'},
    {'schema': 'main_gold',   'name': 'dim_request_type'},
    {'schema': 'main_gold',   'name': 'dim_status'},
    {'schema': 'main_gold',   'name': 'fct_311_requests'},
] %}

{% set profile_unions = [] %}
{% for t in tables_to_profile %}
  {% set get_cols_sql %}
    select column_name from information_schema.columns
    where table_schema = '{{ t.schema }}'
      and table_name   = '{{ t.name }}'
    order by ordinal_position
  {% endset %}
  {% if execute %}
    {% set cols_result = run_query(get_cols_sql) %}
    {% set col_names = cols_result.columns[0].values() %}
  {% else %}
    {% set col_names = [] %}
  {% endif %}
  {% for c in col_names %}
    {% if not c.startswith('_dlt_') %}
      {% set q %}
      select
        now()                                                                  as profiled_at,
        '{{ t.name }}'                                                         as table_name,
        '{{ c }}'                                                              as column_name,
        count(*)                                                               as row_count,
        count(*) - count("{{ c }}")                                            as null_count,
        cast(count(*) - count("{{ c }}") as double) / nullif(count(*), 0)      as pct_null,
        count(distinct "{{ c }}")                                              as distinct_count,
        cast(count(distinct "{{ c }}") as double) / nullif(count(*), 0)        as pct_distinct,
        cast(min("{{ c }}") as varchar)                                        as min_value,
        cast(max("{{ c }}") as varchar)                                        as max_value,
        min(length(cast("{{ c }}" as varchar)))                                as min_length,
        max(length(cast("{{ c }}" as varchar)))                                as max_length,
        avg(length(cast("{{ c }}" as varchar)))                                as avg_length
      from {{ t.schema }}.{{ t.name }}
      {% endset %}
      {% do profile_unions.append(q) %}
    {% endif %}
  {% endfor %}
{% endfor %}

{% if profile_unions %}
{{ profile_unions | join(' union all ') }}
{% else %}
-- compile-time introspection returned empty (e.g. tables not built yet)
select
  cast(null as timestamptz) as profiled_at,
  cast(null as varchar)     as table_name,
  cast(null as varchar)     as column_name,
  cast(null as bigint)      as row_count,
  cast(null as bigint)      as null_count,
  cast(null as double)      as pct_null,
  cast(null as bigint)      as distinct_count,
  cast(null as double)      as pct_distinct,
  cast(null as varchar)     as min_value,
  cast(null as varchar)     as max_value,
  cast(null as integer)     as min_length,
  cast(null as integer)     as max_length,
  cast(null as double)      as avg_length
where false
{% endif %}
