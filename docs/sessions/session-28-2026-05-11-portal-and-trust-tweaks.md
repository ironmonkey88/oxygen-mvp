---
session: 28
date: 2026-05-11
start_time: 22:00 ET
end_time: 23:15 ET
type: code
plan: none
layers: [portal, docs]
work: [feature, bugfix, docs]
status: complete
---

## Goal

Small portal polish: flip Sonnet refs to Opus (model migration landed Session 26 but portal HTML wasn't synced), add last-data-date + last-pipeline-run stats to the front page, widen the `/trust` Test Results table (was clipping the Expected column). Also: research a Somerville wards map as hero background and either ship or document as follow-up.

## What shipped

- **Portal Sonnet → Opus refs** ([`portal/index.html`](../../portal/index.html)) — three replacements:
  - "Built on Oxygen" prose: "backed by Claude Sonnet 4.6" → "backed by Claude Opus 4.7"
  - Stack-detail row: "Claude Sonnet" → "Claude Opus"
  - Stack-tool row: "Claude Sonnet 4.6" → "Claude Opus 4.7"
- **Portal stats bar gains two new entries**: `2026-05-09 / Last data point` (MAX(`date_created_dt`) from gold fact) and `2026-05-11 / Last pipeline run` (most recent `run_at` from `main_admin.fct_test_run`). Grid changed from fixed 4-column to responsive `repeat(auto-fit, minmax(180px, 1fr))` so the 6 stats wrap cleanly on narrower viewports. `.stat` gains a bottom border so wrapped rows don't orphan visually. Values currently **hardcoded**; auto-refresh from DuckDB on `run.sh` queued as a follow-up in TASKS.md.
- **Trust page `/trust` table widening** ([`scripts/generate_trust_page.py`](../../scripts/generate_trust_page.py)) — done in two passes:
  - First pass (commit `4dd2909`): `section { max-width: 1100px → 1400px }`. Still appeared truncated.
  - Second pass (commit `afd009a`): max-width 1400 → 1600; added visible thin scrollbar styling (`scrollbar-width: thin` + webkit pseudo-elements) since macOS hides scrollbars by default; switched `.test-id` and `.mono` from `white-space: nowrap` to `word-break: break-all` so long test IDs wrap inside their column. The Test Results table has 7 columns (Status / Test / Target / Actual / Expected / Variance / Message), not the 4-5 visible in the initial truncation report.
- **Deploys**: `portal/index.html` synced to `/var/www/somerville/index.html` on EC2 via scp + cp; trust page regenerated via `.venv/bin/python scripts/generate_trust_page.py` then deployed. Verified live via curl.
- **TASKS.md** — MVP 1.5 row marked `[x]` for portal polish; two follow-ups queued: auto-refresh dates, Somerville wards map.

## Decisions

- **Hardcoded stats dates rather than wiring run.sh auto-substitution.** Auto-update via Python script + run.sh step would have been the durable solution but adds workflow weight for a "small tweak" ask. Hardcoded dates suffice for the next pipeline-run cycle; auto-refresh queued as TASKS.md follow-up so the next time `./run.sh` runs, this gets revisited deliberately rather than left to drift.
- **Word-break: break-all over min-width approach for the trust table.** Could have set `.tests-table { min-width: 1400px }` to force horizontal scroll. Chose word-break instead so long test IDs (`baseline.dim_request_type.all.row_count` — 42 chars) wrap inside their column rather than forcing the column wide. Visible scrollbar still present for the cases where 7 columns of content exceed the section width on a narrow viewport.
- **Somerville wards map deferred to a focused pass.** The Socrata wards dataset (`ym5n-phxd`) is a "blobby" view (no GeoJSON export — backend rejects with `Unexportable view type: blobby`). OpenStreetMap Overpass API queries returned HTML errors on first attempts (mixed results across queries — likely query-shape issues, not API outage). Pragmatic next-pass options documented in TASKS.md: trace the city's PDF (`https://www.somervillema.gov/sites/default/files/ward-and-precinct-map.pdf`), pull from MassGIS shapefiles with `geopandas`, or render a simpler Somerville municipal-boundary SVG as decorative rather than precise. Estimated 30-60 min focused work.

## Issues encountered

### Trust table truncation appeared to persist after first widening

After commit `4dd2909` (section 1100 → 1400) Gordon screenshot showed the table still clipping at the Expected column. Three contributing factors discovered in the diagnosis:

1. The table has 7 columns, not the 4-5 visible. Status / Test / Target / Actual / Expected / Variance / Message.
2. macOS hides scrollbars by default. `overflow-x: auto` was working — table content was horizontally scrollable — but the absent scrollbar made the truncation look like a hard wall.
3. `.test-id { white-space: nowrap }` forced the Test column wider than necessary for long mono strings.

Three-part fix landed in `afd009a`: max-width 1600, visible scrollbar styling (cross-browser), word-break break-all on mono columns.

### Wards map sources don't give what we want easily

The Socrata dataset's metadata page suggests "GeoJSON" availability but the backend rejects `format=GeoJSON` exports because the view is a "blobby" type (presumably a PDF wrapper, not a queryable spatial table). The standard SODA row-fetch (`.json`) returns "Non-tabular datasets do not support rows requests." OSM Overpass first query returned 89KB but hit Alabama's Somerville; bbox-narrowed query returned an HTML error response (likely query syntax issue under the cited Overpass version).

Documented sources in TASKS.md follow-up so the next focused pass starts from known dead-ends rather than retracing.

## Next action

MVP 2 plan-scoping (per TASKS.md Next Focus). MVP 1.5 hardening complete except for the two queued follow-ups (auto-refresh dates, wards map). Active MVP is MVP 2 — Visual Knowledge Products. Builder Agent in `--local` mode, first Data App scope, semantic-layer additions are the open questions.
