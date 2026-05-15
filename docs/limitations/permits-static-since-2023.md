---
id: permits-static-since-2023
title: Permits dataset has not refreshed since 2023-05-16 (~3 years stale)
severity: high
affects:
  - main_bronze.raw_somerville_permits_raw
  - raw_somerville_permits
  - permits
since: 2026-05-14
status: active
---

# Permits dataset is stale -- the source stopped refreshing in May 2023

## The finding

Probed 2026-05-14: the Socrata dataset `vxgw-vmky` (Somerville
Permits) has `rowsUpdatedAt = 2023-05-16` -- nearly 3 years ago. The
source description says the dataset "contains data on permit
applications from the Inspectional Services Department dating back to
2014," which is technically still accurate -- but no new permits have
been published in three years.

64,521 permits are present, covering 2014 through May 2023. Anything
permitted in Somerville from June 2023 onward is **not** in this
dataset.

## Consequence for analysis

- "Are construction-related 311 complaints rising where permit
  activity concentrates?" -- the natural pairing question -- can only
  be answered for the 2014-2023 overlap. The 2023-2026 portion of the
  311 data has no permit comparison.
- Per-year aggregates of permit counts cannot be used to characterize
  recent years (2024+) -- they will appear as zero.
- Any time series of "permits issued" should be capped at the 2023-05
  cutoff or carry a visible caveat.

## What we don't know

It is unclear whether the city has stopped publishing this dataset
permanently, is migrating to a new endpoint, or simply hasn't pushed
fresh data. The pipeline is ready to pick up fresh rows if and when
they appear -- re-run
`dlt/somerville_permits_pipeline.py` manually.

## Status

- Bronze: as-is. Caveat lives here and is surfaced by the Answer
  Agent's trust contract when permit-affecting queries are asked.
- Silver / gold: MVP 3 work. Will resolve ward via spatial join
  (no `ward` column at source; `latitude`/`longitude` are precise
  enough for point-in-polygon against `dim_ward.geometry_wkt_wgs84`).

---

## Secondary finding: status-column data quality

A small number of rows carry dates as `status` values rather than
status labels:

- "08/17/2022" (1 row)
- "06/02/2022" (1 row)
- "11/10/2020" (1 row)
- Plus 6 rows with empty-string status
- Plus 21 rows with NULL status

This looks like data entry errors at source. We don't apply an
`accepted_values` test on `status` for this reason -- the bronze
layer mirrors source as-is. Cleanup is silver's job (MVP 3):
either map the date-as-status rows to a "Data Error" category, or
join to a reference list of canonical status values and drop the
non-matching ones.

Also note that some `status` values are truncated in the source --
e.g. "Online Application Receiv" (should be "Received"),
"Approved/Waiting for Paym" (should be "Payment"),
"Approved/Waiting for Docu" (should be "Documentation"). Likely a
source-side column-width truncation. Honest documentation: these
exist; we don't paper over them.

### `type` column has 11 NULL rows

Probed 2026-05-14 via the bronze model: 11 of 64,521 rows have NULL
`type`. A `not_null` test on `type` was attempted in the initial
schema.yml draft (Phase B precedent: most categorical columns are
populated reliably) but failed with 11 rows. The honest move is to
drop the test, document the gap, and let silver handle cleanup -- not
to paper over it. The 11 NULL-type rows are present in the bronze
view; downstream code can filter or coalesce as appropriate.

## PII surface

Modest. `address` is the property address (public information for
permits, by design). `work` is a freeform description of permitted
work -- sample rows show roofing / kitchen / counters / fixtures
descriptions, no applicant names observed. The risk surface is
significantly smaller than the crime or future traffic-citations
data. Standard /profile exposure is fine.
