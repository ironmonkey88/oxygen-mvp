# Prompt — Happiness Survey silver + gold curation (MVP 3, trend-only)

**Kind:** coding
**Date:** 2026-05-24
**Plan:** 44 (per LOG.md Plans Registry: Plan 41 reserved for DBA v1.2 calibration, Plan 42 reserved for memory-to-file migrations, Plan 43 done, Plan 44 is the next contiguous slot — the original "Plan 24" reservation in LOG.md refers to this same work and should be marked done by this plan)
**Scope:** new `dbt/models/silver/` content (first silver model in the project), new `dbt/models/gold/` fact + dims for the survey, semantic-layer additions under `semantics/`, limitations registry updates, LOG/TASKS/session-file housekeeping
**Effort:** one session, ~2-4 hours (real pre-flight risk on column-drift harmonization)
**Depends on:** Nothing currently in-flight. Plan 41 (DBA v1.2 calibration) and Plan 42 (memory-to-file migrations) remain reserved and don't touch the warehouse layers this plan does.

---

## Outcome

Somerville residents and analysts get the first genuine perception signal in the warehouse: a city-wide and ward-level view of how Somerville residents have felt about their city across eight survey waves from 2011 to 2025. They can ask "has happiness in Ward 3 trended up or down since 2013?" and get an honest, reproducible answer — not a misleading one. The gold fact is the first row in the Silver tier of the warehouse (a tier that has been structurally present but empty since the medallion architecture was set up), and the first analyst-facing surface that pairs a perception metric with the existing operational data by ward and year.

Honest is doing real work in that paragraph. The Happiness Survey has three structural problems documented in `docs/limitations/happiness-survey-self-selection-and-coverage.md`: respondents are self-selected (not a representative sample of residents), about half the rows have no ward (all of 2011 + a residual), and the question set drifted across waves (only 8 of 50 `_num` columns hit the ≥5-wave / <50%-NULL bar that Plan 23 Phase D set). This plan does not solve those problems — they are properties of the data, not the warehouse. What it does is curate the survey into silver + gold such that an analyst querying it cannot accidentally produce a misleading number. The 2011 wave is excluded from ward analysis; questions are filtered to their actual coverage years; the gold layer is aggregates-only (no per-respondent demographic dims). Every limitation surfaces in the trust contract.

## Context

Plan 23 Phase D halted on 2026-05-15 with a documented finding: 8 of 50 `_num` satisfaction columns survived the cross-wave-presence filter (Plan 23 prompt-set threshold was ≥12). The halt was correct — thin gold jammed into MVP 2 would have shipped a misleading surface where analysts treated columns as fully covered when only the core happiness trio was. This plan picks up the work as a dedicated MVP 3 effort with curation scaffolding the Plan 23 prompt deliberately left out.

A few things to know that shaped this prompt:

- **Three business-analyst-step decisions are locked.** Chat asked Gordon the questions DASHBOARDS.md §2.1 (and the analogous discipline for warehouse models) demands. Answers: (1) gold scope is **trend over time** — city and ward across waves — *not* the operational-pairing fact table; (2) gold carries **no demographic dimensions** — aggregate measures only, k-anonymity enforced by absence rather than by suppression logic; (3) the silver/gold schema **designs for weighting** (reserves a `weight` column on the per-respondent silver row and a `weight_strategy` column on the aggregated gold fact) but ships unweighted in this plan — the weighting computation is a follow-up plan when a defensible strategy is named.
- **Silver tier is empty today.** The dbt project has a configured `silver` schema (`dbt/dbt_project.yml`: `silver: +schema: silver, +materialized: table`) and the `/erd` page renders a Silver placeholder waiting for the first model (`scripts/generate_erd_page.py` reads `dbt/models/silver/schema.yml`). Plan 24/25 explicitly named Plan 24 as the landing point for the first silver model and a self-resolving placeholder. This plan exercises the silver path end-to-end for the first time.
- **The 8 surviving `_num` columns are the gold measure set.** Plan 23 Phase D's halt matrix in `docs/limitations/happiness-survey-self-selection-and-coverage.md` named them: `happiness_num`, `life_satisfaction_num`, `somerville_satisfaction_num`, `beauty_neighborhood_satisfaction_num`, `streets_maintenance_satisfaction_num`, `education_quality_satisfaction_num`, `social_community_events_satisfaction_num`, `city_services_information_availability_satisfaction_num`. Each has a coverage profile (8/8 waves for the top three, down to 6/8 for the bottom three). The coverage profile travels with the data into gold as a per-question coverage table — analysts who pull a question see which waves it was actually asked in.
- **No new bronze ingestion.** The survey bronze (`main_bronze.raw_somerville_happiness_survey_raw`, 12,583 rows, 150 cols) landed in Plan 21 and is unchanged. This plan only adds silver + gold + semantic.
- **PHILOSOPHY.md §5 names this work explicitly.** The k-anonymity floor on survey data is one of the four boundary constraints PHILOSOPHY.md §5 calls out as not-in-the-trade-off-space. "No demographic dims in gold" satisfies that constraint structurally — there are no thin demographic slices to suppress because the dims aren't there.

## Work

**Phase A — Silver: per-respondent clean view.**

A1. Create `dbt/models/silver/stg_happiness_survey.sql`. Materialization: `table` (per dbt_project.yml's silver default). Source: `{{ ref('raw_somerville_happiness_survey') }}` (bronze view). One row per (respondent_id, year). Columns:

- `respondent_id` (TEXT, source `id` cast)
- `year` (INTEGER, source `year` cast)
- `ward` (TEXT, source `ward` cast; NULL preserved — handled at gold)
- The 8 surviving `_num` columns from the Phase D matrix, cast to DOUBLE: `happiness_num`, `life_satisfaction_num`, `somerville_satisfaction_num`, `beauty_neighborhood_satisfaction_num`, `streets_maintenance_satisfaction_num`, `education_quality_satisfaction_num`, `social_community_events_satisfaction_num`, `city_services_information_availability_satisfaction_num`
- `weight` (DOUBLE, NULL — reserved for future weighting; documented in schema.yml as the slot for a defensible weighting strategy when one is computed)
- Standard audit columns: `_extracted_at`, `_dlt_load_id`, `_dlt_id` carried through

A2. Create `dbt/models/silver/schema.yml` with:

- Model description (3-4 sentences naming: per-respondent grain, 8-column curated `_num` set per Plan 23 Phase D matrix, ward NULL preserved, weight column reserved-but-NULL)
- Column descriptions for all 13 columns (per-column for the curated set, with each `_num` column noting its waves-of-coverage from the Phase D matrix)
- Tests:
  - `unique` + `not_null` on a synthetic PK `(respondent_id, year)` — use a `dbt_utils.unique_combination_of_columns` test if `dbt_utils` is available; otherwise an inline SQL test asserting `count(*) = count(distinct concat(respondent_id, '|', year))`
  - `not_null` on `year`
  - `accepted_values` on `year` ∈ {2011, 2013, 2015, 2017, 2019, 2021, 2023, 2025}
  - For each `_num` column: a range test asserting values ∈ {1, 2, 3, 4, 5} OR NULL (Likert 1-5)

A3. **No demographic columns surface in silver.** Demographics (age, gender, race, identity flags, household composition) stay in bronze. The silver row is what the gold layer aggregates; with no demo dims in gold, demos don't need to be in silver. If a future plan wants to add a demographic surface, it adds them to silver then; doing so now would invite premature reach.

**Phase B — Gold: trend fact + supporting dims.**

B1. Create `dbt/models/gold/dim_survey_question.sql`. Materialization: `table`. Hand-rolled dimension with 8 rows, one per surviving `_num` column. Columns:

- `survey_question_id` (TEXT, surrogate — slug form of the column name, e.g. `happiness`, `life_satisfaction`, `somerville_satisfaction`, etc.)
- `column_name` (TEXT, the source `_num` column name)
- `question_label` (TEXT, human-readable — e.g., "How happy are you right now?", "Life satisfaction overall", drawn from the survey instrument; if exact text isn't recoverable from the source, use a short paraphrase and note in schema.yml)
- `topic` (TEXT, one of: `core_wellbeing`, `neighborhood`, `city_services`, `community_education`, `civic_information` — assigned by Code with a rationale in commit; the 8 questions split naturally across these)
- `scale_min` (INTEGER, 1), `scale_max` (INTEGER, 5)
- `first_wave_asked` (INTEGER), `last_wave_asked` (INTEGER), `waves_asked_count` (INTEGER) — from the Phase D matrix

B2. Create `dbt/models/gold/dim_survey_wave.sql`. Materialization: `table`. Hand-rolled dimension with 8 rows, one per wave year. Columns:

- `survey_wave_id` (TEXT, the year as string — e.g., `'2011'`)
- `wave_year` (INTEGER)
- `respondent_count` (INTEGER, from silver `count(*) where year = N`)
- `ward_coverage_pct` (DOUBLE, from silver — share of rows in wave with non-NULL ward; ~0% for 2011, ~99%+ for 2013 onward)
- `notes` (TEXT — e.g., "Distributed differently from later waves; ward not collected" for 2011)

B3. Create `dbt/models/gold/fct_happiness_survey.sql`. Materialization: `table`. **Grain: one row per (survey_wave_id, geography_level, geography_key, survey_question_id)** — pre-aggregated, no per-respondent rows. Columns:

- Surrogate key `survey_observation_id` (TEXT, md5 of `survey_wave_id + geography_level + coalesce(geography_key, 'NULL') + survey_question_id`)
- FK columns: `survey_wave_id`, `survey_question_id`
- `geography_level` (TEXT, one of `'city'` or `'ward'`)
- `geography_key` (TEXT, the ward number `'1'..'7'` when `geography_level = 'ward'`; NULL when `geography_level = 'city'`)
- `respondent_count` (INTEGER, count of non-NULL responses to this question at this geography in this wave)
- `mean_score` (DOUBLE, average of the `_num` value at the grain)
- `median_score` (DOUBLE)
- `score_1_count`, `score_2_count`, `score_3_count`, `score_4_count`, `score_5_count` (INTEGER each — the Likert distribution; lets analysts compute "% who rated 4 or 5" without re-querying silver)
- `weight_strategy` (TEXT, NULL today — reserved for naming the weighting strategy when one is applied; e.g., `'raked_age_ward_2020_acs'`; documented in schema.yml as the companion to the silver `weight` reservation)

The 2011 wave should appear at `geography_level = 'city'` only — never at `'ward'` (the ward column is NULL for all 2011 rows; ward-level aggregation produces a single misleading "NULL-ward" row that the model should not emit). Filter logic in the SQL: ward aggregation joins silver on `year >= 2013` and `ward IS NOT NULL`.

B4. Create `dbt/models/gold/schema.yml` additions for the three new models. For each, model description + column descriptions + tests:

- `dim_survey_question`: `unique` + `not_null` on `survey_question_id`; `accepted_values` on `topic` ∈ {`core_wellbeing`, `neighborhood`, `city_services`, `community_education`, `civic_information`}
- `dim_survey_wave`: `unique` + `not_null` on `survey_wave_id`; `accepted_values` on `wave_year`
- `fct_happiness_survey`: `unique` + `not_null` on `survey_observation_id`; `relationships` to `dim_survey_wave.survey_wave_id` and `dim_survey_question.survey_question_id`; `accepted_values` on `geography_level` ∈ {`'city'`, `'ward'`}; `not_null` on `respondent_count` and `mean_score`

B5. **Do not add a `relationships` test from `fct_happiness_survey.geography_key` to `dim_ward.ward`.** The grain mixes `city` (NULL geography_key) and `ward` (numeric geography_key); a relationships test against `dim_ward` would fail on the city rows. Document this in schema.yml as a deliberate choice with a note that a future plan might split the fact into per-geography views if joining to `dim_ward` becomes important.

**Phase C — Semantic layer.**

C1. Create `semantics/views/happiness_survey.view.yml`. Single primary entity `survey_observation` with key `survey_observation_id`. Foreign entities for `survey_wave` (key `survey_wave_id`) and `survey_question` (key `survey_question_id`). Dimensions: `geography_level`, `geography_key`, `wave_year` (via the wave foreign entity — `{{survey_wave.wave_year}}`), `survey_question_id`, `question_topic` (via the question entity — `{{survey_question.topic}}`). Measures:

- `total_respondents` — `sum` of `respondent_count`
- `mean_score_overall` — `average` of `mean_score` (note: this is mean-of-means at the grain, which is correct for trend-tracking but not equivalent to a respondent-level grand mean; document this distinction in the measure description)
- `pct_top_two_box` — `custom`, SQL: `SUM(score_4_count + score_5_count) * 1.0 / NULLIF(SUM(respondent_count), 0)` — the standard "% who rated 4 or 5"
- `pct_bottom_two_box` — `custom`, SQL: `SUM(score_1_count + score_2_count) * 1.0 / NULLIF(SUM(respondent_count), 0)`

C2. Create `semantics/views/survey_questions.view.yml` and `semantics/views/survey_waves.view.yml` — minimal lookup views over the two dimensions, so the semantic layer can answer "what questions are in the survey?" and "what waves are in the survey?" without joining through the fact.

C3. Create a new topic `semantics/topics/perception.topic.yml` that names the three views. The topic description states explicitly that this is the perception signal — opinion data from a self-selected sample, not population statistics. Wire the topic into the answer agent in `agents/answer_agent.agent.yml` alongside the existing topics (`service_requests`, `public_safety`, `built_environment`, `city_context`).

C4. Run `oxy validate` on the new YAML. Halt-and-surface if validation fails — vocabulary locks from prior plans apply (measure types `{count, sum, average, min, max, count_distinct, median, custom}`; dimension types `{string, number, date, datetime, boolean}` — no `avg`, no `timestamp`).

**Phase D — Limitations registry update.**

D1. Update `docs/limitations/happiness-survey-self-selection-and-coverage.md`:

- Status section: flip "Gold: deferred (Plan 23 Phase D halted)" → "Gold: shipped (Plan 44) — aggregate-only, no demographic dims, unweighted with weight column reserved for future plan."
- Add a new section "What MVP 3 silver/gold did and did not do" naming the three decisions (trend-only scope, no demographic dims, weight-reserved-unweighted) and the rationale for each.
- Keep the Phase D matrix; it's the column-coverage truth that travels with the data into `dim_survey_question`.

D2. Create `docs/limitations/survey-gold-unweighted.md` (new limitation entry). Severity: medium. Affects: `fct_happiness_survey`, `happiness_survey`, `perception`. Body covers: (1) gold ships unweighted; aggregates describe respondents, not residents; (2) the `weight` column on silver and `weight_strategy` column on gold are reserved for a future plan that names a defensible weighting strategy (e.g., raking to ACS age × ward); (3) trust-contract framing for any analyst surface that uses these measures: every headline must say "respondents who answered" rather than "Somerville residents."

D3. Create `docs/limitations/survey-trend-only-no-demographics.md` (new limitation entry). Severity: low (this is a deliberate scope choice, not a data problem). Affects: `fct_happiness_survey`. Body: gold MVP 3 surfaces trend over time at city + ward grain. Demographic dimensions (age, race, gender, identity flags) are present in bronze but deliberately not surfaced in silver or gold per the k-anonymity floor in PHILOSOPHY.md §5. A future plan with a defensible suppression strategy (e.g., k=5 floor on joined demographic slices) could expand the surface; until then, the absence is the protection.

**Phase E — Run and verify.**

E1. Local `dbt run` (or remote on EC2 — Code's call). Confirm all three gold models + the silver model build clean.

E2. Local `dbt test`. All new tests pass.

E3. Row-count sanity checks (manual queries Code documents in the report-back):

- `select count(*) from main_silver.stg_happiness_survey` — should equal 12,583 (bronze row count)
- `select count(*) from main_gold.fct_happiness_survey where geography_level = 'city'` — should equal 8 waves × 8 questions = 64 (if every question is asked in every wave; the actual count will be lower per the Phase D matrix — document the actual number)
- `select count(*) from main_gold.fct_happiness_survey where geography_level = 'ward'` — should equal 7 waves (2013-2025) × 7 wards × 8 questions = 392 at most (again, lower per actual coverage)
- `select wave_year, ward_coverage_pct from main_gold.dim_survey_wave order by wave_year` — should show ~0% for 2011, near-100% for later waves

E4. `./run.sh manual` end-to-end on EC2. Confirms the run.sh pipeline picks up the new models, regenerates `/metrics` (the page should now include perception measures), regenerates `/erd` (the Silver tier placeholder should auto-resolve into a real diagram with the one silver model + 13 columns), and confirms admin tests still pass.

E5. Answer-agent smoke test. Two questions, run via the chat agent, document the responses in the report-back:

- "What is the trend in life satisfaction in Somerville from 2013 to 2025?" — should return a city-level mean over the relevant waves with trust-contract receipts.
- "How does happiness in Ward 3 compare to Ward 5 in 2023?" — should return ward-level means with the appropriate caveat (respondents, not residents).

**Phase F — Housekeeping.**

F1. `LOG.md` Plans Registry: flip the existing "Plan 24" row from `reserved` to `done` with a brief summary (and rename it `Plan 24` → `Plan 44`? — see Halt condition below; if the old slot was renumbered by Plan 43 cleanup, work against the actual current registry). Add an Active Decisions row for the three locked decisions.

F2. `TASKS.md`: Plan 44 row `[~]` → `[x]` at session end; update "Next Focus" to remove Plan 24 from the queued list (it's been done) and surface the natural follow-ups: weighting computation plan, dashboard built on the new fact, operational-pairing fact (the "did satisfaction track outcomes?" question).

F3. Session file at `docs/sessions/session-NN-2026-05-24-plan-44-happiness-survey-silver-gold.md` (Code resolves NN; Session 65 was the last logged).

F4. **Prompt + report files per Plan 43 convention.** This prompt arrives via the `commit this prompt` flow (Chat commits to `docs/prompts/plan-44-happiness-survey-silver-gold.md` on branch `claude/plan-44-happiness-survey-silver-gold`). At session end, Code writes the report to `docs/prompts/plan-44-happiness-survey-silver-gold.report.md` alongside the prompt.

F5. `LOG.md` "Last Updated" bumped.

## Verification

**Static-artifact gates:**

- `dbt/models/silver/stg_happiness_survey.sql` exists with the 13-column shape named in A1.
- `dbt/models/silver/schema.yml` exists with model + 13 column descriptions + the named tests.
- `dbt/models/gold/dim_survey_question.sql`, `dim_survey_wave.sql`, `fct_happiness_survey.sql` exist with the shapes named in B1/B2/B3.
- `dbt/models/gold/schema.yml` additions present with descriptions + tests + the deliberately-absent `relationships` test on `geography_key` documented per B5.
- `semantics/views/happiness_survey.view.yml`, `survey_questions.view.yml`, `survey_waves.view.yml` exist with the entities/dims/measures named in C1/C2.
- `semantics/topics/perception.topic.yml` exists and names the three views.
- `agents/answer_agent.agent.yml` includes the `perception` topic.
- `docs/limitations/happiness-survey-self-selection-and-coverage.md` updated per D1.
- `docs/limitations/survey-gold-unweighted.md` and `docs/limitations/survey-trend-only-no-demographics.md` created per D2/D3.
- `docs/limitations/_index.yaml` regenerated by `run.sh` step 9/9 (automatic).
- LOG.md Plans Registry shows Plan 44 done; TASKS.md Plan 44 row `[x]`; session file present; prompt+report sibling files present.

**Live-functional gates:**

- `dbt run` clean (all new models build).
- `dbt test` clean (all new tests pass).
- `oxy validate` clean (semantic layer additions parse).
- `./run.sh manual` exits 0 end-to-end; the new gold + dim rows are queryable from `main_gold.*`; `/metrics` regenerated with perception measures visible; `/erd` Silver tier placeholder replaced with a real one-model diagram; admin tests still green.
- Answer-agent smoke-test questions return sensible answers with trust contract firing (SQL + row count + citations + relevant limitations entry surfaced).

## Halt conditions

- **Pre-flight finds the 8 surviving `_num` columns don't match the Phase D matrix.** Re-query bronze to confirm cross-wave presence. If the surviving set is different from what the limitation entry names, halt and surface the new matrix — the prompt's gold dim shape changes (different rows in `dim_survey_question`).
- **dbt_utils not available** for the `(respondent_id, year)` uniqueness test. Substitute an inline SQL test (named in A2) and proceed; this is a Code's-call gotcha, not a halt.
- **`oxy validate` flags a semantic-layer issue.** Halt at Phase C4 and surface — vocabulary lock violations (measure type, dimension type) have bitten prior plans and the fixup is mechanical, but the halt is honest reporting.
- **The plan-number slot is wrong.** If LOG.md's Plans Registry has shifted between this prompt being drafted and Code starting, work against the actual current slot. The original "Plan 24 reserved" row in the registry should be marked done by this work regardless of what number this plan ships as — the reservation is the same work.
- **Answer-agent smoke test fails.** Two failure shapes: (a) the agent can't reach the new topic — surface as a wiring issue with the answer_agent.agent.yml edit; (b) the agent returns a number that's wrong relative to a bronze sanity check — halt and surface, this is what the smoke test is for.
- **The Silver `/erd` placeholder doesn't auto-resolve.** Plan 25 explicitly designed for this: the generator reads `dbt/models/silver/schema.yml` and emits a real diagram on next `./run.sh`. If it doesn't happen, the bug is in `scripts/generate_per_tier_erd.py`, not in this plan's models. Surface as a Plan 25 carry-over bug, don't fix it inline unless it's a one-line obvious fix.

## Out of scope

- **Demographic dimensions in silver or gold.** Decision locked: aggregates only. A future plan with a defensible suppression strategy can add them.
- **Weighting computation.** The schema reserves the column slots (`weight` on silver, `weight_strategy` on gold) but ships unweighted. Computing weights — raking to ACS, propensity adjustment, anything else — is a follow-up plan when a defensible strategy is named.
- **The operational-pairing fact.** "Did satisfaction track outcomes?" (ward × year × survey question × operational outcome) is a separate analytical surface. It would be built as a new gold model joining `fct_happiness_survey` with `fct_311_requests`, `fct_crime_incidents`, etc. — or, more honestly, as a dashboard or analyst notebook rather than a fact. Deliberately deferred.
- **A dashboard.** Plan 24 lands the data, not the dashboard. Once gold is live, a perception-trend dashboard (likely a Verdict-First Trend family member per `docs/dashboard-family-design-2026-05-22.md`) is the natural next plan.
- **Silver layer standards in STANDARDS.md §5.3.** STANDARDS.md §5.3 names silver standards as placeholder — "full standards land in MVP 3." This plan lands the first silver model, but writing the full silver-tier standards section is a separate doc plan after the first model is in production. The current model should be built to follow the existing silver checklist items (PII redaction (n/a — no PII here), dedup, type casting, unique key tests, not_null tests) as a working reference for the standards plan.
- **Builder-CLI dashboard work.** Plans 18 + 19 remain queued separately.

## Commit shape

Single PR holding Phases A–F. The phases are jointly valuable — silver without gold isn't queryable; gold without semantic isn't agent-reachable; agent without limitations entries breaks the trust contract. Commit message names Plan 44.

Per CLAUDE.md autonomous PR-merge policy: push → `gh pr create` → `gh pr merge --merge --delete-branch` autonomously once verification gates pass. The five live-functional gates (`dbt run`, `dbt test`, `oxy validate`, `./run.sh manual`, answer-agent smoke test) all need to pass; partial completion on any of them flips the status to `partial` and pauses the merge per CLAUDE.md autonomous-merge rules.

---

## Notes for Code

- **This is the first silver model in the project.** The dbt configuration has supported the tier since the warehouse was set up; this plan exercises it for the first time. If anything in `dbt_project.yml`'s `silver:` configuration turns out not to work cleanly (schema creation, materialization), that's a real finding — surface it rather than working around it.
- **`/erd` auto-resolution is load-bearing for Plan 25's claim.** Plan 25's session note ended with "the Silver placeholder will auto-populate when Plan 24's first silver model lands — no further ERD work needed." This plan's `./run.sh manual` step is the test of that claim. If the placeholder doesn't resolve cleanly, that's worth knowing.
- **k-anonymity by absence vs. by suppression.** The reason the gold layer has no demographic dimensions is that thin-cell suppression logic in views is harder to reason about and easier to defeat (a sophisticated user can re-construct suppressed cells from adjacent ones). Removing the dimensions entirely makes the protection structural rather than computational. This is the right design but it does mean an analyst who wants demographic-cut analysis is gated until a future plan with explicit suppression machinery — which is the right gate.
- **Question-text recovery.** The 8 surviving `_num` columns' exact survey wording isn't in the bronze schema (it documents column names mechanically). Code can either (a) use the Socrata metadata API to fetch question text if available, (b) paraphrase short labels from the column names with a `[paraphrase]` marker in `dim_survey_question.question_label`, or (c) leave `question_label` NULL with the column_name as the only identifier and surface a follow-up plan to enrich it. Pick honestly; don't invent confident question text.
- **The `mean of means` measure** in C1 is technically correct for the grain (one row per geography × wave × question), but it's not the same number as a respondent-level grand mean would produce. Document this clearly in the measure description — the trust-contract receipt should make the distinction visible to the analyst.
- **2011 wave handling.** The model excludes 2011 from ward aggregation entirely (no NULL-ward rows). 2011 still appears at `geography_level = 'city'` for the questions it asked. This makes the 2011 wave usable for city-wide trend baselines while preventing accidental misuse at the ward level. Document the choice in `dim_survey_wave` notes.
