{{ config(materialized='view', schema='bronze') }}

-- Bronze: exact mirror of Somerville 311 SODA API.
-- All source columns kept as VARCHAR per docs/schema.sql.
-- _dlt_load_id and _dlt_id retained for lineage/debugging.
-- union_by_name=true: older Parquet files are missing the survey/dept columns.
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
    _dlt_load_id,
    _dlt_id
from read_parquet(
    '/home/ubuntu/oxygen-mvp/data/raw/somerville_311/**/*.parquet',
    union_by_name=true
)
