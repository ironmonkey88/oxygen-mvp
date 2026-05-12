#!/usr/bin/env python3
"""Generate the /profile portal page from schema.yml + fct_column_profile_raw.

Plan 1b decision 1b/D option (c): dbt's `schema.yml` files stay hand-written
and are the source of truth for column descriptions; this script does NOT
modify them. Profile shape data lives in `main_admin.fct_column_profile_raw`
and is surfaced on its own portal route at `/profile`.

The /profile page renders one section per (schema, table) and one row per
column with:
  - column name + type
  - hand-written description (from dbt's schema.yml)
  - profile facts (row count, non-null %, distinct count)
  - type-specific shape data (range for numeric/date; top-5 for text;
    true/false split for boolean)

Excludes the same patterns as profile_tables.py: tables starting with `_`
and tables ending with `_raw`.
"""
from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

import duckdb
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DUCKDB_PATH = REPO_ROOT / "data" / "somerville.duckdb"
SCHEMA_YML_FILES = [
    REPO_ROOT / "dbt" / "models" / "bronze" / "schema.yml",
    REPO_ROOT / "dbt" / "models" / "gold" / "schema.yml",
]
OUT_PATH = REPO_ROOT / "portal" / "profile.html"

SCHEMA_TO_LABEL = {
    "main_bronze": "Bronze (raw mirror)",
    "main_gold":   "Gold (business-ready)",
}


def load_descriptions() -> dict:
    """Return {(schema_label, table_name, column_name): description_html}.

    schema_label is derived from the file path (bronze, gold), not from
    the dbt source-schema metadata, so a missing source block doesn't
    drop the descriptions on the floor.
    """
    descs: dict[tuple[str, str, str], str] = {}
    for sf in SCHEMA_YML_FILES:
        if not sf.exists():
            continue
        layer = sf.parent.name  # 'bronze' or 'gold'
        with open(sf) as f:
            doc = yaml.safe_load(f)
        for model in doc.get("models", []):
            for col in model.get("columns", []):
                key = (layer, model["name"], col["name"])
                descs[key] = (col.get("description") or "").strip()
    return descs


def load_profiles() -> dict:
    """Return {(schema, table, column): latest_profile_row} as dicts."""
    with duckdb.connect(str(DUCKDB_PATH), read_only=True) as conn:
        rows = conn.execute("""
            WITH ranked AS (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY schema_name, table_name, column_name
                    ORDER BY profiled_at DESC
                ) AS rn
                FROM main_admin.fct_column_profile_raw
                WHERE table_name NOT LIKE '\\_%' ESCAPE '\\'
                  AND table_name NOT LIKE '%\\_raw' ESCAPE '\\'
            )
            SELECT
                schema_name, table_name, column_name, column_type,
                row_count, non_null_count, null_pct, distinct_count,
                min_value, max_value, mean_value, p50_value, p95_value,
                zero_count, negative_count,
                min_date, max_date, span_days,
                min_length, max_length, avg_length, empty_string_count, top_5_values,
                true_count, false_count,
                profiled_at
            FROM ranked WHERE rn = 1
            ORDER BY schema_name, table_name, column_name
        """).fetchall()
        cols = [
            "schema_name", "table_name", "column_name", "column_type",
            "row_count", "non_null_count", "null_pct", "distinct_count",
            "min_value", "max_value", "mean_value", "p50_value", "p95_value",
            "zero_count", "negative_count",
            "min_date", "max_date", "span_days",
            "min_length", "max_length", "avg_length", "empty_string_count", "top_5_values",
            "true_count", "false_count",
            "profiled_at",
        ]
    return {
        (r[0], r[1], r[2]): dict(zip(cols, r))
        for r in rows
    }


def format_shape(p: dict) -> str:
    """Return one short line summarizing type-specific shape."""
    bits: list[str] = []
    if p["min_value"] is not None:
        mn, mx, mean = p["min_value"], p["max_value"], p["mean_value"]
        p50, p95 = p["p50_value"], p["p95_value"]
        bits.append(f"range <code>{mn:g}</code>..<code>{mx:g}</code>")
        if mean is not None:
            bits.append(f"mean <code>{mean:.2f}</code>")
        if p50 is not None and p95 is not None:
            bits.append(f"p50 <code>{p50:g}</code>, p95 <code>{p95:g}</code>")
        if p["zero_count"]:
            bits.append(f"zeros <code>{p['zero_count']:,}</code>")
        if p["negative_count"]:
            bits.append(f"negative <code>{p['negative_count']:,}</code>")
    if p["min_date"] is not None:
        mnd = p["min_date"].date().isoformat() if hasattr(p["min_date"], "date") else str(p["min_date"])[:10]
        mxd = p["max_date"].date().isoformat() if hasattr(p["max_date"], "date") else str(p["max_date"])[:10]
        bits.append(f"dates <code>{mnd}</code> → <code>{mxd}</code>")
        if p["span_days"]:
            bits.append(f"span <code>{p['span_days']:,}</code> days")
    if p["min_length"] is not None:
        bits.append(f"len <code>{p['min_length']}</code>..<code>{p['max_length']}</code>")
        if p["empty_string_count"]:
            bits.append(f"empty strings <code>{p['empty_string_count']:,}</code>")
    if p["true_count"] is not None or p["false_count"] is not None:
        t = p["true_count"] or 0
        f = p["false_count"] or 0
        total = t + f
        if total > 0:
            bits.append(f"true <code>{t/total*100:.1f}%</code>")
    return " · ".join(bits)


def format_top5(top5_json: str | None) -> str:
    if not top5_json:
        return ""
    try:
        top5 = json.loads(top5_json)
    except (json.JSONDecodeError, TypeError):
        return ""
    items = []
    for entry in top5:
        v = escape(str(entry.get("value", "")))
        c = entry.get("count", 0)
        pct = entry.get("pct", 0)
        items.append(f'<li><code>{v}</code> <span class="muted">{c:,} ({pct}%)</span></li>')
    return f'<ul class="top5">{"".join(items)}</ul>'


def render(descs: dict, profiles: dict) -> str:
    by_schema_table: dict[tuple[str, str], list[dict]] = {}
    for key, p in profiles.items():
        st = (p["schema_name"], p["table_name"])
        by_schema_table.setdefault(st, []).append(p)

    sections = []
    last_profiled = None
    for (schema, table) in sorted(by_schema_table.keys()):
        layer = "bronze" if schema == "main_bronze" else "gold" if schema == "main_gold" else schema
        cols = sorted(by_schema_table[(schema, table)], key=lambda r: r["column_name"])
        row_count = cols[0]["row_count"] if cols else 0
        rows_html = []
        for p in cols:
            col = p["column_name"]
            ctype = escape(p["column_type"])
            desc_key = (layer, table, col)
            desc = descs.get(desc_key, "")
            desc_html = f'<div class="col-desc">{escape(desc)}</div>' if desc else ""
            facts = (
                f'rows <code>{p["row_count"]:,}</code> · '
                f'non-null <code>{p["non_null_count"]:,}</code> '
                f'({100 - (p["null_pct"] or 0):.1f}%) · '
                f'distinct <code>{p["distinct_count"]:,}</code>'
            )
            shape = format_shape(p)
            top5 = format_top5(p["top_5_values"])
            rows_html.append(f"""
              <tr>
                <td class="col-name">
                  <div class="col-name-name">{escape(col)}</div>
                  <div class="col-type">{ctype}</div>
                </td>
                <td class="col-body">
                  {desc_html}
                  <div class="col-facts">{facts}</div>
                  {f'<div class="col-shape">{shape}</div>' if shape else ''}
                  {top5}
                </td>
              </tr>
            """)
            if last_profiled is None or p["profiled_at"] > last_profiled:
                last_profiled = p["profiled_at"]

        sections.append(f"""
          <section class="table-section">
            <h2 class="table-name"><span class="table-schema">{escape(schema)}.</span>{escape(table)}</h2>
            <div class="table-meta">{row_count:,} rows · {len(cols)} columns</div>
            <table class="cols">
              <colgroup><col class="col-name-col"><col></colgroup>
              <tbody>{"".join(rows_html)}</tbody>
            </table>
          </section>
        """)

    profiled_label = (
        last_profiled.strftime("%Y-%m-%d %H:%M UTC") if last_profiled else "—"
    )
    body = "\n".join(sections)
    total_cols = sum(len(v) for v in by_schema_table.values())
    table_count = len(by_schema_table)
    return HTML_TEMPLATE.format(
        body=body,
        profiled_label=profiled_label,
        total_cols=total_cols,
        table_count=table_count,
    )


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Column profiles — Somerville 311</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  @font-face {{ font-family: 'DM Serif Display'; src: url('/fonts/DMSerifDisplay-Regular.woff2') format('woff2'); font-weight: 400; }}
  @font-face {{ font-family: 'DM Mono';          src: url('/fonts/DMMono-Regular.woff2')          format('woff2'); font-weight: 400; }}
  @font-face {{ font-family: 'Instrument Sans';  src: url('/fonts/InstrumentSans-Regular.woff2')  format('woff2'); font-weight: 400; }}
  @font-face {{ font-family: 'Instrument Sans';  src: url('/fonts/InstrumentSans-Medium.woff2')   format('woff2'); font-weight: 500; }}

  :root {{
    --bg: #f7f6f2;
    --bg-card: #ffffff;
    --text: #1a1a1a;
    --text-mid: #4a4a4a;
    --text-muted: #8a8a8a;
    --green: #2c5f2d;
    --green-pale: #e8f0eb;
    --border: #e3e1dc;
  }}

  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: 'Instrument Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
  }}
  a {{ color: var(--text-mid); }}
  a:hover {{ color: var(--text); }}
  code {{
    font-family: 'DM Mono', monospace;
    background: var(--bg); border: 1px solid var(--border);
    padding: 1px 5px; border-radius: 3px; font-size: 12px;
  }}

  .nav {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 40px; border-bottom: 1px solid var(--border);
  }}
  .nav-brand {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 18px; letter-spacing: 0.01em;
  }}
  .nav-links a {{ font-size: 14px; margin-left: 24px; text-decoration: none; }}

  .hero {{ padding: 56px 40px 28px; max-width: 880px; }}
  .hero-label {{
    font-family: 'DM Mono', monospace;
    font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--green); display: inline-block; padding-bottom: 6px;
  }}
  .hero h1 {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 46px; line-height: 1.05; margin: 6px 0 12px;
  }}
  .hero p {{ color: var(--text-mid); font-size: 16px; max-width: 620px; }}
  .hero .count {{
    font-family: 'DM Mono', monospace; font-size: 13px;
    color: var(--text-muted); margin-top: 12px;
  }}

  main {{ padding: 12px 40px 80px; max-width: 1400px; }}

  .table-section {{
    background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px;
    padding: 22px 26px; margin-bottom: 24px;
  }}
  .table-name {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 26px; margin: 0;
  }}
  .table-schema {{
    font-family: 'DM Mono', monospace; font-size: 14px;
    color: var(--text-muted); font-weight: normal;
  }}
  .table-meta {{
    font-family: 'DM Mono', monospace; font-size: 12px;
    color: var(--text-muted); margin: 4px 0 18px;
  }}

  table.cols {{ border-collapse: collapse; width: 100%; }}
  table.cols .col-name-col {{ width: 240px; }}
  table.cols td {{
    border-top: 1px solid var(--border);
    padding: 14px 4px; vertical-align: top;
  }}
  table.cols tr:first-child td {{ border-top: 0; }}

  .col-name-name {{
    font-family: 'DM Mono', monospace; font-size: 14px;
    color: var(--text); padding-right: 16px; word-break: break-all;
  }}
  .col-type {{
    font-family: 'DM Mono', monospace; font-size: 11px;
    color: var(--green); letter-spacing: 0.04em; margin-top: 3px;
  }}

  .col-desc {{ color: var(--text-mid); font-size: 14px; margin-bottom: 8px; }}
  .col-facts {{
    font-family: 'DM Mono', monospace; font-size: 12px;
    color: var(--text-muted); margin-bottom: 4px;
  }}
  .col-shape {{
    font-family: 'DM Mono', monospace; font-size: 12px;
    color: var(--text-mid); margin-top: 4px;
  }}

  ul.top5 {{
    list-style: none; padding: 0; margin: 8px 0 0;
    display: flex; flex-wrap: wrap; gap: 6px 14px;
  }}
  ul.top5 li {{
    font-family: 'DM Mono', monospace; font-size: 12px;
  }}
  ul.top5 .muted {{ color: var(--text-muted); }}
</style>
</head>
<body>
  <nav class="nav">
    <div class="nav-brand">Somerville 311</div>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/docs/">Docs</a>
      <a href="/erd">Schema</a>
      <a href="/metrics">Metrics</a>
      <a href="/profile">Profiles</a>
      <a href="/trust">Trust</a>
    </div>
  </nav>

  <header class="hero">
    <span class="hero-label">Column profiles</span>
    <h1>What's in each column.</h1>
    <p>Auto-generated shape data for every bronze and gold column: row counts,
    distinct counts, null percentages, value distributions, top-5 values.
    Hand-written descriptions live in dbt's <a href="/docs/">data dictionary</a>;
    this page is the observational counterpart.</p>
    <div class="count">{total_cols} columns across {table_count} tables · last profiled {profiled_label}</div>
  </header>

  <main>
    {body}
  </main>
</body>
</html>
"""


def main() -> int:
    descs = load_descriptions()
    profiles = load_profiles()
    if not profiles:
        print("  no rows in fct_column_profile_raw — run profile_tables.py first", file=sys.stderr)
        return 1
    html = render(descs, profiles)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"  wrote {OUT_PATH} ({len(profiles)} columns)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
