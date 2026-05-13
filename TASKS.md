# TASKS.md — Oxygen MVP Task Tracker

> Status markers: `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked
> Claude Code updates this file as work progresses.

---

## Next Focus — MVP 2 Plan-Scoping: First Data App via Builder Agent

MVP 1 fully closed. Sign-off landed Session 25 (`oxy start --local` pivot); MVP 1.5 closed Sessions 26–28 (Opus 4.7 + public `/chat`); Plans 1a + 1b closed Sessions 29–30 (daily incremental refresh + observability + column profiling + `/erd` + `/profile`). Retrospective at [`docs/retrospective/mvp1-lessons-learned.md`](docs/retrospective/mvp1-lessons-learned.md) (Session 31).

The first MVP 2 deliverable is **one dashboard built through conversation with Builder Agent**. The dashboard demonstrates the analyst-outcome test from BUILD.md §5: "The analyst describes a dashboard in chat; Builder Agent assembles it. Iterates by conversation, not by writing YAML."

Per the MVP.md Working Backwards example, the anchor target is service equity across neighborhoods, with four investigative angles (volume, resolution rate, resolution time, service mix) one click apart.

### Scope decisions to be made (in plan-scoping session)

- [ ] **Which first dashboard?** Options: single-angle (resolution time by ward) vs multi-angle (full equity dashboard) vs two-step build (single-angle then expand via conversation)
- [ ] **What semantic-layer additions are required?** Likely `avg_days_to_close` measure, resolution-time-band dimension, possibly category rollup
- [ ] **What does the Builder Agent conversation look like?** Capture the intended demo transcript before construction so we can measure how close the actual session lands
- [ ] **What surface?** Portal `/dashboard` route, in-chat embedding (`run_app` tool), or both
- [ ] **Where does the dashboard reference the new audit columns and trust signals?** Should `_extracted_at` of the latest record appear somewhere — and does the dashboard read from `fct_pipeline_run_raw` for a "last refreshed" line?

### Pre-flight verification needed (do BEFORE plan-scoping commits to shape)

Builder Agent is documented in Oxygen changelogs ([2026-04-09](docs/oxygen-docs/changelog/2026-04-09.md) intro, [2026-04-16](docs/oxygen-docs/changelog/2026-04-16.md) improvements, [2026-05-07](docs/oxygen-docs/changelog/2026-05-07.md) major upgrade) but NOT in the canonical `learn-about-oxy/` guide. Per the changelogs, Builder is "a builder copilot agent that can read, modify, and iterate on your Oxygen project files" — workspace-wide, not Data-App-specific. UI surface is the chat panel's "Build mode" (alongside "Ask mode"), plus a dedicated Builder Dialog. Tools include `run_app` (executes a Data App by path, fed back as context), `read_file`, file-edit tools with HITL approvals, and 15+ dbt-aware tools.

- [ ] **"Build mode" reachable in the chat panel** at `http://18.224.151.49/chat` (Basic Auth) or `http://oxygen-mvp.taildee698.ts.net:3000` (Tailnet) — does the chat panel offer Build mode alongside Ask mode in `--local` mode?
- [ ] **Builder can read/modify YAML files in the workspace** — the canonical capability test; should produce `FileChangePending` events with HITL approval
- [ ] **Data Apps render in the SPA** — `oxy run apps/foo.app.yml` or the IDE's app browser; note that `oxy build` is for vector embeddings, not Data App rendering
- [ ] **Builder's `run_app` tool works in `--local` mode** — the key MVP 2 capability (Builder builds → runs → refines a dashboard in one loop)
- [ ] **No multi-workspace wizard gates Build mode in `--local`** — would re-introduce the Session 25 blocker
- [ ] **Latest Oxygen changelog reviewed at plan-scoping** — per retrospective lesson, platform velocity has been delivering Verified Queries, Data Apps, Slack, MCP, A2A throughout this project

### Out of scope for MVP 2's first plan

- Additional data sources (weather first, then ward + demographics — each its own plan)
- Expanded trust page prose (own plan)
- Full Data Apps library (MVP 4)
- Routing Agent / multi-topic dispatch (MVP 4)
- Slack / MCP / A2A sharing surfaces (MVP 4)
- Return to multi-workspace mode (MVP 4 prerequisite, not MVP 2)

### Carry-over queued items (independent of MVP 2)

- [ ] Auto-refresh portal stats dates from DuckDB on `run.sh` (currently hardcoded — Session 28 follow-up)
- [ ] Somerville wards map as portal hero background (Socrata blob-only + OSM Overpass errored; pragmatic path is stylized SVG)
- [ ] Investigate why recent `./run.sh daily` invocations are landing `run_status='partial'` (admin tests failing — likely drift-fail at the new baseline; Session 31 pre-flight observation)

---

## Sign-off Status

### MVP 1 — 1st Data Product
- [x] Environment set up on EC2
- [x] GitHub repo initialized and connected
- [x] dlt pipeline ingesting Somerville 311 data — 1,168,959 rows loaded
- [x] Data model designed — schema.sql written, ERD generated
- [x] nginx installed, portal live and verified at http://18.224.151.49
- [x] dbt initialized; bronze model live (1.17M rows, 5/5 tests pass)
- [x] dbt gold models live: `dim_date` (3,993), `dim_request_type` (342), `dim_status` (4), `fct_311_requests` (1,168,959); 14/14 tests pass
- [x] Portal designed and fonts self-hosted (DM Serif Display, DM Mono, Instrument Sans)
- [x] Portal verified live in browser at http://18.224.151.49
- [x] Airlayer CLI 0.1.1 installed on EC2
- [x] Airlayer semantic layer: 4 views + 1 topic, schema valid, executes via auto-join
- [x] Oxygen runtime live on EC2 — `oxy start` brings up Postgres container + web app on :3000; `oxy build` exits 0 in plain non-interactive ssh
- [x] Env vars in `/etc/environment` — `ANTHROPIC_API_KEY`, `OXY_DATABASE_URL`, plus `~/.local/bin` on PATH; documented in [SETUP.md](SETUP.md) §7
- [x] Answer Agent `.agent.yml` configured — minimal FR scope (no trust contract yet)
- [x] Chat UI accessible and answering questions correctly — verified in SPA at `http://oxygen-mvp.taildee698.ts.net:3000` after Session 25 pivot to `oxy start --local`. "How many 311 requests were opened in 2024?" returned 113,961 with execute_sql artifact + "Returned 1 row." + Citations (`main_gold.fct_311_requests` + `requests` Airlayer view) + analyst-honest Known limitations section. CLI `oxy run` path also intact across full bench 5/5 (Q1 113,961, Q2 49,782 YTD, Q3 top types match, Q4 block-code-padded NA sentinel surfaced, Q5 satisfaction 4.44/5 blended). Reboot survival proven Sessions 24 + 25.
- [x] Trust contract on agent (SQL + row count + citations in every response)  *(Plan 6 — STANDARDS §4.1 4/4)*
- [x] Admin DQ framework in place  *(2026-05-08 — D2 of overnight; 3 admin models, run.sh, load_dbt_results.py; verified across 2 consecutive runs)*

### MVP 1.5 — Post-Sign-off Hardening
- [x] Switch Answer Agent from Sonnet 4.6 to Opus 4.7 *(2026-05-11; commit `a5853d0` switched `config.yml` + `agents/answer_agent.agent.yml`; CLI bench 5/5 + SPA bench Q1–Q5 in single thread, no `ApiError`; rate-limit headroom 30K → 500K tokens/min; `agent-rate-limit-multi-turn-spa` limitation `mitigated-by-opus-4-7-migration`)*
- [x] Portal polish: Sonnet → Opus refs (3 places), `Last data point` + `Last pipeline run` stats added, stats grid responsive, trust page section max-width 1100 → 1400 *(2026-05-11)*
- [ ] Auto-refresh portal stats dates from DuckDB on `run.sh` *(hardcoded for now; should sed-substitute from `MAX(date_created_dt)` + run timestamp on each pipeline run; small Python script + run.sh step 7.5 pattern)*
- [ ] Somerville wards map as hero background *(Socrata wards dataset `ym5n-phxd` is blob-only, not exportable as GeoJSON; OpenStreetMap Overpass query returns errors; pragmatic path: render a stylized SVG outline manually from MassGIS shapefile or trace the city PDF at https://www.somervillema.gov/sites/default/files/ward-and-precinct-map.pdf; deferred for a focused pass)*
- [x] Public chat access via nginx Basic Auth at `/chat` *(2026-05-11; final design: auth-gate only `/chat` entry; SPA internal paths `/api`, `/assets`, `/home`, `/threads`, `/oxygen-*` proxy unauth (the SPA's streaming agent POST omits credentials, so gating those paths loops). bcrypt `analyst` credential in `/etc/nginx/.htpasswd` root:www-data 640 — NOT in repo, .gitignore hardened. Portal hero pill clickable. **Gate 4 PASSED**: Gordon SPA-tested in browser, asked "how many requests", agent returned 1,170,023 with execute_sql artifact + Citations, no second auth prompt. Trade-off recorded at `docs/limitations/chat-auth-basic-cleartext.md` — API-token-burn risk only, no data exposure; replaced by MVP 4's Magic Link + HTTPS)*

#### Plan 1a — Daily Incremental Refresh + Observability *(2026-05-11 — in progress)*
Foundation for Plan 1b. Architectural decisions resolved in chat: (A) Python owns `*_raw` admin tables; (B) systemd unit drops oxy dependency; (C) dlt-direct-to-DuckDB merge replaces filesystem Parquet; (D) preserve captured-exit pattern in run.sh; (E) /trust surfacing deferred to follow-on; (F) load_dbt_results lives in `dlt/`, no `check_drift.py` (drift via `dbt test --select admin`); (G) modified-field name TBD from SODA pre-flight.

- [x] Step 0 — Pre-flight: dlt 1.26.0 ✓ python-ulid installed ✓ bronze schema captured ✓ gold count 1,170,023 ✓ PK confirmed `id` (not `case_id`) ✓ **modified-field finding**: dataset has NO publisher-maintained per-row modified column; Socrata's `:updated_at` is republish-batch-level → switched plan from watermark+3-day-lookback to **full-pull + merge on `id`** per pre-flight recommendation (path 1)
- [x] Step 1 — Audit columns on bronze: `_extracted_at`, `_extracted_run_id`, `_first_seen_at`, `_source_endpoint` populated on 1,170,591 rows; 0 NULLs across all four; bronze.yml descriptions updated *(commit pending)*
- [x] Step 2 — Pipeline refactor: filesystem-Parquet → DuckDB direct, `dlt.destinations.duckdb`, write_disposition=merge on `id`, full pull (no watermark); bronze view repointed at `main_bronze.raw_311_requests_raw`; gold rebuilt; 19/19 tests pass; **2024 regression check: 113,961 (exact match to Plan 6 D3)**
- [x] Step 3 — `scripts/pipeline_run_start.py` + `scripts/pipeline_run_end.py` + Python-owned `main_admin.fct_pipeline_run_raw`; smoke-tested with manual run_id 01KRD6G8EHV0J4RJAM1XQWKWA3, INSERT + UPDATE both work; `run.sh` rewritten preserving captured-exit pattern (decision D) with trap-on-error → record failed status
- [x] Step 4 — `scripts/source_health_check.py` + Python-owned `main_admin.fct_source_health_raw`; smoke-tested, check_status=ok, source_row_count=1,170,591, 7 hours since `rowsUpdatedAt`, HTTP 200
- [x] Step 5 — End-to-end `./run.sh manual` validation: first attempt's `set +e ; cmd ; set -e` captured-exit tripped the ERR trap on bash 5.x (run logged as failed at stage `dbt_test_admin`); switched to the `cmd || rc=$?` idiom (POSIX-exempt from errexit), reverified via partial-run test on EC2 → all 10 stages execute, `run_status='partial'` recorded when admin tests fail. Three rows now in `main_admin.fct_pipeline_run_raw` (the 5s standalone test, the 770s broken-trap run kept as history, the 29s partial run with fix).
- [x] Step 6 — `systemd/pipeline-refresh.{service,timer}` deployed; `pipeline-refresh.timer` shows next-run **Tue 2026-05-12 10:00:00 UTC = 6:00 AM EDT** in `systemctl list-timers`. No `oxy.service` dependency.
- [x] Step 7 — `systemd/source-health-check.{service,timer}` deployed; `source-health-check.timer` shows next-run **Tue 2026-05-12 05:00:00 UTC** (top of next hour, 22 min after activation).
- [x] Step 8 — Two limitations entries written: `source-bulk-republish-no-per-row-modified.md` (honest documentation that source publishes in bulk with no per-row modified field) and `audit-columns-non-analytics.md` (the six underscore-prefixed metadata columns are not analytics). `docs/limitations/_index.yaml` regenerated: 10 → 12 active entries.
- [x] Step 9 — `ARCHITECTURE.md` gained "Pipeline & Observability" section + Run Order updated to 10 stages with captured-exit + trap detail; `CLAUDE.md` Run Order section synced; `SETUP.md` §5 added `python-ulid` to pip install, new §15 "Pipeline scheduling" with install/verify/manual-invoke/inspect snippets; `LOG.md` Active Decisions row for Plan 1a with full change set; `docs/sessions/session-29-...md` narrative written.
- [x] Step 10 — Commit `a0f4904` on `claude/nice-shtern-4d9efc` (20 files, +1015/-87). Local-only — push/merge to `main` pending Gordon's call.

#### Plan 1b — Column Profiling + Portal Documentation *(2026-05-12 — in progress)*
Architectural decisions resolved in chat: **1b/A** = Python-owned `fct_column_profile_raw` (same pattern as Plan 1a admin tables); **1b/D** = option (c) — keep `dbt/models/*/schema.yml` hand-written, surface profiles on a new dedicated `/profile` portal page driven by `fct_column_profile_raw`, never touch dbt's schema files programmatically.

- [x] Phase 1 — `scripts/profile_tables.py` + `main_admin.fct_column_profile_raw` (Python-owned); 75 columns profiled in 5.5s after adding `_dlt_*` + `*_raw` exclusion patterns
- [x] Phase 2 — `scripts/check_profile_staleness.py` reports `CURRENT` after fresh profile run; wired into run.sh stages 9b (`cmd || rc=$?` form) + 9c (conditional regen)
- [x] Phase 3 — `scripts/generate_profile_page.py` writes `portal/profile.html` (75 columns, 5 tables, 73KB); reads `schema.yml` for descriptions + `fct_column_profile_raw` for shape; dbt schema files never touched
- [x] Phase 4 — `scripts/generate_warehouse_erd.py` (8 models, 2 relationships from dbt `relationships:` tests; audit cols omitted) + `scripts/generate_semantic_layer_diagram.py` (1 topic, 4 views, 4 base tables)
- [x] Phase 5 — `scripts/generate_erd_page.py` assembles `portal/erd.html` with both Mermaid sources via jsdelivr CDN; `nginx/somerville.conf` gains `location = /profile` + `location = /erd`; reload tested. Portal nav (`portal/index.html`) extended with `/erd` and `/profile` links; live homepage verified
- [x] Phase 6 — `systemd/profile-tables.{service,timer}` deployed; `systemctl list-timers` shows next run **Sun 2026-05-17 06:00:00 UTC = 2:00 AM EDT**; `ExecStartPost` refreshes `/profile` page + deploys after each regen. No `oxy.service` dependency
- [x] Phase 7 — `ARCHITECTURE.md` (Pipeline & Observability extended; 5-route portal table); `SETUP.md` (§15 → 3 timers, run-order list bumped to 9b–9e); `CLAUDE.md` (Plan 1b workflow note with manual `profile_tables.py + generate_profile_page.py` after dbt model changes); `LOG.md` (Active Decisions row); `docs/sessions/session-30-...md` narrative written
- [x] Phase 8 — Commit `0a0a065` (2026-05-12 10:36 EDT) on `claude/eloquent-varahamihira-a0c106`

### MVP 2 — Visual Knowledge Products
- [ ] Airapp `.app.yml` with charts

### MVP 3 — Governance and Trust
- [ ] dbt Silver model with PII redaction
- [ ] dbt Gold model updated with dim_location
- [ ] Tailscale access control

### MVP 4 — Semantic Depth and Sharing
- [ ] Full Airlayer metric library
- [ ] Routing Agent configured

---

## Overnight Session — 2026-05-07 → 2026-05-08

### Deliverable 0 — Doc cleanup
- [x] Apply CLAUDE.md + ARCHITECTURE.md edits, commit, push
- [x] EC2 `git pull origin main` and verify commit landed

### Deliverable 1 — Gold dbt models
- [x] Query bronze on EC2 to confirm column names/types
- [x] Write `gold/dim_date.sql`
- [x] Write `gold/dim_request_type.sql`
- [x] Write `gold/dim_status.sql`
- [x] Write `gold/fct_311_requests.sql`
- [x] Add gold tests (unique/not_null/relationships)
- [x] `dbt run --select gold` and `dbt test --select gold` clean
- [x] Commit and push gold models

### Deliverable 2 — Airlayer CLI install
- [x] Install Airlayer CLI on EC2; `airlayer --version` works (0.1.1)
- [x] Sanity check `airlayer query --help` runs (CLI shape note logged)
- [x] Log version + system packages added to LOG.md
- [x] Commit LOG.md/TASKS.md update

### Deliverable 3 — Semantic layer
- [x] Create `semantics/views/{requests,request_types,statuses,dates}.view.yml`
- [x] Create `semantics/topics/service_requests.topic.yml`
- [x] Update `config.yml` to register `somerville` datasource (oxy 0.5.47 schema: `model_ref`/`key_var`)
- [x] ~~`oxy build` exits 0~~ — *gate downgraded 2026-05-08 07:31 ET. `oxy validate` (config syntax, exits 0) + `airlayer query -x` (real data, 5 rows) cover the intent; `oxy build` (vector embeddings) only matters once `oxy start` is up, which lands with the Answer Agent.*
- [x] `airlayer query ... -x` returns rows (5 rows, auto-join via entity match)
- [x] Commit and push semantic layer

---

## MVP 1 — 1st Data Product
**Goal:** Static data file → DuckDB → Airlayer → Answer Agent chat UI

### Scope statement
- Target user: city analyst, not general resident
- Goal: analyst asks Answer Agent a question, gets a correct answer with SQL + row count + citations, and can verify it independently
- Bar: extreme trustability — every answer is inspectable and reproducible
- Out of scope this MVP: charts, exports, follow-up suggestions, anomaly surfacing, /about page, long-form .qmd-style docs
- See [STANDARDS.md](STANDARDS.md) for "done done" criteria

### Repo Cleanup (Session 5)
- [x] Audit local Mac vs EC2 vs GitHub for missing source files
- [x] Recover `dlt/somerville_311_pipeline.py` into the repo (live EC2 copy)
- [x] Recover `dbt/dbt_project.yml` and `dbt/models/bronze/*` from EC2 backup
- [x] Update `bronze/raw_311_requests.sql` to mirror all 22 source columns per `docs/schema.sql`
- [x] Verify Bronze model builds and 5/5 tests pass on EC2
- [x] Add `dbt/profiles.yml` to `.gitignore`; remove repo-local profile alternative from `SETUP.md`
- [x] Confirm `dim_origin` and `portal/` already present in `ARCHITECTURE.md` and `TASKS.md`

### MVP 1 — Hardening for analyst trust

#### Plan 6 — Answer Agent + Trust Contract (2026-05-09 21:00 ET — closed)
Closes STANDARDS §4.1 (4/4) and §5.7 (4/4).
- [x] Pre-flight: agent yaml + limitations read; Oxygen runtime confirmed up (curl :3000 → 200; `oxy start` running as nohup since May 8 — not as systemd, that's a §3.2 row 4 gap for Plan 7); STANDARDS §7 open question resolved (partial native — runtime renders SQL+result; citations/row-count/limitations are prompt-enforced); CLI invocation = `oxy run agents/answer_agent.agent.yml "<question>"`
- [x] D1 — Trust contract in `agents/answer_agent.agent.yml` `system_instructions`: 4-section reply contract (Returned N rows / Answer / Citations / Known limitations); engineering-honest tone (no emoji, no marketing); limitations index loaded as `context.file` `docs/limitations/_index.yaml`; commit `b3b5217` + index-only follow-up
- [x] D1 follow-up — switched from full-bodies `*.md` glob to `_index.yaml` after Q3+Q5 first-attempt rate-limited at 30K tokens/min (full-body context too large); index pipeline (`scripts/build_limitations_index.py` + `run.sh` step 9/9) generates the index from frontmatter
- [x] D2 — Matching rule: substring of any `affects:` value appears in SQL or in cited views; prompt-only (no post-processing wrapper); verified Q4 surfaced `block-code-padded` + `location-ward-block-only` correctly with no false positives; verified Q5 surfaced `2024-survey-columns-sparse` + `survey-columns-on-fact` correctly
- [x] D3 — 5/5 test bench passed (transcripts in `scratch/plan6_test_bench/q[1-5]_*.md`): Q1 2024=113,961 ✓ (regression match), Q2 partial-year 49,782 ✓ (SQL correct; agent prose hallucinated "2025" — knowledge-cutoff issue, follow-on for prompt hardening), Q3 top-10 ✓ (Pothole at #10 with 21,393), Q4 block-level ✓ (with diligent NA-sentinel callout), Q5 satisfaction ✓ (76.0% Very Satisfied, both survey limitations surfaced, percentage math reconciled)
- [x] D4 — STANDARDS §4.1 4/4 + §5.7 4/4 flipped; STANDARDS §7 open question resolved; session 18 file; LOG.md updated; commits `b3b5217` (D1) + Plan 8/D1-followup commit + Plan 6 close commit

#### Plan 8 — Limitations Registry Expansion (2026-05-09 21:00 ET — closed)
Closes STANDARDS §4.4 row 2.
- [x] `2024-survey-columns-sparse.md` tightened from `affects: [requests]` (overfired on every requests-view query) to `affects: [accuracy, courtesy, ease, overallexperience]` (granular column names)
- [x] `location-ward-block-only.md` (warning, 2026-05-07; affects ward, block_code)
- [x] `survey-columns-on-fact.md` (info, 2026-05-07; affects accuracy, courtesy, ease, overallexperience — actual columns; brief had speculative names)
- [x] `dept-tags-as-booleans.md` (info, 2026-05-07; affects 8 boolean tag column names)
- [x] `bronze-varchar-source-cols.md` (info, 2026-05-07; affects bronze.raw_311_requests, main_bronze.raw_311_requests)
- [x] `open-status-not-just-open.md` (warning, 2026-05-07; affects open_requests — note: brief referenced is_open which doesn't exist in current schema, reframed around the open_requests measure semantics)
- [x] `open-requests-no-join-filter.md` (info, 2026-05-08; affects open_requests)
- [x] `current-year-partial.md` (warning, 2026-05-08; affects current_date sentinel)
- [x] `oxy-build-postgres-dependency.md` (info, 2026-05-08; affects deploy.oxy_build sentinel — does NOT auto-surface on analyst queries by design)
- [x] `scripts/build_limitations_index.py` reads `*.md` frontmatter (stdlib-only — no PyYAML dep); `docs/limitations/_index.yaml` generated with 10 active entries; `run.sh` step 9/9 wires it into the pipeline
- [x] Surfacing verified end-to-end via Plan 6 D3 test bench Q4 + Q5; STANDARDS §4.4 row 2 → [x]; session 18 file; LOG; commit

#### Plan 7 — MVP 1 Sign-off Sweep (2026-05-09 21:40 ET — closed)
Closed STANDARDS §5.8 last row; STANDARDS §6 walk landed 9/10 Foundations + 16/16 trust + 7/7 layers + 5/5 E2E smoke.
- [x] D1 — STANDARDS §6 walk: §3.2 (4/5 — systemd row open), §3.3 ✓, §4.5 (2/3 — repo-public row open), §5.1–5.8 all flipped with evidence (curl checks for /metrics, /docs, /trust live; dlt pipeline source URL + `4pyi-uqq6` + `replace` + `union_by_name=true` confirmed; bronze 25 descs + 1 unique + 3 not_null + 1 accepted_values; gold 51 descs + 4 unique + 7 not_null + 2 relationships + 1 accepted_values; semantic `oxy validate` 6/6 valid)
- [x] D2 — Portal copy refreshed and deployed: hero ("Somerville 311, queryable in plain English"; analyst-honest blurb stating SQL+row count+citations on every reply); stats (date range / source columns / documented limitations count); replaced /erd + /tasks asset cards (routes don't exist) with /trust + /metrics cards; "Built on Oxygen" prose detoxed to factual stack description; verified live via curl
- [x] D3 — Sign-off determination: 2 boxes still `[ ]`, both Gordon-decision-shaped (systemd-as-MVP1-requirement, repo-public). LOG.md Active Blockers section has the table. MVP 1 is **sign-off-ready pending these two decisions** — not auto-flipping.
- [x] D4 — Session file 19; LOG Plans Registry; commit `Plan 7 close`

#### Plan 5 D1 follow-on — Git pipe pattern coverage (2026-05-10 16:45 ET — closed)
Session 21. Root cause: `*` in allowlist patterns does not match `|`; piped git commands (`git log 2>&1 | head`) were prompting in unattended overnight sessions.
- [x] Root cause identified: `Bash(git *)` covers non-piped forms only — `|` is not matched by `*` in Claude Code patterns
- [x] Added `Bash(git * | *)` — single-pipe bare git forms (merge commit `997dc04`)
- [x] Added `Bash(git -C * * | *)` — single-pipe worktree-path forms (merge commit `997dc04`)
- [x] Added `Bash(git * | * | *)` — double-pipe fallback (merge commit `997dc04`)
- [x] Added `Bash(git rev-list *)` + `Bash(git -C * rev-list *)` — commit counting (merge commit `997dc04`)
- [x] Added `Bash(git ls-remote *)` + `Bash(git -C * ls-remote *)` — remote ref listing (merge commit `997dc04`)
- [x] Added `Bash(git branch *)` + `Bash(git -C * branch *)` — broad branch coverage (merge commit `997dc04`)
- [x] Removed duplicate `"Bash(bash *)"` entry from worktree `settings.json` (merge commit `997dc04`)
- [x] CLAUDE.md Allowlist policy + Bash Safety sections updated with pipe-coverage note (merge resolution)
- [x] Session 21 file, LOG.md, TASKS.md committed and pushed to `origin/claude/gifted-cartwright-9b6bac`

#### Plan 5 — Tech Debt Sweep (2026-05-10 09:55 ET — closed)
- [x] D1 — settings.local.json pruned to `{"permissions":{"allow":[]}}` (every pattern was redundant with tool-family allows in settings.json); added `Bash(bash *)` to settings.json so script invocations don't stall; CLAUDE.md "Allowlist policy" extended with "what belongs where" + periodic-prune subsection; commit `b274ae7`
- [x] D2 — `dbt/profiles.example.yml` shipped; SETUP.md §8 rewritten to reference cp+edit pattern; closes the machine-specificity gap noted in 2026-05-07 22:13 ET decision; commit `1f0d05d`
- [x] D3 — scratch/ hygiene check: only `plan6_test_bench/` exists (just-created in Session 18); no old runner files, no stale ad-hoc SQL; nothing to prune; commit `1f0d05d`
- [x] D4 — run.sh step-text consistency: already aligned in Session 18 when step 9 was added (1/9 through 9/9, plus 5b/9 sub-step); no drift to fix; verified via grep
- [x] D5 — doc reconciliation: CLAUDE.md Run Order section updated 7→9 steps (with 5b sub-step); ARCHITECTURE.md Run Order code block updated 7→9 steps with full bash-shape; ARCHITECTURE.md Portal routes table updated (/trust now Plan 4 done; /erd + /tasks marked deferred-from-MVP-1 + portal-card-removed); ARCHITECTURE.md "Process management" line corrected (Oxygen is nohup, not systemd — STANDARDS §3.2 row 4 open); TASKS.md "Deliverable B [~]" closed
- [x] D6 — Session 20 file; LOG.md updates; commit `Plan 5 close`; WAKE-UP BRIEF commit on top

#### Plan 9 rev 2 — Allowlist Coverage + Bash Safety Hook (2026-05-09 19:35 ET — closed)
- [x] Layer 0 audit: confirmed `defaultMode: acceptEdits`, bare `Read`/`Write`/`Edit`, `WebFetch(*)`, `Read(**/.env)` deny, `$schema` all intact from Plan 9 rev 1; no drift
- [x] Layer 1 allow merge: added `Bash(git *)` (bare) + `Bash(sudo ln *)` (broader); all rev 1 patterns preserved
- [x] Layer 1 deny merge: added `Read(~/.ssh/**)`, `Read(~/.gnupg/**)`, `Bash(launchctl *)`, `Bash(eval *)`, `Bash(curl * | bash*)`, `Bash(curl * | sh*)`, `Bash(wget * | bash*)`, `Bash(wget * | sh*)`
- [x] Layer 2 hook: `.claude/hooks/block-dangerous.sh` — blocks `&&`, `||`, naked `;`, `$(...)` (arithmetic `$((...))` exempt via `\$\([^(]` regex), `<()`, `>()`, leading `cd `, leading `export `; loop keywords carve-out via `sed -E 's/;[[:space:]]+(do|then|done|fi|else|elif)([[:space:]]|$)/ \1\2/g'` strip
- [x] Layer 2 wire: appended as second entry in `hooks.PreToolUse` (matcher Bash) — task-warning hook preserved
- [x] Layer 2 chmod: hook is executable (`-rwxr-xr-x`)
- [x] Layer 1 verify: `python3 -m json.tool .claude/settings.json` exits 0
- [x] Layer 3 CLAUDE.md: "Bash Safety" section landed between Rules and Naming Standards
- [x] Layer 4 audit: `scripts/check_allowlist_coverage.sh` rewritten — 11 idioms ran without prompting, 13/13 hook-deny/allow assertions passed
- [x] Session 17 file written ([docs/sessions/session-17-2026-05-09-plan-9-rev2-bash-safety-hook.md](docs/sessions/session-17-2026-05-09-plan-9-rev2-bash-safety-hook.md)); LOG.md Recent Sessions + Decisions updated; clean commit on `origin/main`

#### Plan 9 — Allowlist Coverage, Once and For All (2026-05-09 19:05 ET — closed)
- [x] Layer 0: structural audit + add `defaultMode: acceptEdits`, top-level `Read`/`Write`/`Edit`/`WebFetch(*)`, `autoMode.environment.allowNetwork: true`, `$schema`, `Read(**/.env)` deny  *(verified via `jq '.permissions.defaultMode, ."$schema", .autoMode.environment.allowNetwork'`)*
- [x] Layer 1: broaden allow patterns (verification idioms cohort) in `.claude/settings.json`  *(added wget/rsync/npm/pnpm/for/while/if/[/[[/cat/less/more/sed/cmp/yq/python3 -m json.tool/pwd/uptime/whoami; existing curl/jq/grep/head/tail/awk/find/stat already covered)*
- [x] Layer 1 verify: deny list intact; granular sudo allows preserved (no blanket `sudo *` deny); `python3 -m json.tool .claude/settings.json` exits 0  *(deny list 25 entries inc. new `Read(**/.env)`; granular sudo: nginx/systemctl/cp/mv/ln/chmod/chown/tail/cat/grep/sed-n still present)*
- [x] Layer 2: create `scripts/check_allowlist_coverage.sh` and run it clean (no prompts)  *(ran first pass clean — Code's running session picked up the new patterns mid-flight, no restart needed)*
- [x] Layer 3: CLAUDE.md — Allowlist `[x]` rule + general `[x]` evidence rule  *(under "LOG.md and Sessions Logging Protocol" section, after Transcript timestamps)*
- [x] Session file written; LOG.md Recent Sessions updated; Decisions logged; clean commit on `origin/main`  *(see commit hash in session note)*

#### Plan 0 — FR loose ends (2026-05-08 10:05 ET — closed)
- [x] Move `ANTHROPIC_API_KEY` and `OXY_DATABASE_URL` to `/etc/environment` (Option A — `~/.profile` empirically didn't reach non-interactive ssh)
- [x] Extend PATH in `/etc/environment` to include `/home/ubuntu/.local/bin` so `oxy`/`airlayer` resolve in plain ssh
- [x] Remove `export ANTHROPIC_API_KEY=...` line from `~/.bashrc`
- [x] Update [SETUP.md](SETUP.md) §7 (env vars) + §11 (systemd unit env vars + ExecStart path)
- [x] Update [CLAUDE.md](CLAUDE.md) "LLM Configuration" — current `model_ref`/`key_var` schema + two-var contract pointing at SETUP.md
- [x] Close `oxy build` deferred gate (Decisions Log + Blockers Log + MVP 1 caveat removed)
- [x] Flag `:3000` public exposure in Current Status — closes in Plan 1 (Tailscale)
- [x] Broaden `.claude/settings.json` + `settings.local.json` allowlist for `git -C * <write-op> *` and bare `git <write-op> *` patterns; deliberately omit `reset`, `push --force`, `branch`
- [x] Validation gate 1: `ssh oxygen-mvp 'echo $ANTHROPIC_API_KEY | head -c 14'` → `sk-ant-api03-E`
- [x] Validation gate 2: `ssh oxygen-mvp 'echo $OXY_DATABASE_URL'` → `postgresql://postgres:postgres@localhost:15432/oxy`
- [x] Validation gate 3: `ssh oxygen-mvp 'oxy build'` exit 0 (no `bash -ic`)
- [x] Validation gate 4: agent regression check — "How many 311 tickets were filed in 2024?" still returns 113,961

##### Plan 0 amendments — systemd Option (a) + Deliverable 7 allowlist restructure (2026-05-08 10:18 ET)
- [x] SETUP.md §11 systemd unit: Option (a) — `EnvironmentFile=/etc/environment` instead of explicit `Environment=` directives (single source of truth)
- [x] Capture pre-restructure allowlist state in LOG.md Decisions Log (settings.json: 112 allow / 66 git-related, settings.local.json: 51 allow, no deny)
- [x] D7a — `Edit(.claude/settings.local.json)` + `Write(.claude/settings.local.json)` auto-allowed (Code can self-amend)
- [x] D7b — tool-family wildcards: `Bash(git *)`, `Bash(git -C * *)`, `Bash(dbt *)`, `Bash(oxy *)`, `Bash(airlayer *)`, `Bash(python3 *)`, `Bash(duckdb *)`
- [x] D7b — removed redundant per-subcommand entries from settings.local.json (51 → 18 allow entries)
- [x] D7c — added `permissions.deny` array: `git reset`, `git push --force/-f`, `git branch -d/-D`, `rm -rf`, `sudo` (12 entries, both bare-`git` and `git -C`)
- [x] D7d — `python3 -m json.tool` validates both settings.json and settings.local.json
- [x] D7e — CLAUDE.md Rules: one-line allowlist policy referring to settings.local.json (auto) vs settings.json (Gordon-gated)
- [x] D7e — Decisions Log entry for the policy shift
- [ ] D7 validation: in next Code session, confirm a routine command (e.g. `git -C <worktree> commit`) proceeds without prompt; confirm a destructive command (e.g. `git reset --hard`) still prompts. Cannot validate in this session — Code reads allowlist at session start.

#### Tailscale (pulled forward from MVP 3) — Plan 1 in progress
- [x] Install Tailscale on EC2  *(2026-05-08, 1.96.4; `tailscale up --hostname=oxygen-mvp --ssh`; node IP 100.73.216.43; MagicDNS `oxygen-mvp.taildee698.ts.net` resolves)*
- [x] Authenticate Gordon's laptop and EC2 to same Tailnet  *(both visible in `tailscale status`: laptop 100.122.230.71, EC2 100.73.216.43)*
- [x] Repoint local `~/.ssh/config` `oxygen-mvp` alias from public IP → `oxygen-mvp.taildee698.ts.net`  *(2026-05-08; backup at `~/.ssh/config.bak.preTailscale`)*
- [x] Verify SSH works over Tailscale  *(D3 gate: `ssh oxygen-mvp 'echo ok'` → ok; verbose probe confirms `Authenticated to oxygen-mvp.taildee698.ts.net ([100.73.216.43]:22)`)*
- [x] Verify Oxygen :3000 reachable over Tailscale  *(curl from laptop: MagicDNS hostname → 200, Tailnet IP → 200; service bound to 0.0.0.0:3000)*
- [x] Update AWS security group: SSH and :3000 closed to public, port 80 stays open  *(2026-05-08, post-delete probes: Tailnet SSH ok, Tailnet :3000 = 200, public :3000 = curl timeout exit 28, public :80 = 200)*
- [ ] Update SETUP.md, CLAUDE.md, ARCHITECTURE.md to reflect new access pattern  *(also document nginx docroot = `/var/www/somerville` via `sites-enabled/somerville`, NOT `/var/www/html`)*
- [x] D4 — portal `/chat` link decision  *(2026-05-08; hybrid: dropped nav CTA + asset-card link, replaced hero CTA with non-link `Private beta` pill matching nav-badge styling; removed 3 stale `:3000` comments + dead `.nav-cta`/`.hero-cta` CSS; deployed to `/var/www/somerville/index.html`; live portal clean)*

#### dbt docs (production-strength documentation)
- [x] Audit all schema.yml files: every model has description, every column has description (no nulls)  *(2026-05-08 D1)*
- [x] Add bronze model + column descriptions  *(1/1 model + 24/24 cols)*
- [x] Add gold model + column descriptions  *(4/4 models + 47/47 cols)*
- [x] Add admin model + column descriptions  *(D2 — 3/3 models + all cols)*
- [x] Add `dbt docs generate` step to run.sh  *(step 6/7)*
- [x] Configure nginx /docs route to serve dbt/target/  *(alias fixed: dbt 1.11 emits index.html directly to dbt/target/, not a subdir; /home/ubuntu chmod 755 for www-data traversal)*
- [x] Verify /docs renders on portal  *(`curl http://18.224.151.49/docs/index.html` → 200, title "dbt Docs")*

#### Portal pages for trust
- [x] Build /metrics page generator (auto-generated from Airlayer YAML — every measure with definition and expanded SQL)  *(2026-05-08 D3 — `scripts/generate_metrics_page.py`; live at `/metrics`; 2 measures across 4 views)*
- [x] Build /trust page (driven by admin.fct_test_run — last run, pass/fail counts, test details, data freshness)  *(Plan 4 — `scripts/generate_trust_page.py`; live at `/trust`; 36 tests on the latest run; synthetic-fail render check verified green→red→green on 2026-05-09)*
- [x] Update portal/index.html nav: surface /docs, /metrics, /trust alongside /chat  *(Plan 4 — three route links added to `.nav-links`; chat handled via existing hero "Private beta" pill per Session 11/12 decision)*
- [ ] Update portal/index.html copy to reflect analyst persona (engineering-honest, not marketing)  *(Plan 7)*

#### Limitations registry
- [x] Decide location and format (open question in STANDARDS.md)  *(2026-05-08 D0 — Option b: `docs/limitations/` Markdown + YAML frontmatter)*
- [x] Document known 311 data limitations  *(Plan 8 — 10 active entries; index at `docs/limitations/_index.yaml` generated by `scripts/build_limitations_index.py` as run.sh step 9/9)*
- [ ] Surface limitations on /trust page  *(Plan 7 — `/trust` page is admin-DQ-driven today; surfacing limitations is a separate UI pass)*
- [x] Configure Answer Agent to reference limitations when relevant  *(Plan 6 D2 — agent reads `_index.yaml`, matches affects against SQL/cited views, surfaces matches in Citations + Known limitations sections; verified Q4+Q5 of D3 test bench)*

### Documentation — MVP 1 scope sharpening
- [x] Deliverable A: STANDARDS.md written, committed, pushed
- [x] Deliverable B: TASKS.md updates (scope statement, Hardening section, Answer Agent + Sign-off updates, marks done)  *(Plans 6/7/8/5 closed via the rev 2 batch — all relevant rows reconciled)*
- [ ] Deliverable C: LOG.md session entry + Decisions Log + Current Status

### Environment Setup
- [x] Provision EC2 instance (t4g.medium, Ubuntu 24.04 LTS ARM) — IP: 18.224.151.49
- [x] SSH in and install Docker (29.4.3)
- [x] Install Oxygen (0.5.47)
- [x] Install Python 3.12 and create virtual environment
- [x] Install Python packages: `dlt[duckdb]` 1.26.0, `dbt-core` 1.11.9, `dbt-duckdb` 1.10.1
- [x] Initialize GitHub repo and push all project files
- [x] Clone project repo and create `data/` directory
- [x] Set `ANTHROPIC_API_KEY` environment variable
- [x] Configure EC2 to pull from GitHub repo on each session  *(addressed by `CLAUDE.md` "Session Start on EC2" section per Session 5 follow-up)*
- [x] Configure dbt profile (`~/.dbt/profiles.yml`)
- [x] Create `config.yml` for Oxygen (model + database config) — landed in overnight session
- [x] Run `oxy start` and confirm UI loads at port 3000  *(2026-05-08 09:30 ET — Postgres container up, web app on :3000 returns 200, `oxy build` exits 0)*
- [ ] Persist `OXY_DATABASE_URL=postgresql://postgres:postgres@localhost:15432/oxy` so `oxy build` works in any shell  *(2026-05-08 09:32 ET — `oxy start` creates the container but doesn't export the URL; Session 7 worked around it inline. Add to `~/.bashrc` or have `run.sh` source it from `oxy status` output.)*
- [ ] Move `ANTHROPIC_API_KEY` and `~/.local/bin` (oxy, airlayer) exports out of `~/.bashrc` into `~/.profile` (or a sourced env file)  *(2026-05-08 09:32 ET — Ubuntu's default `.bashrc` early-returns for non-interactive shells, so plain `ssh oxygen-mvp 'cmd'` doesn't see the key or the binaries; Session 7 worked around with `bash -ic`. Fix at the source.)*

### Ingestion (dlt)
- [x] Identify Somerville 311 dataset ID on data.somervillema.gov — `4pyi-uqq6`, 1.17M rows, 22 columns
- [x] Profile API: confirmed access, volume per year, classification breakdown, date format
- [x] Write `dlt/somerville_311_pipeline.py` — filesystem destination, Parquet partitioned by year, replace disposition
- [x] Run pipeline and confirm Parquet files land in `~/oxygen-mvp/data/raw/`
- [x] Verify row count — 1,168,959 of 1,168,959 loaded

### Data Profiling & Quality (dbt — admin schema)
- [x] Query raw Parquet files on EC2 and extract full column list with types and sample values  *(via `information_schema.columns` Jinja introspection in fct_data_profile.sql)*
- [x] Create `admin` schema in `dbt_project.yml`  *(already present from Session 5; admin models populate it)*
- [x] Write `admin/fct_data_profile.sql` — column-level profiling, observational only
- [x] Write `admin/dim_data_quality_test.sql` — one row per defined test
- [x] Write `admin/fct_test_run.sql` — one row per test per run, sourced from `raw_dbt_results_raw`  *(landing table; no dbt-managed bronze view — design departure documented in session 13)*
- [x] Write `dlt/load_dbt_results.py` — loads `dbt/target/run_results.json` into `main_bronze.raw_dbt_results_raw` in DuckDB  *(plain duckdb, not dlt — simpler, no metadata-column pollution)*
- [x] Write `run.sh` — single entry point, correct run order, captures dbt test exit code without halting
- [x] Auto-generate baselines on first run — `certified_by = 'system'`  *(17 baselines: 12 yearly + 5 totals; is_incremental filter freezes them)*
- [x] Confirm baseline comparisons fail dbt run on drift beyond tolerance  *(2026-05-09 Plan 3 D3 — synthetic 30% perturbation on 2015 row count baseline; `dq_drift_fail_guardrail` singular test fired; final exit 1; baseline restored; arc preserved in `fct_test_run`)*

### Transformation (dbt — bronze schema)
- [x] Initialize dbt project (`dbt init`) in `dbt/` directory
- [x] Configure `dbt_project.yml` with all four schemas: bronze, silver, gold, admin
- [x] Configure `~/.dbt/profiles.yml` on EC2
- [x] Write `bronze/raw_311_requests.sql` — exact mirror, columns derived from actual Parquet data
- [x] Run `dbt run --select bronze` and confirm model builds
- [x] Run `dbt test --select bronze` — arrival checks only

### Transformation (dbt — gold schema)
- [x] Write `gold/dim_date.sql` — standard date spine
- [x] Write `gold/dim_request_type.sql` — sourced from actual column values
- [x] Write `gold/dim_status.sql` — sourced from actual column values
- [ ] Write `gold/dim_origin.sql` — sourced from actual column values  *(deferred — not in overnight scope)*
- [x] Write `gold/fct_311_requests.sql` — location fields denormalized, no `dim_location` yet
- [x] Run `dbt run --select gold` and confirm all models build
- [x] Add dbt tests: unique + not_null on all surrogate keys
- [x] Add dbt tests: accepted_values on status  *(classification/origin: deferred, surface in semantic layer instead)*

### Docs
- [x] Create `docs/schema.sql` — DDL source of truth (already written, needs committing)

### Portal
- [x] Install nginx on EC2
- [x] Deploy portal index.html at port 80 — verified live at http://18.224.151.49
- [x] Fix portal "Open Chat →" link — Plan 0.5 closed 2026-05-08 11:48 ET (3 hrefs repointed to `http://18.224.151.49:3000/`, nginx `location /chat` block removed; gates 1-4 green; gate 5 = Gordon's browser test)
- [ ] Add /tasks route — rendered TASKS.md
- [ ] Add /erd route — ERD SVG from schema.sql
- [ ] Add /docs route — dbt docs generate output

### Semantic Layer (Airlayer)
- [x] Review Airlayer docs (incl. https://github.com/oxy-hq/airlayer/blob/main/docs/schema-format.md)
- [x] Create `semantics/views/*.view.yml` + `semantics/topics/service_requests.topic.yml` (replaces old single-file `.sem.yml`)
- [x] Define initial views and dimensions (request type, status, opened date, ward, block_code)
- [x] Define initial measures (`total_requests`, `open_requests`)
- [ ] Define `avg days open` measure  *(deferred — needs `most_recent_status_date - date_created_dt` math, MVP 4 metric library)*
- [x] Airlayer schema valid (`airlayer validate` clean) and executes via auto-join (`airlayer query -x` returned 5 rows)
- [x] Confirm Airlayer loads without errors in Oxygen — `oxy validate` clean ("All 5 config files are valid"); `oxy build` deferred to Answer Agent session

### Answer Agent
- [x] Review Answer Agent docs: https://oxy.tech/docs/guide/learn-about-oxy/agents.md
- [x] Create `agents/answer_agent.agent.yml`
- [x] Configure `execute_sql` tool and Airlayer context block
- [x] Configure agent prompt to require SQL, row count, and citations in every response  *(Plan 6 D1 — STANDARDS §4.1; verified across 5/5 test bench)*
- [x] Test with 3–5 sample questions in Oxygen chat UI  *(2026-05-08 09:31 ET — FR smoke test: Test A 2024 = 113,961 ✓ exact match, Test B 2026 "this year" = 48,806 ✓ exact match, agent correctly resolved current year via `year(current_date)`)*
- [x] Confirm agent returns accurate answers  *(both smoke tests exact-match DuckDB ground truth)*
- [x] Test bench: 5 representative analyst questions, verify responses include SQL + row count + citation in every reply  *(Plan 6 D3 — 5/5 trust contract; transcripts in `scratch/plan6_test_bench/q[1-5]_*.md`)*

### MVP 1 Sign-off
- [ ] All checks in [STANDARDS.md](STANDARDS.md) MVP 1 sign-off checklist pass
- [ ] Analyst can ask "How many 311 requests opened in 2024?" and get an answer with SQL, row count, and citation
- [ ] Analyst can ask "Most common request types?" and get an answer with SQL, row count, and citation
- [ ] /trust page shows green for last pipeline run
- [ ] /metrics page lists all current measures with definitions
- [ ] /docs page renders dbt documentation with no missing descriptions

---

## MVP 2 — Visual Knowledge Products
**Goal:** The analyst describes a dashboard in chat; Builder Agent assembles it. Iterates by conversation, not by writing YAML.

- [ ] Review Airapp docs: https://oxy.tech/docs/guide/learn-about-oxy/data-apps.md
- [ ] Create `apps/somerville_dashboard.app.yml`
- [ ] Add chart: requests by type (bar)
- [ ] Add chart: requests over time (line)
- [ ] Add metric: total open requests
- [ ] Confirm agent can trigger dashboard components from chat
- [ ] MVP 2 sign-off: agent generates a chart in response to a chart request

---

## MVP 3 — Governance and Trust
**Goal:** The analyst trusts the underlying data without having to verify it themselves. Verified Queries badges, full medallion architecture, native agent testing.

- [ ] Write Silver model: `models/silver/stg_311_requests.sql`
  - [ ] Normalize field names
  - [ ] Cast types
  - [ ] Deduplicate
  - [ ] Redact PII fields (names, contact info)
- [ ] Promote location to `gold/dim_location.sql`
- [ ] Add dbt tests: unique keys and non-null checks on Silver
- [ ] Add dbt tests: business rule validation on Gold
- [ ] Update Airlayer to point to Gold layer
- [ ] Add Tailscale for access control (replacing open port 3000)
- [ ] MVP 3 sign-off: `dbt test` passes clean, PII confirmed redacted

---

## MVP 4 — Semantic Depth and Sharing
**Goal:** The analyst's findings move from personal to shared via Slack, MCP, A2A, BI tools, and public chat.

- [ ] Audit existing Airlayer metrics — identify gaps
- [ ] Expand `somerville_311.sem.yml` with full metric library
  - [ ] Response time metrics (avg days to close, SLA compliance)
  - [ ] Geographic dimensions (ward, neighborhood)
  - [ ] Department/category breakdowns
  - [ ] Year-over-year comparisons
- [ ] Review Routing Agent docs: https://oxy.tech/docs/guide/learn-about-oxy/routing-agents.md
- [ ] Create `agents/routing_agent.agent.yml` (`type: routing`)
- [ ] Configure routing to dispatch to answer agent
- [ ] Test routing with ambiguous queries
- [ ] MVP 4 sign-off: routing agent correctly dispatches 5 varied test queries
