---
id: dept-tags-as-booleans
title: Department tags are flat boolean columns on the fact, not a dim
severity: info
affects:
  - is_emergency_readiness_tag
  - is_green_space_tag
  - is_infrastructure_tag
  - is_noise_tag
  - is_reliable_service_tag
  - is_city_services_tag
  - is_public_space_tag
  - is_voting_tag
since: 2026-05-07
status: active
---

# Department tags are flat boolean columns on the fact

`main_gold.fct_311_requests` carries 8 boolean department-tag columns
(`is_emergency_readiness_tag`, `is_green_space_tag`,
`is_infrastructure_tag`, `is_noise_tag`, `is_reliable_service_tag`,
`is_city_services_tag`, `is_public_space_tag`, `is_voting_tag`). Tags
are not normalized into a `dim_department`; a single request can carry
multiple tags simultaneously.

## Impact

- Cannot easily ask "which department fielded the most requests" — that
  question is ambiguous when a single request carries multiple tags.
- Tag coverage is sparse: only 987 of 1,169,935 rows (~0.08%) carry any
  tag (verified 2026-05-10). Tag-based aggregations cover a tiny minority
  of requests.
- Adding a new department requires a schema change to the fact table.

## Workaround

For "tag is set" filters, query the boolean directly
(`WHERE is_noise_tag = true`). For "any tag set" queries, OR all eight
booleans together. For analyst-level questions about department, frame
results as "of the 0.08% of requests that carry a tag…" rather than
"of all requests."

## Resolution path

A normalized `dim_department` and a `bridge_request_department` table
could land in MVP 3, but the upstream feed's tag sparsity makes this a
low priority.
