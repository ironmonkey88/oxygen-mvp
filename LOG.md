# LOG.md — Captain's Log Summary

> Single-screen view of project state. Full session narratives live in [`docs/sessions/`](docs/sessions/).

---

## Current Status

**Active MVP:** MVP 1 — Static data → DuckDB → Airlayer → Answer Agent chat UI
**Phase:** FR pass complete (Answer Agent answers test questions correctly). Plan 0 closed (env vars, allowlist, docs). Next: Plan 0.5 (portal /chat fix) → Plan 1 (Tailscale) → Plans 2-5 for trust pass.
**Open security gap:** `:3000` is publicly accessible. Closes in Plan 1 (Tailscale).
**Last Updated:** 2026-05-08 11:15 ET (LOG.md refactor — Plan A)

---

## Recent Sessions

### Session 9 — 2026-05-08 11:30 ET — plans-0.5-and-1-queued
[full narrative](docs/sessions/session-09-2026-05-08-plans-0.5-and-1-queued.md)

- **Goal:** Close Plan 0 feedback, queue Plans 0.5 + 1, capture meta-lessons.
- **Shipped:** Plan 0.5 (portal /chat fix) and Plan 1 (Tailscale) drafted with environment-assumption pre-flight; Plan 0 confirmed closed.
- **Decisions:** 4 decisions — see Decisions Log
- **Status:** complete
- **Next:** Hand Plan 0.5 to Code.

### Session 8 — 2026-05-08 10:00 ET — plan-0-loose-ends
[full narrative](docs/sessions/session-08-2026-05-08-plan-0-loose-ends.md)

- **Goal:** Close FR loose ends (env vars, OXY_DATABASE_URL, allowlist, public :3000 flag).
- **Shipped:** /etc/environment env-var contract; SETUP.md + CLAUDE.md updates; broadened allowlist (tool-family + destructive-deny); commits e5e94e3 + 196cf28.
- **Decisions:** 4 decisions — see Decisions Log
- **Status:** complete
- **Next:** Plan 0.5 (portal /chat fix), then Plan 1 (Tailscale).

### Session 7 — 2026-05-08 morning ET — fr-answer-agent
[full narrative](docs/sessions/session-07-2026-05-08-fr-answer-agent.md)

- **Goal:** FR pass — Answer Agent answers test questions end-to-end.
- **Shipped:** agents/answer_agent.agent.yml; Oxygen runtime live on EC2; commits f9b3b59 + 5f91595. Test A (2024)=113,961 ✓, Test B (2026)=48,806 ✓.
- **Decisions:** 2 decisions — see Decisions Log
- **Status:** complete
- **Next:** Trust contract pass — but first close three flags (env vars, docs, public :3000).

### Session 6 — 2026-05-08 09:02 ET — mvp1-scope-sharpening
[full narrative](docs/sessions/session-06-2026-05-08-mvp1-scope-sharpening.md)

- **Goal:** Sharpen MVP 1 around analyst persona + extreme trustability bar; capture in STANDARDS.md.
- **Shipped:** STANDARDS.md (7 sections); TASKS.md scope statement + Hardening section; allowlist broadened to tool families.
- **Decisions:** 9 decisions — see Decisions Log
- **Status:** complete
- **Next:** Pick first hardening thread (Tailscale or dbt docs).

### Session 5 — 2026-05-07 22:00 ET → 2026-05-08 07:00 ET — cleanup-and-overnight-run
[full narrative](docs/sessions/session-05-2026-05-07-cleanup-and-overnight-run.md)

- **Goal:** Repo audit + overnight run (gold + Airlayer + semantic).
- **Shipped:** Bronze recovered + tests passing; gold models built (14/14 tests); Airlayer 0.1.1 installed; semantic layer (4 views, 1 topic) executes via auto-join.
- **Decisions:** 11 decisions — see Decisions Log
- **Status:** complete (oxy build gate downgraded — closed in Session 7)
- **Next:** Decide CLAUDE.md model_ref doc fix; broaden allowlist; plan Answer Agent session.

---

## Earlier Sessions

- **Session 4** — 2026-05-07 17:00–18:25 ET — Schema design + portal deployed. [full narrative](docs/sessions/session-04-2026-05-07-schema-and-portal.md)
- **Session 3** — 2026-05-07 14:25–15:50 ET — EC2 provisioned, dlt pipeline designed. [full narrative](docs/sessions/session-03-2026-05-07-ec2-provisioned.md)
- **Session 2** — 2026-05-07 — Project files written. [full narrative](docs/sessions/session-02-2026-05-07-project-files-written.md)
- **Session 1** — 2026-05-07 — Project kickoff. [full narrative](docs/sessions/session-01-2026-05-07-project-kickoff.md)

---

## Active Decisions (last 30 days)

> Rolling window. Older rows live in [`docs/log-archive.md`](docs/log-archive.md).

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-07 | Use dlt for ingestion instead of Airway | dlt is Python-native and mature; Airway not yet evaluated |
| 2026-05-07 | Use dbt Core for transformation instead of Airform | Gordon knows dbt deeply; Airform too new (April 2026) |
| 2026-05-07 | Use DuckDB as warehouse | Zero-config embedded OLAP; sufficient for 1.17M records |
| 2026-05-07 | Use Claude Sonnet 4.6 as LLM | Best price/performance for analytics Q&A |
| 2026-05-07 | Deploy on AWS EC2 t4g.medium | Single instance, internal use first |
| 2026-05-07 | Ubuntu 24.04 LTS instead of 22.04 | 22.04 not available as Quick Start AMI in us-east-2 |
| 2026-05-07 | Port 3000 open to all for MVP | Public open data — low risk; Tailscale before MVP 3 (later pulled forward to MVP 1) |
| 2026-05-07 | LOG.md entries include date and time | Gordon's session traceability requirement |
| 2026-05-07 15:50 ET | dlt filesystem destination (Parquet) over DuckDB destination | Storage-agnostic — readable by Snowflake, Spark, editors |
| 2026-05-07 15:50 ET | Partition Parquet files by year (1 file/year) | Clean handoff to other tools; DuckDB can prune partitions |
| 2026-05-07 15:50 ET | Somerville 311 volume is 1.17M rows (~100-115k/year) | Original 20-30k/year estimate was wrong — actual 3-5x higher |
| 2026-05-07 15:50 ET | Load all classifications at Bronze | Filter at Silver/Gold, not ingestion |
| 2026-05-07 15:50 ET | dlt id PK + merge write disposition | Idempotent monthly refreshes |
| 2026-05-07 | Admin schema: fct_data_profile, dim_data_quality_test, fct_test_run | DQ star schema for test results and baselines |
| 2026-05-07 | fct_data_profile observational only | Profiling never assertional |
| 2026-05-07 | Baselines auto-generated, certified_by='system' | Eliminates manual seeding |
| 2026-05-07 | dbt results: run_results.json → load_dbt_results.py → raw_dbt_results → fct_test_run | Historical tracking without modifying dbt internals |
| 2026-05-07 | run.sh sole pipeline entry point | Enforces correct run order |
| 2026-05-07 | Gold: fct_311_requests + 4 dims; dim_location deferred to MVP 3 | MVP 1 scope; location denormalized for now |
| 2026-05-07 | Dept tag columns as flat booleans on fact | Multi-tag rows; only 4,187/1.17M have tags |
| 2026-05-07 | Survey columns on fact table | Sparse Likert strings; no referential integrity |
| 2026-05-07 | Naming: snake_case, _dt, is_, pct_, _count | Consistent with dbt conventions |
| 2026-05-07 | docs/schema.sql is DDL source of truth | ERD generated from DDL |
| 2026-05-07 | GitHub repo private; EC2 clones, local Mac authors | Single source of truth |
| 2026-05-07 18:17 ET | nginx as portal server on port 80 | Static + /chat proxy + /docs alias |
| 2026-05-07 18:25 ET | Fonts self-hosted in portal/fonts/ | Google Fonts gstatic requires browser UA |
| 2026-05-07 18:25 ET | Portal design tokens: DM Serif Display, DM Mono, Instrument Sans | Matches Somerville Analytics mockup |
| 2026-05-07 22:13 ET | ~/.dbt/profiles.yml only — no repo-local | Avoids machine-specific paths in git |
| 2026-05-07 22:13 ET | Bronze keeps source columns as VARCHAR | Transforms deferred to silver |
| 2026-05-07 22:13 ET | No empty stubs for unbuilt components | Land when their MVP is built |
| 2026-05-07 22:13 ET | Recovered backup dbt scaffold rather than starting fresh | Real prior work, aligns with schema.sql |
| 2026-05-07 22:22 ET | dlt metadata columns retained on Bronze view for lineage | Schema/view drift reconciled at 24 columns |
| 2026-05-07 22:22 ET | Always-ask boundary explicit in memory | Schema/semantic/agent/destructive ops require confirmation |
| 2026-05-07 22:22 ET | EC2 pulls from main at session start | Session 5 caught EC2 7 commits behind |
| 2026-05-07 22:52 ET | .view.yml + .topic.yml replace .sem.yml | Matches Airlayer schema spec |
| 2026-05-07 22:52 ET | semantics/views/ + semantics/topics/ structure | Aligns with Oxygen's recommended layout |
| 2026-05-07 23:05 ET | Gold location = ward + block_code only | Bronze has no neighborhood/lat/long/address |
| 2026-05-07 23:05 ET | Gold surrogate keys named _id (md5 hash) | _sk reserved for MVP 3+ |
| 2026-05-07 23:05 ET | is_open=false only for Closed | Open/In Progress/On Hold all true |
| 2026-05-07 23:05 ET | scratch/-then-scp workflow for ad-hoc DuckDB queries | Heredocs trip the allowlist |
| 2026-05-07 23:29 ET | Airlayer 0.1.1 via prebuilt aarch64 binary | No Rust toolchain required |
| 2026-05-07 23:29 ET | Datasource config in config.yml, not on CLI | Airlayer 0.1.1 has no --connection flag |
| 2026-05-08 07:22 ET | Semantic location dims = ward + block_code only | Bronze constraint |
| 2026-05-08 07:22 ET | requests.open_requests filter = status != 'Closed' (no join) | Avoids cross-view fan-out |
| 2026-05-08 07:22 ET | config.yml uses model_ref + key_var (oxy 0.5.47 schema) | CLAUDE.md sample stale; doc fix deferred |
| 2026-05-08 07:22 ET | Airlayer entity keys must also be declared as dimensions | airlayer validate requirement |
| 2026-05-08 07:31 ET | oxy build gate downgraded for MVP 1 | oxy validate + airlayer query -x cover the intent |
| 2026-05-08 09:02 ET | Target persona = city analyst, not general resident | Power user; defers /about, charts, exports |
| 2026-05-08 09:02 ET | Trust bar: extreme trustability, not just trustworthy | Citations, SQL, row counts in every response |
| 2026-05-08 09:02 ET | Tailscale pulled forward from MVP 3 to MVP 1 | Operational necessity; closes :3000 |
| 2026-05-08 09:02 ET | STANDARDS.md is single-file spec for "done done" | No duplication elsewhere |
| 2026-05-08 09:02 ET | /trust page dynamic (admin schema driven) | Yes/no on data health today |
| 2026-05-08 09:02 ET | /metrics auto-generated from Airlayer YAML | Single source of truth for definitions |
| 2026-05-08 09:02 ET | /about page deferred from MVP 1 | Not analyst persona |
| 2026-05-08 09:02 ET | Long-form .qmd docs deferred from MVP 1 | dbt docs sufficient |
| 2026-05-08 09:02 ET | Exports/charts/follow-ups/anomalies deferred to MVP 2+ | Single experience focus |
| 2026-05-08 09:02 ET | Allowlist: broad patterns, not per-message regex | Ergonomics + narrow deny-by-omission |
| 2026-05-08 10:30 ET | /etc/environment canonical for SSH-visible env vars | Option A from three options; single-user EC2 makes mode 644 trivial |
| 2026-05-08 10:30 ET | systemd unit gets explicit Environment= directives | Two sources of truth, isolation between SSH and service contexts |
| 2026-05-08 10:30 ET | oxy build deferred gate fully resolved | Embeddings built during FR pass |
| 2026-05-08 10:30 ET | Allowlist frame: tool-family-allow + destructive-deny | Per-command lists are a treadmill |
| 2026-05-08 11:30 ET | Sequencing locked: 0.5 → 1 → 2 → 3 → 4 → 5 | Demo broken first; security gap second; deps from there |
| 2026-05-08 11:30 ET | Plans touching environment-specific mechanisms verify empirically in pre-flight | Two prior failures (Airlayer-bundled, ~/.profile) confirm pattern |
| 2026-05-08 11:30 ET | Portal /chat link directly to :3000 for MVP 1 | Subdomain (Option C) deferred |
| 2026-05-08 11:30 ET | Plan 1 Deliverable 4 surfaces Tailnet target choice mid-execution | IP vs MagicDNS vs other — Gordon decides |
| 2026-05-08 11:15 ET | LOG.md split into summary + docs/sessions/ archive | Plan A refactor — bounded LOG.md, on-demand session retrieval |

---

## Active Blockers

> Resolved blockers live in [`docs/log-archive.md`](docs/log-archive.md).

None at this time.

---

## Pointers

- Older sessions: [`docs/sessions/`](docs/sessions/)
- Older decisions and resolved blockers: [`docs/log-archive.md`](docs/log-archive.md)
- "Sign-off Status" (formerly "Accomplishments by MVP") moved to [`TASKS.md`](TASKS.md)
