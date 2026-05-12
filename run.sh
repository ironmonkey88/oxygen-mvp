#!/usr/bin/env bash
# run.sh — single entry point for the Somerville 311 pipeline.
# See ARCHITECTURE.md for run order rationale.
#
# Run types (first positional arg, default 'manual'):
#   daily    — invoked by systemd pipeline-refresh.service
#   manual   — invoked by a human
#   backfill — special historical reload
#
# Order:
#   0. record run start  — main_admin.fct_pipeline_run_raw, returns run_id
#   1. dlt ingest        — Somerville 311 SODA API → raw_311_requests_raw (merge on `id`)
#   2. dbt run bronze gold
#   3. dbt test bronze gold (capture exit; do NOT halt)
#   4. dlt load_dbt_results — append run_results.json into raw_dbt_results_raw
#   5. dbt run admin     — fct_data_profile, dim_data_quality_test, fct_test_run
#   5b. dbt test admin   — drift-fail guardrail (capture exit; do NOT halt)
#   6. dbt docs generate — keep /docs current
#   7. /metrics page     — regenerate from semantics/views/*.view.yml
#   8. /trust page       — regenerate from main_admin.fct_test_run
#   9. limitations index — regenerate docs/limitations/_index.yaml from .md frontmatter
#  10. record run end    — UPDATE fct_pipeline_run_raw with status + stage outcomes
#
# Exit code: max(bronze/gold-test exit, admin-test exit). Tests can fail
# without losing admin tables or the trust page (which is the whole point
# of capturing run_results before failing).

set -euo pipefail

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$REPO_ROOT"

# Activate venv (dbt, dlt, duckdb live here)
# shellcheck disable=SC1091
source "$REPO_ROOT/.venv/bin/activate"

RUN_TYPE="${1:-manual}"

# Step 0: record run start, capture run_id
RUN_ID=$(python scripts/pipeline_run_start.py --run-type="$RUN_TYPE")
echo "==> 0/10 pipeline run started: $RUN_ID ($RUN_TYPE)"

# Stage state — bash variables, updated as we go, written into run record on exit
BRONZE_STATUS="not_run"
GOLD_STATUS="not_run"
ADMIN_STATUS="not_run"
DBT_TEST_EXIT=0
DBT_ADMIN_TEST_EXIT=0
ERROR_STAGE="setup"

# Trap: any unhandled non-zero exit records the failure and bubbles up.
on_error() {
    local code=$?
    set +e
    python scripts/pipeline_run_end.py \
        --run-id="$RUN_ID" \
        --status=failed \
        --error-stage="$ERROR_STAGE" \
        --error-message="run.sh halted at stage $ERROR_STAGE with exit $code" \
        --bronze-status="$BRONZE_STATUS" \
        --gold-status="$GOLD_STATUS" \
        --admin-status="$ADMIN_STATUS"
    exit $code
}
trap on_error ERR

# Step 1: dlt ingest (full pull + merge on `id`)
ERROR_STAGE="dlt_ingest"
echo "==> 1/10 dlt ingest somerville 311"
python dlt/somerville_311_pipeline.py "$RUN_ID"

# Step 2: dbt run bronze + gold
ERROR_STAGE="dbt_run_bronze_gold"
echo "==> 2/10 dbt run --select bronze gold"
( cd dbt && dbt run --select bronze gold )
BRONZE_STATUS="success"
GOLD_STATUS="success"

# Step 3: dbt test bronze + gold (captured-exit; do not halt)
# Use `cmd || rc=$?` idiom rather than `set +e ; cmd ; set -e` — the latter
# was observed to trip the ERR trap on bash 5.x when the subshell exits
# non-zero; the `|| ...` form is exempt from errexit per POSIX.
ERROR_STAGE="dbt_test_bronze_gold"
echo "==> 3/10 dbt test --select bronze gold (captured)"
DBT_TEST_EXIT=0
( cd dbt && dbt test --select bronze gold ) || DBT_TEST_EXIT=$?
echo "    dbt test exit code: $DBT_TEST_EXIT"

# Step 4: load dbt run_results into raw_dbt_results_raw
ERROR_STAGE="load_dbt_results"
echo "==> 4/10 load dbt results"
python dlt/load_dbt_results.py

# Step 5: dbt run admin
ERROR_STAGE="dbt_run_admin"
echo "==> 5/10 dbt run --select admin"
( cd dbt && dbt run --select admin )
ADMIN_STATUS="success"

# Step 5b: dbt test admin (captured-exit; drift-fail guardrail)
ERROR_STAGE="dbt_test_admin"
echo "==> 5b/10 dbt test --select admin (captured)"
DBT_ADMIN_TEST_EXIT=0
( cd dbt && dbt test --select admin ) || DBT_ADMIN_TEST_EXIT=$?
echo "    dbt admin-test exit code: $DBT_ADMIN_TEST_EXIT"

# Step 6: dbt docs generate
ERROR_STAGE="dbt_docs"
echo "==> 6/10 dbt docs generate"
( cd dbt && dbt docs generate )

# Step 7: /metrics page
ERROR_STAGE="metrics_page"
echo "==> 7/10 generate /metrics page"
python scripts/generate_metrics_page.py
if [ -d /var/www/somerville ]; then
    cp portal/metrics.html /var/www/somerville/metrics.html
    echo "    deployed to /var/www/somerville/metrics.html"
fi

# Step 8: /trust page
ERROR_STAGE="trust_page"
echo "==> 8/10 generate /trust page"
python scripts/generate_trust_page.py
if [ -d /var/www/somerville ] && [ -f portal/trust.html ]; then
    cp portal/trust.html /var/www/somerville/trust.html
    echo "    deployed to /var/www/somerville/trust.html"
fi

# Sync the static portal index too — so nav changes land without a manual scp.
if [ -d /var/www/somerville ] && [ -f portal/index.html ]; then
    cp portal/index.html /var/www/somerville/index.html
    echo "    synced portal/index.html → /var/www/somerville/index.html"
fi

# Step 9: build limitations index
ERROR_STAGE="limitations_index"
echo "==> 9/10 build limitations index"
python3 scripts/build_limitations_index.py

# Step 10: record run end (success or partial depending on test exits)
ERROR_STAGE="run_end"
if [ "$DBT_TEST_EXIT" -ne 0 ] || [ "$DBT_ADMIN_TEST_EXIT" -ne 0 ]; then
    FINAL_STATUS="partial"
else
    FINAL_STATUS="success"
fi
echo "==> 10/10 record run end ($FINAL_STATUS)"
python scripts/pipeline_run_end.py \
    --run-id="$RUN_ID" \
    --status="$FINAL_STATUS" \
    --bronze-status="$BRONZE_STATUS" \
    --gold-status="$GOLD_STATUS" \
    --admin-status="$ADMIN_STATUS"

# Final exit code = larger of the two captured test exits
FINAL_EXIT=$DBT_TEST_EXIT
if [ "$DBT_ADMIN_TEST_EXIT" -gt "$FINAL_EXIT" ]; then FINAL_EXIT=$DBT_ADMIN_TEST_EXIT; fi

echo
echo "===== run complete ====="
echo "    run_id:                           $RUN_ID"
echo "    run_type:                         $RUN_TYPE"
echo "    dbt test exit code (bronze/gold): $DBT_TEST_EXIT"
echo "    dbt test exit code (admin):       $DBT_ADMIN_TEST_EXIT"
echo "    run_status:                       $FINAL_STATUS"
echo "    final exit code:                  $FINAL_EXIT"
exit $FINAL_EXIT
