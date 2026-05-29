# CLAUDE.md — Instructions for Claude Code

> **⚠️ Which repo is this? Read before you get confused by recent history.**
> This is **`oxygen-mvp`** — the **Somerville** civic-analytics build (GitHub `ironmonkey88/oxygen-mvp`, live EC2 at `oxygen-mvp.taildee698.ts.net`, the 4-MVP sequence, MVP 2 active).
>
> There is a **separate sibling repo** at `/Users/gordonwong/claude-projects/stack-in-a-box` (GitHub `ironmonkey88/stack-in-a-box`): a **generic, dataset-agnostic analytics-stack template** *extracted from* this project's proven patterns. It is **not** a rename, fork, or pivot of oxygen-mvp — both projects continue independently. stack-in-a-box uses **NYC 311 smoke data** (not Somerville 311), has **its own CLAUDE.md + discipline docs + plan ledger** (its Plan 1, Plan 2, … are unrelated to oxygen-mvp's plans), and has **no EC2 yet** (its Plan 3 provisions the first one).
>
> If recent conversation/session history mentions "stack-in-a-box," "the second batch," NYC 311, or PRs against `ironmonkey88/stack-in-a-box`, **that work belongs to the sibling repo, not here.** Do not import its plan numbers, TASKS/LOG entries, NYC 311 models, or commits into oxygen-mvp. When you're working in `stack-in-a-box`, follow *its* CLAUDE.md; when you're here, follow this one. Don't conflate the two ledgers, MVP/plan sequences, smoke datasets, or EC2 hosts.

This file is instructions for Claude Code. The project has a hierarchy of documents — read in this order:

**Foundational (not project-specific):**
- `docs/Analytics_Platform_Primer.docx` — analytics-platform knowledge the project builds on (Knowledge Products, the Hierarchy of Needs, the Maturity Lifecycle, the medallion architecture, Working Backwards). Read once.

**Convictions (foundational, not authority):**
- `PHILOSOPHY.md` — the *why beneath the why*: three inspirations (Fix The News, Intelligent Optimism, system humanism); the synthesis (an honest full picture is itself service to residents); the institutional precedent (New Urban Mechanics); the engineering discipline (systems-engineering V-model + requirements-first + lifecycle); seven principles each tied to something already in the codebase. Not operational — MVP.md and BUILD.md remain the authorities on scope and "done." Consult §3 and §6 as a tiebreaker when a design question is genuinely open.

**Strategic + construction (project authorities):**
- `MVP.md` — the *why*: protagonist, emotional arc (relief → momentum → ownership → pride → sharing), success test ("you have to try this"), the compass, the portal as opening note, the four-MVP roadmap.
- `BUILD.md` — the *how*: Knowledge Product Pipeline instantiated stage-by-stage, Component Trajectory (best-of-breed today, Oxygen-native at the destination), the four-MVP build sequence with what each retires/produces, disciplines that hold the work together, scope boundaries, glossary.
- `STACK.md` — the *what*: self-contained reference for every Oxygen component (Answer Agent, Builder Agent, Semantic Layer, Data Apps, Verified Queries, workspace modes, etc.) and every external tool (dlt, DuckDB, dbt, nginx, Tailscale, Claude API). Written so Chat understands the technologies without fetching Oxygen docs. Update when a new component is adopted or an Oxygen changelog redefines an existing one.

**Exploratory (orientation, not authority):**
- `PRODUCT_NOTES.md` — exploratory notebook for product ideas surfaced during MVP work. Read for inspiration and orientation, not for planning — MVP.md and BUILD.md remain the authorities. If a notebook idea and an authoritative doc disagree, the authoritative doc wins.

**Operational (this file and downstream):**
- `CLAUDE.md` — operating instructions for Claude Code (this file)
- `ARCHITECTURE.md` — stack decisions, component map, data flow, constraints
- `STANDARDS.md` — "done done" gates by layer; MVP 1 sign-off checklist
- `DASHBOARDS.md` — design standard for every `apps/*.app.yml`: purpose+audience step, three-tier base, recent-situation layer, mandatory trust signals, file contract. Read before building or reviewing a Data App.
- `PROMPTS.md` — Chat-to-Code prompt standard. Defines the two prompt kinds (coding vs information), the canonical header + section shape for each, and the 9-step workflow Code runs on receipt of every prompt. Read on every prompt arrival.
- `SETUP.md` — environment setup, install commands, config files
- `LOG.md` — current status, decisions, blockers
- `TASKS.md` — task tracker (the "Next Focus" section at the top is the active pointer)

---

## What You Are Building

[MVP.md](MVP.md) defines what this project is for — the analyst experience the build commits to creating. [BUILD.md](BUILD.md) defines how every layer is constructed to deliver that experience. Read both before doing substantive work; this file is operational and assumes you have.

**Your job:** Configure and wire together Oxygen's components using declarative YAML and SQL, in service of the MVP.md compass — *does this protect the path through the analyst's emotional arc, or does it leak friction back in?* BUILD.md §3 names what each pipeline stage constructs; BUILD.md §4 names when to migrate custom scaffolding to Oxygen-native; BUILD.md §7 names the disciplines that keep the work coherent.

**Not your job:** Write custom agents, ETL logic, or application code unless Oxygen cannot do it natively. Configuration over custom code is the default per BUILD.md §7.

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
| Semantic Layer | Airlayer (`.view.yml` + `.topic.yml`) |
| Q&A Agent | Answer Agent (`.agent.yml`) |
| Builder Agent | Build mode in Oxygen chat panel (workspace-wide AI copilot, MVP 2+) |
| Routing | Routing Agent (`.agent.yml` `type: routing`) — MVP 4 only |
| Dashboards | Data Apps (`.app.yml`) |

See [STACK.md](STACK.md) for full self-contained definitions of each Oxygen component and external tool. See [ARCHITECTURE.md](ARCHITECTURE.md) for system flow and design decisions.

---

## Project File Structure

```
oxygen-mvp/
├── run.sh                          ← single entry point — always use this
├── CLAUDE.md
├── MVP.md                          ← strategic positioning (read first)
├── BUILD.md                        ← construction logic per layer
├── STACK.md                        ← self-contained component reference
├── STANDARDS.md                    ← done-done gates by layer
├── ARCHITECTURE.md
├── DASHBOARDS.md                   ← Data App design standard
├── PROMPTS.md                      ← Chat-to-Code prompt standard
├── PHILOSOPHY.md                   ← Convictions (not authority — read once)
├── PRODUCT_NOTES.md                ← exploratory notebook
├── SETUP.md
├── LOG.md
├── TASKS.md
├── session-starter.md              ← per-session orientation
├── slack-update-format.md          ← Slack handoff format
├── config.yml
├── portal/                         ← static HTML mirrored to /var/www/somerville
│   ├── index.html                  ← project portal, served by nginx at port 80
│   ├── chat-redirect.html
│   ├── dashboards.html             ← auto-built listing of apps/*.app.yml
│   ├── erd-tier-*.mmd              ← per-tier ERD diagrams
│   ├── somerville-wards-background.svg
│   └── fonts/
├── nginx/
│   └── somerville.conf             ← canonical site config (deploy via SETUP.md §13)
├── systemd/
│   ├── pipeline-refresh.{service,timer}      ← daily 06:00 ET
│   ├── profile-tables.{service,timer}        ← weekly Sun 02:00 ET
│   └── source-health-check.{service,timer}   ← hourly
├── docs/
│   ├── schema.sql                  ← DDL reference loaded as Answer Agent context
│   ├── limitations/                ← Markdown + _index.yaml limitations registry
│   ├── sessions/                   ← per-session narratives (session-NN-*.md)
│   ├── log-archive.md              ← rotated LOG.md overflow
│   ├── oxygen-docs/                ← mirrored Oxygen documentation
│   └── tech-debt-review-2026-05-17.md
├── data/
│   └── somerville.duckdb
├── dlt/
│   ├── somerville_311_pipeline.py
│   ├── somerville_crime_pipeline.py
│   ├── somerville_permits_pipeline.py
│   ├── somerville_traffic_citations_pipeline.py
│   ├── somerville_at_a_glance_pipeline.py
│   ├── somerville_happiness_survey_pipeline.py
│   └── load_dbt_results.py         ← appends run_results.json → raw_dbt_results_raw
├── scripts/                        ← Python build/deploy helpers + dlt helpers
│   ├── pipeline_run_{start,end}.py
│   ├── generate_*.py               ← /metrics, /trust, /profile, /erd, /about, /dashboards
│   ├── profile_tables.py
│   ├── check_profile_staleness.py
│   ├── source_health_check.py
│   ├── ingest_somerville_wards.py
│   ├── build_limitations_index.py
│   ├── build_socrata_inventory.py
│   └── _nav.py                     ← shared nav HTML
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.example.yml        ← template; live profile at ~/.dbt/profiles.yml
│   ├── models/
│   │   ├── bronze/                 ← raw views, _raw tables owned by dlt
│   │   ├── silver/                 ← MVP 3 (placeholder today)
│   │   ├── gold/                   ← facts + dimensions
│   │   └── admin/                  ← profiling + DQ star schema
│   └── tests/
│       └── singular/               ← dq_drift_fail_guardrail.sql
├── semantics/
│   ├── views/                      ← 11 .view.yml files (one per gold table)
│   └── topics/                     ← service_requests, public_safety, built_environment, city_context
├── agents/
│   └── answer_agent.agent.yml      ← Routing Agent lands in MVP 4
└── apps/
    └── rat_complaints_by_ward.app.yml   ← first Builder-CLI dashboard
```

---

## MVP Sequence — Do Not Skip Ahead

The four nested MVPs are defined in [BUILD.md §5](BUILD.md) with analyst outcomes, layers added, configuration produced, scaffolding retired, maturity stage, and demo moment. One-line summaries:

1. **MVP 1 — First Knowledge Product.** ✅ **Signed off 2026-05-11.** Analyst asks a question and gets a verifiable answer with SQL, row count, and citation. Achieved via `oxy start --local` (single-workspace mode); multi-workspace migration deferred to MVP 4.
2. **MVP 2 — Visual Knowledge Products. (active)** The analyst describes a dashboard in chat; Builder Agent assembles it. Iterates by conversation, not by writing YAML.
3. **MVP 3 — Governance and Trust.** The analyst trusts the underlying data without having to verify it themselves. Verified Queries, full medallion, native agent testing.
4. **MVP 4 — Semantic Depth and Sharing.** The analyst's findings move from personal to shared via Slack, MCP, A2A, BI tools, and public chat. Also returns the deployment to multi-workspace mode + Magic Link auth + HTTPS.

Complete each MVP fully before starting the next.

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

## Receiving prompts from Chat

When receiving a prompt from Chat: follow the workflow defined in [PROMPTS.md](PROMPTS.md) §5. Read the header, verify state, branch on kind, and run the steps in order. Coding requests get the full 9-step flow; information requests skip to execution.

Four rules worth internalizing:

- **Code/config changes commit only after their verification gate passes.** Documentation changes (LOG.md, TASKS.md, session notes, handoffs, limitations, glossary edits) commit without a gate — the artifact existing in the committed state is the gate. See PROMPTS.md §5 Step 8.
- **A partial completion with a documented finding outranks a fake-clean `complete`.** Status vocabulary: `complete`, `partial`, `blocked`, `deferred`. Pick the honest one.
- **The report-back (PROMPTS.md §5 Step 9) is the last thing Code emits in the session.** No afterthoughts, no follow-up messages, no "one more thing." If something surfaces after the report, it goes into the next session's report.
- **Prompts may arrive as files in `docs/prompts/plan-NN-<slug>.md`** rather than as pasted text. When they do, execution still follows PROMPTS.md §5, with Step 4's restatement and Step 9's report-back additionally written to the file (Step 9 lands in the sibling `plan-NN-<slug>.report.md`). See PROMPTS.md §5.5 and [`docs/prompts/README.md`](docs/prompts/README.md) for the full convention.

### Autonomous PR-merge policy

<!-- POLICY:autonomous_pr_merge — established Session 47 (2026-05-15); landed in this committed location Session 50 (2026-05-15) -->

**Behavior:** after a piece of work has passed its verification gates and been committed, run `git push` → `gh pr create` → `gh pr merge --merge` in one autonomous flow on this repo. Don't pause to ask "want me to merge?". This is Gordon's standing instruction; landed here so memory drops or fresh-machine sessions inherit it.

**Pause and surface (do NOT auto-merge) when:**
- Status is `partial` or `blocked`
- A live-functional verification gate couldn't be cleared in-session
- A prompt's Halt conditions fired
- PR checks failed
- The PR targets a repo other than this one
- The user has explicitly asked you to pause before merge

**Scope:** this repo's PRs only. Cross-repo PRs, force-merges over failed checks, sending messages (Slack/email/PR comments), and any deploys to systems other than this project's EC2 still require explicit instruction.

**Source of truth:** this section. The per-machine memory file (`feedback_autonomous_execution.md`) is a pointer back here.

---

## Rules

- **Oxygen-native first** — use YAML/SQL config before writing any code
- **DuckDB file locking** — dlt, dbt, and Oxygen share one `.duckdb` file; run them sequentially, never concurrently. Order: dlt → dbt → oxy. See `ARCHITECTURE.md`.
- **Airlayer is the semantic source of truth** — never hardcode metrics in SQL or app configs
- **PII redaction in dbt Silver layer** — required before MVP 3 sign-off
- **Flag Oxygen limitations immediately** — surface problems before building workarounds
- **Update TASKS.md** as work completes — `[x]` done · `[~]` in progress · `[!]` blocked
- **Update LOG.md** after completing tasks, making decisions, or hitting blockers
- **Allowlist policy** — three tiers, never mix them:
  - **`settings.json` (committed, git-tracked):** universal patterns — tool-family wildcards, verification idioms, deny list. Any pattern needed across sessions, machines, or by future teammates belongs here. Changing this file requires a commit (Gordon reviews and merges). Evidence rule: a `[x]` for any allowlist change must include `git show HEAD:.claude/settings.json | grep -F '<pattern>'`.
  - **`settings.local.json` (per-machine, gitignored):** machine-specific only — SSH key paths (`Read(//Users/gordonwong/.ssh/**)`), local MCP tools (`mcp__Claude_in_Chrome__tabs_context_mcp`). Code may self-amend this file freely. Prune it whenever patterns accumulate; anything load-bearing should already be covered by a tool-family wildcard in `settings.json`.
  - **`.claude/worktrees/*/.claude/settings.local.json` (also gitignored):** must mirror canonical `settings.local.json` exactly. Worktree drift is the bug. Never let session-specific patterns (`nc -zv`, `echo "$(git ...)"` with hardcoded paths) accumulate here. When a worktree session needs a new universal pattern, promote it to `settings.json` and mirror across all worktree locals.
  - Destructive subcommands (`git reset`, `git push --force`, `git branch -d`, `rm -rf`, `sudo`) are explicitly denied in `settings.json` and will always prompt regardless of allow list.
  - **Pipe coverage:** `*` in allowlist patterns does NOT match `|`. Piped git commands (`git log | head`) need explicit pipe patterns: `Bash(git * | *)` and `Bash(git -C * * | *)` cover all single-pipe git forms. Double-pipe: `Bash(git * | * | *)`.

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
- **Pipes `|` are allowed** — the hook does not block `|`. However, the allowlist pattern `*` does not match `|`, so piped commands need explicit patterns in `settings.json` (see Allowlist policy above).

If the hook denies a command, the deny reason in the tool result tells you the fix. Re-issue as separate tool calls in the shape the hook expects.

Note on activation timing: settings are re-read per tool call, so editing `settings.json` mid-session activates the hook for subsequent calls in the *same* session — not just the next one.

---

## Known gotchas

- **`git push` fails with `HTTP 400` + `remote end hung up unexpectedly`** on commits containing large binary blobs (PNG screenshots, HTML evidence files, etc.). Fix: bump the per-repo HTTP postBuffer once: `git -C <repo-path> config http.postBuffer 524288000`. EC2's local clone already has this set as of Plan 33; fresh local clones (worktrees, new machines) need to re-set it. Pattern: if a push fails with that exact error on a commit with hundreds of KB or more of binary data, set the buffer and retry — don't compress, don't drop the evidence files.

- **The bash safety hook fires *before* Claude Code's built-in auto-allow.** A command whose leading token would normally auto-allow (`ls`, `grep`, `cat`, `git log`, etc.) will still be hook-denied if the command string contains a hook-blocked operator (`&&`, `||`, naked `;`, `$(...)`, `<()`, `>()`, leading `cd`, leading `export`). Practical implication: don't reach for the `command || fallback` pattern thinking "ls would auto-allow, the `||` should be fine" — the hook gets a vote first. Use separate Bash calls or write the chain to a `scratch/` wrapper. *Inferred during Plan 36's allowlist audit from a real `ls .../worktrees/ 2>/dev/null || echo "no"` denial event; precedence not documented in Claude Code upstream as of 2026-05-22.*

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
./run.sh           # defaults to run_type=manual
./run.sh daily     # what systemd's pipeline-refresh.service passes
```

`run.sh` records run-level observability into
`main_admin.fct_pipeline_run_raw` and enforces the correct sequence:

0. `python scripts/pipeline_run_start.py --run-type=$RUN_TYPE` → `RUN_ID` (Plan 1a)
1. `python dlt/somerville_311_pipeline.py $RUN_ID` *(full pull + merge on `id` into `main_bronze.raw_311_requests_raw`; ~5 min)*
2. `dbt run --select bronze gold`
3. `dbt test --select bronze gold` *(captured-exit; does not halt)*
4. `python dlt/load_dbt_results.py` *(appends run_results.json to `main_bronze.raw_dbt_results_raw`)*
5. `dbt run --select admin`
5b. `dbt test --select admin` *(drift-fail guardrail; captured-exit — Plan 3 D3)*
6. `dbt docs generate` *(regenerates `/docs`)*
7. `python scripts/generate_metrics_page.py` + deploy to `/var/www/somerville/metrics.html` *(regenerates `/metrics` — Plan 2 D3)*
8. `python scripts/generate_trust_page.py` + deploy to `/var/www/somerville/trust.html` + sync `portal/index.html` *(regenerates `/trust` — Plan 4)*
9. `python scripts/build_limitations_index.py` *(regenerates `docs/limitations/_index.yaml` from `*.md` frontmatter — Plan 8)*
10. `python scripts/pipeline_run_end.py --run-id=$RUN_ID --status=$FINAL_STATUS ...` *(UPDATE fct_pipeline_run_raw with status + stage outcomes; Plan 1a)*

A bash `trap on_error ERR` records `run_status='failed'` with the
failing stage name if any non-test stage halts. Final exit code =
`max(bronze/gold-test exit, admin-test exit)` — any failing test
surfaces, but admin tables, the trust page, and the run-end record
still get populated.

**Plan 1b notes.** After adding, dropping, or significantly modifying
a dbt model (`dbt/models/**/*.sql` or column descriptions in
`dbt/models/*/schema.yml`), manually regenerate column profiles so
`/profile` reflects the new schema immediately:

```bash
.venv/bin/python scripts/profile_tables.py
.venv/bin/python scripts/generate_profile_page.py
```

The next `./run.sh` would catch it within 24 hours via the staleness
check (stage 9b), but explicit invocation keeps the portal in sync
during active development. dbt's own `schema.yml` files are NEVER
touched by the profile pipeline — they remain hand-written editorial
content. Profile data lives in `main_admin.fct_column_profile_raw`
and is surfaced only on the `/profile` portal route.

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
  - name: claude-opus-4-7
    vendor: anthropic
    model_ref: claude-opus-4-7
    key_var: ANTHROPIC_API_KEY
```

The Answer Agent migrated from Sonnet 4.6 to Opus 4.7 on 2026-05-11 (TASKS.md MVP 1.5 row, commit `a5853d0`). The driver was SPA rate-limit headroom — Opus 4.7 carries a much larger tokens/min ceiling, which the multi-turn SPA chat path was tripping under Sonnet. Trust contract behavior and the 5-question CLI bench were re-verified post-migration.

Two env vars must be set on EC2 before running Oxygen:

| Var | Used for |
|---|---|
| `ANTHROPIC_API_KEY` | Answer Agent's LLM calls |
| `OXY_DATABASE_URL` | `oxy build` / `oxy serve` connection to the Postgres container that `oxy start` manages (typically `postgresql://postgres:postgres@localhost:15432/oxy`) |

Both live in `/etc/environment` — see SETUP.md §7 for why (`~/.bashrc` and `~/.profile` aren't read by plain non-interactive `ssh ec2 'cmd'`). If either is missing, stop and ask Gordon.

---

## Reference Links

**Local mirror first.** Oxygen's documentation is mirrored in this repo at [`docs/oxygen-docs/`](docs/oxygen-docs/) (see [README](docs/oxygen-docs/README.md) for structure + refresh procedure). Prefer the local copy for grep/read — it's offline, version-controlled, and the same snapshot Chat sees via project knowledge. The web URLs below are the canonical sources; consult them when something might have changed since the mirror was last refreshed.

### Oxygen source (private, gh-authenticated)
- Oxygen runtime source: https://github.com/oxy-hq/oxygen-internal — use this for behavior questions where docs are ambiguous or stale. The `oxy` binary on EC2 reports its build commit via `/api/health` (`build_info.git_commit`).
- Oxygen Claude Code skills: https://github.com/oxy-hq/skills — official skill recipes for using Oxygen from Claude Code; worth a look before writing custom slash commands.

### Oxygen docs (web canonical)
- Oxygen Docs index (AI-friendly): https://oxy.tech/docs/llms.txt (also mirrored at [`docs/oxygen-docs/llms.txt`](docs/oxygen-docs/llms.txt))
- Welcome: https://oxy.tech/docs/guide/welcome
- Agents: https://oxy.tech/docs/guide/learn-about-oxy/agents.md
- Routing Agents: https://oxy.tech/docs/guide/learn-about-oxy/routing-agents.md
- Semantic Layer: https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer.md
- Data Apps: https://oxy.tech/docs/guide/learn-about-oxy/data-apps.md
- AWS Deployment: https://oxy.tech/docs/guide/deployment/hands-on/aws.md
- `oxy` CLI reference: https://oxy.tech/docs/guide/reference/oxy-commands.md
- Environment variables: https://oxy.tech/docs/guide/reference/environment-variables.md

### Related projects
- Airlayer Repo: https://github.com/oxy-hq/airlayer
- Airlayer Schema Format: https://github.com/oxy-hq/airlayer/blob/main/docs/schema-format.md
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

### Verification gates for `[x]` ticks

Extends the `[x]` evidence rule for boxes whose claim is about *behavior at a point in time*, not about an artifact existing in the repo.

Distinguish two kinds of boxes:

- **Static-artifact boxes** — the satisfying state is a file, a config, a description in `schema.yml`, a deny pattern in `settings.json`. These can be ticked once on a commit hash and stay ticked until the artifact changes.
- **Live-functional boxes** — the satisfying state is something running correctly: "chat answers correctly", "trust contract on the agent", "/trust page is green", "`./run.sh` end-to-end". These can regress silently between sessions — the artifact didn't change, but the runtime did.

Rules for live-functional boxes:

1. The `[x]` must reference a verification command (or curl, or query) that can be re-run later. Pasting the output once is fine; what matters is that future-Code can re-run the same command and check the same shape.
2. At MVP sign-off — for any MVP, not just MVP 1 — every live-functional box in STANDARDS.md §6 must be re-verified *in the sign-off session*. Inherited ticks from earlier sessions are not sufficient. The cost of re-running a curl or an `oxy run` is seconds; the cost of false-green at sign-off is months of trust debt.
3. When in doubt, re-run. If a box describes something the runtime is responsible for, the verification is cheap and should be habit, not exception.
4. STANDARDS §6's `/chat` row (or any "Routes live: X" row where X is gated by org/workspace/auth state) requires either a real UI walkthrough or an explicit re-interpretation note recorded inline next to the `[x]`. "Satisfied by a private-beta pill on the portal" is one valid re-interpretation; using it silently is not.
5. For gates that depend on visual / SPA-mediated / client-rendered surfaces, use `scripts/rendered_page.py` — `test_page()` for pass/fail assertions, `review_page()` for grounded reviews. See STANDARDS.md §8 "Rendered-page verification" for usage. Plan 32's halt was the cost of not having this helper: the diagnosis was based on the source file rather than the rendered DOM, so the fix landed in the wrong place. The retrospective principle "verify the rendered surface, not the artifact one level removed" now has automation; for any live-functional gate touching visual output, prefer it over `curl` + grep. **For multi-element targets** (dashboards with many panels, etc.), pass `targets_selector="..."` (CSS selector or list) to `review_page()` — Plan 39 added this; default `None` preserves the original back-link probe.

Why this exists: Session 22 found Oxygen's web-UI org state empty despite STANDARDS §5.8 row 2 (`Routes live: /chat`) being `[x]` and TASKS.md row 25 ("Chat UI accessible and answering questions correctly") being `[x]` with an exact-match 113,961 / 48,806 quote from Session 7. Both ticks survived through Sign-off Sweep (Plan 7) without anyone re-verifying that the SPA chat path actually worked end-to-end; the rows were interpreted as covered by CLI evidence (`oxy run`) and a "Private beta pill" on the portal. That interpretation may be right or wrong, but it should be on the page next to the tick, not in a session note three days back.
