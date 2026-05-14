{{ config(materialized='table', schema='gold') }}

-- Gold: dim_offense_code -- one row per distinct offense_code value
-- observed in fct_crime_incidents. 39 rows: 37 atomic NIBRS codes
-- (3-character) plus the 2 source-side multi-code grouping strings
-- used for "Other Criminal MV Offenses" and "Sex Offenses".
--
-- Joins to fct_crime_incidents.offense_code without a multi-offense
-- carve-out (Plan 13 Phase 2 deviation from the Chat design -- see
-- Phase 2 commit message and docs/limitations/crime-multi-offense-rows.md).
--
-- The dim sources from the fact rather than bronze so cleanup
-- (offensecode column transforms) flows from one place. is_active
-- is always TRUE today; placeholder for future code retirement.
select distinct
    offense_code,
    offense,
    offense_type,
    offense_category,
    multi_offense_flag                                          as is_multi_offense_grouping,
    true                                                        as is_active
from {{ ref('fct_crime_incidents') }}
where offense_code is not null
order by offense_code
