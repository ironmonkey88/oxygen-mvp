# Plan 12 — Additional Data Sources: Socrata Inventory + Wards + Crime

**Status:** active overnight execution (2026-05-13).
**Type:** data substrate growth — knowledge-graph expansion (PRODUCT_NOTES.md
entry 1, human-driven form).
**Plan slot:** Plan 12, next after Plan 11 scoping.

## Why this plan exists

The four-MVP build sequence (BUILD.md §5) commits to the analyst asking
questions through the entire Knowledge Product Pipeline. To answer
questions richer than "what happened in 311?", the warehouse needs more
data than 311 alone. This plan grows the substrate.

The previous queue framing was "weather first, then ward + demographics."
Gordon's overnight reorder makes it **wards + crime first**, with weather
deferred. Rationale: wards unlocks ward-level mapping (portal hero
TODO + future neighborhood analysis); crime is the closest data shape to
311 and lets the analyst start asking equity questions across services.

The first deliverable (Socrata inventory) is framing pre-work — produces
the catalog Code and Gordon will triage against in future plans. The
catalog itself is also a Knowledge Product on the platform — a queryable
view of what's available.

This plan is the first concrete instance of PRODUCT_NOTES.md entry 1
("knowledge-graph expansion") in human-driven form. Eventually the
analytics agent would surface the gap and a chief-researcher agent would
ingest the new source. Tonight, Code + Gordon do it directly.

## Inputs (from prior session + the overnight prompt)

| Decision | Answer |
|---|---|
| **Reorder of "additional data sources" queue** | Wards + crime first; weather deferred |
| **Inventory scope** | All ~50 datasets on `data.somervillema.gov`; one row per dataset; full metadata; row count via SODA `count(*)` for tabular datasets; skipped for blob |
| **Inventory persistence** | `main_admin.fct_socrata_catalog_raw` (Python-owned, `_raw` suffix); append-only with `cataloged_at` |
| **Wards ingestion pattern** | Static reference data — NOT the 311 dlt-template pattern. Simple one-shot script; no systemd timer; re-runnable manually |
| **Crime ingestion pattern** | Fact-shaped, time-series — adapt the existing `dlt/somerville_311_pipeline.py` template |
| **PII for crime** | Bronze only; no redaction overnight (MVP 3 work); document PII in a limitations entry; gate `/profile` exposure |
| **Honest reporting** | Better to ship 1 of 3 cleanly than 3 of 3 sloppily; partial completion is acceptable |

## Phases

### Phase 1 — Socrata inventory for Somerville

**Deliverable:**

- `scripts/build_socrata_inventory.py` — pages through the Socrata
  Discovery API at `https://api.us.socrata.com/api/catalog/v1`,
  computes `count(*)` per tabular dataset, writes to
  `main_admin.fct_socrata_catalog_raw` with a fresh `cataloged_at`.
- `scripts/generate_socrata_inventory_page.py` — reads the latest
  catalog snapshot, writes `docs/socrata-inventory.md` grouped by
  domain category with Code's "why this might matter" annotation
  per dataset + top-3-plus recommendation menu.
- `docs/socrata-inventory.md` — committed output.

**Out of scope for Phase 1:**
- No actual data ingestion beyond the catalog itself
- No `dbt` schema.yml entries for `*_raw` admin tables (Python-owned
  by convention, per Plan 1a / Plan 1b precedent)
- No non-Socrata sources (ACS, OSM, MassGIS)

### Phase 2 — Ward boundaries

**Pre-flight:**
1. Search the inventory for ward-related datasets
2. Confirm shape (tabular vs blob, geometry column if tabular,
   downloadable format if blob)
3. Fall back to Somerville GIS portal / MassGIS / OSM Overpass if
   Socrata has nothing usable

**If usable source found:**
- `main_bronze.raw_somerville_wards` (1 row per ward, polygon + ward
  number + name)
- `main_gold.dim_ward` (ward_id, ward_number, ward_name, geometry)
- `dbt/models/{bronze,gold}/...sql` + schema.yml
- `semantics/views/wards.view.yml` + add to
  `semantics/topics/service_requests.topic.yml`
- Validate via `airlayer query -x`
- Run `./run.sh` to regenerate `/erd`, `/profile`, `/trust`

**If no usable source:** `docs/limitations/wards-no-clean-geospatial-source.md`;
skip gold + semantic; move on.

**Out of scope:** portal hero map SVG; 311 ward inference backfill;
adding wards to `./run.sh` (one-shot).

### Phase 3 — Crime data (bronze only)

**Pre-flight:**
1. Pick the most analogous-to-311 dataset (incident-grain, geo-tagged,
   multi-year)
2. Verify tabular
3. Inspect schema for PII columns
4. Verify row count is sane (<10M)

**Ingestion:**
- `dlt/somerville_crime_pipeline.py` adapted from
  `dlt/somerville_311_pipeline.py`
- `main_bronze.raw_somerville_crime` with audit columns matching the
  311 pattern
- `dbt/models/bronze/raw_somerville_crime.sql` passthrough view +
  schema.yml entries
- `docs/limitations/crime-data-pii-unredacted-in-bronze.md`
- `docs/schema.sql` updated with the new bronze DDL
- `./run.sh` addition only if daily refresh fits; otherwise a separate
  systemd timer (probably weekly given the dataset's documented
  refresh cadence)

**Honest reporting:**
- `/profile` and `/trust` auto-pick-up the new bronze table; verify
  PII exclusion at the profile level
- Limitations entry surfaces via the Answer Agent's trust contract

**Out of scope:** silver / gold / semantic / public surface / join to
311 / crime-by-ward analysis. All daytime decisions.

## Sign-off gates

**Static-artifact (all phases):**
- [ ] `main_admin.fct_socrata_catalog_raw` populated; latest snapshot
  has 49 rows
- [ ] `docs/socrata-inventory.md` exists, renders, lists all 49
  datasets with annotations
- [ ] Phase 2: either bronze + gold + semantic for wards OR a
  limitations entry explaining why not
- [ ] Phase 3: `dlt/somerville_crime_pipeline.py` + bronze model +
  schema.yml + PII limitation entry exist
- [ ] LOG.md Plans Registry row Plan 12; status = `done` if all three
  phases shipped, `partial` if one phase blocked

**Live-functional (re-verified at the end):**
- [ ] `.venv/bin/python scripts/build_socrata_inventory.py` runs clean
  on a fresh invocation
- [ ] If wards ingested: `airlayer query -x` resolves a wards-joined
  question successfully
- [ ] If crime ingested: `SELECT COUNT(*) FROM main_bronze.raw_somerville_crime`
  matches the row count from the inventory
- [ ] `./run.sh manual` exits successfully with the new bronze tables
  in scope (assuming crime bronze landed in the run order)

## Out of scope (whole plan)

- Plan 11 execution (still scoping — pending Gordon's review)
- PII redaction for crime (MVP 3)
- Crime-by-ward joined analysis (post-bronze daytime work)
- Portal hero ward map SVG (Session 28 follow-up; unblocked by
  Phase 2 but not part of Plan 12)
- Weather / ACS / non-Socrata sources (follow-on plans)
- Silver layer anywhere (MVP 3)
