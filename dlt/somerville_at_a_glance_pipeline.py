"""Somerville at a Glance ingestion pipeline (one-shot, replace mode).

Prompt 11 Phase D (2026-05-14). Long/tidy-format KPI table:
demographic + housing + economic metrics for Somerville (and
Massachusetts for comparison), 2010-2023 ACS plus historical
population back to 1850.

Source: Socrata `jnde-mi6j`. 749 rows / 6 columns. Grain is one row
per (topic, description, year, geography). Underlying source is ACS,
which updates annually -- daily ingest doesn't make sense. Treated as
a manual one-shot ingestion, **not wired into run.sh**.

This is the data source for the /somerville (info) portal page, Phase
E of this batch.

Tables produced in `main_bronze`:
  - raw_somerville_at_a_glance_raw (dlt-owned, replace target)

Audit columns injected per row:
  - _extracted_at      TIMESTAMP   when this run extracted the row
  - _extracted_run_id  TEXT (ULID) which manual run produced this state
  - _source_endpoint   TEXT        SODA URL the row came from

No `_first_seen_at` -- replace mode wipes the table on each ingest.

Usage:
    python dlt/somerville_at_a_glance_pipeline.py [RUN_ID]
"""
import sys
from datetime import datetime, timezone
from typing import Iterator

import dlt
import requests
from ulid import ULID

SODA_BASE = "https://data.somervillema.gov/resource/jnde-mi6j.json"
PAGE_SIZE = 5_000  # source ~749 rows; 1 page covers it
DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
SOURCE_ENDPOINT = SODA_BASE

ALL_COLUMNS = ",".join([
    "topic",
    "description",
    "year",
    "value",
    "units",
    "geography",
])


def fetch_all() -> Iterator[dict]:
    """Paginate (trivially -- one page) through the at-a-glance dataset."""
    offset = 0
    while True:
        params = {
            "$select": ALL_COLUMNS,
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$order": "topic ASC, year ASC, geography ASC",
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


def main() -> None:
    run_id = sys.argv[1] if len(sys.argv) > 1 else str(ULID())
    extracted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    print(f"\n=== somerville_at_a_glance pipeline run {run_id} ===")
    print(f"  extracted_at: {extracted_at.isoformat()}Z (UTC)")
    print(f"  destination:  duckdb @ {DUCKDB_PATH}")

    @dlt.resource(
        name="raw_somerville_at_a_glance_raw",
        write_disposition="replace",
    )
    def _resource():
        yield from add_audit_columns(fetch_all(), run_id, extracted_at)

    pipeline = dlt.pipeline(
        pipeline_name="somerville_at_a_glance",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="main_bronze",
    )
    info = pipeline.run(_resource())
    print(f"\nload info: {info}")


if __name__ == "__main__":
    main()
