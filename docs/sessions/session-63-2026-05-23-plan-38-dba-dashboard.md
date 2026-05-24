---
session: 63
date: 2026-05-23
start_time: 22:10 ET
end_time: 23:09 ET
type: code
plan: plan-38
layers: [ingestion, bronze, admin, portal, infra, docs]
work: [feature, infra, docs]
status: complete
---

## Goal

Plan 38 — DBA Dashboard A+B + Track C tidy-day batch per `docs/dba-dashboard-design-2026-05-17.md`. Phase A (chat-state integration) halt-gates Phase B (dashboard generator + nginx + systemd + Playwright). Plus 4 Track C items.

## What shipped

**Phase A — chat-state integration:**

- `docs/design-reviews/chat-state-schema-inspection-2026-05-22.md` — comprehensive schema findings (51-table Postgres schema, multi-tenant adjacent surfaces, single-tenant `--local` data, key finding that `messages.input_tokens`/`output_tokens` exist and unlock Anthropic-spend tracking the design doc had cut).
- `dlt/oxy_chat_activity_pipeline.py` — dlt + psycopg2, custom resource joining `messages × threads` at message grain, merge-on-`message_id`, audit columns. 102 messages × 14 threads landed in 0.42s.
- `main_admin.fct_chat_activity_raw` populated with 17 columns (12 source + 3 audit + 2 dlt-internal).
- `docs/limitations/chat-activity-local-state-only.md` — covers local-state-only risk + container-teardown loss + token-spend-as-proxy framing.

**Phase B — dashboard generator + infra:**

- `scripts/generate_admin_dashboard.py` — 10-panel static HTML generator (~420 lines). Strict-yellow rule + "what's currently yellow" advisory. Each panel has `<details>` SQL source citation per design doc §9.
- `systemd/dashboard-refresh.service` + `.timer` — 15-min cadence, installed + enabled.
- `nginx/somerville.conf` `/admin` location with `allow 100.64.0.0/10; allow 127.0.0.1; deny all`.
- `DASHBOARDS.md` §9 operator-dashboard carve-out.
- `docs/design-reviews/admin-dashboard-v1-2026-05-22/` — Playwright artifact + extensive finding.

**Live dashboard** at `http://oxygen-mvp/admin/`: headline YELLOW (2 advisory items), 8 panels GREEN + 2 YELLOW. C2 (NEW) shows $20.00 (7d) Opus 4.7 spend.

## Decisions

- **Halt-and-surface at Phase A1** per prompt's §A2 halt condition #3. The `messages` table's token columns unlock cost-proxy tracking the design doc had cut. Gordon picked "expand v1 to include token-spend panel."
- **Loader source: dlt with postgres source** (Gordon's pick). Implemented as dlt resource using psycopg2 for the join query — matches project's existing dlt pattern.
- **Split Track C into Plan 39** per prompt's Out-of-Scope clause. Phase A + Phase B is already a substantial PR.

## Issues encountered

- Initial generator queries used `run_status='succeeded'` but actual enum is `success`/`failed`/`partial`; similar mismatch on `check_status` (used `'healthy'`, actual `'ok'`). Caught by smoke-running the generator and seeing impossible RED headline. Fixed in 4 small edits; second run produced correct YELLOW.
- Plan 33 helper's annotation selector is hardcoded to back-link elements — per-panel callouts didn't draw on the dashboard. Full-page screenshot still useful as evidence. v1.1 enhancement candidate: add `targets_selector` parameter to `review_page()`.

## Next action

Plan 39 (Track C — 4 tidy-day items). Plan 40 (memory-to-file migrations, re-numbered from original Plan 38). Plan 24 + Plans 18/19 + DBA Dashboard v1.1 cost-panel scope still queued — design doc §11's "Cost panels as a future plan" becomes immediately scopable now that token data is in the warehouse.
