# CLAUDE.md — Instructions for Claude Code

This file is instructions for Claude Code. For project context, read these files first:
- `ARCHITECTURE.md` — stack decisions, component map, data flow, constraints
- `SETUP.md` — environment setup, install commands, config files
- `LOG.md` — current status, decisions, blockers
- `TASKS.md` — task tracker

---

## What You Are Building

A public-facing analytics platform for Somerville, MA open data, built on Oxygen (oxy.tech).
Users ask natural language questions about 311 service request data via a chat UI.

**Your job:** Configure and wire together Oxygen's components using declarative YAML and SQL.
**Not your job:** Write custom agents, ETL logic, or application code unless Oxygen cannot do it natively.

---

## The Developer

Gordon is an experienced Snowflake/dbt/Looker architect who is new to Oxygen.
- Do NOT explain medallion architecture, semantic layers, dbt patterns, or star schemas — he knows these
- DO explain how Oxygen implements these concepts differently
- Lead with the dbt/Looker analogy, then explain the Oxygen difference

---

## Stack at a Glance

| Layer | Tool |
|---|---|
| Ingestion | dlt |
| Warehouse | DuckDB |
| Transformation | dbt Core |
| Semantic Layer | Airlayer (`.sem.yml`) |
| Q&A Agent | Answer Agent (`.agent.yml`) |
| Routing | Routing Agent (`type: routing`) — MVP 4 only |
| Dashboards | Airapp (`.app.yml`) |

See `ARCHITECTURE.md` for full detail.

---

## Project File Structure

```
oxygen-mvp/
├── run.sh                          ← single entry point — always use this
├── CLAUDE.md
├── ARCHITECTURE.md
├── SETUP.md
├── LOG.md
├── TASKS.md
├── config.yml
├── data/
│   └── somerville.duckdb
├── dlt/
│   ├── somerville_311_pipeline.py
│   └── load_dbt_results.py         ← loads run_results.json → raw_dbt_results
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── bronze/
│   │   ├── silver/
│   │   ├── gold/
│   │   └── admin/                  ← profiling + DQ star schema
│   └── tests/
├── semantic/
│   └── somerville_311.sem.yml
├── agents/
│   ├── answer_agent.agent.yml
│   └── routing_agent.agent.yml
└── apps/
    └── somerville_dashboard.app.yml
```

---

## MVP Sequence — Do Not Skip Ahead

1. **MVP 1** — dlt snapshot → DuckDB → Airlayer → Answer Agent chat UI
2. **MVP 2** — Add Airapp charts and dashboards
3. **MVP 3** — dbt Bronze/Silver/Gold pipeline with PII redaction
4. **MVP 4** — Full Airlayer metric library + Routing Agent

Complete each MVP fully before starting the next.

---

## Task Discipline

Every piece of work requires a task in TASKS.md. This is enforced by a PreToolUse hook that fires before any EC2 command.

**Before starting any work:**
1. Create the task in TASKS.md if it doesn't exist
2. Mark it `[~]` in progress
3. Run the work
4. Mark it `[x]` when done — immediately, not at end of session

Do not batch task updates. Update as you go.

A hook in `.claude/settings.json` will soft-warn before any `ssh oxygen-mvp` command if no `[~]` task exists in TASKS.md.

---

## Rules

- **Oxygen-native first** — use YAML/SQL config before writing any code
- **DuckDB file locking** — dlt, dbt, and Oxygen share one `.duckdb` file; run them sequentially, never concurrently. Order: dlt → dbt → oxy. See `ARCHITECTURE.md`.
- **Airlayer is the semantic source of truth** — never hardcode metrics in SQL or app configs
- **PII redaction in dbt Silver layer** — required before MVP 3 sign-off
- **Flag Oxygen limitations immediately** — surface problems before building workarounds
- **Update TASKS.md** as work completes — `[x]` done · `[~]` in progress · `[!]` blocked
- **Update LOG.md** after completing tasks, making decisions, or hitting blockers

---

## Naming Standards

### Schemas
| Schema | Purpose |
|---|---|
| `bronze` | Raw source data |
| `silver` | Cleaned and typed |
| `gold` | Business-ready |
| `admin` | Infrastructure and profiling |

### Table Prefixes
| Prefix | Schema | Example |
|---|---|---|
| `raw_` | bronze | `raw_311_requests` |
| `stg_` | silver | `stg_311_requests` |
| `fct_` | gold | `fct_311_requests` |
| `dim_` | gold | `dim_date` |
| `fct_` | admin | `fct_data_profile` |
| `dim_` | admin | `dim_data_quality_test` |
| `fct_` | admin | `fct_test_run` |

### Column Conventions
- Snake case everywhere: `request_type`, `opened_dt`
- Primary keys: `[table]_id` e.g. `request_id`
- Surrogate keys (MVP 3+): `[table]_sk`
- Dates/timestamps: `_dt` suffix — `opened_dt`, `closed_dt`
- Booleans: `is_` prefix — `is_open`, `is_active`
- Percentages: `pct_` prefix — `pct_null`, `variance_pct`
- Counts: `_count` suffix — `null_count`, `distinct_count`

---

## Read the Data First

**Before writing any dbt model columns**, query the actual source data on EC2:

```sql
DESCRIBE SELECT * FROM read_parquet('data/raw/somerville_311/**/*.parquet');
SELECT * FROM read_parquet('data/raw/somerville_311/**/*.parquet') LIMIT 5;
```

Never assume column names from API documentation. Always derive from actual data.

---

## Run Order — Always Use run.sh

**Never run dlt, dbt, or oxy commands individually.** Always use:

```bash
./run.sh
```

`run.sh` enforces the correct sequence:
1. dlt ingest
2. dbt run
3. dbt test (captures exit code, does not halt on failure)
4. dlt load_dbt_results.py
5. dbt run --select admin

See `ARCHITECTURE.md` for the full annotated run order.

---

## Data Quality Design

Three separate concerns — do not mix them:

| Concern | Table | Assertional? | Fails run? |
|---|---|---|---|
| Profiling | `fct_data_profile` | No — observational only | Never |
| Baseline comparisons | `fct_test_run` | Yes | Yes, on drift beyond tolerance |
| dbt tests | `fct_test_run` | Yes | Yes, on failure |

- Profiling runs do **not** generate rows in `fct_test_run`
- Baselines are auto-generated on first run with `certified_by = 'system'`
- dbt test results are parsed from `dbt/target/run_results.json` via `load_dbt_results.py`

See `ARCHITECTURE.md` for full table designs.

---

## LLM Configuration

```yaml
# config.yml
models:
  - name: claude
    vendor: anthropic
    model: claude-sonnet-4-6
```

Requires `ANTHROPIC_API_KEY` environment variable. If not set, stop and ask Gordon.

---

## Reference Links

- Oxygen Docs: https://oxy.tech/docs/llms.txt
- Oxygen Agents: https://oxy.tech/docs/guide/learn-about-oxy/agents.md
- Oxygen Routing Agents: https://oxy.tech/docs/guide/learn-about-oxy/routing-agents.md
- Oxygen Semantic Layer: https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer.md
- Oxygen Data Apps: https://oxy.tech/docs/guide/learn-about-oxy/data-apps.md
- Oxygen AWS Deployment: https://oxy.tech/docs/guide/deployment/hands-on/aws.md
- dlt Docs: https://dlthub.com/docs
- dbt Core Docs: https://docs.getdbt.com
- dbt-duckdb Adapter: https://github.com/duckdb/dbt-duckdb
- Somerville Data Portal: https://data.somervillema.gov

---

## LOG.md Logging Protocol

Update `LOG.md` automatically — do not wait for Gordon to ask. This is a hard requirement, not a suggestion.

**When:** After any `[x]` task, after any blocker, after any architectural decision, at end of session. Do not batch — log as you go.

**What:** Session summary, decisions made (also add to Decisions Log table), blockers hit (also add to Blockers Log table), accomplishments.

**Timestamp format:** `YYYY-MM-DD HH:MM ET` — always run `date` to get the exact time. Never use vague terms like "~evening". Gordon is in US Eastern time (ET).

**Format:** Prepend new entries to the Session Log section. Never delete old entries.

**Also update TASKS.md:** Mark tasks `[x]` as they complete. Do not wait until end of session.
