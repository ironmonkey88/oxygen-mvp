"""Record pipeline run completion in main_admin.fct_pipeline_run_raw.

Updates the row created by pipeline_run_start.py. Run.sh calls this twice in
the success path (no, once) and from the failure trap (with --status=failed
and --error-stage / --error-message set).

Usage:
    scripts/pipeline_run_end.py --run-id RUN --status success [extra flags]
"""
import argparse
import sys
from datetime import datetime, timezone

import duckdb

DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--status", required=True,
                   choices=["success", "partial", "failed"])
    p.add_argument("--error-stage", default=None)
    p.add_argument("--error-message", default=None)

    p.add_argument("--records-fetched", type=int, default=None)
    p.add_argument("--records-new", type=int, default=None)
    p.add_argument("--records-updated", type=int, default=None)

    p.add_argument("--source-rows-updated-at", default=None,
                   help="ISO timestamp of Socrata `rowsUpdatedAt` at run time")
    p.add_argument("--source-row-count", type=int, default=None)
    p.add_argument("--source-freshness-lag-sec", type=int, default=None)

    p.add_argument("--bronze-status", default=None)
    p.add_argument("--bronze-test-count", type=int, default=None)
    p.add_argument("--bronze-test-failures", type=int, default=None)
    p.add_argument("--gold-status", default=None)
    p.add_argument("--gold-test-count", type=int, default=None)
    p.add_argument("--gold-test-failures", type=int, default=None)
    p.add_argument("--admin-status", default=None)
    p.add_argument("--admin-test-count", type=int, default=None)
    p.add_argument("--admin-test-failures", type=int, default=None)

    args = p.parse_args()
    completed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    with duckdb.connect(DUCKDB_PATH) as conn:
        row = conn.execute(
            "SELECT run_started_at FROM main_admin.fct_pipeline_run_raw WHERE run_id = ?",
            (args.run_id,),
        ).fetchone()
        if not row:
            sys.stderr.write(f"ERROR: run_id {args.run_id} not found\n")
            sys.exit(1)
        duration_sec = int((completed_at - row[0]).total_seconds())

        src_updated = None
        if args.source_rows_updated_at:
            src_updated = datetime.fromisoformat(
                args.source_rows_updated_at.replace("Z", "+00:00")
            ).replace(tzinfo=None)

        conn.execute(
            """
            UPDATE main_admin.fct_pipeline_run_raw
            SET run_completed_at = ?,
                run_duration_seconds = ?,
                run_status = ?,
                error_stage = ?,
                error_message = ?,
                records_fetched = COALESCE(?, records_fetched),
                records_new = COALESCE(?, records_new),
                records_updated = COALESCE(?, records_updated),
                source_rows_updated_at = COALESCE(?, source_rows_updated_at),
                source_row_count = COALESCE(?, source_row_count),
                source_freshness_lag_sec = COALESCE(?, source_freshness_lag_sec),
                bronze_status = COALESCE(?, bronze_status),
                bronze_test_count = COALESCE(?, bronze_test_count),
                bronze_test_failures = COALESCE(?, bronze_test_failures),
                gold_status = COALESCE(?, gold_status),
                gold_test_count = COALESCE(?, gold_test_count),
                gold_test_failures = COALESCE(?, gold_test_failures),
                admin_status = COALESCE(?, admin_status),
                admin_test_count = COALESCE(?, admin_test_count),
                admin_test_failures = COALESCE(?, admin_test_failures)
            WHERE run_id = ?
            """,
            (
                completed_at, duration_sec, args.status,
                args.error_stage, args.error_message,
                args.records_fetched, args.records_new, args.records_updated,
                src_updated, args.source_row_count, args.source_freshness_lag_sec,
                args.bronze_status, args.bronze_test_count, args.bronze_test_failures,
                args.gold_status, args.gold_test_count, args.gold_test_failures,
                args.admin_status, args.admin_test_count, args.admin_test_failures,
                args.run_id,
            ),
        )

    sys.stderr.write(
        f"run {args.run_id} → {args.status} ({duration_sec}s)\n"
    )


if __name__ == "__main__":
    main()
