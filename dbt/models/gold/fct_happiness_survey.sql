{{ config(materialized='table', schema='gold') }}

-- Gold: fct_happiness_survey -- trend-only perception fact at
-- (wave, geography_level, geography_key, question) grain. The first
-- analyst-facing perception surface in the warehouse (Plan 44, MVP 3).
--
-- Grain produces three row families:
--   * (wave, 'city', NULL, question) -- one row per wave per question
--     that was asked in that wave (>0 responses); all 8 waves
--     including 2011.
--   * (wave, 'ward', ward, question) -- one row per wave per ward per
--     question that was asked in that wave; 2013-2025 only.
--   * 2011 produces no ward rows by design -- the 2011 wave's ward
--     column is 0% populated and aggregating "NULL ward" as a single
--     row would be misleading. See dim_survey_wave.notes for 2011.
--
-- Aggregates ship UNWEIGHTED. The weight_strategy column is NULL on
-- every row today. A future plan that names a defensible weighting
-- strategy populates this column and recomputes the Likert
-- distributions weighted; until then, every aggregate describes
-- respondents who answered, not Somerville residents. See
-- docs/limitations/survey-gold-unweighted.md.
--
-- Likert-distribution columns (score_1_count..score_5_count) let
-- semantic-layer measures compute top-two-box / bottom-two-box
-- percentages without re-querying silver.

with respondents as (
    select
        year,
        ward,
        happiness_num,
        life_satisfaction_num,
        somerville_satisfaction_num,
        beauty_neighborhood_satisfaction_num,
        streets_maintenance_satisfaction_num,
        education_quality_satisfaction_num,
        social_community_events_satisfaction_num,
        city_services_information_availability_satisfaction_num
    from {{ ref('stg_happiness_survey') }}
),

-- Unpivot the 8 columns to (year, ward, question_id, score) so we can
-- aggregate uniformly across questions.
unpivoted as (
    select year, ward, 'happiness'                          as survey_question_id, happiness_num                                          as score from respondents
    union all
    select year, ward, 'life_satisfaction',                                       life_satisfaction_num                                  from respondents
    union all
    select year, ward, 'somerville_satisfaction',                                 somerville_satisfaction_num                            from respondents
    union all
    select year, ward, 'beauty_neighborhood',                                     beauty_neighborhood_satisfaction_num                   from respondents
    union all
    select year, ward, 'streets_maintenance',                                     streets_maintenance_satisfaction_num                   from respondents
    union all
    select year, ward, 'education_quality',                                       education_quality_satisfaction_num                     from respondents
    union all
    select year, ward, 'social_community_events',                                 social_community_events_satisfaction_num               from respondents
    union all
    select year, ward, 'city_services_information_availability',                  city_services_information_availability_satisfaction_num from respondents
),

-- City-level aggregation: includes 2011.
city_grain as (
    select
        cast(year as varchar)            as survey_wave_id,
        'city'                           as geography_level,
        cast(null as varchar)            as geography_key,
        survey_question_id,
        count(score)                     as respondent_count,
        avg(score)                       as mean_score,
        median(score)                    as median_score,
        cast(count(*) filter (where score = 1) as integer) as score_1_count,
        cast(count(*) filter (where score = 2) as integer) as score_2_count,
        cast(count(*) filter (where score = 3) as integer) as score_3_count,
        cast(count(*) filter (where score = 4) as integer) as score_4_count,
        cast(count(*) filter (where score = 5) as integer) as score_5_count
    from unpivoted
    where score is not null
    group by year, survey_question_id
),

-- Ward-level aggregation: 2013+ only (2011 has 0% ward coverage);
-- excludes NULL-ward rows from later waves.
ward_grain as (
    select
        cast(year as varchar)            as survey_wave_id,
        'ward'                           as geography_level,
        ward                             as geography_key,
        survey_question_id,
        count(score)                     as respondent_count,
        avg(score)                       as mean_score,
        median(score)                    as median_score,
        cast(count(*) filter (where score = 1) as integer) as score_1_count,
        cast(count(*) filter (where score = 2) as integer) as score_2_count,
        cast(count(*) filter (where score = 3) as integer) as score_3_count,
        cast(count(*) filter (where score = 4) as integer) as score_4_count,
        cast(count(*) filter (where score = 5) as integer) as score_5_count
    from unpivoted
    where score is not null
      and year >= 2013
      and ward is not null
    group by year, ward, survey_question_id
),

combined as (
    select * from city_grain
    union all
    select * from ward_grain
)

select
    md5(survey_wave_id || '|' || geography_level || '|' || coalesce(geography_key, 'NULL') || '|' || survey_question_id) as survey_observation_id,
    survey_wave_id,
    survey_question_id,
    geography_level,
    geography_key,
    cast(respondent_count as integer)  as respondent_count,
    mean_score,
    median_score,
    score_1_count,
    score_2_count,
    score_3_count,
    score_4_count,
    score_5_count,
    cast(null as varchar)              as weight_strategy
from combined
where respondent_count > 0
