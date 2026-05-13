{{ config(materialized='view', schema='bronze') }}

-- Bronze: passthrough view over the Python-owned wards shapefile mirror.
-- Source data is owned by `scripts/ingest_somerville_wards.py`; this view
-- drops the binary GEOMETRY column (kept on the raw table for spatial
-- operations) and exposes WKT representations for portability + dbt
-- compatibility.
-- Static reference data: one row per administrative ward (7 wards).
select
    cast(ward as integer)                              as ward_number,
    cast(objectid as integer)                          as object_id,
    cast(ogc_fid as integer)                           as ogc_fid,
    shape_leng                                         as shape_length_ftus,
    shape_area                                         as shape_area_sqftus,
    geometry_wkt_wgs84,
    geometry_wkt_source,
    _source_srid,
    _extracted_at,
    _source_url,
    _source_filename
from {{ source('bronze_raw', 'raw_somerville_wards_raw') }}
