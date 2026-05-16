#!/usr/bin/env python3
"""Assemble portal/erd.html from the Mermaid sources.

Renders, top to bottom:
  - Tier flowchart (from portal/erd-warehouse.mmd) — structure + flow
  - Per-tier erDiagrams (from portal/erd-tier-{bronze,gold,admin}.mmd) —
    column-level detail, one per tier. Silver renders as an HTML
    placeholder until MVP 3's survey-curation plan lands the first
    silver model.
  - Semantic-layer diagram (from portal/erd-semantic-layer.mmd)

Uses the official Mermaid CDN (jsdelivr) for client-side rendering. The
.mmd files are committed alongside the HTML so they can be inspected or
re-rendered offline.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

# Local import: scripts/_nav.py is the shared nav source.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nav import nav_html, NAV_CSS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH       = REPO_ROOT / "portal" / "erd.html"
WAREHOUSE_MMD  = REPO_ROOT / "portal" / "erd-warehouse.mmd"
SEMANTIC_MMD   = REPO_ROOT / "portal" / "erd-semantic-layer.mmd"

# Per-tier erDiagram inputs. Missing file => empty tier (placeholder rendered).
TIER_MMD = {
    "bronze": REPO_ROOT / "portal" / "erd-tier-bronze.mmd",
    "silver": REPO_ROOT / "portal" / "erd-tier-silver.mmd",
    "gold":   REPO_ROOT / "portal" / "erd-tier-gold.mmd",
    "admin":  REPO_ROOT / "portal" / "erd-tier-admin.mmd",
}

# Tier metadata for headings, captions, accent colors.
TIER_META = {
    "bronze": {
        "label": "Bronze",
        "subtitle": "Source mirrors — raw, untransformed feeds",
        "accent": "#a07028",
        "fill":   "#efe0c8",
        "text":   "#3d2806",
        "caption": "Each table mirrors a Socrata source one-to-one. "
                   "dlt owns the merge; dbt only passes the bronze view through. "
                   "Audit columns (<code>_extracted_at</code>, <code>_dlt_id</code>, …) "
                   "are omitted from this diagram — they're on /docs/ and /profile.",
    },
    "silver": {
        "label": "Silver",
        "subtitle": "Curated derivations — coming with MVP 3",
        "accent": "#888888",
        "fill":   "#e8e8e8",
        "text":   "#333333",
        "caption": "The Silver tier is structurally present but holds "
                   "no tables yet. Plan 24 (MVP 3 — Happiness Survey "
                   "silver/gold curation) will land the first silver "
                   "model. The generator reads <code>dbt/models/silver/"
                   "schema.yml</code>, so a new silver model lands on "
                   "this diagram on the next <code>./run.sh</code>.",
    },
    "gold": {
        "label": "Gold",
        "subtitle": "Analyst-facing star schema — fct + dim tables",
        "accent": "#c19d3a",
        "fill":   "#fff4c8",
        "text":   "#5c4a0b",
        "caption": "Six fact tables (311 requests, crime, citations, "
                   "permits, KPI snapshots) and seven dimensions "
                   "(ward, date, request type, status, offense code + "
                   "category, KPI topic). FK arrows show fct → dim "
                   "joins. This is what the chat agent queries.",
    },
    "admin": {
        "label": "Admin",
        "subtitle": "Pipeline + data-quality observability",
        "accent": "#3a8fc1",
        "fill":   "#dceefc",
        "text":   "#0b3a5c",
        "caption": "Three observability tables: pipeline runs, data "
                   "quality test definitions, and test run results. "
                   "Powers /trust and the drift-fail guardrail in "
                   "<code>./run.sh</code>.",
    },
}


def tier_section_html(tier: str, mmd_content: str | None) -> str:
    meta = TIER_META[tier]
    badge_style = (
        f"display:inline-block;width:10px;height:10px;border-radius:50%;"
        f"background:{meta['fill']};border:1px solid {meta['accent']};"
        f"margin-right:8px;vertical-align:middle;"
    )
    header = (
        f'<h2 class="tier-heading"><span class="tier-badge" '
        f'style="{badge_style}"></span>{meta["label"]} — '
        f'<span class="tier-subtitle">{meta["subtitle"]}</span></h2>'
    )
    caption = f'<p class="lede">{meta["caption"]}</p>'

    if mmd_content:
        body = f'<pre class="mermaid">\n{mmd_content}\n      </pre>'
    else:
        # Empty-tier placeholder. Styled to match the tier's accent so it
        # reads as intentional rather than broken, with a dashed border
        # echoing the flowchart's Silver placeholder.
        body = (
            f'<div class="tier-empty" style="'
            f'border:1px dashed {meta["accent"]};'
            f'background:{meta["fill"]};'
            f'color:{meta["text"]};'
            f'padding:32px 24px;text-align:center;border-radius:4px;'
            f'font-family:\'DM Mono\', monospace;font-size:13px;'
            f'">(no tables yet — the Silver tier lands with MVP 3 '
            f'survey curation)</div>'
        )

    return (
        '<section class="diagram tier-section">'
        f'{header}{caption}{body}'
        '</section>'
    )


HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Schema — Somerville 311</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  // useMaxWidth: false on both er + flowchart so the SVG renders at its
  // natural size and .mermaid's overflow-x:auto becomes the active scroll
  // surface. The warehouse erDiagram is ~2365px wide -- with useMaxWidth
  // true (Mermaid 10 default) it scaled down to fit container, making
  // text microscopic at any viewport. See Plan B-revisited investigation.
  mermaid.initialize({{
    startOnLoad: true,
    theme: 'neutral',
    flowchart: {{ useMaxWidth: false }},
    er:        {{ useMaxWidth: false }}
  }});
</script>
<style>
  @font-face {{ font-family: 'DM Serif Display'; src: url('/fonts/DMSerifDisplay-Regular.woff2') format('woff2'); font-weight: 400; }}
  @font-face {{ font-family: 'DM Mono';          src: url('/fonts/DMMono-Regular.woff2')          format('woff2'); font-weight: 400; }}
  @font-face {{ font-family: 'Instrument Sans';  src: url('/fonts/InstrumentSans-Regular.woff2')  format('woff2'); font-weight: 400; }}
  @font-face {{ font-family: 'Instrument Sans';  src: url('/fonts/InstrumentSans-Medium.woff2')   format('woff2'); font-weight: 500; }}

  :root {{
    --bg:        #f7f6f2;
    --bg-card:   #ffffff;
    --text:      #1a1a1a;
    --text-mid:  #4a4a4a;
    --text-muted:#8a8a8a;
    --green:     #2c5f2d;
    --green-pale:#e8f0eb;
    --border:    #e3e1dc;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: 'Instrument Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.5;
  }}
  a {{ color: var(--text-mid); }}
  a:hover {{ color: var(--text); }}

{NAV_CSS}

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

  section.diagram {{
    background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px;
    padding: 22px 26px; margin-bottom: 28px;
  }}
  section.diagram h2 {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 26px; margin: 0 0 6px;
  }}
  section.diagram p.lede {{
    color: var(--text-mid); font-size: 15px; margin: 0 0 18px; max-width: 720px;
  }}

  /* Per-tier section accents */
  section.tier-section h2.tier-heading {{
    font-size: 22px; margin: 0 0 8px;
  }}
  section.tier-section .tier-subtitle {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 14px; color: var(--text-muted);
    font-weight: 400; letter-spacing: 0;
  }}

  /* Tier-detail divider — sits before the Bronze section to signal
     the altitude shift from "flow overview" to "column-level detail". */
  .tier-detail-divider {{
    display: flex; align-items: center; gap: 14px;
    margin: 8px 0 22px;
  }}
  .tier-detail-divider::before, .tier-detail-divider::after {{
    content: ""; flex: 1; height: 1px; background: var(--border);
  }}
  .tier-detail-divider span {{
    font-family: 'DM Mono', monospace; font-size: 11px;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text-muted);
  }}

  .mermaid {{
    background: #fafafa;
    border: 1px solid var(--border); border-radius: 4px;
    padding: 18px; margin: 0; overflow-x: auto;
  }}

  footer {{
    padding: 24px 40px 60px; color: var(--text-muted); font-size: 12px;
    font-family: 'DM Mono', monospace;
  }}
</style>
</head>
<body>
  {nav_block}

  <header class="hero">
    <span class="hero-label">Warehouse &amp; semantic layer</span>
    <h1>How the data is shaped.</h1>
    <p>The analyst's chat agent reads two layers: a relational warehouse
    of bronze + gold tables (medallion architecture) and a semantic layer
    of views and topics on top. Analysts don't query tables directly —
    they ask the agent. These diagrams document the structure the agent
    has access to.</p>
  </header>

  <main>
    <section class="diagram">
      <h2>Warehouse tables</h2>
      <p class="lede">Tables grouped by medallion tier:
      <strong>bronze</strong> mirrors the source,
      <strong>silver</strong> (coming with MVP 3) will hold curated
      derivations, <strong>gold</strong> is analyst-facing, and
      <strong>admin</strong> carries pipeline + data-quality
      observability. The dotted "dbt" arrows indicate the medallion
      flow conceptually; solid arrows are foreign-key relationships
      between tables. Column-level details live in the
      <a href="/docs/">data dictionary</a>; column-level shape lives
      on <a href="/profile">/profile</a>.</p>
      <pre class="mermaid">
{warehouse_mermaid}
      </pre>
    </section>

    <div class="tier-detail-divider">
      <span>Column-level detail by tier</span>
    </div>

{tier_sections}

    <section class="diagram">
      <h2>Semantic layer</h2>
      <p class="lede">Each view in the diagram maps to a
      <code>.view.yml</code> file in <code>semantics/views/</code>; each
      topic groups views in <code>semantics/topics/</code>. Views are the
      contract surface for the chat agent — what it knows about the data,
      including the measures it can compute. Measure definitions live on
      <a href="/metrics">/metrics</a>.</p>
      <pre class="mermaid">
{semantic_mermaid}
      </pre>
    </section>
  </main>

  <footer>generated {generated_at}</footer>
</body>
</html>
"""


def main() -> int:
    if not WAREHOUSE_MMD.exists():
        print(f"ERROR: missing {WAREHOUSE_MMD}", file=sys.stderr)
        return 1
    if not SEMANTIC_MMD.exists():
        print(f"ERROR: missing {SEMANTIC_MMD}", file=sys.stderr)
        return 1

    warehouse = WAREHOUSE_MMD.read_text(encoding="utf-8")
    semantic = SEMANTIC_MMD.read_text(encoding="utf-8")
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Build the per-tier sections in medallion order.
    tier_section_blocks: list[str] = []
    for tier in ("bronze", "silver", "gold", "admin"):
        mmd_path = TIER_MMD[tier]
        if mmd_path.exists():
            mmd_content = mmd_path.read_text(encoding="utf-8")
        else:
            mmd_content = None
        tier_section_blocks.append(tier_section_html(tier, mmd_content))
    tier_sections = "\n    ".join(tier_section_blocks)

    html = HTML.format(
        warehouse_mermaid=warehouse,
        semantic_mermaid=semantic,
        tier_sections=tier_sections,
        generated_at=generated,
        NAV_CSS=NAV_CSS,
        nav_block=nav_html(active="erd"),
    )

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"  wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
