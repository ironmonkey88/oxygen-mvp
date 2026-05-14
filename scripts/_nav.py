"""Shared portal nav fragment.

One canonical source for the seven-link nav rendered across every static
portal surface. Imported by:

- scripts/generate_metrics_page.py     (active='metrics')
- scripts/generate_trust_page.py       (active='trust')
- scripts/generate_profile_page.py     (active='profile')
- scripts/generate_erd_page.py         (active='erd')
- scripts/generate_homepage_summary.py (active='home', rewrites portal/index.html)
- scripts/generate_dashboards_listing.py (active='dashboards', rewrites portal/dashboards.html)

The hand-written pages (portal/index.html, portal/dashboards.html) carry
BEGIN_NAV / END_NAV marker comments; the homepage + dashboards generators
replace the marker-bounded region on every pipeline run, the same way they
already refresh stats + dataset cards + the dashboards listing.

NAV_CSS is an optional CSS-string constant that generators which don't
yet share the homepage's stylesheet can inline. The hand-written pages
already define the same rules, so they don't include it (and shouldn't
duplicate).
"""
from __future__ import annotations

# Each tuple: (href, label, key). `key` is matched against the `active`
# arg in nav_html(). Order is fixed -- this is the visual order.
NAV_ITEMS: tuple[tuple[str, str, str], ...] = (
    ("/", "Home", "home"),
    ("/dashboards", "Dashboards", "dashboards"),
    ("/metrics", "Metrics", "metrics"),
    ("/trust", "Trust", "trust"),
    ("/profile", "Profiles", "profile"),
    ("/erd", "Schema", "erd"),
    ("/docs/", "Data dictionary", "docs"),
)


def nav_html(active: str = "") -> str:
    """Return the canonical <nav> block.

    `active` should be one of: "home", "dashboards", "metrics", "trust",
    "profile", "erd", "docs". If empty or unknown, no entry is marked
    active.
    """
    valid_keys = {item[2] for item in NAV_ITEMS}
    if active and active not in valid_keys:
        raise ValueError(
            f"nav_html: unknown active key {active!r}; "
            f"expected one of {sorted(valid_keys)}"
        )

    link_lines = []
    for href, label, key in NAV_ITEMS:
        if key == active:
            link_lines.append(
                f'      <span class="nav-current" aria-current="page">{label}</span>'
            )
        else:
            link_lines.append(f'      <a href="{href}">{label}</a>')
    links_block = "\n".join(link_lines)

    return (
        '<nav>\n'
        '    <div class="nav-brand">\n'
        '      Somerville Analytics\n'
        '      <span class="nav-badge">MVP 2</span>\n'
        '    </div>\n'
        '    <div class="nav-links">\n'
        f"{links_block}\n"
        '    </div>\n'
        '  </nav>'
    )


# Canonical CSS for the nav. The hand-written pages already define
# equivalent rules in their own <style> blocks. Generators that don't
# share the homepage's stylesheet should inline this verbatim.
NAV_CSS = """  /* Shared portal nav (scripts/_nav.py) */
  nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    height: 52px;
    background: var(--white, #ffffff);
    border-bottom: 1px solid var(--border, #e2dfd8);
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .nav-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: -0.2px;
  }
  .nav-badge {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--green, #1e4d2b);
    background: var(--green-pale, #e8f0eb);
    border: 1px solid #b8d4c0;
    padding: 2px 7px;
    border-radius: 4px;
  }
  .nav-links {
    display: flex;
    align-items: center;
    gap: 28px;
    font-size: 14px;
    color: var(--text-mid, #4a4a4a);
  }
  .nav-links a {
    text-decoration: none;
    color: inherit;
    transition: color .15s;
  }
  .nav-links a:hover { color: var(--text, #1a1a1a); }
  .nav-current {
    color: var(--green, #1e4d2b);
    font-weight: 600;
    cursor: default;
  }"""
