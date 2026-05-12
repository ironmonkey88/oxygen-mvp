{{ config(materialized='view', schema='bronze') }}

-- Bronze: exact mirror of Somerville 311 SODA API.
-- Source data is owned by dlt (`main_bronze.raw_311_requests_raw`) since
-- Plan 1a (2026-05-12); this view passes columns through and casts the
-- date strings to VARCHAR for downstream layers per docs/schema.sql.
-- All audit/lineage columns retained.
select
    id,
    classification,
    category,
    type,
    origin_of_request,
    date_created::VARCHAR                              as date_created,
    most_recent_status,
    most_recent_status_date::VARCHAR                   as most_recent_status_date,
    block_code,
    ward,
    accuracy,
    courtesy,
    ease,
    overallexperience,
    emergency_readiness_and_response_planning,
    green_space_care_and_maintenance,
    infrastructure_maintenance_and_repairs,
    noise_and_activity_disturbances,
    reliable_service_delivery,
    navigating_city_services_and_policies,
    public_space_cleanliness_and_environmental_health,
    voting_and_election_information,
    _extracted_at,
    _extracted_run_id,
    _first_seen_at,
    _source_endpoint,
    _dlt_load_id,
    _dlt_id
from {{ source('bronze_raw', 'raw_311_requests_raw') }}
