-- CP-12: 311 status history, one row per request per status period (SCD Type 2).
-- Built from snapshots/snap_311_status.sql, which captures each daily pull.
-- observed_from/observed_to are when our pipeline saw the status; status_date is the
-- city's own date for that status change. History starts with the first snapshot run.
select
    id                                              as request_id,
    most_recent_status                              as status,
    try_cast(most_recent_status_date as date)       as status_date,
    dbt_valid_from                                  as observed_from,
    dbt_valid_to                                    as observed_to,
    dbt_valid_to is null                            as is_current
from {{ ref('snap_311_status') }}
