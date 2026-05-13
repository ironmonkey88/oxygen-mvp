"""Fetch Somerville's Socrata catalog and write to main_admin.fct_socrata_catalog_raw.

One row per dataset. Append-only with cataloged_at so refresh runs keep history.
Row counts fetched via SODA count(*) for tabular datasets; skipped for blob types.

Run: .venv/bin/python scripts/build_socrata_inventory.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import requests

DOMAIN = "data.somervillema.gov"
CATALOG_URL = "https://api.us.socrata.com/api/catalog/v1"
SODA_BASE = f"https://{DOMAIN}/resource"
DB_PATH = os.environ.get("DUCKDB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "somerville.duckdb"))
TABLE = "main_admin.fct_socrata_catalog_raw"
USER_AGENT = "oxygen-mvp-inventory/1.0 (gordon@oxy.tech)"


def fetch_catalog() -> list[dict]:
    """Page through the catalog API. Returns every result entry."""
    results: list[dict] = []
    offset = 0
    page = 100
    headers = {"User-Agent": USER_AGENT}
    while True:
        params = {"domains": DOMAIN, "limit": page, "offset": offset}
        r = requests.get(CATALOG_URL, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        batch = data.get("results", [])
        total = data.get("resultSetSize", 0)
        if not batch:
            break
        results.extend(batch)
        if len(results) >= total:
            break
        offset += page
    return results


def soda_count(dataset_id: str) -> tuple[int | None, str, str | None]:
    """Returns (row_count, method, error). method ∈ {soda_count, skipped_blob, error}."""
    url = f"{SODA_BASE}/{dataset_id}.json"
    headers = {"User-Agent": USER_AGENT}
    try:
        r = requests.get(url, params={"$select": "count(*)"}, headers=headers, timeout=30)
        if r.status_code != 200:
            return None, "error", f"HTTP {r.status_code}: {r.text[:200]}"
        body = r.json()
        # SODA returns [{"count":"N"}] or [{"count_*":"N"}]
        if isinstance(body, list) and body:
            for key in ("count", "count_*"):
                if key in body[0]:
                    return int(body[0][key]), "soda_count", None
            # fallback: take the first value
            return int(next(iter(body[0].values()))), "soda_count", None
        return None, "error", f"Unexpected body: {body!r}"
    except Exception as exc:  # noqa: BLE001
        return None, "error", f"{type(exc).__name__}: {exc}"


def to_row(entry: dict, cataloged_at: datetime) -> dict:
    res = entry.get("resource", {}) or {}
    cls = entry.get("classification", {}) or {}
    metadata = entry.get("metadata", {}) or {}
    dataset_id = res.get("id")
    resource_type = res.get("type")
    lens_view_type = res.get("lens_view_type")
    blob_mime_type = res.get("blob_mime_type")

    # Tabular = SODA-queryable. Anything that has a blob_mime_type is NOT tabular.
    # Socrata `type` values that are tabular: "dataset". Others (map, chart, filter,
    # story, link, href, blob, calendar, form, file) are not.
    is_tabular = (resource_type == "dataset") and (blob_mime_type is None)

    columns_name = res.get("columns_name") or []
    columns_field_name = res.get("columns_field_name") or []
    columns_datatype = res.get("columns_datatype") or []
    columns_description = res.get("columns_description") or []

    row_count, row_count_method, row_count_error = (None, "skipped_blob", None)
    if is_tabular:
        row_count, row_count_method, row_count_error = soda_count(dataset_id)

    return {
        "cataloged_at": cataloged_at,
        "dataset_id": dataset_id,
        "title": res.get("name"),
        "description": res.get("description") or "",
        "attribution": res.get("attribution"),
        "resource_type": resource_type,
        "lens_view_type": lens_view_type,
        "is_tabular": is_tabular,
        "blob_mime_type": blob_mime_type,
        "domain_category": cls.get("domain_category"),
        "domain_tags": json.dumps(cls.get("domain_tags") or []),
        "domain_metadata": json.dumps(cls.get("domain_metadata") or []),
        "column_count": len(columns_name),
        "column_names": json.dumps(columns_name),
        "column_field_names": json.dumps(columns_field_name),
        "column_types": json.dumps(columns_datatype),
        "column_descriptions": json.dumps(columns_description),
        "row_count": row_count,
        "row_count_method": row_count_method,
        "row_count_error": row_count_error,
        "created_at": res.get("createdAt"),
        "updated_at": res.get("updatedAt"),
        "data_updated_at": res.get("data_updated_at"),
        "metadata_updated_at": res.get("metadata_updated_at"),
        "permalink": entry.get("permalink"),
        "resource_endpoint": f"{SODA_BASE}/{dataset_id}.json" if is_tabular else None,
        "page_views_total": (res.get("page_views") or {}).get("page_views_total"),
        "download_count": res.get("download_count"),
        "provenance": res.get("provenance"),
        "license": (metadata.get("license") or None),
    }


DDL = """
CREATE SCHEMA IF NOT EXISTS main_admin;
CREATE TABLE IF NOT EXISTS main_admin.fct_socrata_catalog_raw (
  cataloged_at TIMESTAMP NOT NULL,
  dataset_id VARCHAR NOT NULL,
  title VARCHAR,
  description VARCHAR,
  attribution VARCHAR,
  resource_type VARCHAR,
  lens_view_type VARCHAR,
  is_tabular BOOLEAN,
  blob_mime_type VARCHAR,
  domain_category VARCHAR,
  domain_tags VARCHAR,
  domain_metadata VARCHAR,
  column_count INTEGER,
  column_names VARCHAR,
  column_field_names VARCHAR,
  column_types VARCHAR,
  column_descriptions VARCHAR,
  row_count BIGINT,
  row_count_method VARCHAR,
  row_count_error VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  data_updated_at TIMESTAMP,
  metadata_updated_at TIMESTAMP,
  permalink VARCHAR,
  resource_endpoint VARCHAR,
  page_views_total INTEGER,
  download_count INTEGER,
  provenance VARCHAR,
  license VARCHAR
);
"""


def main() -> int:
    cataloged_at = datetime.now(timezone.utc)
    print(f"[{cataloged_at.isoformat()}] Fetching Socrata catalog for {DOMAIN}...")
    entries = fetch_catalog()
    print(f"  → {len(entries)} dataset entries")

    rows: list[dict] = []
    for i, entry in enumerate(entries, 1):
        row = to_row(entry, cataloged_at)
        rows.append(row)
        tag = "tabular" if row["is_tabular"] else f"blob({row['resource_type']})"
        rc = row["row_count"] if row["row_count"] is not None else "n/a"
        print(f"  [{i:>2}/{len(entries)}] {row['dataset_id']} {tag:<14} rows={rc} title={row['title'][:60]!s}")
        time.sleep(0.1)  # be polite to the API

    con = duckdb.connect(DB_PATH)
    con.execute(DDL)
    cols = list(rows[0].keys())
    placeholders = ", ".join(["?"] * len(cols))
    insert_sql = f"INSERT INTO {TABLE} ({', '.join(cols)}) VALUES ({placeholders})"
    for row in rows:
        con.execute(insert_sql, [row[c] for c in cols])
    con.commit()
    cnt = con.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
    latest = con.execute(f"SELECT COUNT(*) FROM {TABLE} WHERE cataloged_at = ?", [cataloged_at]).fetchone()[0]
    con.close()
    print(f"[done] {TABLE}: {cnt} total rows ({latest} from this run at {cataloged_at.isoformat()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
