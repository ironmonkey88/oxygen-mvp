# Prompt -- Green pipeline, box deploys from git, query endpoint live, alerts

**Kind:** coding
**Date:** 2026-10-23
**Scope:** `run.sh`, `dbt/models/gold/fct_crime_incidents*`, `dbt/models/admin/` drift baselines, `systemd/`, `nginx/somerville.conf`, `.gitignore` + generated `portal/` files, PR #93 (`mcp/`, `scripts/build_ro_snapshot.py`), `ironmonkey88/wong-way-server` PR #2; the live box (`ubuntu@100.112.46.36`, `~/oxygen-mvp`)
**Effort:** 1 session, about 3-4 hours
**Depends on:** #92 (warehouse lock, merged), #93 (MCP server, open), #94 (dbt Charts boards, merged)

---

## Outcome (required)

Somerville Civic Pulse refreshes itself every morning and says so honestly,
what runs on the server is exactly what is in GitHub, and Claude can query the
warehouse live. Today three things are quietly wrong: the daily refresh has
been marked failed since Oct 21 even though the data loads, so the query
snapshot stopped updating on Oct 20; the server runs a June checkout patched by
hand, so the repo and the box disagree (the repo's nginx config would break the
live site if redeployed); and the query endpoint Code built on Oct 12 was never
switched on. After this prompt a reader of the portal, Gordon, and the Claude
Dashboard all see current data, and the next drift or failure raises an alert
instead of waiting for an audit.

## Context (conditional)

Audit by Cowork, 2026-10-23 (read-only, over Tailscale SSH):

- `pipeline-refresh` ended `run_status: partial`, exit 1, on Oct 21, 22 and 23.
  Failing tests on Oct 23: `not_null_fct_crime_incidents_multi_offense_flag`,
  `..._offense_category`, `..._offense_code` (1 row each) and
  `dq_drift_fail_guardrail` (FAIL 3). Bronze/gold data still loaded.
- `civic-pulse-snapshot.service` is wired by `OnSuccess=` on `pipeline-refresh`,
  so `/srv/civic-pulse/somerville_ro.duckdb` is still dated Oct 20.
- Box checkout: HEAD `50ca146` (PR #85), 22 commits behind `origin/main`, with
  main's later files copied in by hand. `git diff origin/main` on the box shows
  real drift only in `nginx/somerville.conf` (box: `listen 127.0.0.1:8080`,
  `absolute_redirect off`, no `auth_basic`; repo: `listen 80` + Basic Auth) and
  in generated files (`portal/index.html`, `portal/erd-tier-*.mmd`,
  `docs/limitations/_index.yaml`). Untracked on the box: `charts/`,
  `dbt_charts.yml`, `scripts/render_boards.sh`, `scripts/build_ro_snapshot.py`,
  `systemd/dbt-charts-boards.*` (all now in main except the snapshot script,
  which is in #93).
- PR #93: `mcp/` server code is not on the box, no container runs it, and the
  Caddyfile (`/opt/wong-way-server/Caddyfile`) has no `/mcp` route.
  `https://somerville.thewongway.co/mcp` returns 404.
- Server pattern (Gordon, 2026-09-09): Caddy + Docker Compose from
  `ironmonkey88/wong-way-server`, pull-based deploys (`wong-way-deploy.timer`),
  healthchecks.io as the one monitoring dashboard.

Gordon's decisions, 2026-10-23:
1. A `partial` run counts as success to systemd, with an alert.
2. The box pulls `main` automatically before each pipeline run.

## Work (required)

**Phase 0 -- Back up (before touching anything).**
Tar into `~/backups/2026-10-23/`: the box's modified and untracked files under
`~/oxygen-mvp` (`git status --porcelain` list), `/etc/nginx/sites-available/somerville`,
`/etc/systemd/system/*.service`, `*.timer` and `*.service.d/`, and
`/opt/wong-way-server/Caddyfile`. Paste the file list into the report.

**Phase 1 -- Green pipeline.**
1. Find the crime incident(s) with NULL `offense_code` / `offense_category` /
   `multi_offense_flag`. If it's a gap in the gold model (an unmapped offense
   code, a join miss), fix the model. If the source genuinely sends it that
   way, keep the row, add a limitation in `docs/limitations/`, and change those
   tests to `severity: warn`. Do not drop the row silently.
2. Find the three `dq_drift_fail_guardrail` failures. Fix the baseline or the
   tolerance if it's an expected change (say why); fix the data if it isn't.
3. `run.sh`: exit 0 on `partial` (still recorded as `partial` in
   `fct_pipeline_run_raw`), non-zero only on a halted stage. Or, if a distinct
   code is cleaner, use one and add it to `SuccessExitStatus=` in
   `pipeline-refresh.service`. Either way `OnSuccess=` jobs must run after a
   partial.

**Phase 2 -- Box deploys from git.**
1. Commit the box's real nginx site config as `nginx/somerville.conf`.
2. Stop tracking files `run.sh` regenerates (`portal/index.html` sections,
   `portal/erd-*.mmd`, `docs/limitations/_index.yaml`, and any others you find)
   and add them to `.gitignore`. If a generated file must stay in git because
   nginx serves it from the repo, say so and leave it.
3. On the box, after Phase 0: bring `~/oxygen-mvp` to a clean `origin/main`
   (fetch, then check out main's tree; the hand-copied files already match main
   except nginx and generated files, covered above). No tree-wide destructive
   command until the backup exists and you have shown the diff that would be
   discarded.
4. Add a `git pull --ff-only origin main` step before the pipeline runs
   (`ExecStartPre=` in `pipeline-refresh.service`, as `ubuntu`, under the
   existing flock). A failed fast-forward must stop the deploy step and alert,
   not overwrite.
5. Install every unit file in `systemd/` from the repo copy and
   `systemctl daemon-reload`. Prefer symlinks into the repo or a single install
   script so the repo stays the source of truth; say which you chose.

**Phase 3 -- Query endpoint live.**
1. Rebase PR #93 on main, review, merge.
2. Run the MCP server as a Compose service in `wong-way-server` (it ships a
   Dockerfile), mounting `/srv/civic-pulse/` read-only. Merge and deploy
   `wong-way-server` #2 (or its successor) for the `/mcp` route. Keep the rate
   limit and request-size limit.
3. Re-run the acceptance checks from #93's handoff: MCP `initialize` +
   `tools/list` from the public internet; `SELECT count(*) FROM
   main_gold.fct_311_requests` matches `/trust`; a write
   (CREATE/INSERT/ATTACH/COPY) is refused; a runaway cross join stops at 15 s.

**Phase 5 -- Alerts.**
Add healthchecks.io checks (ping URLs in `/etc/wong-way/` or the existing env
file, not in git) for: `pipeline-refresh` (success ping; a `partial` run pings
`/fail` with the failing tests in the body), `civic-pulse-snapshot`, and
`dbt-charts-boards`. Grace periods sized to a daily job. Name each check so
Gordon can tell them apart.

## Verification (required)

Static:
- Phase 0 backup listed in the report.
- `nginx/somerville.conf` in main matches `/etc/nginx/sites-available/somerville`
  (`diff` empty).
- On the box: `git -C ~/oxygen-mvp status --short` is empty and
  `git rev-parse HEAD` equals `origin/main`.

Live-functional (re-runnable):
- `sudo systemctl start pipeline-refresh` finishes `Result=success`;
  `civic-pulse-snapshot` runs after it and the snapshot's mtime is today.
- `curl -s -o /dev/null -w '%{http_code}'` on
  `https://somerville.thewongway.co/`, `/trust`, `/boards/rat_complaints/`
  each returns 200.
- The `/mcp` acceptance checks above, outputs pasted.
- A trivial docs-only commit pushed to main reaches the box at the next
  pipeline run (or a manual `ExecStartPre` run), shown by `git log -1` on the box.
- Each healthchecks.io check has received at least one ping.
- The Oct 24 06:00 ET run is green (re-check the next session if it hasn't run yet).

## Halt conditions (conditional)

- The crime NULL rows turn out to be many (more than a handful) or a whole
  offense family: stop and report counts before choosing fix vs warn.
- The box's working tree holds a change that is NOT in main and is NOT nginx
  or a generated file: stop, list it, and ask.
- Any step would take the public portal down for more than a couple of
  minutes outside 06:00-07:00 ET.

## Out of scope (conditional)

- Swapping `/dashboards` from the Oxygen app to the dbt Charts board.
- Changing the answer agent's model or evals.
- SSH key pruning, the reboot, docs/LOG/TASKS tidy, Wong Way notes: Cowork
  did these on 2026-10-23 (Session 74). After that cleanup the box's
  `authorized_keys` holds `gordon-mac` and one `cowork-chief@...-2026-10-23`
  key; `~/oxygen-mvp-backup` and `~/oxygen-eval` are archived under
  `~/backups/`.

## Commit shape (required)

Plan 53. One PR on oxygen-mvp holding Phases 1, 2 and 5 (jointly needed to
make the box trustworthy); #93 merged on its own; the Caddy/Compose change as a
PR on wong-way-server. Report-back in
`docs/prompts/plan-53-green-pipeline-git-deploys-mcp-live.report.md`.
