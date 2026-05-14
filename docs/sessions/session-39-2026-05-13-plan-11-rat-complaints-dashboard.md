---
session: 39
date: 2026-05-13
start_time: 17:50 ET
end_time: 22:15 ET
type: code
plan: plan-11
layers: [semantic, gold, portal, docs]
work: [feature, docs]
status: complete
---

## Goal

Execute Plan 11 — the rat-complaints-by-ward dashboard via Builder
Agent. Pre-flight Builder Agent + Data Apps gates honestly; construct
the dashboard; integrate trust signals; build a `/dashboards` portal
listing; document gaps as limitation entries.

Gordon's carry-forward decisions for this session: ward-only
(no neighborhood mapping); transcript saved to `docs/transcripts/`
repo-side (portal exposure deferred).

## What shipped

**6 phases of plan-11 phase work, all green or partial-with-finding:**

- Phase 1 (no commit — pre-flight gate): G1 PASS (changelog reviewed).
  G2–G6 PASS via the **`oxy agentic run --domain builder builder`
  CLI** — a path the Plan 11 plan didn't initially know about.
  G5 partial-fail (`oxy run apps/X.app.yml` not supported in oxy
  0.5.47 — STACK.md §1.9 was wrong); G6 partial — Builder uses
  `execute_sql`, not a dedicated `run_app` tool. Within gate budget
  (≤2 fails). G7 N/A (`--local` mode in use).
- Phase 2: data pre-flight complete. Refined the rat-complaint filter
  from `LIKE '%rat%'` (which catches false positives like
  "consideration request" and "vaccine clinic registration") to an
  IN-list of 4 explicit types — `Rats`, `Rodent Assistance Program
  request`, `Rodent Assistance Program inquiry`, and `School Rodent
  Control` (trailing space — source-side padding family). 14,036 rows
  total. Ward distribution 1,250–2,661 (more even than 311's overall
  distribution); 167 NULL ward (1.2%, vs 38% overall). All 12,599
  closed complaints have both `date_created_dt` and
  `most_recent_status_dt` — full resolution-time derivability.
  Median 4d, avg 300d (heavy long tail).
- Phase 3: [directional transcript](../transcripts/plan-11-rat-complaints-directional-transcript.md)
  drafted — opening prompt + expected Builder moves + expected file
  shape + success criteria.
- Phase 4: Builder Agent construction session ran via
  `oxy agentic run --domain builder builder`. Builder ran 4 real
  verification queries (matched Phase 2 pre-flight totals exactly).
  Hit a CLI bug where the token-budget "Continue with double budget"
  resume answer was accepted by `oxy agentic answer` but never
  triggered run-state-machine resume. Cancelled the run; used
  Builder's verified queries verbatim to hand-write
  [`apps/rat_complaints_by_ward.app.yml`](../../apps/rat_complaints_by_ward.app.yml).
  `oxy validate` green; 12 config files valid.
- Phase 5: trust signals integrated in the app YAML — `last_refreshed`
  task reading from `main_admin.fct_pipeline_run_raw`, citations
  markdown block, known-limitations markdown block with refs to the
  bronze-ward limitation. Visual SPA render verification deferred
  (no Chrome MCP) — captured in `dashboard-render-spa-only`
  limitation.
- Phase 6: [`portal/dashboards.html`](../../portal/dashboards.html) +
  nginx `/dashboards` route + portal index nav link. Hand-written
  per the prompt; generator pattern deferred to a follow-on. Live at
  `http://18.224.151.49/dashboards` (`curl` confirms 200).
- Phase 7: 2 new limitation entries —
  [`plan-11-builder-cli-token-budget-hang`](../limitations/plan-11-builder-cli-token-budget-hang.md)
  and [`dashboard-render-spa-only`](../limitations/dashboard-render-spa-only.md).
  STACK.md §1.9 corrected (the `oxy run apps/<name>.app.yml` claim
  was wrong; rendering is SPA-only in oxy 0.5.47). Limitations index
  regenerated to 19 active entries (was 17).
- Phase 8: [retro](../transcripts/plan-11-rat-complaints-builder-session.md#retro-phase-8)
  in the session transcript — comparison of actual vs directional,
  customer-feedback findings, three Oxy-shaped recommendations.

## Decisions

- **Builder Agent CLI is the load-bearing pre-flight discovery.**
  Phase 1 initially looked stop-and-surface (no Chrome MCP); probing
  oxy's CLI surface revealed `oxy agentic run --domain builder`,
  which makes Builder Agent + HITL + tool use all CLI-testable.
  Opportunistic principle in action: the assumed "SPA-only" path
  wasn't the only path.
- **Refined filter to explicit IN-list, not LIKE-pattern.** Phase 2
  finding: `LIKE '%rat%'` matches false positives. The explicit
  4-type list + TRIM() handles the trailing-space source quirk
  consistently with the existing `block-code-padded` pattern.
- **Hand-write `.app.yml` fallback after token-budget CLI hang.**
  Builder generated all 4 verified queries before the budget cap;
  the file-write step never completed. Hand-writing uses Builder's
  exact SQL — the work is Builder-authored at the SQL level, just
  not Builder-assembled at the file level. Per Plan 11's explicit
  fallback path. Customer-feedback finding logged for Oxy.
- **STACK.md §1.9 fixed.** The "From the CLI: `oxy run apps/<name>.app.yml`"
  line was incorrect; oxy 0.5.47's `oxy run` rejects `.app.yml`.
  Rendering is SPA-only. Updated to name the SPA path explicitly +
  link to the limitation entry.

## Issues encountered

- **Builder CLI token-budget resume hang** (documented as a new
  limitation). `oxy agentic answer --answer "Continue with double
  budget"` returned success but did not advance the run. Cancelled
  + hand-wrote the file. This is a real Oxy CLI bug worth filing
  upstream.
- **Visual SPA render unavailable from Code overnight.** Chrome MCP
  not connected; documented as a separate limitation. Sign-off-worthy
  but partial — the dashboard renders correctly per structural +
  SQL gates, but the chart layout has not been eyeballed.
- **2 stale `oxy agentic run` processes on EC2 from earlier Phase 1
  probes** were killed mid-session. Cosmetic; no impact on Plan 11
  output.

## Next action

Plan 14 (operational hygiene): drift-fail baseline re-anchor, portal-
deploy ownership durable fix, LOG.md compression pass. All three
land on a fresh `claude/plan-14-operational-hygiene` branch.
