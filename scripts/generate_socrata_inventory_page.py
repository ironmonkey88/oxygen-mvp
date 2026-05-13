"""Read main_admin.fct_socrata_catalog_raw and write docs/socrata-inventory.md.

Renders the latest cataloged_at run only. Groups by domain_category, sorts within
group by row_count desc (nulls last). Annotations are written into the template
below — Code's judgment on "why this might matter."
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import duckdb

DB_PATH = os.environ.get("DUCKDB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "somerville.duckdb"))
OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "socrata-inventory.md"
TABLE = "main_admin.fct_socrata_catalog_raw"

# Per-dataset annotations: Code's judgment on relevance to the project.
# Keys are 4x4 dataset_ids. Anything not annotated gets "(unannotated — see description)".
ANNOTATIONS: dict[str, str] = {
    # Public Safety (load-bearing for crime + Plan 12)
    "aghs-hqvg": "Crime incidents 2017–present, ward + block_code geo, daily refresh with 1-mo delay. Sensitive incidents stripped of time/location at source. **Plan 12 Phase 3 target.**",
    "mtik-28va": "Vehicle crash records from SPD. Smaller than Crime Reports (3K rows). Useful as supplemental safety/equity context.",
    "3mqx-eye9": "Traffic citations issued. 67K rows. Useful for enforcement-equity questions (do citations cluster by ward?).",
    "mdb2-mgc7": "Calls for service / dispatch records. 336K rows — broadest police feed. Heavier ingestion; potential MVP 3+ candidate when crime-by-equity scope expands.",
    "ezmv-8wys": "Motor vehicle crashes 2010–2018. Historical only; no recent updates. Less useful unless asking historical questions.",

    # Service requests (311 already ingested)
    "4pyi-uqq6": "**Already ingested.** Source for `main_bronze.raw_311_requests_raw`. The MVP's primary fact table.",

    # Permits & development
    "vxgw-vmky": "Building/zoning permits. 64K rows. Useful for development-pressure analysis joined to 311 (construction-related complaints vs. permit activity).",
    "nneb-s3f7": "Permit applications (pre-approval). 100K rows. Complements the Permits dataset.",

    # Geospatial reference (all blob on Socrata)
    "ym5n-phxd": "Ward polygons. **Plan 12 Phase 2 target** — blob-only on Socrata, downloadable; format check pending. Unlocks ward-level mapping + portal hero TODO.",
    "n5md-vqta": "Neighborhood polygons. Higher-resolution than wards. MVP 3 candidate for `dim_location`.",
    "pz4k-wh6e": "City boundary polygon. One row. Useful for clipping spatial joins to Somerville.",
    "da4y-vuae": "Voting precinct polygons. Finer-grained than wards. Plan 12+ candidate.",
    "7jtq-qmnf": "Street centerlines. Useful for routing / proximity questions; lower priority than wards.",
    "uzdd-gyjv": "Building footprints. Spatial polygons. Useful for property-grain analysis later.",
    "crrw-ex2a": "Zoning & overlay districts. Spatial. Pairs with Permits for development-pressure analysis.",
    "9i64-4hby": "Open space (parks etc) polygons. Useful for accessibility + service-equity questions.",
    "gw4w-w7cw": "Tax parcel polygons. Finest-grained property data. MVP 3+ candidate; PII-adjacent (owner names may appear).",
    "yswj-3fdd": "Impervious surfaces polygons. Useful for stormwater + climate questions.",
    "i28f-q9cg": "1-ft contour lines. Specialized GIS. Low priority for analyst questions.",
    "5ebe-mbbc": "2015 aerial imagery (large file). Not analyst-queryable.",
    "9yqy-rex4": "Police station locations.",
    "vjwd-26r7": "Fire station locations.",
    "hm5m-dtda": "Fire response district polygons.",
    "jich-f4v9": "Parking meter locations.",
    "bpsf-vg2d": "Trash receptacle locations.",
    "y6ii-trws": "Place names (POI). Reference layer.",
    "9xw5-tezf": "Polling place locations.",

    # Transportation / mobility
    "qu9x-4xq5": "Bicycle & pedestrian counts. 2.5K rows. Useful for active-transport equity questions.",
    "xavb-4s9w": "Parking permits issued. 288K rows. Useful for car-ownership + ward-level questions.",

    # Surveys & feedback (analyst-relevant if survey topics align)
    "wmeh-zuz2": "Happiness Survey responses. 12K rows. Multi-year, cross-cutting community sentiment.",
    "9a8v-ve6k": "Public Safety community survey. Pairs with crime data for perception-vs-reality analysis.",
    "vamq-kd64": "Open Space & Recreation Plan survey. Pairs with parks/open-space spatial layer.",
    "usj9-kz3f": "ADA accessibility community survey. Small (635 rows); pairs with sidewalk-related 311 categories.",
    "scm7-xh8d": "Citizenserve applicant feedback 2023. Permit-experience feedback. Very small.",
    "6x35-pz53": "2015 Solar Survey responses. Historical, narrow scope.",
    "brzm-dycd": "Parks & Rec program feedback. Small (448 rows).",
    "qc8i-5r57": "School Building Project community feedback. Small narrow scope.",
    "e7ix-nqn6": "Winter Warming Center 2024/25 feedback. Small.",
    "hpdk-b2g6": "Afterschool needs assessment. Small.",

    # Participatory budgeting (small datasets)
    "52dh-yc6q": "PB demographic submissions. 26 rows. Demographic-equity in PB process.",
    "2tt6-zua8": "PB voting results. 20 rows.",
    "pdjd-r9yq": "PB voter demographics. 3K rows.",
    "brrj-v9a4": "PB submissions. 966 rows.",

    # Administrative / reference
    "jnde-mi6j": "Somerville at a Glance — KPI snapshot dataset.",
    "wz6k-gm5k": "Capital Investment Plan FY16–26. 58 rows. Useful for spending-vs-need ward analysis.",
    "pm7h-ga9w": "Annual jobs count. 22 rows. Macro indicator.",
    "qsv6-v7hu": "School staff MBTA pass pilot. 16 rows. Narrow.",
    "754v-8e35": "Website analytics. 23K rows of page-view data. Operational; low analyst priority.",

    # Test / noise
    "7f7a-jts5": "**Test dataset.** Noise. Skip.",
}

# Top recommendations after wards + crime, ordered.
TOP_RECOMMENDATIONS = [
    {
        "dataset_id": "vxgw-vmky",
        "title": "Permits",
        "why": (
            "Joins cleanly to 311 by ward + date_created. Lets the analyst answer "
            "'are construction-related 311 complaints rising where permit activity "
            "concentrates?' — a development-pressure question that's first on city "
            "planners' minds. 64K rows, tabular, well-documented columns. "
            "Pairs naturally with the wards + crime work for a planning-and-safety "
            "equity narrative."
        ),
    },
    {
        "dataset_id": "mdb2-mgc7",
        "title": "Police Data: Computer Aided Dispatch (CAD)",
        "why": (
            "336K rows of calls-for-service — broader than Crime Reports (which only "
            "logs incidents that became reports). CAD captures the full demand on "
            "police resources. Adding this after Crime Reports lets the analyst "
            "separate 'incidents reported' from 'calls placed,' which is the right "
            "frame for service-equity questions about police response."
        ),
    },
    {
        "dataset_id": "wmeh-zuz2",
        "title": "Somerville Happiness Survey Responses",
        "why": (
            "12K rows over multiple years of community sentiment. The closest "
            "Somerville comes to a perception-of-services signal that complements "
            "the operational 311/crime data. Pairs with the survey columns already "
            "in 311 (`accuracy`, `courtesy`, `ease`, `overallexperience`) for a "
            "richer sentiment-vs-operations comparison."
        ),
    },
    {
        "dataset_id": "qu9x-4xq5",
        "title": "Bicycle & Pedestrian Counts",
        "why": (
            "2.5K rows. Active-transport observation data. Pairs with crash/citation "
            "data for safety-equity analysis (where are pedestrians being counted vs. "
            "where are they being struck?). Smaller than the candidates above; "
            "include if Gordon wants 4 instead of 3."
        ),
    },
    {
        "dataset_id": "n5md-vqta",
        "title": "Neighborhoods",
        "why": (
            "Higher-resolution geospatial than wards. Blob on Socrata (same shape as "
            "wards); ingestion uses the same pattern as Plan 12 Phase 2. The clean "
            "neighborhood dimension is a Plan 11 carry-forward question (deferred to "
            "MVP 3 by default); landing this overnight would move the answer forward."
        ),
    },
]


def render(con: duckdb.DuckDBPyConnection) -> str:
    latest = con.execute(
        f"SELECT MAX(cataloged_at) FROM {TABLE}"
    ).fetchone()[0]
    total = con.execute(
        f"SELECT COUNT(*) FROM {TABLE} WHERE cataloged_at = ?", [latest]
    ).fetchone()[0]
    tabular = con.execute(
        f"SELECT COUNT(*) FROM {TABLE} WHERE cataloged_at = ? AND is_tabular", [latest]
    ).fetchone()[0]
    blob = total - tabular

    rows = con.execute(
        f"""
        SELECT
          dataset_id, title, description, attribution, resource_type,
          lens_view_type, is_tabular, blob_mime_type, domain_category,
          domain_tags, column_count, column_names, column_types,
          row_count, row_count_method, row_count_error,
          created_at, updated_at, data_updated_at,
          permalink, resource_endpoint, page_views_total, download_count
        FROM {TABLE}
        WHERE cataloged_at = ?
        ORDER BY
          COALESCE(domain_category, 'Uncategorized'),
          is_tabular DESC,
          row_count DESC NULLS LAST,
          title
        """,
        [latest],
    ).fetchall()

    col_idx = {
        "dataset_id": 0, "title": 1, "description": 2, "attribution": 3, "resource_type": 4,
        "lens_view_type": 5, "is_tabular": 6, "blob_mime_type": 7, "domain_category": 8,
        "domain_tags": 9, "column_count": 10, "column_names": 11, "column_types": 12,
        "row_count": 13, "row_count_method": 14, "row_count_error": 15,
        "created_at": 16, "updated_at": 17, "data_updated_at": 18,
        "permalink": 19, "resource_endpoint": 20, "page_views_total": 21, "download_count": 22,
    }

    out: list[str] = []
    out.append("# Socrata Inventory — Somerville Open Data\n")
    out.append(f"Auto-generated from `main_admin.fct_socrata_catalog_raw` at "
               f"{latest.isoformat()}. Source: "
               f"[`scripts/generate_socrata_inventory_page.py`](../scripts/generate_socrata_inventory_page.py). "
               f"Refresh with `.venv/bin/python scripts/build_socrata_inventory.py` "
               f"then re-run the generator.\n")
    out.append(f"**Summary.** {total} datasets total on `data.somervillema.gov`. "
               f"**{tabular} tabular** (SODA-queryable), **{blob} blob** "
               f"(map/file/filter — not SODA-queryable, but most are downloadable as "
               f"shapefile / geojson / image).\n")

    # Triage: top-3-plus recommendations
    out.append("## Triage — recommended next ingestions after wards + crime\n")
    out.append("Code's judgment, ranked. Gordon decides.\n")
    for i, rec in enumerate(TOP_RECOMMENDATIONS, 1):
        out.append(f"### {i}. `{rec['dataset_id']}` — {rec['title']}\n")
        out.append(f"{rec['why']}\n")

    out.append("---\n")
    out.append("## Full catalog by category\n")

    # Group by domain_category
    grouped: dict[str, list[tuple]] = {}
    for r in rows:
        cat = r[col_idx["domain_category"]] or "Uncategorized"
        grouped.setdefault(cat, []).append(r)

    for cat in sorted(grouped.keys()):
        cat_rows = grouped[cat]
        out.append(f"### {cat} ({len(cat_rows)} datasets)\n")
        for r in cat_rows:
            ds_id = r[col_idx["dataset_id"]]
            title = r[col_idx["title"]] or "(untitled)"
            is_tab = r[col_idx["is_tabular"]]
            row_count = r[col_idx["row_count"]]
            col_count = r[col_idx["column_count"]] or 0
            res_type = r[col_idx["resource_type"]]
            data_updated = r[col_idx["data_updated_at"]]
            permalink = r[col_idx["permalink"]]
            annotation = ANNOTATIONS.get(ds_id, "(unannotated — see description)")

            tab_marker = "**tabular**" if is_tab else f"*blob ({res_type})*"
            row_str = f"{row_count:,}" if row_count is not None else "—"
            updated_str = data_updated.isoformat() if data_updated else "—"

            out.append(f"#### [{title}]({permalink}) — `{ds_id}`\n")
            out.append(f"- **Shape:** {tab_marker} · {col_count} columns · {row_str} rows\n")
            out.append(f"- **Last updated:** {updated_str}\n")
            out.append(f"- **Why this might matter:** {annotation}\n")

    out.append("---\n")
    out.append("## Methodology\n")
    out.append("- **Source:** Socrata Discovery API at "
               f"`https://api.us.socrata.com/api/catalog/v1?domains=data.somervillema.gov` "
               "(paginated; one row per dataset).\n")
    out.append("- **Row counts:** Per-dataset SODA `count(*)` for tabular datasets; "
               "skipped for blob types (map/file/filter/etc — Socrata's "
               "Non-tabular datasets do not support rows requests).\n")
    out.append("- **Persistence:** `main_admin.fct_socrata_catalog_raw`, append-only "
               "with `cataloged_at`. Re-running the build script adds a fresh snapshot "
               "without clobbering history.\n")
    out.append("- **Annotations:** Hand-written `why this might matter` line per "
               "dataset, in `scripts/generate_socrata_inventory_page.py`. Update there "
               "as understanding evolves.\n")

    return "".join(out)


def main() -> int:
    con = duckdb.connect(DB_PATH, read_only=True)
    text = render(con)
    con.close()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(text)
    print(f"[wrote] {OUT_PATH} ({len(text):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
