{% docs __overview__ %}

# Somerville Analytics — Data dictionary

<a href="/" style="display:inline-block;padding:8px 16px;margin:4px 0 20px;background:#e8f0eb;border:1px solid #b8d4c0;border-radius:4px;color:#1e4d2b;font-weight:600;text-decoration:none;font-size:14px">&larr; Back to Somerville Analytics portal</a>

This is the data dictionary for an independent, resident-built data platform exploring Somerville's public Open Data. It documents every table and column the platform makes available, with descriptions, relationships, tests, and lineage — so an analyst (or an answer agent) can see exactly what's in the warehouse before asking a question of it. **Not affiliated with the City of Somerville**; the data is the city's public 311 + crime + open-data feeds, the warehouse and dictionary are this project's.

## What's in the warehouse

The platform tracks two topics today:

- **`service_requests`** — Somerville 311 service requests since 2015 (1.17M rows). Volume, resolution speed, ward distribution, category breakdown. The substrate behind most "how is the city operating?" questions.
- **`public_safety`** — Somerville Police crime incidents since 2017 (22K rows). NIBRS-coded offenses, ward + block geography, multi-offense flagging.

Both topics share a `wards` dimension (the same 7-ward geometry) and a `dates` dimension, so cross-topic questions are possible — e.g. "which wards have the highest combined 311 + crime activity?"

## How it's organized

The warehouse is medallion-architected — raw data lands in **bronze**, gets cleaned + business-shaped into **gold**, and the agent + dashboards read from gold. The dictionary on this site mirrors that layering. Roughly:

- **`raw_311_requests`**, **`raw_somerville_crime`** — bronze. Pull-from-source views with audit columns and minimal typing. Useful for lineage and reprocessing; not where analyst questions land.
- **`fct_311_requests`**, **`fct_crime_incidents`** — gold. The fact tables. Each row is a request or incident. These are what the chat agent queries.
- **`dim_ward`**, **`dim_request_type`**, **`dim_offense_code`**, **`dim_offense_category`**, **`dim_status`**, **`dim_date`** — gold dimensions. The lookup tables that make the facts navigable.
- **`fct_pipeline_run_raw`**, **`fct_test_run`**, **`fct_data_profile`**, **`fct_column_profile_raw`** — admin. Pipeline observability + data quality. Used by the [`/trust`](/trust) and [`/profile`](/profile) portal pages.

## How to browse

The left-hand sidebar lists every model. Click a model to see:

- **Description** — what this table holds in plain language.
- **Columns** — names, types, hand-written descriptions, plus any tests dbt runs against them (not-null, unique, accepted-values, relationships to other models).
- **Lineage graph** — the upstream sources and downstream consumers, rendered as an interactive DAG. This is the fastest way to answer "where does this column come from?" or "what breaks if I change this?".

A few useful entry points:

- For analyst-facing questions, start in **`gold`** (`fct_311_requests`, `fct_crime_incidents`, the `dim_*` tables).
- For provenance and reprocessing, **`bronze`** shows what came from the upstream API.
- For pipeline + data-quality observability, **`admin`** has the run records and test results.

## Limits worth knowing

The data dictionary documents what *exists*. It doesn't describe everything the data *can't yet tell you* — for that, the [limitations registry](/trust) is the source of truth. Honest gaps include: sub-ward geography deferred to MVP 3 (`dim_location`); no demographic correlations (no ACS data joined yet); survey-signal columns populated for <1% of rows; sensitive crime incidents have year-only dates. Both the chat agent and each dashboard panel link to relevant entries in the registry when they touch a flagged area.

<a href="/" style="display:inline-block;padding:8px 16px;margin:8px 0;background:#e8f0eb;border:1px solid #b8d4c0;border-radius:4px;color:#1e4d2b;font-weight:600;text-decoration:none;font-size:14px">&larr; Back to Somerville Analytics portal</a>

{% enddocs %}
