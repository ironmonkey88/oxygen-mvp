{{ config(materialized='table', schema='gold') }}

-- Gold: dim_survey_question -- the 8 satisfaction Likert columns that
-- survived the Plan 23 Phase D cross-wave-presence filter. Hand-rolled
-- because the source bronze documents column names mechanically (no
-- per-column question text); the question_label values here are short
-- paraphrases marked [paraphrase] -- the exact survey wording can be
-- enriched in a future plan if the Socrata metadata exposes it.
--
-- Topic taxonomy (5 buckets covering the 8 questions):
--   core_wellbeing       -- the headline happiness + life-satisfaction +
--                           "place to live" trio
--   neighborhood         -- neighborhood-level questions (beauty)
--   city_services        -- service-delivery satisfaction (streets)
--   community_education  -- community + education
--   civic_information    -- information availability
--
-- first_wave_asked / last_wave_asked / waves_asked_count summarize the
-- Phase D matrix in docs/limitations/happiness-survey-self-selection-and-coverage.md.
-- "Asked" here means "wave where the column has >50% non-NULL".
-- Non-contiguous coverage (e.g. social_community_events skipped 2017)
-- is documented in schema.yml.

select * from (
  values
    ('happiness',                          'happiness_num',                                          '[paraphrase] Overall happiness right now',                                        'core_wellbeing',      1, 5, 2011, 2025, 8),
    ('life_satisfaction',                  'life_satisfaction_num',                                  '[paraphrase] Life satisfaction overall',                                          'core_wellbeing',      1, 5, 2011, 2025, 8),
    ('somerville_satisfaction',            'somerville_satisfaction_num',                            '[paraphrase] Satisfaction with Somerville as a place to live',                    'core_wellbeing',      1, 5, 2011, 2025, 8),
    ('beauty_neighborhood',                'beauty_neighborhood_satisfaction_num',                   '[paraphrase] Satisfaction with neighborhood beauty / aesthetics',                 'neighborhood',        1, 5, 2013, 2025, 7),
    ('streets_maintenance',                'streets_maintenance_satisfaction_num',                   '[paraphrase] Satisfaction with street maintenance',                               'city_services',       1, 5, 2013, 2025, 7),
    ('education_quality',                  'education_quality_satisfaction_num',                     '[paraphrase] Satisfaction with education quality',                                'community_education', 1, 5, 2011, 2021, 6),
    ('social_community_events',            'social_community_events_satisfaction_num',               '[paraphrase] Satisfaction with social and community events',                      'community_education', 1, 5, 2013, 2025, 6),
    ('city_services_information_availability', 'city_services_information_availability_satisfaction_num', '[paraphrase] Satisfaction with availability of information about city services', 'civic_information',   1, 5, 2015, 2025, 6)
) as t(
    survey_question_id,
    column_name,
    question_label,
    topic,
    scale_min,
    scale_max,
    first_wave_asked,
    last_wave_asked,
    waves_asked_count
)
