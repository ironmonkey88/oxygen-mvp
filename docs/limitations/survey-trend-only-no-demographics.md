---
id: survey-trend-only-no-demographics
title: Happiness Survey gold is trend-only -- no demographic dimensions in silver or gold
severity: low
affects:
  - main_gold.fct_happiness_survey
  - main_silver.stg_happiness_survey
  - happiness_survey
  - perception
since: 2026-05-25
status: active
---

# Happiness Survey gold is trend-only -- no demographic dimensions

The Happiness Survey gold layer (Plan 44) surfaces trend over time
at city + ward grain. Demographic dimensions present in bronze
(age, gender, race, identity flags, household composition,
household income, housing status, language, education, tenure) are
**deliberately not surfaced** in silver or gold.

This isn't a data-quality issue. It's a scope decision -- a low-
severity caveat in the limitations registry so the absence is
documented, not a problem to fix.

## Why no demographic dimensions

Per PHILOSOPHY.md sec.5, k-anonymity on survey data is one of the
boundary constraints that's not in the trade-off space. Two ways to
enforce a k-anonymity floor on demographic combinations are
available:

1. **Suppress thin cells in views.** Build the views with
   demographic dimensions exposed, then filter out result rows
   where the underlying cell count falls below some threshold k.
   Computationally protective but defeatable -- a sophisticated
   user can reconstruct suppressed cells from adjacent ones.
2. **Don't surface the dimensions at all.** Aggregate over
   demographic dimensions in silver -> gold; the dim isn't in the
   warehouse, so there's nothing to suppress.

Plan 44 chose option 2 for MVP 3. The protection is structural
rather than computational. An analyst who wants demographic-cut
analysis is gated until a future plan with explicit suppression
machinery -- which is the right gate to have.

## What gold does surface

- Per-wave trend: aggregate scores per question per wave.
- Per-ward trend: aggregate scores per question per ward per wave
  (2013-2025; 2011 excluded for ward-level per
  [`happiness-survey-self-selection-and-coverage`](happiness-survey-self-selection-and-coverage.md)).
- Question coverage matrix: per-question first / last / count of
  waves where the question cleared the >50% non-NULL filter.

That set is enough to answer "has happiness trended up or down in
Somerville / Ward N since 2013?" -- the core trend question that
motivated the curation work. It is NOT enough to answer "are renters
happier than owners in Ward 3?" or any other demographically-cut
question.

## What a future demographics plan would need

To expand gold to surface demographic cuts safely, the follow-up
plan needs:

1. **A k-anonymity floor.** Common choice is k=5 (no published cell
   describes fewer than 5 respondents); some civic-survey contexts
   use k=10. The choice itself is a decision worth making
   explicitly.
2. **A cell-collapse rule for thin demographic categories.** When a
   demographic combination falls below k, collapse to a less-thin
   parent category (e.g. "65+" instead of "65-74").
3. **A pivot decision: silver or gold.** Demographic columns can be
   added to silver and aggregated into a wider gold fact, or kept
   in silver and joined to gold via a per-respondent view. The
   pivot affects what the semantic layer can express.

Plan 44 deliberately defers all three. Until a plan that addresses
them ships, the dimensions are absent and the protection is the
absence.
