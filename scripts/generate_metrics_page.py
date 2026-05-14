#!/usr/bin/env python3
"""
Generate a static /metrics page from the Airlayer view YAML.

Walks `semantics/views/*.view.yml`, expands every `measures:` entry, and
emits an HTML page listing each measure with its description, type,
filters, and the SQL it expands to. Output: `portal/metrics.html`.
Run.sh copies it to `/var/www/somerville/metrics.html` for serving.

SQL is composed directly from the YAML structure (declarative). We do
not call airlayer at runtime — the YAML itself is authoritative for
measure semantics, and the generator stays a pure-Python build tool
that doesn't need a DuckDB connection.

Design tokens (fonts, colors) match portal/index.html.
"""
from __future__ import annotations

import sys
from pathlib import Path
from html import escape

import yaml

# Local import: scripts/_nav.py is the shared nav source.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nav import nav_html, NAV_CSS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
VIEWS_DIR = REPO_ROOT / "semantics" / "views"
OUT_PATH = REPO_ROOT / "portal" / "metrics.html"


def expand_measure_sql(view: dict, measure: dict) -> str:
    """Compose the SQL a measure expands to, given its view and definition."""
    table = view.get("table", "<unknown_table>")
    mtype = measure.get("type", "count")
    expr = measure.get("expr")
    filters = measure.get("filters", []) or []
    where = " AND ".join(f["expr"] for f in filters if f.get("expr"))

    if mtype == "count":
        select = "COUNT(*)"
    elif mtype == "count_distinct" and expr:
        select = f"COUNT(DISTINCT {expr})"
    elif mtype == "sum" and expr:
        select = f"SUM({expr})"
    elif mtype == "avg" and expr:
        select = f"AVG({expr})"
    elif mtype == "min" and expr:
        select = f"MIN({expr})"
    elif mtype == "max" and expr:
        select = f"MAX({expr})"
    else:
        select = f"{mtype.upper()}({expr or '*'})"

    sql = f"SELECT {select} AS {measure['name']}\nFROM {table}"
    if where:
        sql += f"\nWHERE {where}"
    return sql


def load_views() -> list[dict]:
    views = []
    for path in sorted(VIEWS_DIR.glob("*.view.yml")):
        with open(path) as f:
            views.append(yaml.safe_load(f))
    return views


def render_measure_card(view: dict, measure: dict) -> str:
    name = measure.get("name", "")
    desc = measure.get("description", "")
    mtype = measure.get("type", "")
    filters = measure.get("filters", []) or []
    sql = expand_measure_sql(view, measure)

    filter_html = ""
    if filters:
        items = "".join(
            f'<li><code>{escape(f.get("expr", ""))}</code></li>' for f in filters
        )
        filter_html = f"<div class='label'>Filters</div><ul class='filters'>{items}</ul>"

    return f"""
    <article class="measure-card">
      <div class="measure-head">
        <span class="measure-view">{escape(view.get("name", ""))}</span>
        <span class="measure-sep">·</span>
        <h2 class="measure-name">{escape(name)}</h2>
        <span class="measure-type">{escape(mtype)}</span>
      </div>
      <p class="measure-desc">{escape(desc) if desc else "<em>No description</em>"}</p>
      {filter_html}
      <div class="label">Expanded SQL</div>
      <pre class="sql"><code>{escape(sql)}</code></pre>
    </article>
    """


def render(views: list[dict]) -> str:
    cards = []
    measure_count = 0
    for view in views:
        for m in view.get("measures") or []:
            cards.append(render_measure_card(view, m))
            measure_count += 1

    body = "\n".join(cards) if cards else "<p>No measures defined yet.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Metrics — Somerville 311</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  @font-face {{ font-family: 'DM Serif Display'; src: url('/fonts/DMSerifDisplay-Regular.woff2') format('woff2'); font-weight: 400; font-style: normal; }}
  @font-face {{ font-family: 'DM Mono';          src: url('/fonts/DMMono-Regular.woff2')          format('woff2'); font-weight: 400; font-style: normal; }}
  @font-face {{ font-family: 'Instrument Sans';  src: url('/fonts/InstrumentSans-Regular.woff2')  format('woff2'); font-weight: 400; font-style: normal; }}
  @font-face {{ font-family: 'Instrument Sans';  src: url('/fonts/InstrumentSans-Medium.woff2')   format('woff2'); font-weight: 500; font-style: normal; }}

  :root {{
    --bg:         #f7f6f2;
    --bg-card:    #ffffff;
    --white:      #ffffff;
    --text:       #1a1a1a;
    --text-mid:   #4a4a4a;
    --text-muted: #8a8a8a;
    --green:      #1e4d2b;
    --green-mid:  #2d6a3f;
    --green-pale: #e8f0eb;
    --border:     #e2dfd8;
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

{NAV_CSS}

  .hero {{ padding: 56px 40px 28px; max-width: 720px; }}
  .hero-label {{
    font-family: 'DM Mono', monospace;
    font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--green); display: inline-block; padding-bottom: 6px;
  }}
  .hero h1 {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 46px; line-height: 1.05; margin: 6px 0 12px;
  }}
  .hero p {{ color: var(--text-mid); font-size: 16px; max-width: 560px; }}
  .hero .count {{
    font-family: 'DM Mono', monospace; font-size: 13px;
    color: var(--text-muted); margin-top: 12px;
  }}

  main {{ padding: 12px 40px 80px; max-width: 1100px; }}
  .measure-card {{
    background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px;
    padding: 22px 24px; margin-bottom: 16px;
  }}
  .measure-head {{ display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }}
  .measure-view {{
    font-family: 'DM Mono', monospace; font-size: 12px;
    color: var(--text-muted); letter-spacing: 0.04em;
  }}
  .measure-sep {{ color: var(--text-muted); }}
  .measure-name {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 22px; margin: 0;
  }}
  .measure-type {{
    margin-left: auto;
    font-family: 'DM Mono', monospace; font-size: 11px; color: var(--green);
    background: var(--green-pale); border: 1px solid #b8d4c0;
    padding: 2px 8px; border-radius: 4px; letter-spacing: 0.04em;
  }}
  .measure-desc {{ color: var(--text-mid); margin: 10px 0 14px; font-size: 15px; }}
  .label {{
    font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--text-muted); margin: 12px 0 6px;
  }}
  .filters {{ list-style: none; padding: 0; margin: 0 0 4px; }}
  .filters li {{ font-family: 'DM Mono', monospace; font-size: 13px; padding: 2px 0; }}
  .filters code {{
    background: var(--bg); border: 1px solid var(--border);
    padding: 1px 6px; border-radius: 3px;
  }}
  pre.sql {{
    font-family: 'DM Mono', monospace; font-size: 13px;
    background: var(--bg); border: 1px solid var(--border); border-radius: 4px;
    padding: 12px 14px; margin: 0; overflow-x: auto; line-height: 1.5;
  }}
  pre.sql code {{ color: var(--text); }}
</style>
</head>
<body>
  {nav_html(active="metrics")}

  <header class="hero">
    <span class="hero-label">Metrics catalog</span>
    <h1>Every measure, expanded.</h1>
    <p>Auto-generated from the Airlayer view YAML. One card per measure, with
    its description, type, filters, and the SQL it expands to. Single source
    of truth for what each metric means.</p>
    <div class="count">{measure_count} measure{'' if measure_count == 1 else 's'} across {len(views)} view{'' if len(views) == 1 else 's'}.</div>
  </header>

  <main>
    {body}
  </main>
</body>
</html>
"""


def main() -> int:
    views = load_views()
    html = render(views)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    measure_count = sum(len(v.get("measures") or []) for v in views)
    print(f"  wrote {OUT_PATH} ({measure_count} measures across {len(views)} views)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
