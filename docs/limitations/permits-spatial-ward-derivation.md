---
id: permits-spatial-ward-derivation
title: 3.4% of permits have NULL ward — geocoded outside the Somerville polygon set
severity: warning
affects:
  - main_gold.fct_permits
  - ward
since: 2026-05-15
status: active
---

# 3.4% of permits have NULL ward — geocoded outside the Somerville polygon set

## The finding

The source dataset (Socrata `vxgw-vmky`) has no `ward` column. Gold
derives `ward` via point-in-polygon spatial join of (longitude,
latitude) against `dim_ward.geometry_wkt_wgs84` (WGS84 WKT, sourced
from Socrata `ym5n-phxd`).

Pre-flight 2026-05-15 result:

- **64,521 total permits.**
- **64,513 with latitude+longitude** (99.99%). 8 rows are missing both.
- **62,337 matched to a ward polygon** (96.62% of total / 96.63% of
  with-latlng).
- **2,176 rows (3.37%) have lat+lng but fall outside the 7 ward
  polygons.** These get NULL ward.

The 90% halt threshold (set in the Phase A pre-flight contract) is
comfortably cleared. Match rate is in the same range as the
crime-ward-coverage-gaps posture (~87% match for crime).

## Why some permits fall outside

Three plausible reasons (not separately quantified):

- **Boundary geocoding precision.** Permits issued for properties on
  the Somerville–Cambridge or Somerville–Medford line may geocode to
  coordinates marginally outside the ward polygons. Same physics that
  produces crime's 2 `'CAM'` rows.
- **Out-of-Somerville geocoding errors.** Source-side geocoders
  sometimes produce coordinates in adjacent municipalities, especially
  for addresses on shared streets (Mass Ave, Highland Ave, etc.).
- **Source data anomalies.** A handful of permits may carry
  coordinates that have nothing to do with the property (defaulted to
  a city-hall location, swapped lat/lng, etc.). Not separately audited.

Per-ward distribution post-join (pre-flight 5):

| ward | row_count |
|---|---|
| 5 | 10,770 |
| 6 | 10,437 |
| 3 | 9,417 |
| 1 | 8,985 |
| 2 | 8,461 |
| 7 | 7,182 |
| 4 | 7,085 |
| UNMATCHED | 2,176 |

All 7 wards have plausibly proportional volumes (~7K-11K). The
UNMATCHED bucket isn't concentrated in any ward.

## Impact

- **Ward-aggregated permit queries are systematically incomplete by
  ~3.4%.** Same posture as crime's ~13% NULL ward, but smaller surface.
- **Cross-topic comparisons amplify.** Comparing permits-by-ward to
  311-by-ward (where 311 has its own NULL-ward limitation) or to
  crime-by-ward (~13% NULL) compounds the gap.
- **No `ward = 'CAM'` analogue.** Unlike crime, the permits dataset
  doesn't tag cross-jurisdiction rows separately — the 2,176 UNMATCHED
  rows are all NULL, undifferentiated.

## Workaround

- **Use `permit_count` for total volume; filter `WHERE ward IS NOT
  NULL` when ward attribution matters.** The measure surface in
  `semantics/views/permits.view.yml` is built so the agent can
  surface this distinction.
- **The `relationships` test on `ward → dim_ward.ward` carves out
  `WHERE ward IS NOT NULL`** so the gap doesn't trip the test.

## Resolution path

Source-side. Two possible improvements:

- The city could publish the permits dataset with a `ward` column
  derived against the same shapefile used for `dim_ward` (would
  eliminate the geocoding-precision issue).
- A silver layer could attempt a "nearest ward within X meters"
  fallback for the 2,176 UNMATCHED rows, but that introduces
  attribution decisions (a permit 200m outside the polygon isn't
  obviously "in" any ward) and is out of scope for MVP 2 gold. MVP 3
  silver work, if pursued.
