# Report: Plan 53, green pipeline, box deploys from git, query endpoint live, alerts

**Date:** 2026-10-23 · **By:** Claude Code (Chief) · **PRs:** #93 (merged `0f1fde0`),
ironmonkey88/wong-way-server#2 (merged `96581a6`), #96 (this one: Phases 1, 2, 5)

## Outcome

- **Pipeline:** green. The 19:37 UTC run ended `Result=success`, `run_status: success`, exit 0.
- **Snapshot:** `civic-pulse-snapshot` ran after it via `OnSuccess=` and rebuilt the snapshot at 19:53 UTC.
- **Box checkout:** clean and tracking `origin/main`.
- **Query endpoint:** `https://somerville.thewongway.co/mcp` is live.
- **Alerts:** wired but silent. There are no healthchecks.io checks yet, so `hc_ping.sh` logs `HC_… not set`. See Open.

## Phase 0: backup

`~/backups/2026-10-23/plan53/` on the box:
- `oxygen-mvp-dirty.tgz`: the 37 paths from `git status --porcelain --untracked-files=all`, listed in `repo-files.txt`.
- `etc.tgz`: `/etc/nginx/sites-available/somerville`, every `/etc/systemd/system/*.service` and `*.timer`, `pipeline-refresh.service.d/`, and `/opt/wong-way-server/Caddyfile`.

Before checkout, every dirty or untracked box file was compared with `origin/main`:
- **Identical to main:** 31 files (all units, `run.sh`, admin models, charts, and the rest).
- **Generated:** `docs/limitations/_index.yaml`, `portal/erd-tier-gold.mmd`, `portal/index.html` (only the stat values differed: 1.18M→1.23M and similar), `portal/erd-tier-silver.mmd`, and `data/boards/`.
- **#93's file:** `scripts/build_ro_snapshot.py`, byte-identical to the PR.

No halt condition fired.

## Phase 1: green pipeline

1. **Crime NULLs.** One row: case `26066325` (2026-09-17, ward 3).
   - Socrata `aghs-hqvg` publishes it with no `offensecode`, `offense`, `offensetype` or `category`. `$where=offensecode IS NULL` returns 1, so the source sends it that way and it's not a model gap.
   - The row is kept and documented in `docs/limitations/crime-incidents-missing-offense.md`.
   - The three `not_null` tests use `warn_if: ">0"`, `error_if: ">10"`. A handful of source gaps warns, and a regression still fails.
2. **`dq_drift_fail_guardrail` FAIL 3.** These were the same three tests, recorded as `fail` in `fct_test_run`. dbt `warn` maps to `warn` there (`fct_test_run.sql`), and the guardrail keys on `fail`. Proven on a warehouse copy before deploy (PASS=10, WARN=3, ERROR=0), then live: admin tests exit 0.
3. **`run.sh` exit code.**
   - Exits 0 on `success` and on `partial`; the run is still recorded as `partial` in `fct_pipeline_run_raw`.
   - Only a halted stage exits non-zero.
   - Writes `data/run_status.txt` (status, run id, failing tests from `scripts/failing_tests.py`), which the alert reads.

## Phase 2: box deploys from git

1. **`nginx/somerville.conf`:** main already matched the live file (`48bae86`). `diff` against `/etc/nginx/sites-available/somerville` is empty.
2. **No longer tracked:**
   - `portal/erd-tier-*.mmd`;
   - `docs/limitations/_index.yaml` (the answer agent reads it, so `deploy_from_git.sh` rebuilds it after every deploy).

   **Still tracked, as templates:** `portal/index.html` and `portal/dashboards.html`. Their generators wrote into them in place; they now write to the gitignored `portal/build/`, and `run.sh` deploys from there.
3. **Box checkout:** `git checkout -f -B main 6fea069` (#96's tip, a descendant of `origin/main`), upstream `origin/main`. `git status --short` is empty before and after a full pipeline run. `_index.yaml` was rebuilt right away (35 entries).
4. **`scripts/deploy_from_git.sh`:** runs as `ExecStartPre=-` under the exclusive warehouse lock.
   - It does `git merge --ff-only origin/main`.
   - On failure it leaves the tree alone, writes `data/deploy_status.txt` (`failed: …` plus `git status`), and the pipeline runs on the current code. The status file makes the pipeline alert ping `/fail`.
   - Live: `ok 6fea069 -> 6fea069`.
5. **Unit install: copies, via `systemd/install.sh`, not symlinks.** A symlinked unit would change at the next reboot or `daemon-reload` with nobody looking. With copies, a pulled unit change takes effect only when someone runs `sudo systemd/install.sh`. The deploy step runs `install.sh --check` and reports drift as a failed deploy. Installed 2026-10-23: three units changed (`pipeline-refresh`, `civic-pulse-snapshot`, `dbt-charts-boards`), and `--check` is clean.

## Phase 3: query endpoint live

- **#93** merged with a merge commit, so wong-way-server's image pin `2391bd6` stays reachable from main.
- **wong-way-server#2** merged after resolving a conflict. Main's new `access-api` had taken `127.0.0.1:18438`, the port #2 used, and Caddy's `forward_auth` for every private site calls that port. MCP moved to **18441**. The container `civic-pulse-mcp:2391bd6` is up. The `/mcp` body limit (64 KB) and per-IP rate limit are unchanged.
- **Acceptance, from the public internet (2026-10-23 19:3x UTC):**

| Check | Result |
|---|---|
| `initialize` | `protocolVersion 2025-06-18`, `serverInfo.name civic-pulse-sql` |
| `tools/list` | `['query', 'list_tables', 'describe_table']` |
| `SELECT count(*) FROM main_gold.fct_311_requests` | `{"n": 1232404}`; `/trust` shows `1,232,404` |
| CREATE / INSERT / ATTACH / COPY | `only SELECT / WITH queries are allowed (got CREATE)`, `(got INSERT)`, `(got ATTACH)`, `(got COPY)` |
| `fct_311_requests` × itself | `query timed out after 15 s and was cancelled`, elapsed 15 s |

## Phase 5: alerts

- `scripts/hc_ping.sh KEY UNIT [STATUS_FILE…]` runs from `ExecStopPost=-` on `pipeline-refresh` (`PIPELINE_REFRESH`, with both status files), `civic-pulse-snapshot` (`CIVIC_PULSE_SNAPSHOT`) and `dbt-charts-boards` (`DBT_CHARTS_BOARDS`).
- It pings `/fail` on a failed unit, a `partial` run, a failed deploy or unit drift. The body holds the status files and the journal tail.
- URLs come from `/etc/wong-way/healthchecks.env` (`HC_<KEY>=https://hc-ping.com/<uuid>`, root:ubuntu 640). With no URL set, it logs a line and never fails the unit.

## Verification

| Check | Result |
|---|---|
| Backup listed | yes (above) |
| nginx repo = live | `diff` empty |
| Box tree clean | 0 lines, before and after the run |
| Box HEAD = `origin/main` | **not yet**: HEAD `6fea069` (#96), `origin/main` `0f1fde0`. Becomes true at the first run after #96 merges. |
| `pipeline-refresh` → success | `Result=success`, exit 0 (19:37 UTC run) |
| Snapshot ran after it, mtime today | `Result=success`; `/srv/civic-pulse/somerville_ro.duckdb` modified 2026-10-23 19:53 |
| `/`, `/trust`, `/boards/rat_complaints/` | 200, 200, 200 |
| `/mcp` acceptance | above |
| Docs-only commit reaches the box | **not yet**: needs #96 on main first |
| Each healthchecks.io check pinged | **not done**: no checks exist |
| Oct 24 06:00 ET run green | **not yet run**: re-check next session |
| `systemctl --failed` | empty |

## Open

1. **Merge #96.** The next `pipeline-refresh` then fast-forwards the box to `main`, and the "HEAD = origin/main" and docs-only-commit checks can be closed.
2. **healthchecks.io (Gordon).**
   - **Checks to create:** "Civic Pulse: pipeline-refresh", "Civic Pulse: snapshot" and "Civic Pulse: dbt Charts boards", each with a 1-day period and 2-hour grace.
   - **Install:** put the three ping URLs in `/etc/wong-way/healthchecks.env` as `HC_PIPELINE_REFRESH`, `HC_CIVIC_PULSE_SNAPSHOT` and `HC_DBT_CHARTS_BOARDS`, mode 640 root:ubuntu.
   - **Alternative:** give Chief a project API key and Chief creates them.
3. **Seen, out of scope:** `ss -ltn` shows `0.0.0.0:3000` (oxy) and `0.0.0.0:15432` listening on all interfaces. The EC2 security group allows only 80/443, so they are not public `[Likely]`, but they should bind to loopback.
