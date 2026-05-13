"""Somerville Police Crime Reports ingestion pipeline (full-pull + merge on `incnum`).

Plan 12 Phase 3 (2026-05-13). Adapted from `dlt/somerville_311_pipeline.py`
— same shape (full-pull, merge-on-PK, DuckDB destination, audit columns)
applied to Socrata dataset `aghs-hqvg`.

Source: City of Somerville Police Department crime reports, 2017-present.
22K rows as of 2026-05-13 — tiny by comparison to 311. Refreshes daily
from source with a one-month publication delay (per the Socrata
description). Source-level PII redaction is already applied to sensitive
incidents (time/location stripped); see
`docs/limitations/crime-data-pii-unredacted-in-bronze.md` for what still
needs care.

Tables produced in `main_bronze`:
  - raw_somerville_crime_raw (dlt-owned, merge target)

Audit columns injected per row:
  - _extracted_at      TIMESTAMP   when this run extracted the row
  - _extracted_run_id  TEXT (ULID) which pipeline run produced this state
  - _source_endpoint   TEXT        SODA URL the row came from

`_first_seen_at` follows the 311 pattern — added via ALTER TABLE after
merge, populated only for rows where it's still NULL (preserved across
re-extractions).

Usage:
    python dlt/somerville_crime_pipeline.py [RUN_ID]
"""
import sys
from datetime import datetime, timezone
from typing import Iterator

import dlt
import duckdb
import requests
from ulid import ULID

SODA_BASE = "https://data.somervillema.gov/resource/aghs-hqvg.json"
PAGE_SIZE = 50_000  # source is ~22K total; 1 page covers it but the loop is safe
DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
SOURCE_ENDPOINT = SODA_BASE

# Source columns observed on 2026-05-13 via SODA probe.
ALL_COLUMNS = ",".join([
    "incnum",
    "day_and_month",
    "year",
    "police_shift",
    "offensecode",
    "offense",
    "incdesc",
    "offensetype",
    "category",
    "blockcode",
    "ward",
])


def fetch_all() -> Iterator[dict]:
    """Paginate through every crime record via SODA `$limit` + `$offset`."""
    offset = 0
    while True:
        params = {
            "$select": ALL_COLUMNS,
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$order": "incnum ASC",
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
    """Inject pipeline-metadata columns into every row before dlt sees them."""
    for row in rows:
        row["_extracted_at"] = extracted_at
        row["_extracted_run_id"] = run_id
        row["_source_endpoint"] = SOURCE_ENDPOINT
        yield row


def post_merge_first_seen(extracted_at: datetime) -> None:
    """Maintain `_first_seen_at` semantics outside the dlt payload."""
    with duckdb.connect(DUCKDB_PATH) as conn:
        conn.execute("""
            ALTER TABLE main_bronze.raw_somerville_crime_raw
            ADD COLUMN IF NOT EXISTS _first_seen_at TIMESTAMP
        """)
        conn.execute("""
            UPDATE main_bronze.raw_somerville_crime_raw
            SET _first_seen_at = _extracted_at
            WHERE _first_seen_at IS NULL
        """)


def main() -> None:
    run_id = sys.argv[1] if len(sys.argv) > 1 else str(ULID())
    extracted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    print(f"\n=== somerville_crime pipeline run {run_id} ===")
    print(f"  extracted_at: {extracted_at.isoformat()}Z (UTC)")
    print(f"  destination:  duckdb @ {DUCKDB_PATH}")

    @dlt.resource(
        name="raw_somerville_crime_raw",
        primary_key="incnum",
        write_disposition="merge",
    )
    def _resource():
        yield from add_audit_columns(fetch_all(), run_id, extracted_at)

    pipeline = dlt.pipeline(
        pipeline_name="somerville_crime",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="main_bronze",
    )
    info = pipeline.run(_resource())
    print(f"\nload info: {info}")

    post_merge_first_seen(extracted_at)
    print("post-merge _first_seen_at: done")


if __name__ == "__main__":
    main()
