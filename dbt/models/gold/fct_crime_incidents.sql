{{ config(materialized='table', schema='gold') }}

-- Gold: fct_crime_incidents -- one row per Somerville Police incident.
-- Source: main_bronze.raw_somerville_crime (dlt-merged from Socrata
-- `aghs-hqvg`). 22,325 rows as of 2026-05-13.
--
-- Grain: one row per source case number (`incnum`). Surrogate PK
-- (md5 of case_number) matches the project's gold-dim pattern;
-- case_number is preserved on the fact so analysts can back-reference
-- the public Somerville Police log.
--
-- Three source-data realities the transformation handles:
--
-- (1) Sensitive-incident redaction. 2,798 rows (12.5%) have their
-- day-and-month, block code, and ward stripped at source to protect
-- victim privacy. These rows surface as incident_year_only=TRUE with
-- NULL incident_dt + NULL block_code. They retain a valid
-- incident_year. The sensitive-incident incnum uses a 9-char sentinel
-- format (`1xxxxxxxx`) distinct from the 8-char year-prefixed format
-- of non-sensitive incidents (`YYxxxxxx`). See limitations:
-- crime-sensitive-incidents-no-month.
--
-- (2) Multi-code offense conventions. 2,875 rows (12.9%) carry a
-- comma-separated offense_code rather than a single NIBRS code.
-- Two source-convention groupings exist: '991, 998, 999' (= "Other
-- Criminal MV Offenses", 2,500 rows) and '11A - 11D, 36A, 36B' (=
-- "Sex Offenses", 375 rows). DEVIATION FROM PLAN 13 DESIGN: rather
-- than NULLing offense_code on these rows, we preserve the source
-- string as the offense_code value and include both groupings as rows
-- in dim_offense_code. multi_offense_flag stays for analyst filtering.
-- See limitations: crime-multi-offense-rows.
--
-- (3) Ward coverage gaps. 2,911 rows (13.0%) have NULL ward; 2 rows
-- carry 'CAM' (apparent Cambridge cross-jurisdiction). The bronze
-- source pads ward to length 15 with spaces; we trim here. See
-- limitations: crime-ward-coverage-gaps.
select
    md5(incnum)                                                          as incident_id,
    incnum                                                               as case_number,
    case
        when day_and_month is null then null
        else try_strptime(year || '/' || day_and_month, '%Y/%m/%d')::date
    end                                                                  as incident_dt,
    cast(year as smallint)                                               as incident_year,
    (day_and_month is null)                                              as incident_year_only,
    police_shift,
    offensecode                                                          as offense_code,
    (offensecode like '%,%')                                             as multi_offense_flag,
    offense,
    offensetype                                                          as offense_type,
    category                                                             as offense_category,
    nullif(trim(ward), '')                                               as ward,
    blockcode                                                            as block_code,
    _extracted_at,
    _extracted_run_id,
    _first_seen_at,
    _source_endpoint
from {{ ref('raw_somerville_crime') }}
