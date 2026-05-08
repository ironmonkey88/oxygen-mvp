# LOG.md — Oxygen MVP Captain's Log

> **Source of truth for project status.** Claude Code updates this file automatically after completing tasks, making decisions, or hitting blockers. Do not delete old entries.

---

## Current Status

**Active MVP:** MVP 1 — Static data → DuckDB → Airlayer → Answer Agent chat UI
**Phase:** Semantic layer complete. All four overnight deliverables green after Gordon downgraded the `oxy build` gate to `oxy validate` + `airlayer query -x`. Next: Answer Agent (will pull `oxy start` + `oxy build` in naturally).
**Last Updated:** 2026-05-08 07:31 ET (Overnight Session — Claude Code)

---

## Session Log

### Overnight Session — Deliverable 3 — 2026-05-08 07:22 ET (Semantic layer, Claude Code)

**Goal:** ship the four `.view.yml` files + topic + `config.yml`, then pass the two validation gates.

**Accomplishments:**
- Created `semantics/views/{requests,request_types,statuses,dates}.view.yml` and `semantics/topics/service_requests.topic.yml` — 4 views, 1 topic.
- Created `config.yml` at project root with merged Oxygen + Airlayer config: `models` (Anthropic Claude Sonnet 4.6), `databases` (somerville → DuckDB), `defaults.database: somerville`.
- `requests` view declares primary entity on `id` and three foreign entities (`date_created_dt`, `request_type_id`, `status_id`); auto-join works.
- `airlayer validate` — Schema is valid: 4 views, 1 topic.
- **Validation gate 1 (airlayer query -x): PASSED.** `airlayer query --measure requests.total_requests --dimension request_types.request_type --limit 5 -c config.yml -x` returned 5 rows with sensible counts (e.g. "Obtain a parking permit inquiry": 74,443). Auto-generated SQL: `SELECT request_types.request_type, COUNT(*) FROM main_gold.dim_request_type LEFT JOIN main_gold.fct_311_requests ON request_type_id = request_type_id GROUP BY 1 LIMIT 5`. Auto-join inferred from entity match.
- **Validation gate 2 (oxy build): NOT PASSED — see blocker below.** `oxy validate` passes ("All 5 config files are valid"), confirming the semantic config is well-formed; `oxy build` is blocked on Oxygen's runtime stack.
- Mid-deliverable fixes:
  - `airlayer validate` initially failed: entity keys must be declared as dimensions. Added `request_type_id` and `status_id` dimensions to `requests.view.yml`.
  - `oxy build` initially failed: deserialize error on `models.model` field. Oxy 0.5.47 schema uses `model_ref` (not `model`) and `key_var` (env var name) per [oxy-hq/oxy/examples/config.yml](https://github.com/oxy-hq/oxy/blob/main/examples/config.yml). Updated `config.yml` accordingly.

**Decisions Made:**
- `requests` view denormalized location dims = `ward`, `block_code` (only what bronze actually has — not `neighborhood`/`lat`/`long`/`address`).
- `open_requests` measure filter is `status != 'Closed'` (text comparison on the local fact column) rather than a join through `statuses.is_open`. Simpler, no fan-out, same result.
- `oxy build` validation gate left unpassed rather than spinning up Docker Postgres in the middle of an overnight session — Gordon should make the call on bringing up Oxygen's full stack in the morning.
- CLAUDE.md's `LLM Configuration` snippet is stale (`model:` → should be `model_ref:` per oxy 0.5.47). Not edited — out of scope for this deliverable. Recommend a quick doc-fix commit.

**Blockers:** None — `oxy build` gate downgraded by Gordon at 2026-05-08 07:31 ET (option (b) below). `oxy validate` + `airlayer query -x` together cover the original gate intent.

**Next Action:** Answer Agent — `oxy start` and `oxy build` will land naturally there.

---

### Overnight Session — Deliverable 2 — 2026-05-07 23:29 ET (Airlayer CLI install, Claude Code)

**Goal:** install the standalone Airlayer Rust CLI on EC2 and confirm it can be invoked.

**Accomplishments:**
- Ran `bash <(curl -sSfL https://raw.githubusercontent.com/oxy-hq/airlayer/main/install_airlayer.sh)` on EC2.
- Installer downloaded a prebuilt binary for `aarch64-unknown-linux-gnu` (no Rust toolchain needed).
- Binary landed at `/home/ubuntu/.local/bin/airlayer` (already on the default Ubuntu login PATH via `~/.profile`).
- Version confirmed: `airlayer 0.1.1`.
- Sanity-checked: `airlayer --help`, `airlayer --version`, `airlayer query --help` all run.
- No system packages added.

**CLI shape note (matters for Deliverable 3):**
Airlayer 0.1.1 does **not** accept a `--connection` flag on `airlayer query`. Datasource connections are loaded from `config.yml` via `-c/--config`. The prompt's exact sanity command (`--connection "duckdb:///..."`) failed with `unexpected argument '--connection'`; running with just `--help` succeeds. Subcommands available in 0.1.1: `query`, `validate`, `init`, `update`, `test-connection`, `convert`, `build`, `pull`, `inspect`. Important for Deliverable 3: `--datasource <DATASOURCE>` selects which database from `config.yml` to execute against, and `-x/--execute` requires `--config` plus an `exec-*` feature flag.

**Decisions Made:**
- No system packages installed — prebuilt aarch64 binary is sufficient.
- Non-login SSH sessions don't pick up `~/.local/bin` in PATH; commands must either source the profile or prefix with `~/.local/bin/airlayer`. Will use `export PATH=$HOME/.local/bin:$PATH` in scripted SSH calls.
- Skipped `airlayer init` — would scaffold its own `config.yml`/`CLAUDE.md`/skills, which would conflict with the existing repo. Will hand-write the semantic layer config in Deliverable 3.

**Blockers:** None

**Next Action:** Deliverable 3 — write `semantics/views/*.view.yml`, `semantics/topics/service_requests.topic.yml`, register the `somerville` datasource in `config.yml`, and pass both validation gates (`oxy build` and an `airlayer query -x` returning rows).

---

### Overnight Session — Deliverable 1 — 2026-05-07 23:05 ET (Gold dbt models, Claude Code)

**Goal:** build the four MVP 1 gold models (`dim_date`, `dim_request_type`, `dim_status`, `fct_311_requests`) plus tests, with no silver layer in between.

**Pre-flight profiling (scratch/null_check.py):**
- Zero NULLs across `id`, `date_created`, `type`, `most_recent_status`, `most_recent_status_date`, `classification`, `origin_of_request` — defensive coalesce not needed for FK hashes.
- DuckDB `extract(dow from ...)` returns Sunday=0..Saturday=6, so `dow IN (0, 6)` = weekend.
- Status cardinality is 4: `Closed` (1.15M), `Open` (9.7K), `In Progress` (6.0K), `On Hold` (245). No ambiguity for `is_open` mapping.
- `bronze.type` cardinality 342; `category` cardinality 21.
- Bronze location columns are only `ward` and `block_code` — there is no `neighborhood`, `lat`, `long`, or `address`. Diverged from prompt and used only what exists.

**Accomplishments:**
- Wrote `dbt/models/gold/dim_date.sql` — date spine 2015-07-01 → 2026-06-05 (max + 30 days), 3,993 rows.
- Wrote `dbt/models/gold/dim_request_type.sql` — md5 hash surrogate key, 342 rows.
- Wrote `dbt/models/gold/dim_status.sql` — md5 surrogate key, `is_open` derived from status text, 4 rows.
- Wrote `dbt/models/gold/fct_311_requests.sql` — 1,168,959 rows, location denormalized (`ward`, `block_code`), survey columns retained as VARCHAR, dept tag columns converted via `try_cast(... as boolean)` to preserve NULL.
- Wrote `dbt/models/gold/schema.yml` — unique + not_null on PKs/SKs, accepted_values on status, relationships from `fct_311_requests` to both dims.
- Validation: `dbt run --select gold` PASS=4, `dbt test --select gold` PASS=14, both WARN=0 ERROR=0.
- Cleared dbt deprecation `MissingArgumentsPropertyInGenericTestDeprecation` by wrapping `relationships` test args under `arguments:` key.
- Sanity checks (scratch/gold_row_check.py): row counts and classification breakdown match bronze exactly.

**Decisions Made:**
- Surrogate keys named with `_id` suffix per overnight prompt (CLAUDE.md reserves `_sk` for MVP 3+). md5 hashes of the source text.
- `is_open` mapping (no ambiguity in observed values): `Closed → false`, `Open/In Progress/On Hold → true`.
- Location fields on fact: `ward` and `block_code` only — neighborhood/lat/long/address do not exist in the bronze source. `dim_location` still deferred to MVP 3.
- Dept tag flags use `try_cast(col as boolean)` so the three-state nature (`'1'` → true, `'0'` → false, NULL → NULL) is preserved.
- Dept tag columns renamed with `is_<area>_tag` per CLAUDE.md naming standard.
- `dim_origin` deferred from this overnight session — not in prompt scope; flagged in TASKS.md.
- `accepted_values` test added only for status; classification/origin deferred (they'll surface as semantic layer dimensions in Deliverable 3 instead of dbt tests).
- Tooling discipline: switched to scratch/-then-scp pattern for ad-hoc DuckDB queries (per Gordon's mid-session feedback) — no more SSH heredocs.

**Blockers:** None

**Next Action:** Deliverable 2 — install the standalone Airlayer CLI on EC2.

---

### Overnight Session — Deliverable 0 — 2026-05-07 22:52 ET (Doc cleanup, Claude Code)

**Goal:** apply Gordon's edits fixing `.sem.yml` → `.view.yml` and documenting the Airlayer dual-engine model (Oxygen built-in + standalone Rust CLI).

**Accomplishments:**
- Applied 3 edits to `CLAUDE.md`: Stack at a Glance row, Project File Structure (`semantic/` → `semantics/views/` + `semantics/topics/`), Reference Links (added Airlayer repo + schema-format).
- Applied 3 edits to `ARCHITECTURE.md`: Stack Decisions row, Component Map diagram, Airlayer subsection (full rewrite covering two engines / one schema, semantic_query tool, oxy build, project structure).
- Committed `71a8fd9` on the worktree branch, fast-forwarded `main`, pushed `origin/main`.
- EC2 pulled — confirmed `git log -1` on EC2 reports `71a8fd9 docs: fix .sem.yml → .view.yml, document Airlayer dual-engine model`. EC2 was 7 commits behind GitHub at session start (pattern from Session 5); now caught up.

**Decisions Made:**
- `.view.yml` is the canonical file extension for views; `.topic.yml` for topics. `.sem.yml` no longer used anywhere in the project docs.
- Airlayer is a dual-engine system: Oxygen's built-in semantic engine and the standalone Rust CLI share the same schema. Agents query via the `semantic_query` tool with a `topic` parameter.
- Project structure is `semantics/views/` and `semantics/topics/` at project root (plural, with subdirs) — replaces the old single-file `semantic/somerville_311.sem.yml`.

**Blockers:** None

**Next Action:** Deliverable 1 — query bronze on EC2 then build the four gold dbt models.

---

### Session 5 follow-up — 2026-05-07 22:22 ET (Hygiene, Claude Code)

**Goal:** close out four follow-ups from Session 5 cleanup. No model logic touched.

**Accomplishments:**
- Reconciled `docs/schema.sql` with the live Bronze view: added `_dlt_load_id` and `_dlt_id` to `bronze.raw_311_requests` with a comment block explaining they're retained at every layer for lineage.
- Tightened the autonomous-execution memory entry. Replaced the loose "don't ask for routine reversible work" rule with two explicit lists: a "do not ask" list (file edits, allowlist additions, read-only git/EC2, scp, dbt/dlt/oxy runs) and an "always ask first" list (schema changes that propagate downstream, semantic/agent edits, destructive ops, pushes, anything that changes the data contract or costs money).
- Added "Session Start on EC2" section to `CLAUDE.md`: first command on EC2 every session is `cd ~/oxygen-mvp && git pull origin main`. Added a one-liner pointer in `SETUP.md` Run Order section.

**Decisions Made:**
- dlt metadata columns (`_dlt_load_id`, `_dlt_id`) are retained on the Bronze view for lineage. `docs/schema.sql` updated to match — schema and view now agree at 24 columns.
- Always-ask boundary made explicit in memory. Schema, semantic-layer, agent, and data-contract changes always go through Gordon — even when broader work is approved.
- EC2 pulls from GitHub `main` at the start of every session. The Session 5 drift (EC2 7 commits behind) was the trigger.

**Blockers:** None

**Next Action:** Start MVP 1 gold models in a fresh session.

---

### Session 5 — 2026-05-07 22:00–22:15 ET (Cleanup, Claude Code)

**Goal:** audit repo vs docs, sync missing source files, lock down before gold models.

**Audit findings:**
- Local Mac: had docs and `portal/` only — no source code dirs.
- EC2 `~/oxygen-mvp/`: had `dlt/somerville_311_pipeline.py` (untracked); no `dbt/`, `agents/`, `semantic/`, `apps/`, `config.yml`, or `run.sh`.
- EC2 `~/oxygen-mvp-backup/`: contained dbt scaffold from before the post-clone restore — `dbt_project.yml`, `models/bronze/raw_311_requests.sql`, `models/bronze/schema.yml`. Bronze SQL referenced only 10 source columns, predates the 22-column re-ingest.
- EC2 was 7 commits behind GitHub `main` (gitignore + CLAUDE.md + ARCHITECTURE.md updates not pulled).
- `dim_origin` already present in `ARCHITECTURE.md` Tables list and `TASKS.md` gold section — added in commit `ac5093e`. Audit prompt was based on stale info.
- `portal/` already documented in `ARCHITECTURE.md` (Web portal + Portal routes sections). Audit prompt was based on stale info.

**Accomplishments:**
- Recovered `dlt/somerville_311_pipeline.py` from live EC2 into local repo.
- Recovered `dbt/dbt_project.yml`, `dbt/models/bronze/raw_311_requests.sql`, `dbt/models/bronze/schema.yml` from EC2 backup into local repo.
- Rewrote `bronze/raw_311_requests.sql` to match `docs/schema.sql`: all 22 source columns + 2 dlt metadata columns, all VARCHAR, `union_by_name=true` for cross-year Parquet shape drift.
- Verified Bronze on EC2: `dbt debug` clean, `dbt run --select bronze` built `main_bronze.raw_311_requests` (1,168,959 rows, 24 cols), `dbt test --select bronze` passed 5/5 (id unique, id not_null, classification not_null + accepted_values, date_created not_null).
- Added `dbt/profiles.yml` to `.gitignore`; rewrote `SETUP.md` step 8 to drop the repo-local profile alternative and align profile name to `somerville_311`.
- Allowlisted ~60 read-only Bash commands in `.claude/settings.json` (git/gh/rg/etc.) to reduce permission prompts.

**Decisions Made:**
- `~/.dbt/profiles.yml` (user-local) is the only supported profile path. No `dbt/profiles.yml` in the repo.
- Bronze keeps source columns as VARCHAR (matches `docs/schema.sql`); date columns cast `::VARCHAR` rather than `::TIMESTAMP`.
- `_dlt_load_id` and `_dlt_id` retained on the bronze view for lineage/debugging — extras beyond the 22 logical schema columns.
- No empty stubs for unbuilt components (`agents/`, `semantic/`, `apps/`, `config.yml`, `run.sh`, silver/gold/admin model dirs). They land when their MVP is built.
- Recovered the backup dbt scaffold rather than starting dbt fresh — backup is real prior work and aligns with schema.sql once columns are extended.

**Blockers:** None

**Next Action:** Pull on EC2 to sync the committed scaffold, then start MVP 1 gold models in a fresh session.

---

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

### Session 5 — 2026-05-07 ~22:00 ET → 2026-05-08 ~07:00 ET (Claude.ai planning + Code overnight run)

**Context:**
Planning conversation in Claude.ai to scope a multi-deliverable overnight 
run for Code: gold layer + Airlayer install + semantic layer. Process 
notes captured here so future sessions can see how we worked, not just 
what we shipped.

**Process accomplishments:**
- Caught two factual errors in the prep before handing off to Code:
  - I (Claude.ai) initially asserted Airlayer was bundled into Oxygen and 
    needed no install. Gordon pushed back with the GitHub URL. Verified 
    via repo: Airlayer is a separate Rust binary with its own install 
    script. Correction made before any work was given to Code.
  - Discovered our docs used `.sem.yml` everywhere, but the actual file 
    extension is `.view.yml` (confirmed in airlayer/docs/schema-format.md, 
    which states "This is the same format used by Oxy"). Doc cleanup 
    became Deliverable 0 of the overnight run.
- Confirmed Oxygen and standalone Airlayer share the exact same `.view.yml` 
  schema. Two engines, one schema. Going with Option B (install both) 
  gives us a CLI for shell-based testing without spinning up the Oxygen 
  runtime.
- Walked through dependency check (gold → Airlayer → semantic, sequential), 
  validation gates, and explicit out-of-scope list (silver, run.sh, admin 
  schema, Answer Agent) before Code received the prompt. Prevented scope 
  creep overnight.
- Gordon kept Claude.ai honest by asking "did we resolve all your 
  questions?" before handoff — surfaced the residual config.yml collision 
  question, which got added to the prompt as "flag as blocker if it 
  appears."
- Pre-run doc fixes (CLAUDE.md, ARCHITECTURE.md) handed to Code as 
  Deliverable 0 with explicit before/after blocks rather than free-form 
  "update the docs" — much faster and unambiguous.

**Decisions made (process / planning):**
- Session-starter.md stays in two places (local copy and repo copy) — 
  serves as a stable contract that rarely changes. LOG.md is the state 
  that changes session to session.
- For overnight runs: each deliverable commits and pushes independently. 
  Don't batch. Code's commit cadence ("feat(gold): ...", 
  "chore(airlayer): install", "feat(semantic): ...") worked as designed.
- For overnight runs: validation gates must be concrete, runnable 
  commands. "Done when X passes" beats "done when it works."
- Out-of-scope items must be listed explicitly in the prompt. Code 
  honored "do not build silver, run.sh, admin schema, or Answer Agent" 
  cleanly.

**Blockers encountered overnight (process-related):**
- Heredocs over SSH (`ssh oxygen-mvp '... <<EOF'`) trip Claude Code's 
  permission system on every call, even with `Bash(ssh oxygen-mvp *)` in 
  the allowlist. The newline + `#` pattern can hide arguments from path 
  validation. Manual approval required each time.
- Worktree git commands (`git -C /path/to/worktree commit ...`) don't 
  match allowlist patterns like `Bash(git commit *)` because `-C <path>` 
  comes before the subcommand. "Allow always" doesn't always stick because 
  worktree paths contain session-specific identifiers.
- Combined effect: overnight run paused multiple times waiting for human 
  approval. Did not fully run unattended.

**Resolutions / lessons for future overnight runs:**
- Allowlist needs broader patterns. Update `.claude/settings.local.json` 
  to include `Bash(git *)` and `Bash(git -C *)` rather than relying on 
  per-subcommand patterns. Add `Bash(duckdb *)`, `Bash(dbt *)`, 
  `Bash(oxy *)`, `Bash(airlayer *)`, `Bash(python3 *)`.
- For multi-line SQL or Python on EC2, do NOT use heredocs. Write the 
  query/script to a file in `scratch/` (gitignored) on local, scp to 
  /tmp/ on EC2, run with `duckdb -f` or `python script.py`. Bonus: 
  queries become reproducible artifacts.
- For future runs of this length, walk the allowlist + heredoc rule 
  through Code in advance as a pre-flight, not in the middle of the run.

**Decisions surfaced for Gordon's morning review:**
- CLAUDE.md `LLM Configuration` snippet uses `model:` but Oxygen 0.5.47 
  wants `model_ref` + `key_var`. Code flagged but did not edit without 
  signoff. Needs decision.
- `oxy build` requires Oxygen runtime (Docker + Postgres on port 3000 via 
  `oxy start`). Was not run. `oxy validate` (config syntax) and 
  `airlayer query -x` (actual execution returning 5 rows with auto-join) 
  both passed — semantic layer is functionally working. `oxy build` 
  deferred to first Answer Agent session when `oxy start` will be running 
  anyway. Recommend marking Deliverable 3 done with this caveat.

**Net result:**
- Deliverables 0, 1, 2 fully complete.
- Deliverable 3 functionally complete (semantic layer works); only the 
  heaviest validation gate (`oxy build`) deferred to next session for 
  good reason.
- Two real lessons captured for future overnight runs (allowlist + 
  heredocs).

**Next action:**
- Decide on CLAUDE.md `model_ref` edit (Code is paused waiting).
- Update `.claude/settings.local.json` allowlist before next overnight 
  attempt.
- Plan next session: Answer Agent (will pull in `oxy start` + `oxy build` 
  naturally).

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
| 2026-05-07 22:13 ET | Profiles live in `~/.dbt/profiles.yml` only — no repo-local `dbt/profiles.yml` | Avoids checking machine-specific paths into git; SETUP.md updated, gitignore extended |
| 2026-05-07 22:13 ET | Bronze keeps source columns as VARCHAR per `docs/schema.sql` | Date columns cast `::VARCHAR` rather than `::TIMESTAMP`; transforms deferred to silver |
| 2026-05-07 22:13 ET | No empty stubs for unbuilt components | `agents/`, `semantic/`, `apps/`, `config.yml`, `run.sh`, silver/gold/admin model dirs land when their MVP is built |
| 2026-05-07 22:13 ET | Recovered backup dbt scaffold rather than starting fresh | Backup is real prior work, aligns with schema.sql once columns extended |
| 2026-05-07 22:22 ET | dlt metadata columns retained on Bronze view for lineage; `docs/schema.sql` updated to match | Schema/view drift reconciled at 24 columns; lineage trace is valuable at every layer |
| 2026-05-07 22:22 ET | Always-ask boundary made explicit in memory | Permissive "don't ask" rule alone was too loose; schema/semantic/agent/destructive ops still require explicit confirmation |
| 2026-05-07 22:22 ET | EC2 pulls from GitHub `main` at the start of every session | Session 5 found EC2 7 commits behind; CLAUDE.md "Session Start on EC2" section + SETUP.md pointer |
| 2026-05-07 22:52 ET | `.view.yml` (views) + `.topic.yml` (topics) replace `.sem.yml` everywhere | Matches Airlayer schema spec; same file format used by Oxygen's built-in engine and the standalone Rust CLI |
| 2026-05-07 22:52 ET | Project structure: `semantics/views/` + `semantics/topics/` (plural, subdirs) | Replaces old `semantic/somerville_311.sem.yml`; aligns with Oxygen's recommended layout |
| 2026-05-07 23:05 ET | Gold location fields limited to `ward` + `block_code` | Bronze data does not contain neighborhood/lat/long/address — read-the-data-first rule overrode the prompt's wider list |
| 2026-05-07 23:05 ET | Gold surrogate keys named `_id` (md5 hash of source text) | Aligned with overnight prompt; CLAUDE.md `_sk` convention reserved for MVP 3+ |
| 2026-05-07 23:05 ET | `is_open = false` only for `Closed`; true for Open/In Progress/On Hold | All four observed status values mapped unambiguously; logged in `dim_status.sql` |
| 2026-05-07 23:05 ET | Adopted scratch/-then-scp workflow for ad-hoc DuckDB queries | Heredoc SSH commands trip the read-only allowlist on every call; new `scratch/` dir gitignored, files run via `~/oxygen-mvp/.venv/bin/python /tmp/foo.py` |
| 2026-05-07 23:29 ET | Airlayer 0.1.1 installed via prebuilt aarch64 binary at `~/.local/bin/airlayer` | No Rust toolchain or system packages required — installer binary is self-contained |
| 2026-05-07 23:29 ET | Datasource config lives in `config.yml`, not on the airlayer CLI | Airlayer 0.1.1 has no `--connection` flag on `query`; `-c/--config` + `--datasource` is the supported path |
| 2026-05-08 07:22 ET | Semantic location dims = `ward` + `block_code` only | Bronze data is the source of truth — neighborhood/lat/long/address don't exist; same constraint as gold fct |
| 2026-05-08 07:22 ET | `requests.open_requests` filter = `status != 'Closed'` (no join) | Avoids cross-view join + fan-out; `status` text already on fct, equivalent semantics to `is_open = true` |
| 2026-05-08 07:22 ET | `config.yml` uses `model_ref` + `key_var` (oxy 0.5.47 schema) | CLAUDE.md sample uses outdated `model:` field; fixed in config.yml, doc fix deferred to Gordon |
| 2026-05-08 07:22 ET | Airlayer entity keys must also be declared as dimensions | `airlayer validate` rejects entities pointing to undeclared columns; added FK ID dims to `requests.view.yml` |
| 2026-05-08 07:31 ET | `oxy build` validation gate downgraded for MVP 1; replaced by `oxy validate` + `airlayer query -x` | `oxy build` is for vector embeddings, not config validation. The `oxy validate` syntax check + `airlayer query -x` actual-execution check together cover the original "config is valid + queryable" intent. Real `oxy build` will run naturally during the Answer Agent session when `oxy start` is up. |

---

## Blockers Log

| Date | Blocker | Status | Resolution |
|------|---------|--------|------------|
| 2026-05-07 18:28 ET | Port 80 not open in AWS security group — portal unreachable from public internet | Resolved | Gordon added inbound HTTP rule (port 80, 0.0.0.0/0) in AWS console |
| 2026-05-08 07:22 ET | `oxy build` validation gate fails: `OXY_DATABASE_URL environment variable is required. Use 'oxy start' to automatically start PostgreSQL with Docker, or set OXY_DATABASE_URL to your PostgreSQL connection string.` | Resolved 2026-05-08 07:31 ET | Gate downgraded: `oxy validate` (config syntax, exits 0) + `airlayer query -x` (real data, 5 rows) cover the original intent. Real `oxy build` deferred to Answer Agent session when `oxy start` will be running. See Decisions Log entry for 2026-05-08 07:31 ET. |

---

## Accomplishments by MVP

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
- [ ] Admin DQ framework in place
- [ ] Answer Agent `.agent.yml` configured
- [ ] Chat UI accessible and answering questions  *(blocked on `oxy start` — Docker + Postgres bring-up)*

### MVP 2 — Visual Data Product
- [ ] Airapp `.app.yml` with charts

### MVP 3 — Governance Layer
- [ ] dbt Silver model with PII redaction
- [ ] dbt Gold model updated with dim_location
- [ ] Tailscale access control

### MVP 4 — Semantics
- [ ] Full Airlayer metric library
- [ ] Routing Agent configured
