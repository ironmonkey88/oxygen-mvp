---
id: crime-data-pii-unredacted-in-bronze
title: Crime data carries source-level PII risk; not redacted in bronze
severity: warning
affects:
  - main_bronze.raw_somerville_crime_raw
  - main_bronze.raw_somerville_crime
  - incnum
  - blockcode
since: 2026-05-13
status: active
---

# Crime data carries source-level PII risk; not redacted in bronze

The Somerville Police crime reports dataset
(`main_bronze.raw_somerville_crime`, sourced from Socrata `aghs-hqvg`)
is ingested at bronze with no project-side PII transformation. Silver-
layer redaction is MVP 3 work; until then, the bronze table is
**gated** — not surfaced publicly, not exposed through the Answer
Agent's trust contract on resident-facing surfaces, and not joined to
311 in any analyst-facing artifact without intentional review.

## What's PII-adjacent in this dataset

What we found via empirical schema inspection on 2026-05-13 (22,325 rows,
2017–2026):

- **No names, addresses, phone numbers, email addresses, or birthdates.**
  The columns are limited to `incnum`, `day_and_month`, `year`,
  `police_shift`, `offensecode`, `offense`, `incdesc`, `offensetype`,
  `category`, `blockcode`, `ward`. A scan of `incdesc` found 0 rows
  containing `@` or phone-number-shaped patterns.
- **`incdesc` is generic NIBRS legal text**, not victim-specific
  narrative. The top 5 most-common `incdesc` values are standard FBI
  category definitions (e.g. "The unlawful taking of articles from a
  motor vehicle, locked or unlocked.").
- **Source-level redaction already applied.** Per the Socrata
  description: "Incidents deemed sensitive by enforcement agencies are
  included in the data set but are stripped of time or location
  information to protect the privacy of victims. For these incidents,
  only the year of the offense is provided."

## What still warrants care

- **`incnum`** could be cross-referenced if you had access to other
  police records (e.g. an FOIA-released file referencing the same
  incident number). Not PII in isolation; a re-identification key in
  combination.
- **`blockcode` + offense + date** could potentially identify an
  individual in a small census block, especially for rare offenses.
  Block granularity is ~750 blocks across Somerville; some blocks
  have very few crime entries per year.
- **Even already-redacted crime data is institutionally sensitive.**
  Surfacing it on a public-facing surface (the portal, the public
  `/chat` SPA) without an explicit "this is OK to expose" sign-off
  treats Somerville's redaction effort as carte blanche rather than as
  consent for analytics use. The opportunistic principle's analyst-
  experience-leads test cuts both ways: protecting the analyst's
  conscience matters too.

## Impact

- Bronze table is not for public consumption until either (a) silver
  redaction lands at MVP 3 with project-side review, or (b) a separate
  Gordon-approved sign-off says "publish bronze as-is is OK."
- The `/profile` portal route auto-picks-up the new bronze table via
  `scripts/profile_tables.py`. Profile shows column shape (distinct
  counts, null %), not row content; reviewing the profile is OK.
- The Answer Agent's trust contract will surface this limitation
  entry when queries touch `main_bronze.raw_somerville_crime*` or
  `incnum` or `blockcode`. Granular `affects:` tokens above keep the
  surfacing tight.
- No fact table (`fct_crime`) or semantic-layer view exists. Adding
  one is deferred until silver lands.

## Workaround

For now: ad-hoc analyst queries against bronze are fine (Gordon-only,
not exposed). Cross-references to 311 by `ward` or `blockcode` work
but are bounded by:

- Ward join requires `TRIM(ward)` on the crime side — bronze preserves
  the source-side space padding (length 15).
- Block code formats differ. 311 stores a 15-character "blockcode"
  padded with spaces when unknown (`"NA             "`); crime stores
  a 15-character census block code without that NA-sentinel pattern.
  They overlap when both are real block codes.

## Resolution path

Plan to land alongside Silver (MVP 3):

1. `dbt/models/silver/stg_somerville_crime.sql` — type casts, ward
   trim, sensitive-incident handling, any project-side redaction the
   review decides is needed.
2. `dbt/models/gold/fct_crime.sql` + `semantics/views/crime.view.yml`
   — promotes to analyst-facing once redaction is reviewed.
3. New limitation entry (or this one updated to `status: resolved`)
   when the bronze gate is lifted.

Until then: bronze stays bronze.
