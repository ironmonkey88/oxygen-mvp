---
id: portal-deploy-file-ownership
title: run.sh's portal-deploy stages fail when /var/www files are root-owned
severity: warning
affects:
  - deploy.run_sh
  - profile.html
  - erd.html
since: 2026-05-13
status: active
---

# run.sh's portal-deploy stages fail when /var/www files are root-owned

`./run.sh` (and the systemd `pipeline-refresh.service` that wraps it) runs
as user `ubuntu`. Stages 7 (`/metrics`), 8 (`/trust`), 9d (`/profile`),
and 9e (`/erd`) deploy generated portal pages to `/var/www/somerville/`
using plain `cp` (no sudo). When a target file is root-owned, the `cp`
fails with `Permission denied` and the ERR trap halts the run with
`status=failed` at the failing stage.

## Surface

- Daily run at 2026-05-13 10:00 UTC (`01KRGCF7Y18QZCXX1X2NK65ZT9`)
  failed at `profile_page` for this reason. The pre-existing daily-runs-
  landing-`partial` pattern (Session 31 carry-forward — drift-fail
  guardrail) was masking this; today's runs flipped from `partial` to
  `failed`.
- Manual `./run.sh` invoked during Plan 12 Phase 3 verification
  (2026-05-13 14:24 UTC, `01KRGVJQ26GQXNFNRT4FA0ZHW4`) failed at the
  same stage. Manual `sudo chown ubuntu:ubuntu /var/www/somerville/
  profile.html erd.html erd-warehouse.mmd erd-semantic-layer.mmd`
  restored ubuntu ownership; the follow-up rerun
  (`01KRGWG8N51MHZX09SX4Z61J6G`) completed past that stage.

## Root cause

A `sudo cp` somewhere — most likely during initial Plan 1b deploy or
during a manual portal regen — flipped the file ownership to root.
Once root-owned, ubuntu's plain `cp` cannot overwrite. The other
ubuntu-owned files (index.html, metrics.html, trust.html) continued to
update fine because they were written by `cp` (not `sudo cp`) in
previous runs and stayed ubuntu-owned.

## Workaround

`sudo chown ubuntu:ubuntu /var/www/somerville/*.html
/var/www/somerville/*.mmd` whenever the pattern recurs. Adding a
preflight chown to `./run.sh` would mask the problem rather than fix
it; better to find the upstream cause.

## Resolution path

Three options, decided at a follow-up plan kickoff:

1. **Switch run.sh's portal-deploy stages to `sudo cp`** with a sudoers
   rule for `cp` to `/var/www/somerville/*`. Consistent with the
   sudo-nginx pattern already in run.sh. Most aligned with the
   opportunistic-principle's "what produces a better analyst experience"
   test — analyst doesn't care; consistency wins.
2. **Make `/var/www/somerville/` group-writable for the `ubuntu` group**
   with the right setgid permissions. Cleaner long-term, but the OS-
   level perms drift if anything else writes there.
3. **Run pipeline-refresh.service as root.** Simplest, but expands the
   blast radius of any run.sh bug.

No urgency overnight; the daily runs will keep failing at this stage
until one of these lands. Queued as a follow-up plan.
