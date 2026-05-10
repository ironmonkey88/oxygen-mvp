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
| Semantic Layer | Airlayer (`.view.yml`) — standalone Rust CLI + Oxygen built-in engine |
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
├── portal/
│   └── index.html                  ← project portal, served by nginx at port 80
├── docs/
│   └── schema.sql                  ← DDL source of truth for all tables
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
├── semantics/
│   ├── views/
│   │   ├── requests.view.yml
│   │   ├── request_types.view.yml
│   │   ├── statuses.view.yml
│   │   └── dates.view.yml
│   └── topics/
│       └── service_requests.topic.yml
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
- **Allowlist policy:** `.claude/settings.local.json` is auto-editable by Code (per-machine, gitignored). `.claude/settings.json` requires Gordon's confirmation (committed, wider blast radius). Tool families are allowed wholesale (`Bash(git *)`, `Bash(dbt *)`, `Bash(oxy *)`, `Bash(airlayer *)`, `Bash(python3 *)`, `Bash(duckdb *)`); destructive subcommands (`git reset`, `git push --force`, `git branch -d`, `rm -rf`, `sudo`) are explicitly denied and will always prompt.
  - **What belongs in `settings.json` (committed):** patterns useful across sessions or machines — tool-family wildcards (`Bash(<tool> *)`), verification idioms (`Bash(curl *)`, `Bash(jq *)`), deny patterns. Add only when Gordon confirms; this file's blast radius is everyone who clones the repo.
  - **What belongs in `settings.local.json` (per-machine, gitignored):** session-specific or experimental patterns Code adds to unblock its own work. This file accumulates over time; periodic pruning is fine — anything truly load-bearing should already be covered by a tool-family wildcard in `settings.json`.
  - **Periodic prune:** Plan 5 (or any future tech-debt sweep) — diff local against committed, delete anything subsumed by a tool-family wildcard or by a verification-idiom cohort. Reset local to `{"permissions":{"allow":[]}}` if everything is covered.

---

## Bash Safety

The Claude Code permission system evaluates each Bash tool call as a single string. Even when every component is allowlisted, a chain like `wc *.md && echo done && python3 -m json.tool x.json` does not match any single allow pattern and will prompt or deny. A PreToolUse hook (`.claude/hooks/block-dangerous.sh`) enforces this structurally; the rules below describe what to generate so the hook never fires.

- **Never chain commands** with `&&`, `;`, or `||`. One Bash tool call = one command. Issue follow-up commands as separate tool calls.
- **Never use command substitution** (`$(...)` or backticks). Run the inner command first; pass the result into the next call. Arithmetic `$((...))` is fine.
- **Never use process substitution** (`<(...)`, `>(...)`). Write to a temp file instead.
- **Never start a command with `cd`**. Use `git -C <path> ...` or absolute paths.
- **Never use shell redirects to create files** (`echo > file`, `cat <<EOF > file`). Use the Write tool.
- **Never use `export VAR=...`**. Use inline prefixing: `PATH=/opt/homebrew/bin:$PATH command`.
- `for ... ; do ... ; done`, `while ... ; do ... ; done`, and `if ... ; then ... ; fi` ARE allowed — the hook carves out the loop keywords (`do`/`then`/`done`/`fi`/`else`/`elif`) after `;`.
- `sed -i` IS allowed — destructive-deny still bounds the blast radius.

If the hook denies a command, the deny reason in the tool result tells you the fix. Re-issue as separate tool calls in the shape the hook expects.

Note on activation timing: settings are re-read per tool call, so editing `settings.json` mid-session activates the hook for subsequent calls in the *same* session — not just the next one.

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

## Session Start on EC2

EC2 is reached over Tailscale at the alias `oxygen-mvp` (HostName `oxygen-mvp.taildee698.ts.net`). Public SSH and `:3000` are closed at the AWS security group; only port 80 (portal) is publicly reachable. **Tailscale SSH (`--ssh`) is intentionally OFF** — it preempts OpenSSH and silently breaks `/etc/environment` env-var loading. See [SETUP.md §12](SETUP.md) for full Tailnet access setup.

First command on EC2 every session, before any work:

```bash
cd ~/oxygen-mvp && git pull origin main
```

- If pull reports "Already up to date" — proceed.
- If pull pulls commits — review what changed before running any pipeline.
- If pull reports conflicts — stop and ask Gordon.

GitHub `main` is the source of truth. EC2 is downstream of it. Skipping this step is what caused the Session 5 drift (EC2 was 7 commits behind).

---

## Run Order — Always Use run.sh

**Never run dlt, dbt, or oxy commands individually.** Always use:

```bash
./run.sh
```

`run.sh` activates the project venv at the top, then enforces the correct sequence:
1. `python dlt/somerville_311_pipeline.py`
2. `dbt run --select bronze gold`
3. `dbt test --select bronze gold` *(captures exit code, does not halt on failure)*
4. `python dlt/load_dbt_results.py` *(appends run_results.json to `main_bronze.raw_dbt_results_raw`)*
5. `dbt run --select admin`
5b. `dbt test --select admin` *(drift-fail guardrail; captures exit, does not halt — Plan 3 D3)*
6. `dbt docs generate` *(regenerates `/docs`)*
7. `python scripts/generate_metrics_page.py` + deploy to `/var/www/somerville/metrics.html` *(regenerates `/metrics` — Plan 2 D3)*
8. `python scripts/generate_trust_page.py` + deploy to `/var/www/somerville/trust.html` + sync `portal/index.html` *(regenerates `/trust` — Plan 4)*
9. `python scripts/build_limitations_index.py` *(regenerates `docs/limitations/_index.yaml` from `*.md` frontmatter — Plan 8)*

Final exit code = `max(bronze/gold-test exit, admin-test exit)` — any failing test surfaces, but admin tables and the trust page still get populated.

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
  - name: claude-sonnet-4-6
    vendor: anthropic
    model_ref: claude-sonnet-4-6
    key_var: ANTHROPIC_API_KEY
```

Two env vars must be set on EC2 before running Oxygen:

| Var | Used for |
|---|---|
| `ANTHROPIC_API_KEY` | Answer Agent's LLM calls |
| `OXY_DATABASE_URL` | `oxy build` / `oxy serve` connection to the Postgres container that `oxy start` manages (typically `postgresql://postgres:postgres@localhost:15432/oxy`) |

Both live in `/etc/environment` — see SETUP.md §7 for why (`~/.bashrc` and `~/.profile` aren't read by plain non-interactive `ssh ec2 'cmd'`). If either is missing, stop and ask Gordon.

---

## Reference Links

- Oxygen Docs: https://oxy.tech/docs/llms.txt
- Oxygen Agents: https://oxy.tech/docs/guide/learn-about-oxy/agents.md
- Oxygen Routing Agents: https://oxy.tech/docs/guide/learn-about-oxy/routing-agents.md
- Oxygen Semantic Layer: https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer.md
- Airlayer Repo: https://github.com/oxy-hq/airlayer
- Airlayer Schema Format: https://github.com/oxy-hq/airlayer/blob/main/docs/schema-format.md
- Oxygen Data Apps: https://oxy.tech/docs/guide/learn-about-oxy/data-apps.md
- Oxygen AWS Deployment: https://oxy.tech/docs/guide/deployment/hands-on/aws.md
- dlt Docs: https://dlthub.com/docs
- dbt Core Docs: https://docs.getdbt.com
- dbt-duckdb Adapter: https://github.com/duckdb/dbt-duckdb
- Somerville Data Portal: https://data.somervillema.gov

---

## LOG.md and Sessions Logging Protocol

The captain's log is split into two tiers — a bounded LOG.md summary (state) and `docs/sessions/` archive (narrative).

### Where to write what

**`docs/sessions/session-NN-YYYY-MM-DD-slug.md`** — full narrative for the session. Mid-session issues, decisions, debugging steps, evidence, why we chose X over Y. This is the bronze layer. No length cap, but use the structure below to stay compact.

**LOG.md** — single-screen view of project state. Recent 5 sessions get a 5-line summary linking to the full file. Older sessions are listed as one-liners under "Earlier Sessions." Decisions Log is a 30-day rolling window. Blockers Log is open-blockers only.

**`docs/log-archive.md`** — rotation overflow. Decisions older than 30 days, resolved blockers. Append-only.

### Frontmatter (required, controlled vocabulary)

Every session file starts with this exact frontmatter shape. Vocabulary is closed — adding new values requires editing this section, not an inline judgment call.

```
---
session: <integer>
date: YYYY-MM-DD
start_time: HH:MM ET
end_time: HH:MM ET                    # omit if session ongoing
type: <one of: planning | code | hybrid | overnight>
plan: <one of: plan-0 | plan-0.5 | plan-1 | plan-2 | plan-3 | plan-4 | plan-5 | plan-6 | plan-7 | plan-8 | plan-9 | plan-A | none>
layers: [<zero or more of: ingestion, bronze, silver, gold, admin, semantic, agent, portal, infra, docs>]
work: [<one or more of: feature, bugfix, refactor, planning, hardening, infra, docs, test>]
status: <one of: complete | partial | blocked>
---
```

Rules:
- `plan:` is the dominant plan for this session. If a session spans plans, pick primary; mention others in body.
- `layers:` lists data-model layers and infrastructure surfaces touched. Empty array `[]` is valid for pure planning.
- `work:` describes the kind of work done. Multiple values allowed (`[feature, docs]` is common).
- `status:` is the session's outcome, not the plan's outcome.

### Body structure (fixed five sections)

Each section has a target length. If a section runs over, that's a signal to split the session, not to write longer.

```
## Goal
One sentence. What we set out to do this session.

## What shipped
Bulleted list, one line per item. File paths in code spans. Commit hashes
inline (`abc1234`) when present. No prose. Target: 5-15 bullets.

## Decisions
Bulleted list. Each bullet: <decision> — <rationale in one clause>.
Target: 0-8 bullets. If zero, write "None." not an empty section.

## Issues encountered
Only if relevant. For each issue: one line stating what broke, one line of
evidence (curl result, error message, empirical test outcome), one line
stating the resolution. Three lines per issue, not three paragraphs.
Target: 0-5 issues. Omit the section entirely if there were none.

## Next action
One sentence. What the next session should do. If blocked, name the blocker.
```

### Hard rules

- No "Process / lessons" section. Cross-session lessons go in CLAUDE.md or STANDARDS.md, not in a session file.
- No restating decisions verbatim from the Decisions Log table — the table row exists for that.
- No re-narrating what a plan said. Link to the plan if referenced; don't paste it.
- Code blocks for evidence are encouraged (they compress better than prose).
- "Worth flagging" / "Things to know" preambles are banned. If it's worth flagging, it goes in `## Decisions` or `## Issues encountered`. If it's not, cut it.

### LOG.md Recent Sessions summary format

Each summary in LOG.md is exactly this shape, no variation:

```
### Session N — YYYY-MM-DD HH:MM ET — <slug>
[full narrative](docs/sessions/session-NN-YYYY-MM-DD-slug.md)

- **Goal:** <one sentence from the session file>
- **Shipped:** <one sentence summary of what landed>
- **Decisions:** <count, e.g. "3 decisions"> — see Decisions Log
- **Status:** <complete | partial | blocked>
- **Next:** <one sentence>
```

Five lines of summary per session in LOG.md, period. Detail lives in the session file.

### Rotation rules

- When "Recent Sessions" exceeds 5 entries, the oldest moves to "Earlier Sessions" (one-line summary only, retains link).
- When a Decisions Log row is older than 30 days, move it to `docs/log-archive.md`.
- When a blocker is resolved, move the row to `docs/log-archive.md`.

### When to read what

- Session start: read LOG.md and TASKS.md only. Do not read `docs/sessions/` unless investigating a specific past decision.
- "Why did we do X?" investigation: `grep -l "X" docs/sessions/*.md`, then read matching files. Do not pull all of `docs/sessions/` into context.
- Decision archaeology: check inline Decisions Log first; if older, search `docs/log-archive.md` and the indexed session files via the frontmatter `plan:`, `layers:`, `work:` fields.

### Log file size budgets

- LOG.md: target ~150 lines, hard ceiling 250. If approaching ceiling, run rotation manually.
- Individual session files: target ~100 lines, soft ceiling 300. If a session gets too long, split thematically (`session-09a-...md`, `session-09b-...md`) — sessions don't have to be 1:1 with elapsed time.
- `docs/log-archive.md`: no ceiling. Append-only.

### Health check

When LOG.md feels heavy, run:

```bash
wc -l LOG.md docs/sessions/*.md docs/log-archive.md
```

If LOG.md > 250 lines or any session file > 300 lines, rotate.

### Timestamp + TASKS.md hygiene

- Timestamp format: `YYYY-MM-DD HH:MM ET` — always run `date` to get the exact time. Never use vague terms like "~evening". Gordon is in US Eastern time (ET).
- Update TASKS.md as work completes — `[x]` done · `[~]` in progress · `[!]` blocked. Do not wait until end of session.

### Transcript timestamps

In addition to LOG.md timestamps, emit a one-line marker in chat output at the start of each deliverable, at any pause or blocker, and before any long-running command (>~30 seconds). Format: `[YYYY-MM-DD HH:MM ET] <short label>`. Always run `date` to get the actual time. This makes transcript review tractable for sessions that span hours.

### Allowlist `[x]` rule

A `[x]` for any allowlist change requires evidence the change is in `.claude/settings.json` (committed, tracked file), not just `.claude/settings.local.json` (gitignored, scratch). Acceptable evidence in the session note: a one-line confirmation like

    git show HEAD:.claude/settings.json | grep -F 'Bash(curl *)'

showing the pattern is in the committed file. `settings.local.json` is auto-allowed Code scratch space and never satisfies an allowlist `[x]`. This rule exists because the Plan 0 D7b "regression" (Session 14) was caused by `[x]` marks based on `settings.local.json` edits that never mirrored to the committed file.

### `[x]` evidence rule

Every `[x]` in TASKS.md should be backed by one of:
- a commit hash (the change landed in tracked code),
- a verification command output (a test passed, a curl returned 200, etc.),
- a file path + line range (the documentation was written).

Bare `[x]` based on "I did the thing" is not enough. A `[x]` is a claim; claims need evidence, especially for security/permission changes.
