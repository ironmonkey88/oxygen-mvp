"""Somerville Traffic Citations ingestion pipeline (full-pull + merge on
`citationnum`).

Prompt 11 Phase C (2026-05-14). Adapted from
`dlt/somerville_crime_pipeline.py` -- same shape (full-pull, merge-on-PK,
DuckDB destination, audit columns) applied to Socrata dataset
`3mqx-eye9`.

Source: City of Somerville Police Department traffic citations,
2017-present. ~67K rows as of 2026-05-14. Refreshes daily from source
with a one-month publication delay (per the Socrata description). One
row per (citation, violation) -- `citationnum` carries a violation
suffix (e.g. "T2725339-1") so it serves as the unique merge key.

**PII surface (probed 2026-05-14): low.** No driver name, no license
number, no vehicle make/model. Sample rows carry just intersection
addresses + violation type + ward. See
docs/limitations/traffic-citations-location-and-violation-only.md for
the assessment.

Tables produced in `main_bronze`:
  - raw_somerville_traffic_citations_raw (dlt-owned, merge target)

Audit columns injected per row:
  - _extracted_at      TIMESTAMP   when this run extracted the row
  - _extracted_run_id  TEXT (ULID) which pipeline run produced this state
  - _source_endpoint   TEXT        SODA URL the row came from

`_first_seen_at` follows the 311 / crime pattern -- added via ALTER
TABLE after merge, populated only for rows where it's still NULL
(preserved across re-extractions).

Usage:
    python dlt/somerville_traffic_citations_pipeline.py [RUN_ID]
"""
import sys
from datetime import datetime, timezone
from typing import Iterator

import dlt
import duckdb
import requests
from ulid import ULID

SODA_BASE = "https://data.somervillema.gov/resource/3mqx-eye9.json"
PAGE_SIZE = 50_000  # source ~67K rows; 2 pages cover it
DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
SOURCE_ENDPOINT = SODA_BASE

# Source columns observed via SODA metadata 2026-05-14.
ALL_COLUMNS = ",".join([
    "citationnum",
    "dtissued",
    "police_shift",
    "address",
    "chgcode",
    "chgdesc",
    "chgcategory",
    "vehiclemph",
    "mphzone",
    "lat",
    "long",
    "blockcode",
    "ward",
    "warning",
])


def fetch_all() -> Iterator[dict]:
    """Paginate through every citation-violation row via SODA `$limit` +
    `$offset`. Order by `citationnum` for deterministic pagination."""
    offset = 0
    while True:
        params = {
            "$select": ALL_COLUMNS,
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$order": "citationnum ASC",
        }
        resp = requests.get(SODA_BASE, params=params, timeout=60)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        print(f"  offset={offset}: fetched {len(batch)} rows", flush=True)
        yield from batch
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE


def add_audit_columns(
    rows: Iterator[dict],
    run_id: str,
    extracted_at: datetime,
) -> Iterator[dict]:
    for row in rows:
        row["_extracted_at"] = extracted_at
        row["_extracted_run_id"] = run_id
        row["_source_endpoint"] = SOURCE_ENDPOINT
        yield row


def post_merge_first_seen(extracted_at: datetime) -> None:
    """Maintain `_first_seen_at` outside the dlt payload (311 / crime pattern)."""
    with duckdb.connect(DUCKDB_PATH) as conn:
        conn.execute("""
            ALTER TABLE main_bronze.raw_somerville_traffic_citations_raw
            ADD COLUMN IF NOT EXISTS _first_seen_at TIMESTAMP
        """)
        conn.execute("""
            UPDATE main_bronze.raw_somerville_traffic_citations_raw
            SET _first_seen_at = _extracted_at
            WHERE _first_seen_at IS NULL
        """)


def main() -> None:
    run_id = sys.argv[1] if len(sys.argv) > 1 else str(ULID())
    extracted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    print(f"\n=== somerville_traffic_citations pipeline run {run_id} ===")
    print(f"  extracted_at: {extracted_at.isoformat()}Z (UTC)")
    print(f"  destination:  duckdb @ {DUCKDB_PATH}")

    @dlt.resource(
        name="raw_somerville_traffic_citations_raw",
        primary_key="citationnum",
        write_disposition="merge",
    )
    def _resource():
        yield from add_audit_columns(fetch_all(), run_id, extracted_at)

    pipeline = dlt.pipeline(
        pipeline_name="somerville_traffic_citations",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="main_bronze",
    )
    info = pipeline.run(_resource())
    print(f"\nload info: {info}")

    post_merge_first_seen(extracted_at)
    print("post-merge _first_seen_at: done")


if __name__ == "__main__":
    main()
