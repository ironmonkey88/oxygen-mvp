{{ config(materialized='view', schema='bronze') }}

-- Bronze: passthrough view over the Somerville Traffic Citations mirror.
-- Source data is owned by dlt
-- (`main_bronze.raw_somerville_traffic_citations_raw`), merge mode on
-- `citationnum`. ~67K rows; one row per (citation, violation) -- the
-- `citationnum` field carries a violation suffix (e.g. "T2725339-1").
-- Daily refresh in run.sh (stage 1c), source updates daily with a
-- one-month publication delay.
--
-- PII surface: low (no driver name, no license, no vehicle data; just
-- intersection address + violation + ward). See
-- docs/limitations/traffic-citations-location-and-violation-only.md.
--
-- Arrival data only; type casts, ward-trimming if space-padded like
-- crime's ward column, and any further redaction are deferred to
-- silver/gold (MVP 3 work).
select
    citationnum,
    dtissued,
    police_shift,
    address,
    chgcode,
    chgdesc,
    chgcategory,
    vehiclemph,
    mphzone,
    lat,
    long,
    blockcode,
    ward,
    warning,
    _extracted_at,
    _extracted_run_id,
    _first_seen_at,
    _source_endpoint,
    _dlt_load_id,
    _dlt_id
from {{ source('bronze_raw', 'raw_somerville_traffic_citations_raw') }}
