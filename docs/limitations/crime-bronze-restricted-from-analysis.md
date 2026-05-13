---
id: crime-bronze-restricted-from-analysis
title: Crime bronze table is for lineage and reprocessing — not analysis
severity: warning
affects:
  - main_bronze.raw_somerville_crime_raw
  - main_bronze.raw_somerville_crime
since: 2026-05-13
status: active
---

# Crime bronze table is for lineage and reprocessing — not analysis

`main_bronze.raw_somerville_crime` (and its dlt-owned raw merge target
`raw_somerville_crime_raw`) are not for analytical use. Analyst-facing
crime queries hit `main_gold.fct_crime_incidents` and its dims. Bronze
exists for lineage (track every row back to a specific Socrata pull)
and reprocessing (if the gold transformation needs to be rebuilt).

Plan 13 (2026-05-13) renamed this limitation from
`crime-data-pii-unredacted-in-bronze`. The original framing centered
on a presumed PII risk in the bronze columns. The audit (Plan 12
Phase 3 + Plan 13 design) found the PII surface is small and largely
source-redacted — but the layer-discipline reason for the gating
still applies:

- Bronze preserves source-side artifacts (space-padded ward, the
  9-char `1xxxxxxxx` sensitive-incident incnums, the 15-char census
  block codes, etc.) without cleanup. Querying bronze directly means
  every analyst would have to handle the source's idiosyncrasies.
- Gold (`fct_crime_incidents`) is the curated analyst surface where
  TRIM, type casts, multi-code-flagging, and date derivation are
  applied once.

## PII audit summary

- **No names, addresses, phone numbers, email, or DOB** in any
  column.
- **`incdesc` is generic NIBRS legal text**, not victim-specific
  narrative. Top values are standard FBI category definitions
  repeated across thousands of rows. The gold layer drops the
  column for that reason (redundant with `offense` / `offense_type` /
  `offense_category` plus `dim_offense_code`'s denormalized
  definition coverage).
- **`incnum` (case_number at gold) is a public reference** — NIBRS
  case numbers appear routinely in police logs. Kept on the gold
  fact so analysts can back-reference specific incidents in the
  public Somerville Police log.
- **Source-level redaction** already strips time + location from
  sensitive incidents (2,798 rows = 12.5%). These rows have NULL
  `day_and_month` and NULL `blockcode`; gold surfaces this with the
  `incident_year_only` flag and the
  `crime-sensitive-incidents-no-month` limitation.

The implicit-identifiability concern (rare offense + small ward +
specific date) is real and bounded by the source's day-stripping for
the categories most at risk. Gold inherits the source's redaction
posture.

## Workaround

For analyst questions: query `main_gold.fct_crime_incidents` and its
companion dims (`dim_offense_code`, `dim_offense_category`,
`dim_ward`) via the `public_safety` topic in Airlayer. The Answer
Agent's trust contract surfaces the relevant gold-level limitations
on any query that touches the affected columns.

For lineage / reprocessing: read bronze directly, but cite the
limitation in any output. The `_first_seen_at`, `_extracted_at`,
and `_extracted_run_id` columns trace every row back to the
specific pipeline run that produced it.

## Resolution path

Plan to land alongside Silver (MVP 3). If MVP 3 introduces a
project-side silver layer, the bronze gate would relax for power
users on a per-investigation basis, while the routine analyst path
stays on gold. Until then, gold is the only analyst surface.
