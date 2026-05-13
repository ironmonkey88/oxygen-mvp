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

`./run.sh manual` ran end-to-end with the new stage 1b included.

**First attempt — `01KRGVJQ26GQXNFNRT4FA0ZHW4`, 916s** — FAILED at
stage 9d/10 (`profile_page`) with `cp: cannot create regular file
'/var/www/somerville/profile.html': Permission denied`. Root cause:
a `sudo cp` from this session's earlier manual portal regen had
flipped the file ownership to root; run.sh runs as `ubuntu` and uses
plain `cp` (no sudo) on portal-deploy stages. The new crime stage 1b
ran clean — the failure was downstream and unrelated to Phase 3.
Today's earlier daily run at 10:00 UTC (`01KRGCF7Y18QZCXX1X2NK65ZT9`)
failed at the same stage for the same reason; the pre-existing
daily-runs-landing-`partial` pattern (Session 31) flipped to `failed`
today.

**Fix** — `sudo chown ubuntu:ubuntu /var/www/somerville/profile.html
erd.html erd-warehouse.mmd erd-semantic-layer.mmd`. Documented in
`docs/limitations/portal-deploy-file-ownership.md`; durable fix
(sudo cp vs setgid vs systemd-as-root) is a follow-up plan.

**Second attempt — `01KRGWG8N51MHZX09SX4Z61J6G`, 833s** — landed
clean past stage 9d. Final status: `partial` (final exit 1 from the
pre-existing `dq_drift_fail_guardrail` Session-31 carry-forward; all
other stages green).

- Stages 0–10 all executed
- Stage 1 (dlt 311): 1,171,107 rows fetched, ~9 min load
- Stage 1b (dlt crime, NEW): 22,325 rows in 7.94 s
- Stage 2 (dbt run bronze + gold): 8/8 OK
- Stage 3 (dbt test bronze + gold): 27/27 PASS — including the new
  wards (3) + crime (2) tests
- Stage 5 (dbt run admin): 3/3 OK
- Stage 5b (dbt test admin): 12/13 PASS, 1 ERROR (drift-fail, expected
  carry-forward)
- Stages 6–10: dbt docs + /metrics (3 measures × 5 views) + /trust
  (44 tests) + limitations index (14 entries — incl. new
  portal-deploy-file-ownership) + /profile (112 cols) + /erd (11
  models, 5 semantic views) all clean

Crime bronze fully integrated end-to-end. Plan 12 verified.

## Next action

None on this branch — Plan 12 closed. Plan 11 execution still pending
Gordon's review of the scoping document.
