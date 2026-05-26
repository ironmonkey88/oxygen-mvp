---
id: happiness-survey-self-selection-and-coverage
title: Happiness Survey -- self-selection bias, multi-year column drift, ward coverage gap
severity: high
affects:
  - main_bronze.raw_somerville_happiness_survey_raw
  - raw_somerville_happiness_survey
  - happiness_survey
since: 2026-05-14
status: active
---

# Somerville Happiness Survey -- analytical caveats

The biennial Happiness Survey (Socrata `wmeh-zuz2`, 2011-2025) is the
only perception signal in the warehouse. It pairs powerfully with the
operational data (311, crime, future permits + citations) -- *did
satisfaction track outcomes?* -- but three structural features make
that pairing non-trivial. Any analysis that joins survey responses to
operational data needs to surface all three.

## 1. Self-selection bias -- respondents are not a random sample

The city sends the survey to a sample of residents and accepts mailed-
back or online responses. The 12,583 rows are people who **chose to
respond**. Compared to the city as a whole, respondents likely:

- Skew older (response rates correlate with age on civic surveys
  generally),
- Skew longer-tenure (newer residents respond at lower rates),
- Skew more civically engaged (the act of responding is itself a
  civic-participation marker).

The 2011 wave alone has 6,167 rows -- 49% of the entire dataset --
because that wave was distributed differently. Any cross-wave
comparison carries an additional response-mode artifact.

**Consequence for joined analysis:** survey-derived metrics cannot be
generalized to the city's population without weighting. Headlines like
"60% of respondents feel safe" are statements about respondents, not
about Somerville residents. State that explicitly in any data app or
report that surfaces survey aggregates.

## 2. Ward coverage gap -- 50% of rows have NULL ward

Probed 2026-05-14: 6,225 of 12,583 rows (49.5%) have NULL `ward`.
Approximately:

- All 6,167 rows from the 2011 wave have NULL ward (the 2011 survey
  didn't collect it).
- A small residual (~58 rows) from later waves missing ward, likely
  blank-on-paper responses.

**Consequence:** ward-joined analysis (the natural pairing with 311,
crime, etc.) loses 49.5% of the dataset upfront and effectively
becomes a 2013-2025 analysis (`year >= 2013`). The 2011 wave is
useful for city-wide trend baselines but not for ward-level pairing.

## 3. Multi-year column drift -- waves don't ask the same questions

The 150 columns reflect cumulative survey shape across 8 waves
(2011-2025). Different waves asked different question sets:

- The identity-flag columns (`lgbtqia_yn`, `disability_yn`,
  `neurodivergent_yn`, `cultural_religious_minority_yn`) are 2023+
  additions; NULL for earlier years.
- Satisfaction topics evolved -- some `{topic}_num` /
  `{topic}_label` pairs only appear in waves where the topic was
  asked.
- Demographic bucket definitions shifted across waves (age bucket
  boundaries, race/ethnicity categories).

**Consequence:** any time series comparing a question across waves
must filter to the year range where the question was actually asked.
Naive `AVG(column)` across all years will silently drop years where
the column is NULL. Year-aware filtering is required in silver/gold
(MVP 3 work).

## 4. Quasi-identifier risk

No direct identifiers (name, email, address) are in the dataset.
Bucketed source values reduce identifiability significantly (age as
"35 to 44", income as ranges). However, combinations remain risky:

- Low-population ward x low-frequency identity flag x housing tenure
  x household composition can identify a unique respondent in
  principle.
- `/profile` already publishes per-column distinct counts and null
  rates, which are aggregate statistics -- not per-row -- so the
  surface there is low-risk. The risk is in joined queries against
  the dim columns at thin slices.

**Mitigation:** `/profile` exposure is bounded to aggregate shape
stats only. Silver/gold (MVP 3) should add k-anonymity gates on any
joined views that surface per-respondent detail in thin demographic
slices.

## Status

- Bronze: as-is. Caveats live here and are surfaced by the Answer
  Agent's trust contract when survey-affecting queries are asked.
- **Silver: shipped (Plan 44).** `main_silver.stg_happiness_survey`
  -- 12,583 rows, per-respondent grain, 8 curated `_num` columns
  cast to DOUBLE, ward NULL preserved, `weight` reserved-NULL.
- **Gold: shipped (Plan 44) -- aggregate-only, no demographic dims,
  unweighted with weight column reserved for future plan.** Three
  models: `dim_survey_question` (8 rows, question catalog with
  coverage profile), `dim_survey_wave` (8 rows, wave catalog with
  ward coverage %), `fct_happiness_survey` (trend fact at
  wave × geography_level × geography_key × question grain; city +
  ward levels; 2011 excluded from ward aggregation). Reachable via
  the `perception` semantic topic. See companion limitations
  [`survey-gold-unweighted`](survey-gold-unweighted.md) and
  [`survey-trend-only-no-demographics`](survey-trend-only-no-demographics.md).

## What MVP 3 silver/gold did and did not do

Plan 44 locked three decisions before building:

1. **Scope: trend over time, not the operational-pairing fact.**
   Gold answers "how has feeling about X trended across waves in
   Somerville / Ward N?" -- not "did satisfaction track outcomes?"
   The operational-pairing surface (survey × 311 × crime × permits
   joined by ward × year) is deliberately deferred to a future plan;
   it's likely best built as a dashboard or analyst notebook rather
   than a fact.
2. **No demographic dimensions in silver or gold.** Demographics
   (age, gender, race, identity flags, household composition,
   income) stay in bronze. The k-anonymity protection is structural
   (PHILOSOPHY.md sec.5): with no demographic dims surfaced, there
   are no thin slices to suppress. A future plan with explicit
   suppression machinery (e.g. k=5 floor on joined demographic
   combinations) can expand the surface.
3. **Designed for weighting, ships unweighted.** Silver reserves a
   `weight` column on every respondent row; gold reserves a
   `weight_strategy` column on every observation row. Both are
   NULL today. A follow-up plan that names a defensible weighting
   strategy (e.g. raking to ACS age x ward 2020) populates these and
   re-renders the aggregates weighted.

The Phase D coverage matrix below is the canonical source for which
8 of 50 satisfaction Likert columns surface in silver / gold. It
travels with the data into `dim_survey_question`:
`first_wave_asked` / `last_wave_asked` / `waves_asked_count` carry
the relevant per-question numbers from the matrix.

## Phase D pre-flight cross-wave-presence matrix (2026-05-15)

8 of 50 `_num` columns met the ≥5-wave / <50%-NULL filter:

| column | waves<50% NULL |
|---|---|
| `happiness_num` | 8 |
| `life_satisfaction_num` | 8 |
| `somerville_satisfaction_num` | 8 |
| `beauty_neighborhood_satisfaction_num` | 7 |
| `streets_maintenance_satisfaction_num` | 7 |
| `education_quality_satisfaction_num` | 6 |
| `social_community_events_satisfaction_num` | 6 |
| `city_services_information_availability_satisfaction_num` | 6 |

The 42 excluded columns split into:

- Topics asked in 4 waves (4 columns: housing_condition, getting_around,
  neighbors, priced_out, crossing_street_safety, rats_mice,
  city_services_quality).
- Topics asked in 2 waves (5 columns).
- Topics asked in 1 wave (24 columns including
  `feel_safe_somerville_num` — the Plan 23 prompt-named safety Likert).
- Topics asked in 0 waves at <50% NULL (8 columns, mostly 2025
  additions covering childcare / OST / accessibility).

**The right move per the prompt's halt instruction**: dedicate a
future MVP 3 plan to survey silver/gold. That plan can do
question-key harmonization across waves, k-anonymity on demographic
combinations, weighting strategy documentation, and year-aware
filtering on the column-drift surface. Treating the 8 surviving
columns as "MVP 2 minimum viable survey gold" without that scaffolding
ships a misleading analyst surface (analysts would treat the columns
as fully covered; they aren't).
