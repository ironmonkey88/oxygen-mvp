"""Hourly source-health check for the Somerville 311 SODA endpoint.

Writes one row per invocation to main_admin.fct_source_health_raw. Tracked
independently of pipeline runs: hourly cadence (via systemd timer) gives a
finer-grained view of source availability than the daily pipeline can.

For the Somerville 311 dataset there is no per-row modified field; Socrata's
`rowsUpdatedAt` is republish-batch-level (the whole dataset is re-uploaded
periodically, not row-by-row). We capture that timestamp plus the source's
total row count and the HTTP outcome.

Owned by Python (not dbt): table is created on first run, rows append-only.
"""
import sys
import time
from datetime import datetime, timezone

import duckdb
import requests
from ulid import ULID

DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
SODA_DATA = "https://data.somervillema.gov/resource/4pyi-uqq6.json"
SODA_METADATA = "https://data.somervillema.gov/api/views/4pyi-uqq6.json"
STALENESS_HOURS = 36

DDL = """
CREATE SCHEMA IF NOT EXISTS main_admin;
CREATE TABLE IF NOT EXISTS main_admin.fct_source_health_raw (
    check_id                   TEXT PRIMARY KEY,
    checked_at                 TIMESTAMP NOT NULL,
    source_endpoint            TEXT NOT NULL,
    source_rows_updated_at     TIMESTAMP,
    source_row_count           BIGINT,
    hours_since_source_update  INTEGER,
    check_status               TEXT NOT NULL,
    http_response_code         INTEGER,
    fetch_duration_ms          INTEGER,
    error_message              TEXT
);
"""


def main() -> None:
    check_id = str(ULID())
    checked_at = datetime.now(timezone.utc).replace(tzinfo=None)

    source_rows_updated_at = None
    source_row_count = None
    hours_since = None
    http_code = None
    fetch_ms = None
    check_status = "unreachable"
    error_message = None

    started = time.time()
    try:
        meta_resp = requests.get(SODA_METADATA, timeout=15)
        http_code = meta_resp.status_code
        fetch_ms = int((time.time() - started) * 1000)
        if meta_resp.status_code != 200:
            error_message = f"metadata HTTP {meta_resp.status_code}"
        else:
            m = meta_resp.json()
            rows_updated_at_epoch = m.get("rowsUpdatedAt")
            if rows_updated_at_epoch is not None:
                source_rows_updated_at = datetime.fromtimestamp(
                    rows_updated_at_epoch, tz=timezone.utc
                ).replace(tzinfo=None)
                hours_since = int(
                    (checked_at - source_rows_updated_at).total_seconds() / 3600
                )

            count_resp = requests.get(
                SODA_DATA,
                params={"$select": "count(*) AS n"},
                timeout=15,
            )
            if count_resp.status_code == 200:
                data = count_resp.json()
                if data and "n" in data[0]:
                    source_row_count = int(data[0]["n"])

            if hours_since is not None and hours_since > STALENESS_HOURS:
                check_status = "stale"
            else:
                check_status = "ok"
    except requests.RequestException as e:
        fetch_ms = int((time.time() - started) * 1000)
        check_status = "unreachable"
        error_message = str(e)[:500]
    except Exception as e:
        fetch_ms = int((time.time() - started) * 1000)
        check_status = "unreachable"
        error_message = f"{type(e).__name__}: {str(e)[:500]}"

    with duckdb.connect(DUCKDB_PATH) as conn:
        conn.execute(DDL)
        conn.execute(
            """
            INSERT INTO main_admin.fct_source_health_raw VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                check_id, checked_at, SODA_DATA,
                source_rows_updated_at, source_row_count,
                hours_since, check_status,
                http_code, fetch_ms, error_message,
            ),
        )

    sys.stderr.write(
        f"check {check_id} → {check_status} "
        f"(http={http_code}, source_row_count={source_row_count}, "
        f"hours_since={hours_since})\n"
    )


if __name__ == "__main__":
    main()
