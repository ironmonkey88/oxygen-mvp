{{ config(
    materialized='table',
    schema='gold',
    pre_hook=["INSTALL spatial", "LOAD spatial"]
) }}

-- Gold: fct_permits -- one row per Somerville building / inspection
-- permit. Source: main_bronze.raw_somerville_permits (dlt-replaced from
-- Socrata `vxgw-vmky`). 64,521 rows covering 2014-02-13 to 2023-10-24.
--
-- The source dataset stopped refreshing on 2023-05-16 -- see
-- docs/limitations/permits-static-since-2023.md. Gold mirrors the source
-- shape; the staleness caveat is surfaced by the Answer Agent's trust
-- contract when permit-affecting queries are asked.
--
-- Ward derivation (no `ward` column at source). Point-in-polygon join
-- of (longitude, latitude) against dim_ward.geometry_wkt_wgs84 (WGS84
-- WKT). Spatial extension loaded via pre_hook so dbt can run this on
-- a clean DuckDB connection. Pre-flight 2026-05-15 result:
--   - 64,513 / 64,521 rows have latitude+longitude (99.99%).
--   - 62,337 / 64,521 rows match a ward polygon (96.62%).
--   - 2,176 rows (3.37%) have lat/lng but fall outside the 7 ward
--     polygons -- treated as NULL ward, same posture as crime's ~13%
--     NULL ward. See docs/limitations/permits-spatial-ward-derivation.md.
--
-- Source-quality realities passed through:
--   - 11 rows have NULL `type` (per Plan 21 honest-test discipline).
--   - 21 rows have NULL `status`; 6 rows have empty-string status;
--     3 rows carry dates as `status` values ("08/17/2022" etc.).
--   - `is_issued` derived as `status = 'Issued'` (96.68% of rows).
with ward_polys as (
    select
        ward,
        st_geomfromtext(geometry_wkt_wgs84) as geom
    from {{ ref('dim_ward') }}
),
permit_with_pt as (
    select
        *,
        case
            when latitude is null or longitude is null then null
            else st_point(cast(longitude as double), cast(latitude as double))
        end as pt
    from {{ ref('raw_somerville_permits') }}
),
permit_with_ward as (
    select
        p.*,
        w.ward as derived_ward
    from permit_with_pt p
    left join ward_polys w
        on p.pt is not null
       and st_contains(w.geom, p.pt)
)
select
    md5(id)                                                                       as permit_id,
    id                                                                            as permit_number,
    cast(application_date as date)                                                as application_date,
    cast(issue_date as date)                                                      as issue_date,
    cast(extract(year from application_date) as smallint)                         as application_year,
    cast(extract(year from issue_date) as smallint)                               as issue_year,
    type                                                                          as permit_type,
    status                                                                        as permit_status,
    (status = 'Issued')                                                           as is_issued,
    amount                                                                        as permit_amount,
    address,
    work                                                                          as work_description,
    derived_ward                                                                  as ward,
    latitude,
    longitude,
    _extracted_at,
    _extracted_run_id,
    _source_endpoint
from permit_with_ward
