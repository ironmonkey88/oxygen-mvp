# DBA Dashboard — Design Document

**Status:** design phase (no implementation yet)
**Date:** 2026-05-17
**Author:** Chat session with Gordon
**Audience for the dashboard:** the platform operator — Gordon today, anyone Oxygen hands a reference deployment to tomorrow
**Companion docs:** [DASHBOARDS.md](../DASHBOARDS.md), [BUILD.md](../BUILD.md), [ARCHITECTURE.md](../ARCHITECTURE.md), [PHILOSOPHY.md](../PHILOSOPHY.md)

---

## 1. Purpose (per DASHBOARDS.md §2.1)

A single operator-facing surface answering one question: is the platform running cleanly? Today there is no unified answer; the data exists in `fct_pipeline_run_raw`, `fct_source_health_raw`, `fct_column_profile_raw`, and Anthropic's usage console — but an operator has to look in four places and synthesize. The DBA dashboard collapses that synthesis into one page that loads in under two seconds and tells the operator at a glance whether to investigate.

It is not the analyst-facing `/trust` page. `/trust` answers "should I trust this dataset?" with prose framing and editorial care for an analyst audience. The DBA dashboard answers "is the machine running?" with panel density for an operator. Same underlying data in places; different selection, different framing, different audiences. Both surfaces survive.

This document covers the internal v1 only. A public-subset derivation (à la Cloudflare's status page) is a deliberate future plan; each panel below is tagged `internal-only` or `public-eligible` so the future derivation has zero ambiguity. Building both at once would double scope and require an editorial layer (incident communication, framing) that v1 doesn't have.

## 2. The "is everything green?" rule

Per the operator's settled preference: anything yellow makes the headline yellow; only fully-green makes the headline green. The strict rule.

Under healthy operation the headline will frequently sit at yellow, because the platform has expected advisory states — the `by_design`-flagged baseline drifts, the occasional source-health blip, the in-flight refresh. Those don't represent platform problems; they represent the strict-yellow rule doing its job.

To prevent strict-yellow from becoming noise that gets tuned out, the dashboard pairs the headline traffic light with a "what's currently yellow" panel that lists every yellow contributor by name, severity, and source. The headline tells you whether to look; the advisory panel tells you where. Without the panel, the headline is a nag with no payload.

There is no fourth color. Red means at least one critical item is failing — pipeline didn't run today, Anthropic API is down, EC2 is unreachable, warehouse stale > 48 hours. Yellow means at least one advisory item is non-green. Green means everything is green. Three states, clean enough for an at-a-glance read.

**Headline computation**

```
headline = "red"    if ANY panel.severity == "critical" and panel.state != "green"
        else "yellow" if ANY panel.state != "green"
        else "green"
```

Each panel below carries an explicit `severity: critical | advisory` classification. That classification is the only lever that distinguishes strict-yellow noise from red-alert.

## 3. Panel inventory

Eleven panels, organized into four groups. Each panel declares:

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

### Group C: Activity and cost

**C1. Chat activity (last 7 days)**

- **What:** count of agent conversations, count of messages, count of distinct sessions; sparkline of daily message volume
- **Source:** NEW INTEGRATION — Oxygen exposes message history in its own SQLite/state store; needs a small reader script landing rows into a new `main_admin.fct_chat_activity_raw`. Open question: what shape does Oxygen's local-mode chat state actually have? Implementation prompt must verify before promising a schema.
- **Severity:** advisory (low chat activity is informational, not a failure)
- **Public-eligible:** no — usage information

**C2. Anthropic API spend (this month)**

- **What:** month-to-date USD spend; sparkline of daily spend; current burn rate vs. last month's same-day pace
- **Source:** NEW INTEGRATION — Anthropic Usage API. New pipeline stage `dlt/load_anthropic_usage.py` lands daily rollups into `main_admin.fct_anthropic_usage_raw`. Refresh cadence: daily (the API has its own 24h-ish lag).
- **Severity:** advisory by default; the design recommends a configured monthly budget threshold that elevates to critical when crossed
- **Public-eligible:** no — commercial information

**C3. AWS/EC2 spend (this month)**

- **What:** month-to-date USD spend on the EC2 host; sparkline; same framing as C2
- **Source:** NEW INTEGRATION — AWS Cost Explorer API. New pipeline stage `dlt/load_aws_costs.py` lands daily rollups into `main_admin.fct_aws_cost_raw`. Cost Explorer has a ~24h lag.
- **Severity:** advisory by default; same budget-threshold elevation option as C2
- **Public-eligible:** no

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
|   • C2: API spend pace 11% over last month                |
+----------------------------------------------------------+
|  A1 Last refresh    A2 Streak       A3 Duration trend     |
+----------------------------------------------------------+
|  B1 Source freshness (table, 6 rows)                      |
+----------------------------------------------------------+
|  B2 dbt tests       B3 Profile coverage                   |
+----------------------------------------------------------+
|  C1 Chat activity   C2 API spend     C3 AWS spend         |
+----------------------------------------------------------+
|  D1 Oxygen health   D2 Warehouse size                     |
+----------------------------------------------------------+
```

## 5. Refresh cadence

The dashboard is a regenerated static HTML page, in keeping with the rest of the portal architecture (no live server-side rendering, no client-side data fetching for v1).

- Regenerated by `run.sh` at the end of every pipeline run (alongside `/trust`, `/metrics`, `/profile`).
- Plus a lighter regeneration cadence for cost panels (C2, C3) and the service-health check (D1) — these can move independently of a pipeline run. v1 keeps it simple: regenerate the whole page on a 15-minute timer via a new lightweight systemd timer (`dashboard-refresh.timer`), which re-queries the existing admin tables and re-runs the page-build-time checks (Oxygen `/api/health`, warehouse size).

The cost-data integrations (`load_anthropic_usage.py`, `load_aws_costs.py`) run on their own daily timer, not on every dashboard refresh. They're upstream of the dashboard, not part of it.

## 6. URL and access

- **URL:** `/admin` (not `/dba`, which reads as a job title rather than a function). nginx serves the static page from `/var/www/somerville/admin/`.
- **Access control:** the v1 page is internal-only and must not be publicly indexable. nginx config gates `/admin` behind the same Basic Auth used for `/chat`, or — preferred — behind a Tailnet-only IP restriction so it isn't reachable from the public internet at all. The design favors the Tailnet restriction; Basic Auth is the fallback.
- **No nav-link from the public portal homepage.** The page exists; it doesn't advertise itself. A future plan that builds the public-subset derivation will create a separate `/status` URL with its own publicly-linked entry point.

## 7. The public-subset derivation (future plan, not v1)

For when the public-status-page plan eventually opens, this is the selection that would go public, in transformed form:

- **A1** → "Data was last refreshed at [time]. Current freshness: [N hours old]." No success/fail framing.
- **A2** → "Data has refreshed successfully on N of the last 30 days."
- **B1** → table form OK; hide endpoint URLs; show source names only.
- **B2** → "N data-quality tests passed in the last run." No test names, no fail/warn breakdown.
- **D1** → "Chat service: up / degraded / down." No latency, no uptime detail.

Everything else stays internal. Costs, chat activity, warehouse internals, profile coverage, pipeline durations — none of those go public.

The future plan also needs to add editorial structure that v1 does not have: incident communication (a place to post "we're investigating an issue"), historical uptime (N-day rollups), and per-panel descriptive prose that translates internal concepts (dbt tests, Socrata sources) into public-audience language. That editorial layer is the actual hard part of the public derivation, not the panel selection.

## 8. What this design deliberately omits

- **No log tailing.** The dashboard is summary-grade; raw `journalctl` output belongs in `ssh` sessions.
- **No alerting.** Alerting is its own plan with its own delivery channel (email? Slack? webhook?); the dashboard is the display. v1 builds the display; alerting can hang off the same admin tables in a later plan.
- **No historical drill-down beyond sparklines.** A "click the panel for 90 days of detail" view would double the page's complexity and significantly delay v1. Sparklines are sufficient for "is the trend worsening or recovering."
- **No multi-tenancy.** The dashboard reflects one platform deployment. Stack-in-a-Box recipients get their own deployment's dashboard; there's no notion here of "all deployments at once."
- **No SLO / SLA framing.** v1 doesn't claim service levels. The strict yellow rule is operator preference, not a commitment to an external party.

## 9. Standards-doc impact

This design implies one small update to `DASHBOARDS.md`, because the current standard is written for analyst dashboards driven by semantic-layer measures. The DBA dashboard reads admin tables directly. A clean one-paragraph addition to `DASHBOARDS.md`:

> Operator dashboards (`/admin`, future `/status`) may read from `main_admin.*` tables directly rather than through the semantic layer. The trust-contract receipts requirement applies to the underlying SQL queries, not to a semantic-layer wrapper; operator-dashboard panels must still cite their source table and the query that produced the displayed value, exactly as analyst dashboards must.

That carve-out is honest and small. Worth landing it as part of the dashboard implementation PR rather than separately.

## 10. What the v1 implementation will need

For when the implementation prompt comes (separately, after this design is signed off):

**New data sources:**

- Anthropic Usage API integration → `main_admin.fct_anthropic_usage_raw`
- AWS Cost Explorer API integration → `main_admin.fct_aws_cost_raw`
- Oxygen chat-state reader → `main_admin.fct_chat_activity_raw` (open question on schema until Oxygen's local store is inspected)

**New scripts:**

- `dlt/load_anthropic_usage.py`
- `dlt/load_aws_costs.py`
- `scripts/load_chat_activity.py` (or equivalent)
- `scripts/generate_admin_dashboard.py`

**New infrastructure:**

- `dashboard-refresh.timer` + `.service` for the 15-minute cadence
- nginx route for `/admin` with Tailnet-only restriction (preferred) or Basic Auth (fallback)

**New secrets:**

- Anthropic Admin API key (for the Usage API — distinct from the inference key already in `/etc/environment`)
- AWS access key with `ce:GetCostAndUsage` IAM permission

**New limitations entries:**

- `aws-cost-explorer-24h-lag.md`
- `anthropic-usage-api-rounding.md` (if rounding behavior turns out to matter)
- `chat-activity-local-state-only.md` (chat activity is whatever Oxygen's local store contains; if `--local` mode loses state on restart, this becomes load-bearing)

## 11. Open questions to resolve before implementation

1. **Oxygen chat-state schema.** What does Oxygen's local-mode chat history actually look like on disk? A `--local` deployment vs. multi-workspace will have different shapes. Implementation prompt needs a verification step before promising a schema.
2. **Budget thresholds for cost panels.** If C2 and C3 should elevate to `critical` at a threshold, what threshold? "Anything over $X this month" is configurable; needs a value.
3. **Anthropic Admin API access.** Confirm the Anthropic account has Admin API access enabled and an API key for it; this is distinct from the inference key.
4. **AWS IAM permissions.** Confirm a key with `ce:GetCostAndUsage` is available, or be willing to provision one.
5. **Tailnet-only vs. Basic Auth for `/admin` access.** Both work; Tailnet is preferred per design. Operator's call which to ship.

## 12. Sign-off checklist

Before this design becomes an implementation prompt, the following must be true:

- [ ] Operator agrees with the panel inventory (Section 3) — adds, cuts, severity adjustments
- [ ] Operator agrees with the strict-yellow + advisory-panel pairing (Section 2)
- [ ] Open questions in Section 11 are answered or explicitly deferred
- [ ] `DASHBOARDS.md` standards carve-out (Section 9) is approved
- [ ] Plan-number slot reserved in LOG.md Plans Registry

After sign-off, implementation splits into at least two plans:

- **Plan N:** the three new data integrations (Anthropic Usage, AWS Cost Explorer, Oxygen chat-state) landing into admin tables. Pure pipeline work, no UI.
- **Plan N+1:** the dashboard generator and the page itself, reading the new tables plus the existing ones. Pure presentation work.

Splitting is recommended because the integrations are independently useful (the cost tables, in particular, become source material for future panels and alerts), and because a single PR doing both would be hard to review.
