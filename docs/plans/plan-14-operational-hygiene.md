# Plan 14 — Operational Hygiene

**Status:** done, Session 40 (2026-05-13).
**Type:** plan-and-execute. Three small operational fixes bundled into
one plan + PR.

## Why this plan exists

Three operational issues accumulated through MVPs 1 → 13 that block
clean daily operation and clean reporting:

1. **`./run.sh` lands `partial` every day** because
   `dq_drift_fail_guardrail` fires on a year_2026 baseline that's
   structurally unstable (certified mid-year at a partial count;
   grows past tolerance within days). Session 31 flagged it as
   carry-forward; no plan addressed it until now.
2. **Portal deploys break intermittently** when a stray `sudo cp`
   flips a target file to root ownership, blocking ubuntu's
   subsequent plain `cp`. Plan 12 close documented the symptom but
   only chowned the affected files as a one-time fix.
3. **LOG.md is 303 lines** — over the 250 hard ceiling since the
   retrospective (Session 31). Four sessions of accumulated decisions
   without a compression pass.

All three are operational debt — none block product progress, but
each adds friction that compounds over time. Plan 14 closes the
debt.

## Scope

Three sections; one PR.

### 14a — Drift-fail baseline re-anchor

**Diagnosis** (from `main_admin.fct_test_run`):

- The failing test in every recent run is
  `baseline.raw_311_requests.year_2026.row_count`.
- Baseline was certified 2026-05-08 22:04 UTC at `expected_value =
  49416` with `tolerance_pct = 1%`.
- Current actual: 50,954 (and growing daily).
- Variance: 3.11% — over the 1% tolerance.
- All other 11 yearly baselines (2015 through 2025) pass within
  tolerance and are structurally stable (closed years).

**Root cause.** A current-year baseline is not stable. Every day new
311 requests are filed for the current year; the row count grows
indefinitely until year-end. A 1% tolerance trips after a few days of
normal ingestion. The baseline was correctly seeded at the time of
certification — the design didn't anticipate that current-year rows
shouldn't be baselined.

**Fix.** Two parts:

1. Surgical UPDATE on `dim_data_quality_test`:
   ```sql
   UPDATE main_admin.dim_data_quality_test
   SET is_active = false
   WHERE test_id = 'baseline.raw_311_requests.year_2026.row_count'
   ```
   The fct_test_run model's `LEFT JOIN ... AND d.is_active = true`
   excludes inactive baselines; the test row's `expected_value` comes
   back NULL; the model's CASE evaluates NULL → status='warn' (not
   fail); the `dq_drift_fail_guardrail` singular test only fires on
   `status='fail'` rows.
2. Update `dbt/models/admin/dim_data_quality_test.sql` so future
   runs don't recreate the trap: `is_active = (year !=
   extract(year from current_date)::integer)`. The
   `is_incremental()` filter still protects already-frozen baselines;
   the new logic applies to any year that hasn't yet been baselined
   (e.g., when 2027 rolls in, year_2026 will be a NEW row landing as
   active; year_2027 will land as inactive; the existing year_2026
   row stays inactive even though the model would otherwise mark it
   active, because the incremental filter blocks re-emission).

A new limitation entry,
[`drift-fail-current-year-baseline-unstable`](../limitations/drift-fail-current-year-baseline-unstable.md),
documents the pattern so future-Code understands the design choice.

### 14b — Portal-deploy ownership durable fix

**Diagnosis.** Plan 12 close documented the symptom in
`docs/limitations/portal-deploy-file-ownership.md`: when a target
file under `/var/www/somerville/` becomes root-owned (e.g., from a
manual `sudo cp` during a session), the next `./run.sh`'s plain
`cp` from the systemd `ubuntu` user fails with permission denied.
Three resolution paths were named: switch `run.sh` to `sudo cp`,
setgid the directory, or run pipeline-refresh as root.

**Fix chosen.** Option A (switch `run.sh` to use `sudo`) variant: a
self-healing `deploy_html` helper near the top of `run.sh`:

```bash
deploy_html() {
    local src="$1" dst="$2"
    if [ -e "$dst" ] && [ ! -w "$dst" ]; then
        sudo chown ubuntu:ubuntu "$dst" 2>/dev/null || true
    fi
    cp "$src" "$dst"
}
```

Replaces 5 inline `cp portal/X /var/www/somerville/X` sites in
`run.sh` (metrics, trust, index, profile, erd). Sudoers already
allows ubuntu passwordless sudo for chown (verified
`sudo -n chown ubuntu:ubuntu /var/www/somerville/index.html` exits 0
on EC2). Resilient: even if a stray `sudo cp` flips a file to root
ownership tomorrow, the next `./run.sh` recovers automatically.

No reboot test needed — the helper runs on every pipeline pass; the
daily systemd timer exercises it daily. End-to-end verification in
this plan's session note confirms it works.

### 14c — LOG.md compression pass

**Approach.** Move all 2026-05-07 through 2026-05-09 Active Decisions
rows (104 rows covering MVP 1 foundation + Plans 0 through 9 rev 2)
to `docs/log-archive.md`. Keep 2026-05-10 onwards visible.

**Why aggressive (vs the strict 30-day rotation rule).** The strict
rule says "older than 30 days." Today is 2026-05-13; the oldest rows
are 2026-05-07 = 6 days old. Strict rule wasn't triggering. But the
project's volume of decisions per day is high (10–30 rows added per
plan kickoff). 4 sessions of accumulated decisions without rotation
puts LOG.md over the 250-line ceiling. The pragmatic cut for this
compression pass: "MVP 1 era decisions are stable enough to archive,
regardless of calendar age." Pattern recorded in `log-archive.md`'s
intro.

**Result.** LOG.md compressed 303 → 198 lines. Active Decisions
section starts at 2026-05-10 with the post-MVP-1 era decisions
visible.

## Sign-off gates (all met)

- [x] **14a:** `./run.sh manual` lands `run_status=success`, exit 0.
  13/13 admin tests PASS. Verified end-to-end Session 40
  (run_id captured in session note).
- [x] **14b:** `deploy_html` helper in `run.sh`; sudoers allows
  ubuntu passwordless chown; end-to-end pipeline run completes
  cleanly without permission-denied at any of the 5 portal-deploy
  sites.
- [x] **14c:** LOG.md under 250 lines. 104 rows moved to log-archive
  with rationale recorded.

## Out of scope

- Re-anchoring the closed-year baselines (2015–2025). All 11 are
  passing within tolerance and structurally stable; no change needed.
- Other limitations / decisions older than 30 days. Plan 14c only
  archived MVP 1 era; later compression passes can be more
  fine-grained if needed.
- Reboot test for 14b. The deploy_html runs on every pipeline pass;
  the next daily 6 AM EDT run exercises it.
