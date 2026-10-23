---
session: 74
date: 2026-10-23
start_time: 15:02 ET
end_time: 15:40 ET
type: hybrid
plan: none
layers: [portal, infra, docs]
work: [planning, docs]
status: complete
---

## Goal
Audit the repo and the live box for drift, debt and creep, record the October work that skipped this log, and scope the fix.

## What shipped
- Catch-up record of PRs merged without session notes: #86 (EC2 migration runbook, 07-09), #87 (`profile-tables` waits out the DuckDB lock, 10-07), #88 (production: Gemini 3.8 Flash via OpenRouter, date-aware agent, building-permit definition, nginx behind Caddy, 10-11), #89 (rolling-average and fixed-subset DQ checks replace frozen totals, 10-11), #90 (headless answer-agent evals, 10-11), #91 (admin schema accepts rolling/fixed check types, 10-12), #92 (warehouse `flock` for all DuckDB jobs; dlt deletes completed load jobs, 10-12). #93 (MCP server + snapshot job) still open.
- Docs corrected to match production: `CLAUDE.md` (LLM block, env vars, Caddy/auth sentence, stack table and file tree gain dbt Charts, duplicate MVP line removed), `STACK.md` §2.8, `ARCHITECTURE.md` Answer Agent model, `SETUP.md` env vars.
- `LOG.md` back under its 250-line ceiling (297 → 231): Sessions 63–64 rotated to one-liners, the Current Status "Previously" stack and 68 decisions older than 30 days moved to `docs/log-archive.md`; registry rows for Plans 52–53.
- `TASKS.md` Next Focus rewritten around Plan 53; the July EC2-migration row closed as stale.
- `docs/prompts/plan-53-green-pipeline-git-deploys-mcp-live.md`: the fix, as a Code prompt.

## Decisions
- A `partial` pipeline run counts as success to systemd, with an alert — Gordon; otherwise `OnSuccess=` jobs (the MCP snapshot) stall on any test failure.
- The box pulls `main` before each pipeline run — Gordon; ends the hand-copied drift.
- Old box home folders (`oxygen-mvp-backup`, `oxygen-eval`) archived to `~/backups/`, not deleted — reversible.

## Issues encountered
- Pipeline marked failed three days running while data still loads.
- Evidence: `run_status: partial`, exit 1 on 10-21/22/23; Oct 23 failures `not_null_fct_crime_incidents_{offense_code,offense_category,multi_offense_flag}` (1 row each) and `dq_drift_fail_guardrail` (FAIL 3); `/srv/civic-pulse/somerville_ro.duckdb` mtime 2026-10-20.
- Resolution: Plan 53 Phases 1 and 5.
- Box is not deployed from git.
- Evidence: box HEAD `50ca146`, 22 behind; `git diff origin/main` drift in `nginx/somerville.conf` (box `listen 127.0.0.1:8080`, no `auth_basic`; repo `listen 80` + Basic Auth) and generated `portal/` + `_index.yaml` files.
- Resolution: Plan 53 Phase 2.
- MCP endpoint never switched on.
- Evidence: no `mcp/` on the box, no container, no `/mcp` in the Caddyfile, `https://somerville.thewongway.co/mcp` → 404.
- Resolution: Plan 53 Phase 3.

## Next action
Run Plan 53 in Code; Cowork handles SSH key pruning, folder archive and the reboot outside it.
