#!/usr/bin/env bash
# run.sh — single entry point for the Somerville 311 pipeline.
# See ARCHITECTURE.md for run order rationale.
#
# Order:
#   1. dlt ingest        — Somerville 311 SODA API → Parquet
#   2. dbt run bronze gold
#   3. dbt test bronze gold (capture exit; do NOT halt)
#   4. dlt load_dbt_results — append run_results.json into raw_dbt_results_raw
#   5. dbt run admin     — fct_data_profile, dim_data_quality_test, fct_test_run
#   6. dbt docs generate — keep /docs current
#   7. /metrics page     — regenerate from semantics/views/*.view.yml
#
# Exit code: the captured dbt-test exit. Tests can fail without losing
# admin tables (which is the whole point of capturing run_results).

set -euo pipefail

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$REPO_ROOT"

# Activate venv (dbt, dlt, duckdb live here)
# shellcheck disable=SC1091
source "$REPO_ROOT/.venv/bin/activate"

echo "==> 1/7 dlt ingest somerville 311"
python dlt/somerville_311_pipeline.py

echo "==> 2/7 dbt run --select bronze gold"
( cd dbt && dbt run --select bronze gold )

echo "==> 3/7 dbt test --select bronze gold (capture exit, do not halt)"
set +e
( cd dbt && dbt test --select bronze gold )
DBT_TEST_EXIT=$?
set -e
echo "    dbt test exit code: $DBT_TEST_EXIT"

echo "==> 4/7 dlt load_dbt_results"
python dlt/load_dbt_results.py

echo "==> 5/7 dbt run --select admin"
( cd dbt && dbt run --select admin )

echo "==> 5b/7 dbt test --select admin (drift-fail guardrail; capture exit, do not halt)"
set +e
( cd dbt && dbt test --select admin )
DBT_ADMIN_TEST_EXIT=$?
set -e
echo "    dbt admin-test exit code: $DBT_ADMIN_TEST_EXIT"

echo "==> 6/7 dbt docs generate"
( cd dbt && dbt docs generate )

echo "==> 7/7 generate /metrics page"
python scripts/generate_metrics_page.py
if [ -d /var/www/somerville ]; then
    cp portal/metrics.html /var/www/somerville/metrics.html
    echo "    deployed to /var/www/somerville/metrics.html"
fi

echo
echo "===== run complete ====="
echo "    dbt test exit code (bronze/gold): $DBT_TEST_EXIT"
echo "    dbt test exit code (admin):       $DBT_ADMIN_TEST_EXIT"
# Final exit is the larger of the two captured exits — any failure surfaces.
FINAL_EXIT=$DBT_TEST_EXIT
if [ "$DBT_ADMIN_TEST_EXIT" -gt "$FINAL_EXIT" ]; then FINAL_EXIT=$DBT_ADMIN_TEST_EXIT; fi
echo "    final exit code:                  $FINAL_EXIT"
exit $FINAL_EXIT
