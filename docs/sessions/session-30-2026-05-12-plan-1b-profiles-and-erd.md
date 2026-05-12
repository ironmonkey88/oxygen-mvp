---
session: 30
date: 2026-05-12
start_time: 10:15 ET
type: code
plan: plan-1b
layers: [admin, portal, infra, docs]
work: [feature, infra, docs]
status: complete
---

## Goal

Execute Plan 1b (Column Profiling + Portal Documentation) — add per-column shape data to a Python-owned admin table, surface it on a new `/profile` portal route, ship Mermaid warehouse + semantic-layer diagrams on a new `/erd` route. Resolve 1b/D (option c — `schema.yml` stays hand-written, profiles on a dedicated portal page).

## What shipped

- `scripts/profile_tables.py` — Python-owned `main_admin.fct_column_profile_raw`; profiles every analyst-facing bronze + gold column. Exclusion patterns keep dlt internals (`_dlt_*`) and dlt landing tables (`*_raw`) out. 75 columns across 5 tables in ~5.5s.
- `scripts/check_profile_staleness.py` — cheap check (~100ms) for `run.sh` integration. Triggers regen on schema change or >10% table row-count delta. Mirrors profile_tables.py's exclusion patterns exactly.
- `scripts/generate_profile_page.py` — reads both `dbt/models/*/schema.yml` (for hand-written descriptions) AND `fct_column_profile_raw` (for shape data); emits `portal/profile.html`. dbt's schema files are NEVER touched.
- `scripts/generate_warehouse_erd.py` — emits Mermaid `erDiagram` source from dbt schema.yml `relationships:` tests (8 models, 2 relationships); audit columns omitted for legibility.
- `scripts/generate_semantic_layer_diagram.py` — emits Mermaid `graph TD` of topics → views → base tables (1 topic, 4 views, 4 base tables).
- `scripts/generate_erd_page.py` — assembles `portal/erd.html` with both Mermaid diagrams; client-side render via jsdelivr CDN.
- `nginx/somerville.conf` — `location = /profile` and `location = /erd` added (matching `/metrics` and `/trust` patterns).
- `systemd/profile-tables.{service,timer}` — Sunday 2 AM ET weekly regen with `ExecStartPost` profile-page refresh + deploy. No `oxy.service` dependency.
- `run.sh` — stages 9b (staleness check, `cmd || rc=$?` form), 9c (conditional regen), 9d (`/profile` page), 9e (warehouse ERD + semantic + `/erd` page). All four new stages run after limitations index and before `pipeline_run_end`.
- `ARCHITECTURE.md` — Pipeline & Observability section extended with Plan 1b mechanics + a "Portal documentation surfaces" table covering all five routes (/docs, /erd, /metrics, /profile, /trust).
- `SETUP.md` §15 — third timer (`profile-tables.timer`) added; install command simplified to `systemd/*.service systemd/*.timer` glob; run-order list bumped to include 9b–9e.
- `CLAUDE.md` — Plan 1b workflow note: manual `profile_tables.py + generate_profile_page.py` after dbt model changes, with explicit "dbt's schema.yml files are NEVER touched by the profile pipeline" reminder.
- `LOG.md` — Active Decisions row capturing 1b/D option (c) rationale + the five-portal-routes inventory.

## Decisions

- **1b/A (raised pre-execution): Python-owned `fct_column_profile_raw`**, same pattern as Plan 1a's `fct_pipeline_run_raw` and `fct_source_health_raw`. `dbt run --select admin` cannot clobber profile history.
- **1b/D (raised pre-execution): option (c) — `schema.yml` stays hand-written.** dbt's globbing of `models/**/*.yml` means renaming hand-written schema files to `schema.source.yml` while auto-generating `schema.yml` would have caused dbt to load both files and error on duplicate model definitions. The alternative considered ((a), moving sources outside `models/` + gitignoring the generated `schema.yml`) was rejected for its hand-edit-lost risk — anyone using `vim dbt/models/bronze/schema.yml` would lose work on the next regen, and new clones would see empty schema files until the pipeline runs. Option (c) keeps dbt's convention intact and gives /profile freedom to be a richer surface than what dbt docs renders.
- **Exclude `_dlt_*` and `*_raw` tables from profiles.** First profile run produced 131 rows including profiles for `_dlt_loads`, `_dlt_pipeline_state`, `_dlt_version`, `raw_311_requests_raw`, `raw_dbt_results_raw` — none of which an analyst queries. Filter applied in both `profile_tables.py` and `check_profile_staleness.py` (same `NOT LIKE '\\_%' AND NOT LIKE '%\\_raw'` pattern); truncated and re-ran, ended at 75 analyst-facing rows.
- **Mermaid CDN over local copy.** The `/erd` page loads Mermaid from jsdelivr at runtime. Internal-tool, daily-refresh portal — offline resilience is not a load-bearing concern. If it becomes one, vendoring is a 30-line follow-on.

## Issues encountered

- **scp accidentally placed `plan1b_truncate_profile.py` under `scripts/` instead of `/tmp/`.** Single multi-source scp with destination ending in `scripts/` (no trailing slash on the destination on the previous command) put both files there. Caught immediately, removed, re-scp'd to `/tmp/`. No production impact.

## Next action

Commit Plan 1b on `claude/nice-shtern-4d9efc`. Push (or merge to `main`) at Gordon's discretion — Plan 1a's commit `a0f4904` is still unpushed too, so they go together. After that, MVP 2 (Visual Knowledge Products / Builder Agent) plan-scoping resumes as the active focus per `TASKS.md` Next Focus.
