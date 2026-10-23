---
session: 73
date: 2026-10-20
start_time: 15:51 ET
end_time: 15:00 ET
type: code
plan: none
layers: [portal, infra, docs]
work: [feature, infra, docs]
status: complete
---

## Goal
Port the rat-complaints Oxygen Data App to dbt Charts as the first step in replacing Oxygen's dashboard layer (Gordon, 2026-10-20: "We can slowly replace the oxygen code. It's not being actively developed any more").

## What shipped
- `dbt_charts.yml`: dbt Charts project root; one `somerville` DuckDB source on `./data/somerville.duckdb` (opened read-only by dct).
- `charts/meta.yml`: shared defaults (source, `paper` theme, single-column prose).
- `charts/rat_complaints.yml`: port of `apps/rat_complaints_by_ward.app.yml`. Same SQL logic and DASHBOARDS.md shape: recent-situation layer (90-day KPI with change, weekly bars, ward over-representation), headline, ward equity (raw + per km²), time to close, trust footer.
- `scripts/render_boards.sh` + `systemd/dbt-charts-boards.{service,timer}`: renders every `charts/*.yml` to `/var/www/somerville/boards/<name>/index.html` daily at 06:45 ET under a shared `data/.warehouse.lock` (served by nginx's catch-all `location /`, no nginx change). A failed render leaves the previous page. (`d773b40` replaced the first draft's `run.sh` step 8e.)
- `.gitignore`: `data/boards/` (render output).
- 2026-10-23 deployed on the box: `dct` 0.10.0 in its own venv (`~/.local/share/dbt-charts`, linked at `~/.local/bin/dct`); the three board files, the script and both units copied in as new files; timer enabled; first run `Result=success`; `https://somerville.thewongway.co/boards/rat_complaints/` → 200 (871,917 bytes). Live data: 14,716 complaints, 362 in the last 90 days.
- Verified against a local warehouse built from today's Open Data pull: `dct validate` clean, zero render warnings, PNG reviewed. 14,703 rat complaints; 363 in the last 90 days (−19.3% vs prior 90).

## Decisions
- 90-day windows anchor to the newest request in the warehouse, not `CURRENT_DATE` — closes the "recent window is relative to data freshness" limitation the Oxygen app documented.
- Hard-coded counts in the Oxygen app's prose (14,036 total, 167 no-ward) replaced with query-driven KPIs so the board cannot go stale.
- `dct` installed in its own venv (`~/.local/share/dbt-charts`), not into `.venv` — dbt-charts 0.10.0 pins dbt-core 1.12 and must not move the pipeline's dbt.
- Own timer, not a `run.sh` stage or `OnSuccess=` — the box's `run.sh` has local changes on top of `50ca146` (not pulled from main), and `pipeline-refresh` exits 1 on a `partial` run (it did on 2026-10-23), which would also skip an `OnSuccess=` hook.
- Oxygen app and `/dashboards` listing left in place until Gordon compares the two.

## Issues encountered
- `dct` KPI `style.value.format` rejects strftime specs.
- Evidence: `ERR-FORMAT-INVALID Unknown number format '%Y-%m-%d %H:%M'`.
- Resolution: format the refresh timestamp in SQL (`STRFTIME`).
- The box's repo is not on main.
- Evidence: `git log -1` on the box = `50ca146` (PR #85) with 10 locally modified tracked files, `run.sh` among them.
- Resolution: deployed new files only, no `git pull`; flagged for a separate reconcile.

## Next action
Decide whether `/dashboards` links to `/boards/rat_complaints/` in place of the Oxygen app; separately, reconcile the box's working tree with main.
