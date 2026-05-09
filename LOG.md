# LOG.md — Captain's Log Summary

> Single-screen view of project state. Full session narratives live in [`docs/sessions/`](docs/sessions/).

---

## Plans Registry

> Canonical plan sequence locked in Session 9 (2026-05-08). Each plan is named `Plan <number> — <label>` per Rule 9 of [session-starter.md](session-starter.md). Reference plans by full name in commits and LOG entries. Plans 0–1 were scoped at Session 9; later slots had only their slot reserved, scoped when picked up.

| # | Name | Status | Closed in |
|---|------|--------|-----------|
| 0 | FR loose ends | done | Session 8 |
| 0.5 | Portal /chat fix | done | Session 11 |
| 1 | Tailscale | done | Session 12 |
| 2 | Admin DQ Overnight | done | Session 13 |
| 3 | MVP 1 Loose Ends + Doc Reconciliation | in progress | Session 14 |
| 4 | Trust Page + Answer Agent | queued | — |
| 5 | TBD (slot reserved by Session 9) | unscoped | — |

**Session counter:** contiguous 1–N, tracked by Code; all session files present at [`docs/sessions/`](docs/sessions/). Chat-side planning notes have their own threading and may diverge — Code's counter is authoritative for the project record.

---

## Current Status

**Active MVP:** MVP 1 — Static data → DuckDB → Airlayer → Answer Agent chat UI
**Phase:** Overnight run D0–D3 closed end-to-end. Limitations registry seeded; dbt docs populated and live at `/docs`; admin DQ framework verified across two `./run.sh` runs (3 admin tables populating correctly, baselines frozen, dbt results captured); `/metrics` page generated and live. Public attack surface still port 80 only. FR pass still intact. Next: SETUP/CLAUDE/ARCHITECTURE doc updates, then `/trust` page + trust contract pass on the Answer Agent.
**Open security gap:** None. Closed in Plan 1.
**Last Updated:** 2026-05-08 22:55 ET (Session 13 — overnight D0–D3 closed)

---

## Recent Sessions

### Session 13 — 2026-05-08 16:30 ET — Plan 2 — Admin DQ Overnight
[full narrative](docs/sessions/session-13-2026-05-08-overnight-d0-d3.md)

- **Goal:** Land four overnight deliverables under Plan 2 — Admin DQ Overnight: limitations registry, dbt docs population + `/docs` route, admin DQ framework + `run.sh`, `/metrics` page.
- **Shipped:** D0 limitations registry (README + 2 seeds, STANDARDS §7 resolved); D1 dbt docs (1+24 bronze, 4+47 gold descriptions; nginx `/docs` alias fixed; `/home/ubuntu` 750→755 for www-data traversal); D2 admin DQ (3 models + `dlt/load_dbt_results.py` + `run.sh`; verified across 2 `./run.sh` runs); D3 `/metrics` generator (live at `/metrics`); plus pre-flight `--ssh=false` revert + allowlist restore. Commits `6c75210` `d3a1778` `06f1776` `72345c4` `edb508d` `fddec4e`.
- **Decisions:** 8 decisions — see Decisions Log
- **Status:** complete
- **Next:** Update SETUP/CLAUDE/ARCHITECTURE for Tailnet access + nginx docroot + venv pattern. Then `/trust` page and trust contract pass.

### Session 12 — 2026-05-08 13:30 ET — plan-1-tailscale
[full narrative](docs/sessions/session-12-2026-05-08-plan-1-tailscale.md)

- **Goal:** Close public `:3000` gap via Tailscale; strip broken public chat CTAs.
- **Shipped:** Tailscale 1.96.4 on EC2 (MagicDNS `oxygen-mvp.taildee698.ts.net`); SSH alias repointed; AWS SG `:22`/`:3000` deleted; portal hybrid update (drop nav+asset CTAs, hero `Private beta` pill); commit `ae20c94`.
- **Decisions:** 3 decisions — see Decisions Log
- **Status:** complete
- **Next:** Update SETUP.md/CLAUDE.md/ARCHITECTURE.md for new access pattern + nginx docroot.

### Session 11 — 2026-05-08 11:35 ET — portal-chat-fix
[full narrative](docs/sessions/session-11-2026-05-08-portal-chat-fix.md)

- **Goal:** Make portal chat link actually open the chat UI (Option A: direct `:3000` link).
- **Shipped:** 3 portal hrefs repointed; nginx `location /chat` removed; deployed; commit 6d76594. Gates 1-4 green, gate 5 = Gordon's browser test.
- **Decisions:** 0 new (Option A captured in Session 9) — see Decisions Log
- **Status:** complete (pending Gordon's browser confirmation)
- **Next:** Plan 1 (Tailscale) — its Deliverable 4 will update the same hrefs to a Tailnet target.

### Session 10 — 2026-05-08 11:15 ET — log-refactor
[full narrative](docs/sessions/session-10-2026-05-08-log-refactor.md)

- **Goal:** Split LOG.md into bounded summary + docs/sessions/ archive; establish frontmatter, body, and rotation rules.
- **Shipped:** LOG.md 682 → 161 lines; 9 session files migrated; docs/log-archive.md created; CLAUDE.md protocol rewritten; commit a72bd2a.
- **Decisions:** 0 new (architectural choice made in Session 9) — see Decisions Log
- **Status:** complete
- **Next:** Hand Plan 0.5 to Code.

### Session 9 — 2026-05-08 11:30 ET — plans-0.5-and-1-queued
[full narrative](docs/sessions/session-09-2026-05-08-plans-0.5-and-1-queued.md)

- **Goal:** Close Plan 0 feedback, queue Plans 0.5 + 1, capture meta-lessons.
- **Shipped:** Plan 0.5 (portal /chat fix) and Plan 1 (Tailscale) drafted with environment-assumption pre-flight; Plan 0 confirmed closed.
- **Decisions:** 4 decisions — see Decisions Log
- **Status:** complete
- **Next:** Hand Plan 0.5 to Code.

---

## Earlier Sessions

- **Session 8** — 2026-05-08 10:00 ET — Plan 0 loose ends; `/etc/environment` env-var contract; allowlist broadened (D7 tool-family + destructive-deny); commits `e5e94e3` `196cf28`. [full narrative](docs/sessions/session-08-2026-05-08-plan-0-loose-ends.md)
- **Session 7** — 2026-05-08 morning ET — FR pass; Answer Agent live, agents/answer_agent.agent.yml; 2024=113,961 ✓, 2026=48,806 ✓. [full narrative](docs/sessions/session-07-2026-05-08-fr-answer-agent.md)
- **Session 6** — 2026-05-08 09:02 ET — MVP 1 scope sharpening + STANDARDS.md. [full narrative](docs/sessions/session-06-2026-05-08-mvp1-scope-sharpening.md)
- **Session 5** — 2026-05-07 22:00 ET → 2026-05-08 07:00 ET — Cleanup + overnight run (gold + Airlayer + semantic). [full narrative](docs/sessions/session-05-2026-05-07-cleanup-and-overnight-run.md)
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
| 2026-05-08 13:56 ET | Portal chat CTA = hybrid (drop nav+asset, hero `Private beta` pill) | No Tailnet hostname leakage; hero pill keeps visual hierarchy at the page centerpiece |
| 2026-05-08 13:56 ET | SSH alias targets MagicDNS hostname, not Tailnet IP | IP-stable across node re-registrations |
| 2026-05-08 13:56 ET | ~~Tailscale SSH (`--ssh`) enabled alongside OpenSSH pubkey~~ → reverted same day | Initial "belt-and-suspenders" framing was wrong: Tailscale SSH preempts port 22 for Tailnet peers via `tailscaled be-child`, bypassing OpenSSH PAM and silently breaking `/etc/environment` env-var loading (PATH/ANTHROPIC_API_KEY/OXY_DATABASE_URL all missing in non-interactive SSH). See 2026-05-08 16:45 ET row. |
| 2026-05-08 13:58 ET | MVP 1 chat is private-beta-only; public portal advertises it but doesn't link to it | Tailnet-only access; no public hostname leak; portal shows `Private beta` pill instead of CTA |
| 2026-05-08 17:05 ET | Limitations registry → `docs/limitations/` (Option b) | Markdown + YAML frontmatter; single canonical location for Answer Agent and `/trust` page; resolves STANDARDS.md §7 |
| 2026-05-08 17:30 ET | nginx docroot is `/var/www/somerville` (active `somerville` site), NOT `/var/www/html` | Default site isn't enabled; `sites-enabled/somerville` is the only active server block; documented to avoid Plan 1 D4-style misdeploy recurrence |
| 2026-05-08 17:35 ET | `/home/ubuntu` mode 750 → 755 | Allows nginx www-data to traverse and serve `/docs` from in-repo `dbt/target/`; single-user EC2; sensitive subdirs (`.ssh`) keep their own 700 |
| 2026-05-08 18:00 ET | Admin DQ — dlt landing table at `main_bronze.raw_dbt_results_raw`; no bronze dbt view; natural keys (no `test_sk`/`test_run_sk`) | Avoids dbt-VIEW vs duckdb-TABLE name conflict; admin models reference the table directly. Surrogate keys can be added later if joins need them. |
| 2026-05-08 18:15 ET | `dim_data_quality_test` uses `is_incremental()` filter on `test_id` | Baselines seeded exactly once and stay frozen. Re-certifying is a manual update; out of scope for MVP 1. |
| 2026-05-08 22:10 ET | `/metrics` generator → `scripts/generate_metrics_page.py` | Pure-Python build tooling reading `semantics/views/*.view.yml`; portal stays static; runs as `run.sh` step 7/7; resolves STANDARDS.md §7 |
| 2026-05-08 22:30 ET | Allowlist policy restored — Plan 0 D7 (tool-family-allow + destructive-deny) had regressed | settings.json now has `Bash(python3 *)`, `Bash(dbt *)`, etc. plus deny entries (`git reset --hard`, `git push --force`, `rm -rf`, `sudo rm/dd/bash/sh/-i/-s`); narrow `sudo nginx`/`sudo systemctl … nginx` allowed for ops-side work |
| 2026-05-08 23:00 ET | Plan-naming convention adopted (Rule 9) | Every plan gets a number + content-bearing label; full name used in commits and LOG; lives in session-starter.md |
| 2026-05-08 23:00 ET | Session 9 plan sequence is canonical; chat-introduced names fill reserved slots | Plans 0.5 and 1 were fully scoped at Session 9; slots 2–5 were reserved without scope. Chat's later "Plan 2 / Plan 3 / Plan 4" naming aligns with those slots — no relabeling required. Plan 5 still unscoped. |
| 2026-05-08 23:00 ET | Session counter is contiguous 1–N, tracked by Code (authoritative) | Chat-side planning notes may have a separate count that diverged after Session 6 (Code-led sessions weren't logged on Chat's side). Code's counter is the project record going forward. |
| 2026-05-08 23:00 ET | Allowlist "regression" was an incomplete implementation, not a regression | Plan 0 D7b commit (196cf28) only added git write-op patterns; tool-family wildcards and deny list never landed in committed settings.json until Session 13's edb508d. TASKS.md `[x]` mark was based on settings.local.json (gitignored) edits that were never mirrored to settings.json. No active overwriter; root cause was a partial commit. |
| 2026-05-08 16:45 ET | Disable Tailscale SSH (`tailscale set --ssh=false`) — OpenSSH+pubkey only | Restores `/etc/environment` loading via PAM. We weren't using Tailscale SSH features (single dev, single MBP, `.pem` deployed). Re-enable + fix env-var path properly when a real driver appears (second device, teammate). |

---

## Active Blockers

> Resolved blockers live in [`docs/log-archive.md`](docs/log-archive.md).

None at this time.

---

## Pointers

- Older sessions: [`docs/sessions/`](docs/sessions/)
- Older decisions and resolved blockers: [`docs/log-archive.md`](docs/log-archive.md)
- "Sign-off Status" (formerly "Accomplishments by MVP") moved to [`TASKS.md`](TASKS.md)
