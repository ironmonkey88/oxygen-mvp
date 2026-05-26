{{ config(materialized='table', schema='silver') }}

-- Silver: stg_happiness_survey -- per-respondent clean view of the 8
-- analyst-usable satisfaction Likerts from the Somerville Happiness
-- Survey (Plan 44, the project's first silver model). One row per
-- (respondent_id, year). Source: bronze view raw_somerville_happiness_survey
-- over main_bronze.raw_somerville_happiness_survey_raw (12,583 rows,
-- 8 waves 2011-2025).
--
-- Curation discipline (Plan 23 Phase D matrix; pre-flight 2026-05-25
-- re-confirmed identical coverage):
--   - 8 of 50 `_num` satisfaction columns survived the
--     >=5-wave / <50%-NULL filter. Only those 8 surface here.
--   - Bronze stores everything as VARCHAR. We TRY_CAST `year` to
--     INTEGER and each `_num` column to DOUBLE so silver carries
--     analytical types.
--   - Ward is preserved NULL. The 2011 wave (6,167 rows) has 0% ward
--     coverage; 2013+ waves have 98-99%. The gold layer is the place
--     that excludes 2011 from ward aggregation -- silver keeps the
--     full row set so the count(*) sanity check matches bronze.
--   - `weight` is reserved but NULL on every row today. A future plan
--     that names a defensible weighting strategy (e.g. raking to ACS
--     age x ward) populates this column; gold then propagates it via
--     weighted aggregates and stamps the chosen strategy into
--     `fct_happiness_survey.weight_strategy`. See
--     docs/limitations/survey-gold-unweighted.md.
--   - Demographics (age, gender, race, identity flags, household
--     composition, income) stay in bronze. Per the k-anonymity floor
--     in PHILOSOPHY.md sec.5, the protection is structural -- the dims
--     aren't in silver, so there's nothing to suppress in gold. A
--     future plan with explicit k-anon machinery would add them to
--     silver then. See docs/limitations/survey-trend-only-no-demographics.md.
--
-- PII redaction is n/a here -- bronze carries no direct identifiers
-- (no name, no email, no address), and the demographic columns we'd
-- need to suppress aren't being surfaced in the first place. Silver's
-- standard PII-redaction step is intentionally a no-op for this
-- dataset.

select
    cast(id as varchar)                                              as respondent_id,
    try_cast(year as integer)                                        as year,
    cast(ward as varchar)                                            as ward,
    try_cast(happiness_num as double)                                as happiness_num,
    try_cast(life_satisfaction_num as double)                        as life_satisfaction_num,
    try_cast(somerville_satisfaction_num as double)                  as somerville_satisfaction_num,
    try_cast(beauty_neighborhood_satisfaction_num as double)         as beauty_neighborhood_satisfaction_num,
    try_cast(streets_maintenance_satisfaction_num as double)         as streets_maintenance_satisfaction_num,
    try_cast(education_quality_satisfaction_num as double)           as education_quality_satisfaction_num,
    try_cast(social_community_events_satisfaction_num as double)     as social_community_events_satisfaction_num,
    try_cast(city_services_information_availability_satisfaction_num as double)
                                                                     as city_services_information_availability_satisfaction_num,
    cast(null as double)                                             as weight,
    _extracted_at,
    _dlt_load_id,
    _dlt_id
from {{ ref('raw_somerville_happiness_survey') }}
where id is not null
  and year is not null
