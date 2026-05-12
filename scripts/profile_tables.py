"""Profile every column of bronze + gold tables.

Read-only on the schemas being profiled; one brief write at the end to
INSERT the new profile rows. Python-owned table per Plan 1b decision 1b/A
(`main_admin.fct_column_profile_raw`) — `CREATE TABLE IF NOT EXISTS` on
first invocation, append-only thereafter.

The output is consumed by `scripts/generate_profile_page.py` to render
the `/profile` portal page (Plan 1b decision 1b/D option c). dbt's
`schema.yml` files are NOT touched — column descriptions remain
hand-written.

Usage:
    profile_tables.py [--run-id RUN_ID]

If --run-id is provided, the profile rows carry it for traceability
back to a pipeline run (`main_admin.fct_pipeline_run_raw.run_id`).
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Optional

import duckdb
from ulid import ULID

DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
PROFILED_SCHEMAS = ["main_bronze", "main_gold"]
TOP_N_VALUES = 5

NUMERIC_TYPES = {"INTEGER", "BIGINT", "DOUBLE", "DECIMAL", "FLOAT", "REAL", "HUGEINT", "SMALLINT", "TINYINT"}
DATE_TYPES = {"TIMESTAMP", "DATE", "TIMESTAMP_NS", "TIMESTAMP_MS", "TIMESTAMPTZ", "TIMESTAMP WITH TIME ZONE"}
TEXT_TYPES = {"VARCHAR", "TEXT", "STRING"}
BOOLEAN_TYPES = {"BOOLEAN", "BOOL"}

DDL = """
CREATE SCHEMA IF NOT EXISTS main_admin;
CREATE TABLE IF NOT EXISTS main_admin.fct_column_profile_raw (
    profile_id              TEXT PRIMARY KEY,
    profiled_at             TIMESTAMP NOT NULL,
    run_id                  TEXT,

    schema_name             TEXT NOT NULL,
    table_name              TEXT NOT NULL,
    column_name             TEXT NOT NULL,
    column_type             TEXT NOT NULL,

    row_count               BIGINT,
    non_null_count          BIGINT,
    null_count              BIGINT,
    null_pct                DOUBLE,
    distinct_count          BIGINT,

    min_value               DOUBLE,
    max_value               DOUBLE,
    mean_value              DOUBLE,
    p25_value               DOUBLE,
    p50_value               DOUBLE,
    p75_value               DOUBLE,
    p95_value               DOUBLE,
    zero_count              BIGINT,
    negative_count          BIGINT,

    min_date                TIMESTAMP,
    max_date                TIMESTAMP,
    span_days               INTEGER,

    min_length              INTEGER,
    max_length              INTEGER,
    avg_length              DOUBLE,
    empty_string_count      BIGINT,
    top_5_values            TEXT,

    true_count              BIGINT,
    false_count             BIGINT
);
"""


def profile_column(
    conn: duckdb.DuckDBPyConnection,
    schema: str,
    table: str,
    column: str,
    col_type: str,
    run_id: Optional[str],
) -> dict:
    profile_id = str(ULID())
    profiled_at = datetime.now(timezone.utc).replace(tzinfo=None)
    qcol = f'"{column}"'
    qtab = f"{schema}.{table}"

    row_count, non_null_count, null_count, distinct_count = conn.execute(f"""
        SELECT
            COUNT(*),
            COUNT({qcol}),
            COUNT(*) - COUNT({qcol}),
            COUNT(DISTINCT {qcol})
        FROM {qtab}
    """).fetchone()
    null_pct = (null_count / row_count * 100.0) if row_count > 0 else 0.0

    record = {
        "profile_id": profile_id,
        "profiled_at": profiled_at,
        "run_id": run_id,
        "schema_name": schema,
        "table_name": table,
        "column_name": column,
        "column_type": col_type,
        "row_count": row_count,
        "non_null_count": non_null_count,
        "null_count": null_count,
        "null_pct": null_pct,
        "distinct_count": distinct_count,
        "min_value": None, "max_value": None, "mean_value": None,
        "p25_value": None, "p50_value": None, "p75_value": None, "p95_value": None,
        "zero_count": None, "negative_count": None,
        "min_date": None, "max_date": None, "span_days": None,
        "min_length": None, "max_length": None, "avg_length": None,
        "empty_string_count": None, "top_5_values": None,
        "true_count": None, "false_count": None,
    }

    if non_null_count == 0:
        return record

    col_type_upper = col_type.upper().split("(")[0].strip()

    if col_type_upper in NUMERIC_TYPES:
        row = conn.execute(f"""
            SELECT
                MIN({qcol})::DOUBLE,
                MAX({qcol})::DOUBLE,
                AVG({qcol})::DOUBLE,
                quantile_cont({qcol}, 0.25)::DOUBLE,
                quantile_cont({qcol}, 0.50)::DOUBLE,
                quantile_cont({qcol}, 0.75)::DOUBLE,
                quantile_cont({qcol}, 0.95)::DOUBLE,
                COUNT(*) FILTER (WHERE {qcol} = 0),
                COUNT(*) FILTER (WHERE {qcol} < 0)
            FROM {qtab}
            WHERE {qcol} IS NOT NULL
        """).fetchone()
        (record["min_value"], record["max_value"], record["mean_value"],
         record["p25_value"], record["p50_value"], record["p75_value"],
         record["p95_value"], record["zero_count"], record["negative_count"]) = row

    elif col_type_upper in DATE_TYPES:
        row = conn.execute(f"""
            SELECT
                MIN({qcol})::TIMESTAMP,
                MAX({qcol})::TIMESTAMP
            FROM {qtab}
            WHERE {qcol} IS NOT NULL
        """).fetchone()
        record["min_date"], record["max_date"] = row
        if record["min_date"] is not None and record["max_date"] is not None:
            record["span_days"] = (record["max_date"] - record["min_date"]).days

    elif col_type_upper in TEXT_TYPES:
        row = conn.execute(f"""
            SELECT
                MIN(LENGTH({qcol})),
                MAX(LENGTH({qcol})),
                AVG(LENGTH({qcol}))::DOUBLE,
                COUNT(*) FILTER (WHERE {qcol} = '')
            FROM {qtab}
            WHERE {qcol} IS NOT NULL
        """).fetchone()
        (record["min_length"], record["max_length"],
         record["avg_length"], record["empty_string_count"]) = row

        top5 = conn.execute(f"""
            SELECT {qcol}, COUNT(*) AS cnt
            FROM {qtab}
            WHERE {qcol} IS NOT NULL
            GROUP BY {qcol}
            ORDER BY cnt DESC, {qcol} ASC
            LIMIT {TOP_N_VALUES}
        """).fetchall()
        record["top_5_values"] = json.dumps([
            {
                "value": str(v)[:200],
                "count": int(c),
                "pct": round(c / non_null_count * 100.0, 2),
            }
            for v, c in top5
        ])

    elif col_type_upper in BOOLEAN_TYPES:
        row = conn.execute(f"""
            SELECT
                COUNT(*) FILTER (WHERE {qcol} = TRUE),
                COUNT(*) FILTER (WHERE {qcol} = FALSE)
            FROM {qtab}
            WHERE {qcol} IS NOT NULL
        """).fetchone()
        record["true_count"], record["false_count"] = row

    return record


def get_columns_to_profile(conn: duckdb.DuckDBPyConnection) -> list:
    """List columns of analyst-facing tables only.

    Exclusions:
      - Tables starting with `_` — dlt internal bookkeeping
        (`_dlt_loads`, `_dlt_pipeline_state`, `_dlt_version`).
      - Tables ending with `_raw` — dlt-owned landing tables that sit
        behind dbt-owned views (`raw_311_requests_raw`,
        `raw_dbt_results_raw`). The view counterpart is profiled instead.
    """
    placeholders = ",".join("?" * len(PROFILED_SCHEMAS))
    return conn.execute(f"""
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema IN ({placeholders})
          AND table_name NOT LIKE '\\_%' ESCAPE '\\'
          AND table_name NOT LIKE '%\\_raw' ESCAPE '\\'
        ORDER BY table_schema, table_name, ordinal_position
    """, PROFILED_SCHEMAS).fetchall()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    started = datetime.now(timezone.utc).replace(tzinfo=None)
    print(f"profile run starting at {started.isoformat()}Z")
    if args.run_id:
        print(f"  associated run_id: {args.run_id}")

    profiles: list[dict] = []
    with duckdb.connect(DUCKDB_PATH, read_only=True) as conn:
        columns = get_columns_to_profile(conn)
        print(f"  profiling {len(columns)} columns across {len(PROFILED_SCHEMAS)} schemas")
        for schema, table, column, col_type in columns:
            try:
                profile = profile_column(conn, schema, table, column, col_type, args.run_id)
                profiles.append(profile)
            except Exception as e:
                print(f"  ERROR: {schema}.{table}.{column}: {e}", file=sys.stderr)

    with duckdb.connect(DUCKDB_PATH) as conn:
        conn.execute(DDL)
        for p in profiles:
            conn.execute("""
                INSERT INTO main_admin.fct_column_profile_raw (
                    profile_id, profiled_at, run_id,
                    schema_name, table_name, column_name, column_type,
                    row_count, non_null_count, null_count, null_pct, distinct_count,
                    min_value, max_value, mean_value,
                    p25_value, p50_value, p75_value, p95_value,
                    zero_count, negative_count,
                    min_date, max_date, span_days,
                    min_length, max_length, avg_length,
                    empty_string_count, top_5_values,
                    true_count, false_count
                ) VALUES (
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?
                )
            """, (
                p["profile_id"], p["profiled_at"], p["run_id"],
                p["schema_name"], p["table_name"], p["column_name"], p["column_type"],
                p["row_count"], p["non_null_count"], p["null_count"], p["null_pct"], p["distinct_count"],
                p["min_value"], p["max_value"], p["mean_value"],
                p["p25_value"], p["p50_value"], p["p75_value"], p["p95_value"],
                p["zero_count"], p["negative_count"],
                p["min_date"], p["max_date"], p["span_days"],
                p["min_length"], p["max_length"], p["avg_length"],
                p["empty_string_count"], p["top_5_values"],
                p["true_count"], p["false_count"],
            ))

    finished = datetime.now(timezone.utc).replace(tzinfo=None)
    elapsed = (finished - started).total_seconds()
    print(f"  wrote {len(profiles)} profile rows in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
