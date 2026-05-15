#!/usr/bin/env python3
"""
Generate a static /trust page from admin.fct_test_run.

Reads the most recent run from the admin DQ tables, plus data freshness
from gold.fct_311_requests, and emits an HTML page with a status banner,
freshness stats, and a per-test results table sorted failures-first.
Output: `portal/trust.html`. run.sh copies it to
`/var/www/somerville/trust.html` for nginx to serve at /trust.

Pure-Python build tool — opens DuckDB read-only. Runs after dbt (admin
schema must be populated first); see run.sh sequencing.

Design tokens match portal/index.html and portal/metrics.html.
"""
from __future__ import annotations

import statistics
import sys
from datetime import timedelta
from html import escape
from pathlib import Path

import duckdb

# Eastern time offset for display in the run-history table. EDT (UTC-4)
# used year-round; matches generate_homepage_summary.py.
ET_OFFSET = timedelta(hours=-4)
RUN_HISTORY_LIMIT = 30
PIPELINE_HISTORY_LIMIT = 30

# Local import: scripts/_nav.py is the shared nav source.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nav import nav_html, NAV_CSS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "somerville.duckdb"
OUT_PATH = REPO_ROOT / "portal" / "trust.html"


def fetch_latest_run(conn) -> tuple | None:
    row = conn.execute(
        """
        SELECT run_id, MAX(run_at) AS run_at
        FROM main_admin.fct_test_run
        GROUP BY run_id
        ORDER BY run_at DESC
        LIMIT 1
        """
    ).fetchone()
    return row


def fetch_run_summary(conn, run_id) -> tuple:
    return conn.execute(
        """
        SELECT
            COUNT(*) FILTER (WHERE status = 'pass') AS pass_count,
            COUNT(*) FILTER (WHERE status = 'fail') AS fail_count,
            COUNT(*) FILTER (WHERE status = 'warn') AS warn_count,
            COUNT(*)                                AS total_count
        FROM main_admin.fct_test_run
        WHERE run_id = ?
        """,
        [run_id],
    ).fetchone()


def fetch_run_tests(conn, run_id) -> list[tuple]:
    return conn.execute(
        """
        SELECT
            r.test_id,
            COALESCE(d.test_type, '')   AS test_type,
            COALESCE(d.table_name, '')  AS table_name,
            COALESCE(d.column_name, '') AS column_name,
            r.status,
            r.actual_value,
            r.expected_value,
            r.variance_pct,
            r.failure_message
        FROM main_admin.fct_test_run r
        LEFT JOIN main_admin.dim_data_quality_test d USING (test_id)
        WHERE r.run_id = ?
        ORDER BY
            CASE r.status WHEN 'fail' THEN 0 WHEN 'warn' THEN 1 ELSE 2 END,
            r.test_id
        """,
        [run_id],
    ).fetchall()


def fetch_run_history(conn, limit: int = RUN_HISTORY_LIMIT) -> list[tuple]:
    """Aggregate per-run test outcomes for the most recent `limit` runs.

    Returns (run_id, run_at_utc, pass_count, fail_count, warn_count,
    total_count), newest first.
    """
    return conn.execute(
        f"""
        SELECT
            run_id,
            MAX(run_at)                              AS run_at,
            COUNT(*) FILTER (WHERE status = 'pass')  AS pass_count,
            COUNT(*) FILTER (WHERE status = 'fail')  AS fail_count,
            COUNT(*) FILTER (WHERE status = 'warn')  AS warn_count,
            COUNT(*)                                 AS total_count
        FROM main_admin.fct_test_run
        GROUP BY run_id
        ORDER BY run_at DESC
        LIMIT {int(limit)}
        """
    ).fetchall()


def fetch_pipeline_run_history(conn, limit: int = PIPELINE_HISTORY_LIMIT) -> list[tuple]:
    """Operational history of recent pipeline runs from fct_pipeline_run_raw.

    Returns rows newest-first with: run_id, run_started_at (UTC),
    run_completed_at (UTC, nullable), run_duration_seconds (nullable),
    run_type, run_status, records_fetched (nullable),
    records_new (nullable), records_updated (nullable),
    error_stage (nullable).
    """
    return conn.execute(
        f"""
        SELECT
            run_id,
            run_started_at,
            run_completed_at,
            run_duration_seconds,
            run_type,
            run_status,
            records_fetched,
            records_new,
            records_updated,
            error_stage
        FROM main_admin.fct_pipeline_run_raw
        ORDER BY run_started_at DESC
        LIMIT {int(limit)}
        """
    ).fetchall()


def fetch_data_freshness(conn) -> tuple:
    return conn.execute(
        """
        SELECT
            MAX(date_created_ts)       AS max_opened_ts,
            MAX(most_recent_status_ts) AS max_updated_ts,
            COUNT(*)                   AS total_rows
        FROM main_gold.fct_311_requests
        """
    ).fetchone()


def fmt_ts(ts) -> str:
    if ts is None:
        return "—"
    return ts.strftime("%Y-%m-%d %H:%M UTC")


def fmt_ts_et(ts) -> str:
    if ts is None:
        return "—"
    return (ts + ET_OFFSET).strftime("%Y-%m-%d %H:%M ET")


def fmt_ts_et_short(ts) -> str:
    """ET timestamp without the trailing ' ET' label (the column header carries
    that label in the pipeline-history table)."""
    if ts is None:
        return "—"
    return (ts + ET_OFFSET).strftime("%Y-%m-%d %H:%M")


def fmt_duration(secs) -> str:
    """Human-friendly Xm Ys / Xs / Xh Ym duration. NULL/None -> em dash."""
    if secs is None:
        return "—"
    secs = int(secs)
    if secs < 60:
        return f"{secs}s"
    m, s = divmod(secs, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


def fmt_count(n) -> str:
    if n is None:
        return "—"
    return f"{int(n):,}"


def fmt_int(n) -> str:
    if n is None:
        return "—"
    return f"{int(n):,}"


def fmt_variance(v) -> str:
    if v is None:
        return ""
    return f"{v * 100:+.2f}%"


def render_table_target(table_name: str, column_name: str) -> str:
    if table_name and column_name:
        return f"{escape(table_name)}.{escape(column_name)}"
    if table_name:
        return escape(table_name)
    return ""


def render_test_row(t: tuple) -> str:
    (test_id, test_type, table_name, column_name, status,
     actual, expected, variance_pct, message) = t
    status_class = {
        "pass": "badge-pass",
        "fail": "badge-fail",
        "warn": "badge-warn",
    }.get(status, "badge-warn")
    return f"""
    <tr class="row-{escape(status)}">
      <td><span class="badge {status_class}">{escape(status)}</span></td>
      <td class="mono test-id">{escape(test_id)}</td>
      <td class="mono">{render_table_target(table_name, column_name)}</td>
      <td class="mono">{escape(actual or "")}</td>
      <td class="mono">{escape(expected or "")}</td>
      <td class="mono">{fmt_variance(variance_pct)}</td>
      <td>{escape(message or "")}</td>
    </tr>
    """


def render_no_run() -> str:
    return _wrap(
        body_inner="""
        <header class="hero">
          <span class="hero-label">Trust report</span>
          <h1>No pipeline runs yet.</h1>
          <p>Run <code>./run.sh</code> on the warehouse host to populate
          <code>main_admin.fct_test_run</code>; this page reflects the most
          recent run.</p>
        </header>
        """,
    )


def render_history_section(history: list[tuple]) -> str:
    """Render the "Pipeline reliability" section (history of last N runs)."""
    if not history:
        return ""

    total_runs = len(history)
    fully_passing = sum(1 for h in history if h[3] == 0)

    # Sparkline: one tile per run, oldest-left to newest-right, so the
    # eye reads "recent green streak" left-to-right like a calendar.
    sparkline_cells = []
    for run_id, run_at, p, f, w, total in reversed(history):
        if f > 0:
            cls, label = "spark-fail", "fail"
        elif w > 0:
            cls, label = "spark-warn", "warn"
        else:
            cls, label = "spark-pass", "pass"
        sparkline_cells.append(
            f'<span class="spark-cell {cls}" '
            f'title="{escape(fmt_ts_et(run_at))} — {p}/{total} pass, '
            f'{f} fail, {w} warn"></span>'
        )

    rows = []
    for run_id, run_at, p, f, w, total in history:
        if f > 0:
            badge_cls = "badge-fail"
            badge_text = f"{f} failed"
        elif w > 0:
            badge_cls = "badge-warn"
            badge_text = f"{w} warn"
        else:
            badge_cls = "badge-pass"
            badge_text = "all pass"
        rows.append(
            f"""
            <tr>
              <td class="mono">{escape(fmt_ts_et(run_at))}</td>
              <td class="num">{total}</td>
              <td class="num">{p}</td>
              <td class="num">{f}</td>
              <td class="num">{w}</td>
              <td><span class="badge {badge_cls}">{escape(badge_text)}</span></td>
            </tr>
            """
        )

    return f"""
    <section class="history">
      <div class="section-num">03</div>
      <div class="section-title">Pipeline reliability</div>
      <p class="section-lede"><strong>{fully_passing} of the last
      {total_runs} runs</strong> passed all tests. Each tile below is one
      pipeline run, oldest on the left — green is all-pass, amber is
      warn-only, red is any-fail.</p>
      <div class="sparkline">{''.join(sparkline_cells)}</div>
      <div class="table-wrap">
        <table class="tests-table">
          <thead>
            <tr>
              <th>Run completed</th>
              <th>Tests</th>
              <th>Pass</th>
              <th>Fail</th>
              <th>Warn</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
    </section>
    """


def render_pipeline_history_section(pipeline_history: list[tuple]) -> str:
    """Operational history table — run timing + record counts.

    Distinct from `render_history_section` (which aggregates test-run
    outcomes by run_id). This one shows the pipeline's operational
    shape: when it started, how long it ran, what it pulled.
    """
    if not pipeline_history:
        return ""

    durations = [int(r[3]) for r in pipeline_history if r[3] is not None]
    if durations:
        median_secs = int(statistics.median(durations))
        median_str = fmt_duration(median_secs)
        n_with_duration = len(durations)
        summary = (
            f"Median run time across the last {n_with_duration} completed "
            f"runs: <strong>{escape(median_str)}</strong>."
        )
    else:
        summary = "No completed runs recorded yet."

    rows: list[str] = []
    for (run_id, started, completed, duration_s, run_type, status,
         fetched, new, updated, error_stage) in pipeline_history:
        if status == "success":
            badge_cls, badge_text = "badge-pass", "success"
        elif status == "partial":
            badge_cls, badge_text = "badge-warn", "partial"
        elif status == "failed":
            badge_cls, badge_text = "badge-fail", "failed"
        else:
            badge_cls, badge_text = "badge-warn", status or "?"
        # For failed runs, append the failing stage name as a small note
        # so operators see at a glance where the run halted.
        status_html = f'<span class="badge {badge_cls}">{escape(badge_text)}</span>'
        if status == "failed" and error_stage:
            status_html += (
                f' <span class="run-error-stage">at '
                f'<code>{escape(error_stage)}</code></span>'
            )
        rows.append(
            f"""
            <tr>
              <td class="mono">{escape(fmt_ts_et_short(started))}</td>
              <td class="mono">{escape(fmt_ts_et_short(completed))}</td>
              <td class="num">{escape(fmt_duration(duration_s))}</td>
              <td>{status_html}</td>
              <td class="num">{escape(fmt_count(fetched))}</td>
              <td class="num">{escape(fmt_count(new))}</td>
              <td class="num">{escape(fmt_count(updated))}</td>
            </tr>
            """
        )

    return f"""
    <section class="pipeline-history">
      <div class="section-num">04</div>
      <div class="section-title">Pipeline history</div>
      <p class="section-lede">{summary} Times in ET. Records-fetched
      columns are populated from Plan 1a onward; older runs show
      &mdash;.</p>
      <div class="table-wrap">
        <table class="tests-table">
          <thead>
            <tr>
              <th>Started (ET)</th>
              <th>Completed (ET)</th>
              <th>Duration</th>
              <th>Status</th>
              <th>Records fetched</th>
              <th>New</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
    </section>
    """


def render(run_id, run_at, summary, tests, freshness, history,
           pipeline_history) -> str:
    pass_count, fail_count, warn_count, total_count = summary
    max_opened_ts, max_updated_ts, total_rows = freshness
    overall_pass = fail_count == 0
    banner_class = "banner-pass" if overall_pass else "banner-fail"
    banner_label = (
        "All tests passed"
        if overall_pass
        else f"{fail_count} test{'s' if fail_count != 1 else ''} failed"
    )

    rows_html = "\n".join(render_test_row(t) for t in tests) if tests else (
        "<tr><td colspan='7'>No tests recorded for this run.</td></tr>"
    )
    warn_chip = (
        f'<span class="chip chip-warn">{warn_count} warn</span>'
        if warn_count else ""
    )

    body_inner = f"""
    <header class="hero">
      <span class="hero-label">Trust report</span>
      <div class="banner {banner_class}">
        <div class="banner-label">{escape(banner_label)}</div>
        <div class="banner-meta">
          <span class="chip chip-pass">{pass_count} pass</span>
          {warn_chip}
          {f'<span class="chip chip-fail">{fail_count} fail</span>' if fail_count else ''}
          <span class="chip chip-total">{total_count} total</span>
        </div>
      </div>
      <div class="run-meta">
        <span><span class="label-mono">run_at</span> {escape(fmt_ts(run_at))}</span>
        <span><span class="label-mono">run_id</span> <code>{escape(str(run_id)[:12])}…</code></span>
      </div>
    </header>

    <section class="freshness">
      <div class="section-num">01</div>
      <div class="section-title">Data freshness</div>
      <div class="freshness-grid">
        <div class="stat">
          <div class="stat-value">{fmt_int(total_rows)}</div>
          <div class="stat-label">Total 311 rows in gold</div>
        </div>
        <div class="stat">
          <div class="stat-value mono-stat">{escape(fmt_ts(max_opened_ts))}</div>
          <div class="stat-label">Latest <code>date_created_ts</code></div>
        </div>
        <div class="stat">
          <div class="stat-value mono-stat">{escape(fmt_ts(max_updated_ts))}</div>
          <div class="stat-label">Latest <code>most_recent_status_ts</code></div>
        </div>
      </div>
    </section>

    <section class="tests">
      <div class="section-num">02</div>
      <div class="section-title">Test results</div>
      <p class="section-lede">Every test recorded for the latest run, sorted
      failures-first. Two test families: <code>baseline.*</code> compares
      live row counts to a frozen expected value; <code>dbt_test.*</code>
      surfaces every dbt test from <code>run_results.json</code>.</p>
      <div class="table-wrap">
        <table class="tests-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Test</th>
              <th>Target</th>
              <th>Actual</th>
              <th>Expected</th>
              <th>Variance</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </section>

    {render_history_section(history)}

    {render_pipeline_history_section(pipeline_history)}
    """
    return _wrap(body_inner)


def _wrap(body_inner: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Trust — Somerville 311</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  @font-face {{ font-family: 'DM Serif Display'; src: url('/fonts/DMSerifDisplay-Regular.woff2') format('woff2'); font-weight: 400; font-style: normal; }}
  @font-face {{ font-family: 'DM Mono';          src: url('/fonts/DMMono-Regular.woff2')          format('woff2'); font-weight: 400; font-style: normal; }}
  @font-face {{ font-family: 'Instrument Sans';  src: url('/fonts/InstrumentSans-Regular.woff2')  format('woff2'); font-weight: 400; font-style: normal; }}
  @font-face {{ font-family: 'Instrument Sans';  src: url('/fonts/InstrumentSans-Medium.woff2')   format('woff2'); font-weight: 500; font-style: normal; }}

  :root {{
    --bg:         #f7f6f2;
    --bg-card:    #ffffff;
    --bg-stat:    #f0eeea;
    --text:       #1a1a1a;
    --text-mid:   #4a4a4a;
    --text-muted: #8a8a8a;
    --green:      #2c5f2d;
    --green-pale: #e8f0eb;
    --red:        #8b1f1f;
    --red-pale:   #f4e5e5;
    --amber:      #8a6a1a;
    --amber-pale: #f5edd9;
    --border:     #e3e1dc;
  }}

  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: 'Instrument Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.55;
  }}
  a {{ color: var(--text-mid); }}
  a:hover {{ color: var(--text); }}
  code {{ font-family: 'DM Mono', monospace; font-size: 0.92em; }}

{NAV_CSS}

  .hero {{ padding: 48px 40px 24px; max-width: 960px; }}
  .hero-label {{
    font-family: 'DM Mono', monospace;
    font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--green); display: inline-block; padding-bottom: 12px;
  }}
  .banner {{
    border-radius: 8px;
    padding: 24px 28px;
    border: 1px solid var(--border);
    display: flex; align-items: center; gap: 24px; flex-wrap: wrap;
  }}
  .banner-pass {{ background: var(--green-pale); border-color: #b8d4c0; }}
  .banner-fail {{ background: var(--red-pale);   border-color: #d4b8b8; }}
  .banner-label {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 32px; line-height: 1.1;
  }}
  .banner-pass .banner-label {{ color: var(--green); }}
  .banner-fail .banner-label {{ color: var(--red); }}
  .banner-meta {{ display: flex; gap: 8px; flex-wrap: wrap; }}
  .chip {{
    font-family: 'DM Mono', monospace; font-size: 12px;
    padding: 3px 9px; border-radius: 4px; border: 1px solid var(--border);
    background: #ffffff; color: var(--text-mid);
  }}
  .chip-pass  {{ color: var(--green); border-color: #b8d4c0; background: var(--green-pale); }}
  .chip-fail  {{ color: var(--red);   border-color: #d4b8b8; background: var(--red-pale); }}
  .chip-warn  {{ color: var(--amber); border-color: #d8c896; background: var(--amber-pale); }}
  .chip-total {{ color: var(--text-muted); }}
  .run-meta {{
    margin-top: 14px; display: flex; gap: 24px; flex-wrap: wrap;
    font-size: 13px; color: var(--text-mid);
  }}
  .label-mono {{
    font-family: 'DM Mono', monospace; font-size: 11px;
    letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted);
    margin-right: 4px;
  }}

  section {{ padding: 28px 40px; max-width: 1600px; }}
  .section-num {{
    font-family: 'DM Mono', monospace; font-size: 11px;
    letter-spacing: 0.08em; color: var(--text-muted);
  }}
  .section-title {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 26px; margin: 4px 0 12px;
  }}
  .section-lede {{ color: var(--text-mid); margin: 0 0 16px; max-width: 720px; }}

  .freshness-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px;
    background: var(--border); border: 1px solid var(--border);
    border-radius: 8px; overflow: hidden;
  }}
  .stat {{ background: var(--bg-card); padding: 22px 24px; }}
  .stat-value {{
    font-size: 28px; font-weight: 600; letter-spacing: -0.5px; line-height: 1.1;
  }}
  .stat-value.mono-stat {{
    font-family: 'DM Mono', monospace; font-size: 16px; font-weight: 400;
    letter-spacing: 0;
  }}
  .stat-label {{ color: var(--text-muted); font-size: 13px; margin-top: 6px; }}

  .table-wrap {{
    overflow-x: auto; border: 1px solid var(--border); border-radius: 8px;
    background: var(--bg-card);
    /* Always-visible thin scrollbar so users see the table is horizontally
       scrollable on narrower viewports (macOS hides scrollbars by default). */
    scrollbar-width: thin;
  }}
  .table-wrap::-webkit-scrollbar {{ height: 8px; }}
  .table-wrap::-webkit-scrollbar-track {{ background: var(--bg-stat); }}
  .table-wrap::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
  .tests-table {{
    width: 100%; border-collapse: collapse; font-size: 13px;
  }}
  .tests-table th, .tests-table td {{
    padding: 10px 12px; text-align: left; vertical-align: top;
    border-bottom: 1px solid var(--border);
  }}
  .tests-table th {{
    font-family: 'DM Mono', monospace; font-size: 11px;
    letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-muted);
    background: var(--bg-stat); font-weight: 500;
  }}
  .tests-table tr:last-child td {{ border-bottom: none; }}
  .tests-table .mono {{ font-family: 'DM Mono', monospace; font-size: 12px; word-break: break-all; }}
  .tests-table .test-id {{ color: var(--text); word-break: break-all; }}
  .tests-table .row-fail td {{ background: #fbf3f3; }}
  .tests-table .row-warn td {{ background: #fbf6e8; }}

  .badge {{
    font-family: 'DM Mono', monospace; font-size: 11px;
    padding: 2px 8px; border-radius: 4px; border: 1px solid var(--border);
    text-transform: uppercase; letter-spacing: 0.05em;
  }}
  .badge-pass {{ color: var(--green); border-color: #b8d4c0; background: var(--green-pale); }}
  .badge-fail {{ color: var(--red);   border-color: #d4b8b8; background: var(--red-pale); }}
  .badge-warn {{ color: var(--amber); border-color: #d8c896; background: var(--amber-pale); }}

  /* Run-history section (Item 5) */
  .tests-table td.num {{
    font-family: 'DM Mono', monospace; font-size: 12px;
    text-align: right; white-space: nowrap;
  }}
  .run-error-stage {{
    font-size: 11px; color: var(--text-muted); margin-left: 6px;
    white-space: nowrap;
  }}
  .run-error-stage code {{
    background: var(--bg-stat); padding: 1px 5px; border-radius: 3px;
    font-size: 11px;
  }}
  .sparkline {{
    display: flex; flex-wrap: wrap; gap: 4px;
    margin: 8px 0 20px;
  }}
  .spark-cell {{
    width: 18px; height: 18px; border-radius: 3px;
    border: 1px solid var(--border);
    background: var(--bg-stat);
  }}
  .spark-cell.spark-pass {{ background: var(--green-pale); border-color: #b8d4c0; }}
  .spark-cell.spark-warn {{ background: var(--amber-pale); border-color: #d8c896; }}
  .spark-cell.spark-fail {{ background: var(--red-pale);   border-color: #d4b8b8; }}
</style>
</head>
<body>
  {nav_html(active="trust")}

  {body_inner}
</body>
</html>
"""


def main() -> int:
    if not DB_PATH.exists():
        # Local dev environment may not have the warehouse — degrade gracefully
        # rather than break the pipeline.
        print(f"  WARNING: {DB_PATH} not found; trust page not generated", file=sys.stderr)
        return 0

    conn = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        run = fetch_latest_run(conn)
        if not run:
            html = render_no_run()
            n = 0
        else:
            run_id, run_at = run
            summary = fetch_run_summary(conn, run_id)
            tests = fetch_run_tests(conn, run_id)
            freshness = fetch_data_freshness(conn)
            history = fetch_run_history(conn)
            pipeline_history = fetch_pipeline_run_history(conn)
            html = render(run_id, run_at, summary, tests, freshness,
                          history, pipeline_history)
            n = summary[3]
    finally:
        conn.close()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"  wrote {OUT_PATH} ({n} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
