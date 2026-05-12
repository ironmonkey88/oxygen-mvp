"""Somerville 311 ingestion pipeline (full-pull + merge on `id`).

Plan 1a redesign (2026-05-12): switched from filesystem-Parquet (year-partitioned)
to DuckDB destination with `merge` write disposition on the source primary key
`id`. The Somerville dataset has no per-row modified field; Socrata's
`:updated_at` is republish-batch-level. Full-pull each run is fast (~1-2 min
for 1.17M rows) and gives correct INSERT-vs-UPDATE semantics out of the box.

Tables produced in `main_bronze`:
  - raw_311_requests_raw (dlt-owned, merge target)
  - _dlt_pipeline_state, _dlt_loads, _dlt_version (dlt metadata)

Audit columns injected per row:
  - _extracted_at      TIMESTAMP   when this run extracted the row
  - _extracted_run_id  TEXT (ULID) which pipeline run produced this state
  - _source_endpoint   TEXT        SODA URL the row came from

`_first_seen_at` is not in the payload — it lives in the target table and is
set by a post-merge UPDATE (preserved across re-extractions, set fresh on
INSERT).

Usage:
    python dlt/somerville_311_pipeline.py [RUN_ID]

If RUN_ID is omitted, a fresh ULID is generated (ad-hoc invocation). In
run.sh the run_id is supplied by scripts/pipeline_run_start.py so the same
identifier appears in fct_pipeline_run_raw and on every row this run touched.
"""
import sys
from datetime import datetime, timezone
from typing import Iterator

import dlt
import duckdb
import requests
from ulid import ULID

SODA_BASE = "https://data.somervillema.gov/resource/4pyi-uqq6.json"
PAGE_SIZE = 50_000
DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
SOURCE_ENDPOINT = SODA_BASE

ALL_COLUMNS = ",".join([
    "id", "classification", "category", "type", "origin_of_request",
    "most_recent_status_date", "most_recent_status", "date_created",
    "block_code", "ward",
    "accuracy", "courtesy", "ease", "overallexperience",
    "emergency_readiness_and_response_planning",
    "green_space_care_and_maintenance",
    "infrastructure_maintenance_and_repairs",
    "noise_and_activity_disturbances",
    "reliable_service_delivery",
    "navigating_city_services_and_policies",
    "public_space_cleanliness_and_environmental_health",
    "voting_and_election_information",
])


def fetch_all() -> Iterator[dict]:
    """Paginate through every 311 record via SODA `$limit` + `$offset`."""
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
    """Inject pipeline-metadata columns into every row before dlt sees them."""
    for row in rows:
        row["_extracted_at"] = extracted_at
        row["_extracted_run_id"] = run_id
        row["_source_endpoint"] = SOURCE_ENDPOINT
        yield row


def post_merge_first_seen(extracted_at: datetime) -> None:
    """Maintain `_first_seen_at` semantics outside the dlt payload.

    On first ever run, dlt creates the table without this column. We add it
    via ALTER ... IF NOT EXISTS (idempotent across runs) and then set it to
    `_extracted_at` only for rows where it's still NULL (i.e. brand-new
    INSERTs from this run). Existing rows keep their original first-seen
    timestamp because dlt's merge UPDATE only touches columns in the payload.
    """
    with duckdb.connect(DUCKDB_PATH) as conn:
        conn.execute("""
            ALTER TABLE main_bronze.raw_311_requests_raw
            ADD COLUMN IF NOT EXISTS _first_seen_at TIMESTAMP
        """)
        conn.execute("""
            UPDATE main_bronze.raw_311_requests_raw
            SET _first_seen_at = _extracted_at
            WHERE _first_seen_at IS NULL
        """)


def main() -> None:
    run_id = sys.argv[1] if len(sys.argv) > 1 else str(ULID())
    extracted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    print(f"\n=== somerville_311 pipeline run {run_id} ===")
    print(f"  extracted_at: {extracted_at.isoformat()}Z (UTC)")
    print(f"  destination:  duckdb @ {DUCKDB_PATH}")

    @dlt.resource(
        name="raw_311_requests_raw",
        primary_key="id",
        write_disposition="merge",
    )
    def _resource():
        yield from add_audit_columns(fetch_all(), run_id, extracted_at)

    pipeline = dlt.pipeline(
        pipeline_name="somerville_311",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="main_bronze",
    )
    info = pipeline.run(_resource())
    print(f"\nload info: {info}")

    post_merge_first_seen(extracted_at)
    print("post-merge _first_seen_at: done")


if __name__ == "__main__":
    main()
