"""Build the read-only snapshot that the Civic Pulse MCP server serves.

The MCP server (mcp/server.py) never touches the production warehouse. This
script, run by civic-pulse-snapshot.service after each successful
pipeline-refresh, produces /srv/civic-pulse/somerville_ro.duckdb:

1. Copy the production file with a plain file copy. No DuckDB connection, so no
   lock is taken and the hourly source-health writers are never blocked. The copy
   is retried until the source's size and mtime are unchanged across it and no
   .wal file sits beside it (a writer was mid-transaction).
2. Open that private copy read-only and CREATE TABLE ... AS SELECT only the
   columns in ALLOWED below into a fresh database. Anything not listed (a new
   table, a new column) stays out until someone adds it here.
3. Check row counts match, then rename the new file over the old one. The server
   opens the file per query, so the next query sees the new data; a query already
   running keeps the old inode.

On any failure the previous snapshot is left in place and the unit exits 1.

Excluded on purpose (2026-10-12, Gordon): fct_permits.work_description (free text
with names, phone numbers and emails of owners and contractors) and
fct_citations.address / latitude / longitude (house-level location and time of a
traffic stop). Do not add them back without his yes.

Usage:
    build_ro_snapshot.py [--src PATH] [--out PATH]
"""
import argparse
import os
import shutil
import sys
import time
from datetime import datetime, timezone

import duckdb

SRC = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
OUT = "/srv/civic-pulse/somerville_ro.duckdb"
SCHEMA = "main_gold"
COPY_ATTEMPTS = 10
COPY_RETRY_SECONDS = 30

ALLOWED: dict[str, list[str]] = {
    "dim_date": [
        "date_dt", "year", "quarter", "month", "month_name", "day", "day_of_week",
        "day_name", "week_of_year", "is_weekend", "fiscal_year",
    ],
    "dim_kpi_topic": [
        "topic", "first_year", "latest_year", "observation_count", "geography_count",
        "has_massachusetts_benchmark", "has_somerville_data",
    ],
    "dim_offense_category": ["offense_category", "severity_rank"],
    "dim_offense_code": [
        "offense_code", "offense", "offense_type", "offense_category",
        "is_multi_offense_grouping", "is_active",
    ],
    "dim_request_type": ["request_type_id", "request_type", "first_seen_dt", "last_seen_dt", "request_count"],
    "dim_status": ["status_id", "status", "is_open", "first_seen_dt", "last_seen_dt"],
    "dim_survey_question": [
        "survey_question_id", "column_name", "question_label", "topic", "scale_min",
        "scale_max", "first_wave_asked", "last_wave_asked", "waves_asked_count",
    ],
    "dim_survey_wave": ["survey_wave_id", "wave_year", "respondent_count", "ward_coverage_pct", "notes"],
    "dim_ward": [
        "ward_id", "ward", "ward_name", "geometry_wkt_wgs84", "area_sqm", "area_sqkm",
        "perimeter_m", "_extracted_at",
    ],
    "fct_311_requests": [
        "id", "classification", "category", "request_type", "request_type_id", "status",
        "status_id", "origin", "date_created_dt", "date_created_ts", "most_recent_status_dt",
        "most_recent_status_ts", "ward", "block_code", "accuracy", "courtesy", "ease",
        "overallexperience", "is_emergency_readiness_tag", "is_green_space_tag",
        "is_infrastructure_tag", "is_noise_tag", "is_reliable_service_tag",
        "is_city_services_tag", "is_public_space_tag", "is_voting_tag",
    ],
    # Excluded: address, latitude, longitude.
    "fct_citations": [
        "citation_id", "citation_number", "citation_ts", "citation_date", "citation_year",
        "police_shift", "charge_code", "charge_description", "charge_category", "vehicle_mph",
        "posted_mph_zone", "ward", "block_code", "warning_flag", "is_warning", "_extracted_at",
    ],
    "fct_crime_incidents": [
        "incident_id", "case_number", "incident_dt", "incident_year", "incident_year_only",
        "police_shift", "offense_code", "multi_offense_flag", "offense", "offense_type",
        "offense_category", "ward", "block_code", "_extracted_at",
    ],
    "fct_happiness_survey": [
        "survey_observation_id", "survey_wave_id", "survey_question_id", "geography_level",
        "geography_key", "respondent_count", "mean_score", "median_score", "score_1_count",
        "score_2_count", "score_3_count", "score_4_count", "score_5_count", "weight_strategy",
    ],
    # Excluded: work_description.
    "fct_permits": [
        "permit_id", "permit_number", "application_date", "issue_date", "application_year",
        "issue_year", "permit_type", "permit_status", "is_issued", "permit_amount", "address",
        "ward", "latitude", "longitude", "_extracted_at",
    ],
    "fct_somerville_kpi": [
        "kpi_id", "topic", "year", "value", "kpi_description", "units", "geography", "_extracted_at",
    ],
}


def _fingerprint(path: str) -> tuple[int, int]:
    st = os.stat(path)
    return st.st_mtime_ns, st.st_size


def stable_copy(src: str, dst: str) -> None:
    """Copy src to dst, retrying until no writer touched src during the copy."""
    for attempt in range(1, COPY_ATTEMPTS + 1):
        if not os.path.exists(src + ".wal"):
            before = _fingerprint(src)
            shutil.copyfile(src, dst)
            if _fingerprint(src) == before and not os.path.exists(src + ".wal"):
                return
        print(f"source changed during copy (attempt {attempt}/{COPY_ATTEMPTS}); retrying", flush=True)
        time.sleep(COPY_RETRY_SECONDS)
    raise RuntimeError(f"could not get a stable copy of {src} after {COPY_ATTEMPTS} attempts")


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def build(raw: str, out_tmp: str, source_mtime: datetime) -> dict[str, int]:
    con = duckdb.connect(out_tmp)
    try:
        con.execute(f"ATTACH '{raw}' AS src (READ_ONLY)")
        con.execute(f"CREATE SCHEMA {SCHEMA}")
        counts: dict[str, int] = {}
        for table, columns in ALLOWED.items():
            present = {
                r[0] for r in con.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_catalog = 'src' AND table_schema = ? AND table_name = ?",
                    [SCHEMA, table],
                ).fetchall()
            }
            missing = [c for c in columns if c not in present]
            if missing:
                raise RuntimeError(f"{SCHEMA}.{table} is missing allowed columns {missing}")
            ignored = sorted(present - set(columns))
            if ignored:
                print(f"{table}: not exposed {ignored}", flush=True)
            cols = ", ".join(_quote(c) for c in columns)
            con.execute(
                f"CREATE TABLE {SCHEMA}.{_quote(table)} AS "
                f"SELECT {cols} FROM src.{SCHEMA}.{_quote(table)}"
            )
            src_n = con.execute(f"SELECT count(*) FROM src.{SCHEMA}.{_quote(table)}").fetchone()[0]
            new_n = con.execute(f"SELECT count(*) FROM {SCHEMA}.{_quote(table)}").fetchone()[0]
            if src_n != new_n:
                raise RuntimeError(f"{table}: copied {new_n} rows, source has {src_n}")
            counts[table] = new_n
        con.execute(
            f"CREATE TABLE {SCHEMA}.snapshot_info AS SELECT "
            "?::TIMESTAMPTZ AS built_at, ?::TIMESTAMPTZ AS source_modified_at",
            [datetime.now(timezone.utc), source_mtime],
        )
        con.execute("DETACH src")
        con.execute("CHECKPOINT")
        return counts
    finally:
        con.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    out_dir = os.path.dirname(args.out)
    raw = os.path.join(out_dir, ".source-copy.duckdb")
    out_tmp = os.path.join(out_dir, ".snapshot-building.duckdb")
    for leftover in (raw, out_tmp, out_tmp + ".wal"):
        if os.path.exists(leftover):
            os.remove(leftover)

    try:
        stable_copy(args.src, raw)
        source_mtime = datetime.fromtimestamp(os.stat(raw).st_mtime, timezone.utc)
        counts = build(raw, out_tmp, source_mtime)
        os.chmod(out_tmp, 0o644)
        os.replace(out_tmp, args.out)
    except Exception as exc:  # leave the previous snapshot serving
        print(f"snapshot NOT updated: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        for leftover in (raw, out_tmp, out_tmp + ".wal"):
            if os.path.exists(leftover):
                os.remove(leftover)

    total = sum(counts.values())
    print(f"snapshot updated: {args.out}, {len(counts)} tables, {total} rows", flush=True)
    for table, n in counts.items():
        print(f"  {table}: {n}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
