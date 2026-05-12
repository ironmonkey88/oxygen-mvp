---
id: source-bulk-republish-no-per-row-modified
title: Source publishes the dataset in bulk; there is no per-row modified field
severity: info
affects:
  - requests
  - pipeline.refresh
since: 2026-05-12
status: active
---

# Source publishes the dataset in bulk; there is no per-row modified field

The Somerville 311 SODA dataset at
`https://data.somervillema.gov/resource/4pyi-uqq6.json` exposes 23 columns
(the business `id` plus 22 data fields). **None** of them is a
publisher-maintained "last modified" timestamp. The dataset metadata
endpoint reports a single `rowsUpdatedAt` value that advances when Socrata
republishes the dataset as a whole — every row's Socrata system field
`:updated_at` matches that single republish timestamp.

Verified at pre-flight 2026-05-12: `rowsUpdatedAt` was 2026-05-07 11:09 UTC
across the entire dataset (1.17M rows); a 2018 record's `:updated_at`
equalled the dataset-level republish timestamp, not its own row creation
time.

## Impact

- We cannot do "incremental by row-modified" extraction. There is no
  reliable per-row signal that tells us a record changed.
- The dataset is published as a periodic full snapshot, not as an
  append-only event stream.

## Workaround

The pipeline does a **full pull on every run** and merges on `id`. New
records `INSERT`, existing records `UPDATE` with the latest content. The
audit column `_first_seen_at` is preserved across re-extractions so each
row carries its true first-seen-by-us timestamp. The
`_extracted_at` audit column advances on every run.

Source freshness is observable two ways:

- `main_admin.fct_source_health_raw.source_rows_updated_at` records the
  source's `rowsUpdatedAt` at each hourly check; analysts see this on
  `/trust`.
- `main_admin.fct_pipeline_run_raw.source_rows_updated_at` records the
  same value at pipeline-run time.

If `source_rows_updated_at` does not advance run-over-run, the source
hasn't been republished — a source-side condition, not a pipeline issue.

## Resolution path

None planned. This is a property of the upstream feed, not a flaw on
our side. The full-pull design is correct for this source.
