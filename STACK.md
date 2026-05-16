# STACK.md — Technology Reference

The canonical "what is X, what does it do, where does it sit" for every
component this project uses. Written to be **self-contained** — Chat
cannot fetch URLs, so every definition here is full prose, not a pointer.

**When to update:** any plan that introduces a new Oxygen component or
external tool updates the relevant section here as part of close-out.
Same discipline as LOG.md updates.

**Reading order:**
- §1 Oxygen components — native to Oxygen, what we configure
- §2 External tools — what we use that isn't Oxygen
- §3 Pipeline conventions — schema/table/column naming
- §4 Data sources — what we ingest

---

## 1. Oxygen components

### 1.1 Oxy CLI / runtime

**What it is:** The Oxygen runtime, distributed as a single binary `oxy`.
Reads a workspace directory (`config.yml` + agents/ + semantics/ + apps/
+ etc.), brings up a PostgreSQL service (Docker-managed by default), and
serves a web SPA + REST API on port 3000. Sees the workspace as the unit
of orchestration.

**Why it matters:** Replaces a half-dozen tools that an analytics team
would otherwise wire together by hand (chat UI + agent runtime + semantic
layer engine + dashboard renderer + governance UI).

**Key commands:**
- `oxy validate` — schema-check every YAML file in the workspace; exits 0
  if all config is valid. Catches typos before runtime.
- `oxy run <path>` — execute an agent, workflow, or data-app file from
  the CLI. Useful for headless smoke tests.
- `oxy build` — generate vector embeddings for routing agents and Verified
  Queries. Required before routing agents work. Requires PostgreSQL up.
- `oxy start` / `oxy serve` — deployment commands; see §1.2.

**Used in this project:** All MVPs. Daily `./run.sh` validates the
workspace as part of admin DQ; agent answers run through `oxy run` for
the headless test bench.

---

### 1.2 Workspace modes

**What they are:** Three documented deployment shapes (per the 2026-04-09
changelog), distinguished by whether the runtime manages PostgreSQL
locally and whether the UI exposes multi-workspace switching.

| Mode | Command | What it does | Auth |
|------|---------|--------------|------|
| **Local machine** | `oxy start` | Single workspace at `./`. Docker-managed PostgreSQL container. Onboarding wizard if no projects detected. Magic Link auth. | Magic link |
| **Remote single-workspace** | `oxy serve --local` | Single fixed workspace, embedded PostgreSQL on disk (no Docker). Targeted at VMs and containers. | Guest |
| **Cloud / multi-workspace** | `oxy serve` | Multi-tenant: users import repos from GitHub, switch between workspaces via UI, members + roles. Requires external PostgreSQL and a GitHub App. | Magic link + workspace RBAC |

**Project-specific finding (Session 25, 2026-05-11):** This project runs
`oxy start --local` on EC2, which sits between the documented "Local
machine" and "Remote single-workspace" modes — it uses the `oxy start`
entry point but with the `--local` flag that forces single-workspace +
guest-auth + reads the workspace path directly. The multi-workspace
onboarding wizard (the default `oxy start` UI flow) requires fresh
CSV/Parquet uploads into a new `.db/` directory and offers no path for
pointing at an existing populated DuckDB file — making `--local` the
right mode for users who already have a built warehouse.

**MVP migration path:** MVPs 1–3 use `oxy start --local`. MVP 4 returns
to multi-workspace mode (`oxy serve`) because Magic Link auth, Slack/MCP
sharing surfaces, and workspace RBAC live there.

---

### 1.3 Semantic Layer (Airlayer)

**What it is:** Oxygen's declarative business-logic layer. Translates
raw warehouse tables into business concepts that agents can reason about
without needing to see SQL schemas. Defined in YAML across two file
types: `.view.yml` (one per logical model) and `.topic.yml` (one per
subject area, groups related views).

**Why it matters:** Without the semantic layer, the Answer Agent would
have to read raw DDL and guess at relationships. With it, the agent
queries against named entities and pre-defined measures — and every
team member queries the same definitions.

**Four core concepts:**
- **Views** — logical data models. Each view defines a `table` (or
  custom SQL), the entities the view exposes, and the available
  dimensions and measures.
- **Entities** — distinct objects (customers, requests, requests_types).
  Used for automatic relationship discovery and intelligent joins
  between views.
- **Dimensions** — attributes for grouping/filtering/segmenting
  (request status, ward, opened year).
- **Measures** — aggregations and metrics (`total_requests`,
  `open_requests`, `avg_days_to_close`).

**Two formats:** the rich `.view.yml`/`.topic.yml` format above, and a
lighter `.schema.yml` format ("Semantic Model") for simpler use cases.
This project uses the rich format.

**Project files:** `semantics/views/{requests,request_types,statuses,dates}.view.yml`
+ `semantics/topics/service_requests.topic.yml`.

**Common gotcha:** Entity keys must also be declared as dimensions —
not implicit. `airlayer validate` catches this.

---

### 1.4 Answer Agent

**What it is:** A prompted LLM agent that answers data questions. Defined
in `.agent.yml` files. The agent reads its `system_instructions`, has
access to `tools` (most importantly `execute_sql`), can be given
`context` files (typically the semantic layer + a limitations index),
and uses a configured `database`. The "default" agent type — `.agent.yml`
files with no `type:` line are Answer Agents.

**Why it matters:** This is the primary analyst-facing surface in MVP 1.
The trust contract — every reply contains SQL + row count + citations
+ known limitations — is enforced via `system_instructions` prose.

**Key components (per Oxygen docs):**

| Component | Required | What it does |
|-----------|----------|--------------|
| `model` | yes | LLM model name (defined in `config.yml`) |
| `system_instructions` | yes | The agent's prompt |
| `context` | no | Files injected into the prompt (e.g., semantic layer YAML, limitations index) |
| `tools` | no | What the agent can call (e.g., `execute_sql`) |
| `database` | no | Default database for `execute_sql` (from `config.yml`) |
| `variables` | no | Typed input vars with JSON-Schema validation |

**UI surface:** The chat panel's "Ask mode," plus the Procedures/Agents
browser where Answer Agents are listed and can be opened directly.

**Project file:** `agents/answer_agent.agent.yml`. Trust contract is
prompt-only; Oxygen's runtime renders the `execute_sql` artifact (SQL
+ result table) natively, the rest (row count line, citations section,
limitations section) is enforced by prose in `system_instructions`.

**Used in this project:** MVP 1.

---

### 1.5 Routing Agent

**What it is:** A special agent type (`type: routing` in `.agent.yml`)
that acts as a dispatcher. It analyzes incoming questions, finds the
best matching route via vector embeddings (semantic search), forwards
the request to a downstream Answer Agent, workflow, or `.sql` file,
and optionally synthesizes the result.

**Why it matters:** Beyond MVP 1, the project will have multiple
specialized Answer Agents (one per topic, say). A Routing Agent in
front of them lets the analyst ask anything without picking a target
manually.

**Key mechanism:** Each Routing Agent maintains its own vector DB
named `{agent_name}-routing` in LanceDB. `oxy build` populates it.
Routes are specified as a list in the YAML — files or glob patterns
like `agents/*.agent.yml` or `workflows/*.workflow.yml`.

**Used in this project:** MVP 4. Not deployed yet.

---

### 1.6 Agentic Agent

**What it is:** A higher-level agent type (`.agentic.yml`) that
implements a Finite State Machine for multi-step reasoning. Unlike
Answer Agents (one-shot Q&A) and Workflows (fixed task sequences),
agentic agents have explicit states the agent transitions between
autonomously based on its reasoning. Introduced 2026-04-02.

**Why it matters:** Use case is interactive exploration where the agent
needs to plan, query, reflect, and revise — not just answer-a-question.

**Related but distinct file type:** `.aw.yml` (Agentic Workflows) — same
FSM mechanic but described as workflows-with-agency rather than agents.
Likely consolidating over time; for now the docs distinguish them.

**Used in this project:** Not in MVPs 1–4 as currently scoped. Listed
here so future plans don't conflate Agentic Agents with the simpler
Answer Agent.

---

### 1.7 Workflows

**What they are:** Deterministic sequences of tasks (`.workflow.yml`).
Each task is either a deterministic command (e.g., `execute_sql` with a
named SQL query) or an agent call with a prompt. Outputs flow forward
via Jinja references — `{{ name_of_task }}`. DAG-shaped, fixed order.

**Why it matters:** Workflows are the right shape for predictable
batch pipelines (e.g., a nightly report generator). They're what you'd
build if the steps don't need agent autonomy.

**Used in this project:** Not in MVPs 1–4 as currently scoped. The
project's `./run.sh` is a shell-script equivalent to a workflow; could
migrate when Oxygen's workflow runner matures.

---

### 1.8 Builder Agent

**What it is:** An AI copilot that reads, modifies, and iterates on
Oxygen project files through an AI-driven pipeline. Workspace-wide —
edits semantic-layer YAML, SQL files, dbt configs, agent definitions,
and Data Apps. Built on the same FSM framework as agentic agents
(suspension, tool use, result interpretation).

**Why it matters:** Builder Agent is the construction interface from
MVP 2 onward. The analyst describes what they want in plain English;
Builder writes the YAML, runs it to validate, and refines. Replaces
hand-editing of `.view.yml`, `.app.yml`, etc.

**UI surface:**
- The chat panel's **"Build mode"** (alongside "Ask mode")
- A dedicated **Builder Dialog** with an Auto-approve toggle
- A **Builder follow-up input** for iteration

**Key tools (per 2026-05-07 changelog):**
- `run_app` — executes a Data App by path, feeds structured results
  back as context for the next step (enables build → test → refine
  loops on dashboards)
- `read_file` — raw file content, capped at 100k chars
- File-edit tools with HITL approvals via `FileChangePending` events;
  sequential per-file confirmations on batched writes (rejecting one
  file no longer blocks the others)
- 15+ dbt-aware tools: `run_dbt_models`, `test_dbt_models`,
  `compile_dbt_model`, `get_dbt_lineage`, `init_dbt_project`, etc.

**Typical workflow:**
1. Analyst: "Show me service request volume by ward, monthly"
2. Builder: drafts `.app.yml` + writes SQL → `read_file` → presents
   for HITL approval
3. Analyst: approves; Builder calls `run_app` → reads chart result
4. Analyst: "Add a drill-down on top categories"
5. Builder edits the same file → re-runs → loops

**What it is NOT:** A narrow dashboard constructor. Easy mistake —
MVP.md's framing emphasizes the dashboard-from-conversation outcome,
but Oxygen's definition is broader: workspace-wide file editor that
*happens* to make dashboards one of its common workflows.

**Documentation gap:** Builder Agent has no `learn-about-oxy/builder-agent.md`
page in Oxygen's canonical guide. The only authoritative source is
three changelog entries: 2026-04-09 (intro), 2026-04-16 (smarter file
edits, prompt improvements), 2026-05-07 (major upgrade — `run_app`,
sequential confirmations, dbt prompt guidance, conversation-history
fix). A project-side gap-fill is this section.

**Used in this project:** MVP 2 (first Data App via conversation),
likely MVP 3 (Verified Queries modifications).

**Pre-flight unknown:** Whether Builder is fully reachable in
`oxy start --local` mode is not yet verified empirically. First MVP 2
pre-flight task.

---

### 1.9 Data Apps

**What they are:** Configuration-based dashboards (`.app.yml`) — SQL
queries (`tasks`) feeding visualization components (`display`).
Renders interactive dashboards in the SPA without any custom frontend
code.

**Anatomy:**

| Component | Required | What it does |
|-----------|----------|--------------|
| `name` | yes | Unique identifier |
| `description` | no | Brief purpose |
| `tasks` | yes | SQL queries (named) that prep data |
| `display` | yes | Visualization components rendering the data |

**`tasks` shape:** Each task has `name`, `type` (currently only
`execute_sql`), `database`, and either `sql_query` (inline) or
`sql_file` (path). Optional `variables`, `cache`, `export`.

**How they get run:**
- From the SPA: open the workspace's app browser at
  `http://oxygen-mvp.taildee698.ts.net:3000/apps/<name>`
- From Builder Agent (CLI or SPA): the agent reads the app file and
  runs individual task SQL via `execute_sql`. In `oxy 0.5.47` there
  is no dedicated `run_app` tool surface — Builder verifies app
  execution by re-running each task's SQL. The MVP 2 "build → run →
  refine" loop happens conversationally rather than via a single
  tool call.
- `oxy validate --file apps/<name>.app.yml` confirms YAML structure
  but does not render. There is **no `oxy run` path for `.app.yml`**
  in `oxy 0.5.47` — `oxy run` accepts only `.sql`, `.procedure.yml`,
  `.workflow.yml`, `.automation.yml`, `.agent.yml`, and `.aw.yml`.
  See `docs/limitations/dashboard-render-spa-only.md`.

**Common gotcha:** `oxy build` (vector embeddings for routing) is NOT
how you render Data Apps. Open the SPA's app browser instead.

**Used in this project:** MVP 2 (first Data App), MVP 4 (full library).

---

### 1.10 Verified Queries

**What they are:** Pre-written `.sql` files in the workspace that the
analytics agent executes verbatim — bypassing LLM SQL generation
entirely. Discovered automatically alongside procedures and workflows
(no extra config). Results are flagged with a **verified badge** in
the UI so downstream consumers can distinguish them from LLM-generated
answers. Introduced 2026-05-07.

**Why it matters:** For high-stakes or frequently-asked questions, the
agent picks a vetted, human-authored SQL file over generating new SQL.
The answer is reproducible and audit-friendly.

**Discovery:** The agent uses the same semantic-search mechanism as
routing — `.sql` files alongside procedures/workflows are candidates
when the agent selects the best way to answer a question.

**Used in this project:** MVP 3 (governance + trust).

---

### 1.11 SQL Modeling (Airform — native dbt-style)

**What it is:** Oxygen's built-in dbt-compatible SQL modeling layer.
Place dbt projects under `modeling/<project-name>/` in the workspace;
Oxy auto-discovers them. No separate `dbt` CLI or Python environment
required at runtime — Oxy executes the models directly against any
database in `config.yml`. Powered internally by Airform (a separate
oxy-hq repo). Introduced 2026-04-30; substantial dbt-tool additions
in 2026-05-07's Builder release.

**Why it matters:** Future migration path off the external `dbt`
binary this project currently uses. Removes a dependency; brings
modeling under the same workspace + IDE umbrella as everything else.

**Configuration:** Each project needs an `oxy.yml` next to
`dbt_project.yml` that maps dbt target names → Oxy database names
from `config.yml`. Oxy validates type compatibility (snowflake
target → Snowflake database) before any run.

**Used in this project:** Not yet. The project ships with external
dbt Core (see §2.3). Migration to Airform is one of the BUILD.md §4
component-trajectory destinations — defer until Airform proves out at
this project's scale.

---

### 1.12 IDE / Developer Portal

**What it is:** The Oxygen web SPA at port 3000. Browser-based IDE
for editing workspace files, running queries, viewing semantic-layer
graphs, opening Data Apps, chatting with agents (Ask + Build modes),
and inspecting modeling runs. Powered by the same `oxy` binary that
serves the API.

**Why it matters:** The IDE is how Builder Agent's HITL approvals
surface; how `/profile` and `/erd` data become visible if Oxygen
chooses to render them natively; and the eventual home for everything
this project currently builds custom (portal pages, Data Apps).

**Sub-surfaces named in changelogs:**
- Procedures / Agents browser (lists Answer + Routing agents)
- Chat panel (Ask + Build modes)
- Modeling section (dbt projects, model runs, lineage graphs)
- Settings dialog (Notion-style, single dialog as of 2026-05-07,
  scoped to org-level vs workspace-level with local-mode hiding
  org-only sections)
- App browser (runs `.app.yml` files)
- Workspace switcher (multi-workspace mode only)

**Used in this project:** MVP 1 (chat panel, Ask mode); MVP 2 (chat
panel Build mode + Data App rendering).

---

### 1.13 Slack Bot (Universal, multi-tenant)

**What it is:** A single shared Slack app that any Oxygen organization
can connect to via OAuth (introduced 2026-04-30). Per-thread workspace
+ agent selection through a Claude-style Block Kit picker. Slack users
match to Oxy accounts by email (magic-link fallback when email match
fails). Per-thread context — each conversation remembers which
workspace and agent were selected. Bot tokens stored per-organization
with encryption. Chart images uploaded directly to Slack via
`files.uploadV2`.

**Why it matters:** The "make sharing easy" stage of the Knowledge
Product Pipeline. Analyst's findings move from the Oxygen SPA into
the team's chat tool without any custom integration work.

**Auth requirement:** Multi-workspace mode (`oxy serve`). The Slack
bot is per-organization, so single-workspace `--local` mode wouldn't
benefit.

**Used in this project:** MVP 4.

---

### 1.14 MCP Server

**What it is:** Oxygen exposes its agents and data over the Model
Context Protocol (MCP), letting other MCP-compatible clients (Claude
Desktop, Claude Code, Cursor, etc.) talk to Oxy agents as tools.
Per-organization. Mentioned in welcome.md and integrated into the
April 30 Oxygen rebrand pass.

**Why it matters:** The "share with arbitrary AI tools" stage.
Without MCP, the agent only lives in the Oxy SPA + Slack. With it,
any MCP-aware tool becomes a surface.

**Used in this project:** MVP 4.

---

### 1.15 A2A Protocol

**What it is:** Agent-to-Agent protocol — referenced in MVP.md as
one of the MVP 4 sharing surfaces. Lets other agentic systems
(another Oxygen org, a custom agent) call into this project's
agents as peers. Less covered in the changelog excerpts seen so
far — caveat: this section needs depth from a more thorough docs
or source-repo pass before MVP 4 planning.

**Used in this project:** MVP 4.

---

## 2. External tools

This section covers everything not native to Oxygen. Each entry names
the tool, its role here, the version we run, and its
Oxygen-native-replacement story (per BUILD.md §4).

### 2.1 dlt

**What it is:** A Python library for declarative data ingestion. Pull
from an API, normalize, write to a destination. We use it to fetch
Somerville 311 records from the Socrata API and merge into DuckDB on
the PK `id`.

**Role here:** Ingestion. Owns `dlt/somerville_311_pipeline.py` (the
311 pull) and `dlt/load_dbt_results.py` (loads dbt's `run_results.json`
into bronze for admin DQ).

**Version:** 1.26.0 with `[duckdb]` extra. Plus `python-ulid 3.1.0`
for run IDs.

**Migration trigger:** If Oxygen ships an ingestion equivalent
(speculated as "Airway" in BUILD.md framing), the project would
migrate. Not on the near roadmap; Airway hasn't been mentioned in
the changelogs seen so far.

---

### 2.2 DuckDB

**What it is:** Embedded OLAP database — a single `.duckdb` file
opened by client libraries. Zero-config, columnar, fast on the data
shapes we have (low millions of rows, analytical queries).

**Role here:** The warehouse. `data/somerville.duckdb` is the single
source of truth on EC2. dlt writes to it, dbt models query it, Oxygen's
Answer Agent reads it via `execute_sql`.

**File locking constraint:** DuckDB serializes writes — only one
process can hold a write lock. The `./run.sh` script enforces
sequential order (dlt → dbt → oxy reads) so writes never overlap.
Oxygen reads lazily and doesn't hold the file open (verified via
`lsof`).

**Version:** bundled with dbt-duckdb and dlt[duckdb].

**Migration trigger:** None planned. DuckDB scales fine to the
expected MVP 4 data volumes; Oxygen supports it natively as a
database backend.

#### Spatial extension — pattern and pre-flight rule

**Pre-flight rule, before the pattern.** Before reaching for the
spatial join, pre-flight whether spatial derivation is the best signal
available. If the source publishes a usable region column (`ward`,
`neighborhood`, `precinct`), compare its coverage to the spatial join's
projected coverage. Use whichever wins; document the comparison either
way. The spatial pattern is correct when source doesn't publish, OR
when source coverage is meaningfully worse than spatial would produce.

Two Plan 23 precedents:

- **Permits (Phase A, [PR #36](https://github.com/ironmonkey88/oxygen-mvp/pull/36)).** Source has no `ward` column.
  Spatial join derived ward at 96.62% match (62,337 / 64,521 rows;
  2,176 outside Somerville polygons get NULL ward). The pattern landed.
- **Citations (Phase B, [PR #38](https://github.com/ironmonkey88/oxygen-mvp/pull/38)).** Source publishes `ward` with
  0.12% NULL (84 / 67,311 rows). Pre-flight ran the spatial join
  speculatively: 99.82% match, *worse* than source's 99.88% coverage.
  Spatial was NOT used despite the pattern being available.

**Halt threshold:** if spatial-derived match rate is <90% of total
rows, halt and surface. Don't paper over — that signals geocoding
quality, polygon boundary issues, or coordinate-system mismatch worth
investigating before the gold layer ships.

**The pattern** (lifted from `dbt/models/gold/fct_permits.sql`):

```sql
{{ config(
    materialized='table',
    schema='gold',
    pre_hook=["INSTALL spatial", "LOAD spatial"]
) }}

with ward_polys as (
    select ward, st_geomfromtext(geometry_wkt_wgs84) as geom
    from {{ ref('dim_ward') }}
),
points as (
    select *,
           case when latitude is null or longitude is null then null
                else st_point(cast(longitude as double),
                              cast(latitude as double)) end as pt
    from {{ ref('raw_source_with_latlng') }}
),
joined as (
    select p.*, w.ward as derived_ward
    from points p
    left join ward_polys w
      on p.pt is not null and st_contains(w.geom, p.pt)
)
select ... from joined
```

`dim_ward.geometry_wkt_wgs84` stores polygons as WGS84 WKT strings;
`ST_GeomFromText` re-parses them at join time, `ST_Contains` does the
point-in-polygon test. `pre_hook` ensures `INSTALL spatial; LOAD
spatial;` runs on each model materialization (DuckDB extensions are
per-connection). The `LEFT JOIN ... ON p.pt IS NOT NULL AND
ST_Contains(...)` form keeps `derived_ward` NULL for rows missing
lat/lng without exploding the join cardinality.

For the `relationships` test on the derived ward column, add a
`WHERE ward IS NOT NULL` carve-out so the small unmatched fraction
doesn't trip the test (per Plan 23 Phase A precedent).

---

### 2.3 dbt Core

**What it is:** SQL transformation framework — declarative models
(`.sql` files) + tests + docs. Reads from a source (bronze), writes
to derived models (silver, gold, admin).

**Role here:** Transformation. Models live in `dbt/models/{bronze,gold,admin}/`.
The bronze schema mirrors the source; gold is the analyst-facing
star schema; admin holds run + DQ observability. Silver (PII redaction)
is deferred to MVP 3.

**Version:** dbt-core 1.11.9 + dbt-duckdb adapter 1.10.1.

**Schema convention note:** dbt-duckdb prefixes schemas with the
database name. Our profile points at `somerville.duckdb`, so the
configured schemas `bronze`/`silver`/`gold`/`admin` materialize as
`main_bronze`/`main_silver`/`main_gold`/`main_admin`. Queries against
DuckDB must use the prefixed name.

**Migration trigger:** Oxygen ships native SQL Modeling (§1.11) that
understands dbt project conventions. Migration when Airform proves
out at this project's scale.

---

### 2.4 nginx

**What it is:** Web server for the public portal at port 80. Serves
static HTML from `/var/www/somerville/`, reverse-proxies `/chat`
(Basic Auth-gated) to the Oxygen SPA at `localhost:3000`, and
exposes `/docs` (dbt docs), `/erd`, `/metrics`, `/profile`, `/trust`
as static-file routes.

**Role here:** Portal serving + Basic Auth gate. The canonical config
lives in `nginx/somerville.conf` in the repo; `./run.sh` doesn't
deploy it (deploy is manual via `scp` + `sudo cp` + `nginx -t` +
`systemctl reload nginx`).

**Version:** system-managed Ubuntu 24.04 package.

**Migration trigger:** MVP 4 returns to multi-workspace Oxygen
(`oxy serve`), which serves its own auth + multi-org surfaces. nginx
may stay around for the static portal even then, but `/chat` would
go directly to Oxygen.

---

### 2.5 systemd

**What it is:** Linux service manager. We use it to orchestrate four
services + timers on EC2.

**Role here:**
- `oxy.service` — Oxygen runtime as a system service (Session 24)
- `pipeline-refresh.service` + `pipeline-refresh.timer` — daily
  `./run.sh daily` at 6 AM EDT
- `source-health-check.service` + `source-health-check.timer` —
  hourly Socrata ping
- `profile-tables.service` + `profile-tables.timer` — Sunday 2 AM
  EDT column profile regen

All four timers explicitly drop the `oxy.service` dependency so a
refresh isn't blocked when Oxygen restarts.

**Migration trigger:** None. systemd is OS-level orchestration that
Oxygen doesn't aim to replace.

---

### 2.6 Tailscale

**What it is:** Mesh VPN. Closed the public `:22` (SSH) and `:3000`
(Oxygen) ports on the AWS security group; access is via the Tailnet
at `oxygen-mvp.taildee698.ts.net`. Plan 1 (Session 12).

**Important constraint:** Tailscale SSH (`--ssh`) is intentionally
OFF. When enabled, it preempts OpenSSH for Tailnet peers via
`tailscaled be-child`, bypassing PAM and silently breaking
`/etc/environment` env-var loading.

**Version:** 1.96.4.

**Migration trigger:** MVP 4 — once HTTPS + Magic Link auth ship for
public access, the project-team Tailnet path may stay (for ops) but
public chat goes through the auth surfaces.

---

### 2.7 AWS EC2

**What it is:** The single VM hosting everything — Oxygen runtime,
DuckDB warehouse, nginx portal, all systemd services.

**Specs:** `t4g.medium`, Ubuntu 24.04 LTS ARM. Public IP
`18.224.151.49` (port 80 only); SSH + Oxygen reachable only over
Tailnet.

**Why this size:** Sufficient for 1.17M-row workload + Oxygen +
PostgreSQL + nginx + dbt + dlt with headroom. Will revisit if MVP 4
data volume grows materially.

---

### 2.8 Claude API (Anthropic)

**What it is:** The LLM provider for Oxygen's Answer Agent (and
Builder Agent when MVP 2 lands). Configured in `config.yml` and
referenced from `.agent.yml`.

**Current model:** `claude-opus-4-7` (since 2026-05-11 — MVP 1.5).
Migrated from `claude-sonnet-4-6` because Sonnet's 30K input
tokens/min Tier 1 rate limit was hit on SPA multi-turn conversations;
Opus has 500K/min on the same tier (16× headroom).

**Cost:** ~$5–6/month current spend at MVP 1 load; projected $25–30/month
under MVP 2 usage. Trivial relative to the project's value.

**Two env vars on EC2 (per CLAUDE.md):**
- `ANTHROPIC_API_KEY` — agent LLM calls
- `OXY_DATABASE_URL` — `oxy build`/`oxy serve` connection to the
  Postgres container Oxy manages

Both live in `/etc/environment` (not `~/.bashrc` — plain non-interactive
SSH doesn't load that).

---

### 2.9 GitHub

**What it is:** Source of truth for the repo. EC2 clones and pulls;
local Mac authors and pushes.

**Repo:** `ironmonkey88/oxygen-mvp`. Currently private; STANDARDS §4.5
row 1 reinterpreted as "team-clonable" (Session 24) — public flip
deferred as a separate launch decision.

**Worktree convention:** Code operates in worktrees under
`.claude/worktrees/<name>/`. Main checkout lives at the project root.

---

### 2.10 Claude Code

**What it is:** The CLI agent (this conversation) that executes plans
against the project. Reads CLAUDE.md, BUILD.md, MVP.md, LOG.md, TASKS.md
for context; uses the local docs mirror at `docs/oxygen-docs/` for
Oxygen reference; writes files, runs commands, makes commits.

**Notable settings:** `defaultMode: acceptEdits` auto-accepts Edit/
Write/Read on project files; a PreToolUse hook (`.claude/hooks/block-dangerous.sh`)
denies risky Bash shapes (chains, command substitution, leading `cd`,
etc.); three-tier allowlist (committed `settings.json` + per-machine
`settings.local.json` + worktree-scoped). See CLAUDE.md "Bash Safety"
and "Allowlist policy" sections.

---

## 3. Pipeline conventions

These are the project's stable naming choices. Drift here breaks
queries silently — agents and dashboards rely on the prefixes.

### Schemas

| Schema (DuckDB-prefixed) | Purpose |
|--------------------------|---------|
| `main_bronze` | Raw source data (dlt-owned `*_raw` tables + dbt-owned passthrough views) |
| `main_silver` | Cleaned and typed (PII redaction; deferred to MVP 3) |
| `main_gold` | Business-ready facts + dims |
| `main_admin` | Infrastructure observability (run history, source health, column profiles, DQ test results) |

### Table prefixes

| Prefix | Schema(s) | Example |
|--------|-----------|---------|
| `raw_` | bronze | `raw_311_requests`, `raw_311_requests_raw` |
| `stg_` | silver (MVP 3+) | `stg_311_requests` |
| `fct_` | gold + admin | `fct_311_requests`, `fct_pipeline_run_raw` |
| `dim_` | gold + admin | `dim_date`, `dim_data_quality_test` |
| `*_raw` suffix | bronze + admin | dlt-owned merge target or admin landing table |

### Column conventions

- **snake_case everywhere:** `request_type`, `opened_dt`
- **Primary keys:** `<table>_id` (e.g., `request_id`)
- **Surrogate keys (MVP 3+):** `<table>_sk`
- **Dates/timestamps:** `_dt` suffix (`opened_dt`, `closed_dt`)
- **Booleans:** `is_` prefix (`is_open`, `is_active`)
- **Percentages:** `pct_` prefix (`pct_null`, `variance_pct`)
- **Counts:** `_count` suffix (`null_count`, `distinct_count`)

### Audit columns (bronze)

Every row in dlt-owned bronze `*_raw` tables carries these four
pipeline-metadata columns. **Not for analysis** — use the source
`date_created_dt`, not `_extracted_at`.

| Column | What it is |
|--------|-----------|
| `_extracted_at` | When the row was extracted from source in this run |
| `_extracted_run_id` | ULID of the `./run.sh` invocation that extracted it |
| `_first_seen_at` | When this row's `id` was first observed (preserved across re-extractions) |
| `_source_endpoint` | The Socrata URL the row came from |

### Portal routes

| Route | Purpose | Source of truth |
|-------|---------|-----------------|
| `/` | Portal landing | `portal/index.html` |
| `/docs/` | Data dictionary | dbt-generated `dbt/target/` |
| `/erd` | Warehouse ERD + semantic-layer diagram | `scripts/generate_erd_page.py` (Plan 1b) |
| `/metrics` | Airlayer measure catalog | `scripts/generate_metrics_page.py` |
| `/profile` | Column shape (distinct counts, null %, etc.) | `scripts/generate_profile_page.py` (Plan 1b) |
| `/trust` | Pipeline + DQ reliability | `scripts/generate_trust_page.py` |
| `/chat` | Public chat (Basic Auth) | nginx proxy → Oxygen SPA `:3000` |

---

## 4. Data sources

### Somerville 311

**Endpoint:** Socrata API at `data.somervillema.gov`, dataset
`4pyi-uqq6`. Public, no API key required for the read volumes here.

**Volume:** ~1.17M rows total, growing ~100–115K/year. As of 2026-05-12,
1,170,637 rows in the source.

**Schema:** 22 source columns (case ID, dates, type, status, ward,
block code, dept flags, survey scores, etc.). Plus 6 metadata columns
(`_extracted_at`, `_extracted_run_id`, `_first_seen_at`,
`_source_endpoint`, `_dlt_load_id`, `_dlt_id`) added in bronze.

**Pull pattern:** Full pull on every `./run.sh`. The source has NO
publisher-maintained per-row modified field — Socrata's `:updated_at`
matches the dataset-wide `rowsUpdatedAt` value for every row, so a
watermark-based incremental pull doesn't work. dlt merges on PK `id`,
preserving `_first_seen_at` across re-extractions. See
`docs/limitations/source-bulk-republish-no-per-row-modified.md`.

**Cadence:** Daily via `pipeline-refresh.timer` at 6 AM EDT.

---

## Maintenance

This file lives at the project root alongside CLAUDE.md, BUILD.md,
MVP.md. Update it when:

1. A new Oxygen component enters the project's surface (e.g., MVP 4
   adds Slack — flesh out §1.13).
2. A new external tool is adopted (e.g., adding S3 — add §2.x).
3. An Oxygen changelog redefines a component already in §1 (e.g.,
   Builder Agent gets dedicated `learn-about-oxy/` docs — update §1.8
   and remove the "Documentation gap" note).
4. A pipeline convention changes (silver lands, ward dimension comes
   online, etc.).

The doc is for both Code and Chat. Chat especially cannot fetch
Oxygen URLs, so keep definitions **self-contained** — no "see
https://oxy.tech/…" pointers as substitutes for the prose.
