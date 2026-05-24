"""DBA dashboard generator — Plan 38 Phase B.

Generates `/var/www/somerville/admin/index.html` from main_admin.* tables
plus page-build-time probes (Oxygen `/api/health`, DuckDB pragma size).

Layout per design doc §4 (with Plan 38's added C2 token-spend panel):

  Row 1: Headline traffic light (strict-yellow rule)
  Row 2: What's currently yellow (advisory)
  Row 3: A1 | A2 | A3                  (pipeline health)
  Row 4: B1                            (source freshness, full row)
  Row 5: B2 | B3 | C1                  (tests | profile | chat)
  Row 6: C2 | D1 | D2                  (tokens | health | warehouse)

Run at the end of run.sh (alongside /trust, /metrics, /profile) AND on a
15-minute systemd timer (dashboard-refresh.timer) for D1/D2/C1/C2 freshness.

Per design doc §9 + DASHBOARDS.md operator-dashboard carve-out: each
panel cites its source table and the SQL that produced the displayed
value.
"""
from __future__ import annotations

import html
import json
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import duckdb

DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
OXY_HEALTH_URL = "http://127.0.0.1:3000/api/health"
DEPLOY_PATH = Path("/var/www/somerville/admin/index.html")

# Strict-yellow severity model
CRITICAL = "critical"
ADVISORY = "advisory"

GREEN = "green"
YELLOW = "yellow"
RED = "red"

# Opus 4.7 pricing — for C2 spend-proxy panel
OPUS_INPUT_USD_PER_M = 15.0
OPUS_OUTPUT_USD_PER_M = 75.0


def fmt_ts(ts) -> str:
    if ts is None:
        return "—"
    if hasattr(ts, "strftime"):
        return ts.strftime("%Y-%m-%d %H:%M ET")
    return str(ts)


def fmt_ago(ts, now) -> str:
    if ts is None:
        return "—"
    if hasattr(ts, "tzinfo") and ts.tzinfo is not None:
        delta = now.astimezone(ts.tzinfo) - ts if hasattr(now, "astimezone") else None
    delta_s = (now - ts.replace(tzinfo=None)).total_seconds() if hasattr(ts, "tzinfo") and ts.tzinfo else (now - ts).total_seconds()
    if delta_s < 60:
        return f"{int(delta_s)}s ago"
    if delta_s < 3600:
        return f"{int(delta_s / 60)}m ago"
    if delta_s < 86400:
        return f"{int(delta_s / 3600)}h ago"
    return f"{int(delta_s / 86400)}d ago"


# ============================================================================
# Panel queries — each returns (color, headline, why, sql, source_table)
# ============================================================================

def panel_a1_last_refresh(con, now):
    sql = """
        SELECT run_started_at, run_status, run_duration_seconds
        FROM main_admin.fct_pipeline_run_raw
        WHERE run_status IN ('success', 'failed', 'partial')
        ORDER BY run_started_at DESC LIMIT 1
    """
    row = con.execute(sql).fetchone()
    if not row:
        return RED, ADVISORY, "No pipeline runs recorded", "No data", sql, "fct_pipeline_run_raw"
    ts, status, dur = row
    ago = fmt_ago(ts, now)
    if status == "failed":
        return RED, CRITICAL, f"Last run failed {ago}", f"{ago} · {status}", sql, "fct_pipeline_run_raw"
    delta_h = (now - ts).total_seconds() / 3600 if not hasattr(ts, "tzinfo") or ts.tzinfo is None else (now - ts.replace(tzinfo=None)).total_seconds() / 3600
    if delta_h > 26:
        return YELLOW, CRITICAL, f"Last refresh {ago} (>26h)", f"{ago} · {status}", sql, "fct_pipeline_run_raw"
    if status == "partial":
        return YELLOW, CRITICAL, f"Last refresh {ago} (partial)", f"{ago} · partial · {dur}s", sql, "fct_pipeline_run_raw"
    return GREEN, CRITICAL, f"Last refresh {ago}", f"{ago} · {status} · {dur}s", sql, "fct_pipeline_run_raw"


def panel_a2_streak(con, now):
    sql = """
        WITH recent AS (
            SELECT DATE_TRUNC('day', run_started_at) AS day,
                   MAX(CASE WHEN run_status = 'success' THEN 1 ELSE 0 END) AS any_success
            FROM main_admin.fct_pipeline_run_raw
            WHERE run_started_at > NOW() - INTERVAL 30 DAY
            GROUP BY 1
        )
        SELECT
          SUM(any_success) AS success_days,
          COUNT(*) AS total_days
        FROM recent
    """
    row = con.execute(sql).fetchone()
    if not row or row[1] is None or row[1] == 0:
        return RED, ADVISORY, "No runs in last 30 days", "0/0 days", sql, "fct_pipeline_run_raw"
    succ, tot = int(row[0] or 0), int(row[1])
    pct = succ / tot * 100 if tot else 0
    headline = f"{succ}/{tot} days had a successful run"
    if pct == 100:
        return GREEN, CRITICAL, headline, headline, sql, "fct_pipeline_run_raw"
    if pct >= 80:
        return YELLOW, CRITICAL, f"{headline} ({pct:.0f}%)", headline, sql, "fct_pipeline_run_raw"
    return RED, CRITICAL, f"{headline} ({pct:.0f}%)", headline, sql, "fct_pipeline_run_raw"


def panel_a3_duration_trend(con, now):
    sql = """
        SELECT
          MEDIAN(run_duration_seconds) FILTER (
              WHERE run_started_at > NOW() - INTERVAL 30 DAY
                AND run_status = 'success'
          ) AS median_30d,
          (SELECT run_duration_seconds
           FROM main_admin.fct_pipeline_run_raw
           WHERE run_status = 'success'
           ORDER BY run_started_at DESC LIMIT 1) AS latest
        FROM main_admin.fct_pipeline_run_raw
    """
    row = con.execute(sql).fetchone()
    if not row or row[0] is None or row[1] is None:
        return YELLOW, ADVISORY, "Insufficient pipeline-run history", "—", sql, "fct_pipeline_run_raw"
    med, latest = float(row[0]), float(row[1])
    delta_pct = (latest - med) / med * 100 if med else 0
    headline = f"{int(latest)}s vs {int(med)}s 30d median"
    if abs(delta_pct) <= 20:
        return GREEN, ADVISORY, headline, headline + f" ({delta_pct:+.0f}%)", sql, "fct_pipeline_run_raw"
    if abs(delta_pct) <= 50:
        return YELLOW, ADVISORY, headline + f" ({delta_pct:+.0f}%)", headline + f" ({delta_pct:+.0f}%)", sql, "fct_pipeline_run_raw"
    return RED, ADVISORY, headline + f" ({delta_pct:+.0f}%)", headline + f" ({delta_pct:+.0f}%)", sql, "fct_pipeline_run_raw"


def panel_b1_source_freshness(con, now):
    sql = """
        WITH latest AS (
            SELECT source_endpoint, check_status, hours_since_source_update,
                   ROW_NUMBER() OVER (PARTITION BY source_endpoint
                                      ORDER BY checked_at DESC) AS rn
            FROM main_admin.fct_source_health_raw
        )
        SELECT source_endpoint, check_status, hours_since_source_update
        FROM latest WHERE rn = 1
        ORDER BY check_status DESC, hours_since_source_update DESC NULLS LAST
    """
    rows = con.execute(sql).fetchall()
    if not rows:
        return YELLOW, CRITICAL, "No source-health checks recorded", "—", sql, "fct_source_health_raw"
    bad = [r for r in rows if r[1] not in ("healthy", "ok")]
    table_rows_html = "".join(
        f"<tr><td>{html.escape(r[0])}</td><td>{html.escape(r[1] or '—')}</td><td>{r[2] if r[2] is not None else '—'}</td></tr>"
        for r in rows
    )
    table_html = (
        '<table class="dba-source-table"><thead><tr>'
        '<th>Source endpoint</th><th>Status</th><th>Hours since source update</th>'
        '</tr></thead><tbody>'
        + table_rows_html
        + '</tbody></table>'
    )
    if not bad:
        return GREEN, CRITICAL, f"All {len(rows)} sources healthy", table_html, sql, "fct_source_health_raw"
    return YELLOW, CRITICAL, f"{len(bad)}/{len(rows)} sources non-healthy", table_html, sql, "fct_source_health_raw"


def panel_b2_dbt_tests(con, now):
    sql = """
        WITH last_run AS (
            SELECT run_id FROM main_admin.fct_test_run
            ORDER BY run_at DESC LIMIT 1
        )
        SELECT status, COUNT(*) AS n
        FROM main_admin.fct_test_run
        WHERE run_id = (SELECT run_id FROM last_run)
        GROUP BY status
    """
    rows = con.execute(sql).fetchall()
    if not rows:
        return YELLOW, CRITICAL, "No test runs recorded", "—", sql, "fct_test_run"
    counts = {s.lower() if s else "?": int(n) for s, n in rows}
    fail = counts.get("fail", 0) + counts.get("failed", 0) + counts.get("error", 0)
    warn = counts.get("warn", 0) + counts.get("warning", 0)
    passed = counts.get("pass", 0) + counts.get("passed", 0) + counts.get("ok", 0) + counts.get("success", 0)
    total = sum(counts.values())
    headline = f"{passed}/{total} passed"
    if warn:
        headline += f", {warn} warn"
    if fail:
        headline += f", {fail} fail"
    if fail:
        return RED, CRITICAL, headline, headline, sql, "fct_test_run"
    if warn:
        return YELLOW, CRITICAL, headline, headline, sql, "fct_test_run"
    return GREEN, CRITICAL, headline, headline, sql, "fct_test_run"


def panel_b3_profile_coverage(con, now):
    sql = """
        SELECT COUNT(DISTINCT table_name) AS tables,
               COUNT(*) AS columns
        FROM main_admin.fct_column_profile_raw
        WHERE profiled_at > NOW() - INTERVAL 7 DAY
    """
    row = con.execute(sql).fetchone()
    if not row or not row[0]:
        return YELLOW, CRITICAL, "No profile data in last 7 days", "—", sql, "fct_column_profile_raw"
    tables, columns = int(row[0]), int(row[1])
    return GREEN, CRITICAL, f"{tables} tables / {columns} columns profiled (7d)", f"{tables} tables · {columns} columns", sql, "fct_column_profile_raw"


def panel_c1_chat_activity(con, now):
    sql = """
        SELECT
          COUNT(DISTINCT thread_id) AS conversations,
          COUNT(*) AS messages
        FROM main_admin.fct_chat_activity_raw
        WHERE message_created_at > NOW() - INTERVAL 7 DAY
    """
    row = con.execute(sql).fetchone()
    if not row:
        return YELLOW, ADVISORY, "No chat-activity data available", "—", sql, "fct_chat_activity_raw"
    convs, msgs = int(row[0] or 0), int(row[1] or 0)
    headline = f"{convs} conversations / {msgs} messages (7d)"
    # Advisory panel — never red. Yellow if 0 (signal of total inactivity).
    if msgs == 0:
        return YELLOW, ADVISORY, "No chat activity in last 7 days", headline, sql, "fct_chat_activity_raw"
    return GREEN, ADVISORY, headline, headline, sql, "fct_chat_activity_raw"


def _sparkline_svg(values, width=200, height=30, color="#1e6091"):
    """Tiny inline-SVG sparkline. `values` is a list of numbers, oldest first."""
    if not values or len(values) < 2:
        return ""
    vmin, vmax = min(values), max(values)
    span = vmax - vmin or 1.0
    step = width / (len(values) - 1)
    points = " ".join(
        f"{i * step:.1f},{height - ((v - vmin) / span) * height:.1f}"
        for i, v in enumerate(values)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" style="vertical-align:middle">'
        f'<polyline fill="none" stroke="{color}" stroke-width="1.5" points="{points}"/>'
        f'</svg>'
    )


def panel_c2_cost(con, now):
    """v1.1 cost panel: month-to-date spend + 30d sparkline + burn-rate delta.

    Replaces v1's 7-day rolling token-spend panel (Plan 38 stop-gap).
    Pricing assumes Opus 4.7 flat rate — Plan 40 pre-flight confirmed
    `messages` table has no model column; config.yml runs a single-model
    setup. See docs/limitations/cost-panel-pricing-assumptions.md.
    """
    # Month-to-date assistant token consumption
    mtd_sql = f"""
        SELECT
          COALESCE(SUM(input_tokens), 0) AS in_tokens,
          COALESCE(SUM(output_tokens), 0) AS out_tokens,
          ROUND(SUM(input_tokens) * {OPUS_INPUT_USD_PER_M} / 1000000
              + SUM(output_tokens) * {OPUS_OUTPUT_USD_PER_M} / 1000000, 2) AS usd
        FROM main_admin.fct_chat_activity_raw
        WHERE DATE_TRUNC('month', message_created_at) = DATE_TRUNC('month', NOW())
          AND is_human = FALSE
    """
    row = con.execute(mtd_sql).fetchone()
    if not row:
        return YELLOW, ADVISORY, "No chat-activity data available", "—", mtd_sql, "fct_chat_activity_raw"
    mtd_in, mtd_out, mtd_usd = int(row[0] or 0), int(row[1] or 0), float(row[2] or 0.0)

    # Last month, same calendar-day cutoff (for burn-rate comparison)
    last_sql = f"""
        SELECT
          ROUND(SUM(input_tokens) * {OPUS_INPUT_USD_PER_M} / 1000000
              + SUM(output_tokens) * {OPUS_OUTPUT_USD_PER_M} / 1000000, 2) AS usd
        FROM main_admin.fct_chat_activity_raw
        WHERE DATE_TRUNC('month', message_created_at) = DATE_TRUNC('month', NOW() - INTERVAL 1 MONTH)
          AND EXTRACT(DAY FROM message_created_at) <= EXTRACT(DAY FROM NOW())
          AND is_human = FALSE
    """
    last_row = con.execute(last_sql).fetchone()
    last_usd = float(last_row[0] or 0.0) if last_row else 0.0

    # 30-day daily-spend sparkline
    sparkline_sql = f"""
        SELECT DATE_TRUNC('day', message_created_at) AS day,
               ROUND(SUM(input_tokens) * {OPUS_INPUT_USD_PER_M} / 1000000
                   + SUM(output_tokens) * {OPUS_OUTPUT_USD_PER_M} / 1000000, 4) AS usd
        FROM main_admin.fct_chat_activity_raw
        WHERE message_created_at > NOW() - INTERVAL 30 DAY
          AND is_human = FALSE
        GROUP BY 1 ORDER BY 1
    """
    spark_rows = con.execute(sparkline_sql).fetchall()
    spark_values = [float(r[1] or 0) for r in spark_rows]

    # Burn-rate delta vs last month at this point
    if last_usd > 0:
        delta_pct = ((mtd_usd - last_usd) / last_usd) * 100
        delta_str = f"{delta_pct:+.0f}% vs last month at this point"
    else:
        delta_str = "no prior-month baseline"

    sparkline_html = _sparkline_svg(spark_values) if len(spark_values) >= 2 else ""
    headline = f"${mtd_usd:.2f} MTD · {delta_str}"
    why = (
        f"${mtd_usd:.2f} MTD · {mtd_in:,} in / {mtd_out:,} out tokens · "
        f"{delta_str} · 30d daily-spend sparkline: {sparkline_html} · "
        f"Opus 4.7 flat-rate pricing (single-model config). "
        f"See <a href='/admin/' style='text-decoration:underline;color:inherit'>methodology</a>."
    )
    return GREEN, ADVISORY, headline, why, mtd_sql, "fct_chat_activity_raw"


def panel_d1_oxygen_health(now):
    sql = "synchronous probe at page build time"
    t0 = time.time()
    try:
        req = urllib.request.Request(OXY_HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            elapsed_ms = int((time.time() - t0) * 1000)
            status_code = resp.status
            body = resp.read(2000).decode("utf-8", errors="replace")
            try:
                payload = json.loads(body)
                status_field = payload.get("status", "?")
            except Exception:
                status_field = "?"
            if status_code == 200 and status_field in ("healthy", "ok"):
                return GREEN, CRITICAL, f"{status_field} · {elapsed_ms}ms", f"HTTP {status_code} · {status_field} · {elapsed_ms}ms", f"GET {OXY_HEALTH_URL}", "oxy /api/health"
            return YELLOW, CRITICAL, f"{status_code} · {status_field} · {elapsed_ms}ms", f"HTTP {status_code} · {status_field}", f"GET {OXY_HEALTH_URL}", "oxy /api/health"
    except (urllib.error.URLError, socket.timeout) as exc:
        elapsed_ms = int((time.time() - t0) * 1000)
        return RED, CRITICAL, f"unreachable · {elapsed_ms}ms", f"{type(exc).__name__}: {exc}", f"GET {OXY_HEALTH_URL}", "oxy /api/health"


def panel_d2_warehouse_size(con, now):
    sql_size = "PRAGMA database_size"
    sql_rows = """
        SELECT SUM(estimated_size) AS total_rows
        FROM duckdb_tables() WHERE schema_name = 'main_bronze'
    """
    try:
        size_row = con.execute(sql_size).fetchone()
        # pragma_database_size returns dict-like; index 0 is database_name; size_str is later
        # actually: duckdb pragma_database_size schema differs; let's grab the total_blocks/wal_size string
        # Simpler: query system function for the actual file size
        import os
        size_bytes = os.path.getsize(DUCKDB_PATH)
        size_mb = size_bytes / 1024 / 1024
        rows_row = con.execute(sql_rows).fetchone()
        bronze_rows = int(rows_row[0] or 0) if rows_row else 0
        headline = f"{size_mb:.1f} MB · {bronze_rows:,} bronze rows (est)"
        return GREEN, ADVISORY, headline, headline, f"os.path.getsize({DUCKDB_PATH}) + duckdb_tables()", "warehouse"
    except Exception as exc:
        return YELLOW, ADVISORY, f"Size probe failed: {type(exc).__name__}", str(exc), "warehouse probe", "warehouse"


# ============================================================================
# HTML rendering
# ============================================================================

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DBA dashboard — Somerville Analytics</title>
  <meta name="robots" content="noindex,nofollow">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            max-width: 1100px; margin: 1.5em auto; padding: 0 1em; color: #1a1a1a;
            background: #fafafa; }}
    h1 {{ font-size: 1.6em; margin: 0 0 0.2em 0; }}
    .subtitle {{ color: #6b6b6b; font-size: 0.9em; margin: 0 0 1.5em 0; }}
    .headline {{ display: flex; align-items: center; gap: 1em; padding: 1em 1.2em;
                 border-radius: 8px; margin-bottom: 1em; }}
    .headline.green {{ background: #e8f0eb; border: 1px solid #b8d4c0; }}
    .headline.yellow {{ background: #fff8e5; border: 1px solid #e8d480; }}
    .headline.red {{ background: #fce8e8; border: 1px solid #e0b0b0; }}
    .dot {{ width: 1.2em; height: 1.2em; border-radius: 50%; flex-shrink: 0; }}
    .dot.green {{ background: #2d8856; }}
    .dot.yellow {{ background: #d49b1a; }}
    .dot.red {{ background: #b03c3c; }}
    .headline-text {{ font-weight: 600; font-size: 1.1em; }}
    .headline-meta {{ color: #6b6b6b; font-size: 0.9em; margin-left: auto; }}
    .advisory {{ background: #fff; border: 1px solid #d8d8d8; border-radius: 6px;
                 padding: 0.7em 1em; margin-bottom: 1em; font-size: 0.95em; }}
    .advisory h3 {{ margin: 0 0 0.4em 0; font-size: 0.95em; color: #6b6b6b; }}
    .advisory ul {{ margin: 0; padding-left: 1.4em; }}
    .grid {{ display: grid; gap: 0.6em; margin-bottom: 0.6em; }}
    .grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
    .grid-1 {{ grid-template-columns: 1fr; }}
    .panel {{ background: #fff; border: 1px solid #d8d8d8; border-radius: 6px;
              padding: 0.8em 1em; font-size: 0.9em; }}
    .panel-title {{ font-weight: 600; font-size: 0.85em; color: #6b6b6b;
                    text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.3em; }}
    .panel-value {{ font-size: 1.05em; margin-bottom: 0.4em; }}
    .panel-status {{ display: inline-block; width: 0.7em; height: 0.7em;
                     border-radius: 50%; margin-right: 0.4em; vertical-align: middle; }}
    .panel-cite {{ font-size: 0.75em; color: #8a8a8a; margin-top: 0.6em;
                   border-top: 1px dotted #e0e0e0; padding-top: 0.4em; }}
    .panel-cite details summary {{ cursor: pointer; }}
    .panel-cite pre {{ background: #f5f5f5; padding: 0.5em; overflow-x: auto;
                       font-size: 0.85em; margin: 0.3em 0 0 0; }}
    .dba-source-table {{ border-collapse: collapse; width: 100%; font-size: 0.85em; }}
    .dba-source-table th, .dba-source-table td {{ text-align: left;
                                                   padding: 0.25em 0.5em;
                                                   border-bottom: 1px solid #eee; }}
    footer {{ color: #8a8a8a; font-size: 0.8em; margin-top: 2em;
              border-top: 1px solid #d8d8d8; padding-top: 0.6em; }}
  </style>
</head>
<body>
  <h1>DBA dashboard</h1>
  <p class="subtitle">Operator-internal — Plan 38 v1 — refreshed every 15 min</p>

  <div class="headline {headline_color}">
    <div class="dot {headline_color}"></div>
    <div class="headline-text">Platform: {headline_color_upper}</div>
    <div class="headline-meta">{headline_summary} · Last refresh: {refresh_ago}</div>
  </div>

  <div class="advisory">
    <h3>What's currently yellow</h3>
    {advisory_body}
  </div>

  <div class="grid grid-3">
    {row_3}
  </div>
  <div class="grid grid-1">
    {row_4}
  </div>
  <div class="grid grid-3">
    {row_5}
  </div>
  <div class="grid grid-3">
    {row_6}
  </div>

  <footer>
    Source: <code>main_admin.*</code> tables + page-build-time probes
    (<code>{health_url}</code>, DuckDB size). Generated by
    <code>scripts/generate_admin_dashboard.py</code>. See design doc
    <code>docs/dba-dashboard-design-2026-05-17.md</code>.
  </footer>
</body>
</html>
"""


def render_panel(panel_id: str, name: str, color: str, headline: str, why: str, sql: str, source_table: str) -> str:
    return f"""
    <div class="panel" data-panel-id="{html.escape(panel_id)}">
      <div class="panel-title"><span class="panel-status {color}"></span>{panel_id} · {html.escape(name)}</div>
      <div class="panel-value">{why}</div>
      <div class="panel-cite">
        <details>
          <summary>Source: <code>{html.escape(source_table)}</code></summary>
          <pre>{html.escape(sql.strip())}</pre>
        </details>
      </div>
    </div>
    """


def main() -> int:
    now = datetime.now()
    con = duckdb.connect(DUCKDB_PATH, read_only=True)

    panels = []
    # (panel_id, display_name, fn, args)
    panels.append(("A1", "Last refresh", *panel_a1_last_refresh(con, now)))
    panels.append(("A2", "Streak (30d)", *panel_a2_streak(con, now)))
    panels.append(("A3", "Duration trend", *panel_a3_duration_trend(con, now)))
    panels.append(("B1", "Source freshness", *panel_b1_source_freshness(con, now)))
    panels.append(("B2", "dbt tests", *panel_b2_dbt_tests(con, now)))
    panels.append(("B3", "Profile coverage", *panel_b3_profile_coverage(con, now)))
    panels.append(("C1", "Chat activity (7d)", *panel_c1_chat_activity(con, now)))
    panels.append(("C2", "Cost (MTD)", *panel_c2_cost(con, now)))
    panels.append(("D1", "Oxygen runtime health", *panel_d1_oxygen_health(now)))
    panels.append(("D2", "Warehouse size", *panel_d2_warehouse_size(con, now)))

    # panels rows: (panel_id, name, color, severity, headline, why, sql, source_table)
    # Strict-yellow rule: any red on critical → RED; any non-green → YELLOW; else GREEN
    headline_color = GREEN
    yellow_items = []
    for pid, name, color, severity, headline, why, sql, source_table in panels:
        if color == RED and severity == CRITICAL:
            headline_color = RED
        elif color != GREEN:
            yellow_items.append((pid, name, severity, headline, color))
            if headline_color == GREEN:
                headline_color = YELLOW
    # Even if headline is red, list all non-green items in advisory
    if headline_color == RED:
        for pid, name, color, severity, headline, why, sql, source_table in panels:
            if color != GREEN and (pid, name, severity, headline, color) not in yellow_items:
                yellow_items.append((pid, name, severity, headline, color))

    # Sort: criticals first
    yellow_items.sort(key=lambda x: (0 if x[2] == CRITICAL else 1, x[0]))

    if not yellow_items:
        advisory_body = '<p style="margin:0;color:#2d8856;font-weight:600;">All systems green.</p>'
    else:
        advisory_body = '<ul>' + "".join(
            f'<li><strong>{pid}</strong> ({name}, {severity}): {html.escape(str(headline))}</li>'
            for pid, name, severity, headline, color in yellow_items
        ) + '</ul>'

    headline_summary_parts = []
    if any(it[4] == RED for it in yellow_items):
        headline_summary_parts.append(f"{sum(1 for it in yellow_items if it[4] == RED)} critical")
    if yellow_items:
        headline_summary_parts.append(f"{len(yellow_items)} advisory items")
    headline_summary = " · ".join(headline_summary_parts) if headline_summary_parts else "All systems green"

    refresh_ago = "just now"  # generation time

    # Render panel rows
    by_id = {pid: (pid, name, color, severity, headline, why, sql, source_table)
             for pid, name, color, severity, headline, why, sql, source_table in panels}

    def render(pid):
        _, name, color, severity, headline, why, sql, source_table = by_id[pid]
        return render_panel(pid, name, color, headline, why, sql, source_table)

    row_3 = render("A1") + render("A2") + render("A3")
    row_4 = render("B1")
    row_5 = render("B2") + render("B3") + render("C1")
    row_6 = render("C2") + render("D1") + render("D2")

    page = PAGE_TEMPLATE.format(
        headline_color=headline_color,
        headline_color_upper=headline_color.upper(),
        headline_summary=headline_summary,
        refresh_ago=refresh_ago,
        advisory_body=advisory_body,
        row_3=row_3,
        row_4=row_4,
        row_5=row_5,
        row_6=row_6,
        health_url=OXY_HEALTH_URL,
    )

    DEPLOY_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = DEPLOY_PATH.with_suffix(".html.tmp")
    tmp.write_text(page)
    tmp.replace(DEPLOY_PATH)
    con.close()
    print(f"  wrote {DEPLOY_PATH} ({len(page)} bytes; headline={headline_color})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
