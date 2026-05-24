---
id: cost-panel-pricing-assumptions
title: DBA dashboard C2 cost panel assumes Opus 4.7 flat-rate pricing
severity: advisory
affects:
  - admin_dashboard
  - panel-c2
  - cost_tracking
since: 2026-05-24
status: active
---

# Cost panel pricing assumptions

## What the panel computes

The DBA dashboard's C2 panel reports month-to-date Anthropic API spend
derived from `main_admin.fct_chat_activity_raw.input_tokens` +
`output_tokens`, multiplied by per-token rates. v1.1 (Plan 40) added
this panel as a replacement for v1's stop-gap 7-day token-count panel.

## Pricing assumptions

**Rates applied (verified 2026-05-23):**

- Input tokens: $15.00 per million
- Output tokens: $75.00 per million
- Model: Claude Opus 4.7 (per `config.yml` — single-model setup)

**Why flat-rate:** Plan 40 pre-flight inspected the chat-state schema
(`messages` table in the `oxy-postgres` container) and found no `model`
column or equivalent provider/model identifier on individual messages.
The project's `config.yml` configures a single Anthropic model (Opus
4.7) for the Answer Agent, so all assistant messages should be Opus 4.7
calls. The flat-rate calculation is correct under that assumption.

**If the deployment ever runs mixed models** (e.g., Sonnet for some
agents, Opus for others), this panel's spend number becomes a
mixed-rate average and won't reflect actual billed spend. Two
mitigations to consider in that case:

1. Add a `model` column to the chat-state ingestion via dlt
   (`dlt/oxy_chat_activity_pipeline.py`) — Oxygen may already record
   model per message in a metadata field this loader currently drops.
2. Apply per-row pricing in the C2 panel calculation, joining each
   row's model identifier to a pricing table.

Neither mitigation is needed today.

## Lag inherent in the 15-minute regen cadence

The C2 panel reflects token counts as of the last
`scripts/generate_admin_dashboard.py` invocation. Per the
`dashboard-refresh.timer` 15-minute schedule, the panel can be up to
15 minutes behind real-time. For burn-rate-vs-last-month comparisons
this is well below the resolution of the comparison; for active-chat
"how am I spending RIGHT NOW" questions, it isn't real-time.

Acceptable for v1.1 — the panel's job is daily/monthly trend
visibility, not minute-by-minute cost tracking.

## Local-mode chat state is comprehensive (for this deployment)

Same caveat as `chat-activity-local-state-only.md`: the panel only
reflects chat activity that landed in the local `oxy-postgres`
container. If Oxygen ever serves agent traffic via a path that doesn't
write to local Postgres (e.g., a hypothetical cloud-routed agent in a
multi-workspace future deployment), that traffic's tokens won't show
up in this panel.

For the current `--local` single-workspace EC2 deployment, the
container's Postgres IS the comprehensive record. Container teardown
loses history; see `chat-activity-local-state-only.md`.

## Verification

Cross-check the C2 panel's MTD figure against the Anthropic console
billing dashboard once per month. The two should match within a few
percent (the dashboard's 15-min lag + Anthropic billing-cycle
boundaries explain any small drift).

A bigger discrepancy than ~5% is a finding:

- Did `oxy-postgres` get recreated (history reset)?
- Did the project run a model other than Opus 4.7 at any point?
- Did Oxygen serve agent traffic from a path that bypassed local
  Postgres?

## Related

- Loader: [`dlt/oxy_chat_activity_pipeline.py`](../../dlt/oxy_chat_activity_pipeline.py)
- Schema inspection: [`docs/design-reviews/chat-state-schema-inspection-2026-05-22.md`](../design-reviews/chat-state-schema-inspection-2026-05-22.md)
- v1 cost-panel finding (chat-state has token columns): Plan 38 / PR [#65](https://github.com/ironmonkey88/oxygen-mvp/pull/65)
- v1.1 cost-panel implementation: Plan 40
- DBA dashboard design: [`docs/dba-dashboard-design-2026-05-17.md`](../dba-dashboard-design-2026-05-17.md) §11
