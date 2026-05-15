---
id: somerville-at-a-glance-acs-scope
title: Somerville at a Glance -- pre-aggregated KPI snapshot, not microdata
severity: low
affects:
  - main_bronze.raw_somerville_at_a_glance_raw
  - raw_somerville_at_a_glance
  - somerville_at_a_glance
since: 2026-05-14
status: active
---

# Somerville at a Glance: what it is and what it isn't

The 749-row at-a-glance dataset is a **pre-aggregated KPI summary**
drawn mostly from Census + ACS data 2010-2023, with some historical
population back to 1850. One row per (topic, description, year,
geography). 25 distinct topics across demographics, housing,
education, income, transportation, and language.

It is the natural data source for orienting context ("what is
Somerville?") -- a new analyst or outside visitor should be able to
look at it and quickly understand the city's scale, demographic
shape, and trends.

## What it is

- Polished, ready-to-chart KPI values.
- Side-by-side with Massachusetts comparator values where applicable.
- Time series for trend topics (Population, Median Rent Overtime,
  Median Household Income Overtime, etc.).

## What it isn't

- **Not microdata.** This dataset cannot answer "how many Somerville
  residents in age bracket X have income Y" -- those questions require
  ACS Public Use Microdata Sample (PUMS) joins which are out of scope
  for this project.
- **Not joined to operational data.** There is no ward column. The
  metrics are city-wide or state-wide; ward-level demographic context
  for joining to 311 / crime / permits / citations is not in this
  dataset. For ward-level demographic joins, ACS tract-level data
  would need to be ingested separately and reaggregated to the ward
  geometry (silver/gold work, MVP 3+).
- **Not the authoritative source.** The dataset is derived; if a
  number is contested, the authoritative ACS table (via
  Census.gov) is the citation, not this snapshot. Treat
  `raw_somerville_at_a_glance` as a convenience-shaped view of public
  ACS values, not an independent ground truth.
- **Not column-level rich.** Just topic + description + year + value
  + units + geography. Enough for orientation, not enough for
  fine-grained demographic analysis.

## Update cadence

ACS releases annually; the city refreshes this dataset on an
ad-hoc cadence (`rowsUpdatedAt = 2026-05-11` at first ingest).
Re-ingest manually -- not in `run.sh`.

## Status

- Bronze: as-is. Caveats live here and are surfaced by the Answer
  Agent's trust contract when at-a-glance-affecting queries are
  asked.
- Silver / gold: probably never. The source shape is already
  analytically convenient for the orienting-context use case.
- Portal: used directly by the /somerville info page generator
  (Prompt 11 Phase E). The page is informational, not analytical;
  it lifts values straight from this bronze view.
