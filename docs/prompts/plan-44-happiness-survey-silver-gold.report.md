# Report — Happiness Survey silver + gold curation (MVP 3, trend-only)

**Companion to:** [`plan-44-happiness-survey-silver-gold.md`](plan-44-happiness-survey-silver-gold.md)
**Session:** [67](../sessions/session-67-2026-05-25-plan-44-happiness-survey-silver-gold.md)
**PR:** [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71)
**Date:** 2026-05-25

---

## Gate table

| Scope | Status | PR / commit |
|---|---|---|
| A1 — silver model SQL | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| A2 — silver schema.yml | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| A3 — no demographics in silver | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| B1 — `dim_survey_question` | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| B2 — `dim_survey_wave` | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| B3 — `fct_happiness_survey` | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| B4/B5 — gold schema.yml additions + relationships-test absence documented | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| C1-C3 — semantic views + perception topic + agent wiring | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| C4 — `oxy validate` (gate) | complete | 21/21 valid |
| D1 — limitations update | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| D2 — `survey-gold-unweighted.md` | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| D3 — `survey-trend-only-no-demographics.md` | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`89d6ecc`) |
| E1 — `dbt run --select silver gold` | complete | 16/16 PASS in 5.16s |
| E2 — `dbt test --select silver gold` | complete | 111/111 PASS in 3.03s |
| E3 — row-count sanity | complete | silver 12,583 = bronze; fact 57 city + 371 ward; 0 ward rows for 2011 |
| E4 — `./run.sh manual` end-to-end | complete | exit 0, 875s, run_id `01KSGZ0MJB2AGACM4N2S83RW3G`; `/erd` Silver placeholder auto-resolved |
| E5 — answer-agent smoke (2 questions) | complete | both fire trust contract correctly; all 3 limitations surfaced as expected |
| F1-F5 — LOG / TASKS / session file / prompt+report convention | complete | [#71](https://github.com/ironmonkey88/oxygen-mvp/pull/71) (`2be2db3`) |

## Shipped

**Silver — the project's first silver model:**

- [`dbt/models/silver/stg_happiness_survey.sql`](../../dbt/models/silver/stg_happiness_survey.sql) — per-respondent (id, year) grain; 12,583 rows = bronze count; 8 curated `_num` Likert columns from the Phase D matrix cast to DOUBLE via TRY_CAST; ward NULL preserved; `weight` column reserved-NULL; audit columns (`_extracted_at`, `_dlt_load_id`, `_dlt_id`) carried through.
- [`dbt/models/silver/schema.yml`](../../dbt/models/silver/schema.yml) — model + 13 column descriptions documenting curation discipline; tests on `respondent_id` (not_null, unique), `year` (not_null, accepted_values), and each `_num` column (accepted_values `[1..5]` with `is not null` predicate). `dbt_utils` not installed → inline range tests instead of `dbt_utils.unique_combination_of_columns`.

**Gold — 3 new models:**

- [`dim_survey_question.sql`](../../dbt/models/gold/dim_survey_question.sql) — 8 hand-rolled rows; topic taxonomy of 5 buckets (core_wellbeing / neighborhood / city_services / community_education / civic_information); coverage profile (`first_wave_asked` / `last_wave_asked` / `waves_asked_count`) travels from the Phase D matrix.
- [`dim_survey_wave.sql`](../../dbt/models/gold/dim_survey_wave.sql) — 8 rows data-driven from silver; `respondent_count` + `ward_coverage_pct` stay in sync on every refresh; 2011's `notes` flags the ward-coverage gap and the city-only handling in the fact.
- [`fct_happiness_survey.sql`](../../dbt/models/gold/fct_happiness_survey.sql) — trend fact at (wave × geography_level × geography_key × question) grain; UNION ALL of city + ward CTEs; ward CTE filters `year >= 2013 AND ward IS NOT NULL` to exclude 2011; Likert distribution columns enable top/bottom-two-box at semantic layer; `weight_strategy` reserved-NULL.
- [`gold/schema.yml`](../../dbt/models/gold/schema.yml) — three new model entries with descriptions + tests; deliberate absence of `relationships` test on `geography_key → dim_ward.ward` documented (grain mixes city + ward; a relationships test would fail on city rows).

**Semantic + agent wiring:**

- [`semantics/views/happiness_survey.view.yml`](../../semantics/views/happiness_survey.view.yml) — primary entity `survey_observation` + FK entities for `survey_wave` and `survey_question`; measures `total_respondents`, `mean_score_overall` (with mean-of-means caveat in description), `pct_top_two_box`, `pct_bottom_two_box` (the last two as `custom` SQL).
- [`survey_questions.view.yml`](../../semantics/views/survey_questions.view.yml) and [`survey_waves.view.yml`](../../semantics/views/survey_waves.view.yml) — lookup views.
- [`perception.topic.yml`](../../semantics/topics/perception.topic.yml) — new topic naming the three views; description carries explicit caveats (self-selection, 2011 ward gap, unweighted, respondents-not-residents).
- [`answer_agent.agent.yml`](../../agents/answer_agent.agent.yml) — `context.topic.src` glob expanded from `service_requests.topic.yml` only to all 5 topics (previous wildcard on views was already picking up new views; the topic list was the wiring gap).

**Limitations registry (1 updated + 2 new):**

- [`happiness-survey-self-selection-and-coverage.md`](../limitations/happiness-survey-self-selection-and-coverage.md) — Status section flipped to "Silver / Gold both shipped"; new "What MVP 3 silver/gold did and did not do" section names the three locked decisions and rationale.
- [`survey-gold-unweighted.md`](../limitations/survey-gold-unweighted.md) — new, medium severity; respondents-vs-residents framing + reserved `weight` / `weight_strategy` slots + trust-contract framing rule ("respondents who answered", not "Somerville residents").
- [`survey-trend-only-no-demographics.md`](../limitations/survey-trend-only-no-demographics.md) — new, low severity; k-anonymity-by-absence rationale + what a future demographics plan would need (k-floor, cell-collapse rule, silver vs gold pivot).

**Housekeeping (Phase F):**

- LOG.md: Plan 44 row at top of recent reverse-chronological cluster; original "Plan 24" reservation flipped to "done (under Plan 44)"; Last Updated bumped to 2026-05-25 21:29 ET; Session 67 entry added at top of Recent Sessions; Session 62 rotated to Earlier per 5-entry cap.
- TASKS.md: Plan 44 row flipped `[~]` → `[x]`; Next Focus header rewritten to surface the new follow-ups (weighting computation + perception-trend dashboard + operational-pairing analysis).
- Session file at [`session-67-2026-05-25-plan-44-happiness-survey-silver-gold.md`](../sessions/session-67-2026-05-25-plan-44-happiness-survey-silver-gold.md).
- Plan 43 prompt+report convention: prompt file landed at session start; this report file is the smoke-test output landed as last commit before merge.

**Verification evidence:**

- E1 / E2 / E3: ran on EC2 over Tailscale via the venv `dbt` and a Python duckdb script in `/tmp/`. Pre-flight matrix matched the limitation entry exactly (8 columns surviving the Phase D filter; 12,583 rows; ward 0%/2011 → 96-99.5%/2013+).
- E4: `./run.sh manual` ran 875s end-to-end on EC2; final exit code 0; profile staleness detected (+28 new columns from the 4 Plan 44 models) and re-profiled (422 columns total). `/erd` Silver tier auto-resolved to `portal/erd-tier-silver.mmd (1 models, 0 within-tier rels)` — Plan 25's load-bearing claim confirmed. `/metrics` regen: 29 measures × 14 views (+7 from perception).
- E5: `oxy run agents/answer_agent.agent.yml "<question>"` for both smoke-test questions. Q1 returned 7 rows (life satisfaction city 2013→2025; mean 4.12→3.95; top-two-box 89.1%→78.0%), trust contract surfaced `survey-gold-unweighted` + `happiness-survey-self-selection-and-coverage`. Q2 returned 2 rows (happiness Ward 3 vs Ward 5 2023; both ~3.83 mean / ~74% top-two-box), trust contract surfaced all 3 new limitations including `survey-trend-only-no-demographics` (which fired because the question naturally invites demographic slicing — exactly the case the limitation was written for).

## Worth flagging

- **Permissive fact-row filter (design call).** Any (wave, question) combination with ≥1 non-NULL respondent score gets a row in the fact. The strict alternative would have filtered to combinations clearing the Phase D >50%-non-NULL threshold; that would silently drop real responses (e.g. 2025 education_quality had ~612 responses, ~44% non-NULL, below threshold; permissive keeps them). The matrix threshold travels in `dim_survey_question` (`first_wave_asked` / `last_wave_asked`) so analysts who want strict can join + filter explicitly. Documented in the fact-model SQL header.
- **Question text is paraphrased, not verbatim.** Bronze documents column names mechanically without per-question survey wording. `dim_survey_question.question_label` carries short paraphrases prefixed `[paraphrase]` (option (b) from the prompt's Notes-for-Code) rather than NULL or invented confident text. A future plan with access to the survey instrument can replace them with verbatim wording.
- **Topic taxonomy is Code's call.** The 5-bucket grouping (core_wellbeing / neighborhood / city_services / community_education / civic_information) was assigned by Code with rationale in the commit + the dim_survey_question SQL header. The 8 questions split naturally across these; if Gordon prefers a different grouping (e.g. merging neighborhood + city_services into "physical_environment"), it's a one-line edit in the VALUES table.
- **The `mean_score_overall` measure is mean-of-means at the grain.** Mathematically correct for trend-tracking when grouped by wave / geography / question, but NOT equivalent to a respondent-level grand mean (which would require querying silver). The measure description documents this so the trust-contract receipt surfaces the distinction to analysts who ask for "a true average."
- **EC2 had pre-existing regen drift** at session start (`docs/limitations/_index.yaml` + `portal/index.html`) — discarded via `git checkout --` before branch switch; `./run.sh manual` at end regenerated them against the new Plan 44 limitations + warehouse state, so the drift is now correct and tracked.
- **`/erd` Silver placeholder auto-resolved** (Plan 25's load-bearing claim). `portal/erd-tier-silver.mmd` now lists 1 model; the placeholder pattern in `scripts/generate_per_tier_erd.py` worked end-to-end on its first real exercise of the silver path.

## Ready for more work — natural next moves

1. **Survey weighting computation plan** — populates the reserved `weight` (silver) + `weight_strategy` (gold) slots with a defensible strategy (e.g. raking to ACS age × ward 2020). The schema slots and the trust-contract framing rule are in place; the missing piece is the methodology decision.
2. **Perception-trend dashboard** — first dashboard built on the new `fct_happiness_survey`. Likely a Verdict-First Trend family member per [`docs/dashboard-family-design-2026-05-22.md`](../dashboard-family-design-2026-05-22.md). The shape (wave × question line chart with optional ward filter) maps cleanly onto the family's standard template.
3. **Operational-pairing analysis** — "did satisfaction track outcomes?" joining `fct_happiness_survey` × `fct_311_requests` / `fct_crime_incidents` / `fct_permits` by ward × year. Per the prompt's Out-of-Scope, this is deferred and most likely belongs as a dashboard or analyst notebook rather than a new fact. A scoping conversation when ready.
4. **Question-text enrichment** — small follow-up to replace the `[paraphrase]`-prefixed `question_label` values with verbatim survey-instrument wording if accessible.
5. **Plan 41** (DBA v1.2 calibration) — best after a few weeks of v1.1 data accumulates.
6. **Plan 42** (memory-to-file migrations) — needs the deliberate placement conversation. Can now target placement adjacent to PROMPTS.md §5.5 (added in Plan 43).
