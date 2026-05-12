---
id: audit-columns-non-analytics
title: Underscore-prefixed columns are pipeline metadata, not analytical fields
severity: info
affects:
  - _extracted_at
  - _extracted_run_id
  - _first_seen_at
  - _source_endpoint
  - _dlt_load_id
  - _dlt_id
since: 2026-05-12
status: active
---

# Underscore-prefixed columns are pipeline metadata, not analytical fields

Every bronze row carries six pipeline-metadata columns, all prefixed with
a single underscore. They describe the pipeline's relationship to the
row — when we extracted it, which run produced it, when we first saw it —
**not** anything about the underlying 311 service request.

| Column | Meaning |
|---|---|
| `_extracted_at` | UTC timestamp when this run extracted the row. Advances on every refetch. |
| `_extracted_run_id` | ULID of the pipeline run that produced this row's current state. Joins to `main_admin.fct_pipeline_run_raw.run_id`. |
| `_first_seen_at` | UTC timestamp when our pipeline first ingested this record. Preserved across subsequent re-extractions. |
| `_source_endpoint` | SODA URL the row came from. Static for this project. |
| `_dlt_load_id` | dlt's internal load identifier. |
| `_dlt_id` | dlt's internal row-level identifier. |

## Impact

If the agent ever cites one of these columns in an analytical answer
(e.g. "the most recent request was extracted on..."), that's a bug —
the analyst is asking about the **city's** 311 system, not our
pipeline's behavior.

Specifically:

- "When was this case opened?" — use `date_created` (gold:
  `opened_dt` / `date_created_dt`), **not** `_extracted_at` or
  `_first_seen_at`.
- "When was this case last updated by the city?" — use
  `most_recent_status_date` (gold: `most_recent_status_dt`), **not**
  `_extracted_at`. Note that the source publishes the dataset in bulk
  with no per-row modified field (see
  [`source-bulk-republish-no-per-row-modified`](source-bulk-republish-no-per-row-modified.md)).
- Run-level questions ("when did the pipeline last refresh?", "are
  any rows stale?") belong on `/trust`, driven by
  `main_admin.fct_pipeline_run_raw`, not by the underscore columns.

## Workaround

None needed. These columns are documented in
`dbt/models/bronze/schema.yml` with explicit `**PIPELINE METADATA — not
for analysis.**` markers in their descriptions. The Answer Agent's
system instructions plus the limitations index keep them out of
analytical answers.

## Resolution path

By design. Pipeline observability columns are intentionally separated
from analytical fields and named to advertise the distinction.
