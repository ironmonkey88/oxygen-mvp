#!/usr/bin/env python3
"""Generate the /dashboards listing from apps/*.app.yml.

Reads each `apps/*.app.yml`, extracts the `# === DASHBOARD METADATA ===`
comment block at the top (Plan 17 contract), and rewrites a
marker-bounded listing in `portal/dashboards.html` with one card
per app.

If an app has no metadata block, falls back to extracting `name:` +
first paragraph of `description:` -- but the canonical pattern is
that every `.app.yml` carries a metadata block.

The "Open in workspace" URL uses the base64-encoded full file path,
per the Session 42 fix to the SPA's `/apps/:pathb64` route contract.

Output: `portal/dashboards.html` (in-place between markers).
run.sh deploys to /var/www/somerville/dashboards.html.
"""
from __future__ import annotations

import base64
import re
from html import escape
from pathlib import Path

import yaml

# Local import: scripts/_nav.py is the shared nav source.
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nav import nav_html  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"
HTML_PATH = REPO_ROOT / "portal" / "dashboards.html"
SPA_BASE = "http://oxygen-mvp.taildee698.ts.net:3000"

_META_RE = re.compile(
    r"# === DASHBOARD METADATA.*?===\n(?P<body>.*?)# === END DASHBOARD METADATA ===",
    re.DOTALL,
)
_LISTING_RE = re.compile(
    r"<!-- BEGIN_DASHBOARDS_LISTING.*?-->.*?<!-- END_DASHBOARDS_LISTING -->",
    re.DOTALL,
)
_NAV_RE = re.compile(
    r"<!-- BEGIN_NAV.*?-->.*?<!-- END_NAV -->",
    re.DOTALL,
)


def parse_metadata_block(text: str) -> dict | None:
    """Extract and parse the # === DASHBOARD METADATA === comment block.

    Returns the parsed YAML dict, or None if no block is present.
    """
    m = _META_RE.search(text)
    if not m:
        return None
    body = m.group("body")
    # Strip leading "# " or "#" from each line
    yaml_lines = []
    for line in body.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("# "):
            yaml_lines.append(stripped[2:])
        elif stripped.startswith("#"):
            yaml_lines.append(stripped[1:].lstrip(" "))
        # Skip lines without # prefix (shouldn't happen inside the block)
    yaml_text = "\n".join(yaml_lines)
    try:
        return yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        print(f"  WARN: metadata block failed to parse as YAML: {e}")
        return None


def fallback_metadata(text: str, path: Path) -> dict:
    """If no metadata block, extract minimal fields from `name:` + `description:`."""
    # name:
    name_match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else path.stem
    title = name.replace("_", " ").title()
    # description: multi-line block scalar -- grab first paragraph
    desc_match = re.search(r"^description:\s*\|\n((?:[ \t]+.*\n)+)", text, re.MULTILINE)
    short_desc = ""
    if desc_match:
        # take first non-empty line of the block
        for line in desc_match.group(1).splitlines():
            line = line.strip()
            if line:
                short_desc = line
                break
    return {
        "title": title,
        "short_desc": short_desc,
        "source_tables": [],
        "limitations": [],
        "trust_signals": [],
        "coverage": "",
        "row_caption": "",
        "topic": "",
    }


def app_url(app_path: Path) -> str:
    """Compute the base64-encoded /apps/<pathb64> URL.

    Per the Session 42 fix: the SPA route /apps/:pathb64 expects the
    base64 of the full file path relative to repo root, e.g.
    apps/rat_complaints_by_ward.app.yml -> YXBwcy9yYXRfY29tcGxhaW50c19ieV93YXJkLmFwcC55bWw=
    """
    rel_path = app_path.relative_to(REPO_ROOT).as_posix()
    encoded = base64.b64encode(rel_path.encode()).decode()
    return f"{SPA_BASE}/apps/{encoded}"


def render_card(meta: dict, rel_path: str, url: str) -> str:
    title = meta.get("title") or rel_path
    short_desc = meta.get("short_desc") or ""
    row_caption = meta.get("row_caption") or ""
    coverage = meta.get("coverage") or ""
    topic = meta.get("topic") or ""
    source_tables = meta.get("source_tables") or []
    limitations = meta.get("limitations") or []
    trust_signals = meta.get("trust_signals") or []

    meta_spans = []
    if row_caption:
        meta_spans.append(
            f'<span><strong>Rows:</strong> {escape(str(row_caption))}</span>'
        )
    if coverage:
        meta_spans.append(
            f'<span><strong>Coverage:</strong> {escape(str(coverage))}</span>'
        )
    if topic:
        meta_spans.append(
            f'<span><strong>Topic:</strong> <code>{escape(str(topic))}</code></span>'
        )
    if source_tables:
        first = source_tables[0]
        more = f' +{len(source_tables) - 1}' if len(source_tables) > 1 else ''
        meta_spans.append(
            f'<span><strong>Source:</strong> <code>{escape(str(first))}</code>{escape(more)}</span>'
        )
    if trust_signals:
        trust_html = " &middot; ".join(escape(str(s)) for s in trust_signals)
        meta_spans.append(
            f'<span><strong>Trust:</strong> {trust_html}</span>'
        )

    meta_block = '\n          '.join(meta_spans) if meta_spans else ''

    limits_html = ''
    if limitations:
        limit_links = ', '.join(
            f'<code>{escape(str(l))}</code>' for l in limitations
        )
        limits_html = (
            f'\n        <div class="dash-card-limits">'
            f'<strong>Limitations:</strong> {limit_links} '
            f'&mdash; see <a href="/trust">/trust</a></div>'
        )

    return f"""      <div class="dash-card">
        <div class="dash-card-head">
          <div class="dash-card-title">{escape(title)}</div>
          <div class="dash-card-id">{escape(rel_path)}</div>
        </div>
        <div class="dash-card-desc">{escape(short_desc)}</div>
        <div class="dash-card-meta">
          {meta_block}
        </div>{limits_html}
        <a href="{escape(url)}" class="dash-card-link">Open in workspace &rarr;</a>
      </div>"""


def main() -> None:
    if not HTML_PATH.exists():
        raise SystemExit(f"HTML file missing: {HTML_PATH}")

    apps = sorted(APPS_DIR.glob("*.app.yml"))
    if not apps:
        print("WARNING: no apps/*.app.yml found")

    cards = []
    for app_path in apps:
        text = app_path.read_text()
        meta = parse_metadata_block(text)
        if meta is None:
            print(f"  {app_path.name}: no metadata block, using fallback extraction")
            meta = fallback_metadata(text, app_path)
        else:
            print(f"  {app_path.name}: parsed metadata ({meta.get('title','?')})")
        rel_path = app_path.relative_to(REPO_ROOT).as_posix()
        url = app_url(app_path)
        cards.append(render_card(meta, rel_path, url))

    if cards:
        listing = "\n".join(cards)
    else:
        listing = (
            '      <div class="dash-empty">No dashboards yet. '
            'See <a href="/docs">/docs</a> for the data dictionary.</div>'
        )

    listing_html = (
        "<!-- BEGIN_DASHBOARDS_LISTING (generated by "
        "scripts/generate_dashboards_listing.py) -->\n"
        '    <div class="dash">\n'
        f"{listing}\n"
        "    </div>\n"
        "    <!-- END_DASHBOARDS_LISTING -->"
    )

    nav_block = (
        "<!-- BEGIN_NAV (rewritten by scripts/generate_dashboards_listing.py "
        "from scripts/_nav.py) -->\n  "
        + nav_html(active="dashboards")
        + "\n  <!-- END_NAV -->"
    )

    html = HTML_PATH.read_text()
    new_html, subs = _LISTING_RE.subn(listing_html, html)
    if subs != 1:
        raise SystemExit(
            f"Expected exactly 1 BEGIN_DASHBOARDS_LISTING block, found {subs}. "
            "Run with --init to add markers to portal/dashboards.html."
        )
    new_html, nav_subs = _NAV_RE.subn(nav_block, new_html)
    if nav_subs != 1:
        raise SystemExit(
            f"Expected exactly 1 BEGIN_NAV block, found {nav_subs}"
        )
    HTML_PATH.write_text(new_html)
    print(f"refreshed {HTML_PATH.relative_to(REPO_ROOT)} with {len(cards)} dashboards + nav")


if __name__ == "__main__":
    main()
