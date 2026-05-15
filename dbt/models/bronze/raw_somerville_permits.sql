{{ config(materialized='view', schema='bronze') }}

-- Bronze: passthrough view over the Somerville Permits mirror. Source
-- data is owned by dlt (`main_bronze.raw_somerville_permits_raw`),
-- replace mode -- the source is nearly 3 years stale (rowsUpdatedAt
-- 2023-05-16) so re-ingesting fresh on each manual run is fine.
--
-- 64,521 rows / 10 source columns. Arrival data only; type casts,
-- spatial-join-to-ward via lat/lng (no ward column at source), and
-- status-value cleanup (data quality issue: some rows have dates as
-- status values) are deferred to silver/gold (MVP 3 work).
--
-- See docs/limitations/permits-static-since-2023.md for the staleness
-- caveat + the status-column data quality issue.
select
    id,
    application_date,
    issue_date,
    type,
    status,
    amount,
    address,
    latitude,
    longitude,
    work,
    _extracted_at,
    _extracted_run_id,
    _source_endpoint,
    _dlt_load_id,
    _dlt_id
from {{ source('bronze_raw', 'raw_somerville_permits_raw') }}
