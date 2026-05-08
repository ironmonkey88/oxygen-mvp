{{ config(materialized='table', schema='gold') }}

-- One row per Somerville 311 request.
-- Location denormalized: bronze only carries `ward` and `block_code` (no
-- neighborhood/lat/long/address columns exist). dim_location deferred to MVP 3.
-- PII redaction is MVP 3 scope and not applied here.
-- Dept tag columns: bronze stores '0'/'1'/NULL strings; try_cast → boolean preserves NULL.
select
    id,
    classification,
    category,
    type                                                                  as request_type,
    md5(type)                                                             as request_type_id,
    most_recent_status                                                    as status,
    md5(most_recent_status)                                               as status_id,
    origin_of_request                                                     as origin,
    cast(date_created::timestamp as date)                                 as date_created_dt,
    date_created::timestamp                                               as date_created_ts,
    cast(most_recent_status_date::timestamp as date)                      as most_recent_status_dt,
    most_recent_status_date::timestamp                                    as most_recent_status_ts,
    ward,
    block_code,
    accuracy,
    courtesy,
    ease,
    overallexperience,
    try_cast(emergency_readiness_and_response_planning      as boolean) as is_emergency_readiness_tag,
    try_cast(green_space_care_and_maintenance               as boolean) as is_green_space_tag,
    try_cast(infrastructure_maintenance_and_repairs         as boolean) as is_infrastructure_tag,
    try_cast(noise_and_activity_disturbances                as boolean) as is_noise_tag,
    try_cast(reliable_service_delivery                      as boolean) as is_reliable_service_tag,
    try_cast(navigating_city_services_and_policies          as boolean) as is_city_services_tag,
    try_cast(public_space_cleanliness_and_environmental_health as boolean) as is_public_space_tag,
    try_cast(voting_and_election_information                as boolean) as is_voting_tag
from {{ ref('raw_311_requests') }}
