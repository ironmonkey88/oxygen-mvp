---
id: drift-fail-current-year-baseline-unstable
title: Current-year row-count baselines are structurally unstable; deactivated by design
severity: info
affects:
  - main_admin.dim_data_quality_test
  - main_admin.fct_test_run
  - dq_drift_fail_guardrail
since: 2026-05-13
status: active
---

# Current-year row-count baselines are structurally unstable; deactivated by design

The `dim_data_quality_test` model auto-seeds a per-year row-count
baseline for `main_bronze.raw_311_requests` for every year present in
the source (2015 → current). For closed years (2015–2025), the row
counts are stable; a baseline + 1% tolerance is sound.

For the **current year**, the row count grows indefinitely until
year-end — every day adds new 311 requests. A baseline certified
mid-year at a partial count trips the 1% tolerance after a few days
of normal ingestion. The `dq_drift_fail_guardrail` singular test
then fires on each pipeline run, landing `./run.sh` as `partial`.

## Diagnosis (2026-05-13)

`baseline.raw_311_requests.year_2026.row_count` certified 2026-05-08
22:04 UTC at `expected_value = 49416`. Actual on 2026-05-13:
`50954`. Variance: 3.11% — over the 1% tolerance. Every daily run
between 2026-05-08 and 2026-05-13 landed `partial` because of this
single test (12/13 admin tests PASS, 1 fail = drift-fail).

The pattern is structural, not a data-quality issue. The pipeline
is working correctly; the test was the wrong shape.

## Fix (Plan 14a, 2026-05-13)

Two parts:

1. **Surgical UPDATE:** `is_active = false` for the year_2026 row in
   `dim_data_quality_test`. `fct_test_run` left-joins
   `dim_data_quality_test` with `is_active = true`; inactive
   baselines produce NULL expected, which the model treats as
   status='warn' (not 'fail'). `dq_drift_fail_guardrail` only fires
   on `status='fail'` — so warn rows are silent.
2. **Model update:** `dbt/models/admin/dim_data_quality_test.sql`
   `baselines_yearly` CTE now sets `is_active = (year != extract(year
   from current_date)::integer)`. Future current-year rows land
   inactive; stable historical years stay active baselines. The
   existing `is_incremental()` filter protects already-frozen
   baseline rows.

## Verification

After the fix, `./run.sh manual` lands `run_status=success`, exit 0.
13/13 admin tests PASS (was 12/13 ERROR). First successful run since
Session 31's flagging of the issue.

## Workaround for future-Code

When a new year rolls over (e.g., 2027 starts):

- The model's `is_active = (year != current_year)` logic will make
  the new year_2027 row inactive on first run.
- The previously-current year_2026 row stays inactive (frozen by the
  incremental filter; the UPDATE we did is persistent).
- **Manual re-certification recommended.** When a year closes, the
  analyst should certify the now-stable baseline:
  ```sql
  UPDATE main_admin.dim_data_quality_test
  SET is_active = true,
      expected_value = (
          SELECT COUNT(*)::VARCHAR
          FROM main_bronze.raw_311_requests
          WHERE EXTRACT(YEAR FROM date_created::timestamp) = 2026
      ),
      certified_at = NOW(),
      certified_by = 'manual_re_certification'
  WHERE test_id = 'baseline.raw_311_requests.year_2026.row_count'
  ```
  This is a once-per-year operation; queue it as a calendar task or
  add to a January operations checklist.

## Why not auto-certify on year-close

Possible, but not done in Plan 14a:

- A simple year-end heuristic in the model (e.g.,
  `is_active = (year < current_year)` AND grandfathered for the new
  current year) would auto-handle the transition. But it would
  re-certify the baseline value automatically, which loses the
  intentional "human reviewed this" signal of a manual baseline.
- Plan 14a chose: deactivate current year automatically; require a
  human to reactivate. Pattern preserves the existing baseline-as-
  human-decision posture. Revisit if calendar-year churn becomes
  ops-friction.

## Resolution path

No resolution needed — the pattern works as designed. This entry
exists so future Code understands why year_2026 (and any future
current-year row) is intentionally inactive in
`dim_data_quality_test`.
