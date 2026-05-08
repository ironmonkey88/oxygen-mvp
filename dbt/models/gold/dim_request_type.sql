{{ config(materialized='table', schema='gold') }}

select
    md5(type)                                  as request_type_id,
    type                                       as request_type,
    cast(min(date_created::timestamp) as date) as first_seen_dt,
    cast(max(date_created::timestamp) as date) as last_seen_dt,
    count(*)                                   as request_count
from {{ ref('raw_311_requests') }}
group by type
