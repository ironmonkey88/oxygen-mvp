---
id: location-ward-block-only
title: Gold location dimensions are ward and block_code only
severity: warning
affects:
  - ward
  - block_code
since: 2026-05-07
status: active
---

# Gold location dimensions are ward and block_code only

The gold fact `main_gold.fct_311_requests` exposes only two location
dimensions: `ward` (Somerville ward number) and `block_code` (census block
code). The Somerville 311 source feed does not publish neighborhood,
latitude/longitude, or street address fields suitable for joinable
geographic analysis, so none of those are surfaced.

## Impact

- Geographic queries cannot answer "which neighborhood" or "which
  intersection" — only "which ward" or "which block."
- Distance/proximity analysis is not possible at the request level.
- Ward + block_code together are sufficient for political-geography
  rollups but coarse for service-delivery analysis.

## Workaround

For neighborhood-level analysis, the analyst would need to join an
external ward-to-neighborhood mapping (none is shipped with this MVP).
Block-level analysis works directly off `block_code` once the
`block-code-padded` limitation is also handled.

## Resolution path

Planned for MVP 3 — `gold/dim_location.sql` will surface a richer
location dim sourced from the Somerville open-data parcel layer. Until
then, queries are bounded to ward + block.
