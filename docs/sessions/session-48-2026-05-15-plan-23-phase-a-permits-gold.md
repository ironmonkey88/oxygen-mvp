---
session: 48
date: 2026-05-15
start_time: 14:30 ET
end_time: 22:22 ET
type: code
plan: plan-A
layers: [gold, semantic, docs]
work: [feature, docs]
status: partial
---

## Goal

Execute Plan 23 — gold + semantic layers for the four Plan-21 bronze datasets (permits, citations, Somerville-at-a-Glance, Happiness Survey) — across four independent phases. One PR per phase per the prompt's independent-value model.

## What shipped

- **Phase A complete.** Permits gold + semantic landed via [PR #36](https://github.com/ironmonkey88/oxygen-mvp/pull/36), merge commit `d269aab`. Files:
  - `dbt/models/gold/fct_permits.sql` — gold fact with dbt `pre_hook=["INSTALL spatial", "LOAD spatial"]`, surrogate PK md5(permit_number), spatial CTE deriving `ward` via ST_Contains against `dim_ward.geometry_wkt_wgs84`. Source-quirk passthrough (11 NULL `type`, status anomalies).
  - `dbt/models/gold/schema.yml` — fct_permits entry: column descriptions; not_null/unique on permit_id + permit_number; not_null on application_date; relationships to dim_ward with `WHERE ward IS NOT NULL` carve-out.
  - `semantics/views/permits.view.yml` — 5 measures (permit_count, issued_permit_count, total_issued_permit_value, avg_issued_permit_value, distinct_address_count), 14 dimensions. Initial draft used `type: avg` for the avg measure; `oxy validate` rejected; fixup commit `8d15977` renamed to `type: average` per Airlayer vocabulary.
  - `semantics/topics/built_environment.topic.yml` — new topic carrying permits + wards + dates. Permits is its own analytical domain; not service_requests, not public_safety.
  - `docs/schema.sql` — fct_permits DDL block in established format, placed after fct_311_requests before the ADMIN section.
  - `docs/limitations/permits-spatial-ward-derivation.md` — new entry documenting the 96.62% spatial match rate, the 2,176 unmatched rows, and the relationships-test carve-out.
- **Verification:** dbt run --select fct_permits PASS=1; dbt test --select fct_permits PASS=6 (not_null + unique on permit_id + permit_number, not_null on application_date, relationships to dim_ward); oxy validate "All 14 config files are valid".
- **Housekeeping:** LOG.md Plan 23 Plans Registry row (status: partial); two Active Decisions rows (Phase A spatial match findings + Airlayer measure-type vocabulary lock); Session 48 entry in Recent Sessions; Last Updated bumped; TASKS.md Next Focus updated to point at Phases B/C/D as fresh-thread work; this session note.

## Decisions

- **Reconciliation choice on Plan 23:** ship Phase A standalone, defer B/C/D. The prompt's per-phase independent-value model explicitly enables this — Phase A is useful as soon as it lands regardless of whether the others ship. Doing all four in this thread would have stretched the session past the honest-reporting bandwidth signal (Plan 22 already landed earlier today; the multi-phase merge clarification before that; the prompt-and-prompt-landing improvement before that). Cleaner to land Phase A well than to half-do four phases.
- **Airlayer measure-type vocabulary lock:** the valid types are `{count, sum, average, min, max, count_distinct, median, custom}`. `avg` is the SQL function but not a measure-type name. Documented in a new Active Decisions row so future view-YAML drafts don't repeat the trip.

## Issues encountered

- **`oxy validate` rejected `type: avg`.** Failed with "unknown variant `avg`, expected one of `count`, `sum`, `average`, ...". Resolution: rename to `type: average` in permits.view.yml; scp to EC2; re-run validate (clean). Fixup commit `8d15977` carried the fix; landed in PR #36.
- **EC2 worktree state after direct scp.** During the validate iteration I scp'd the fixed permits.view.yml directly into `/home/ubuntu/oxygen-mvp/semantics/views/` (outside git). That left EC2's `claude/plan-23-permits-gold` branch with a "modified" working tree on that file. Discarded with `git checkout -- semantics/views/permits.view.yml` before switching back to main. Lesson: post-fixup-commit, re-fetch on EC2 rather than continuing to scp piecemeal.

## Next action

Plan 23 Phases B / C / D in fresh threads. The original Plan 23 prompt has each scoped; lift directly:

- **Phase B (Citations).** Same shape as A — spatial point-in-polygon ward derivation, gold fact, view, limitations. Joins into the existing `public_safety` topic. Pre-flight gate: lat/lng coverage <90% on bronze halts.
- **Phase C (Somerville-at-a-Glance).** Long-tidy KPI fact + new `dim_kpi_topic`. No spatial join. New `city_context` topic.
- **Phase D (Happiness Survey).** Halt risk: cross-wave column-presence filter (column must appear in ≥5 of 8 waves with <50% NULL). If <12 columns survive, halt and surface — survey isn't usable gold yet, should be a dedicated MVP 3 silver/gold plan. New `resident_perception` topic.

Each is independently valuable. Phase D's halt risk should not block B or C.
