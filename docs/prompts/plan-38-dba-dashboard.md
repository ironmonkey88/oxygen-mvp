# Prompt — DBA Dashboard Phase A + Phase B + Track C tidy-day batch

**Status:** reconstructed from session narrative — not the original Chat-issued prompt.
**Sources:** [`docs/dba-dashboard-design-2026-05-17.md`](../dba-dashboard-design-2026-05-17.md) (the canonical design doc this plan executes), [`docs/sessions/session-63-2026-05-23-plan-38-dba-dashboard.md`](../sessions/session-63-2026-05-23-plan-38-dba-dashboard.md), [`TASKS.md`](../../TASKS.md) Plan 38 row, [`LOG.md`](../../LOG.md) Plans Registry row, [`docs/limitations/chat-activity-local-state-only.md`](../limitations/chat-activity-local-state-only.md).
**Reconstruction date:** 2026-05-24 by Plan 43 (prompt + report lineage).
**Confidence:** Phase scope, halt conditions, and verification gates are taken directly from session narrative + the design doc that explicitly defined the v1 build sequence. The exact wording of the §A2 halt conditions (referenced in the session note as "the prompt's §A2 halt condition #3") is *(reconstructed, medium confidence)* — the halt that actually fired (Anthropic-spend tracking unlocked by populated `messages.input_tokens` columns) is grounded in the session note + the limitations entry. Track C scope is taken directly from Plan 39's session note since Plan 39 picked it up.

**Kind:** coding
**Date:** 2026-05-23
**Plan:** 38
**Scope:** new `dlt/oxy_chat_activity_pipeline.py`; new `main_admin.fct_chat_activity_raw`; new `scripts/generate_admin_dashboard.py`; new `systemd/dashboard-refresh.{service,timer}`; `nginx/somerville.conf` edits; `DASHBOARDS.md` carve-out; new `docs/limitations/chat-activity-local-state-only.md`; new `docs/design-reviews/admin-dashboard-v1-2026-05-22/` artifact; Track C is documentation-only across `.claude/`, `session-starter.md`, `dbt/models/*/schema.yml`, `TASKS.md`.
**Effort:** one long session, ~3-5 hours (Phase A halt-gated; if Phase A halts, Phase B doesn't run this session).
**Depends on:** [`docs/dba-dashboard-design-2026-05-17.md`](../dba-dashboard-design-2026-05-17.md) — the design doc lands first and defines v1 (10 panels in groups A/B/C, strict-yellow rule, operator-only audience). Plan 33 (Playwright rendered-page helper) — merged; used for the Phase B design-review artifact.

---

## Outcome

A DBA-style dashboard goes live at `http://oxygen-mvp/admin/` (Tailnet-only) that gives the operator one screen for "is the platform healthy?" — the kind of single-pane-of-glass an on-call dashboard offers in a real production stack. It's strictly yellow-or-red on operator-judgment thresholds (not green-everything-is-fine), with a top-of-page "what's currently yellow" advisory so the operator doesn't have to scan every panel. v1 covers refresh health, source freshness, and chat activity; the design doc names what's parked for v1.1 and beyond.

Phase A integrates the chat-state data (currently siloed in oxy-postgres) into the admin schema so the dashboard can show chat activity at all. Phase A is halt-gated — if the schema inspection finds something the design doc didn't anticipate, surface and decide before building the loader. Phase B builds the dashboard generator, the static HTML pipeline, the systemd refresh timer, the nginx route, and a Playwright design-review artifact.

Track C is an opportunistic tidy-day batch covering 4 unrelated cleanup items that fit in the same PR window.

## Context

The DBA dashboard design (`docs/dba-dashboard-design-2026-05-17.md`) was authored in Plan-37-adjacent design work and defines a 10-panel layout in three groups:

- **Group A (refresh):** A1 last refresh, A2 streak (rolling 12-day window), A3 duration vs 30-day median.
- **Group B (source health):** B1 source freshness (v1: 311 only — others parked for v1.1).
- **Group B continued (test results):** B2 dbt test results (pass/warn/fail counts).
- **Group C (chat activity):** C1 question volume, C2 (planned for later — see Phase A halt below).
- **Group D (advisory):** D1 "what's currently yellow" — top-of-page rollup. D2 staleness explainer for known-stale sources.

Headline color: strict-yellow rule per the design doc — green requires every panel to be green; one yellow panel turns the headline yellow. The audience is operators, not analysts; the dashboard lives at `/admin` not on the public portal.

**Phase A loader.** Chat state lives in oxy-postgres (the Postgres container `oxy start --local` brings up). To get it into the warehouse, we need a loader that reads `messages` + `threads` from oxy-postgres and lands them in `main_admin.fct_chat_activity_raw`. The design doc anticipates a thin pipeline: dlt + a custom postgres source, merge-on-`message_id`. The design doc cut Anthropic-API spend tracking as "Admin API blocked" — the Admin Console doesn't expose per-key spend at API level.

**Phase A halt-and-surface contract.** Before building the loader, inspect the oxy-postgres schema and confirm the design doc's assumptions hold. Specifically, the §A2 halt conditions Code should honor:

1. Schema fundamentally different from what the design doc assumes (no `messages` table, or no thread-grain join key).
2. PII risk in the chat data that wasn't anticipated.
3. Anthropic API spend buried in metadata — if `messages` has `input_tokens`/`output_tokens` populated, that unlocks the cost tracking the design doc cut; that's a v1 expansion worth surfacing, not silently scoping in.
4. Multi-tenant data leakage risk (the prod-shape oxy schema has organization-scoping; the `--local` single-tenant shape may not).

If any halt condition fires, write the schema-inspection finding to `docs/design-reviews/chat-state-schema-inspection-2026-05-22.md` and surface to Gordon before proceeding to A2 (loader build).

**Phase B build sequence:** loader → generator → nginx → systemd → Playwright. Loader populates the table the generator reads. Generator writes static HTML to `/var/www/somerville/admin/index.html`. nginx routes `/admin` to that path with Tailnet-only `allow`. systemd timer fires every 15 minutes. Playwright captures the final rendered surface for the design-review artifact.

**Track C — 4 tidy-day items.** Unrelated cleanup that fits in the same session window:

- C1: stale branch cleanup. Plan 32 / 33 / 34 / 35 produced several `claude/*` branches that merged but didn't auto-delete. Walk `gh api repos/.../branches`, delete any merged-to-main branch. Anticipate ~6 stale branches.
- C2: `session-starter.md` extension — add a new "Code's Operating Environment (Brief)" section after "How We Work Together" covering 6 named drift items (autonomous-merge policy location, 3-tier allowlist, bash safety + hook precedence, EC2 dbt PATH, scp→pull lock, git push postBuffer). Keep it tight — each drift item gets 2-3 lines.
- C3: `dbt/models/*/schema.yml` — add `data_type:` annotations to columns that lack them (estimated ~250 columns across bronze + gold). Use DuckDB DESCRIBE as the source. Script approach acceptable.
- C4: review `docs/tech-debt-review-2026-05-17.md` item 13 — stale "LOG.md Recent Sessions rotation — currently 6 entries (41-46)" self-flag in TASKS.md that's been resolved many times since. Remove the stale `[ ]` entry.

## Work

**Phase A — chat-state integration.**

A1. Inspect oxy-postgres schema. Write findings to `docs/design-reviews/chat-state-schema-inspection-2026-05-22.md`. Cover:

- Full table list (`\dt` equivalent).
- `messages` table shape (columns, types, populated/nullable).
- `threads` table shape.
- Multi-tenant surfaces (organization tables, scoping).
- Single-tenant data in `--local` mode (which tables actually have rows).
- Key finding: does `messages` have `input_tokens`/`output_tokens` populated? (Halt-gate.)

**HALT-AND-SURFACE per §A2 halt conditions** if any fire. Don't proceed to A2 silently if a halt condition surfaced.

A2. Build the loader: `dlt/oxy_chat_activity_pipeline.py`. Custom dlt resource using psycopg2 to query the join `messages × threads` at message grain. Merge on `message_id`. Audit columns per project conventions (`_extracted_at`, `_extracted_run_id`, `_first_seen_at`). Target: `main_admin.fct_chat_activity_raw`.

A3. Run the loader once to populate the table. Capture row count + timing in the session note.

A4. Write `docs/limitations/chat-activity-local-state-only.md` covering:

- Local-state-only risk (single-tenant container; multi-tenant prod schema would need a different loader shape).
- Container-teardown loss (oxy-postgres is ephemeral on container teardown unless persisted).
- If C2 spend is in scope post-halt-and-surface: token-spend-as-proxy framing (estimated cost ≠ billed cost; flat-rate calc on single-model deployment).

**Phase B — dashboard generator + infra.** Only runs if Phase A landed cleanly.

B1. `scripts/generate_admin_dashboard.py` — static HTML generator covering the 10 panels per the design doc. Each panel emitted via a `render_panel()` helper. Per the design doc:

- Strict-yellow headline rule (every panel green → green; one yellow → yellow; any red → red).
- "What's currently yellow" advisory panel at the top, naming each non-green panel + its reading.
- Each panel includes a `<details>` block citing the SQL it ran (per design doc §9 transparency rule).

B2. `systemd/dashboard-refresh.service` + `systemd/dashboard-refresh.timer` — 15-minute cadence. Service runs the generator + deploys to `/var/www/somerville/admin/index.html`. Install + enable.

B3. `nginx/somerville.conf` — new `location /admin` with:

```
allow 100.64.0.0/10;
allow 127.0.0.1;
deny all;
```

Tailnet (100.64/10) + loopback only. Test config reload, then sudo nginx reload.

B4. `DASHBOARDS.md` — add §9 operator-dashboard carve-out documenting that the admin dashboard is exempt from the public dashboard standards (no `.app.yml`, no purpose+audience step, no Builder Agent integration — it's static HTML for one audience: the operator).

B5. Capture the live surface via Plan 33's Playwright helper: `scripts/rendered_page.py` `review_page()` against `http://oxygen-mvp/admin/`. Write the artifact to `docs/design-reviews/admin-dashboard-v1-2026-05-22/`.

**Track C — tidy-day batch.**

C1. Stale branch cleanup. List merged branches via `gh api repos/<owner>/<repo>/branches`. For each that's merged to main and not `main` itself, `gh api -X DELETE`. Use a while-read loop (loops are bash-hook-exempt). Surface the actual count if it differs materially from the anticipated 6.

C2. `session-starter.md` "Code's Operating Environment (Brief)" section per Context.

C3. `dbt/models/*/schema.yml` `data_type:` annotations. Query DuckDB DESCRIBE for each model's columns; write the type as a YAML key on each column entry. Use a script (line-based + state-machine pass) to avoid mangling existing YAML. Run `dbt parse` after to confirm clean.

C4. Remove `docs/tech-debt-review-2026-05-17.md` item 13 stale TASKS entry. Also remove any adjacent stale TASKS items that name themselves as removable.

## Verification

**Static-artifact gates (Phase A):**

- `docs/design-reviews/chat-state-schema-inspection-2026-05-22.md` exists with the full schema findings.
- `dlt/oxy_chat_activity_pipeline.py` exists and runs to completion.
- `main_admin.fct_chat_activity_raw` exists with rows.
- `docs/limitations/chat-activity-local-state-only.md` exists.

**Static-artifact gates (Phase B):**

- `scripts/generate_admin_dashboard.py` exists; running it produces `/var/www/somerville/admin/index.html` with 10 panels.
- `systemd/dashboard-refresh.{service,timer}` exist; `systemctl list-timers` shows `dashboard-refresh.timer` active.
- `nginx/somerville.conf` has the new `/admin` location with Tailnet allow + deny-all default.
- `DASHBOARDS.md` §9 operator-dashboard carve-out exists.
- `docs/design-reviews/admin-dashboard-v1-2026-05-22/` exists with screenshot + finding.

**Live-functional gates:**

- `http://oxygen-mvp/admin/` (over Tailscale) returns 200 and renders the 10-panel layout.
- Headline color is interpretable (likely YELLOW given current platform state — A2 streak partial, B2 has 1 dbt warn).
- "What's currently yellow" advisory names each non-green panel.
- Public IP `http://18.224.151.49/admin/` returns 403 (deny-all matched).
- Loopback `http://127.0.0.1/admin/` on EC2 returns 200.

**Static-artifact gates (Track C):**

- `gh api repos/.../branches` shows `main` only (or surfaces actual remaining branches if any were intentionally kept).
- `session-starter.md` has new "Code's Operating Environment (Brief)" section with the 6 drift items.
- `dbt/models/bronze/schema.yml` + `dbt/models/gold/schema.yml` have `data_type:` keys on columns; `dbt parse` exits clean.
- `TASKS.md` no longer has the stale LOG-rotation self-flag entry.

## Halt conditions

**Phase A:**

- §A2-1: oxy-postgres schema fundamentally different from design-doc assumption — no `messages` table or no thread-grain key. Halt + surface.
- §A2-2: PII risk in the chat data that wasn't anticipated. Halt + surface.
- §A2-3: Anthropic API spend buried in metadata — if `messages.input_tokens`/`output_tokens` are populated, that unlocks v1 cost tracking the design doc cut. Surface, don't silently scope in.
- §A2-4: Multi-tenant data leakage risk in `--local` shape. Halt + surface.

If Phase A halts, do not proceed to Phase B in this session. Track C can still ship; surface as a partial.

**Phase B:**

- `nginx -t` fails after the `/admin` location is added. Halt + surface; do not reload.
- Generator writes invalid HTML (malformed `<details>` blocks, missing panels). Halt + surface.

**Track C:**

- C1 stale branch count is materially different from anticipated (anticipate ~6; if it's 0 or 50+, surface).
- C3 `dbt parse` fails post-enrichment. Halt + surface; roll back the enrichment script's edits before commit.

## Out of scope

- **v1.1 panels.** Source freshness for sources other than 311 (B1 expansion), per-question Anthropic spend (deeper than C2 if it lands), AWS cost panel (C3 in design doc, requires Cost Explorer API).
- **Public access.** `/admin` stays Tailnet-only. No magic-link or HTTPS for v1.
- **Two-way controls.** v1 is read-only. No buttons to kick off `./run.sh` or restart services.
- **Track C item not in the named 4.** Don't accumulate scope — if a 5th tidy item surfaces during execution, surface it as a Worth-flagging item for a future plan.

## Commit shape

Single PR holding Phase A + Phase B + Track C. Phase A and Phase B are jointly valuable (loader without dashboard is dead weight; dashboard without loader is empty Group C panel). Track C is opportunistic but fits naturally in the same PR window.

If Phase A halts, the PR can still ship Track C as a partial; Phase B holds for the next plan.

Per CLAUDE.md autonomous-PR-merge policy: push → `gh pr create` → `gh pr merge --merge --delete-branch` autonomously if all gates pass. Pause if Phase A halts.
