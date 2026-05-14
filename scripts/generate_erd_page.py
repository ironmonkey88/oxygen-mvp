#!/usr/bin/env python3
"""Assemble portal/erd.html from the two Mermaid sources.

Renders:
  - Warehouse ERD (from portal/erd-warehouse.mmd)
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
      <p class="lede">Bronze mirrors the source, gold is business-ready,
      admin is data-quality + pipeline observability. Column-level details
      live in the <a href="/docs/">data dictionary</a>; column-level shape
      lives on <a href="/profile">/profile</a>. Audit columns
      (<code>_extracted_at</code>, <code>_first_seen_at</code>, etc.)
      are omitted here for legibility.</p>
      <pre class="mermaid">
{warehouse_mermaid}
      </pre>
    </section>

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

    html = HTML.format(
        warehouse_mermaid=warehouse,
        semantic_mermaid=semantic,
        generated_at=generated,
        NAV_CSS=NAV_CSS,
        nav_block=nav_html(active="erd"),
    )

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"  wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
