# TASKS.md — Oxygen MVP Task Tracker

> Status markers: `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked
> Claude Code updates this file as work progresses.

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

#### Tailscale (pulled forward from MVP 3)
- [ ] Install Tailscale on EC2
- [ ] Authenticate Gordon's laptop and EC2 to same Tailnet
- [ ] Update AWS security group: SSH and :3000 closed to public, port 80 stays open
- [ ] Verify SSH works over Tailscale
- [ ] Verify Oxygen :3000 reachable over Tailscale
- [ ] Update SETUP.md and CLAUDE.md to reflect new access pattern

#### dbt docs (production-strength documentation)
- [ ] Audit all schema.yml files: every model has description, every column has description (no nulls)
- [ ] Add bronze model + column descriptions
- [ ] Add gold model + column descriptions
- [ ] Add admin model + column descriptions (when admin schema lands)
- [ ] Add `dbt docs generate` step to run.sh
- [ ] Configure nginx /docs route to serve dbt/target/static_index.html
- [ ] Verify /docs renders on portal

#### Portal pages for trust
- [ ] Build /metrics page generator (auto-generated from Airlayer YAML — every measure with definition and expanded SQL)
- [ ] Build /trust page (driven by admin.fct_test_run — last run, pass/fail counts, test details, data freshness)
- [ ] Update portal/index.html nav: surface /docs, /metrics, /trust alongside /chat
- [ ] Update portal/index.html copy to reflect analyst persona (engineering-honest, not marketing)

#### Limitations registry
- [ ] Decide location and format (open question in STANDARDS.md)
- [ ] Document known 311 data limitations
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
- [ ] Query raw Parquet files on EC2 and extract full column list with types and sample values
- [ ] Create `admin` schema in `dbt_project.yml`
- [ ] Write `admin/fct_data_profile.sql` — column-level profiling, observational only
- [ ] Write `admin/dim_data_quality_test.sql` — one row per defined test
- [ ] Write `admin/fct_test_run.sql` — one row per test per run, sourced from `raw_dbt_results`
- [ ] Write `dlt/load_dbt_results.py` — loads `dbt/target/run_results.json` into `raw_dbt_results` in DuckDB
- [ ] Write `run.sh` — single entry point, correct run order, captures dbt test exit code without halting
- [ ] Auto-generate baselines on first run — `certified_by = 'system'`
- [ ] Confirm baseline comparisons fail dbt run on drift beyond tolerance

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
- [!] Fix portal "Open Chat →" link — renders blank page in browser  *(2026-05-08 09:46 ET — nginx `/chat` proxies the SPA HTML but `/assets/*.js` at root hits portal's `try_files` and 404s. WebSocket path likely also affected. Awaiting Chat's call on Option A (drop subpath proxy, link directly to `http://18.224.151.49:3000/`) vs Option B (full nginx subpath rewrite) vs Option C (subdomain). See LOG.md 09:46 ET addendum for details.)*
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
