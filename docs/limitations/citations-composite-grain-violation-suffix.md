---
id: citations-composite-grain-violation-suffix
title: Citations grain is (citation, violation) -- multi-violation tickets become multiple rows
severity: warning
affects:
  - main_bronze.raw_somerville_traffic_citations
  - main_gold.fct_citations
  - citations
since: 2026-05-15
status: active
---

# Citations grain is (citation, violation), not (citation)

## The finding

Probed 2026-05-15 on the source dataset (Socrata `3mqx-eye9`,
67,311 rows): every `citationnum` value carries a numeric suffix
(e.g. `T123-1`, `T123-2`). When stripped, 67,311 rows resolve to
**61,603 distinct "root" citation numbers** -- meaning 5,708 rows are
supplementary-violation entries on tickets that issued more than one
violation.

The bronze view passes the suffixed form through as-is. The gold
fact (`fct_citations`) preserves the same grain: one row per
(citation, violation). A surrogate `citation_id = md5(citation_number)`
keeps the row PK unique without invented composite keys.

## Why we keep it as-is at gold

The Plan 23 prompt explicitly designated suffix-strip as silver work:
> "Violation-suffix carve-out. Per the documented composite-citation-
> grain issue, do NOT strip the violation suffix in this prompt --
> that's silver work."

The standing rationale: silver layer derivations (suffix-strip,
deduplication by root citation, derived "first-violation-only" view)
are a curation choice. Gold mirrors the source shape so the
underlying grain is visible to analysts -- a `COUNT(*)` returns
67,311; a `COUNT(DISTINCT REGEXP_REPLACE(citation_number, '-[0-9]+$',
''))` returns 61,603. Both are correct answers to different questions.

## Consequence for analysis

- **`citation_count` measure counts violation-rows, not ticket-events.**
  A traffic stop that issues 3 violations contributes 3 to
  `citation_count`. For "how many traffic stops issued a citation",
  the analyst needs a suffix-stripped count -- currently expressible
  as ad-hoc SQL, not a built-in measure.
- **Ward and date aggregates are ratio-stable.** Aggregating by
  ward, date, or charge_category gives proportional answers either
  way (the supplementary-violation rows share the same ward + date as
  the root). Distortion only appears in "how many tickets did SPD
  issue" framings.
- **Cross-topic comparisons** with 311 (one row per request) or
  crime (one row per incident) need to be careful: citations
  count-by-ward is in violation-rows, not ticket-events.

## Workaround

For analyses where the grain matters:
- Use `COUNT(DISTINCT REGEXP_REPLACE(citation_number, '-[0-9]+$', ''))`
  for ticket-event counts.
- Filter to `citation_number LIKE '%-1'` for the "first violation per
  ticket" view (informal but works on the observed data).
- Plan 23 prompt names a silver-grain derived table as the durable fix.

## Status

- Bronze: as-is.
- Gold: as-is. Composite grain preserved with `citation_id` surrogate
  PK; root-citation derivation deferred to silver per Plan 23 prompt.
- Silver / future: derive a `fct_citation_events` table at the
  ticket-event grain (one row per root citation) joined to a
  `fct_citation_violations` line-item table. MVP 3 work.
