"""Source-health check for Somerville Socrata datasets.

Single parameterized script — call with the dataset slug to check one
dataset. Hourly cadence per dataset via independent systemd timers.

Plan 40 expanded coverage from 1 (311) to 6 (311, crime, permits,
traffic-citations, wards, at-a-glance). Pre-flight inspection found all
6 share the same Socrata metadata API shape (`/api/views/{id}.json`
returns `rowsUpdatedAt` for every dataset, including the wards
shapefile blob and the at-a-glance compendium). One script parameterized
on the dataset config is the honest abstraction — the API surface IS
uniform across all 6, only the data shape differs.

Per-dataset staleness thresholds reflect actual refresh expectations:
311 / crime / citations refresh daily so the threshold is 36h; permits
has been static since May 2023 per its limitations entry; wards is
fundamentally static reference data; at-a-glance refreshes annually with
ACS waves. Static/annual datasets get a very high threshold so the
`check_status` doesn't mislead the DBA dashboard's B1 panel into yelling
about long-known states.

Writes one row per invocation to `main_admin.fct_source_health_raw`.
Table schema is unchanged from v1 — same columns, the `source_endpoint`
column distinguishes the datasets in downstream queries.

Usage:
    python scripts/source_health_check.py <dataset-slug>

Where <dataset-slug> is one of: 311, crime, permits, traffic-citations,
wards, at-a-glance.
"""
import sys
import time
from datetime import datetime, timezone

import duckdb
import requests
from ulid import ULID

DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"

# Per-dataset config. The Socrata 4x4 ID + a per-dataset staleness
# threshold in hours. Datasets that are documented-static (wards) or
# documented-annual (at-a-glance) get a very high threshold so the check
# doesn't report long-known states as "stale".
DATASETS = {
    "311": {
        "id": "4pyi-uqq6",
        "staleness_hours": 36,  # daily refresh, allow 1.5x for systemd timing slack
    },
    "crime": {
        "id": "aghs-hqvg",
        "staleness_hours": 36,
    },
    "traffic-citations": {
        "id": "3mqx-eye9",
        "staleness_hours": 36,
    },
    "permits": {
        # Source has been static since 2023-05-16 per
        # docs/limitations/permits-static-since-2023.md. Threshold high
        # enough to suppress chronic-"stale" — the limitation is the truth,
        # not a B1 panel alert.
        "id": "vxgw-vmky",
        "staleness_hours": 24 * 365 * 5,  # 5 years
    },
    "wards": {
        # Reference data; never refreshed expected.
        "id": "ym5n-phxd",
        "staleness_hours": 24 * 365 * 100,  # essentially infinite
    },
    "at-a-glance": {
        # Annual ACS refresh; allow ~13 months of slack.
        "id": "jnde-mi6j",
        "staleness_hours": 24 * 400,
    },
}

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


def check_dataset(slug: str) -> None:
    cfg = DATASETS.get(slug)
    if cfg is None:
        raise SystemExit(f"unknown dataset slug: {slug!r} (choose: {', '.join(DATASETS)})")
    dataset_id = cfg["id"]
    staleness_hours = cfg["staleness_hours"]
    soda_data = f"https://data.somervillema.gov/resource/{dataset_id}.json"
    soda_metadata = f"https://data.somervillema.gov/api/views/{dataset_id}.json"

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
        meta_resp = requests.get(soda_metadata, timeout=15)
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
                soda_data,
                params={"$select": "count(*) AS n"},
                timeout=15,
            )
            if count_resp.status_code == 200:
                data = count_resp.json()
                if data and "n" in data[0]:
                    source_row_count = int(data[0]["n"])

            if hours_since is not None and hours_since > staleness_hours:
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
                check_id, checked_at, soda_data,
                source_rows_updated_at, source_row_count,
                hours_since, check_status,
                http_code, fetch_ms, error_message,
            ),
        )

    sys.stderr.write(
        f"check {check_id} [{slug}] → {check_status} "
        f"(http={http_code}, row_count={source_row_count}, "
        f"hours_since={hours_since})\n"
    )


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            f"usage: source_health_check.py <dataset-slug>\n"
            f"slugs: {', '.join(DATASETS)}"
        )
    check_dataset(sys.argv[1])


if __name__ == "__main__":
    main()
