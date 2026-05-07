# LOG.md — Oxygen MVP Captain's Log

> **Source of truth for project status.** Claude Code updates this file automatically after completing tasks, making decisions, or hitting blockers. Do not delete old entries.

---

## Current Status

**Active MVP:** MVP 1 — Static data → DuckDB → Airlayer → Answer Agent chat UI
**Phase:** dbt Bronze complete — `main_bronze.raw_311_requests` view live, 5/5 tests pass. Next: run.sh + Oxygen config
**Last Updated:** 2026-05-07 17:06 ET (Session 4)

---

## Session Log

### Session 4 (cont.) — 2026-05-07 17:47 ET

**Accomplishments:**
- Created `.gitignore` — excludes `.venv`, `dbt/target`, `data/*.duckdb`, `data/raw`, `*.parquet`, `*.pem`, `.oxy/`
- Initialized git repo locally and pushed to `https://github.com/ironmonkey88/oxygen-mvp.git` (main branch)
- Generated ed25519 SSH key on EC2 (`~/.ssh/github_ec2`), added to GitHub as `oxygen-mvp-ec2`
- Backed up EC2 `~/oxygen-mvp` → `~/oxygen-mvp-backup`, cloned repo fresh, restored `.venv`, `data/`, and `dlt/*.py`
- Updated `ARCHITECTURE.md` to reference `docs/schema.sql` as DDL source of truth
- Re-ingested all years (2015–2026) with `$select` on all 22 columns — sparse columns (survey + dept tags) now captured
- Confirmed `union_by_name=true` required for DuckDB glob reads across years with sparse columns

**Decisions Made:**
- GitHub repo: `git@github.com:ironmonkey88/oxygen-mvp.git` — private, owner `ironmonkey88`
- EC2 clones from GitHub as single source of truth; local Mac is authoring environment
- `docs/` folder created for human-readable artifacts; `schema.sql` will be first entry
- Dept tag columns (8 numeric flags) kept as flat booleans on fact table — multi-tag rows exist, no clean dim key
- Survey columns (`accuracy`, `courtesy`, `ease`, `overallexperience`) kept on fact table — sparse strings

**Blockers:** `schema.sql` not yet created — `docs/schema.sql` reference in ARCHITECTURE.md is forward-looking

**Next Action:** Write gold dbt models (dim_date, dim_request_type, dim_status, fct_311_requests) — columns now confirmed

---

### Session 4 — 2026-05-07 17:00 ET

**Accomplishments:**
- Confirmed actual SODA API schema: 10 data columns (not 22 from metadata endpoint — metadata includes system/hidden fields)
- Scaffolded dbt project on EC2: `dbt_project.yml`, `~/.dbt/profiles.yml`, `models/bronze/`, `models/silver/`, `models/gold/`, `models/admin/`
- Wrote `models/bronze/raw_311_requests.sql` — view over `read_parquet('/home/ubuntu/oxygen-mvp/data/raw/somerville_311/**/*.parquet')`
- `dbt debug` confirmed: connection OK, duckdb=1.10.1, path=/home/ubuntu/oxygen-mvp/data/somerville.duckdb
- `dbt run --select bronze` — 1 view created in `main_bronze` schema (0.10s)
- `dbt test --select bronze` — 5/5 tests pass (not_null id, unique id, not_null date_created, not_null classification, accepted_values classification)
- Row count confirmed via DuckDB: 1,168,959 (matches ingestion)

**Decisions Made:**
- DuckDB schema naming: dbt-duckdb prefixes schemas with `main_` — `bronze` becomes `main_bronze`, `gold` becomes `main_gold` etc. This is expected behavior; Oxygen Airlayer will query `main_gold.*`
- Admin schema added with three tables: `fct_data_profile`, `dim_data_quality_test`, `fct_test_run`
- `fct_data_profile` is observational only — does not generate rows in `fct_test_run`
- Baselines auto-generated on first run with `certified_by = 'system'`
- dbt test results captured via `run_results.json` → `load_dbt_results.py` → `raw_dbt_results` → `fct_test_run`
- `run.sh` is the single entry point for all pipeline runs — never run steps manually
- Gold schema: `fct_311_requests` with location denormalized; `dim_date`, `dim_request_type`, `dim_status`; `dim_location` deferred to MVP 3
- Naming standards established: snake_case columns, `_dt` suffix for dates, `is_` prefix for booleans, `pct_` prefix for percentages, `_count` suffix for counts

**Blockers:** None

**Next Action:** Query raw Parquet files for full column list, then build gold models

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

**Next Action:** dbt project init and Bronze model (`~/oxygen-mvp/dbt/`)

**Session 3 Ingestion Notes:**
- Initial run wrote JSONL (dlt default) — fixed by adding `loader_file_format="parquet"` to `pipeline.run()`
- Initial run had 283-row gap — root cause: `T` separator in date filter vs space separator in stored data causing string comparison failures on Jan 1 records. Fixed by switching to `>=`/`<` with space separator matching the stored format
- Final result: 1,168,959/1,168,959 rows, 13 Parquet files across 12 year folders (2015–2026)

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

**Attendees:** Gordon

**Accomplishments:**
- Reviewed project brief (Oxygen_MVP.md), ARCHITECTURE.md, SETUP.md, CLAUDE.md, and Analytics Platform Primer
- Confirmed stack decisions: dlt + DuckDB + dbt Core + Airlayer + Answer Agent + Airapp
- Created LOG.md and TASKS.md (initial versions)

**Decisions Made:**
- See Decisions Log below

**Blockers:**
- None yet

**Next Action:**
- EC2 instance provisioning (see TASKS.md — MVP 1, Task 1)

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-07 | Use dlt for ingestion instead of Airway | dlt is Python-native and mature; Airway not yet evaluated |
| 2026-05-07 | Use dbt Core for transformation instead of Airform | Gordon knows dbt deeply; Airform only added April 2026 — too new |
| 2026-05-07 | Use DuckDB as warehouse | Zero-config embedded OLAP; sufficient for 20k–30k records/year |
| 2026-05-07 | Use Claude Sonnet 4.6 as LLM | Best price/performance for analytics Q&A |
| 2026-05-07 | Deploy on AWS EC2 t4g.medium | Single instance, internal use first |
| 2026-05-07 | Use Ubuntu 24.04 LTS instead of 22.04 | 22.04 not available as free Quick Start AMI in us-east-2; 24.04 compatible with all deps |
| 2026-05-07 | Port 3000 open to all for MVP | Public Somerville open data — low risk; will add Tailscale before MVP 3 |
| 2026-05-07 | LOG.md entries must include date and time | Gordon's explicit requirement for session traceability |
| 2026-05-07 15:50 ET | Use dlt filesystem destination (Parquet) instead of DuckDB destination | Raw data stored agnostically — readable by Snowflake, Spark, editors without DuckDB. No performance penalty for this analytical workload. DuckDB reads via read_parquet(). |
| 2026-05-07 15:50 ET | Partition Parquet files by year (1 file/year) | Clean handoff to Snowflake/other tools; DuckDB can prune partitions on year filters; ~11 files for full history vs 24 unpartitioned chunks |
| 2026-05-07 15:50 ET | Somerville 311 dataset volume is 1.17M rows (~100-115k/year) | Original ARCHITECTURE.md estimate of 20-30k/year was wrong — actual volume 3-5x higher. DuckDB on t4g.medium handles this fine. |
| 2026-05-07 15:50 ET | Load all classifications (Service, Information, Feedback) at Bronze | Don't filter at ingestion; Silver/Gold dbt models decide what's analytically relevant |
| 2026-05-07 15:50 ET | Use id as dlt primary key, merge write disposition | Idempotent re-runs; monthly refreshes upsert only changed records |
| 2026-05-07 16:21 ET | Use `>=`/`<` with space separator for SODA date filters | `date_created` stored as `"YYYY-MM-DD HH:MM:SS"` (space); using `T` separator caused string comparison failures missing all Jan 1 records per year |
| 2026-05-07 16:58 ET | ARCHITECTURE.md expanded with full schema design and DQ framework | Added database schema (bronze/silver/gold/admin), table designs, admin DQ tables, run.sh as single entry point — sourced from design session in Claude chat |
| 2026-05-07 17:06 ET | dbt-duckdb schema naming: bronze → main_bronze | dbt-duckdb prefixes all schemas with `main_`. Expected behavior — Airlayer and Oxygen queries must use `main_gold.*` not `gold.*` |
| 2026-05-07 17:16 ET | Admin schema has three tables: fct_data_profile, dim_data_quality_test, fct_test_run | Separates observational profiling from assertional test tracking |
| 2026-05-07 17:16 ET | fct_data_profile is observational only — no rows in fct_test_run | Profiling is never assertional; only dbt tests and baseline comparisons generate fct_test_run rows |
| 2026-05-07 17:16 ET | Baselines auto-generated on first run with certified_by = 'system' | Eliminates manual seeding; system certifies initial state, human re-certifies after intentional changes |
| 2026-05-07 17:16 ET | dbt test results flow: run_results.json → load_dbt_results.py → raw_dbt_results → fct_test_run | Keeps dbt results in DuckDB for historical tracking without modifying dbt internals |
| 2026-05-07 17:16 ET | run.sh is the sole pipeline entry point | Enforces correct run order (dlt → dbt run → dbt test → load_dbt_results → dbt run admin); prevents partial runs |
| 2026-05-07 17:16 ET | Gold schema: fct_311_requests (location denormalized), dim_date, dim_request_type, dim_status | Location denormalized at MVP 1 for query simplicity; dim_location deferred to MVP 3 |
| 2026-05-07 17:16 ET | Naming standards: snake_case, _dt dates, is_ booleans, pct_ percentages, _count counts | Consistent with dbt community conventions and CLAUDE.md standards |
| 2026-05-07 17:47 ET | GitHub repo: https://github.com/ironmonkey88/oxygen-mvp.git — private, owner ironmonkey88 | Single source of truth; EC2 clones from GitHub, local Mac is authoring environment |
| 2026-05-07 17:47 ET | docs/ folder created for human-readable artifacts; schema.sql is first planned entry | Separates generated/machine artifacts from human-readable design docs |
| 2026-05-07 17:47 ET | Dept tag columns kept as flat booleans on fact table — not normalized to dim | Multi-tag rows exist (up to 3); no clean 1:1 dim key. Only 4,187 of 1.17M rows have tags. |
| 2026-05-07 17:47 ET | Survey columns kept on fact table — sparse, not dim candidates | accuracy/courtesy/ease/overallexperience are sparse Likert strings; no referential integrity |
| 2026-05-07 17:47 ET | union_by_name=true required for all DuckDB glob reads across Parquet years | Sparse columns (survey, dept tags) only present in recent years; without this flag DuckDB uses first file schema |

---

## Blockers Log

| Date | Blocker | Status | Resolution |
|------|---------|--------|------------|
| — | — | — | — |

---

## Accomplishments by MVP

### MVP 1 — 1st Data Product
- [x] Environment set up on EC2
- [x] dlt pipeline ingesting Somerville 311 data
- [x] dbt Bronze model in place (`main_bronze.raw_311_requests`, 5/5 tests passing)
- [ ] Airlayer `.sem.yml` configured
- [ ] Answer Agent `.agent.yml` configured
- [ ] Chat UI accessible and answering questions

### MVP 2 — Visual Data Product
- [ ] Airapp `.app.yml` with charts

### MVP 3 — Governance Layer
- [ ] dbt Silver model with PII redaction
- [ ] dbt Gold model with business logic

### MVP 4 — Semantics
- [ ] Full Airlayer metric library
- [ ] Routing Agent configured
