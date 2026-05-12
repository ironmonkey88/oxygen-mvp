"""Check whether main_admin.fct_column_profile_raw is current with the warehouse.

Returns:
  0 — profile is current; no regen needed
  1 — profile is stale; caller should regenerate

Triggers staleness when:
  - Set of (schema, table, column) keys in warehouse differs from the latest profile
  - Any tracked table's row count moved by more than 10% since its last profile

Exclusion patterns match `scripts/profile_tables.py` exactly: tables
starting with `_` (dlt internals) and tables ending with `_raw` (dlt
landing tables behind dbt views) are not profiled and therefore not
checked here either.

Used in two places:
  - `run.sh` daily — cheap check that triggers a profile regen mid-pipeline if
    the schema or row counts moved meaningfully
  - manual smoke test — run after dbt model changes to confirm regen will fire
"""
import sys

import duckdb

DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
TRACKED_SCHEMAS = ["main_bronze", "main_gold"]
ROW_COUNT_THRESHOLD = 0.10


def main() -> int:
    try:
        with duckdb.connect(DUCKDB_PATH, read_only=True) as conn:
            placeholders = ",".join("?" * len(TRACKED_SCHEMAS))

            current = conn.execute(f"""
                SELECT table_schema, table_name, column_name
                FROM information_schema.columns
                WHERE table_schema IN ({placeholders})
                  AND table_name NOT LIKE '\\_%' ESCAPE '\\'
                  AND table_name NOT LIKE '%\\_raw' ESCAPE '\\'
            """, TRACKED_SCHEMAS).fetchall()
            current_keys = set((s, t, c) for s, t, c in current)

            try:
                profiled = conn.execute(f"""
                    SELECT DISTINCT schema_name, table_name, column_name
                    FROM main_admin.fct_column_profile_raw
                    WHERE schema_name IN ({placeholders})
                """, TRACKED_SCHEMAS).fetchall()
                profiled_keys = set((s, t, c) for s, t, c in profiled)
            except duckdb.CatalogException:
                print("STALE: fct_column_profile_raw does not exist")
                return 1

            if current_keys != profiled_keys:
                added = current_keys - profiled_keys
                removed = profiled_keys - current_keys
                print(f"STALE: schema changed. Added: {len(added)}, removed: {len(removed)}")
                if added:
                    print(f"  added: {sorted(added)[:5]}")
                if removed:
                    print(f"  removed: {sorted(removed)[:5]}")
                return 1

            tables = set((s, t) for s, t, _ in current_keys)
            for schema, table in tables:
                current_count = conn.execute(
                    f'SELECT COUNT(*) FROM "{schema}"."{table}"'
                ).fetchone()[0]

                row = conn.execute("""
                    SELECT row_count
                    FROM main_admin.fct_column_profile_raw
                    WHERE schema_name = ? AND table_name = ?
                    ORDER BY profiled_at DESC LIMIT 1
                """, (schema, table)).fetchone()

                if not row or row[0] is None:
                    continue
                latest_count = row[0]

                if latest_count == 0:
                    if current_count > 0:
                        print(f"STALE: {schema}.{table} went from 0 → {current_count} rows")
                        return 1
                    continue

                delta = abs(current_count - latest_count) / latest_count
                if delta > ROW_COUNT_THRESHOLD:
                    print(
                        f"STALE: {schema}.{table} row count "
                        f"{latest_count:,} → {current_count:,} (Δ={delta:.1%})"
                    )
                    return 1

            print("CURRENT: profile is up to date")
            return 0

    except Exception as e:
        print(f"STALE: staleness check errored: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
