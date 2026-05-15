#!/usr/bin/env python3
"""Generate a stylized SVG of Somerville's 7 wards for portal background use.

Reads `main_gold.dim_ward.geometry_wkt_wgs84` (Plan 12 Phase 2), parses
the WKT polygons, projects to SVG coordinates, and writes a static
SVG file. Wards rarely change (redistricting only), so this is a
once-off generator -- not wired into `run.sh`. Re-run manually if
ward geometry changes.

Output: `portal/assets/somerville-wards-background.svg`
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "somerville.duckdb"
OUT_PATH = REPO_ROOT / "portal" / "somerville-wards-background.svg"

SVG_WIDTH = 1600
SVG_HEIGHT = 1000


def parse_wkt_polygons(wkt: str) -> list[list[tuple[float, float]]]:
    """Parse WKT POLYGON or MULTIPOLYGON into a list of rings.

    Each ring is a list of (lng, lat) tuples. For MULTIPOLYGONs we
    return all outer rings; inner rings (holes) are dropped (wards
    don't have holes).
    """
    wkt = wkt.strip()
    if wkt.startswith("POLYGON"):
        bodies = [re.search(r"\(\((.*?)\)\)", wkt, re.DOTALL).group(1)]
    elif wkt.startswith("MULTIPOLYGON"):
        # MULTIPOLYGON (((ring1), (hole1)), ((ring2)), ...)
        # Pull each outermost ring; for the wards data we only have
        # single rings per polygon so this is simple.
        bodies = re.findall(r"\(\(([^()]+)\)\)", wkt, re.DOTALL)
    else:
        raise ValueError(f"Unknown WKT shape: {wkt[:50]}")

    rings = []
    for body in bodies:
        # body is "lng lat, lng lat, ..."
        pts = []
        for pair in body.split(","):
            parts = pair.strip().split()
            if len(parts) >= 2:
                pts.append((float(parts[0]), float(parts[1])))
        if pts:
            rings.append(pts)
    return rings


def project(lng: float, lat: float, bbox: tuple, ref_lat: float) -> tuple[float, float]:
    """Project (lng, lat) to SVG (x, y).

    Uses equirectangular projection with cosine correction at ref_lat
    for accurate aspect ratio. SVG y is inverted (grows downward).
    """
    min_lng, min_lat, max_lng, max_lat = bbox
    cos_ref = math.cos(math.radians(ref_lat))
    # Width in "projected degrees": lng range * cos(lat)
    proj_w = (max_lng - min_lng) * cos_ref
    proj_h = (max_lat - min_lat)
    aspect_data = proj_w / proj_h
    aspect_svg = SVG_WIDTH / SVG_HEIGHT
    # Fit data inside SVG, preserve aspect, centered
    if aspect_data > aspect_svg:
        # data wider than svg -> fit by width
        scale = SVG_WIDTH / proj_w
        offset_x = 0
        offset_y = (SVG_HEIGHT - proj_h * scale) / 2
    else:
        scale = SVG_HEIGHT / proj_h
        offset_x = (SVG_WIDTH - proj_w * scale) / 2
        offset_y = 0
    x = offset_x + (lng - min_lng) * cos_ref * scale
    # invert y
    y = offset_y + (max_lat - lat) * scale
    return x, y


def polygon_centroid(pts: list[tuple[float, float]]) -> tuple[float, float]:
    """Area-weighted centroid of a simple polygon via the shoelace formula.

    `pts` is a list of (x, y) tuples in any coordinate system. Polygon may
    or may not be explicitly closed; either form works.
    """
    if not pts:
        return 0.0, 0.0
    if pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    a2 = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        cross = x0 * y1 - x1 * y0
        a2 += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if a2 == 0:
        # Degenerate -- fall back to mean of vertices
        xs = [p[0] for p in pts[:-1]]
        ys = [p[1] for p in pts[:-1]]
        return sum(xs) / len(xs), sum(ys) / len(ys)
    return cx / (3 * a2), cy / (3 * a2)


def polygon_area(pts: list[tuple[float, float]]) -> float:
    """Absolute area of a simple polygon."""
    if len(pts) < 3:
        return 0.0
    if pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    a2 = 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        a2 += x0 * y1 - x1 * y0
    return abs(a2) / 2


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"DuckDB file missing: {DB_PATH}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(DB_PATH), read_only=True)
    rows = conn.execute("""
        SELECT ward, ward_name, geometry_wkt_wgs84
        FROM main_gold.dim_ward
        WHERE geometry_wkt_wgs84 IS NOT NULL
        ORDER BY ward
    """).fetchall()
    conn.close()

    if not rows:
        raise SystemExit("No ward geometries found in dim_ward")

    # Parse all polygons and compute bounding box
    all_polys = []
    min_lng = math.inf
    min_lat = math.inf
    max_lng = -math.inf
    max_lat = -math.inf
    for ward, ward_name, wkt in rows:
        rings = parse_wkt_polygons(wkt)
        all_polys.append((ward, ward_name, rings))
        for ring in rings:
            for lng, lat in ring:
                if lng < min_lng:
                    min_lng = lng
                if lat < min_lat:
                    min_lat = lat
                if lng > max_lng:
                    max_lng = lng
                if lat > max_lat:
                    max_lat = lat

    # Add tiny margin
    margin = 0.002
    bbox = (min_lng - margin, min_lat - margin,
            max_lng + margin, max_lat + margin)
    ref_lat = (min_lat + max_lat) / 2

    # Build SVG: polygons inside an opacity-0.7 group; ward labels in a
    # separate group at full opacity so they stay readable against the
    # background.
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" preserveAspectRatio="xMidYMid meet" '
        f'aria-hidden="true">',
        '  <title>Somerville wards (background)</title>',
        '  <g fill="#d5d2cb" stroke="#b0ab9f" stroke-width="2.5" '
        'stroke-linejoin="round" opacity="0.7">',
    ]
    label_positions: list[tuple[float, float, str]] = []
    for ward, ward_name, rings in all_polys:
        projected_rings: list[list[tuple[float, float]]] = []
        for ring in rings:
            pts: list[tuple[float, float]] = []
            pts_str: list[str] = []
            for lng, lat in ring:
                x, y = project(lng, lat, bbox, ref_lat)
                pts.append((x, y))
                pts_str.append(f"{x:.1f},{y:.1f}")
            parts.append(
                f'    <polygon points="{" ".join(pts_str)}" '
                f'data-ward="{ward}" data-ward-name="{ward_name}" />'
            )
            projected_rings.append(pts)
        if projected_rings:
            largest = max(projected_rings, key=polygon_area)
            cx, cy = polygon_centroid(largest)
            label_positions.append((cx, cy, ward))
    parts.append('  </g>')
    parts.append(
        '  <g font-family="Instrument Sans, -apple-system, sans-serif" '
        'font-size="22" font-weight="600" fill="#6a6a6a" '
        'text-anchor="middle" dominant-baseline="central" '
        'pointer-events="none">'
    )
    for cx, cy, ward in label_positions:
        parts.append(
            f'    <text x="{cx:.1f}" y="{cy:.1f}">Ward {ward}</text>'
        )
    parts.append('  </g>')
    parts.append('</svg>')
    svg = "\n".join(parts) + "\n"

    OUT_PATH.write_text(svg)
    print(f"wrote {OUT_PATH.relative_to(REPO_ROOT)} "
          f"({len(all_polys)} wards, bbox {bbox})")


if __name__ == "__main__":
    main()
