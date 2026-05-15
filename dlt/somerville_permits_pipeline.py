"""Somerville Permits ingestion pipeline (one-shot, replace mode).

Prompt 11 Phase B (2026-05-14). Adapted from
`dlt/somerville_happiness_survey_pipeline.py` -- same shape: small
dataset, replace mode, not wired into `run.sh`.

Source: Inspectional Services Department permit applications dating
back to 2014 (Socrata `vxgw-vmky`). 64,521 rows / 10 columns as of
2026-05-14. **Source `rowsUpdatedAt`: 2023-05-16** -- nearly 3 years
stale. This dataset appears to have stopped being refreshed in May
2023. Re-run manually if a new wave publishes.

Tables produced in `main_bronze`:
  - raw_somerville_permits_raw (dlt-owned, replace target)

Audit columns injected per row:
  - _extracted_at      TIMESTAMP   when this run extracted the row
  - _extracted_run_id  TEXT (ULID) which manual run produced this state
  - _source_endpoint   TEXT        SODA URL the row came from

No `_first_seen_at` -- replace mode wipes the table on each ingest.

Usage:
    python dlt/somerville_permits_pipeline.py [RUN_ID]
"""
import sys
from datetime import datetime, timezone
from typing import Iterator

import dlt
import requests
from ulid import ULID

SODA_BASE = "https://data.somervillema.gov/resource/vxgw-vmky.json"
PAGE_SIZE = 25_000  # source ~64.5K rows; 3 pages cover it
DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
SOURCE_ENDPOINT = SODA_BASE

# Source columns observed via SODA metadata 2026-05-14.
ALL_COLUMNS = ",".join([
    "id",
    "application_date",
    "issue_date",
    "type",
    "status",
    "amount",
    "address",
    "latitude",
    "longitude",
    "work",
])


def fetch_all() -> Iterator[dict]:
    """Paginate through every permit record via SODA `$limit` + `$offset`.

    Order by `id` for deterministic pagination -- ids are
    year-prefixed like `B14-001277`.
    """
    offset = 0
    while True:
        params = {
            "$select": ALL_COLUMNS,
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$order": "id ASC",
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
    print(f"\n=== somerville_permits pipeline run {run_id} ===")
    print(f"  extracted_at: {extracted_at.isoformat()}Z (UTC)")
    print(f"  destination:  duckdb @ {DUCKDB_PATH}")

    @dlt.resource(
        name="raw_somerville_permits_raw",
        write_disposition="replace",
    )
    def _resource():
        yield from add_audit_columns(fetch_all(), run_id, extracted_at)

    pipeline = dlt.pipeline(
        pipeline_name="somerville_permits",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="main_bronze",
    )
    info = pipeline.run(_resource())
    print(f"\nload info: {info}")


if __name__ == "__main__":
    main()
