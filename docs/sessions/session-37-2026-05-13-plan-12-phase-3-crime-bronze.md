---
session: 37
date: 2026-05-13
start_time: 02:00 ET
end_time: 02:35 ET
type: code
plan: plan-12
layers: [ingestion, bronze, docs, infra]
work: [feature, docs]
status: complete
---

## Goal

Execute Plan 12 Phase 3 — ingest Somerville Police crime reports
(Socrata `aghs-hqvg`) into bronze, parallel to 311. Bronze only —
silver/gold/semantic deferred to MVP 3 alongside PII review. Document
the PII surface honestly in a limitations entry. Decide on refresh
cadence and wire to `./run.sh` if appropriate.

## What shipped

- [`dlt/somerville_crime_pipeline.py`](../../dlt/somerville_crime_pipeline.py)
  — adapted from `dlt/somerville_311_pipeline.py`. Full pull + merge
  on `incnum`; same audit-column + `_first_seen_at` pattern; same
  DuckDB destination. 22,325 rows in 7.94 s.
- `main_bronze.raw_somerville_crime_raw` on EC2 (dlt-owned merge
  target). 11 source columns + 6 metadata columns (`_extracted_at`,
  `_extracted_run_id`, `_first_seen_at`, `_source_endpoint`,
  `_dlt_load_id`, `_dlt_id`).
- [`dbt/models/bronze/raw_somerville_crime.sql`](../../dbt/models/bronze/raw_somerville_crime.sql)
  — passthrough view; 11 source columns + audit. dbt run + test 1/1
  OK + 2/2 PASS (not_null + unique on `incnum`).
- [`dbt/models/bronze/schema.yml`](../../dbt/models/bronze/schema.yml)
  extended with source description + per-column descriptions for the
  new model. Ward column flagged as space-padded to length 15 (matches
  Session 28's block-code-padded family of source quirks).
- [`docs/limitations/crime-data-pii-unredacted-in-bronze.md`](../limitations/crime-data-pii-unredacted-in-bronze.md)
  — honest PII audit. Findings: no names / addresses / phone /
  email / DOB; `incdesc` is generic NIBRS legal definitions
  (0 rows containing `@` or phone-pattern); source-level redaction
  already strips time + location from sensitive incidents. Gating
  rationale: even already-redacted crime data warrants intentional
  thinking before public surfacing; bronze stays gated until silver
  review at MVP 3. Limitations index regenerated → 13 active entries
  (was 12).
- [`docs/schema.sql`](../schema.sql) — DDL for
  `bronze.raw_somerville_crime_raw` added.
- [`run.sh`](../../run.sh) — new stage `1b/10` dlt ingest crime,
  between stage 1 (dlt 311) and stage 2 (dbt run). 22K rows / ~8s adds
  trivially to the daily refresh. Header comment block updated.
- Portal `/profile` regenerated — 112 columns across 11 models (was 95
  / 10 after Phase 2); `/erd` regenerated — 11 models; `/trust`
  regenerated — surfaces the new limitation entry through the
  Answer Agent's trust contract.

## Pre-flight findings (committed to the session via decisions below)

- **22,325 rows, 2017–2026, daily-with-1-month-delay refresh
  cadence per source description.** Tiny vs 311's 1.17M; full pull
  takes ~8 s; daily fits.
- **Source-level PII redaction is real.** Sensitive incidents have
  time + location stripped (only year reported). `incdesc` rows are
  100% generic NIBRS legal definitions (no narrative). 0 rows
  containing `@` or phone-shaped patterns.
- **Ward column is space-padded to length 15 in source** — same
  pattern as 311's `block_code` padding. Documented in the bronze
  schema.yml + the new limitation entry. Trim required at any
  `ward`-keyed join to `dim_ward`. Silver-layer work.
- **Per-ward distribution** matches 311's: wards 1+2 highest volume,
  wards 5+7 lowest. ~13% rows have NULL ward.

## Decisions

- **Daily refresh on `./run.sh`, not a separate systemd timer.**
  Source updates daily; 22K-row pull adds ~8 s. Same cadence as 311
  keeps the timer surface simple. The opportunistic principle's
  analyst-experience-leads test: an analyst doesn't care about timer
  topology, they care about whether the data is current. Daily on
  the shared timer ties for "current" with a separate weekly timer
  and wins on operational simplicity.
- **Bronze only — no silver / gold / semantic / fct_crime yet.**
  Defers project-side PII review + ward+blockcode transform decisions
  to a daytime session. Plan 12 Phase 3 is scoped to bronze.
- **PII risk is real but low.** No names / addresses / phone /
  email / DOB. The `incdesc` column is NIBRS standard text. The only
  meaningful re-identification surface is `incnum` (case ID,
  cross-referenceable with other police records) and
  `blockcode + offense + date` for rare offenses in small blocks.
  Limitation entry is precise about what's at risk rather than
  catastrophizing.
- **`/profile` is allowed to include the crime bronze view.** What
  /profile surfaces (distinct counts, null %, top-5 values of
  `incdesc` — which are public NIBRS legal definitions) does not
  expose PII. The gating in the limitation entry applies to row-level
  public consumption, not to column-shape metadata.

## Issues encountered

- None during ingestion. Pipeline ran clean first attempt.

## End-to-end verification

`./run.sh manual` ran end-to-end with the new stage 1b included. Final
status + exit code captured in the session note appendix below if
the run completed in time; otherwise this section is updated on next
session.

## Next action

Plan 12 close — write the close session note, update LOG.md Plans
Registry to `done`, push final commit. Plan 11 review still pending
Gordon's review; not blocked.
