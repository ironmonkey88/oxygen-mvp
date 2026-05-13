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
