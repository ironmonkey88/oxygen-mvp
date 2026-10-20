---
session: 73
date: 2026-10-20
start_time: 15:51 ET
end_time: 16:05 ET
type: code
plan: none
layers: [portal, docs]
work: [feature, docs]
status: partial
---

## Goal
Port the rat-complaints Oxygen Data App to dbt Charts as the first step in replacing Oxygen's dashboard layer (Gordon, 2026-10-20: "We can slowly replace the oxygen code. It's not being actively developed any more").

## What shipped
- `dbt_charts.yml`: dbt Charts project root; one `somerville` DuckDB source on `./data/somerville.duckdb` (opened read-only by dct).
- `charts/meta.yml`: shared defaults (source, `paper` theme, single-column prose).
- `charts/rat_complaints.yml`: port of `apps/rat_complaints_by_ward.app.yml`. Same SQL logic and DASHBOARDS.md shape: recent-situation layer (90-day KPI with change, weekly bars, ward over-representation), headline, ward equity (raw + per km²), time to close, trust footer.
- `run.sh` step 8e: renders every `charts/*.yml` to static HTML and deploys to `/var/www/somerville/boards/<name>/index.html` (served by nginx's catch-all `location /`, no nginx change). Non-fatal: a render failure warns and leaves the previous board.
- `.gitignore`: `data/boards/` (render output).
- Verified against a local warehouse built from today's Open Data pull: `dct validate` clean, zero render warnings, PNG reviewed. 14,703 rat complaints; 363 in the last 90 days (−19.3% vs prior 90).

## Decisions
- 90-day windows anchor to the newest request in the warehouse, not `CURRENT_DATE` — closes the "recent window is relative to data freshness" limitation the Oxygen app documented.
- Hard-coded counts in the Oxygen app's prose (14,036 total, 167 no-ward) replaced with query-driven KPIs so the board cannot go stale.
- `dct` installed as an isolated tool (`uv tool install dbt-charts`), not into `.venv` — dbt-charts 0.10.0 pins dbt-core 1.12 and must not move the pipeline's dbt.
- Render runs inside `run.sh`, so it sits under the `data/.warehouse.lock` the pipeline already holds (PR #92); no separate lock handling.
- Oxygen app and `/dashboards` listing left in place until Gordon compares the two.

## Issues encountered
- `dct` KPI `style.value.format` rejects strftime specs.
- Evidence: `ERR-FORMAT-INVALID Unknown number format '%Y-%m-%d %H:%M'`.
- Resolution: format the refresh timestamp in SQL (`STRFTIME`).

## Next action
On the box: `uv tool install dbt-charts`, run `./run.sh` (or step 8e alone), confirm `https://somerville.thewongway.co/boards/rat_complaints/` renders; then decide whether `/dashboards` links to it in place of the Oxygen app.
