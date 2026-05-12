---
session: 31
date: 2026-05-12
start_time: 17:41 ET
end_time: 18:30 ET
type: code
plan: none
layers: [docs]
work: [docs]
status: complete
---

## Goal

Capture institutional knowledge from MVP 1 (Sessions 1–28) plus the two post-sign-off plans (1a daily refresh + observability, 1b column profiling + `/erd` + `/profile`) in a durable retrospective document, and reorient `TASKS.md` "Next Focus" at MVP 2 plan-scoping before that work begins in Chat.

## What shipped

- [`docs/retrospective/mvp1-lessons-learned.md`](../retrospective/mvp1-lessons-learned.md) — 2,144-word durable artifact covering Oxygen findings, build pattern, Gordon-as-customer, what we'd do differently, and what's load-bearing for MVPs 2–4.
- LOG.md — Current Status updated; Sessions 31, 30, 29 added to Recent (29 + 30 were missing — Plans 1a/1b skipped LOG rotation at commit time); Sessions 24–26 rotated to Earlier as one-liners; retrospective Active Decisions row added; Pointers extended.
- TASKS.md — Plan 1b Phase 8 flipped `[~]` → `[x]` with commit `0a0a065`; "Next Focus" rewritten from "Plan 1a Daily Refresh" to "MVP 2 Plan-Scoping: First Data App via Builder Agent" with scope decisions, pre-flight verification checklist, explicit out-of-scope, and carry-over queue items.

## Decisions

- **Retrospective is a durable artifact, not a session note.** The retrospective doc lives at `docs/retrospective/` rather than being folded into the session archive because it's written for someone joining the project six months from now, including parts of the Oxy team that don't see every commit. Session notes are append-only narrative; the retrospective is a synthesis surface that gets updated when its underlying lessons change.

## Issues encountered

- **LOG.md remains 274 lines, over the 250 hard ceiling.** Pre-existing — was 269 lines at session start. Active Decisions table has accumulated rapidly across Sessions 12–30 and nothing in it is older than the 30-day rotation threshold (today is 2026-05-12; oldest decision is 2026-05-07). The hard ceiling can't be met without either changing the threshold or compressing some rows. Not in scope for this plan; flagging for a future tech-debt pass.
- **Daily `./run.sh` runs are landing `run_status='partial'`.** Pre-flight observation: 4 of the last 5 pipeline runs in `main_admin.fct_pipeline_run_raw` are `partial`. `run_status='partial'` means admin `dbt test` failures didn't halt the run (captured-exit pattern by design) but a test did fail. Likely drift-fail at the new baseline since Plan 1a switched the merge target. Queued under TASKS.md MVP 2 carry-over for investigation; not a blocker on MVP 2 plan-scoping.

## Next action

MVP 2 plan-scoping in Chat. First scope decision: which first dashboard for Builder Agent to construct (single-angle vs multi-angle vs two-step). Pre-flight verifications need to happen in the Chat session itself (or as Code's pre-flight when the plan executes), specifically that Builder Agent is reachable in the SPA in `--local` mode.
