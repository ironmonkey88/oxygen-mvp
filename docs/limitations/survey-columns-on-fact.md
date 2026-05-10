---
id: survey-columns-on-fact
title: Survey columns live on the fact table as sparse Likert strings
severity: info
affects:
  - accuracy
  - courtesy
  - ease
  - overallexperience
since: 2026-05-07
status: active
---

# Survey columns live on the fact table as sparse Likert strings

The four post-resolution survey columns — `accuracy`, `courtesy`, `ease`,
`overallexperience` — sit directly on `main_gold.fct_311_requests` as
VARCHAR Likert-style strings (e.g. `"Excellent"`, `"Good"`, `"Fair"`).
There is no `dim_survey_response` and no referential integrity. This is
distinct from the `2024-survey-columns-sparse` entry, which describes
*coverage* rather than *shape*.

## Impact

- Aggregations require string comparison against expected Likert values
  rather than numeric math; typos and case-mismatch in the source feed
  silently fall through to "other."
- No enum integrity — if a new Likert value appears upstream, downstream
  queries don't catch it.
- Cannot easily join to a survey-instance dim for richer analysis
  (date of survey, channel, etc.) — that history isn't preserved.

## Workaround

Treat the columns as enums with this expected value set:
`Excellent`, `Good`, `Fair`, `Poor`, `Very Poor` (and `NULL` for
no-response). When aggregating, use a `CASE` expression to map to a
1–5 scale.

## Resolution path

A normalized `dim_survey_response` could land in MVP 3 alongside Silver,
but is not planned. The shape mirrors the upstream feed.
