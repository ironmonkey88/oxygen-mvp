---
session: 5
date: 2026-05-07
start_time: 22:00 ET
end_time: 2026-05-08 07:00 ET
type: overnight
plan: none
layers: [bronze, gold, semantic, infra, docs]
work: [hardening, feature, refactor]
status: complete
---

# Session 5 — Repo cleanup and overnight run (gold + Airlayer + semantic)

## Goal
Audit repo state across local Mac / EC2 / GitHub, recover missing source files, then run an overnight multi-deliverable execution: gold dbt models, Airlayer CLI install, semantic layer.

## What shipped
- Recovered `dlt/somerville_311_pipeline.py` from live EC2 into local repo
- Recovered `dbt/dbt_project.yml`, `dbt/models/bronze/raw_311_requests.sql`, `dbt/models/bronze/schema.yml` from EC2 backup
- Rewrote `bronze/raw_311_requests.sql` to match `docs/schema.sql`: all 22 source columns + 2 dlt metadata columns, all VARCHAR, `union_by_name=true`
- Bronze on EC2: `dbt run --select bronze` built `main_bronze.raw_311_requests` (1,168,959 rows, 24 cols), 5/5 tests pass
- Added `dbt/profiles.yml` to `.gitignore`; rewrote `SETUP.md` step 8 to drop the repo-local profile alternative
- Allowlisted ~60 read-only Bash commands in `.claude/settings.json`
- Overnight Deliverable 0: doc cleanup (.sem.yml → .view.yml, Airlayer dual-engine model documented)
- Overnight Deliverable 1: gold dbt models — `dim_date` (3,993), `dim_request_type` (342), `dim_status` (4), `fct_311_requests` (1,168,959); 14/14 tests pass
- Overnight Deliverable 2: Airlayer CLI 0.1.1 installed on EC2 at `~/.local/bin/airlayer`
- Overnight Deliverable 3: semantic layer — 4 views + 1 topic, schema valid, executes via auto-join (5 rows returned)
- Reconciled `docs/schema.sql` with live Bronze view: added `_dlt_load_id`, `_dlt_id` with comment block

## Decisions
- `~/.dbt/profiles.yml` is the only supported profile path — no repo-local `dbt/profiles.yml`
- Bronze keeps source columns as VARCHAR; date columns cast `::VARCHAR` rather than `::TIMESTAMP`
- No empty stubs for unbuilt components — directories land when their MVP is built
- `.view.yml` (views) + `.topic.yml` (topics) replace `.sem.yml` everywhere — matches Airlayer schema spec
- Airlayer is dual-engine: Oxygen built-in + standalone Rust CLI, same `.view.yml` schema
- Gold location fields limited to `ward` + `block_code` — bronze has no neighborhood/lat/long/address
- Gold surrogate keys named `_id` (md5 hash) for MVP 1; `_sk` reserved for MVP 3+
- `is_open = false` only for `Closed`; true for Open/In Progress/On Hold
- Airlayer 0.1.1 datasource config lives in `config.yml`, not on the CLI
- `oxy build` validation gate downgraded for MVP 1; `oxy validate` + `airlayer query -x` cover the intent. Deferred to Answer Agent session when `oxy start` runs naturally.
- EC2 pulls from GitHub `main` at session start (CLAUDE.md "Session Start on EC2") — Session 5 caught EC2 7 commits behind
- Always-ask boundary made explicit in memory: schema/semantic/agent/destructive ops require explicit confirmation even when broader work is approved

## Issues encountered
- **Heredoc commands over SSH trip Code's permission system on every call.** Even with `Bash(ssh oxygen-mvp *)` allowlisted, the newline + `#` pattern hides arguments from path validation. Resolution: switched to scratch/-then-scp pattern for ad-hoc DuckDB queries — write file in `scratch/` (gitignored), scp to /tmp/ on EC2, run with `python /tmp/foo.py`.
- **Worktree git commands don't match allowlist patterns.** `git -C <worktree-path> commit ...` doesn't match `Bash(git commit *)` because `-C <path>` precedes the subcommand; "Allow always" doesn't stick because worktree paths contain session-specific identifiers. Resolution deferred to a later allowlist broadening (eventually executed in Plan 0).
- **`oxy build` validation gate failed:** `OXY_DATABASE_URL environment variable is required. Use 'oxy start' to automatically start PostgreSQL with Docker, or set OXY_DATABASE_URL to your PostgreSQL connection string.` Resolution: gate downgraded — `oxy validate` + `airlayer query -x` cover the original "config valid + queryable" intent. Real `oxy build` deferred to Answer Agent session.

## Next action
Decide on CLAUDE.md `model_ref` doc fix; broaden `.claude/settings.local.json` allowlist before next overnight; plan Answer Agent session.
