{{ config(materialized='table', schema='gold') }}

-- is_open mapping (no ambiguity in the four observed values):
--   'Closed'      → false
--   'Open'        → true
--   'In Progress' → true (still active)
--   'On Hold'     → true (paused but not closed)
select
    md5(most_recent_status)                                          as status_id,
    most_recent_status                                               as status,
    case when most_recent_status = 'Closed' then false else true end as is_open,
    cast(min(date_created::timestamp) as date)                       as first_seen_dt,
    cast(max(date_created::timestamp) as date)                       as last_seen_dt
from {{ ref('raw_311_requests') }}
group by most_recent_status
