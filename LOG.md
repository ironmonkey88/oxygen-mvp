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
| 3 | MVP 1 Loose Ends + Doc Reconciliation | done | Session 14 |
| 4 | Trust Page | done | Session 15 |
| 6 | Answer Agent + Trust Contract | done | Session 18 |
| 8 | Limitations Registry Expansion | done | Session 18 |
| 7 | MVP 1 Sign-off Sweep | done (sign-off pending Gordon's decisions on 2 rows) | Session 19 |
| 5 | Tech Debt Sweep | done | Session 20 |
| 9 | Allowlist Coverage, Once and For All | done | Session 16 |
| 9 rev 2 | Allowlist Coverage + Bash Safety Hook | done | Session 17 |

**Session counter:** contiguous 1–N, tracked by Code; all session files present at [`docs/sessions/`](docs/sessions/). Chat-side planning notes have their own threading and may diverge — Code's counter is authoritative for the project record.

---

## Current Status

**Active MVP:** MVP 1 — Static data → DuckDB → Airlayer → Answer Agent chat UI
**Phase:** Overnight pass complete (Sessions 22–24). Session 22 surfaced the Oxygen onboarding gate; Session 23 codified the verification-gates standard + retroactive swept §6; Session 24 closed Sessions C D1 + D2 (systemd deploy + reboot test PASS, repo-clonable tick) and completed the 5/5 bench re-verification + `./run.sh` end-to-end clean. **MVP 1 sign-off now has 1 open box**: §5.8 row 2 (`/chat` UI walkthrough or CLI-only reinterpretation). Every other §6 box is `[x]` with re-verified evidence from this overnight pass.
**Open security gap:** None. Closed in Plan 1.
**Last Updated:** 2026-05-11 00:15 ET (Session 24 — systemd deploy + reboot test + bench 5/5 + run.sh re-verify)

---

## Recent Sessions

### Session 24 — 2026-05-10 23:20 ET → 00:15 ET — systemd-deploy-and-bench-completion
[full narrative](docs/sessions/session-24-2026-05-10-systemd-deploy-and-bench-completion.md)

- **Goal:** Resume the overnight brief after Session 22/23 wake-up; close bench Q2/Q4/Q5 gaps, run `./run.sh` end-to-end, ship Session C D1 (systemd deploy + reboot) + D2 (repo-clonable tick).
- **Shipped:** Bench 5/5 re-verified (Q1 113,961, Q2 49,782 YTD, Q3 top types, Q4 NA sentinel, Q5 satisfaction 4.44/5); `./run.sh` exit 0 (drift-fail guardrail PASS at new baseline 1,169,935); `oxy.service` deployed with hardened `After=docker.service Requires=docker.service`; **reboot test PASSED** — oxy back active 7s after kernel up, volume persistence proven (Session 22 user record survived); STANDARDS §3.2 row 4 + §4.5 row 1 both `[x]`; §6 §3.2 4/5 → 5/5, §4.5 2/3 → 3/3; SETUP.md §11 updated.
- **Decisions:** 3 decisions — see Decisions Log
- **Status:** complete
- **Next:** MVP 1 sign-off blocked on Gordon's §5.8 row 2 call (UI walkthrough vs CLI-only reinterpretation). Every other §6 box re-verified `[x]`.

### Session 23 — 2026-05-10 22:05 ET → 22:45 ET — verification-gates-standard
[full narrative](docs/sessions/session-23-2026-05-10-verification-gates-standard.md)

- **Goal:** Codify a self-verification standard for live-functional `[x]` ticks in CLAUDE.md, then sweep STANDARDS §6 boxes ticked since Session 15 and flip any that no longer hold.
- **Shipped:** CLAUDE.md "Verification gates for `[x]` ticks" subsection appended; STANDARDS §6 retroactive-verification banner + inline timestamps on smoke rows 1-5; §5.8 row 2 (`/chat`) flipped `[x]` → `[ ]` (port-80 404, Tailnet `:3000` at onboarding screen); §6 Layers Knowledge Product roll-up 6/6 → 5/6; TASKS.md MVP 1 sign-off chat-UI row flipped `[x]` → `[!]`.
- **Decisions:** 3 decisions — see Decisions Log
- **Status:** complete
- **Next:** MVP 1 sign-off session re-runs all 5 Plan 6 D3 bench questions + `./run.sh` end-to-end + re-verifies every §6 `[x]` against the new standard.

### Session 22 — 2026-05-10 21:40 ET → 22:05 ET — oxygen-onboarding-gate
[full narrative](docs/sessions/session-22-2026-05-10-oxygen-onboarding-gate.md)

- **Goal:** Diagnose Oxygen's chat-UI onboarding screen (Gordon hit "Welcome to Oxygen / Create organization" tonight) and restore the org/workspace state so the web UI works again.
- **Shipped:** Pre-flight EC2 sync resolved (drop-and-pull pattern, 4 files matched origin/main, 1 was the stale 4,187 dept-tags version); Oxygen state recon — DuckDB intact (1,169,935 rows), postgres container up with persistent volume but `organizations` = 0, only user is tonight's `local-user@example.com`; CLI agent regression PASS (2024 → 113,961 with full trust contract); decision gate hit "STOP — Code can't drive a browser."
- **Decisions:** 2 decisions — see Decisions Log
- **Status:** blocked (browser-only onboarding flow required; Code-safe path doesn't exist)
- **Next:** Gordon decides — walk the UI wizard tomorrow (then re-tick §5.8 row 2 on a passing SPA query), OR reinterpret §5.8 row 2 as CLI-only and sign off on the `oxy run` evidence.

### Session 21 — 2026-05-10 16:00 ET → 16:45 ET — git-allowlist-fix
[full narrative](docs/sessions/session-21-2026-05-10-git-allowlist-fix.md)

- **Goal:** Fix git read-op allowlist gap that blocked overnight sessions all weekend: piped git commands (`git -C <path> op 2>&1 | head`) were prompting because `*` does not match `|` in allowlist patterns.
- **Shipped:** Pipe patterns added to worktree `settings.json` in merge commit `997dc04` (`Bash(git * | *)`, `Bash(git -C * * | *)`, `Bash(git * | * | *)`); missing read-ops added (`rev-list`, `ls-remote`, broad `branch *`); duplicate `Bash(bash *)` removed; CLAUDE.md pipe-coverage notes added.
- **Decisions:** 1 decision — see Decisions Log
- **Status:** complete
- **Next:** Gordon merges `claude/gifted-cartwright-9b6bac` to main so pipe patterns reach all branches; then resume Plan 10/11. *(merge landed 2026-05-10 21:30 ET — `d71e7d0..5ebb569` pushed to origin/main)*

### Session 20 — 2026-05-09 21:45 ET → 2026-05-10 09:55 ET — Plan 5 — Tech Debt Sweep
[full narrative](docs/sessions/session-20-2026-05-09-plan-5-tech-debt.md)

- **Goal:** Hygiene pass to close out the rev 2 overnight batch — settings reconciliation, dbt profiles example, scratch hygiene, run.sh step-text consistency, doc reconciliation.
- **Shipped:** D1 settings: pruned settings.local.json to empty, added `Bash(bash *)` to settings.json, CLAUDE.md "what belongs where" subsection (commit `b274ae7`); D2 dbt: `dbt/profiles.example.yml` + SETUP §8 rewrite (commit `1f0d05d`); D3 scratch: nothing to prune; D4 run.sh: no drift to fix; D5 docs: CLAUDE.md Run Order 7→9 steps + 5b, ARCHITECTURE.md Run Order bash block + Portal routes table + Process management line corrected, TASKS.md "Deliverable B" closed.
- **Decisions:** 1 decision — see Decisions Log
- **Status:** complete
- **Next:** Gordon's call on the two open MVP 1 sign-off boxes (systemd, repo-public). Then whatever new plan he stacks.

---

## Earlier Sessions

- **Session 19** — 2026-05-09 21:05 ET → 21:45 ET — Plan 7 MVP 1 Sign-off Sweep; STANDARDS §6 walked (23/25 `[x]` with evidence); portal copy refresh deployed (hero, stats, asset cards, "Built on Oxygen" prose); LOG Active Blockers row written with 2 Gordon-decision boxes. [full narrative](docs/sessions/session-19-2026-05-09-plan-7-signoff-sweep.md)
- **Session 18** — 2026-05-09 19:40 ET → 21:05 ET — Plans 6 + 8 — Trust Contract + Limitations Expansion; trust contract in `agents/answer_agent.agent.yml` (4-section reply, runtime renders SQL+result, prompt-enforced citations + limitations); 10 limitation entries + `_index.yaml` + `scripts/build_limitations_index.py` + run.sh step 9/9; 5/5 test bench pass with transcripts in `scratch/plan6_test_bench/`; STANDARDS §4.1 4/4, §4.4 row 2, §5.7 4/4. [full narrative](docs/sessions/session-18-2026-05-09-plans-6-and-8-trust-contract-and-limitations.md)
- **Session 17** — 2026-05-09 19:18 ET → 19:35 ET — Plan 9 rev 2 — Allowlist Coverage + Bash Safety Hook; `.claude/hooks/block-dangerous.sh` denies risky shell shapes (chains, `$(...)`, leading `cd`/`export`) with loop-keyword + arithmetic carve-outs; wired into PreToolUse alongside the task-warning hook; merged 2 allow + 8 deny patterns; `scripts/check_allowlist_coverage.sh` rewritten with 11 idiom + 13 hook assertions. [full narrative](docs/sessions/session-17-2026-05-09-plan-9-rev2-bash-safety-hook.md)
- **Session 16** — 2026-05-09 ~17:30 ET — Plan 9 — Allowlist Coverage, Once and For All; structural restructure (defaultMode acceptEdits, top-level Read/Write/Edit, $schema), broaden allow patterns (verification-idiom cohort), `scripts/check_allowlist_coverage.sh` first pass clean. [full narrative](docs/sessions/session-16-2026-05-09-plan-9-allowlist-coverage.md)
- **Session 15** — 2026-05-09 12:53 ET → 13:30 ET — Plan 4 Trust Page; `scripts/generate_trust_page.py`, run.sh step 8/8 + portal index sync, nginx /trust location, portal nav links, synthetic-fail render check green→red→green. Commits `300acee` + close. [full narrative](docs/sessions/session-15-2026-05-09-plan-4-trust-page.md)
- **Session 14** — 2026-05-08 23:00 ET → 2026-05-09 08:36 ET — Plan 3 hygiene + drift-fail verification; allowlist patterns in committed settings.json, Plans Registry + Rule 9, SETUP/CLAUDE/ARCHITECTURE/STANDARDS catch-up, `nginx/somerville.conf` canonical config, transcript-timestamp rule, drift-fail end-to-end. Commits `6e34fdc` `7346dde` `093b220` `e3a79bb` `0a4c53c` `ee4c488`. [full narrative](docs/sessions/session-14-2026-05-08-plan-3-mvp1-loose-ends.md)
- **Session 13** — 2026-05-08 16:30 ET — Plan 2 Admin DQ Overnight; D0–D3 (limitations registry seed, dbt docs population + `/docs` route, admin DQ framework + run.sh, `/metrics` page). Commits `6c75210` `d3a1778` `06f1776` `72345c4` `edb508d` `fddec4e`. [full narrative](docs/sessions/session-13-2026-05-08-overnight-d0-d3.md)
- **Session 12** — 2026-05-08 13:30 ET — Plan 1 Tailscale; 1.96.4 on EC2, MagicDNS hostname, SSH alias repointed, AWS SG `:22`/`:3000` closed, portal hybrid update (commit `ae20c94`). [full narrative](docs/sessions/session-12-2026-05-08-plan-1-tailscale.md)
- **Session 11** — 2026-05-08 11:35 ET — Plan 0.5 portal /chat fix; 3 hrefs repointed to `:3000`, nginx `location /chat` removed (commit `6d76594`); gates 1-4 green. [full narrative](docs/sessions/session-11-2026-05-08-portal-chat-fix.md)
- **Session 10** — 2026-05-08 11:15 ET — Log refactor: LOG.md split into bounded summary + `docs/sessions/` archive; frontmatter/body/rotation rules established (commit `a72bd2a`). [full narrative](docs/sessions/session-10-2026-05-08-log-refactor.md)
- **Session 9** — 2026-05-08 11:30 ET — Plans 0.5 + 1 queued; sequencing locked (0.5→1→2→3→4→5); pre-flight rule for env-specific assumptions. [full narrative](docs/sessions/session-09-2026-05-08-plans-0.5-and-1-queued.md)
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
| 2026-05-09 08:36 ET | nginx config: `nginx/somerville.conf` in repo is canonical source of truth | Deploy via `scp` + `sudo cp` + `sudo nginx -t` + `sudo systemctl reload nginx`. Closes the implicit-knowledge gap that caused the Plan 1 D4 wrong-docroot detour. |
| 2026-05-09 08:36 ET | Drift-fail flows to non-zero pipeline exit via singular dbt test + run.sh step 5b | `dq_drift_fail_guardrail.sql` fires on any `fct_test_run.status='fail'` for the latest run_id; `run.sh` final exit = max of bronze/gold-test-exit and admin-test-exit. Verified end-to-end via 30% synthetic perturbation. |
| 2026-05-09 08:36 ET | Transcript-timestamp rule | Code emits `[YYYY-MM-DD HH:MM ET] <label>` markers at deliverable starts, pauses/blockers, and before long-running commands. Lives in CLAUDE.md LOG Logging Protocol. |
| 2026-05-08 16:45 ET | Disable Tailscale SSH (`tailscale set --ssh=false`) — OpenSSH+pubkey only | Restores `/etc/environment` loading via PAM. We weren't using Tailscale SSH features (single dev, single MBP, `.pem` deployed). Re-enable + fix env-var path properly when a real driver appears (second device, teammate). |
| 2026-05-09 13:30 ET | `/trust` deploy pattern mirrors `/metrics` exactly | `portal/trust.html` in repo, `run.sh` copies to `/var/www/somerville/trust.html`, nginx serves via `try_files` on `location = /trust`. Single pattern for both auto-generated trust artifacts. |
| 2026-05-09 13:30 ET | `run.sh` syncs `portal/index.html` → `/var/www/somerville/index.html` as a final step | Static portal nav edits landed on EC2 only after a manual scp on first deploy; auto-syncing closes the gap so the canonical source-of-truth at `portal/index.html` stays in lock-step with what nginx serves. |
| 2026-05-09 13:30 ET | `/chat` route satisfied by Private beta pill, not a public route link | Session 11/12 made chat Tailnet-only at `:3000`; portal advertises but doesn't link. STANDARDS.md §5.8 "Routes live: /chat" is interpreted as covered by that convention; Plan 7 sign-off owns any rewording. |
| 2026-05-09 13:30 ET | Synthetic-fail render check is part of Plan 4 done-done | Plan 3 D3 verified the drift-fail mechanism produces fail rows in `fct_test_run`, but the trust page's red-branch CSS hadn't been exercised end-to-end. UPDATE → regen → curl → restore loop confirmed the visual flip green→red→green. |
| 2026-05-09 19:05 ET | Plan 9 lands as a dedicated, separately-committed plan | Third allowlist-coverage incident (Sessions 13, 14, 15) — pattern is structural; rolling it into the rev 2 batch would obscure the fix. |
| 2026-05-09 19:05 ET | `defaultMode: "acceptEdits"` adopted at the `permissions` level | Single high-leverage setting that auto-accepts Edit/Write/Read on project files; prerequisite for clean unattended runs without weakening Bash boundaries. |
| 2026-05-09 19:05 ET | `Bash(sed *)` allowed despite Session 13 incident | Destructive-deny (`rm -rf`, `git reset --hard`, `sudo bash/sh`, `sudo rm/dd`) bounds blast radius; `sed -i` on tracked file is recoverable via `git restore`, on untracked file is a manual-typo class problem. |
| 2026-05-09 19:05 ET | `Bash(npm *)` / `Bash(pnpm *)` allowed prophylactically | Agent and portal don't have Node deps today, but if they grow them, future sessions shouldn't stall on the first install. |
| 2026-05-09 19:05 ET | No blanket `sudo *` deny | Granular deploy-path sudo allows (`sudo cp/mv/ln/chmod/chown/nginx/systemctl …`) used by `run.sh`; blanket deny would prompt every deploy. Granular allows + granular denies stay. |
| 2026-05-09 19:35 ET | Plan 9 rev 2 — structural fix (PreToolUse hook), not more allow patterns | Allowlist syntax cannot match compound commands (`safe-cmd && safe-cmd` matches no single rule). Adding more allow entries was the wrong shape. The hook denies risky structural shapes; the allowlist handles per-command policy. Per Anthropic docs and GitHub issue #20085. |
| 2026-05-09 19:35 ET | Loop-keyword carve-out in the hook regex | Plan-as-handed-off would have blocked `for ... ; do ... ; done` because `; do` matches `;\s`. Hook strips `; (do\|then\|done\|fi\|else\|elif)` before checking for `;` chains. Verified end-to-end via 13 hook-deny/allow assertions. |
| 2026-05-09 19:35 ET | Allow merge, not allow replace | Plan-as-handed-off proposed a "final shape" allow array that dropped ~40 patterns currently in `settings.json` (airlayer, duckdb, gh pr, run.sh, granular nginx sudo). Merge-not-replace preserves Plan 9 rev 1's surface area; rev 2 adds `Bash(git *)` bare and `Bash(sudo ln *)` broader, plus 8 new deny patterns. |
| 2026-05-09 19:35 ET | Hook activates mid-session, not just on session start | Settings re-read per tool call (existing task-warning hook already demonstrates this). Documented in CLAUDE.md Bash Safety so Code knows the hook is live as soon as `settings.json` lands. |
| 2026-05-09 21:05 ET | Trust contract is prompt-only (no post-processing wrapper) | Oxygen runtime renders SQL + result-table natively; the agent's `Output:` section is fully prompt-controlled. Citations + row-count line + limitations live in `system_instructions`. Verified against 5/5 test bench questions. STANDARDS §7 open question resolved. |
| 2026-05-09 21:05 ET | Limitations registry consumed via index file, not full bodies | Initial implementation glob'd `docs/limitations/*.md` into agent context; per-call input ballooned to ~30K tokens, hit Anthropic rate limit (30K/min) on multi-turn questions (Q3, Q5 both failed first attempt). Switched to `docs/limitations/_index.yaml` (id+title+severity+affects+path triples, ~2KB total) generated by `scripts/build_limitations_index.py`. Agent cites by id; analyst opens the file for full detail. |
| 2026-05-09 21:05 ET | Limitation `affects:` use bare/granular tokens, not view-name-only | Initial seed `2024-survey-columns-sparse.md` had `affects: [requests]` which fired on every requests-view query. Tightened to specific column names (`accuracy`, `courtesy`, …). All Plan 8 entries follow this granular pattern: column names, qualified view.dim, or sentinel tokens (`current_date`, `deploy.oxy_build`). |
| 2026-05-09 21:05 ET | Test bench evidence is gitignored under `scratch/plan6_test_bench/` | Per the brief — these are evidence (proof of life), not artifacts (input to the system). The session file summarizes; the analyst can re-run the bench against the live agent at any time to regenerate. |
| 2026-05-09 21:45 ET | MVP 1 sign-off held pending Gordon's call on systemd + repo-public | Plan 7 D3: every box automatable by Code is `[x]`. Two open boxes: §3.2 row 4 (Oxygen as systemd vs. nohup-stable) and §4.5 row 1 (repo public vs. private team-clonable). Both are non-Code decisions; not auto-flipped. |
| 2026-05-09 21:45 ET | Replaced /erd + /tasks asset cards with /trust + /metrics | The /erd and /tasks routes don't exist; linking to dead routes is marketing-shaped. Swapped for /trust and /metrics, which are live and central to the trust contract. |
| 2026-05-10 16:40 ET | `Bash(git * | *)` + `Bash(git -C * * | *)` + `Bash(git * | * | *)` added to worktree `settings.json` | Root cause of weekend git stalls: `*` in allowlist patterns does not match `|`; piped forms need explicit `|`-containing patterns. `Bash(git * | *)` is intentionally broad — deny list still blocks destructive forms in their un-piped shapes; piping `git reset --hard` is not a realistic attack vector. Added to `claude/gifted-cartwright-9b6bac` branch; pending Gordon's merge to main. |
| 2026-05-10 09:55 ET | settings.local.json reset to empty allow array | Diff against settings.json showed every accumulated pattern was redundant with a tool-family wildcard. Empty local + `Bash(bash *)` in settings.json + new CLAUDE.md "what belongs where" codifies the pattern: local is per-machine scratch, committed is project-wide policy. |
| 2026-05-10 10:16 ET | Worktree-scoped settings.local.json writes allowed in committed settings.json | Plan 5 D1 hotfix (commit `b78d3d5`) — explicit `Read/Write(.claude/worktrees/*/.claude/settings.local.json)` patterns. Future sessions can re-empty the local file without prompting Gordon. |
| 2026-05-10 10:35 ET | Agent prompt: never state a calendar year in prose without querying it | Plan 6 follow-on (commit `3603136`). Q2 test bench exposed Sonnet 4-6 hallucinating "2025" when SQL evaluated `year(current_date)` to 2026. Hard rule: if SQL uses `current_date` and prose needs the year, run `SELECT year(current_date)` first. |
| 2026-05-10 10:55 ET | block-code-padded sentinel form corrected: "NA"-space-padded, not whitespace | Plan 8 follow-on (commit `3ea828e`). Q4 test bench showed top block was `"NA             "` (NA + 13 spaces, 38% of rows). |
| 2026-05-10 11:05 ET | dept-tags-as-booleans coverage corrected: 987 / 0.08%, not 4,187 / 0.36% | Plan 8 follow-on (commit `1877ee0`). Audited via `scratch/audit_limitation_claims.py`. |
| 2026-05-10 21:30 ET | `claude/gifted-cartwright-9b6bac` fast-forward-merged to `origin/main` (`d71e7d0..5ebb569`) | 16 commits brought across: Plan 5 D1 follow-on (git pipe patterns universalised), Plans 6/8 follow-ons (block-code-padded sentinel "NA" not whitespace; dept-tags 987 not 4187), Sessions 17-21 narrative archive, Stop hook `systemMessage` fix, `block-dangerous.sh` Bash Safety hook + 3-tier allowlist policy. 6 worktrees compressed to 2 (main + active session); 7 fully-merged local branches still present and require Gordon's per-prompt approval to `git branch -d`. |
| 2026-05-10 22:00 ET | Session A halted at Oxygen onboarding gate — chat-UI restoration deferred to Gordon | Postgres has 0 orgs, 1 user (`local-user@example.com` created tonight 20:54 ET). `oxy` CLI has no org subcommand; REST `/api/orgs` returns `[]` but the full setup chain requires authenticated SPA flow. Brief's hard-stop: "If the only path is browser UI clicks (no CLI/API equivalent), STOP — Code can't drive a browser." Data + agent layers fully healthy: DuckDB 1,169,935 rows, `oxy run` 2024 → 113,961 with full trust contract, `/trust` 36/36 pass, `/metrics` lists both measures, `/docs` 1.8MB. |
| 2026-05-10 22:30 ET | New CLAUDE.md subsection "Verification gates for `[x]` ticks" | Codifies the static-artifact vs. live-functional distinction; mandates re-verification of live-functional boxes at every MVP sign-off (not inherited from earlier sessions); names `/chat`-shaped state-gated routes as requiring either UI walkthrough or explicit inline reinterpretation. Driven by Session 22's discovery that STANDARDS §5.8 row 2 was `[x]` based on a "Private beta pill" reinterpretation buried in an inline note, and Session 7's TASKS.md chat-UI tick (113,961 / 48,806) was either CLI-mislabelled or wiped along with prior org state. |
| 2026-05-10 22:40 ET | STANDARDS §5.8 row 2 (`Routes live: /chat`) flipped `[x]` → `[ ]`; §6 Layers `§5.8 6/6` → `5/6` | Port-80 `/chat` returns 404 (removed in Plan 1 D4); the Tailnet `:3000` chat that the "Private beta" pill advertises is at the onboarding screen (Session 22 — 0 orgs in postgres). The previous interpretation ("pill advertises chat") was structurally true but conditionally load-bearing on a working chat. Gordon decides at MVP 1 sign-off: walk the UI wizard and re-tick, OR reinterpret as CLI-only and re-tick with an inline note. |
| 2026-05-10 23:30 ET | `./run.sh` end-to-end re-verified post-Session-22-sync — clean exit 0 | All 9 steps ran clean; bronze/gold tests exit 0; admin tests exit 0; `dq_drift_fail_guardrail` PASSED at new baseline 1,169,935 rows (variance from frozen 1,168,959 baseline is +0.08%, within tolerance); /trust regenerated at 36/36 pass; metrics + limitations index regenerated. Re-verifies STANDARDS §4.5 row 2 against the new verification-gates standard. |
| 2026-05-10 23:39 ET | Oxygen deployed as systemd service; reboot test PASSED | `/etc/systemd/system/oxy.service` with hardened `After=network.target docker.service` + `Requires=docker.service` + `EnvironmentFile=/etc/environment` + `Restart=always RestartSec=10`. `systemctl enable` symlinked into `multi-user.target.wants`. Reboot test: `sudo reboot` → instance back, oxy active 7s after kernel up, oxy-postgres container recreated against persistent volume, user record from Session 22 survived intact (volume persistence proven). curl :3000 → 200; agent regression 113,961. Hardening beyond SETUP.md §11's original — SETUP.md updated to match what shipped. STANDARDS §3.2 row 4 + §6 §3.2 4/5 → 5/5. |
| 2026-05-10 23:45 ET | STANDARDS §4.5 row 1 (repo-public) reinterpreted as team-clonable; ticked | Pre-authorized by Gordon in overnight brief: "Private, clonable by team — public flip deferred as a separate launch decision, not a sign-off blocker." Inline note added; §6 §4.5 2/3 → 3/3. |
| 2026-05-10 23:55 ET | Bench Q5 re-verified post-reboot after two earlier rate-limit retries | Anthropic 30K/min cap hit during Q4+Q5 parallel batch and the immediate retry (Q5 is heavy — multiple queries, full context including all view files). After ~10 min cooldown during reboot validation, Q5 ran clean: Accuracy 4.39 / Courtesy 4.67 / Ease 4.63 / Overall 4.28, blended 4.44/5.0; both survey-related limitations surfaced. Lesson: bench questions should run sequentially, not parallel, to stay inside the 30K/min input-token window. Plan 6 D3 bench 5/5 fully re-verified across Sessions 23 + 24. |

---

## Active Blockers

> Resolved blockers live in [`docs/log-archive.md`](docs/log-archive.md).

### MVP 1 sign-off blocker as of 2026-05-11 00:15 ET (Session 24 close-out)

Session 24 closed two of the three open boxes; one remains:

| Box | Status | Owner | Notes |
|-----|--------|-------|-------|
| §5.8 row 2 — Routes live: `/chat` | open | Gordon decision | Port-80 `/chat` is 404 (route removed in Plan 1 D4); the Tailnet `:3000` SPA renders the "Create organization" onboarding screen until an org exists (Session 22 — postgres has 0 orgs, 1 user from tonight's signup that survived Session 24's reboot test). CLI path is fully healthy and bench 5/5 re-verified across Sessions 23 + 24. Decision: (a) Gordon walks the UI wizard at `oxygen-mvp.taildee698.ts.net:3000`, creates the org, asks the 2024 question, confirms 113,961, re-ticks the row; or (b) reinterpret §5.8 row 2 as definitively CLI-only (MVP 1's analyst persona uses `oxy run`; SPA chat out of scope), update STANDARDS inline, re-tick. |

Closed in Session 24:
- §3.2 row 4 (systemd) — `oxy.service` deployed, reboot test PASS, volume persistence proven, SETUP.md §11 updated
- §4.5 row 1 (repo-public) — reinterpreted as team-clonable per Gordon's pre-authorization in the overnight brief

After Session 24 sweep: Foundations 10/10, Trustability 16/16, Layers 6/7 sections (§5.8 still 5/6 pending Gordon), E2E smoke 5/5 all re-verified this session. **MVP 1 sign-off blocked on one Gordon call.**

---

## Pointers

- Older sessions: [`docs/sessions/`](docs/sessions/)
- Older decisions and resolved blockers: [`docs/log-archive.md`](docs/log-archive.md)
- "Sign-off Status" (formerly "Accomplishments by MVP") moved to [`TASKS.md`](TASKS.md)
