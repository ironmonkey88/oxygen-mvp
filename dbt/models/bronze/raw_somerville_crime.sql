{{ config(materialized='view', schema='bronze') }}

-- Bronze: passthrough view over the Somerville Police crime reports
-- mirror. Source data is owned by dlt
-- (`main_bronze.raw_somerville_crime_raw`); this view exposes the 11
-- source columns + audit metadata.
--
-- Source-level PII redaction is already applied at the city level
-- (sensitive incidents stripped of time / location), but the bronze
-- table is still PII-adjacent — see
-- docs/limitations/crime-data-pii-unredacted-in-bronze.md. Silver-layer
-- redaction is MVP 3 work.
--
-- Note: `ward` is space-padded to length 15 in source (e.g. '1
-- '). Trim at join to gold's dim_ward.ward. See
-- docs/limitations/crime-data-pii-unredacted-in-bronze.md and
-- docs/limitations/block-code-padded.md for related source-data
-- shape quirks.
select
    incnum,
    day_and_month,
    year,
    police_shift,
    offensecode,
    offense,
    incdesc,
    offensetype,
    category,
    blockcode,
    ward,
    _extracted_at,
    _extracted_run_id,
    _first_seen_at,
    _source_endpoint,
    _dlt_load_id,
    _dlt_id
from {{ source('bronze_raw', 'raw_somerville_crime_raw') }}
