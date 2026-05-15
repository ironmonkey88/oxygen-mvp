{{ config(materialized='view', schema='bronze') }}

-- Bronze: passthrough view over the Somerville Happiness Survey mirror.
-- Source data is owned by dlt (`main_bronze.raw_somerville_happiness_survey_raw`),
-- replace-mode (the survey is biennial and only ~12.5K rows).
--
-- DEPARTURE FROM PRECEDENT: the 311 + crime bronze views list every
-- source column explicitly so a renamed/removed source column trips a
-- loud dbt compile error. This view uses `select *` because the survey
-- has 150 columns -- enumerating them buys little signal at a cost of
-- noise. Per-column documentation lives in schema.yml's column entries.
-- The schema-drift signal moves to the dbt tests on the key columns
-- (id, year, ward) -- if a source rename breaks one of those, the test
-- fails. The 130+ Likert columns are tolerated as a known long tail.
--
-- Arrival data only; type casts, deduplication, year-aware filtering
-- for column drift across waves, and PII / quasi-identifier handling
-- are deferred to silver/gold (MVP 3 work).
select * from {{ source('bronze_raw', 'raw_somerville_happiness_survey_raw') }}
