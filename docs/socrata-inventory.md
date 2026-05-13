# Socrata Inventory — Somerville Open Data
Auto-generated from `main_admin.fct_socrata_catalog_raw` at 2026-05-13T04:48:49.311340. Source: [`scripts/generate_socrata_inventory_page.py`](../scripts/generate_socrata_inventory_page.py). Refresh with `.venv/bin/python scripts/build_socrata_inventory.py` then re-run the generator.
**Summary.** 49 datasets total on `data.somervillema.gov`. **29 tabular** (SODA-queryable), **20 blob** (map/file/filter — not SODA-queryable, but most are downloadable as shapefile / geojson / image).
## Triage — recommended next ingestions after wards + crime
Code's judgment, ranked. Gordon decides.
### 1. `vxgw-vmky` — Permits
Joins cleanly to 311 by ward + date_created. Lets the analyst answer 'are construction-related 311 complaints rising where permit activity concentrates?' — a development-pressure question that's first on city planners' minds. 64K rows, tabular, well-documented columns. Pairs naturally with the wards + crime work for a planning-and-safety equity narrative.
### 2. `mdb2-mgc7` — Police Data: Computer Aided Dispatch (CAD)
336K rows of calls-for-service — broader than Crime Reports (which only logs incidents that became reports). CAD captures the full demand on police resources. Adding this after Crime Reports lets the analyst separate 'incidents reported' from 'calls placed,' which is the right frame for service-equity questions about police response.
### 3. `wmeh-zuz2` — Somerville Happiness Survey Responses
12K rows over multiple years of community sentiment. The closest Somerville comes to a perception-of-services signal that complements the operational 311/crime data. Pairs with the survey columns already in 311 (`accuracy`, `courtesy`, `ease`, `overallexperience`) for a richer sentiment-vs-operations comparison.
### 4. `qu9x-4xq5` — Bicycle & Pedestrian Counts
2.5K rows. Active-transport observation data. Pairs with crash/citation data for safety-equity analysis (where are pedestrians being counted vs. where are they being struck?). Smaller than the candidates above; include if Gordon wants 4 instead of 3.
### 5. `n5md-vqta` — Neighborhoods
Higher-resolution geospatial than wards. Blob on Socrata (same shape as wards); ingestion uses the same pattern as Plan 12 Phase 2. The clean neighborhood dimension is a Plan 11 carry-forward question (deferred to MVP 3 by default); landing this overnight would move the answer forward.
---
## Full catalog by category
### Business & Economic Development (1 datasets)
#### [Annual Count of Jobs in Somerville](https://data.somervillema.gov/d/pm7h-ga9w) — `pm7h-ga9w`
- **Shape:** **tabular** · 2 columns · 22 rows
- **Last updated:** 2024-03-11T16:17:35
- **Why this might matter:** Annual jobs count. 22 rows. Macro indicator.
### Education (1 datasets)
#### [Afterschool Needs Assessment Survey Responses](https://data.somervillema.gov/d/hpdk-b2g6) — `hpdk-b2g6`
- **Shape:** **tabular** · 60 columns · 738 rows
- **Last updated:** 2026-01-28T18:48:08
- **Why this might matter:** Afterschool needs assessment. Small.
### Environment & Open Space (2 datasets)
#### [Open Space and Recreation Plan Survey](https://data.somervillema.gov/d/vamq-kd64) — `vamq-kd64`
- **Shape:** **tabular** · 31 columns · 710 rows
- **Last updated:** 2025-03-12T14:13:52
- **Why this might matter:** Open Space & Recreation Plan survey. Pairs with parks/open-space spatial layer.
#### [2015 Solar Survey Responses](https://data.somervillema.gov/d/6x35-pz53) — `6x35-pz53`
- **Shape:** **tabular** · 20 columns · 336 rows
- **Last updated:** 2015-04-27T17:11:11
- **Why this might matter:** 2015 Solar Survey responses. Historical, narrow scope.
### GIS Data (19 datasets)
#### [2015 MassOrtho Aerial Image](https://data.somervillema.gov/d/5ebe-mbbc) — `5ebe-mbbc`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2019-09-24T19:48:35
- **Why this might matter:** 2015 aerial imagery (large file). Not analyst-queryable.
#### [Buildings](https://data.somervillema.gov/d/uzdd-gyjv) — `uzdd-gyjv`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T10:48:10
- **Why this might matter:** Building footprints. Spatial polygons. Useful for property-grain analysis later.
#### [City Limits](https://data.somervillema.gov/d/pz4k-wh6e) — `pz4k-wh6e`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T10:52:36
- **Why this might matter:** City boundary polygon. One row. Useful for clipping spatial joins to Somerville.
#### [Contours 1 Ft](https://data.somervillema.gov/d/i28f-q9cg) — `i28f-q9cg`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T10:57:11
- **Why this might matter:** 1-ft contour lines. Specialized GIS. Low priority for analyst questions.
#### [FY2025 Tax Parcels](https://data.somervillema.gov/d/gw4w-w7cw) — `gw4w-w7cw`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2024-01-08T22:40:43
- **Why this might matter:** Tax parcel polygons. Finest-grained property data. MVP 3+ candidate; PII-adjacent (owner names may appear).
#### [Fire Response Districts](https://data.somervillema.gov/d/hm5m-dtda) — `hm5m-dtda`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:00:23
- **Why this might matter:** Fire response district polygons.
#### [Fire Stations](https://data.somervillema.gov/d/vjwd-26r7) — `vjwd-26r7`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:01:56
- **Why this might matter:** Fire station locations.
#### [Impervious Surfaces](https://data.somervillema.gov/d/yswj-3fdd) — `yswj-3fdd`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2021-02-10T19:35:28
- **Why this might matter:** Impervious surfaces polygons. Useful for stormwater + climate questions.
#### [Neighborhoods](https://data.somervillema.gov/d/n5md-vqta) — `n5md-vqta`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:03:46
- **Why this might matter:** Neighborhood polygons. Higher-resolution than wards. MVP 3 candidate for `dim_location`.
#### [Open Space](https://data.somervillema.gov/d/9i64-4hby) — `9i64-4hby`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-06-08T11:05:04
- **Why this might matter:** Open space (parks etc) polygons. Useful for accessibility + service-equity questions.
#### [Parking Meters](https://data.somervillema.gov/d/jich-f4v9) — `jich-f4v9`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:11:37
- **Why this might matter:** Parking meter locations.
#### [Place Names](https://data.somervillema.gov/d/y6ii-trws) — `y6ii-trws`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:13:17
- **Why this might matter:** Place names (POI). Reference layer.
#### [Police Stations](https://data.somervillema.gov/d/9yqy-rex4) — `9yqy-rex4`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:14:55
- **Why this might matter:** Police station locations.
#### [Polling Places](https://data.somervillema.gov/d/9xw5-tezf) — `9xw5-tezf`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:16:06
- **Why this might matter:** Polling place locations.
#### [Precincts](https://data.somervillema.gov/d/da4y-vuae) — `da4y-vuae`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:17:42
- **Why this might matter:** Voting precinct polygons. Finer-grained than wards. Plan 12+ candidate.
#### [Streets](https://data.somervillema.gov/d/7jtq-qmnf) — `7jtq-qmnf`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2018-04-11T12:48:26
- **Why this might matter:** Street centerlines. Useful for routing / proximity questions; lower priority than wards.
#### [Trash Receptacles](https://data.somervillema.gov/d/bpsf-vg2d) — `bpsf-vg2d`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:22:31
- **Why this might matter:** Trash receptacle locations.
#### [Wards](https://data.somervillema.gov/d/ym5n-phxd) — `ym5n-phxd`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:23:55
- **Why this might matter:** Ward polygons. **Plan 12 Phase 2 target** — blob-only on Socrata, downloadable; format check pending. Unlocks ward-level mapping + portal hero TODO.
#### [Zoning & Overlay Districts](https://data.somervillema.gov/d/crrw-ex2a) — `crrw-ex2a`
- **Shape:** *blob (file)* · 0 columns · — rows
- **Last updated:** 2017-04-12T11:30:14
- **Why this might matter:** Zoning & overlay districts. Spatial. Pairs with Permits for development-pressure analysis.
### Geography & Demographics (1 datasets)
#### [Somerville at a Glance](https://data.somervillema.gov/d/jnde-mi6j) — `jnde-mi6j`
- **Shape:** **tabular** · 6 columns · 749 rows
- **Last updated:** 2026-05-11T19:58:46
- **Why this might matter:** Somerville at a Glance — KPI snapshot dataset.
### Government & Finance (8 datasets)
#### [311 Service, Information, and Feedback Requests](https://data.somervillema.gov/d/4pyi-uqq6) — `4pyi-uqq6`
- **Shape:** **tabular** · 22 columns · 1,170,637 rows
- **Last updated:** 2026-05-12T06:01:11
- **Why this might matter:** **Already ingested.** Source for `main_bronze.raw_311_requests_raw`. The MVP's primary fact table.
#### [Applications for Permits and Licenses](https://data.somervillema.gov/d/nneb-s3f7) — `nneb-s3f7`
- **Shape:** **tabular** · 51 columns · 101,682 rows
- **Last updated:** 2026-05-12T19:02:38
- **Why this might matter:** Permit applications (pre-approval). 100K rows. Complements the Permits dataset.
#### [Website Analytics](https://data.somervillema.gov/d/754v-8e35) — `754v-8e35`
- **Shape:** **tabular** · 5 columns · 22,948 rows
- **Last updated:** 2023-05-16T04:32:57
- **Why this might matter:** Website analytics. 23K rows of page-view data. Operational; low analyst priority.
#### [Participatory Budgeting Voter Demographics](https://data.somervillema.gov/d/pdjd-r9yq) — `pdjd-r9yq`
- **Shape:** **tabular** · 16 columns · 2,987 rows
- **Last updated:** 2023-12-06T21:44:14
- **Why this might matter:** PB voter demographics. 3K rows.
#### [Participatory Budgeting Submissions](https://data.somervillema.gov/d/brrj-v9a4) — `brrj-v9a4`
- **Shape:** **tabular** · 11 columns · 966 rows
- **Last updated:** 2023-12-06T21:39:34
- **Why this might matter:** PB submissions. 966 rows.
#### [Capital Investment Plan Projects FY16-26](https://data.somervillema.gov/d/wz6k-gm5k) — `wz6k-gm5k`
- **Shape:** **tabular** · 33 columns · 58 rows
- **Last updated:** 2016-02-09T19:48:49
- **Why this might matter:** Capital Investment Plan FY16–26. 58 rows. Useful for spending-vs-need ward analysis.
#### [Participatory Budgeting Submission Demographics](https://data.somervillema.gov/d/52dh-yc6q) — `52dh-yc6q`
- **Shape:** **tabular** · 5 columns · 26 rows
- **Last updated:** 2023-12-06T21:35:08
- **Why this might matter:** PB demographic submissions. 26 rows. Demographic-equity in PB process.
#### [Participatory Budgeting Voting Results](https://data.somervillema.gov/d/2tt6-zua8) — `2tt6-zua8`
- **Shape:** **tabular** · 10 columns · 20 rows
- **Last updated:** 2023-12-06T21:48:00
- **Why this might matter:** PB voting results. 20 rows.
### Health & Wellbeing (4 datasets)
#### [Somerville Happiness Survey Responses](https://data.somervillema.gov/d/wmeh-zuz2) — `wmeh-zuz2`
- **Shape:** **tabular** · 150 columns · 12,583 rows
- **Last updated:** 2025-11-25T20:19:25
- **Why this might matter:** Happiness Survey responses. 12K rows. Multi-year, cross-cutting community sentiment.
#### [Americans with Disabilities Act Community Survey Results](https://data.somervillema.gov/d/usj9-kz3f) — `usj9-kz3f`
- **Shape:** **tabular** · 51 columns · 635 rows
- **Last updated:** 2024-04-16T13:55:27
- **Why this might matter:** ADA accessibility community survey. Small (635 rows); pairs with sidewalk-related 311 categories.
#### [Parks and Recreation Program Feedback Survey Results](https://data.somervillema.gov/d/brzm-dycd) — `brzm-dycd`
- **Shape:** **tabular** · 44 columns · 448 rows
- **Last updated:** 2026-02-27T16:58:03
- **Why this might matter:** Parks & Rec program feedback. Small (448 rows).
#### [Winter Warming Center 2024/2025 Resident Feedback Survey Responses](https://data.somervillema.gov/d/e7ix-nqn6) — `e7ix-nqn6`
- **Shape:** **tabular** · 23 columns · 81 rows
- **Last updated:** 2025-11-26T16:00:29
- **Why this might matter:** Winter Warming Center 2024/25 feedback. Small.
### Planning & Development (2 datasets)
#### [Permits](https://data.somervillema.gov/d/vxgw-vmky) — `vxgw-vmky`
- **Shape:** **tabular** · 10 columns · 64,521 rows
- **Last updated:** 2023-05-16T04:32:56
- **Why this might matter:** Building/zoning permits. 64K rows. Useful for development-pressure analysis joined to 311 (construction-related complaints vs. permit activity).
#### [Somerville School Building Project Community Survey Responses](https://data.somervillema.gov/d/qc8i-5r57) — `qc8i-5r57`
- **Shape:** **tabular** · 65 columns · 2,429 rows
- **Last updated:** 2025-10-28T16:09:20
- **Why this might matter:** School Building Project community feedback. Small narrow scope.
### Public Safety (6 datasets)
#### [Police Data: Computer Aided Dispatch (CAD)](https://data.somervillema.gov/d/mdb2-mgc7) — `mdb2-mgc7`
- **Shape:** **tabular** · 10 columns · 336,222 rows
- **Last updated:** 2026-04-28T06:03:06
- **Why this might matter:** Calls for service / dispatch records. 336K rows — broadest police feed. Heavier ingestion; potential MVP 3+ candidate when crime-by-equity scope expands.
#### [Police Data: Traffic Citations](https://data.somervillema.gov/d/3mqx-eye9) — `3mqx-eye9`
- **Shape:** **tabular** · 14 columns · 67,311 rows
- **Last updated:** 2026-04-28T06:03:29
- **Why this might matter:** Traffic citations issued. 67K rows. Useful for enforcement-equity questions (do citations cluster by ward?).
#### [Police Data: Crime Reports](https://data.somervillema.gov/d/aghs-hqvg) — `aghs-hqvg`
- **Shape:** **tabular** · 11 columns · 22,325 rows
- **Last updated:** 2026-04-28T06:03:11
- **Why this might matter:** Crime incidents 2017–present, ward + block_code geo, daily refresh with 1-mo delay. Sensitive incidents stripped of time/location at source. **Plan 12 Phase 3 target.**
#### [Motor Vehicle Crash Reports (2010-2018)](https://data.somervillema.gov/d/ezmv-8wys) — `ezmv-8wys`
- **Shape:** **tabular** · 89 columns · 4,059 rows
- **Last updated:** 2018-09-17T16:28:10
- **Why this might matter:** Motor vehicle crashes 2010–2018. Historical only; no recent updates. Less useful unless asking historical questions.
#### [Police Data: Crashes](https://data.somervillema.gov/d/mtik-28va) — `mtik-28va`
- **Shape:** **tabular** · 35 columns · 3,341 rows
- **Last updated:** 2026-04-28T06:02:26
- **Why this might matter:** Vehicle crash records from SPD. Smaller than Crime Reports (3K rows). Useful as supplemental safety/equity context.
#### [Public Safety for All Community Survey Results](https://data.somervillema.gov/d/9a8v-ve6k) — `9a8v-ve6k`
- **Shape:** **tabular** · 85 columns · 1,295 rows
- **Last updated:** 2023-10-18T18:05:08
- **Why this might matter:** Public Safety community survey. Pairs with crime data for perception-vs-reality analysis.
### Transportation & Mobility (4 datasets)
#### [City of Somerville Parking Permits](https://data.somervillema.gov/d/xavb-4s9w) — `xavb-4s9w`
- **Shape:** **tabular** · 10 columns · 288,530 rows
- **Last updated:** 2020-12-07T16:34:26
- **Why this might matter:** Parking permits issued. 288K rows. Useful for car-ownership + ward-level questions.
#### [Bicycle & Pedestrian Counts](https://data.somervillema.gov/d/qu9x-4xq5) — `qu9x-4xq5`
- **Shape:** **tabular** · 8 columns · 2,532 rows
- **Last updated:** 2025-12-23T21:53:25
- **Why this might matter:** Bicycle & pedestrian counts. 2.5K rows. Useful for active-transport equity questions.
#### [Somerville Public School Staff MBTA Pass Pilot - Travel & Survey Data](https://data.somervillema.gov/d/qsv6-v7hu) — `qsv6-v7hu`
- **Shape:** **tabular** · 26 columns · 16 rows
- **Last updated:** 2023-10-31T15:17:30
- **Why this might matter:** School staff MBTA pass pilot. 16 rows. Narrow.
#### [test](https://data.somervillema.gov/d/7f7a-jts5) — `7f7a-jts5`
- **Shape:** *blob (filter)* · 8 columns · — rows
- **Last updated:** 2025-12-23T21:53:25
- **Why this might matter:** **Test dataset.** Noise. Skip.
### Uncategorized (1 datasets)
#### [Citizenserve Applicant Feedback 2023 Survey Results](https://data.somervillema.gov/d/scm7-xh8d) — `scm7-xh8d`
- **Shape:** **tabular** · 43 columns · 84 rows
- **Last updated:** 2024-05-31T19:28:07
- **Why this might matter:** Citizenserve applicant feedback 2023. Permit-experience feedback. Very small.
---
## Methodology
- **Source:** Socrata Discovery API at `https://api.us.socrata.com/api/catalog/v1?domains=data.somervillema.gov` (paginated; one row per dataset).
- **Row counts:** Per-dataset SODA `count(*)` for tabular datasets; skipped for blob types (map/file/filter/etc — Socrata's Non-tabular datasets do not support rows requests).
- **Persistence:** `main_admin.fct_socrata_catalog_raw`, append-only with `cataloged_at`. Re-running the build script adds a fresh snapshot without clobbering history.
- **Annotations:** Hand-written `why this might matter` line per dataset, in `scripts/generate_socrata_inventory_page.py`. Update there as understanding evolves.
