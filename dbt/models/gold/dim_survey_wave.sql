{{ config(materialized='table', schema='gold') }}

-- Gold: dim_survey_wave -- one row per Happiness Survey wave year.
-- Data-driven from silver (so the row counts + ward coverage stay in
-- sync with the source on every refresh, rather than being hand-coded
-- numbers that could drift).
--
-- The 2011 wave is the analytical odd-one-out: 6,167 respondents (49%
-- of total dataset) but 0% ward coverage. The notes column flags this
-- so analysts see it without having to consult limitations. Gold fact
-- excludes 2011 from ward-level aggregation but keeps it at city level
-- for the questions it asked (happiness / life_satisfaction /
-- somerville_satisfaction).

with wave_stats as (
    select
        year,
        count(*)                                          as respondent_count,
        count(ward)                                       as rows_with_ward,
        round(100.0 * count(ward) / count(*), 1)          as ward_coverage_pct
    from {{ ref('stg_happiness_survey') }}
    where year is not null
    group by year
)

select
    cast(year as varchar)                                  as survey_wave_id,
    year                                                   as wave_year,
    cast(respondent_count as integer)                      as respondent_count,
    ward_coverage_pct,
    case
        when year = 2011 then 'Distributed differently from later waves; ward not collected. City-level only -- excluded from ward aggregation in fct_happiness_survey.'
        when ward_coverage_pct >= 95 then 'Standard biennial wave; ward coverage healthy.'
        else 'Standard biennial wave; ward coverage partial.'
    end                                                    as notes
from wave_stats
order by year
