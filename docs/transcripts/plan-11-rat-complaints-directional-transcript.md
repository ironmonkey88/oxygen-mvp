# Plan 11 — Directional transcript (Phase 3)

**Written before Phase 4.** This is the prediction the retro (Phase 8)
compares the actual Builder Agent session against.

## Opening prompt

Single prompt sent to Builder Agent via
`oxy agentic run --domain builder builder --question "..."`:

> *I want to build a Somerville rat-complaints dashboard. Audience is
> a city analyst asking 4 angles:*
>
> *1. Frequency — total rat complaints across the dataset.*
> *2. Resolution speed — distribution of days from open to close, for
>    closed complaints.*
> *3. Volume trend — rat complaints by year, 2015–present.*
> *4. Service equity — rat complaints by ward, 7 wards.*
>
> *Filter to four specific request_type values:
> `Rats`, `Rodent Assistance Program request`, `Rodent Assistance
> Program inquiry`, `School Rodent Control ` (trailing space is real —
> use TRIM() to handle the source-side padding).*
>
> *Data sources:*
> *- `main_gold.fct_311_requests` (1.17M rows) — fact table*
> *- `main_gold.dim_request_type` — for the rat filter*
> *- `main_gold.dim_status` — for the Closed filter on resolution speed*
> *- `main_gold.dim_ward` — for ward names and area_sqkm on the
>    by-ward charts*
> *- `main_gold.dim_date` — for the year dimension on the trend chart*
>
> *Resolution-time derivation: `most_recent_status_dt - date_created_dt`
> for rows where `most_recent_status_dt IS NOT NULL` AND status =
> 'Closed'. Median is more informative than mean (long-tail
> distribution — median ~4 days, p95 ~1752 days).*
>
> *Trust contract on the dashboard — surface these on the rendered app:*
> *- A "last refreshed" line reading from
>    `main_admin.fct_pipeline_run_raw.run_completed_at` where
>    `run_status='success'`*
> *- Citations on each chart naming the source tables*
> *- The `location-ward-block-only` limitation on ward-keyed charts
>    (167 NULL-ward rows out of 14K)*
>
> *Output file: `apps/rat_complaints_by_ward.app.yml`. Add any new
> measures to `semantics/views/requests.view.yml` if cleaner. I'll
> approve each file edit individually.*

## Expected Builder moves (directional, not prescriptive)

What I think Builder will do, in roughly this order:

1. **`search_files`** to locate the existing views and fact tables.
2. **`read_file`** on `semantics/views/requests.view.yml` to see the
   existing measures.
3. **`read_file`** on `dbt/models/gold/fct_311_requests.sql` or
   `schema.yml` to confirm the column names (`date_created_dt`,
   `most_recent_status_dt`, `ward`).
4. **`execute_sql`** to verify the rat-type filter returns the
   expected 14K row count.
5. **Propose `apps/rat_complaints_by_ward.app.yml`** in one
   `propose_change` event with 4 tasks (frequency, resolution-speed,
   trend, equity) + 4 display blocks (probably summary card, histogram
   or grouped bar for resolution buckets, line for trend, bar for
   ward).
6. **Possibly propose updates to `semantics/views/requests.view.yml`**
   adding measures like `avg_resolution_days_closed` and
   `median_resolution_days_closed` — though my prompt didn't ask for
   semantic-layer additions explicitly, Builder may suggest them.
7. **Builder will NOT spontaneously add trust signals** (last
   refreshed line, citations, limitation references) — those will
   come from a follow-up prompt iteration. This is a customer-feedback
   observation worth retro-ing.
8. **Builder will NOT use a dedicated `run_app` tool** for the
   verification loop. Per Phase 1 G6 finding, Builder runs SQL via
   `execute_sql` directly. It may not run all 4 angles end-to-end
   before proposing the file; the analyst (Code) prompts for that.

## Expected file shape

`apps/rat_complaints_by_ward.app.yml` (sketched):

```yaml
name: rat_complaints_by_ward
description: "Somerville rat complaints — frequency, resolution speed, volume trend, ward equity"

tasks:
  - name: total_rat_complaints
    type: execute_sql
    database: somerville
    sql_query: |
      SELECT COUNT(*) AS total
      FROM main_gold.fct_311_requests f
      JOIN main_gold.dim_request_type rt USING (request_type_id)
      WHERE TRIM(rt.request_type) IN ('Rats', 'Rodent Assistance Program request',
        'Rodent Assistance Program inquiry', 'School Rodent Control')

  - name: resolution_speed_distribution
    type: execute_sql
    database: somerville
    sql_query: |
      SELECT DATE_DIFF('day', date_created_dt, most_recent_status_dt) AS days_to_close,
             COUNT(*) AS n
      FROM main_gold.fct_311_requests f
      JOIN main_gold.dim_request_type rt USING (request_type_id)
      JOIN main_gold.dim_status s USING (status_id)
      WHERE s.status = 'Closed' AND most_recent_status_dt IS NOT NULL
        AND TRIM(rt.request_type) IN (...)
      GROUP BY 1 ORDER BY 1
      -- might bucket into 0-7d / 8-30d / 31-90d / 91-365d / >1yr

  - name: volume_by_year
    type: execute_sql
    database: somerville
    sql_query: |
      SELECT EXTRACT(YEAR FROM date_created_dt) AS yr, COUNT(*) AS n
      FROM main_gold.fct_311_requests f
      JOIN main_gold.dim_request_type rt USING (request_type_id)
      WHERE TRIM(rt.request_type) IN (...)
      GROUP BY 1 ORDER BY 1

  - name: complaints_by_ward
    type: execute_sql
    database: somerville
    sql_query: |
      SELECT w.ward, w.ward_name, w.area_sqkm, COUNT(*) AS n
      FROM main_gold.fct_311_requests f
      JOIN main_gold.dim_request_type rt USING (request_type_id)
      LEFT JOIN main_gold.dim_ward w ON f.ward = w.ward
      WHERE TRIM(rt.request_type) IN (...)
      GROUP BY w.ward, w.ward_name, w.area_sqkm
      ORDER BY w.ward

display:
  - type: summary_card    # frequency
  - type: bar_chart       # resolution speed (bucketed)
  - type: line_chart      # volume trend by year
  - type: bar_chart       # ward equity

# trust signals to add (probably from follow-up iteration)
# - last_refreshed task reading fct_pipeline_run_raw
# - markdown footer with citations + limitation references
```

The exact `display` syntax may vary — Builder reads Oxygen's app
schema and adapts. Don't pre-judge the structure.

## What success looks like

- Builder produces a syntactically-valid `apps/rat_complaints_by_ward.app.yml`
  that I (Code) accept via `oxy agentic answer --answer Accept ...`.
- `oxy validate --file apps/rat_complaints_by_ward.app.yml` exits 0.
- A subsequent Builder run can execute the SQL inside each task and
  confirm the row counts match the Phase 2 pre-flight (14K total,
  ward distribution 1,250–2,661, resolution-time stats consistent
  with median ~4d / avg 300d).
- Trust signals: at minimum, the analyst can ask "where does this
  data come from" of the Answer Agent and get the right answer. The
  agent's existing trust contract handles the chat surface; the
  dashboard surface inherits via the same source tables.

## What "different from prediction" would look like

- Builder proposes a dramatically different file shape (e.g., one
  task per ward instead of grouping by ward in a single task).
- Builder spontaneously adds the trust-signals tasks without
  prompting.
- Builder fails the propose_change step with the same range overlap
  error pattern observed in the Phase 1 G4 probe.
- Builder edits unrelated files (e.g., proposes new measures on
  semantics/views/requests.view.yml without being asked).

Any of those would be noted in the Phase 8 retro and counted as
customer-feedback findings to Oxy.

## Carry-forward question resolutions

Per the overnight prompt:

- **Q1 (neighborhood scope):** ward-only. Use `dim_ward`. No
  neighborhood mapping. The 167 NULL-ward rows surface via the
  existing `location-ward-block-only` limitation. Recorded here for
  the retro.
- **Q2 (transcript as portal artifact):** save to
  `docs/transcripts/plan-11-rat-complaints-builder-session.md`
  repo-side. Portal exposure deferred to a follow-on plan.
