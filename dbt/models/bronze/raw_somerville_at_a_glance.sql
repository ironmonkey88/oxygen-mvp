{{ config(materialized='view', schema='bronze') }}

-- Bronze: passthrough view over the Somerville at a Glance mirror.
-- Source data is owned by dlt
-- (`main_bronze.raw_somerville_at_a_glance_raw`), replace mode.
-- Long/tidy format: one row per (topic, year, geography) tuple. 749
-- rows / 25 topics / 2 geographies (Somerville, Massachusetts).
--
-- This is the data source for the /somerville info portal page
-- (Prompt 11 Phase E) -- it's read directly by the generator script.
-- Not joined to operational data; serves as orienting context for a
-- new analyst or outside visitor.
--
-- Arrival data only; type casts (year, value -> INTEGER/DOUBLE) and
-- topic-key harmonization are deferred to silver/gold (MVP 3 work --
-- though for this dataset silver may never be needed since the source
-- shape is already analytically convenient).
select
    topic,
    description,
    year,
    value,
    units,
    geography,
    _extracted_at,
    _extracted_run_id,
    _source_endpoint,
    _dlt_load_id,
    _dlt_id
from {{ source('bronze_raw', 'raw_somerville_at_a_glance_raw') }}
