---
id: traffic-citations-location-and-violation-only
title: Traffic Citations are location + violation only -- low PII, but no driver-level breakdown
severity: low
affects:
  - main_bronze.raw_somerville_traffic_citations_raw
  - raw_somerville_traffic_citations
  - traffic_citations
since: 2026-05-14
status: active
---

# Traffic Citations: low PII surface, but driver-level analysis isn't possible

## PII surface assessment

Probed 2026-05-14: the source publishes **location + violation + ward
+ warning/fine flag + speed**. It does **not** publish:

- driver name
- driver license number
- vehicle registration / plate
- vehicle make / model / year / color
- officer name / badge number

Sample rows examined: 3 rows from `https://data.somervillema.gov/resource/3mqx-eye9.json?$limit=3` --
all carry intersection addresses (e.g. "RTE 28 & RTE 38 Somerville,
MA"), MGL violation codes, ward, speed-when-applicable, and a Y/N
warning flag. No personal identifiers.

The PII surface here is meaningfully smaller than the crime dataset
(which carries `blockcode` precision and police-shift detail enough
that combined with the day-and-month + offense type could identify a
narrow incident). Traffic Citations is location-aggregated and
violation-categorized, which is appropriate for the equity-of-
enforcement questions the project intends to ask.

`/profile` exposure is fine -- no per-column risk surface that needs
gating.

## What this dataset CAN'T tell us

The flip side of low PII: the dataset doesn't support driver-level
analysis. Questions the data CAN'T answer:

- Are citations concentrated among repeat offenders? (no driver ID)
- Are particular vehicle types or owners over-cited? (no vehicle data)
- Are particular officers more / less likely to issue warnings vs
  fines? (no officer ID)
- What is the demographic distribution of cited drivers? (no
  demographics)

Questions the data CAN answer (ward + date + violation type are all
present and reliable):

- Where (which wards, which intersections, which streets) are
  citations issued?
- How does enforcement activity vary by ward, controlling for
  population?
- What violations are most common, by ward and time-of-day?
- What is the warning-vs-fine ratio by ward / category?
- How does citation activity correlate with 311 traffic complaints or
  crime in the same ward?

State this scope explicitly in any data app or analysis: the dataset
is about **where and what**, not **who**.

## Data-shape notes

- **Grain**: one row per (citation, violation). A single traffic
  stop with two violations becomes two rows with `citationnum` values
  `T123-1` and `T123-2`. Aggregating by ward/date is correct;
  counting unique citations requires stripping the suffix and
  deduplicating.
- **Ward NULL rate**: 84 of 67,311 rows (~0.12%). Ward analyses are
  effectively complete.
- **Warning vs fine**: ~76% of rows are warnings (`warning = 'Y'`),
  ~24% carry a monetary fine. Distinct populations -- analyses
  intending to measure "enforcement intensity" should pick one and
  state which.
- **`chgcategory` cardinality**: 109 distinct values. Too
  high-cardinality for an `accepted_values` test; relevant categories
  should be filtered by `chgcode` ranges or LIKE patterns at silver.

## Status

- Bronze: as-is. Caveats live here and are surfaced by the Answer
  Agent's trust contract when citation-affecting queries are asked.
- **Gold: landed 2026-05-15 (Plan 23 Phase B).** `main_gold.fct_citations`
  + `semantics/views/citations.view.yml` + topic membership in
  `public_safety`. Type casts done at gold (`citation_ts` →
  TIMESTAMPTZ, `vehicle_mph` → INTEGER, `latitude`/`longitude` →
  DOUBLE). 5 measures shipped: citation_count, count_by_day_shift,
  count_by_night_shift, average_vehicle_speed_on_speed_violations,
  count_distinct_violation_types.
- Silver: deferred to MVP 3. Will optionally derive a citation-event-
  grain table by stripping the violation suffix; see
  citations-composite-grain-violation-suffix limitation.
