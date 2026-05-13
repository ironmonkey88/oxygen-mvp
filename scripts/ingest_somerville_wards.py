"""Ingest the Somerville Wards shapefile (Socrata `ym5n-phxd`) into bronze.

One-shot ingestion for static geospatial reference data. Run manually when
the source updates; not part of `./run.sh` (per Plan 12 brief). Uses
DuckDB's spatial extension to read the ESRI shapefile directly.

Target: main_bronze.raw_somerville_wards_raw (Python-owned, _raw suffix).
Geometry is read in source projection (NAD83 MA State Plane per the
shapefile's .prj) and re-projected to WGS84 EPSG:4326 for downstream
use (lat/lng-friendly).

Run: .venv/bin/python scripts/ingest_somerville_wards.py
"""

from __future__ import annotations

import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("DUCKDB_PATH", str(REPO_ROOT / "data" / "somerville.duckdb"))
RAW_DIR = REPO_ROOT / "data" / "raw" / "somerville_wards"
ZIP_PATH = RAW_DIR / "Wards.zip"
SHP_PATH = RAW_DIR / "Wards.shp"

DATASET_ID = "ym5n-phxd"
BLOB_ID = "73395843-c093-4a7f-aab2-6deb4e452b63"
DOWNLOAD_URL = (
    f"https://data.somervillema.gov/api/views/{DATASET_ID}"
    f"/files/{BLOB_ID}?download=true&filename=Wards.zip"
)
SOURCE_URL = f"https://data.somervillema.gov/d/{DATASET_ID}"
TABLE = "main_bronze.raw_somerville_wards_raw"


def fetch_and_unzip(force: bool = False) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if force or not ZIP_PATH.exists():
        print(f"  downloading {DOWNLOAD_URL}")
        r = requests.get(DOWNLOAD_URL, timeout=60)
        r.raise_for_status()
        ZIP_PATH.write_bytes(r.content)
        print(f"  → {ZIP_PATH} ({len(r.content):,} bytes)")
    else:
        print(f"  using cached {ZIP_PATH}")
    if force or not SHP_PATH.exists():
        print(f"  unzipping → {RAW_DIR}")
        with zipfile.ZipFile(ZIP_PATH) as z:
            z.extractall(RAW_DIR)
    else:
        print(f"  shapefile already unpacked at {SHP_PATH}")
    return SHP_PATH


def inspect_shapefile(con: duckdb.DuckDBPyConnection) -> list[tuple]:
    print(f"  inspecting shapefile attributes")
    rows = con.execute(f"""
        SELECT * EXCLUDE (geom) FROM ST_Read('{SHP_PATH}') LIMIT 100
    """).fetchall()
    cols = [d[0] for d in con.description]
    print(f"  columns: {cols}")
    for r in rows[:5]:
        print(f"  sample: {dict(zip(cols, r))}")
    return rows


def materialize_bronze(con: duckdb.DuckDBPyConnection) -> None:
    extracted_at = datetime.now(timezone.utc)
    print(f"  rebuilding {TABLE} at {extracted_at.isoformat()}")
    con.execute("CREATE SCHEMA IF NOT EXISTS main_bronze")
    # Drop + recreate (single source, full replace each run — same shape as a
    # snapshot reload of static reference data; we are not tracking history
    # of polygon edits here).
    con.execute(f"DROP TABLE IF EXISTS {TABLE}")
    con.execute(f"""
        CREATE TABLE {TABLE} AS
        SELECT
          *,
          ST_AsText(ST_Transform(geom, 'EPSG:2249', 'EPSG:4326', always_xy := TRUE)) AS geometry_wkt_wgs84,
          ST_AsText(geom) AS geometry_wkt_source,
          ST_Area(geom) AS area_source_units,
          TIMESTAMP '{extracted_at.isoformat()}' AS _extracted_at,
          '{SOURCE_URL}' AS _source_url,
          'Wards.shp' AS _source_filename,
          'EPSG:2249' AS _source_srid
        FROM ST_Read('{SHP_PATH}')
    """)
    n = con.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
    print(f"  → {n} wards loaded")
    # describe the resulting bronze schema for the log
    schema = con.execute(f"DESCRIBE {TABLE}").fetchall()
    print(f"  bronze schema:")
    for col_name, col_type, *_ in schema:
        print(f"    - {col_name:<28} {col_type}")


def main() -> int:
    fetch_and_unzip()
    con = duckdb.connect(DB_PATH)
    con.execute("INSTALL spatial")
    con.execute("LOAD spatial")
    inspect_shapefile(con)
    materialize_bronze(con)
    con.commit()
    con.close()
    print(f"[done] {TABLE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
