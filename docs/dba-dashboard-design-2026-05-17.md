# DBA Dashboard — Design Document

**Status:** design phase (no implementation yet)
**Date:** 2026-05-17 (revised after scope cut)
**Author:** Chat session with Gordon
**Audience for the dashboard:** the platform operator — Gordon today, anyone Oxygen hands a reference deployment to tomorrow
**Companion docs:** [DASHBOARDS.md](../DASHBOARDS.md), [BUILD.md](../BUILD.md), [ARCHITECTURE.md](../ARCHITECTURE.md), [PHILOSOPHY.md](../PHILOSOPHY.md)

---

## 0. Revision note

The earlier version of this design included three new external API integrations: Anthropic Usage API for inference spend, AWS Cost Explorer for EC2 spend, and Oxygen chat-state for activity. The Anthropic Admin API requires Organization-tier account access, which this deployment does not have. Rather than ship a v1 with two of three cost integrations or a partial spend story, all spend tracking was cut from v1. The dashboard ships as an activity-and-health surface; cost visibility lives in the AWS and Anthropic consoles for now. See §11 for what a future plan to restore cost panels would look like.

## 1. Purpose (per DASHBOARDS.md §2.1)

A single operator-facing surface answering one question: is the platform running cleanly? Today there is no unified answer; the data exists in `fct_pipeline_run_raw`, `fct_source_health_raw`, `fct_test_run`, and `fct_column_profile_raw` — but an operator has to look in four places and synthesize. The DBA dashboard collapses that synthesis into one page that loads in under two seconds and tells the operator at a glance whether to investigate.

It is not the analyst-facing `/trust` page. `/trust` answers "should I trust this dataset?" with prose framing and editorial care for an analyst audience. The DBA dashboard answers "is the machine running?" with panel density for an operator. Same underlying data in places; different selection, different framing, different audiences. Both surfaces survive.

This document covers the internal v1 only. A public-subset derivation (à la Cloudflare's status page) is a deliberate future plan; each panel below is tagged `internal-only` or `public-eligible` so the future derivation has zero ambiguity. Building both at once would double scope and require an editorial layer (incident communication, framing) that v1 doesn't have.

## 2. The "is everything green?" rule

Per the operator's settled preference: anything yellow makes the headline yellow; only fully-green makes the headline green. The strict rule.

Under healthy operation the headline will frequently sit at yellow, because the platform has expected advisory states — the `by_design`-flagged baseline drifts, the occasional source-health blip, the in-flight refresh. Those don't represent platform problems; they represent the strict-yellow rule doing its job.

To prevent strict-yellow from becoming noise that gets tuned out, the dashboard pairs the headline traffic light with a "what's currently yellow" panel that lists every yellow contributor by name, severity, and source. The headline tells you whether to look; the advisory panel tells you where. Without the panel, the headline is a nag with no payload.

There is no fourth color. Red means at least one critical item is failing — pipeline didn't run today, Oxygen runtime is unreachable, warehouse stale > 48 hours. Yellow means at least one advisory item is non-green. Green means everything is green. Three states, clean enough for an at-a-glance read.

**Headline computation**

```
headline = "red"    if ANY panel.severity == "critical" and panel.state != "green"
        else "yellow" if ANY panel.state != "green"
        else "green"
```

Each panel below carries an explicit `severity: critical | advisory` classification. That classification is the only lever that distinguishes strict-yellow noise from red-alert.

## 3. Panel inventory

Nine panels (eight named + one context panel), organized into four groups. Each panel declares:

- **What:** what it shows
- **Source:** where the data comes from (existing table | new integration)
- **Severity:** `critical` (failure → red) or `advisory` (failure → yellow)
- **Public-eligible:** `yes` (would go on a future public page verbatim) | `subset` (sanitized form OK) | `no` (internal-only)

### Group A: Pipeline health (the load-bearing group)

**A1. Last refresh status**

- **What:** outcome of the most recent `./run.sh` (success / partial / failed) with timestamp and elapsed-since
- **Source:** `main_admin.fct_pipeline_run_raw` (latest row by `run_started_at`)
- **Severity:** critical (a failed daily refresh is a red-alert condition)
- **Public-eligible:** subset — public version shows "data refreshed at [time]" without status nuance

**A2. Refresh streak**

- **What:** count of consecutive successful refreshes; below this, a sparkline of the last 14 days' refresh outcomes
- **Source:** `fct_pipeline_run_raw` aggregated
- **Severity:** advisory (a broken streak shows up in A1; this just contextualizes recovery)
- **Public-eligible:** subset — "uptime over the last N days" is standard public-status-page content

**A3. Pipeline duration trend**

- **What:** last 30 days of pipeline duration as a sparkline; current duration vs. 30-day median as a delta
- **Source:** `fct_pipeline_run_raw.run_duration_seconds`
- **Severity:** advisory (a slowdown is a precursor to a problem, not a problem itself)
- **Public-eligible:** no — implementation detail

### Group B: Data freshness and quality

**B1. Source freshness**

- **What:** for each Socrata endpoint, hours since the source itself last updated (from Socrata's `rowsUpdatedAt`), and hours since we last successfully pulled it. Tabular: one row per source.
- **Source:** `main_admin.fct_source_health_raw` (latest row per source)
- **Severity:** critical (source not pulled in > 48h is red)
- **Public-eligible:** subset — table shape OK, hide endpoint URLs

**B2. dbt test summary (latest run)**

- **What:** pass / warn / fail counts from the latest dbt-test invocation; if any `fail`, list the failing test names; `warn` count is shown but doesn't itself trip yellow if all warns are `by_design`-tagged.
- **Source:** `main_admin.fct_test_run` (existing)
- **Severity:** critical for `fail`; advisory for `warn` (with the by-design carve-out)
- **Public-eligible:** subset — pass/fail count OK; test names no

**B3. Profile coverage**

- **What:** % of tracked columns with a fresh profile (< 7 days old); count of stale profiles
- **Source:** `main_admin.fct_column_profile_raw`
- **Severity:** advisory
- **Public-eligible:** no

### Group C: Activity

**C1. Chat activity (last 7 days)**

- **What:** count of agent conversations, count of messages, count of distinct sessions; sparkline of daily message volume
- **Source:** NEW INTEGRATION — Oxygen exposes message history in its own SQLite/state store; needs a small reader script landing rows into a new `main_admin.fct_chat_activity_raw`. Open question: what shape does Oxygen's local-mode chat state actually have? The implementation prompt must inspect it on EC2 before promising a schema.
- **Severity:** advisory (low chat activity is informational, not a failure)
- **Public-eligible:** no — usage information

*(Group C originally also held two cost panels — C2 Anthropic spend and C3 AWS spend. Both cut from v1; see §0 and §11.)*

### Group D: Service availability

**D1. Oxygen runtime health**

- **What:** `/api/health` response status and latency; uptime since last restart
- **Source:** NEW — small synchronous health check inside the dashboard generator (hits `http://localhost:3000/api/health` at page build time). Optionally also a periodic check landed into a new `main_admin.fct_service_health_raw` table; v1 can be page-build-time only.
- **Severity:** critical
- **Public-eligible:** subset — "chat is up" yes; latency no

**D2. Warehouse size and growth**

- **What:** DuckDB file size; total row count across bronze; growth over last 30 days as a delta
- **Source:** DuckDB `pragma database_size` plus a query across bronze tables; can be computed at page build time
- **Severity:** advisory
- **Public-eligible:** no

### What's currently yellow (the load-bearing context panel)

A vertical list, computed dynamically: every panel currently non-green, shown with its name, current state, and a one-line "why." Sorted by severity (criticals first, then advisories). If everything is green, this panel collapses to a single "All systems green" line.

This panel is the antidote to strict-yellow noise. Without it the nag is uninterpretable; with it, the nag is actionable in under five seconds.

## 4. Layout

A single-page, top-to-bottom dense layout. No tabs. The dashboard's whole job is at-a-glance, and tabs hide signal.

```
+----------------------------------------------------------+
|  [headline traffic light]   Platform: YELLOW             |
|                             2 advisory items             |
|                             Last refresh: 4h ago         |
+----------------------------------------------------------+
|  What's currently yellow                                  |
|   • B2: 1 dbt test in 'warn' (baseline.row_count_2026)   |
|   • A3: pipeline 22% slower than 30-day median           |
+----------------------------------------------------------+
|  A1 Last refresh    A2 Streak       A3 Duration trend     |
+----------------------------------------------------------+
|  B1 Source freshness (table, 6 rows)                      |
+----------------------------------------------------------+
|  B2 dbt tests       B3 Profile coverage   C1 Chat activity|
+----------------------------------------------------------+
|  D1 Oxygen health   D2 Warehouse size                     |
+----------------------------------------------------------+
```

C1 moves up to share a row with B2 and B3 now that Group C is a single panel — keeps the grid tight and avoids a row with one panel and two empty cells.

## 5. Refresh cadence

The dashboard is a regenerated static HTML page, in keeping with the rest of the portal architecture (no live server-side rendering, no client-side data fetching for v1).

- Regenerated by `run.sh` at the end of every pipeline run (alongside `/trust`, `/metrics`, `/profile`).
- Plus a lighter regeneration cadence for D1 (service health) and D2 (warehouse size) — these can move independently of a pipeline run. v1 keeps it simple: regenerate the whole page on a 15-minute timer via a new lightweight systemd timer (`dashboard-refresh.timer`), which re-queries the existing admin tables and re-runs the page-build-time checks (Oxygen `/api/health`, warehouse size).
- Chat activity (C1) loads on the same 15-minute cadence — the Oxygen chat-state reader runs at page build time. No separate timer.

## 6. URL and access

- **URL:** `/admin` (not `/dba`, which reads as a job title rather than a function). nginx serves the static page from `/var/www/somerville/admin/`.
- **Access control:** Tailnet-only IP restriction. The page is internal-only and must not be reachable from the public internet. Basic Auth is the fallback if the Tailnet restriction proves awkward in practice; design ships Tailnet-only.
- **No nav-link from the public portal homepage.** The page exists; it doesn't advertise itself. A future plan that builds the public-subset derivation will create a separate `/status` URL with its own publicly-linked entry point.

## 7. The public-subset derivation (future plan, not v1)

For when the public-status-page plan eventually opens, this is the selection that would go public, in transformed form:

- **A1** → "Data was last refreshed at [time]. Current freshness: [N hours old]." No success/fail framing.
- **A2** → "Data has refreshed successfully on N of the last 30 days."
- **B1** → table form OK; hide endpoint URLs; show source names only.
- **B2** → "N data-quality tests passed in the last run." No test names, no fail/warn breakdown.
- **D1** → "Chat service: up / degraded / down." No latency, no uptime detail.

Everything else stays internal. Chat activity, warehouse internals, profile coverage, pipeline durations — none of those go public. *(Cost panels would have been in this list too; with C2/C3 cut from v1, the question is moot for v1.)*

The future plan also needs to add editorial structure that v1 does not have: incident communication (a place to post "we're investigating an issue"), historical uptime (N-day rollups), and per-panel descriptive prose that translates internal concepts (dbt tests, Socrata sources) into public-audience language. That editorial layer is the actual hard part of the public derivation, not the panel selection.

## 8. What this design deliberately omits

- **No spend tracking.** Cut from v1 per §0. Cost visibility lives in the AWS Console and Anthropic Console for now.
- **No log tailing.** The dashboard is summary-grade; raw `journalctl` output belongs in `ssh` sessions.
- **No alerting.** Alerting is its own plan with its own delivery channel (email? Slack? webhook?); the dashboard is the display. v1 builds the display; alerting can hang off the same admin tables in a later plan.
- **No historical drill-down beyond sparklines.** A "click the panel for 90 days of detail" view would double the page's complexity and significantly delay v1. Sparklines are sufficient for "is the trend worsening or recovering."
- **No multi-tenancy.** The dashboard reflects one platform deployment. Stack-in-a-Box recipients get their own deployment's dashboard; there's no notion here of "all deployments at once."
- **No SLO / SLA framing.** v1 doesn't claim service levels. The strict yellow rule is operator preference, not a commitment to an external party.

## 9. Standards-doc impact

This design implies one small update to `DASHBOARDS.md`, because the current standard is written for analyst dashboards driven by semantic-layer measures. The DBA dashboard reads admin tables directly. A clean one-paragraph addition to `DASHBOARDS.md`:

> Operator dashboards (`/admin`, future `/status`) may read from `main_admin.*` tables directly rather than through the semantic layer. The trust-contract receipts requirement applies to the underlying SQL queries, not to a semantic-layer wrapper; operator-dashboard panels must still cite their source table and the query that produced the displayed value, exactly as analyst dashboards must.

Approved by operator on 2026-05-17. Lands as part of the dashboard implementation PR rather than separately.

## 10. What the v1 implementation will need

For when the implementation prompt comes (separately, after this design is signed off):

**New data sources:**

- Oxygen chat-state reader → `main_admin.fct_chat_activity_raw` (open question on schema until Oxygen's local store is inspected — Phase A verification step)

**New scripts:**

- `scripts/load_chat_activity.py` (or equivalent — naming finalized in Plan A)
- `scripts/generate_admin_dashboard.py`

**New infrastructure:**

- `dashboard-refresh.timer` + `.service` for the 15-minute cadence
- nginx route for `/admin` with Tailnet-only restriction

**New secrets:** none. (Anthropic Admin API and AWS Cost Explorer secrets are no longer needed with cost panels cut.)

**New limitations entries:**

- `chat-activity-local-state-only.md` (chat activity is whatever Oxygen's local store contains; if `--local` mode loses state on restart, this becomes load-bearing)

## 11. Cost panels as a future plan

The design intentionally preserves the work that went into thinking about cost panels, in case a future account-tier change makes them viable. When that happens, the future plan picks up here:

**Panels to restore:**

- **C2. Anthropic API spend (this month).** Month-to-date USD spend; sparkline of daily spend; burn rate vs. last month's same-day pace. Severity advisory by default; configurable budget threshold can elevate to critical. Public-eligible: no.
- **C3. AWS/EC2 spend (this month).** Same shape, different source. Public-eligible: no.

**Integrations required:**

- Anthropic Usage API → `main_admin.fct_anthropic_usage_raw`. Requires an Anthropic Admin API key (`sk-ant-admin-...`), which in turn requires Organization-tier account access.
- AWS Cost Explorer API → `main_admin.fct_aws_cost_raw`. Requires Cost Explorer enabled on the AWS account and IAM credentials with `ce:GetCostAndUsage`. Cost Explorer charges $0.01 per API request; daily cadence puts this in pennies-per-month.

**Layout adjustment:** Group C grows from one panel (C1) back to three (C1 + C2 + C3); the C1-in-Group-B-row arrangement reverts to a dedicated Group C row.

**Limitations entries to add when restored:**

- `aws-cost-explorer-24h-lag.md`
- `anthropic-usage-api-rounding.md` (if rounding behavior turns out to matter)

This section is the durable record of the cost-tracking design so the future plan doesn't re-derive it.

## 12. Open questions to resolve before implementation

1. **Oxygen chat-state schema.** What does Oxygen's local-mode chat history actually look like on disk? A `--local` deployment vs. multi-workspace will have different shapes. Implementation prompt handles this as a Phase A verification step on EC2 before promising a schema.

*(Questions #2–#5 from the prior design — budget thresholds, Anthropic Admin API access, AWS IAM permissions, Tailnet-vs-Basic-Auth — are resolved: thresholds moot with cost cut, Admin API moot with cost cut, AWS IAM moot with cost cut, access settled as Tailnet-only.)*

## 13. Sign-off checklist

Before this design becomes an implementation prompt, the following must be true:

- [x] Operator agrees with the panel inventory (Section 3)
- [x] Operator agrees with the strict-yellow + advisory-panel pairing (Section 2)
- [x] `DASHBOARDS.md` standards carve-out (Section 9) is approved
- [ ] Plan-number slot reserved in LOG.md Plans Registry
- [x] Open questions in Section 12 are answered or explicitly deferred (only #1 remains, handled in Phase A of the implementation prompt)

After sign-off, implementation is two plans:

- **Plan A:** the Oxygen chat-state integration landing into `main_admin.fct_chat_activity_raw`. Pure pipeline work, no UI. Smaller than the prior design's Plan A because the two cost integrations are cut.
- **Plan B:** the dashboard generator and the page itself, reading the new table plus the existing ones. Pure presentation work.

Splitting is recommended because Plan A's data integration has value on its own (the chat-activity table is source material for any future activity-based panel or alert), and because a single PR doing both would be hard to review.
