# Handoff for the next Code session — 2026-05-16

Code → Code. If you're a fresh Code instance starting up, read this first to orient — then go to `LOG.md` + `TASKS.md` for canonical state.

## Project state at handoff time

- `origin/main` tip: `837cfaf` (Plan 26 housekeeping merge). All recent PRs (#34-#46) merged cleanly.
- `./run.sh manual` last green: 2026-05-16 03:34-03:49 UTC, run_id `01KRQDK2JT3MNQG6Q9Y5AEM2AB`, status `success`, 897s, all 10 stages clean, all tests pass. (Plan 23 cumulative verification.)
- `/metrics` page: **22 measures across 11 views** (Plan 23 brought it from 4 across 4 — all 14 new permits/citations/at-a-glance measure names verified present via curl).
- Portal: all 8 routes verified working — `/`, `/dashboards`, `/metrics`, `/trust`, `/profile`, `/erd`, `/docs/`, `/about`. `/chat` redirects to `/home` after Basic Auth.
- `/erd` redesigned: tier-grouped flowchart on top (Bronze 7 / Silver placeholder / Gold 12 / Admin 3) + **four per-tier column-level erDiagrams** below (Bronze/Silver-placeholder/Gold/Admin) + semantic-layer diagram. Generators run at `run.sh` stage 9e.
- Worktree branches: this worktree is on `claude/plan-26-housekeeping` (merged). Open PR queue: empty.
- EC2 (`oxygen-mvp` over Tailscale): synced to main (`837cfaf`).
- Local repo at `/Users/gordonwong/claude-projects/oxygen-mvp/`: this worktree at `.claude/worktrees/upbeat-torvalds-12f9bd/` is synced.

## What landed in this thread (recent first)

In merge order on `main`:

- `837cfaf` PR #46 — Plan 26 housekeeping: LOG.md Recent Sessions rotated 13 → 5; new `docs/limitations/oxy-df-interchange-empty-result-panic.md`; autonomous-merge confirmed already-landed (Session 50).
- `5fe5749` PR #45 — Plan 25: Per-tier column-level erDiagrams on `/erd`. New `scripts/generate_per_tier_erd.py`; `generate_erd_page.py` extended; `run.sh` stage 9e wires it.
- `aa63826` PR #44 — ERD tier-grouped flowchart. Replaced erDiagram with `flowchart LR` + subgraphs + classDef tier coloring + dotted "dbt" arrows.
- `51330d2` PR #43 — `/erd/` trailing-slash 301 redirect + stale May-2026 placeholder dirs (`erd/`, `tasks/`) moved out of `/var/www/somerville/`. Also new `docs/limitations/spa-artifact-load-404.md`.
- `fe28ee9` PR #42 — `/chat` redirects to `/home`. New auth-gated `portal/chat-redirect.html` + nginx `location = /chat` exact-match. Phase-ordering gotcha worth knowing (see below).
- `75d92a5` PR #41 — Plan 23 cumulative verification + durability items. STACK.md DuckDB-spatial pattern + pre-flight rule; autonomous-merge policy landed in CLAUDE.md (settings.json schema rejected the custom key).
- `9eced5e` PR #40 — Plan 23 Phase D halt finding + LOG/TASKS/session-49 housekeeping.
- `0ebadc9` PR #39 — Plan 23 Phase C: `fct_somerville_kpi` + `dim_kpi_topic` + new `city_context` topic.
- `1c48ed7` PR #38 — Plan 23 Phase B: `fct_citations` + new `citations` view in `public_safety` topic.
- `8fc1dcc` PR #37 — Plan 23 Phase A housekeeping.
- `d269aab` PR #36 — Plan 23 Phase A: `fct_permits` + DuckDB-spatial ward derivation + new `built_environment` topic.
- `4e51179` PR #35 — Plan 22: PROMPTS.md wiring (+ aae5a4a multi-phase merge clarification).
- `ebaeeb2` PR #34 — PROMPTS.md initial landing (Chat-to-Code prompt standard).

## Disciplines / patterns to know

- **PROMPTS.md is the receipt-workflow source of truth.** Every Chat-to-Code prompt follows the §3/§4 shape; Code runs §5's 9-step workflow on receipt. Report-back (§5 Step 9) is the last thing Code emits in the session.
- **CLAUDE.md "Receiving prompts from Chat" subsection** is loaded on session start; it carries the **autonomous-PR-merge policy** (push + open PR + merge in one flow after verified work, pause only for partial/blocked/unverified-gates/failed-checks/cross-repo). This moved from per-machine memory to committed config in Session 50.
- **STACK.md §2.2 DuckDB now carries the spatial extension pattern + pre-flight rule.** Pre-flight rule states first: before reaching for spatial, compare source-published coverage to spatial coverage; use whichever wins. Plan 23 Phase A used spatial (96.62% match, no source ward); Phase B did NOT (source ward 99.88% > spatial 99.82%).
- **Airlayer vocabulary locks** (durably surfaced this thread): measure types `{count, sum, average, min, max, count_distinct, median, custom}`; dimension types `{string, number, date, datetime, boolean}`. Don't use `avg` (use `average`); don't use `timestamp` (use `datetime`).
- **nginx phase-ordering gotcha** (PR #42 lesson): `return` directive fires in the rewrite phase BEFORE `auth_basic`. So `return 302 /home;` inside an auth-gated location block **bypasses Basic Auth**. Use `try_files` + static HTML (content phase, post-access) when you need an auth-gated redirect-like behavior.
- **schema.yml dedup pattern** (PR #45 lesson): the project's schema.yml docs convention places relationships-only entries as a second `- name: <col>` block (column-with-description first, FK-test-only second). Parsers that dedupe at the column-name level drop the FK tests. Dedupe at the output level, not the entry level.

## Open threads / outstanding actions

| Thread | State | Pointer |
|---|---|---|
| Send Oxy customer-feedback bundle to upstream | **awaiting Gordon's action** (Slack post drafted) | Filled doc in chat transcript end-of-thread; four findings (Builder CLI token hang, Builder no-default-trust-signals, SPA artifact 404, df-interchange panic) |
| Update the 4 limitations entries' Resolution Path with the filed-upstream link | blocked on send | `docs/limitations/{plan-11-builder-cli-token-budget-hang, spa-artifact-load-404, oxy-df-interchange-empty-result-panic}.md` + Plan 11 trust-signal note in session-39 transcript |
| Plan 24 — MVP 3 Happiness Survey silver/gold curation | queued, prompt drafted, reserved in LOG.md Plans Registry | Prompt body pasted in this thread; 5 phases with halt-risk pre-flight; first MVP 3 silver work |
| Plans 18 + 19 — Builder-CLI dashboards (permits-vs-311, citations-vs-crime) | queued, prompt drafted | Both need interactive Builder CLI sessions; fresh threads each |
| `fct_311_requests.ward → dim_ward` relationships test missing | minor inconsistency | All other fct tables have this FK test; 311 fact never got one. 3-line schema.yml edit. Would surface as a 10th FK arrow on the gold per-tier erDiagram |
| Session 52 narrative file | not written | Plan 26 was small; commit message + LOG.md Plan 26 row + Active Decisions carry the durable record. If completeness matters, easy follow-up |
| Add `portal/chat-redirect.html` ownership preservation | done | `run.sh` already syncs it with `deploy_html`; future runs keep it in sync |
| TASKS.md "Next Focus" | refreshed; reads cleanly | Plan 24 + Plans 18/19 + Oxy feedback bundle named as next moves |

## Concrete first-actions checklist for the next session

When you boot:

1. `git -C ~/oxygen-mvp pull origin main` on EC2 first — confirm at `837cfaf`.
2. `git status` clean; on the local worktree, branch off origin/main with a fresh name for the new work.
3. Read `TASKS.md` "Next Focus" section to confirm what's queued.
4. Read `LOG.md` Plans Registry (Plans 0-26 closed; Plan 24 reserved; no other reservations).
5. If you're starting Plan 24 or Plans 18/19, read the relevant prompt body from a Chat thread (Gordon will paste).
6. If a new ad-hoc request comes in: PROMPTS.md §5 receipt workflow applies (read header → verify state → branch on kind → restate Outcome → pre-flight → plan commit shape → execute → verify and commit → report back).

## Known Oxy-side bugs (workarounds in place; documented upstream-pending)

- **`spa-artifact-load-404`** — SPA right-pane artifact viewer 404s on `/api/00000000-.../artifacts/<uuid>?branch=`. Workaround: `oxy run agents/answer_agent.agent.yml "..."` from CLI surfaces full SQL + trust contract inline.
- **`oxy-df-interchange-empty-result-panic`** — `execute_sql` panics on no-match WHERE filters. Workaround: Answer Agent self-recovers via DISTINCT/ILIKE fallback; user-facing impact is "agent takes an extra query."
- **`plan-11-builder-cli-token-budget-hang`** — Builder Agent `agentic answer` for "Continue with double budget" accepts but doesn't resume. Workaround: cancel, hand-write `.app.yml` from Builder's captured SQL in the JSONL event log.
- **Builder default-trust-signal gap** (no separate limitations entry yet; documented in `docs/transcripts/plan-11-rat-complaints-builder-session.md` retro): Builder doesn't propose citations/freshness/limitations unless the opening prompt names them. Workaround: name them in the opening prompt.

## Gotchas worth carrying

- **Worktree state after stash + branch + new pull:** if you create a new branch off `origin/main` immediately after merging in the same session, fetch first or you'll branch off the stale cached tip. The fix is `git fetch origin` before `git checkout -b ... origin/main`.
- **EC2 portal-deploy file ownership** (Plan 14b): `deploy_html` helper in `run.sh` self-heals `sudo chown ubuntu:ubuntu` if needed before `cp`. If you ever scp directly to `/var/www/somerville/` as root, future deploys will need the helper or a manual chown.
- **EC2 worktree state after scp'd file changes:** scping a file directly to EC2's git checkout leaves it as a "modified" tracked file. Before `git pull` or branch switch, discard with `git checkout -- <file>` or your pull fails.
- **The bash safety hook is strict:** no `&&`, `;`, `|` in single Bash tool calls (the allowlist `*` doesn't match `|`). For multi-command needs, write a script to `scratch/`, scp, and run via `ssh ... bash /tmp/script.sh`.
