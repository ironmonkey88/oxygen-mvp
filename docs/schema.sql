-- =============================================================
-- schema.sql — Somerville 311 Analytics Platform
-- Source of truth for all table definitions.
-- ERD generated from this file. Do not edit the ERD directly.
--
-- Schemas: bronze, gold, admin
-- Silver is defined in MVP 3.
-- =============================================================


-- =============================================================
-- BRONZE — raw source data, exact mirror of SODA API
-- No transforms. All columns VARCHAR. Arrival checks only.
-- =============================================================

CREATE SCHEMA IF NOT EXISTS bronze;

-- Raw 311 requests as received from Somerville SODA API.
-- Column names and types preserved exactly as source delivers them.
-- block_code is padded with spaces in source — do not trim here.
CREATE TABLE IF NOT EXISTS bronze.raw_311_requests (
    id                                              VARCHAR,  -- primary key from source
    classification                                  VARCHAR,  -- Service / Information / Feedback
    category                                        VARCHAR,  -- e.g. Parking, Trash & Recycling
    type                                            VARCHAR,  -- sub-category within category
    origin_of_request                               VARCHAR,  -- Contact Center, Website, etc.
    date_created                                    VARCHAR,  -- timestamp with tz — kept as VARCHAR at bronze
    most_recent_status                              VARCHAR,  -- Open / Closed
    most_recent_status_date                         VARCHAR,  -- timestamp with tz — kept as VARCHAR at bronze
    block_code                                      VARCHAR,  -- sparse, padded with spaces when unknown
    ward                                            VARCHAR,  -- '1'–'7', NULL when unknown
    accuracy                                        VARCHAR,  -- survey: Satisfied / N/A / etc., sparse
    courtesy                                        VARCHAR,  -- survey, sparse
    ease                                            VARCHAR,  -- survey, sparse
    overallexperience                               VARCHAR,  -- survey, sparse
    emergency_readiness_and_response_planning       VARCHAR,  -- dept tag: '0' or '1', sparse
    green_space_care_and_maintenance                VARCHAR,  -- dept tag, sparse
    infrastructure_maintenance_and_repairs          VARCHAR,  -- dept tag, sparse
    noise_and_activity_disturbances                 VARCHAR,  -- dept tag, sparse
    reliable_service_delivery                       VARCHAR,  -- dept tag, sparse
    navigating_city_services_and_policies           VARCHAR,  -- dept tag, sparse
    public_space_cleanliness_and_environmental_health VARCHAR, -- dept tag, sparse
    voting_and_election_information                 VARCHAR,  -- dept tag, sparse

    -- dlt metadata: emitted by the ingest pipeline, retained at every layer
    -- (bronze → silver → gold) so any row can be traced back to its source load.
    _dlt_load_id                                    VARCHAR,  -- dlt load identifier, retained for lineage
    _dlt_id                                         VARCHAR   -- dlt row identifier, retained for lineage
);

-- Raw Somerville wards shapefile mirror — owned by scripts/ingest_somerville_wards.py.
-- Source: Socrata `ym5n-phxd` (Wards) blob, ESRI shapefile bundle.
-- Static reference data; drop+recreate on each ingestion run. One row per ward (7).
-- Geometry held in the source projection (NAD83/MA Mainland, EPSG:2249, US survey feet)
-- via DuckDB's spatial extension; WKT strings in both source projection and WGS84
-- are also persisted for portability + dbt-view compatibility.
CREATE TABLE IF NOT EXISTS bronze.raw_somerville_wards_raw (
    OGC_FID             BIGINT,   -- assigned by the spatial reader
    OBJECTID            BIGINT,   -- ESRI internal id
    WARD                BIGINT,   -- ward number 1–7
    Shape_Leng          DOUBLE,   -- polygon perimeter in US survey feet (source projection unit)
    Shape_Area          DOUBLE,   -- polygon area in sq US survey feet
    geom                GEOMETRY, -- binary geometry in NAD83/MA Mainland (EPSG:2249)
    geometry_wkt_wgs84  VARCHAR,  -- WKT in WGS84 (EPSG:4326) — analyst-friendly
    geometry_wkt_source VARCHAR,  -- WKT in source projection — round-trip-ready
    area_source_units   DOUBLE,   -- redundant with Shape_Area; double-check
    _extracted_at       TIMESTAMP,
    _source_url         VARCHAR,  -- canonical Socrata permalink
    _source_filename    VARCHAR,  -- source shapefile filename inside the ZIP blob
    _source_srid        VARCHAR   -- always 'EPSG:2249' for this dataset
);

-- Raw Somerville Police crime reports mirror — owned by
-- dlt/somerville_crime_pipeline.py. Source: Socrata `aghs-hqvg`.
-- Full pull + merge on PK `incnum` each run. 22K rows as of 2026-05-13;
-- data 2017-present. Source-level PII redaction already applied to
-- sensitive incidents (time/location stripped); project-side silver-layer
-- redaction is MVP 3 work. See
-- docs/limitations/crime-data-pii-unredacted-in-bronze.md.
CREATE TABLE IF NOT EXISTS bronze.raw_somerville_crime_raw (
    incnum              VARCHAR,  -- PK from source; the dlt merge key
    day_and_month       VARCHAR,  -- "M/D"; NULL/blank for sensitive incidents stripped at source
    year                VARCHAR,  -- "2017"–present
    police_shift        VARCHAR,
    offensecode         VARCHAR,  -- 3-char NIBRS code
    offense             VARCHAR,
    incdesc             VARCHAR,  -- NIBRS standard definition text; not victim-specific
    offensetype         VARCHAR,
    category            VARCHAR,  -- NIBRS top-level (Property/Person/Society/Other)
    blockcode           VARCHAR,  -- 15-char census block code; ~750 blocks
    ward                VARCHAR,  -- '1'–'7', space-padded to length 15 in source

    -- pipeline metadata (added by dlt/somerville_crime_pipeline.py)
    _extracted_at       TIMESTAMP,
    _extracted_run_id   VARCHAR,
    _first_seen_at      TIMESTAMP,  -- post-merge UPDATE; preserved across re-extractions
    _source_endpoint    VARCHAR,
    _dlt_load_id        VARCHAR,
    _dlt_id             VARCHAR
);

-- bronze.raw_somerville_at_a_glance_raw -- demographic/housing/economic KPIs
-- (Prompt 11 Phase D, 2026-05-14). Socrata `jnde-mi6j`. Replace mode: 749
-- rows / 6 columns. Long/tidy format: one row per (topic, description, year,
-- geography). 25 topics, 2 geographies (Somerville + Massachusetts), years
-- 1850 (historical population) - 2024 (ACS). Source updates annually with
-- ACS releases. Not wired into run.sh; re-run manually via
-- dlt/somerville_at_a_glance_pipeline.py. Read directly by the /somerville
-- info portal page (Prompt 11 Phase E).
CREATE TABLE IF NOT EXISTS bronze.raw_somerville_at_a_glance_raw (
    topic           VARCHAR,  -- top-level metric grouping (25 distinct values)
    description     VARCHAR,  -- sub-label within topic
    year            INTEGER,
    value           DOUBLE,   -- in the unit named by `units`
    units           VARCHAR,  -- "People" / "USD" / "Percent" / ...
    geography       VARCHAR,  -- 'Somerville' or 'Massachusetts'

    -- pipeline metadata (added by dlt/somerville_at_a_glance_pipeline.py)
    _extracted_at       TIMESTAMP,
    _extracted_run_id   VARCHAR,
    _source_endpoint    VARCHAR,
    _dlt_load_id        VARCHAR,
    _dlt_id             VARCHAR
    -- no _first_seen_at: replace mode wipes the table on each ingest
);

-- bronze.raw_somerville_traffic_citations_raw -- SPD traffic citations
-- (Prompt 11 Phase C, 2026-05-14). Socrata `3mqx-eye9`. Merge mode on
-- `citationnum`. ~67K rows / 14 columns; data 2017-present. Source refreshes
-- daily with a one-month publication delay. Wired into run.sh as stage 1c.
-- Grain: one row per (citation, violation); citationnum carries a violation
-- suffix (e.g. "T2725339-1"). PII surface is low -- intersection-level
-- address, violation type, ward, speed -- no driver name / license / vehicle.
-- See docs/limitations/traffic-citations-location-and-violation-only.md.
CREATE TABLE IF NOT EXISTS bronze.raw_somerville_traffic_citations_raw (
    citationnum         VARCHAR,  -- PK incl. violation suffix; dlt merge key
    dtissued            VARCHAR,  -- timestamp issued; cast to TIMESTAMP in silver
    police_shift        VARCHAR,
    address             VARCHAR,  -- intersection-level text
    chgcode             VARCHAR,  -- MGL violation code; space-padded
    chgdesc             VARCHAR,
    chgcategory         VARCHAR,  -- 109 distinct values
    vehiclemph          VARCHAR,  -- speed (text from source); NULL for non-speeding
    mphzone             VARCHAR,  -- posted speed limit
    lat                 VARCHAR,  -- geocoded latitude; precise to ~4 decimals
    long                VARCHAR,  -- geocoded longitude
    blockcode           VARCHAR,  -- 15-char census block code
    ward                VARCHAR,  -- '1'-'7'; NULL for ~0.12% of rows
    warning             VARCHAR,  -- 'Y' / 'N' (warning vs paid citation)

    -- pipeline metadata (added by dlt/somerville_traffic_citations_pipeline.py)
    _extracted_at       TIMESTAMP,
    _extracted_run_id   VARCHAR,
    _first_seen_at      TIMESTAMP,  -- post-merge UPDATE; preserved across re-extractions
    _source_endpoint    VARCHAR,
    _dlt_load_id        VARCHAR,
    _dlt_id             VARCHAR
);

-- bronze.raw_somerville_permits_raw -- ISD permit applications (Prompt 11 Phase B,
-- 2026-05-14). Socrata `vxgw-vmky`. Replace mode (not merge): 64,521 rows /
-- 10 columns, source `rowsUpdatedAt = 2023-05-16` (nearly 3 years stale). One
-- row per permit application; `id` is the source PK. Manual one-shot ingestion
-- via dlt/somerville_permits_pipeline.py; not wired into run.sh (no point on a
-- daily cadence when source is static). No ward column at source -- ward joins
-- require spatial via lat/lng (silver work). See
-- docs/limitations/permits-static-since-2023.md for staleness + status DQ.
CREATE TABLE IF NOT EXISTS bronze.raw_somerville_permits_raw (
    id                  VARCHAR,  -- PK; year-prefixed (e.g. B14-001277)
    application_date    VARCHAR,  -- calendar_date from source
    issue_date          VARCHAR,  -- calendar_date; NULL for non-issued applications
    type                VARCHAR,  -- ~20 values; mostly Residential Building / Commercial Building
    status              VARCHAR,  -- mostly "Issued"; known DQ issue: some rows carry dates
    amount              DOUBLE,   -- permit fee USD
    address             VARCHAR,  -- property address (public info, not applicant ID)
    latitude            DOUBLE,   -- WGS84
    longitude           DOUBLE,   -- WGS84
    work                VARCHAR,  -- freeform job description

    -- pipeline metadata (added by dlt/somerville_permits_pipeline.py)
    _extracted_at       TIMESTAMP,
    _extracted_run_id   VARCHAR,
    _source_endpoint    VARCHAR,
    _dlt_load_id        VARCHAR,
    _dlt_id             VARCHAR
    -- no _first_seen_at: replace mode wipes the table on each ingest
);

-- bronze.raw_somerville_happiness_survey_raw -- biennial city perception survey
-- (Prompt 11 Phase A, 2026-05-14). Socrata `wmeh-zuz2`.
-- Replace mode (not merge): 12,583 rows / 150 columns, static between waves
-- (next ~2027). One row per (respondent, survey_year); `id` is the source PK.
-- Manual one-shot ingestion via dlt/somerville_happiness_survey_pipeline.py;
-- not wired into run.sh. The DDL below documents only the analyst-relevant
-- columns -- dlt manages the actual schema and infers the long tail of ~120
-- {topic}_num / {topic}_label Likert pairs as VARCHAR / DOUBLE per source.
-- See dbt/models/bronze/schema.yml's raw_somerville_happiness_survey model
-- for per-column docs, and
-- docs/limitations/happiness-survey-self-selection-and-coverage.md for the
-- caveat list.
CREATE TABLE IF NOT EXISTS bronze.raw_somerville_happiness_survey_raw (
    id                                VARCHAR,  -- PK from source; year-prefixed integer
    year                              INTEGER,  -- survey wave: 2011, 2013, ..., 2025
    survey_method                     VARCHAR,
    survey_language                   VARCHAR,
    ward                              VARCHAR,  -- '1'-'7'; NULL for ~50% of rows (all 2011)
    tract                             VARCHAR,
    gender                            VARCHAR,
    age                               VARCHAR,  -- bucketed (e.g. "35 to 44")
    race_ethnicity                    VARCHAR,
    housing_status                    VARCHAR,  -- Renter / Owner / Other
    highest_level_education           VARCHAR,
    tenure                            VARCHAR,
    household_income                  VARCHAR,  -- bucketed
    likely_low_income                 INTEGER,  -- derived 0/1 flag
    likely_cost_burdened              INTEGER,  -- derived 0/1 flag
    language_spoken                   VARCHAR,
    -- + ~120 paired {topic}_num INTEGER + {topic}_label VARCHAR columns for
    --   ~40 satisfaction / concern topics (happiness, life satisfaction,
    --   somerville satisfaction, neighbors, safety, civic participation,
    --   parks, public spaces, streets, social events, housing options,
    --   grocery, health services, transportation, schools, childcare,
    --   city services, emergency response, etc.)
    -- + identity yes/no flags (children_yn, lgbtqia_yn, immigrant_yn,
    --   disability_yn, neurodivergent_yn, student_yn, veteran_yn,
    --   cultural_religious_minority_yn, etc.)
    -- + transportation_*_yn flags (bicycle, car, public_transit, walk, etc.)
    -- + difficulty_paying_*_yn flags
    -- + ACS context (census_year, acs_somerville_median_income,
    --   acs_somerville_avg_household, inflation_adjustment)

    -- pipeline metadata (added by dlt/somerville_happiness_survey_pipeline.py)
    _extracted_at       TIMESTAMP,
    _extracted_run_id   VARCHAR,
    _source_endpoint    VARCHAR,
    _dlt_load_id        VARCHAR,
    _dlt_id             VARCHAR
    -- no _first_seen_at: replace mode wipes the table on each ingest
);

-- Raw load of dbt run_results.json after each pipeline run.
-- Loaded by dlt/load_dbt_results.py. Parsed by admin models.
CREATE TABLE IF NOT EXISTS bronze.raw_dbt_results (
    loaded_at       TIMESTAMPTZ,  -- when this row was loaded
    run_id          VARCHAR,      -- dbt invocation id
    run_started_at  VARCHAR,      -- from run_results.json metadata
    node_id         VARCHAR,      -- dbt node unique_id
    node_name       VARCHAR,      -- short test name
    status          VARCHAR,      -- pass / fail / warn / error
    failures        INTEGER,      -- number of failing rows (tests only)
    message         VARCHAR,      -- dbt failure message if any
    execution_time  FLOAT         -- seconds
);


-- =============================================================
-- GOLD — business-ready facts and dimensions
-- Airlayer and agents point to this schema only.
-- =============================================================

CREATE SCHEMA IF NOT EXISTS gold;

-- Standard date spine. Generated by dbt macro — not sourced from 311 data.
-- Covers 2010-01-01 through 2030-12-31.
CREATE TABLE IF NOT EXISTS gold.dim_date (
    date_sk         INTEGER PRIMARY KEY,  -- surrogate key: YYYYMMDD e.g. 20240101
    date_dt         DATE NOT NULL,
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,     -- 1–4
    month           INTEGER NOT NULL,     -- 1–12
    month_name      VARCHAR NOT NULL,     -- January, February, ...
    week_of_year    INTEGER NOT NULL,     -- 1–53
    day_of_week     INTEGER NOT NULL,     -- 1=Monday, 7=Sunday
    day_name        VARCHAR NOT NULL,     -- Monday, Tuesday, ...
    is_weekend      BOOLEAN NOT NULL
);

-- Classification → category → type hierarchy.
-- Natural key is the concatenation of all three levels.
CREATE TABLE IF NOT EXISTS gold.dim_request_type (
    request_type_sk INTEGER PRIMARY KEY,
    request_type_id VARCHAR NOT NULL,     -- natural key: classification|category|type
    classification  VARCHAR NOT NULL,     -- Service / Information / Feedback
    category        VARCHAR NOT NULL,     -- e.g. Parking, Trash & Recycling
    type            VARCHAR NOT NULL      -- sub-category within category
);

-- Open / Closed status with boolean convenience columns.
CREATE TABLE IF NOT EXISTS gold.dim_status (
    status_sk       INTEGER PRIMARY KEY,
    status_id       VARCHAR NOT NULL,     -- natural key: raw status value
    status          VARCHAR NOT NULL,     -- Open / Closed
    is_open         BOOLEAN NOT NULL,
    is_closed       BOOLEAN NOT NULL
);

-- How the request was submitted: Contact Center, Website, etc.
-- Low cardinality — typically 5–10 distinct values.
-- Ward dim — 7 administrative wards (2020 Census redistricting).
-- Sourced from `scripts/ingest_somerville_wards.py` via bronze.raw_somerville_wards_raw.
-- Static reference data. Natural-key joins to fct_311_requests on `ward`.
CREATE TABLE IF NOT EXISTS gold.dim_ward (
    ward_id             VARCHAR PRIMARY KEY,  -- md5(ward) surrogate key
    ward                VARCHAR NOT NULL UNIQUE,  -- ward number 1–7 (VARCHAR for natural-key join)
    ward_name           VARCHAR,              -- 'Ward N' display label
    geometry_wkt_wgs84  VARCHAR,              -- polygon WKT in WGS84 (EPSG:4326)
    area_sqm            DOUBLE,               -- polygon area in sq meters
    area_sqkm           DOUBLE,               -- polygon area in sq kilometers (~1.3–2.7)
    perimeter_m         DOUBLE,               -- polygon perimeter in meters
    _source_url         VARCHAR,
    _extracted_at       TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold.dim_origin (
    origin_sk       INTEGER PRIMARY KEY,
    origin_id       VARCHAR NOT NULL,     -- natural key: raw origin value
    origin          VARCHAR NOT NULL
);

-- NIBRS offense code dim — 39 rows (37 atomic NIBRS codes + 2 source-side
-- multi-code grouping strings). Sources from fct_crime_incidents.
CREATE TABLE IF NOT EXISTS gold.dim_offense_code (
    offense_code                VARCHAR PRIMARY KEY,
    offense                     VARCHAR NOT NULL,
    offense_type                VARCHAR NOT NULL,
    offense_category            VARCHAR NOT NULL,
    is_multi_offense_grouping   BOOLEAN NOT NULL,
    is_active                   BOOLEAN NOT NULL
);

-- NIBRS top-level category dim — 4 rows, hardcoded.
-- severity_rank is editorial (1=Person, 2=Property, 3=Society, 4=Other).
CREATE TABLE IF NOT EXISTS gold.dim_offense_category (
    offense_category    VARCHAR PRIMARY KEY,
    severity_rank       SMALLINT NOT NULL UNIQUE
);

-- One row per Somerville Police incident report. Source: bronze.raw_somerville_crime
-- via dlt merge on `incnum`. Three source-data realities surfaced via flags +
-- limitations: sensitive-incident redaction (incident_year_only), multi-code offense
-- groupings (multi_offense_flag), ward coverage gaps (ward NULL / 'CAM').
CREATE TABLE IF NOT EXISTS gold.fct_crime_incidents (
    incident_id                 VARCHAR PRIMARY KEY,                  -- md5(case_number)
    case_number                 VARCHAR NOT NULL UNIQUE,              -- NK: source `incnum`
    incident_dt                 DATE,                                 -- NULL for sensitive incidents
    incident_year               SMALLINT NOT NULL,
    incident_year_only          BOOLEAN NOT NULL,                     -- TRUE = day-and-month stripped at source
    police_shift                VARCHAR,                              -- NULL for sensitive incidents
    offense_code                VARCHAR NOT NULL REFERENCES gold.dim_offense_code(offense_code),
    multi_offense_flag          BOOLEAN NOT NULL,
    offense                     VARCHAR,                              -- denormalized from dim_offense_code
    offense_type                VARCHAR,                              -- denormalized from dim_offense_code
    offense_category            VARCHAR NOT NULL REFERENCES gold.dim_offense_category(offense_category),
    ward                        VARCHAR,                              -- 1–7 (FK to dim_ward) / NULL / 'CAM'
    block_code                  VARCHAR,                              -- 15-char census block; NULL for sensitive

    -- audit columns (passthrough from bronze)
    _extracted_at               TIMESTAMP,
    _extracted_run_id           VARCHAR,
    _first_seen_at              TIMESTAMP,
    _source_endpoint            VARCHAR
);

-- One row per 311 request. Grain: one request.
-- Location fields (ward, block_code) are denormalized here for MVP 1.
-- dim_location will be introduced in MVP 3.
-- Dept tag columns cast from VARCHAR '0'/'1' to BOOLEAN.
-- Survey columns kept as VARCHAR — sparse, free-text responses.
CREATE TABLE IF NOT EXISTS gold.fct_311_requests (
    request_sk                  INTEGER PRIMARY KEY,
    request_id                  VARCHAR NOT NULL,         -- NK: source id
    date_created_sk             INTEGER REFERENCES gold.dim_date(date_sk),
    request_type_sk             INTEGER REFERENCES gold.dim_request_type(request_type_sk),
    status_sk                   INTEGER REFERENCES gold.dim_status(status_sk),
    origin_sk                   INTEGER REFERENCES gold.dim_origin(origin_sk),

    -- Timestamps (full precision retained)
    date_created_dt             TIMESTAMPTZ,
    most_recent_status_date_dt  TIMESTAMPTZ,

    -- Derived measures
    days_open                   INTEGER,                  -- most_recent_status_date - date_created

    -- Convenience copy of status (avoids join for simple filters)
    is_open                     BOOLEAN,

    -- Location (denormalized — no dim_location until MVP 3)
    ward                        INTEGER,                  -- cast from VARCHAR; NULL when unknown
    block_code                  VARCHAR,                  -- TRIM() applied; NULL when unknown

    -- Survey responses (sparse — NULL when not submitted)
    survey_accuracy             VARCHAR,
    survey_courtesy             VARCHAR,
    survey_ease                 VARCHAR,
    survey_overall              VARCHAR,                  -- renamed from overallexperience

    -- Department tags (cast from VARCHAR '0'/'1' to BOOLEAN; NULL → FALSE)
    dept_emergency_readiness    BOOLEAN,
    dept_green_space            BOOLEAN,
    dept_infrastructure         BOOLEAN,
    dept_noise                  BOOLEAN,
    dept_reliable_service       BOOLEAN,
    dept_navigating_services    BOOLEAN,
    dept_public_space           BOOLEAN,
    dept_voting                 BOOLEAN
);


-- One row per (Somerville traffic citation, violation) (Socrata `3mqx-eye9`).
-- 67,311 rows covering 2017-01-01 to 2026-03-27; daily refresh.
-- Source publishes ward with 0.12% NULL — spatial join not used.
-- See limitations: traffic-citations-location-and-violation-only,
-- citations-composite-grain-violation-suffix.
CREATE TABLE IF NOT EXISTS gold.fct_citations (
    citation_id                 VARCHAR PRIMARY KEY,                  -- md5(citation_number)
    citation_number             VARCHAR NOT NULL UNIQUE,              -- NK: source `citationnum`, includes suffix
    citation_ts                 TIMESTAMPTZ NOT NULL,                 -- source `dtissued`
    citation_date               DATE,                                 -- DATE(citation_ts)
    citation_year               SMALLINT,
    police_shift                VARCHAR,                              -- same vocabulary as crime
    charge_code                 VARCHAR,                              -- source `chgcode` (MGL reference)
    charge_description          VARCHAR,
    charge_category             VARCHAR,                              -- source `chgcategory` (109 distinct)
    vehicle_mph                 INTEGER,                              -- 82.5% NULL; speed-violation only
    posted_mph_zone             INTEGER,
    latitude                    DOUBLE,
    longitude                   DOUBLE,
    ward                        VARCHAR,                              -- 1-7 (FK to dim_ward); 84 rows NULL
    block_code                  VARCHAR,
    address                     VARCHAR,
    warning_flag                VARCHAR,                              -- 'Y' or 'N'
    is_warning                  BOOLEAN,                              -- derived: warning_flag = 'Y'

    -- audit columns (passthrough from bronze)
    _extracted_at               TIMESTAMP,
    _extracted_run_id           VARCHAR,
    _source_endpoint            VARCHAR
);


-- One row per Somerville building / inspection permit (Socrata `vxgw-vmky`).
-- 64,521 rows covering 2014-02-13 to 2023-10-24. Source stopped refreshing
-- 2023-05-16 -- treat as historical, not ongoing. Ward derived via spatial
-- point-in-polygon join (longitude, latitude) against dim_ward; 96.62%
-- match rate, remaining 3.37% have NULL ward.
-- See limitations: permits-static-since-2023, permits-spatial-ward-derivation.
CREATE TABLE IF NOT EXISTS gold.fct_permits (
    permit_id                   VARCHAR PRIMARY KEY,                  -- md5(permit_number)
    permit_number               VARCHAR NOT NULL UNIQUE,              -- NK: source `id`, year-prefixed (e.g. "B14-001277")
    application_date            DATE NOT NULL,
    issue_date                  DATE,                                 -- NULL for non-issued applications
    application_year            SMALLINT,
    issue_year                  SMALLINT,                             -- NULL when issue_date is NULL
    permit_type                 VARCHAR,                              -- 11 rows NULL (source DQ)
    permit_status               VARCHAR,                              -- ~97% 'Issued'; some date-as-status anomalies
    is_issued                   BOOLEAN,                              -- derived: permit_status = 'Issued'
    permit_amount               DOUBLE,                               -- fee in USD
    address                     VARCHAR,                              -- public for permits
    work_description            VARCHAR,                              -- freeform; no PII observed
    ward                        VARCHAR,                              -- 1-7 (FK to dim_ward) / NULL for outside-Somerville
    latitude                    DOUBLE,
    longitude                   DOUBLE,

    -- audit columns (passthrough from bronze)
    _extracted_at               TIMESTAMP,
    _extracted_run_id           VARCHAR,
    _source_endpoint            VARCHAR
);


-- =============================================================
-- ADMIN — infrastructure: profiling and data quality
-- =============================================================

CREATE SCHEMA IF NOT EXISTS admin;

-- Column-level profiling snapshots.
-- Observational only — does NOT generate rows in fct_test_run.
-- Appended on every pipeline run. Query max(profiled_at) for current state.
CREATE TABLE IF NOT EXISTS admin.fct_data_profile (
    profiled_at     TIMESTAMPTZ NOT NULL,   -- when the profile was run
    table_name      VARCHAR NOT NULL,
    column_name     VARCHAR NOT NULL,
    row_count       INTEGER,                -- total rows in the table at time of profile
    null_count      INTEGER,
    pct_null        FLOAT,                  -- null_count / row_count
    distinct_count  INTEGER,
    pct_distinct    FLOAT,                  -- distinct_count / row_count
    min_value       VARCHAR,                -- all types cast to varchar for uniform schema
    max_value       VARCHAR,
    min_length      INTEGER,                -- shortest string length (chars)
    max_length      INTEGER,
    avg_length      FLOAT
);

-- One row per defined test.
-- Covers baseline comparisons and dbt tests only — not profiling.
-- test_type: 'baseline' | 'dbt_generic' | 'dbt_singular'
-- For dbt tests, expected_value = '0' (zero failures expected).
-- Baselines auto-generated on first run with certified_by = 'system'.
-- Promote to certified_by = 'gordon' to manually certify a baseline.
CREATE TABLE IF NOT EXISTS admin.dim_data_quality_test (
    test_sk         INTEGER PRIMARY KEY,
    test_id         VARCHAR NOT NULL UNIQUE, -- natural key e.g. baseline.raw_311_requests.year_2016.row_count
    test_type       VARCHAR NOT NULL,        -- baseline | dbt_generic | dbt_singular
    table_name      VARCHAR NOT NULL,
    column_name     VARCHAR,                 -- NULL for table-level tests
    metric          VARCHAR NOT NULL,        -- row_count | pct_null | unique | not_null | etc.
    grain           VARCHAR NOT NULL,        -- e.g. year=2016 | all
    expected_value  VARCHAR NOT NULL,        -- certified known-good value
    tolerance_pct   FLOAT NOT NULL DEFAULT 0.0, -- acceptable drift before fail e.g. 0.01 = 1%
    is_active       BOOLEAN NOT NULL DEFAULT TRUE, -- soft-delete: deactivate without losing history
    certified_at    TIMESTAMPTZ NOT NULL,
    certified_by    VARCHAR NOT NULL         -- 'system' or 'gordon'
);

-- One row per test per dbt run.
-- Sources from both baseline comparisons and parsed dbt test results.
-- status: 'pass' | 'fail' | 'warn'
CREATE TABLE IF NOT EXISTS admin.fct_test_run (
    test_run_sk     INTEGER PRIMARY KEY,
    test_sk         INTEGER REFERENCES admin.dim_data_quality_test(test_sk),
    run_id          VARCHAR NOT NULL,        -- dbt invocation id
    run_at          TIMESTAMPTZ NOT NULL,
    actual_value    VARCHAR,                 -- what the data showed
    expected_value  VARCHAR,                 -- copied from dim_data_quality_test at time of run
    variance_pct    FLOAT,                   -- (actual - expected) / expected
    status          VARCHAR NOT NULL,        -- pass | fail | warn
    failure_message VARCHAR                  -- human-readable explanation on fail; NULL on pass
);
