{{ config(materialized='table', schema='gold') }}

-- Gold: dim_ward — one row per administrative ward.
-- Source: Socrata `ym5n-phxd` (Wards), ingested by
-- `scripts/ingest_somerville_wards.py`. Static reference data; the
-- ward count won't change unless the city redistricts.
--
-- Surrogate key: md5 hash of ward number (consistent with other gold
-- dims). Natural join key is `ward` (VARCHAR), matching
-- `fct_311_requests.ward`.
--
-- Geometry kept as WGS84 WKT for portability. Areas converted from US
-- survey feet (source projection unit) to square meters and square
-- kilometers for analyst-friendly units.
select
    md5(cast(ward_number as varchar))                  as ward_id,
    cast(ward_number as varchar)                       as ward,
    'Ward ' || cast(ward_number as varchar)            as ward_name,
    geometry_wkt_wgs84,
    -- 1 US survey foot = 0.3048006096012192 m. 1 sq ft = 0.09290341161327... sq m.
    shape_area_sqftus * 0.09290341161327499            as area_sqm,
    shape_area_sqftus * 0.09290341161327499 / 1.0e6    as area_sqkm,
    shape_length_ftus * 0.3048006096012192             as perimeter_m,
    _source_url,
    _extracted_at
from {{ ref('raw_somerville_wards') }}
order by ward
