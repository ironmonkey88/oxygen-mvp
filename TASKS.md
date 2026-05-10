# TASKS.md — Oxygen MVP Task Tracker

> Status markers: `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked
> Claude Code updates this file as work progresses.

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
- [x] Chat UI accessible and answering questions correctly — FR smoke test passed: 2024 full-year (113,961) and 2026 partial-year (48,806) both exact-match against DuckDB ground truth
- [ ] Trust contract on agent (SQL + row count + citations in every response)
- [x] Admin DQ framework in place  *(2026-05-08 — D2 of overnight; 3 admin models, run.sh, load_dbt_results.py; verified across 2 consecutive runs)*

### MVP 2 — Visual Data Product
- [ ] Airapp `.app.yml` with charts

### MVP 3 — Governance Layer
- [ ] dbt Silver model with PII redaction
- [ ] dbt Gold model updated with dim_location
- [ ] Tailscale access control

### MVP 4 — Semantics
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
- [~] Document known 311 data limitations  *(2 seeds: survey-columns-sparse, block-code-padded; more as they're discovered)*
- [ ] Surface limitations on /trust page
- [ ] Configure Answer Agent to reference limitations when relevant

### Documentation — MVP 1 scope sharpening
- [x] Deliverable A: STANDARDS.md written, committed, pushed
- [~] Deliverable B: TASKS.md updates (scope statement, Hardening section, Answer Agent + Sign-off updates, marks done)
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
- [ ] Configure agent prompt to require SQL, row count, and citations in every response  *(extreme trustability — see STANDARDS.md §4.1; deferred — trust contract is a follow-up pass after FR smoke test)*
- [x] Test with 3–5 sample questions in Oxygen chat UI  *(2026-05-08 09:31 ET — FR smoke test: Test A 2024 = 113,961 ✓ exact match, Test B 2026 "this year" = 48,806 ✓ exact match, agent correctly resolved current year via `year(current_date)`)*
- [x] Confirm agent returns accurate answers  *(both smoke tests exact-match DuckDB ground truth)*
- [ ] Test bench: 5 representative analyst questions, verify responses include SQL + row count + citation in every reply  *(deferred — trust contract pass)*

### MVP 1 Sign-off
- [ ] All checks in [STANDARDS.md](STANDARDS.md) MVP 1 sign-off checklist pass
- [ ] Analyst can ask "How many 311 requests opened in 2024?" and get an answer with SQL, row count, and citation
- [ ] Analyst can ask "Most common request types?" and get an answer with SQL, row count, and citation
- [ ] /trust page shows green for last pipeline run
- [ ] /metrics page lists all current measures with definitions
- [ ] /docs page renders dbt documentation with no missing descriptions

---

## MVP 2 — Visual Data Product
**Goal:** Add charts and visual output to the conversational experience

- [ ] Review Airapp docs: https://oxy.tech/docs/guide/learn-about-oxy/data-apps.md
- [ ] Create `apps/somerville_dashboard.app.yml`
- [ ] Add chart: requests by type (bar)
- [ ] Add chart: requests over time (line)
- [ ] Add metric: total open requests
- [ ] Confirm agent can trigger dashboard components from chat
- [ ] MVP 2 sign-off: agent generates a chart in response to a chart request

---

## MVP 3 — Governance Layer
**Goal:** Star schema, PII redaction, data quality guardrails

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

## MVP 4 — Semantics
**Goal:** Rich metric library + Routing Agent

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
