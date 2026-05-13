---
id: crime-ward-coverage-gaps
title: 13% of crime incidents have no ward — and 2 are cross-jurisdiction
severity: warning
affects:
  - main_gold.fct_crime_incidents
  - ward
since: 2026-05-13
status: active
---

# 13% of crime incidents have no ward — and 2 are cross-jurisdiction

In `main_gold.fct_crime_incidents`:

- **2,911 rows (13.0%) have NULL ward.** Not a parse failure — the
  source publishes them without ward assignment. Possible reasons
  (unverified): out-of-Somerville jurisdiction handled by SPD,
  reporting errors, or pre-NIBRS records missing the field.
- **2 rows have `ward = 'CAM'`** — apparent Cambridge cross-
  jurisdiction incidents on the Somerville blotter. Likely reflect
  incidents on the Somerville–Cambridge boundary that SPD recorded.
  Kept on the fact (not dropped); the `dim_ward` relationships test
  carves them out with `WHERE ward IS NOT NULL AND ward <> 'CAM'`.

## Impact

- **Ward-aggregated crime queries are systematically incomplete by
  13%.** A "crimes by ward" answer covers ~87% of the full dataset.
- **The undercount overlaps with sensitive-incident redaction.** Of
  the 2,911 NULL-ward rows, 2,413 also have `incident_year_only` = TRUE
  (they're in the source-redacted set with day-and-month and block
  also stripped). The remaining 498 NULL-ward rows have full
  day-and-month but somehow missed ward assignment — a smaller
  reporting gap unrelated to victim privacy.
- **Cross-topic comparisons amplify the issue.** When comparing
  crime-by-ward to 311-by-ward, the 311 fact has its own
  `location-ward-block-only` limitation (no neighborhood, no
  lat/lng) and ~38% of 311 rows have NULL ward. The two limitations
  surface together on any comparison query.

## Workaround

- **Use `incidents_with_ward` measure** (defined in
  `semantics/views/crime.view.yml`) — `COUNT(ward)` — for ward-only
  analysis. Excludes both NULL and CAM rows automatically.
- **Compare measures explicitly.** `total_incidents` is 22,325;
  `incidents_with_ward` is 19,412. The gap is the limitation
  surface.
- **Don't try to remap CAM rows.** Keep them visible; the data is
  what it is.

## Resolution path

Source-side. If the Somerville Police publish a backfill or a
revised ward-assignment dataset, the gap would close. The MVP 3
silver layer may add a `ward_assignment_method` column distinguishing
"source-assigned" from "absent-at-source" if the source ever
distinguishes these, but the underlying NULLs aren't fixable
downstream.
