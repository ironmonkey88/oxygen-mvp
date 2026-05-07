# LOG.md — Oxygen MVP Captain's Log

> **Source of truth for project status.** Claude Code updates this file automatically after completing tasks, making decisions, or hitting blockers. Do not delete old entries.

---

## Current Status

**Active MVP:** MVP 1 — Static data → DuckDB → Airlayer → Answer Agent chat UI
**Phase:** Portal live at http://18.224.151.49 — ready to initialize dbt and build models
**Last Updated:** 2026-05-07 18:28 ET (Session 4 — Claude Code)

---

## Session Log

### Session 4 — 2026-05-07 (Claude Code session, ~17:00–18:25 ET)

**Accomplishments (from claude.ai — synced to repo at session start):**
- Designed full database schema: bronze, silver, gold, admin schemas
- Designed admin DQ star schema: `fct_data_profile`, `dim_data_quality_test`, `fct_test_run`
- Profiled actual Parquet columns — confirmed 22 columns, typed and annotated
- Designed all gold models: `fct_311_requests`, `dim_date`, `dim_request_type`, `dim_status`, `dim_origin`
- Wrote `docs/schema.sql` — full DDL, source of truth for all tables
- Established naming standards: snake_case, `_dt`, `is_`, `pct_`, `_count` conventions
- Designed DQ framework: profiling (observational) vs baseline comparisons vs dbt tests (both assertional)
- Designed dbt results capture: `run_results.json` → `load_dbt_results.py` → `raw_dbt_results` → `fct_test_run`

**Accomplishments (Claude Code — committed to GitHub this session):**
- Committed all session 4 files to GitHub `main`: `TASKS.md`, `LOG.md`, `docs/schema.sql`, `portal/index.html`
- Installed nginx 1.24.0 on EC2, enabled as system service
- Created `/var/www/somerville/` directory structure with `/erd` and `/tasks` subdirs
- Configured nginx: root → `/var/www/somerville`, `/docs` → dbt target output, `/chat` → proxy `localhost:3000`
- Deployed `portal/index.html` to `/var/www/somerville/` — confirmed `curl http://localhost` returns HTML
- Rebuilt portal to match Somerville Analytics design: nav with MVP badge, serif hero heading, stats bar, assets 2×2 grid, how-it-works split with stack table, roadmap, footer
- Self-hosted fonts — downloaded latin subset woff2s from Google Fonts API (browser UA required): DM Serif Display, DM Mono, Instrument Sans
- Applied fonts: `DM Serif Display` → hero h1, `DM Mono` → stack layer labels and detail column, `Instrument Sans` → body
- Committed fonts (`portal/fonts/*.woff2`) and updated `portal/index.html` to GitHub `main`
- Updated TASKS.md with Portal section (nginx install and deploy tasks marked `[x]`)

**Decisions Made:**
- Admin schema: `fct_data_profile`, `dim_data_quality_test`, `fct_test_run` — DQ star schema
- `fct_data_profile` is observational only — does not generate rows in `fct_test_run`
- Baselines auto-generated on first run with `certified_by = 'system'`
- dbt test results: `run_results.json` → `load_dbt_results.py` → `raw_dbt_results` → `fct_test_run`
- `run.sh` is the sole pipeline entry point — never run steps individually
- Gold: `fct_311_requests` with location denormalized; `dim_date`, `dim_request_type`, `dim_status`, `dim_origin`
- `dim_location` deferred to MVP 3
- Dept tag columns as flat booleans on fact — multi-tag rows exist, no clean dim key
- Survey columns on fact table — sparse strings, not dim candidates
- Naming standards: snake_case, `_dt` suffix, `is_` prefix, `pct_` prefix, `_count` suffix
- `docs/schema.sql` is DDL source of truth — ERD generated from it, not edited directly
- nginx as portal server: static root + `/docs` alias + `/chat` proxy to Oxygen on port 3000
- Fonts self-hosted in `portal/fonts/` — no external CDN dependency

**Blockers:** None

**Next Action:** Initialize dbt project on EC2 and build bronze model

---

### Session 3 — 2026-05-07 14:25 ET – 15:50 ET

**Accomplishments:**
- Provisioned EC2 instance: `t4g.medium`, Ubuntu 24.04 LTS ARM, `us-east-2` (Ohio)
- Instance ID: `i-0e08479a1e757c118`, Public IP: `18.224.151.49`
- Configured security group: SSH (22) locked to Gordon's IP; port 3000 open to all (MVP decision — public data)
- Installed Docker 29.4.3, Oxygen 0.5.47, Python 3.12.3
- Installed dlt 1.26.0, dbt-core 1.11.9, dbt-duckdb 1.10.1 in `.venv`
- Set `ANTHROPIC_API_KEY` in `~/.bashrc` on EC2
- Configured SSH alias `oxygen-mvp` on local machine (`~/.ssh/config`)
- Configured `.claude/settings.json`: Stop hook for log reminders + permission allowlist
- Explored Somerville SODA API: confirmed access, identified dataset `4pyi-uqq6`, profiled schema and volumes
- Designed dlt pipeline: filesystem destination → Parquet partitioned by year → DuckDB reads via read_parquet()
- Corrected volume estimate: 1.17M total rows, ~100-115k/year (not 20-30k as originally estimated)

**Decisions Made:**
- Use Ubuntu 24.04 LTS instead of 22.04
- Port 3000 open to all for MVP
- PEM key stored at `~/.ssh/oxygen-mvp-server.pem`
- dlt filesystem destination (Parquet) instead of DuckDB destination — storage-agnostic
- Parquet partitioned by year (1 file/year)
- Load all classifications at Bronze; filter in Silver/Gold
- Use `id` as primary key with merge write disposition

**Blockers:** None

**Next Action:** Initialize dbt project and build bronze model

---

### Session 2 — 2026-05-07

**Accomplishments:**
- Written all project files to `/Users/gordonwong/claude-projects/oxygen-mvp/`: CLAUDE.md, ARCHITECTURE.md, SETUP.md, LOG.md, TASKS.md, session-starter.md

**Decisions Made:**
- LOG.md entries must include date and time (not date only)

**Blockers:** None

**Next Action:** EC2 instance provisioning (TASKS.md — MVP 1, Environment Setup)

---

### Session 1 — 2026-05-07

**Accomplishments:**
- Reviewed project brief (Oxygen_MVP.md), ARCHITECTURE.md, SETUP.md, CLAUDE.md, and Analytics Platform Primer
- Confirmed stack decisions: dlt + DuckDB + dbt Core + Airlayer + Answer Agent + Airapp
- Created LOG.md and TASKS.md (initial versions)

**Decisions Made:**
- See Decisions Log below

**Blockers:** None

**Next Action:** EC2 instance provisioning (see TASKS.md — MVP 1, Task 1)

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-07 | Use dlt for ingestion instead of Airway | dlt is Python-native and mature; Airway not yet evaluated |
| 2026-05-07 | Use dbt Core for transformation instead of Airform | Gordon knows dbt deeply; Airform only added April 2026 — too new |
| 2026-05-07 | Use DuckDB as warehouse | Zero-config embedded OLAP; sufficient for 1.17M total records |
| 2026-05-07 | Use Claude Sonnet 4.6 as LLM | Best price/performance for analytics Q&A |
| 2026-05-07 | Deploy on AWS EC2 t4g.medium | Single instance, internal use first |
| 2026-05-07 | Use Ubuntu 24.04 LTS instead of 22.04 | 22.04 not available as free Quick Start AMI in us-east-2; 24.04 compatible with all deps |
| 2026-05-07 | Port 3000 open to all for MVP | Public Somerville open data — low risk; will add Tailscale before MVP 3 |
| 2026-05-07 | LOG.md entries must include date and time | Gordon's explicit requirement for session traceability |
| 2026-05-07 15:50 ET | Use dlt filesystem destination (Parquet) instead of DuckDB destination | Raw data stored agnostically — readable by Snowflake, Spark, editors without DuckDB |
| 2026-05-07 15:50 ET | Partition Parquet files by year (1 file/year) | Clean handoff to Snowflake/other tools; DuckDB can prune partitions on year filters |
| 2026-05-07 15:50 ET | Somerville 311 dataset volume is 1.17M rows (~100-115k/year) | Original estimate of 20-30k/year was wrong — actual volume 3-5x higher |
| 2026-05-07 15:50 ET | Load all classifications (Service, Information, Feedback) at Bronze | Don't filter at ingestion; Silver/Gold dbt models decide what's analytically relevant |
| 2026-05-07 15:50 ET | Use `id` as dlt primary key, merge write disposition | Idempotent re-runs; monthly refreshes upsert only changed records |
| 2026-05-07 | Admin schema: fct_data_profile, dim_data_quality_test, fct_test_run | DQ star schema for tracking test results and baselines |
| 2026-05-07 | fct_data_profile is observational only | Profiling never assertional; only dbt tests and baseline comparisons generate fct_test_run rows |
| 2026-05-07 | Baselines auto-generated on first run with certified_by = 'system' | Eliminates manual seeding; human re-certifies after intentional changes |
| 2026-05-07 | dbt test results: run_results.json → load_dbt_results.py → raw_dbt_results → fct_test_run | Keeps dbt results in DuckDB for historical tracking without modifying dbt internals |
| 2026-05-07 | run.sh is the sole pipeline entry point | Enforces correct run order; prevents partial runs |
| 2026-05-07 | Gold: fct_311_requests with location denormalized, dim_date, dim_request_type, dim_status, dim_origin | MVP 1 model; dim_location deferred to MVP 3 |
| 2026-05-07 | Dept tag columns as flat booleans on fact | Multi-tag rows exist (up to 3); no clean 1:1 dim key. Only 4,187 of 1.17M rows have tags |
| 2026-05-07 | Survey columns kept on fact table | sparse Likert strings; no referential integrity |
| 2026-05-07 | Naming standards: snake_case, _dt, is_, pct_, _count | Consistent with dbt community conventions |
| 2026-05-07 | docs/schema.sql is DDL source of truth | ERD generated from DDL, not edited directly |
| 2026-05-07 | GitHub repo: git@github.com:ironmonkey88/oxygen-mvp.git — private | Single source of truth; EC2 clones from GitHub, local Mac is authoring environment |
| 2026-05-07 18:17 ET | nginx deployed as portal server on port 80 | Serves static portal, proxies /chat to Oxygen port 3000, aliases /docs to dbt output |
| 2026-05-07 18:25 ET | Fonts self-hosted in portal/fonts/ — no CDN | Google Fonts gstatic URLs require browser UA to download; committed woff2 latin subsets to repo |
| 2026-05-07 18:25 ET | Portal design: DM Serif Display hero, DM Mono stack labels, Instrument Sans body | Matches Somerville Analytics mockup provided by Gordon |

---

## Blockers Log

| Date | Blocker | Status | Resolution |
|------|---------|--------|------------|
| 2026-05-07 18:28 ET | Port 80 AWS SG rule added — portal publicly live at http://18.224.151.49 | Resolved | Gordon added inbound HTTP rule in AWS console |

---

## Accomplishments by MVP

### MVP 1 — 1st Data Product
- [x] Environment set up on EC2
- [x] GitHub repo initialized and connected
- [x] dlt pipeline ingesting Somerville 311 data — 1,168,959 rows loaded
- [x] Data model designed — schema.sql written, ERD generated
- [x] nginx installed, portal deployed at http://18.224.151.49 (port 80 pending AWS SG rule)
- [x] Portal designed and fonts self-hosted (DM Serif Display, DM Mono, Instrument Sans)
- [x] Portal verified live in browser at http://18.224.151.49
- [ ] dbt bronze model in place
- [ ] dbt gold models in place
- [ ] Admin DQ framework in place
- [ ] Airlayer `.sem.yml` configured
- [ ] Answer Agent `.agent.yml` configured
- [ ] Chat UI accessible and answering questions

### MVP 2 — Visual Data Product
- [ ] Airapp `.app.yml` with charts

### MVP 3 — Governance Layer
- [ ] dbt Silver model with PII redaction
- [ ] dbt Gold model updated with dim_location
- [ ] Tailscale access control

### MVP 4 — Semantics
- [ ] Full Airlayer metric library
- [ ] Routing Agent configured
