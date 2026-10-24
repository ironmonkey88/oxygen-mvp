"""Print the dbt tests that failed or errored in a run_results.json, one per line.

run.sh calls this right after each `dbt test` step (later dbt commands overwrite
run_results.json) and collects the lines in data/run_status.txt, which
scripts/hc_ping.sh sends to healthchecks.io on a partial run (Plan 53).

Usage: failing_tests.py PATH_TO_RUN_RESULTS_JSON
"""
import json
import sys


def main() -> int:
    try:
        with open(sys.argv[1]) as f:
            results = json.load(f).get("results", [])
    except (OSError, ValueError, IndexError) as exc:
        print(f"(could not read dbt run_results: {exc})")
        return 0
    for r in results:
        if r.get("status") in ("fail", "error"):
            # unique_id is test.<project>.<test_name>.<hash>
            uid = r.get("unique_id", "?")
            parts = uid.split(".")
            name = parts[2] if len(parts) >= 3 else uid
            print(f"{r['status'].upper()} {name} ({r.get('failures') or 0} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
