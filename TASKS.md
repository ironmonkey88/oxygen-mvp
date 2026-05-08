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
- [!] `oxy build` exits 0  — *blocked: requires `oxy start` (Docker + Postgres). `oxy validate` passes; flagged for Gordon to decide.*
- [x] `airlayer query ... -x` returns rows (5 rows, auto-join via entity match)
- [x] Commit and push semantic layer

---

## MVP 1 — 1st Data Product
**Goal:** Static data file → DuckDB → Airlayer → Answer Agent chat UI

### Repo Cleanup (Session 5)
- [x] Audit local Mac vs EC2 vs GitHub for missing source files
- [x] Recover `dlt/somerville_311_pipeline.py` into the repo (live EC2 copy)
- [x] Recover `dbt/dbt_project.yml` and `dbt/models/bronze/*` from EC2 backup
- [x] Update `bronze/raw_311_requests.sql` to mirror all 22 source columns per `docs/schema.sql`
- [x] Verify Bronze model builds and 5/5 tests pass on EC2
- [x] Add `dbt/profiles.yml` to `.gitignore`; remove repo-local profile alternative from `SETUP.md`
- [x] Confirm `dim_origin` and `portal/` already present in `ARCHITECTURE.md` and `TASKS.md`

### Environment Setup
- [x] Provision EC2 instance (t4g.medium, Ubuntu 24.04 LTS ARM) — IP: 18.224.151.49
- [x] SSH in and install Docker (29.4.3)
- [x] Install Oxygen (0.5.47)
- [x] Install Python 3.12 and create virtual environment
- [x] Install Python packages: `dlt[duckdb]` 1.26.0, `dbt-core` 1.11.9, `dbt-duckdb` 1.10.1
- [x] Initialize GitHub repo and push all project files
- [x] Clone project repo and create `data/` directory
- [x] Set `ANTHROPIC_API_KEY` environment variable
- [ ] Configure EC2 to pull from GitHub repo on each session
- [x] Configure dbt profile (`~/.dbt/profiles.yml`)
- [x] Create `config.yml` for Oxygen (model + database config) — landed in overnight session
- [ ] Run `oxy start` and confirm UI loads at port 3000  *(needed before `oxy build` validation gate can pass)*

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
- [!] Confirm Airlayer loads without errors in Oxygen — *blocked on `oxy build` Postgres dep*

### Answer Agent
- [ ] Review Answer Agent docs: https://oxy.tech/docs/guide/learn-about-oxy/agents.md
- [ ] Create `agents/answer_agent.agent.yml`
- [ ] Configure `execute_sql` tool and Airlayer context block
- [ ] Test with 3–5 sample questions in Oxygen chat UI
- [ ] Confirm agent returns accurate answers

### MVP 1 Sign-off
- [ ] User can ask "How many 311 requests were opened in 2024?" and get a correct answer
- [ ] User can ask "What are the most common request types?" and get a correct answer
- [ ] No errors in Oxygen logs during normal use

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
