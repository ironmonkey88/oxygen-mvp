#!/usr/bin/env python3
"""Generate a static /about page introducing Somerville itself.

Reads `main_bronze.raw_somerville_at_a_glance` (Prompt 11 Phase D bronze
view, 749 rows of long/tidy KPI data: 25 topics, Somerville +
Massachusetts comparator, years 1850-2024) and renders it as an
informational portal page. Distinct from the data-platform framing of
the homepage -- this is "what is this city" orienting context.

Per the Prompt 11 Phase E brief: NOT a dashboard. No tier structure.
Just the city's facts presented cleanly. Closer in spirit to the
Welcome section of the homepage than to a Data App.

Output: portal/about.html. run.sh copies it to
/var/www/somerville/about.html for nginx to serve at /about.

Pure-Python build tool -- opens DuckDB read-only. Matches the design
tokens (CSS vars, fonts) of the other generated portal pages.
"""
from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import duckdb

# Local import: scripts/_nav.py is the shared nav source.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nav import nav_html, NAV_CSS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "somerville.duckdb"
OUT_PATH = REPO_ROOT / "portal" / "about.html"

# Topics surfaced as "Latest snapshot" headline numbers (Somerville,
# latest year). Each entry: (topic, description, label, formatter).
HEADLINE_METRICS: tuple[tuple[str, str, str, str], ...] = (
    ("Population",                       "Total Population",       "Population",            "comma"),
    ("Median Household Income Overtime", "Median Household Income","Median household income","usd"),
    ("Median Home Value Overtime",       "Median Home Value",      "Median home value",     "usd"),
    ("Median Rent Overtime",             "Median Rent",            "Median rent",           "usd_per_month"),
)

# Topic ordering on the page. Topics not listed fall through to the
# tail in their natural order.
PRIORITY_TOPICS: tuple[str, ...] = (
    "Population",
    "Median Household Income Overtime",
    "Median Home Value Overtime",
    "Median Rent Overtime",
    "Race & Ethnicity",
    "Educational Attainment",
    "Foreigner-Born Residents",
    "Language Speakers",
    "Commute Mode",
    "Commute Time",
    "Place of Work",
    "Owners vs Renters",
    "Household by Income Category",
    "Poverty",
    "Rent Burdened Households",
    "Vacancy Rate",
    "Age Group",
    "Disability Characteristics",
)


def fetch_all_rows(conn) -> list[tuple]:
    return conn.execute(
        """
        SELECT topic, description, year, value, units, geography
        FROM main_bronze.raw_somerville_at_a_glance
        ORDER BY topic, year, geography, description
        """
    ).fetchall()


def fetch_last_refreshed(conn) -> str:
    row = conn.execute(
        """
        SELECT MAX(_extracted_at) FROM main_bronze.raw_somerville_at_a_glance
        """
    ).fetchone()
    ts = row[0] if row else None
    if ts is None:
        return "unknown"
    return ts.strftime("%Y-%m-%d")


def fmt(value, units: str, fmt_kind: str = "") -> str:
    """Format a numeric value for display.

    fmt_kind overrides take precedence over `units` heuristics.
    """
    if value is None:
        return "--"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return escape(str(value))
    if fmt_kind == "comma":
        return f"{int(v):,}"
    if fmt_kind == "usd":
        return f"${int(v):,}"
    if fmt_kind == "usd_per_month":
        return f"${int(v):,}/mo"
    # Heuristic from `units`
    units_lower = (units or "").lower()
    if "percent" in units_lower:
        return f"{v:g}%"
    if "usd" in units_lower or "dollar" in units_lower:
        return f"${int(v):,}"
    if "people" in units_lower or v.is_integer():
        return f"{int(v):,}"
    return f"{v:g}"


def _year_to_int(y) -> int:
    """Coerce a year value (may be str, int, or None) to int for sorting."""
    if y is None:
        return 0
    try:
        return int(y)
    except (TypeError, ValueError):
        return 0


def headline_value(rows: list[tuple], topic: str, description: str) -> tuple | None:
    """Return the (latest-year, value, units) Somerville row matching topic/description."""
    matches = [
        r for r in rows
        if r[0] == topic and r[1] == description and r[5] == "Somerville"
    ]
    if not matches:
        return None
    # Most recent year wins
    matches.sort(key=lambda r: _year_to_int(r[2]), reverse=True)
    r = matches[0]
    return (r[2], r[3], r[4])  # year, value, units


def render_headline_card(label: str, value_html: str, year, units: str) -> str:
    sub = f"in {year}" if year is not None else ""
    if units and units.lower() not in ("usd", "people"):
        sub = (sub + " | " + escape(units)) if sub else escape(units)
    return f"""
    <div class="headline-card">
      <div class="headline-value">{value_html}</div>
      <div class="headline-label">{escape(label)}</div>
      <div class="headline-sub">{escape(sub)}</div>
    </div>
    """


def render_topic_table(rows: list[tuple], topic: str) -> str:
    """Render a topic's rows as a compact two-column-by-geography table.

    Columns: Description, Year, Somerville value, Massachusetts value.
    """
    topic_rows = [r for r in rows if r[0] == topic]
    if not topic_rows:
        return ""

    # Group by (description, year), then pivot geography into columns
    by_key: dict[tuple, dict[str, tuple]] = {}
    for r in topic_rows:
        _, description, year, value, units, geography = r
        key = (description, year)
        by_key.setdefault(key, {})[geography] = (value, units)

    # Sort by (description, year DESC) so the most recent rises to the top.
    # year can be VARCHAR (dlt's inference) or numeric depending on source --
    # coerce safely.
    def _year_int(y):
        if y is None:
            return 0
        try:
            return int(y)
        except (TypeError, ValueError):
            return 0
    keys_sorted = sorted(
        by_key.keys(),
        key=lambda k: (k[0] or "", -_year_int(k[1])),
    )

    body = []
    for (description, year) in keys_sorted:
        cells = by_key[(description, year)]
        som = cells.get("Somerville")
        ma = cells.get("Massachusetts")
        som_val = fmt(som[0], som[1]) if som else "--"
        ma_val = fmt(ma[0], ma[1]) if ma else "--"
        # Pick units from either cell
        units = (som[1] if som else (ma[1] if ma else "")) or ""
        body.append(
            f"""
            <tr>
              <td class="topic-desc">{escape(description or "")}</td>
              <td class="topic-year mono">{escape(str(year) if year is not None else "--")}</td>
              <td class="topic-units mono">{escape(units)}</td>
              <td class="topic-val mono">{escape(som_val)}</td>
              <td class="topic-val mono">{escape(ma_val)}</td>
            </tr>
            """
        )

    rowcount = len(keys_sorted)
    return f"""
    <section class="topic-section">
      <h2 class="topic-title">{escape(topic)}</h2>
      <div class="topic-meta">{rowcount} row{'s' if rowcount != 1 else ''}</div>
      <div class="table-wrap">
        <table class="topic-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Year</th>
              <th>Units</th>
              <th>Somerville</th>
              <th>Massachusetts</th>
            </tr>
          </thead>
          <tbody>
            {"".join(body)}
          </tbody>
        </table>
      </div>
    </section>
    """


def render(rows: list[tuple], last_refreshed: str) -> str:
    # Headline cards
    headline_cards = []
    for topic, description, label, fmt_kind in HEADLINE_METRICS:
        hv = headline_value(rows, topic, description)
        if hv is None:
            continue
        year, value, units = hv
        value_html = escape(fmt(value, units, fmt_kind))
        headline_cards.append(
            render_headline_card(label, value_html, year, units)
        )

    # Ordered topic sections: priority first, then the rest
    all_topics = sorted({r[0] for r in rows})
    seen = set()
    ordered = []
    for t in PRIORITY_TOPICS:
        if t in all_topics:
            ordered.append(t)
            seen.add(t)
    for t in all_topics:
        if t not in seen:
            ordered.append(t)

    sections_html = "".join(render_topic_table(rows, t) for t in ordered)

    body_inner = f"""
    <header class="hero">
      <span class="hero-label">About Somerville</span>
      <h1>The city, in numbers.</h1>
      <p class="hero-lede">A short orientation: population, housing,
      education, commute, income -- side by side with Massachusetts as
      a comparator -- drawn from the city's "Somerville at a Glance"
      publication. Source for the underlying numbers is US Census +
      ACS via the city's open data portal. This page is part of an
      independent resident project, <strong>not affiliated with the
      City of Somerville</strong>; the numbers are the city's, the
      framing is ours.</p>
    </header>

    <section class="headlines">
      <div class="section-num">01</div>
      <div class="section-title">Latest snapshot</div>
      <p class="section-lede">The current values for the headline
      metrics. Years vary by metric (ACS releases on rolling cadences).</p>
      <div class="headline-grid">
        {"".join(headline_cards)}
      </div>
    </section>

    <section class="topics">
      <div class="section-num">02</div>
      <div class="section-title">By topic</div>
      <p class="section-lede">Every metric in the dataset, grouped by
      topic. Side-by-side Somerville and Massachusetts values where
      both are published. Sourced from
      <a href="https://data.somervillema.gov/dataset/Somerville-at-a-Glance/jnde-mi6j" target="_blank" rel="noopener">data.somervillema.gov/dataset/Somerville-at-a-Glance/jnde-mi6j</a>.</p>
      {sections_html}
    </section>

    <footer class="page-footer">
      <p>Source: City of Somerville open data portal -- "Somerville at
      a Glance" (Socrata dataset <code>jnde-mi6j</code>). Last
      ingested: <code>{escape(last_refreshed)}</code>. Limitations:
      <a href="/trust"><code>somerville-at-a-glance-acs-scope</code></a>
      (this is a pre-aggregated KPI summary, not microdata; not the
      authoritative source -- citations should go to Census/ACS for
      contested figures).</p>
      <p style="margin-top: 16px;">Independent resident project &middot;
      built on Somerville's public Open Data via
      <a href="https://data.somervillema.gov" target="_blank" rel="noopener">data.somervillema.gov</a>
      &middot; not affiliated with the City of Somerville.</p>
    </footer>
    """
    return _wrap(body_inner)


def _wrap(body_inner: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>About Somerville</title>
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
    --green:      #1e4d2b;
    --green-mid:  #2d6a3f;
    --green-pale: #e8f0eb;
    --border:     #e2dfd8;
    --white:      #ffffff;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: 'Instrument Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.55;
  }}
  a {{ color: var(--green-mid); }}
  a:hover {{ color: var(--green); }}
  code {{ font-family: 'DM Mono', monospace; font-size: 0.92em; }}

{NAV_CSS}

  .hero {{ padding: 48px 40px 8px; max-width: 960px; }}
  .hero-label {{
    font-family: 'DM Mono', monospace;
    font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--green); display: inline-block; padding-bottom: 12px;
  }}
  .hero h1 {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 44px; letter-spacing: -0.5px; margin: 0 0 14px;
  }}
  .hero-lede {{
    font-size: 16px; color: var(--text-mid); margin: 0; max-width: 720px;
  }}

  section {{ padding: 28px 40px; max-width: 1400px; }}
  .section-num {{
    font-family: 'DM Mono', monospace; font-size: 11px;
    letter-spacing: 0.08em; color: var(--text-muted);
  }}
  .section-title {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 26px; margin: 4px 0 12px;
  }}
  .section-lede {{ color: var(--text-mid); margin: 0 0 16px; max-width: 720px; }}

  /* Headline grid -- four large cards */
  .headline-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }}
  .headline-card {{
    background: var(--bg-card);
    padding: 28px 28px;
  }}
  .headline-value {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 32px;
    color: var(--green);
    letter-spacing: -0.5px;
    line-height: 1.05;
    margin-bottom: 6px;
  }}
  .headline-label {{
    font-size: 14px;
    font-weight: 500;
    color: var(--text);
  }}
  .headline-sub {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 0.03em;
    margin-top: 4px;
  }}

  /* Topic sections */
  .topic-section {{
    margin: 32px 0;
    padding-top: 24px;
    border-top: 1px solid var(--border);
  }}
  .topic-section:first-child {{ border-top: none; padding-top: 0; }}
  .topic-title {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 22px;
    font-weight: 400;
    margin: 0 0 4px;
    letter-spacing: -0.3px;
  }}
  .topic-meta {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 12px;
    letter-spacing: 0.04em;
  }}

  .table-wrap {{
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg-card);
    scrollbar-width: thin;
  }}
  .table-wrap::-webkit-scrollbar {{ height: 8px; }}
  .table-wrap::-webkit-scrollbar-track {{ background: var(--bg-stat); }}
  .table-wrap::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
  .topic-table {{
    width: 100%; border-collapse: collapse; font-size: 13px;
  }}
  .topic-table th, .topic-table td {{
    padding: 9px 12px;
    text-align: left;
    vertical-align: top;
    border-bottom: 1px solid var(--border);
  }}
  .topic-table th {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-muted);
    background: var(--bg-stat);
    font-weight: 500;
  }}
  .topic-table tr:last-child td {{ border-bottom: none; }}
  .topic-table .mono {{ font-family: 'DM Mono', monospace; }}
  .topic-table .topic-desc {{ color: var(--text); }}
  .topic-table .topic-year {{ color: var(--text-mid); white-space: nowrap; }}
  .topic-table .topic-units {{ color: var(--text-muted); font-size: 11px; }}
  .topic-table .topic-val {{ text-align: right; white-space: nowrap; }}

  .page-footer {{
    padding: 32px 40px 48px;
    color: var(--text-muted);
    font-size: 13px;
    max-width: 960px;
  }}
</style>
</head>
<body>
  {nav_html(active="about")}

  {body_inner}
</body>
</html>
"""


def main() -> int:
    if not DB_PATH.exists():
        print(f"  WARNING: {DB_PATH} not found; about page not generated", file=sys.stderr)
        return 0

    conn = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        rows = fetch_all_rows(conn)
        last_refreshed = fetch_last_refreshed(conn)
    finally:
        conn.close()

    html = render(rows, last_refreshed)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    n_topics = len({r[0] for r in rows})
    print(f"  wrote {OUT_PATH} ({len(rows)} rows across {n_topics} topics)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
