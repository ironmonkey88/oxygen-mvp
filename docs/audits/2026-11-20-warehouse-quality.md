# Civic Pulse warehouse quality audit, 2026-11-20

Asked by Gordon ("fix tech debt before adding to it"), against stack-in-a-box METHODOLOGY R9-R22 and
STANDARDS (layer meanings R19: bronze raw; silver cleansed and related; gold easy to use; metrics "gold plus").
Evidence: the read-only MCP snapshot built 2026-11-20 11:22 UTC, the public /trust page for run 343bbb33
(161 pass, 4 warn, 0 fail), and this repo at ceb6481. Nothing was changed while auditing.

Tags: [CERTAIN] queried or read in the repo; [PROBABLY]; [GUESS].

## What is healthy
- Daily run green; 165 tests recorded per run on /trust; row-count drift guard on 311 by year. [CERTAIN]
- 311 is current (latest request 2026-11-20), keys unique (1,241,277 ids), no future dates, no status before creation. [CERTAIN]
- 311 status history (CP-12) is running; its grain tests pass. [CERTAIN]
- Snapshot for MCP copies only allow-listed columns; permit free text and citation addresses are excluded. [CERTAIN]
- 39 limitations entries, surfaced by the agent. [CERTAIN]

## Findings, worst first

| # | Finding | Evidence | Fix |
|---|---|---|---|
| C1 | **Three of six sources are not refreshed.** Permits read dataset `vxgw-vmky`, which stopped at application date 2023-05-15; the live permits dataset is `nneb-s3f7`. At-a-glance KPIs and the happiness survey were last extracted 2026-05-15. None of the three is in `run.sh`. | `dlt/somerville_permits_pipeline.py:34`; `fct_permits` max application 2023-05-15, `_extracted_at` 2026-05-15; `fct_somerville_kpi` `_extracted_at` 2026-05-15 [CERTAIN] | Switch permits to `nneb-s3f7` (Yu Bei order); put every source in the daily run or a stated schedule |
| C2 | **No freshness tests anywhere.** That is how C1 went unnoticed for three years. | no `freshness:` in `dbt/models/bronze/schema.yml` [CERTAIN] | Source freshness per source with its real cadence (311 daily; crime and citations monthly: both currently end 2026-10-19) |
| C3 | **No silver layer (R19).** Row-level facts and dimensions sit in gold; silver has one model (`stg_happiness_survey`). Cleaning, typing and keys happen inside gold models. | `dbt/models/silver/` [CERTAIN] | Build silver (typed, deduped, keyed, conformed dims, quality flags, personal data removed); keep current gold names as views so MCP, evals and Wheelhouse don't break |
| C4 | **Personal data in gold and the public endpoint.** `fct_permits` carries `address`, `latitude`, `longitude` and they are in the public MCP snapshot. Crime bronze is unredacted (documented). | `build_ro_snapshot.py` ALLOWED; `fct_permits` columns [CERTAIN] | Gordon to decide: permit addresses are public records, but R19 says personal data leaves in silver. Default: drop lat/long and address from the snapshot until silver exists |
| C5 | **No quality flags, unit tests or plausibility bounds.** Bad values pass silently: 5 citations with speeds over 150 mph or below 0; crime has 2,798 year-only dates and 2,920 rows (12%) with no ward; 3 crime not-null tests warn every run. | queries on `fct_citations`, `fct_crime_incidents`; /trust warns [CERTAIN] | `quality` column (ok/suspect/invalid/missing) in silver; unit test per rule; plausibility seed |
| C6 | **Methodology rules R9-R18 not propagated.** Bronze tests not set to warn-by-newest-load, no append-by-load, no on-box diagnosis, no hygiene sweep, no reconciliation or known-answer tests, no coverage gate. | METHODOLOGY pending-propagation table [CERTAIN] | One order per rule group (below) |
| C7 | **Semantic layer on Airlayer**, which Oxygen no longer develops; Wheelhouse reads gold through raw SQL, not metrics (R20). | `semantics/views/*.view.yml`; Wheelhouse build scripts [CERTAIN] | CP-8 (ktx), then move Wheelhouse numbers to metrics |
| C8 | **Wheelhouse numbers don't refresh.** The page is a static build from 2026-11-16/17 queries. | `sites/wheelhouse/data/findings.json` in wong-way-server [CERTAIN] | Rebuild from gold/metrics on a schedule, with the data date shown (already shown) |
| C9 | **Evals cover 311 only.** | `evals/questions.yaml` [CERTAIN] | Known-answer questions per source as it moves to silver |
| C10 | KPI table has years back to 1850 (probably "housing built before" style measures). | `fct_somerville_kpi` min year [CERTAIN]; meaning [GUESS] | Check and document |

## Proposed fix order (no new sources until 1-4 are done)
1. **Freshness + schedule** (C1 part, C2): freshness tests on all sources; at-a-glance and survey on a stated schedule; alert on stale.
2. **Permits switch** (C1): Yu Bei order for `nneb-s3f7`, retiring `vxgw-vmky`.
3. **Personal data** (C4): Gordon's call on permit addresses; snapshot follows it.
4. **Silver layer** (C3, C5): 311 first (it feeds Wheelhouse), then crime, citations, permits; quality flags, unit tests, plausibility, reconciliation and known-answer tests; gold names kept as views.
5. **R9-R18 propagation** (C6) and a coverage gate.
6. **ktx + metrics** (C7, CP-8), then Wheelhouse on metrics with a scheduled rebuild (C8).
7. Evals per source (C9), KPI check (C10).

Then the first new sources from the Thirsty Scholar list (crashes, Focus Areas goals, dispatch calls).
