---
session: 29
date: 2026-05-12
start_time: 23:30 ET
type: code
plan: plan-1a
layers: [ingestion, bronze, admin, infra, docs]
work: [feature, infra, docs]
status: complete
---

## Goal

Execute Plan 1a (Daily Incremental Refresh + Observability) — switch pipeline to merge-on-id, add audit columns, add Python-owned run + source observability tables, wire systemd timers, replace the watermark+lookback design with full-pull after pre-flight finding.

## What shipped

- `dlt/somerville_311_pipeline.py` — destination flipped from filesystem-Parquet (year-partitioned, `replace`) to `dlt.destinations.duckdb` with `write_disposition=merge` on PK `id`. Full pull (no `$where` watermark). Audit decorator injects `_extracted_at`, `_extracted_run_id`, `_source_endpoint`; `_first_seen_at` maintained by post-merge `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` + `UPDATE ... WHERE _first_seen_at IS NULL` inside the script. Accepts `RUN_ID` as `sys.argv[1]`.
- `dbt/models/bronze/raw_311_requests.sql` — view repointed via `{{ source('bronze_raw', 'raw_311_requests_raw') }}`; 22 source columns + 6 metadata (4 new audit + 2 dlt) flowing through to gold-eligible bronze shape.
- `dbt/models/bronze/schema.yml` — added `sources:` block declaring `bronze_raw.raw_311_requests_raw`; 4 new audit column descriptions all prefixed with `**PIPELINE METADATA — not for analysis.**`.
- `scripts/pipeline_run_start.py` — Python-owned `CREATE TABLE IF NOT EXISTS main_admin.fct_pipeline_run_raw`; INSERT with `run_status='in_progress'`; prints `RUN_ID` (ULID) to stdout, log line to stderr.
- `scripts/pipeline_run_end.py` — UPDATE the row, COALESCE all flag fields so partial telemetry from caller still wins over defaults.
- `scripts/source_health_check.py` — Python-owned `main_admin.fct_source_health_raw`; pings Socrata metadata endpoint for `rowsUpdatedAt` and the data endpoint for `count(*)`; one row per invocation.
- `run.sh` — expanded 9→10 stages (added stage 0 `pipeline_run_start.py` + stage 10 `pipeline_run_end.py`); captured-exit pattern preserved around both `dbt test` invocations (decision D from chat pre-execution flag list); `trap on_error ERR` records `run_status='failed'` with stage name + exit code on any non-test failure.
- `systemd/pipeline-refresh.{service,timer}` and `systemd/source-health-check.{service,timer}` — new tracked dir parallel to `nginx/`; systemd unit files **explicitly drop the `oxy.service` dependency** (decision B); daily at 6 AM Eastern + hourly on the hour respectively.
- `docs/limitations/source-bulk-republish-no-per-row-modified.md` — replaces the plan's proposed `refresh-3-day-lookback-tail` after pre-flight verified there's no per-row modified field; honest documentation of source publishing model.
- `docs/limitations/audit-columns-non-analytics.md` — flags the six underscore-prefixed columns as pipeline metadata not analytics, with explicit "use `date_created` not `_extracted_at`" guidance.
- `ARCHITECTURE.md` — new "Pipeline & Observability" section between Data Quality Design and Run Order; Run Order section updated to 10 stages with captured-exit + trap detail.
- `CLAUDE.md` — Run Order section updated to 10 stages and `./run.sh daily` vs `manual`.
- `SETUP.md` — `python-ulid` added to §5; new §15 Pipeline scheduling with install/verify/manual-invoke/inspect snippets.
- `LOG.md` — Decisions Log entry for the full Plan 1a change set.
- `TASKS.md` — Plan 1a section with Step 0–10 progress.

## Decisions

- **Path 1 (full pull + merge on `id`)** over the plan's path 2 (watermark + 3-day lookback). Pre-flight found the source dataset has **no publisher-maintained per-row modified field** (`rowsUpdatedAt: 1778531359` = 2026-05-07 UTC matches `:updated_at` for every sampled row). A watermark against `:updated_at` would either match all rows or none. Full pull at 1.17M rows is 5–6 min of dlt load — acceptable for daily, and gives correct INSERT-vs-UPDATE semantics with `_first_seen_at` preserved across re-extractions.
- **Python-owned admin tables, not dbt models.** Same pattern as `raw_dbt_results_raw`: `CREATE TABLE IF NOT EXISTS` inside the Python script; `dbt run --select admin` can't clobber run history. Plan-as-written would have `dbt run` drop the table on each invocation.
- **Drop oxy.service dependency from systemd units.** dlt + dbt write to DuckDB directly; Oxygen reads concurrently (lazy connection, confirmed via `lsof` — oxy doesn't hold the file open). Coupling the timers to oxy.service would block scheduled refreshes whenever Oxygen restarts.
- **Preserve captured-exit pattern in run.sh.** Plan's proposed `set -e + trap ERR` design would exit on the first non-zero, losing the admin tables and `/trust` population on test failure — the exact behavior Plan 3 D3 went out of its way to design in. New run.sh wraps both `dbt test` invocations in `set +e ; ... ; EXIT=$? ; set -e` and only traps genuinely-fatal stages.
- **/trust page surfacing deferred to a follow-on plan.** The new admin tables are populated and inspectable via DuckDB queries; updating `scripts/generate_trust_page.py` to render run history is its own scope.

## Issues encountered

- **python-ulid 3.x API change.** Plan assumed `ulid.new()` (older `python-ulid` 1.x API); 3.1.0 exposes `from ulid import ULID; str(ULID())`. Fixed in `pipeline_run_start.py`, `source_health_check.py`, and `somerville_311_pipeline.py`. One scp+re-run cycle.
- **dlt load step is slower than expected.** First run (empty target): 5 min for the merge of 1.17M rows. Second run (full target): in progress at this writing. Acceptable for daily cadence; not acceptable for sub-hourly. Documented as a known cost in ARCHITECTURE §Pipeline & Observability.

## Next action

Deploy + activate systemd units on EC2 (`sudo cp` to `/etc/systemd/system/`, `daemon-reload`, `enable --now`, `list-timers` verify). Then commit + push. Plan 1b (column profiling + portal ERD) is queued — pre-flagged issues 1b/A and 1b/D resolved in chat ahead of time.
