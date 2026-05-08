---
session: 4
date: 2026-05-07
start_time: 17:00 ET
end_time: 18:25 ET
type: hybrid
plan: none
layers: [bronze, gold, admin, portal, docs]
work: [planning, feature, infra]
status: complete
---

# Session 4 — Schema design and portal deployed

> Migrated from original LOG.md monolithic format. Preserved as-is.

## Original entry

**Accomplishments (from claude.ai — synced to repo at session start):**
- Designed full database schema: bronze, silver, gold, admin schemas
- Designed admin DQ star schema: fct_data_profile, dim_data_quality_test, fct_test_run
- Profiled actual Parquet columns — confirmed 22 columns, typed and annotated
- Designed all gold models: fct_311_requests, dim_date, dim_request_type, dim_status, dim_origin
- Wrote docs/schema.sql — full DDL, source of truth for all tables
- Established naming standards: snake_case, _dt, is_, pct_, _count conventions
- Designed DQ framework: profiling (observational) vs baseline comparisons vs dbt tests (both assertional)
- Designed dbt results capture: run_results.json → load_dbt_results.py → raw_dbt_results → fct_test_run

**Accomplishments (Claude Code — committed to GitHub this session):**
- Committed all session 4 files to GitHub main: TASKS.md, LOG.md, docs/schema.sql, portal/index.html
- Installed nginx 1.24.0 on EC2, enabled as system service
- Created /var/www/somerville/ directory structure with /erd and /tasks subdirs
- Configured nginx: root → /var/www/somerville, /docs → dbt target output, /chat → proxy localhost:3000
- Deployed portal/index.html to /var/www/somerville/ — confirmed curl http://localhost returns HTML
- Rebuilt portal to match Somerville Analytics design: nav with MVP badge, serif hero heading, stats bar, assets 2×2 grid, how-it-works split with stack table, roadmap, footer
- Self-hosted fonts — downloaded latin subset woff2s from Google Fonts API: DM Serif Display, DM Mono, Instrument Sans
- Applied fonts: DM Serif Display → hero h1, DM Mono → stack layer labels and detail column, Instrument Sans → body
- Committed fonts (portal/fonts/*.woff2) and updated portal/index.html to GitHub main
- Updated TASKS.md with Portal section (nginx install and deploy tasks marked [x])

**Decisions Made:** See Decisions Log (extensive).

**Blockers:** None.

**Next Action:** Initialize dbt project on EC2 and build bronze model.
