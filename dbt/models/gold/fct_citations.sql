{{ config(materialized='table', schema='gold') }}

-- Gold: fct_citations -- one row per (Somerville traffic citation,
-- violation). Source: main_bronze.raw_somerville_traffic_citations
-- (dlt-merged from Socrata `3mqx-eye9`). 67,311 rows covering
-- 2017-01-01 to 2026-03-27 (daily refresh in run.sh stage 1c).
--
-- HONEST-FINDING DEVIATION FROM PROMPT: pre-flight 2026-05-15 found
-- that the source publishes `ward` directly with only 0.12% NULL
-- (84 / 67,311 rows). Spatial join not needed -- using source `ward`
-- is cleaner and more reliable than ST_Contains (99.82% spatial
-- match would have surfaced more unmatched rows than the source's
-- 0.12% NULL rate). The Plan 23 Phase A spatial pre_hook pattern is
-- correctly absent here.
--
-- Source-quality realities passed through:
--   - vehiclemph is 82.5% NULL (55,523 of 67,311) -- speed is
--     recorded only on speed-related violations. 4 rows have
--     vehiclemph > 100 (including one at 62,021 -- data-entry error
--     at source). Passthrough; measure filters take care of it.
--   - citationnum carries a numeric suffix on EVERY row (5,708
--     "root" citations have multiple violations -- 67,311 rows total,
--     61,603 distinct after suffix-strip). Grain is (citation,
--     violation); preserved as-is per the
--     citations-composite-grain-violation-suffix limitation. Silver
--     work will derive a citation-grain table.
--   - warning Y/N split: 51,422 'Y' (warnings) vs 15,889 'N' (fines).
--     is_warning boolean derived for analyst convenience.
select
    md5(citationnum)                                                          as citation_id,
    citationnum                                                               as citation_number,
    dtissued                                                                  as citation_ts,
    cast(dtissued as date)                                                    as citation_date,
    cast(extract(year from dtissued) as smallint)                             as citation_year,
    police_shift,
    chgcode                                                                   as charge_code,
    chgdesc                                                                   as charge_description,
    chgcategory                                                               as charge_category,
    try_cast(vehiclemph as integer)                                           as vehicle_mph,
    try_cast(mphzone as integer)                                              as posted_mph_zone,
    try_cast(lat as double)                                                   as latitude,
    try_cast("long" as double)                                                as longitude,
    nullif(trim(ward), '')                                                    as ward,
    blockcode                                                                 as block_code,
    address,
    warning                                                                   as warning_flag,
    (warning = 'Y')                                                           as is_warning,
    _extracted_at,
    _extracted_run_id,
    _source_endpoint
from {{ ref('raw_somerville_traffic_citations') }}
