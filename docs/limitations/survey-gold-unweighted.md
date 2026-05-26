---
id: survey-gold-unweighted
title: Happiness Survey gold ships unweighted -- aggregates describe respondents, not residents
severity: medium
affects:
  - main_gold.fct_happiness_survey
  - main_silver.stg_happiness_survey
  - happiness_survey
  - perception
  - mean_score_overall
  - pct_top_two_box
  - pct_bottom_two_box
  - total_respondents
since: 2026-05-25
status: active
---

# Happiness Survey gold ships unweighted

The Happiness Survey gold layer (Plan 44) computes every aggregate
without per-respondent weighting. Every number describes the
respondents who answered -- not Somerville residents.

## What this means in practice

If you ask "what's the average happiness score in Ward 3 in 2023?",
the answer is the arithmetic mean of the Likert responses from the
respondents who lived in Ward 3 and chose to answer the 2023 wave.
It is **not** a statistical estimate of how the average resident of
Ward 3 felt in 2023.

The gap between those two numbers can be large. Respondents to civic
surveys typically:

- Skew older than the resident population,
- Skew longer-tenure (newer residents respond at lower rates),
- Skew more civically engaged (the act of responding is itself a
  civic-participation marker).

The 2011 wave alone has 6,167 respondents -- 49% of the entire
dataset -- because that wave was distributed differently. Cross-wave
comparisons therefore carry an additional response-mode artifact on
top of the self-selection bias documented in
[`happiness-survey-self-selection-and-coverage`](happiness-survey-self-selection-and-coverage.md).

## Why ship unweighted

Computing weights honestly is a multi-step problem with multiple
defensible answers:

- **Raking to ACS age × ward.** Standard approach for civic
  surveys; needs the ACS marginals for each wave year and a
  documented choice of which demographic dimensions to rake on.
- **Propensity-score adjustment.** More sophisticated; needs a
  defensible propensity model.
- **Post-stratification with cell collapses.** When cells are too
  thin for raking, you collapse them; the collapse rule is itself
  a decision.

Picking one without naming the choice and documenting its assumptions
would ship "weighted aggregates" that look authoritative but mislead.
Shipping unweighted with the caveat surfaced on every relevant query
is more honest.

## What's reserved for the future plan

The silver and gold schemas have the slots already:

- `main_silver.stg_happiness_survey.weight` -- per-respondent DOUBLE,
  NULL on every row today.
- `main_gold.fct_happiness_survey.weight_strategy` -- VARCHAR
  identifier of the strategy used to compute the aggregate
  (e.g. `raked_age_ward_2020_acs`), NULL on every row today.

A future plan that names a strategy populates `weight` in silver and
re-renders gold with weighted aggregates, stamping the strategy name
into `weight_strategy` so the analyst knows which methodology
produced the number they're looking at.

## Trust-contract framing

Any analyst surface (Answer Agent reply, dashboard headline, brief)
that uses these measures must phrase the result in terms of
respondents, not residents. Examples:

- ✓ "60% of respondents who answered the 2023 wave in Ward 3 rated
  happiness 4 or 5."
- ✗ "60% of Ward 3 residents rated happiness 4 or 5 in 2023."

The Answer Agent's trust contract surfaces this entry when any query
touches the affected views or measures.
