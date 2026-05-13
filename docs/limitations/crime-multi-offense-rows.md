---
id: crime-multi-offense-rows
title: Two NIBRS offense types use multi-code grouping strings as offense_code
severity: warning
affects:
  - main_gold.fct_crime_incidents
  - offense_code
  - multi_offense_flag
since: 2026-05-13
status: active
---

# Two NIBRS offense types use multi-code grouping strings as offense_code

12.9% of crime incidents (2,875 of 22,325 rows, as of 2026-05-13)
carry a comma-separated `offense_code` rather than a single 3-char
NIBRS code. This is **not data-quality drift** — it is a Somerville
Police source convention for two specific NIBRS offense types whose
operational definition spans multiple atomic NIBRS codes.

## The two groupings

| `offense_code` value | `offense` / `offense_type` | row count |
|---|---|---|
| `'991, 998, 999'` | "Other Criminal MV Offenses" | 2,500 |
| `'11A - 11D, 36A, 36B'` | "Sex Offenses" | 375 |

Both groupings are recognized at gold as legitimate `offense_code`
values. They appear as rows in `dim_offense_code` (rows 38 and 39 of
the dim's 39 total), flagged via `is_multi_offense_grouping = TRUE`.
The fact's `relationships` test to `dim_offense_code` passes without
a NULL carve-out — analysts can group by `offense_code` directly and
get 39 buckets.

The `multi_offense_flag` boolean on the fact (= `offense_code LIKE
'%,%'`) lets analysts filter the multi-code rows in or out without
needing the dim:

```sql
-- single-NIBRS-code analysis only
SELECT offense_code, COUNT(*)
FROM main_gold.fct_crime_incidents
WHERE NOT multi_offense_flag
GROUP BY offense_code
```

## Impact

- **Atomic-NIBRS analysis loses 12.9%** if it filters
  `WHERE NOT multi_offense_flag`. The dropped rows are concentrated
  in two offense types — both still visible via `offense_type`
  ("Other Criminal MV Offenses", "Sex Offenses") at the type-level
  aggregation.
- **Code-by-code crime ranking** (e.g. "top 10 offense codes") sees
  `'991, 998, 999'` ranked #2 by frequency (after `23H` All Other
  Larceny). Display this clearly — the rank position is real but
  the row represents a grouping, not a single offense.
- **Joins to external NIBRS catalogs** would need to handle the
  grouping strings specially. We don't currently load any external
  NIBRS catalog; if MVP 3+ adds one, this limitation surfaces the
  required handling.

## History

Plan 13 design (Chat, 2026-05-13) anticipated this as a "one row in
22,325" edge case based on the single example surfaced in Plan 12
Phase 3 sampling. Pre-flight on Plan 13 Phase 1 found the actual
count is 2,875 rows in two structural groupings.

The Plan 13 design recommended NULLing `offense_code` on
multi-offense rows. **Plan 13 Phase 2 deviated** from that
recommendation: keeping `offense_code` as the source string (with
both groupings included in `dim_offense_code`) produces a cleaner
analyst surface than 12.9% NULLs and a `multi_offense_flag` carve-out
on every join. The session note (session-NN-...-plan-13-...) records
the deviation rationale.

## Resolution path

No project-side resolution. The groupings are source-convention; the
gold layer reflects the source faithfully. If a future analyst needs
atomic-code disaggregation for these two offense types (e.g.
distinguishing "11A Forcible Rape" from "36A Incest"), the only
source is the underlying SPD records that the city has not chosen to
publish at code-granularity for these categories.
