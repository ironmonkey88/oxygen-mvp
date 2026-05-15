"""Somerville Happiness Survey ingestion pipeline (one-shot, replace mode).

Prompt 11 Phase A (2026-05-14). Adapted from
`dlt/somerville_crime_pipeline.py` but with two key differences from the
crime template:
  - `write_disposition="replace"` (no merge-on-PK) -- the survey is
    biennial and tiny (12,583 rows / ~12 MB), so re-ingesting fresh on
    each manual run is cheaper than reasoning about merges.
  - **Not wired into `run.sh`.** Biennial cadence; daily pipeline runs
    would just re-ingest the same data. Re-run manually when the city
    publishes a new wave (next: ~2027 per the 2-year cycle).

The 150 source columns are pulled as-is. Bronze keeps the source shape;
column curation is silver's job (MVP 3). See
`scratch/phase-a-preflight.md` (gitignored) for the pre-flight findings
that determined this shape.

Tables produced in `main_bronze`:
  - raw_somerville_happiness_survey_raw (dlt-owned, replace target)

Audit columns injected per row:
  - _extracted_at      TIMESTAMP   when this run extracted the row
  - _extracted_run_id  TEXT (ULID) which manual run produced this state
  - _source_endpoint   TEXT        SODA URL the row came from

No `_first_seen_at` -- replace mode wipes the table on each ingest, so
the column would always equal `_extracted_at`. Skipped to keep the
schema honest.

Usage:
    python dlt/somerville_happiness_survey_pipeline.py [RUN_ID]
"""
import sys
from datetime import datetime, timezone
from typing import Iterator

import dlt
import requests
from ulid import ULID

SODA_BASE = "https://data.somervillema.gov/resource/wmeh-zuz2.json"
PAGE_SIZE = 5_000  # source is ~12.5K rows total; 3 pages cover it comfortably
DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
SOURCE_ENDPOINT = SODA_BASE


def fetch_all() -> Iterator[dict]:
    """Paginate through every survey response via SODA `$limit` + `$offset`.

    No `$select` -- pull every published column. Order by `id` so the
    pagination is deterministic.
    """
    offset = 0
    while True:
        params = {
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


def main() -> None:
    run_id = sys.argv[1] if len(sys.argv) > 1 else str(ULID())
    extracted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    print(f"\n=== somerville_happiness_survey pipeline run {run_id} ===")
    print(f"  extracted_at: {extracted_at.isoformat()}Z (UTC)")
    print(f"  destination:  duckdb @ {DUCKDB_PATH}")

    @dlt.resource(
        name="raw_somerville_happiness_survey_raw",
        write_disposition="replace",
    )
    def _resource():
        yield from add_audit_columns(fetch_all(), run_id, extracted_at)

    pipeline = dlt.pipeline(
        pipeline_name="somerville_happiness_survey",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="main_bronze",
    )
    info = pipeline.run(_resource())
    print(f"\nload info: {info}")


if __name__ == "__main__":
    main()
