---
session: 43
date: 2026-05-14
start_time: 03:00 ET
end_time: 04:30 ET
type: code
plan: plan-15
layers: [portal, docs]
work: [feature, docs]
status: complete
---

## Goal

Refresh the portal homepage so a new analyst lands and immediately understands what's in the dataset, what's freshest, and what they can ask -- without hand-typing URLs. First session of the MVP 2 polish arc (Sessions 43-47).

## What shipped

- New "What's in the data" section: two topic cards (`service_requests` + `public_safety`) with row count, date range, key dim coverage, and per-topic active-limitation count linked to `/trust`
- New "What you can ask" section: six example questions linking to chat or dashboards
- Platform surfaces expanded 4 -> 7 cards (added `/dashboards`, `/profile`, `/erd`; chat + dashboards cards now fully clickable)
- Refreshed stale framing: nav badge MVP 1 -> MVP 2; hero subtitle now mentions 311 + crime; roadmap MVP 1 dim, MVP 2 current; "Out of scope for MVP 1: dashboards" removed; stack table "1.17M rows" -> "311 + crime"
- New generator [`scripts/generate_homepage_summary.py`](../../scripts/generate_homepage_summary.py): reads `fct_311_requests` + `fct_crime_incidents` + `dim_ward` + `fct_pipeline_run_raw` + `docs/limitations/*.md` frontmatter; rewrites two marker-bounded sections (`BEGIN_STATS`/`END_STATS`, `BEGIN_DATASET_CARDS`/`END_DATASET_CARDS`) in `portal/index.html`. ~200ms
- `run.sh` new stage 8b/10 between trust page and portal index sync
- Initial values populated on commit: 1.17M 311, 22.3K crime, 7 wards, 21 active limitations, latest data 2026-05-12, last run 2026-05-14 success
- PR [#6](https://github.com/ironmonkey88/oxygen-mvp/pull/6) opened; merged via stacked-merge as part of the Plans 15/16/17 batch

## Decisions

- **Marker-replacement, not full-regen.** Generator only rewrites between named HTML comment markers. The rest of `portal/index.html` stays hand-editable. Avoids the duplicate-CSS pain of full-regen (`generate_trust_page.py` pattern) for a page with substantial hand-built structure.
- **Per-topic limitation counts via affects-block parsing.** Counts active limitations whose `affects:` list mentions `fct_311_requests` / `raw_311_requests` / `requests.*` (for 311) or `fct_crime_incidents` / `raw_somerville_crime` / `crime.*` (for crime). Reported 3 affect 311, 4 affect crime out of 21 active; reasonable.

## Next action

Continue Plan 16 -- welcome content + ward map background (Session 44).
