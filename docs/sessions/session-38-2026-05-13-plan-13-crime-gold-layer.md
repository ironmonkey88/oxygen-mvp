---
session: 38
date: 2026-05-13
start_time: 12:18 ET
end_time: 13:30 ET
type: code
plan: plan-13
layers: [gold, semantic, docs]
work: [feature, docs]
status: complete
---

## Goal

Execute Plan 13 — design + build the gold layer for crime data on
top of Plan 12 Phase 3's bronze. Chat designed in the previous turn
(silver no, fct_crime_incidents + dim_offense_code +
dim_offense_category, separate public_safety topic, 4 limitations).
Code executes the design, surfaces deviations honestly, runs the
verification gates.

## What shipped

Six phases, six commits on `claude/goofy-gould-2ce2b3` (continuation
from Plan 12; main was ff-merged to this branch's tip before Plan 13
started, so each phase commit is ahead of main again).

- **Phase 1 (no commit — gate).** Pre-flight verified the design's
  assumptions against bronze. Three discrepancies surfaced; see
  "Pre-flight findings" below.
- **Phase 2 ([`fb51194`](https://github.com/ironmonkey88/oxygen-mvp/commit/fb51194)).** [`main_gold.fct_crime_incidents`](../../dbt/models/gold/fct_crime_incidents.sql)
  — 22,325 rows. Surrogate PK `incident_id` (md5 of case_number);
  case_number preserved on the fact for analyst back-reference.
  Derived `incident_dt` (NULL for sensitive incidents), `incident_year`,
  `incident_year_only` flag. `offense_code` per the Phase 2 deviation
  (kept raw, not NULLed for multi-code). `ward` TRIM with NULL/CAM
  passthrough. `block_code` passthrough. dbt 1/1 OK + 10/10 PASS.
- **Phase 3 ([`7648917`](https://github.com/ironmonkey88/oxygen-mvp/commit/7648917)).** [`dim_offense_code`](../../dbt/models/gold/dim_offense_code.sql)
  (39 rows: 37 atomic + 2 grouping strings) + [`dim_offense_category`](../../dbt/models/gold/dim_offense_category.sql)
  (4 rows + editorial `severity_rank`). 27/27 tests PASS across all
  crime gold including relationships to dim_ward (with carve-out),
  dim_offense_code, dim_offense_category.
- **Phase 4 ([`eda1c5d`](https://github.com/ironmonkey88/oxygen-mvp/commit/eda1c5d)).** Three new view files:
  [`crime.view.yml`](../../semantics/views/crime.view.yml),
  [`offense_codes.view.yml`](../../semantics/views/offense_codes.view.yml),
  [`offense_categories.view.yml`](../../semantics/views/offense_categories.view.yml).
  New [`public_safety.topic.yml`](../../semantics/topics/public_safety.topic.yml)
  shares `wards` and `dates` with `service_requests`. `oxy validate`
  11/11 valid. `airlayer validate` 8 views, 2 topics. 5 cross-view
  Airlayer queries verified including auto-join to wards, dates,
  offense_codes, offense_categories.
- **Phase 5 ([`28743fc`](https://github.com/ironmonkey88/oxygen-mvp/commit/28743fc)).** Limitations registry: 1 renamed
  (`crime-data-pii-unredacted-in-bronze` → `crime-bronze-restricted-from-analysis`,
  rewritten to lead with layer discipline; PII findings as
  sub-section) + 3 new gold-level entries
  ([`crime-sensitive-incidents-no-month`](../limitations/crime-sensitive-incidents-no-month.md),
  [`crime-ward-coverage-gaps`](../limitations/crime-ward-coverage-gaps.md),
  [`crime-multi-offense-rows`](../limitations/crime-multi-offense-rows.md)).
  `_index.yaml` regenerated: 14 → 17 active entries. `/trust` page
  re-rendered.
- **Phase 6 ([this commit])** [`docs/schema.sql`](../schema.sql)
  gains DDL for fct_crime_incidents + the 2 dims; LOG.md +
  TASKS.md updated; this session note; final `./run.sh manual`
  end-to-end.

## Pre-flight findings (Phase 1)

Three discrepancies from the Chat design's assumptions. Two require
attention; one was already implicit in the design.

1. **Multi-offense rows: 2,875 (12.9%), not 1.** The design said
   "one row" for `'991, 998, 999'`. Reality: 2,875 rows in two
   source-convention groupings — `'991, 998, 999'` (= "Other
   Criminal MV Offenses", 2,500 rows) and `'11A - 11D, 36A, 36B'`
   (= "Sex Offenses", 375 rows). These are NIBRS source-side
   groupings for two specific offense types, not data-quality
   oddities.

   **Deviation from design.** The design recommended NULLing
   `offense_code` on multi-code rows + carve-out in the
   relationships test. The deviation: keep `offense_code` = raw
   source value, include both groupings in `dim_offense_code` as
   rows flagged with `is_multi_offense_grouping = TRUE`. Cleaner
   analyst surface (39 codes vs 37 + a NULL-bucket of 2,875);
   relationships test passes without carve-out; `multi_offense_flag`
   stays for analyst filtering. The `crime-multi-offense-rows`
   limitation reframes the count + records the deviation rationale.

2. **Sensitive-incident incnum sentinel format.** Non-sensitive
   incnums are 8-char `YYxxxxxx`; sensitive incnums are 9-char
   `1xxxxxxxx`. Pre-flight's "year-prefix vs year mismatch" count
   (2,798) maps exactly to the day_and_month-NULL set. Documented
   in `case_number` column descriptions + the bronze limitation
   rename.

3. **`blockcode` NULL = 2,798**, same rows as `day_and_month` NULL.
   Source strips location AND day for the same sensitive-incident
   set. Folded into the `crime-sensitive-incidents-no-month`
   limitation rather than a separate entry; both columns are part of
   the same source-side redaction.

## Decisions

The structural Plan 13 design decisions held — bronze→gold direct
(no silver), surrogate PK + case_number preserved, separate
`public_safety` topic, three new gold-level limitations. Deviations:

1. **`offense_code` kept as raw source string** (not NULLed for
   multi-code rows). See Pre-flight finding 1.

2. **Plan 13's two open design questions (Q1 + Q2) executed per
   recommendation, pending Gordon's review.**
   - Q1 (denormalize offense / offense_type on fact, or only on
     dim?): denormalized on fact for query convenience, matching
     `fct_311_requests`'s request_type pattern.
   - Q2 (case_number exposure on analyst surface?): kept. Public
     reference, useful for citations in the agent's trust contract.

3. **dim_offense_code sources from the fact, not bronze.** The fact
   already applies the cleanup; deriving the dim from `SELECT DISTINCT`
   on the fact keeps the transformation in one place. The Phase 2
   deviation flows through naturally.

## Issues encountered

- **Multi-offense rows were under-counted in the design.** Pre-flight
  caught it; the structural design held; the deviation handled it.
  Surfaced in the session note + the limitation entry + the Phase 2
  commit message.
- **LOG.md is now 305+ lines, well over the 250 hard ceiling.** Per
  the prompt and prior brief, this isn't addressed in Plan 13. Queued
  tech debt — compression pass overdue.
- **`./run.sh manual` end-to-end run.** The pre-existing
  `dq_drift_fail_guardrail` will continue to land Plan 13 runs as
  `partial`; the portal-deploy ownership regression
  (`portal-deploy-file-ownership` limitation) may recur if anyone
  has run `sudo cp` on the portal files since the last fix.

## Cross-topic comparison sketch

Test of the design's §6 trust-contract walk-through. The analyst's
question "how does crime by ward compare to 311 complaints by ward?"
runs as **two airlayer queries** (one per topic, both joining the
shared `wards` view), and the agent stitches the comparison:

```
# service_requests topic
airlayer query -x --dimension requests.ward \
                  --measure requests.total_requests \
                  --order requests.ward:asc

# public_safety topic
airlayer query -x --dimension crime.ward \
                  --measure crime.total_incidents \
                  --order crime.ward:asc
```

Both Plan 12 (Phase 2) and Plan 13 (Phase 4) verified these
work in isolation. The single-query cross-topic case (`crime`
and `requests` measures in one SELECT) was not attempted — per
the design's §4 reasoning, that's not the intended pattern.

## Next action

None on this branch — Plan 13 closed. Open queues for the morning:
- Plan 11 execution still pending Gordon's review of the scoping doc
- LOG.md compression pass (overdue)
- Portal-deploy ownership durable fix
- Plan 13 design's two open Q's (case_number, denormalization)
  flagged for confirmation
