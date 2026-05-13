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

**For ward-level geography**, the project now ships `main_gold.dim_ward`
(Plan 12 Phase 2, 2026-05-13) — 7 administrative wards with polygon
geometry in WGS84 WKT, area in sq km, and perimeter in meters. The
Airlayer auto-join via the `ward` foreign entity on `requests` brings
ward geometry into any ward-keyed query. This **does not** add per-row
lat/lng to 311; it only enriches the ward dimension.

## Resolution path

Planned for MVP 3 — `gold/dim_location.sql` will surface a richer
location dim sourced from the Somerville open-data parcel layer (or
the `n5md-vqta` neighborhoods blob). Until then, queries are bounded
to ward + block, with the ward polygons available via `dim_ward`.
