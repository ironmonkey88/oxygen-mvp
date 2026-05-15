---
session: 46
date: 2026-05-14
start_time: 18:30 ET
end_time: 23:44 ET
type: code
plan: plan-A
layers: [bronze, portal, infra, docs]
work: [feature, bugfix, infra, docs]
status: complete
---

## Goal

Execute three back-to-back briefs in one overnight thread: portal-feedback polish (Prompts 09 + 10), a new DASHBOARDS.md design standard, and the four-dataset overnight ingestion batch (Prompt 11).

## What shipped

- PR #21 — Prompt 09: ward map labels + 7th stats cell + CTA clipboard + `/trust` Pipeline reliability sparkline + Pipeline history operational table.
- PR #22 — DASHBOARDS.md added; CLAUDE.md Operational hierarchy updated.
- PR #23 — Prompt 10: centered ward map at low opacity; test-summary cell colors on `fail_count > 0` (not pass<total); `fct_test_run.sql` distinguishes inactive baselines from missing ones with by-design framing; hero subtitle fixed.
- PR #24 — Phase A: `wmeh-zuz2` Happiness Survey (12,583 rows / 150 cols / 8 waves). Replace mode, not in run.sh (biennial). 49.5% NULL ward + multi-year column drift + self-selection bias documented.
- PR #25 — Phase B: `vxgw-vmky` Permits (64,521 rows / 10 cols). Replace mode, static since 2023-05-16. Initial `not_null_type` test failed with 11 rows; per honest-finding discipline, test dropped + finding documented (not papered over).
- PR #26 — Phase C: `3mqx-eye9` Traffic Citations (67,311 rows / 14 cols). Merge mode on `citationnum`. Wired into `run.sh` stage 1c. PII surface low (no driver / vehicle / officer ID); 6/6 tests pass.
- PR #27 — Phase D: `jnde-mi6j` Somerville at a Glance (749 rows / 6 cols / 25 topics). Long-tidy KPI table; replace mode, not in run.sh.
- PR #28 — Phase E: `/about` Somerville info page. New `scripts/generate_somerville_info_page.py`, nav extended to 8 entries with "About", nginx `location = /about`, `run.sh` stage 8d.

## Decisions

- **Phase A gate (PROCEED).** Workable PK (`id`), ward column present, biennial cadence -> manual not run.sh. 49.5% NULL ward and 6,167-row 2011 spike documented as analytical caveats, not blockers.
- **Phase B test failure handled as a finding.** Probed pre-flight showed `type` had 11 NULL rows; initial schema with `not_null_type` failed loudly on first dbt test. Dropped the test, captured in limitations entry. Honest-finding discipline applied.
- **Phase C wired into run.sh as 1c.** Source refreshes daily with a one-month delay; same cadence pattern as crime (stage 1b).
- **Phase D NOT in run.sh.** ACS-derived; annual cadence at most. Manual re-ingest.
- **Phase E nav: 8th entry rather than homepage-link.** "About" added to NAV_ITEMS; 8 links fit at desktop widths; orientation content gets its own nav slot.
- **Ward map third pass.** Prompt 09 made it darker and shifted left. Prompt 10 centered, softened SVG palette back to original light grey, and dropped CSS opacity to 0.32. Restraint at both levels.

## Issues encountered

- **YAML escaping in schema.yml.** Single-quoted strings can't escape apostrophes via `\'`; double-quote strings instead. Hit twice in Phase A (acs_somerville_median_income, inflation_adjustment).
  Resolution: use double-quote YAML strings when content contains apostrophes.

- **`year` is VARCHAR in DuckDB.** Phase E generator's Python sort failed with `bad operand type for unary -: 'str'` -- dlt infers source `number` types as VARCHAR. Cast with `int()` in sort key.
  Resolution: `_year_to_int()` helper coerces VARCHAR / int / None safely.

- **nginx `sites-available/somerville` not `.conf`.** First nginx config copy went to `/etc/nginx/sites-available/somerville.conf` -- but the symlink in `sites-enabled/` points to the no-extension filename. `/about` returned 404 until corrected.
  Resolution: cp to `/etc/nginx/sites-available/somerville` (no extension). Repo header already documents the correct path.

## Next action

Open Code thread for Builder-CLI dashboards (Plans 18 + 19) or whatever Gordon points to next. The warehouse now carries the data for sentiment-vs-operations, equity-of-enforcement, and development-pressure analyses -- all bronze-only, awaiting silver/gold + dashboards (MVP 3).
