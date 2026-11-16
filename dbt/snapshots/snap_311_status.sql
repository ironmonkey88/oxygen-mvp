{% snapshot snap_311_status %}
{{
    config(
        schema='snapshots',
        unique_key='id',
        strategy='check',
        check_cols=['most_recent_status', 'most_recent_status_date'],
        hard_deletes='invalidate'
    )
}}
-- CP-12 (Gordon 2026-11-16, "like a scd"): the city publishes only each 311 request's
-- CURRENT status, and dlt merges on id, so yesterday's status is overwritten. This snapshot
-- keeps one row per request per status period from the day it ships. No backfill is
-- possible: history before the first snapshot run does not exist anywhere we can read.
select
    id,
    most_recent_status,
    most_recent_status_date::VARCHAR as most_recent_status_date
-- Read the dlt table directly (not the bronze view) so the snapshot runs before step 2.
from {{ source('bronze_raw', 'raw_311_requests_raw') }}
{% endsnapshot %}
