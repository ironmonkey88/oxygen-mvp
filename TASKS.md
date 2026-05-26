# TASKS.md — Oxygen MVP Task Tracker

> Status markers: `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked
> Claude Code updates this file as work progresses.

---

## Next Focus — Survey weighting + perception-trend dashboard + operational-pairing analysis + Plans 18/19 Builder-CLI dashboards

Plan 44 closed the original Plan 24 reservation (Happiness Survey silver + gold). Natural follow-ups surfaced by that work:

- **Survey weighting computation plan** — populates the reserved `weight` (silver) + `weight_strategy` (gold) slots with a defensible strategy (e.g. raking to ACS age × ward 2020).
- **Perception-trend dashboard** — first dashboard built on the new `fct_happiness_survey`; likely a Verdict-First Trend family member per `docs/dashboard-family-design-2026-05-22.md`.
- **Operational-pairing analysis** — "did satisfaction track outcomes?" joining `fct_happiness_survey` × `fct_311_requests` / `fct_crime_incidents` / `fct_permits` by ward × year. Likely a dashboard or analyst notebook rather than a fact table per Plan 44 Out-of-Scope.
- **Plan 41** (DBA v1.2 calibration) — best after a few weeks of v1.1 data.
- **Plan 42** (memory-to-file migrations) — needs the placement conversation.
- **Plans 18/19** (Builder-CLI dashboards) — still queued.

**Plan 36 done 2026-05-23** — [x] Allowlist audit (information request, PROMPTS.md §2). Report at [`docs/audits/allowlist-audit-2026-05-22.md`](docs/audits/allowlist-audit-2026-05-22.md). Bottom line: 3-tier user-configurable allowlist (Tier 1 `settings.json` / Tier 2 `settings.local.json` / Tier 3 worktree `settings.local.json`) exists exactly as CLAUDE.md "Allowlist policy" documents; two additional surfaces (bash safety hook + Claude Code built-in auto-allow) flagged as not-tiers-but-affect-what-reaches-matcher. Scanned 15 transcripts / 2,514 Bash calls / 200 errored results / **55 denial events**: 52 are hook denials catching Code's own forbidden shell shapes (31 `;`, 21 `&&`/`||`, 2 `$()`), only 3 are real allowlist permission denials and all 3 are `git branch -d` destructive ops correctly caught by the existing deny list. Recommendations: 2 Tier-1 additions (`Bash(gh pr create *)` + `Bash(gh pr merge *)` — every PR cycle prompts despite autonomous-execution policy endorsing them); 5 memory-to-file migrations per Plan 29 durability lesson (boot-audit checklist → CLAUDE.md, git+SSH gotchas → CLAUDE.md "Known gotchas", no-SSH-heredocs → CLAUDE.md "Bash Safety", chat-code handoff format → PROMPTS.md, settings.json editing freedom → CLAUDE.md "Allowlist policy" sub-bullet). Code's read on Plan 37 timing: the 2 `gh` additions are obvious one-line edits; the memory-to-file migrations need a real conversation about placement and wording. Split suggested: Plan 37 = gh additions (small, immediate); Plan 38 = memory-to-file migrations (deliberate). Halt conditions did not fire.

**Plan 37 done 2026-05-23** — [x] gh Tier-1 additions + redundancy cleanup + hook precedence note. Track A: `Bash(gh pr create *)` + `Bash(gh pr merge *)` added to `.claude/settings.json` after the existing `gh pr view/list/diff/checks/status` cluster. Track B: 7 redundant entries removed (`Bash(ls *)`, `Bash(grep *)`, `Bash(cat *)`, `Bash(git -C * log)`, `Bash(git -C * log *)`, `Bash(git log)`, `Bash(git log *)`) — all 4 smoke-test commands (ls / grep / cat / git -C log) auto-allowed silently post-removal via Claude Code built-in. Track C: hook-precedence note added to CLAUDE.md "Known gotchas" subsection capturing that the bash safety hook fires BEFORE built-in auto-allow (verified in pre-flight: `ls /tmp 2>/dev/null || echo nofile` hook-denied for `||` even though `ls` would auto-allow standalone). Halt-condition #3 reproduction confirmed Plan 36's inference. Live test of Track A: this PR's own `gh pr create` + `gh pr merge` calls — first session post-edit.

**Plan 38 done 2026-05-23** — [x] DBA Dashboard Phase A + Phase B (Track C deferred to Plan 39). **Phase A** halt-and-surfaced at A1 per prompt's §A2 condition #3 — `messages` table has `input_tokens`/`output_tokens` populated (Anthropic-spend tracking the design doc cut as "Admin API blocked"). Gordon expanded v1 to include a C2 token-spend panel. Schema inspection doc at `docs/design-reviews/chat-state-schema-inspection-2026-05-22.md`; loader `dlt/oxy_chat_activity_pipeline.py` (dlt + psycopg2, merge-on-message_id, 102 messages × 14 threads in 0.42s); `main_admin.fct_chat_activity_raw` populated; limitations entry `docs/limitations/chat-activity-local-state-only.md`. **Phase B**: `scripts/generate_admin_dashboard.py` (10-panel HTML generator, strict-yellow rule, "what's currently yellow" advisory panel); `systemd/dashboard-refresh.{service,timer}` (15-min cadence, installed + enabled); `nginx/somerville.conf` `/admin` Tailnet-only (`allow 100.64.0.0/10; allow 127.0.0.1; deny all`); DASHBOARDS.md §9 operator-dashboard carve-out; design review at `docs/design-reviews/admin-dashboard-v1-2026-05-22/`. **Live**: headline YELLOW with 2 interpretable items (A2 streak 11/12 days, B2 117/118 + 1 warn); C2 reports $20.00 (7d) Opus 4.7 spend — real cost-proxy. Track C (4 tidy-day items: stale branches, session-starter refresh, schema.yml data_type, TASKS item 13) deferred to Plan 39 — single PR already substantial. **Worth flagging:** Plan 33 helper's annotation selector hardcoded to back-link elements — per-panel callouts didn't draw on dashboard; full-page screenshot still useful evidence. v1.1 enhancement candidate.

**Plan 39 done 2026-05-23** — [x] Track C tidy-day batch + Track P Playwright `targets_selector` enhancement (Track D split to Plan 40). **Track C:** (C1) deleted **41 stale remote branches** via `gh api -X DELETE` loop — far more than the "6 stale" the prompt anticipated; only `main` remains. (C2) session-starter.md gained a new "Code's Operating Environment (Brief)" section after "How We Work Together" with the 6 named drift items (autonomous-merge policy, allowlist 3-tier+, bash safety + hook precedence, EC2 dbt PATH, scp→pull lock, git push postBuffer). (C3) **275 data_type annotations** added across `dbt/models/bronze/schema.yml` (135 columns under `models:` section) + `dbt/models/gold/schema.yml` (140 columns), via `scratch/enrich_schema_yml.py` querying DuckDB DESCRIBE; 0 missing; `dbt parse` clean post-enrichment. (C4) tech-debt review item 13 = stale "LOG.md Recent Sessions rotation — currently 6 entries (41-46)" self-flag in TASKS.md (long resolved; current Recent is 5 entries 59-63); removed the stale `[ ]` entry + adjacent stale "Auto-refresh portal stats" item that had a "can be removed" parenthetical. **Track P:** `scripts/rendered_page.py` `review_page()` gained `targets_selector` parameter (default `None` preserves Plan 33/34 back-link behavior); new `_SELECTOR_TARGETS_PROBE` JS function; P3 label cascade (`data-panel-id` → `id` → first text node truncated). Smoke test against v1 admin dashboard with `targets_selector='.panel'` produced 10 numbered callouts with text-fallback labels (panels lack `data-panel-id` until Track D D3 adds them). STANDARDS.md §8 + CLAUDE.md verification-gates rule 5 updated. Design-review artifact at `docs/design-reviews/playwright-targets-selector-smoke-2026-05-22/`. **Track D split to Plan 40** per Code's call after surfacing scope — Track D (cost panel + 30d sparkline + 5 source-health timers + design doc revision + Playwright v1.1 verification) is realistically 2-4 more hours and deserves a fresh thread.

**Plan 40 done 2026-05-24** — [x] DBA Dashboard v1.1: cost panel replacement + source-health expansion. **D1:** `panel_c2_token_spend` deleted, replaced with `panel_c2_cost` — month-to-date Anthropic spend ($43.65 on first render) + 30-day inline-SVG sparkline (7 active days) + burn-rate-vs-last-month delta (currently "no prior-month baseline" since April had no chat activity; meaningful from June 1 onward). D1-edge: no `model` column on `messages` table; project's config.yml is single-model Opus 4.7; flat-rate calculation documented in new limitations entry `docs/limitations/cost-panel-pricing-assumptions.md`. **D2:** Refactored `scripts/source_health_check.py` to parameterized form (one script handles all 6 Socrata-API datasets — pre-flight found all 6 share `/api/views/{id}.json` shape with `rowsUpdatedAt`, including the wards "shapefile blob" and at-a-glance JSON; the prompt's premise of 3 separate scripts was based on data shape but the API shape is uniform). Existing 311 systemd unit updated for new arg-required script; 5 new timer + service pairs (crime / permits / traffic-citations / wards / at-a-glance) installed + enabled. Per-dataset staleness thresholds reflect documented refresh expectations. All 6 sources visible in B1 panel on first regeneration. **D3:** `data-panel-id` attribute added to each panel element via `render_panel()`; 10 panels (A1-D2) all have the attribute. **D4:** `docs/dba-dashboard-design-2026-05-17.md` revised — §0 revision-2 note, §3 Group B B1 updated for 6-source coverage, §3 Group C now includes C2 spec, §11 marked C2 shipped (C3 AWS still future). **D5:** Playwright verification at `docs/design-reviews/admin-dashboard-v1-1-2026-05-22/`. Live headline YELLOW with 4 advisory items (vs 2 in v1): A2 streak 92%, A3 duration +30% trend, B1 2/6 sources non-healthy (real-stale: crime + traffic-citations 26 days old), B2 1 dbt warn. Worth flagging: B1's expanded coverage surfaced real-stale state that v1's single-source view had hidden. **Design call surfaced**: 1 parameterized checker instead of 3 separate scripts (Socrata API shape uniform across data shapes).

**Plan 41 reserved** [ ] DBA v1.2 — staleness-threshold calibration based on a few weeks of v1.1 data + A3 duration-trend threshold widening (currently 20%, too tight for project scale).

**Plan 42 reserved** [ ] Memory-to-file migrations per Plan 36 §3 (was Plan 38, 40, 41, now Plan 42 after Plan 41 got reserved for DBA v1.2 calibration). Five candidates: `feedback_session_boot_audit.md` → CLAUDE.md; `feedback_git_ssh_gotchas.md` → CLAUDE.md "Known gotchas"; `feedback_no_ssh_heredocs.md` → CLAUDE.md "Bash Safety"; `feedback_chat_code_handoff.md` → PROMPTS.md; `feedback_settings_json.md` → CLAUDE.md "Allowlist policy" sub-bullet. Each needs deliberate placement + wording decisions. **Coordination note:** Plan 43 (prompt+report lineage) also touches PROMPTS.md §5; whoever ships second rebases.

**Plan 44 done 2026-05-25** — [x] Happiness Survey silver + gold curation (MVP 3, trend-only). **First silver model in the project.** **Phase A:** `main_silver.stg_happiness_survey` — per-respondent (id, year) grain, 12,583 rows = bronze count, 8 curated `_num` columns from the Phase D matrix cast to DOUBLE, ward preserved NULL, `weight` reserved-NULL. dbt_utils not installed → inline range tests via accepted_values [1..5] with `is not null` predicates. **Phase B:** 3 gold models — `dim_survey_question` (8 rows hand-rolled with 5-bucket topic taxonomy + coverage profile from Phase D matrix), `dim_survey_wave` (8 rows data-driven from silver), `fct_happiness_survey` (trend fact at wave × geography_level × geography_key × question grain via UNION city + ward CTEs; 2011 excluded from ward aggregation; Likert distribution columns enable top/bottom-two-box at semantic layer; `weight_strategy` reserved-NULL). Deliberate absence of relationships test on `geography_key` → `dim_ward` documented. **Phase C:** 3 semantic views + new `perception` topic; `answer_agent.agent.yml` `context.topic` glob expanded to include all 5 topics (was only `service_requests`). **Phase D:** updated `happiness-survey-self-selection-and-coverage` status section + new "What MVP 3 silver/gold did and did not do" section; new `survey-gold-unweighted` (medium severity, respondents-not-residents framing) + `survey-trend-only-no-demographics` (low severity, k-anonymity-by-absence rationale). **Phase E — all 5 live-functional gates ✅:** dbt run 16/16 PASS; dbt test 111/111 PASS; `oxy validate` 21/21 valid; `./run.sh manual` exit 0 in 875s (run_id `01KSGZ0MJB2AGACM4N2S83RW3G`; 129 PASS bronze/gold tests + 13 PASS admin tests; `/erd` Silver-tier auto-resolved per Plan 25's claim — `portal/erd-tier-silver.mmd` now lists 1 model; `/metrics` regen surfaces 29 measures × 14 views, +7 from perception); answer-agent smoke test 2/2 PASS (Q1 life satisfaction city trend 2013-2025, mean 4.12→3.95, top-two-box 89.1%→78.0%, trust contract fires citations + all 2 relevant limitations; Q2 happiness Ward 3 vs Ward 5 2023, both ~3.83 mean / ~74% top-two-box, trust contract fires all 3 limitations including the new `survey-trend-only-no-demographics` because the question naturally invites demographic slicing). **Phase F:** LOG.md Plan 44 row + original Plan 24 row flipped to "done (under Plan 44)" + Last Updated bump + Session 67 entry + Session 62 rotated to Earlier; TASKS.md Next Focus header rewritten with new follow-ups (weighting computation + perception-trend dashboard + operational-pairing analysis); session file at [`session-67-...`](docs/sessions/session-67-2026-05-25-plan-44-happiness-survey-silver-gold.md); Plan 43 prompt+report sibling files at `docs/prompts/plan-44-happiness-survey-silver-gold.{md,report.md}`. Halt conditions did not fire. **Decisions:** (a) permissive fact-row filter (any wave/question combo with ≥1 respondent gets a row; matrix threshold travels in dim_survey_question for analyst-side filtering — vs strict filter that would silently drop real 2025 education_quality responses); (b) `[paraphrase]`-prefixed question_label values rather than NULL or invented text; (c) topic taxonomy of 5 buckets assigned by Code with rationale in commit.

**Plan 43 done 2026-05-24** — [x] Prompt + report lineage in `docs/prompts/`. **Phase A:** new directory; `docs/prompts/README.md` names the filename convention (`plan-NN-<slug>.md` for prompts; `plan-NN-<slug>.report.md` for reports), lifecycle, lineage chain (Plans Registry ↔ prompt file ↔ session file ↔ report file ↔ PR), backfill policy, coexistence with `docs/handoffs/`. Three reconstructed prompts backfilled with explicit reconstruction notes citing sources + confidence: [`plan-37-allowlist-edits`](docs/prompts/plan-37-allowlist-edits.md), [`plan-38-dba-dashboard`](docs/prompts/plan-38-dba-dashboard.md), [`plan-39-tidy-c-playwright`](docs/prompts/plan-39-tidy-c-playwright.md). Reports NOT backfilled per prompt's out-of-scope. **Phase B:** PROMPTS.md §5 Step 4 amendment (file-side restatement) + Step 9 amendment (sibling `.report.md`) + new §5.5 subsection naming the convention; CLAUDE.md "Receiving prompts from Chat" 4th internalized bullet (3 → 4 rules); session-starter.md "How We Work Together" + "Key Files to Know" updated. **Phase C:** LOG.md Plans Registry row + Last Updated bump + Session 66 Recent entry (Session 61 rotated to Earlier per 5-entry cap); session file at [`docs/sessions/session-66-2026-05-24-plan-43-prompt-report-lineage.md`](docs/sessions/session-66-2026-05-24-plan-43-prompt-report-lineage.md). **Smoke test passed end-to-end on birth session:** prompt arrived via paste, copied verbatim into `docs/prompts/plan-43-prompt-report-lineage.md` as first execution step; sibling `plan-43-prompt-report-lineage.report.md` written as last commit before merge. No halt conditions fired (Plan 42 not in flight; directory net-new; smoke-test gate satisfied).

**Plan 35 done 2026-05-23** — [x] Bottom back-link consistency fix. Plain-Markdown shape applied to bottom link; both back-links now render byte-identically as cyan anchors (computed-style exact match top vs bottom). All 5 sub-gates passed via Plan 33's helper. Boot-audit B1 step-4-extension first-real-use caught the 2026-05-22 systemd portal/index.html drift (+727 311 rows, dates and pipeline timestamp advanced) → committed as separate hygiene PR [#61](https://github.com/ironmonkey88/oxygen-mvp/pull/61) (`6b94a1b`) ahead of Plan 35's main PR [#62](https://github.com/ironmonkey88/oxygen-mvp/pull/62) (`343b5a9`). Design review at `docs/design-reviews/bottom-back-link-fix-plan-35-2026-05-22/`. See [Session 60](docs/sessions/session-60-2026-05-23-plan-35-bottom-back-link.md).

**Plan 34 done 2026-05-23** — [x] dbt-docs back-link fix v2 + carry-over drift items. Track A Approach #1 shipped: plain Markdown `[← Back to Somerville Analytics portal](/)` for top link; all three sub-gates passed via Plan 33's helper (DOM is `<a>`, color cyan vs body gray, click navigates `/docs/` → `/`). Track B: `.oxy_state/` gitignored, boot-audit memory extended with portal/index.html drift check, CLAUDE.md "Known gotchas" subsection added with `http.postBuffer 524288000` note. PR [#60](https://github.com/ironmonkey88/oxygen-mvp/pull/60) merged `751b460`. Design review at `docs/design-reviews/back-link-fix-plan-34-2026-05-22/`. See [Session 59](docs/sessions/session-59-2026-05-23-plan-34-back-link-fix.md).

**Plan 33 done 2026-05-23** — [x] Playwright + Pillow rendered-page helper on EC2 with `test_page(url, assertions) -> TestResult` and `review_page(url, output_dir, focus) -> ReviewArtifact` entry points. Shipped `scripts/rendered_page.py` (260 lines), STANDARDS.md §8 "Rendered-page verification", CLAUDE.md verification-gates rule 5, `docs/design-reviews/README.md`, plus worked-example finding at `docs/design-reviews/dbt-docs-library-inspection-2026-05-22/`. **Library identified:** marked.js with `sanitize: true` — three independent signals (project URL in error code, exact API error strings, 39 token frequency vs. 0 for any other library). **Bonus findings:** dbt-docs SPA is AngularJS 1.x (two un-substituted `{{ ... }}` 404s in network log); all JS inlined in the 1.8MB index.html (no external bundle requests); marked wrapped in custom AngularJS `marked` directive. Halt-and-surface fired cleanly during pre-flight when ARM64 Chromium needed `sudo playwright install-deps` for system libs; Gordon approved. Live-functional gate passed: `python scripts/rendered_page.py --demo-inspect-dbt-docs-library` ran end-to-end producing `annotated.png` + `finding.md` + 5 evidence files (`screenshot.png`, `network-requests.json`, `window-globals.json`, `back-link-dom.json`, `rendered.html`).

**Plan 32 halted 2026-05-22** — [!] dbt docs back-link fix didn't work. Wrapped top `<a>` in `<div>` on branch `claude/plan-32-docs-back-link-fix` (local-only, not pushed), scp'd to EC2, ran `dbt docs generate`, asked Gordon to load `/docs/` over Tailscale. **Both** outcomes were broken: (1) top link still rendered as literal HTML source text — `<div>` wrap didn't change the rendering; (2) bottom link also rendered as literal HTML (outcome b per prompt — same broken state, just unverified before this). Per prompt's named halt condition: "Do not iterate blindly; surface the finding and stop." Reverted EC2 to clean main + re-ran `dbt docs generate` against unchanged source so `/docs/` is back to consistent-with-main state. Local branch retained for follow-up. Diagnostic implication: the SPA's client-side Markdown renderer isn't recognizing `<div>` as block HTML (or something else is escaping the angle brackets); prompt's alternate suggestions are `<p>` wrap or HTML-comment delimiters, but those are guesses too — a real fix needs identifying which Markdown library the dbt-docs SPA bundles and what its block-HTML rules are. Out of scope for this prompt. Gordon to scope follow-up.

**Plan 31 done 2026-05-21** — [x] portal regen catch-up. After confirming all 6 recent PRs (#50–#55) were merged and that EC2 had been stranded on the merged `claude/bold-dirac-7b6669` branch with three uncommitted regen outputs, fast-forwarded EC2 to main (`ee02a42`) and re-ran `./run.sh manual` cleanly: run-id `01KS6T402GAGXATYW3R986AJCH`, 877s, exit 0, all 10 stages green, dbt test bronze/gold + admin both exit 0. Committed the three regen outputs that the pipeline produced against the current data: `docs/limitations/_index.yaml` (+6 entries that already exist as `.md` files in main: citations-composite-grain-violation-suffix, oxy-df-interchange-empty-result-panic, permits-spatial-ward-derivation, somerville-at-a-glance-uneven-year-coverage, spa-artifact-load-404, plus 1 more); `portal/erd-tier-gold.mmd` (+1 line — the `fct_311_requests }o--|| dim_ward : "ward"` arrow from Plan 27, now 10 within-tier rels matching the pipeline output); `portal/index.html` (stats refresh — 31 limitations / 1,174,638 311 rows / 118/118 DQ tests / latest data 2026-05-21). Closes the loose ends from the cross-session merge audit Gordon flagged 2026-05-21 23:00 ET. See [Session 56](docs/sessions/session-56-2026-05-21-plan-31-portal-regen-catchup.md).

**Plan 30 done 2026-05-22** — [x] loose-ends batch. Item 1 (`2486135`): `ward` entries consolidated in `fct_permits` and `fct_citations` (same dedup pattern as Plan 29 Item 3); EC2 `dbt parse` clean + `dbt test --select fct_permits fct_citations` → 12/12 PASS with both `relationships_fct_*_ward__ward__ref_dim_ward_` tests intact. Item 2 — no-op: `PRODUCT_NOTES.md` Entry 5 (annotated multi-track civic timeline) already on main via PR [#51](https://github.com/ironmonkey88/oxygen-mvp/pull/51) commit `c567fd4`. All four 311/crime/permits/citations fact tables now carry a single consolidated `ward` column entry; gold/schema.yml hygiene pattern is uniform across the medallion's gold facts.

**Plan 29 done 2026-05-21** — [x] tidy-day batch (8 items from the 2026-05-17 tech-debt review + EC2 credential check). All commits + EC2 verifications passed. (1) `scripts/generate_metrics_page.py` `avg` → `average` (commit `33569fa`); EC2 regen confirms `AVG(` × 2 / `AVERAGE(` × 0. (2) `run.sh` `deploy_html` precondition + atomic write + chown un-masked (`5bb3761`); 4-scenario local smoke PASS. (3) `dbt/models/gold/schema.yml` ward dedup in fct_311_requests + fct_crime_incidents (`be3cfdc`); EC2 `dbt test --select fct_311_requests fct_crime_incidents` → 19/19 PASS. (4) CLAUDE.md LLM config Sonnet → Opus (`60a1454`). (5) CLAUDE.md file-structure refresh (`83744be`). (6) `docs/schema.sql` rewritten with `main_*` schemas + retitled as agent context, endpoint (a) (`75de3c2`). (7) `.claude/settings.json` `sudo cp/mv/ln` scoped to `/etc/nginx/*` + `/etc/systemd/system/*`, `/etc/*` denies added for cp/mv/ln, plus `rm -fr *` + `git push --force-with-lease *` denies (`cb64e15`); allowlist `[x]` evidence: `git show HEAD:.claude/settings.json | grep -F 'Bash(sudo cp * /etc/nginx/*)'` returns a match. (8) EC2 `/etc/environment` chmod 644 → 640; oxy.service restarted `active`; `/api/health` returns `{"status":"healthy","database":{"connected":true}}`. Trust-contract smoke on EC2: `oxy run agents/answer_agent.agent.yml "How many 311 requests were opened in 2024?"` → **113,961** with `main_gold.fct_311_requests` cited correctly. See [Session 55](docs/sessions/session-55-2026-05-21-plan-29-tidy-day-batch.md).

**Plan 28 done 2026-05-17** — [x] PHILOSOPHY.md landed at repo root (commit `0877242`) plus the three wiring sites per the Plan 22 pattern: CLAUDE.md new "Convictions (foundational, not authority)" tier above Strategic+construction; session-starter.md "How We Work Together" pointer; PROJECT_BRIEF_5_11_26.md §10 reference-map row. Content-additive only — no edits to existing authority docs. See [Session 54](docs/sessions/session-54-2026-05-17-plan-28-philosophy.md).

**Plan 27 done 2026-05-16** — [x] two-item follow-up complete: (a) `fct_311_requests.ward → dim_ward` relationships test added to `dbt/models/gold/schema.yml` (commit `e549a93`); verified on EC2 — `dbt test --select fct_311_requests` 5/5 → 6/6 PASS, new test surfaces as `relationships_fct_311_requests_ward__ward__ref_dim_ward_`, no orphan ward rows (halt condition didn't fire); /erd gold tier reads 10 FK arrows after next regen. (b) `docs/sessions/session-52-2026-05-16-plan-26-housekeeping.md` reconstructed from Plan 26 commit `97f32d6` + LOG.md row + limitations diff (honest note that it was written after the fact in Session 53). See [Session 53](docs/sessions/session-53-2026-05-16-plan-27-ward-fk-and-narrative.md).

**Plan 26 done 2026-05-16** — housekeeping pass. LOG.md Recent Sessions rotated to the 5-entry cap (Sessions 39-46 moved to Earlier Sessions as one-liners). New `oxy-df-interchange-empty-result-panic` limitations entry created (was queued but never made). Oxy customer-feedback doc `[VERIFY]` markers filled inline; ready for Gordon to send to Oxy.

**Plan 25 done 2026-05-16** — per-tier column-level erDiagrams now live on `/erd` below the tier flowchart (Bronze 7 / Silver placeholder / Gold 12 with 9 FK arrows / Admin 3). The Silver placeholder will auto-populate when Plan 24's first silver model lands — no further ERD work needed. See [Session 51](docs/sessions/session-51-2026-05-16-plan-25-per-tier-erdiagrams.md).

**Plan 23 fully resolved 2026-05-15.** All four phases done:
- Phase A (Permits) PR [#36](https://github.com/ironmonkey88/oxygen-mvp/pull/36) merged `d269aab`. Spatial ward 96.62%; new `built_environment` topic.
- Phase B (Citations) PR [#38](https://github.com/ironmonkey88/oxygen-mvp/pull/38) merged `1c48ed7`. Honest finding: source publishes ward directly (0.12% NULL); spatial join skipped. Joins `public_safety` topic.
- Phase C (At-a-Glance) PR [#39](https://github.com/ironmonkey88/oxygen-mvp/pull/39) merged `0ebadc9`. Honest finding: 4-column SK after two test-driven iterations (`topic + year + description + geography`); compendium has Somerville + MA benchmark rows. New `city_context` topic.
- Phase D (Survey) **HALTED** per prompt's named gate: 8/50 `_num` columns survived cross-wave-presence filter (threshold ≥12). Dedicated MVP 3 silver/gold plan required. Column matrix in [happiness-survey-self-selection-and-coverage](docs/limitations/happiness-survey-self-selection-and-coverage.md).

**Next natural threads:**

1. **Plans 18 + 19 — Builder-CLI dashboards** — now buildable with all six datasets in gold + semantic. Cross-source analyst questions (permits vs 311 by ward; citations vs crime by ward; demographic context from At-a-Glance) ready.
2. **MVP 3 — Happiness Survey silver/gold curation** as a dedicated plan. Scope: year-aware column filtering, question-key harmonization across waves, k-anonymity gates on demographic combinations, weighting strategy for joined aggregates.
3. **MVP 3 — silver layer for permits + citations** — citation-event-grain derived view (suffix-strip), ward-trim, status-cleanup on permits.

**Cumulative verification done Session 50 (2026-05-16):** `./run.sh manual` success in 897s on EC2 (run-id `01KRQDK2JT3MNQG6Q9Y5AEM2AB`); `/metrics` regenerated to 22 measures × 11 views; both chat agent test questions answered with trust contract firing. Plan 23 closed end-to-end. Two durability items also landed: STACK.md DuckDB-spatial pattern + pre-flight rule; autonomous-PR-merge policy moved to committed CLAUDE.md.

### Carry-over queued items

- [ ] Builder-CLI dashboard on "permits vs 311 complaints by ward" (Plan 18 redux with the new bronze data)
- [ ] Silver layer: ward-trim, type casts, citation-grain derived view, spatial ward join for permits + citations

---

## Sign-off Status

### MVP 1 — 1st Data Product
- [x] Environment set up on EC2
- [x] GitHub repo initialized and connected
- [x] dlt pipeline ingesting Somerville 311 data — 1,168,959 rows loaded
- [x] Data model designed — schema.sql written, ERD generated
- [x] nginx installed, portal live and verified at http://18.224.151.49
- [x] dbt initialized; bronze model live (1.17M rows, 5/5 tests pass)
- [x] dbt gold models live: `dim_date` (3,993), `dim_request_type` (342), `dim_status` (4), `fct_311_requests` (1,168,959); 14/14 tests pass
- [x] Portal designed and fonts self-hosted (DM Serif Display, DM Mono, Instrument Sans)
- [x] Portal verified live in browser at http://18.224.151.49
- [x] Airlayer CLI 0.1.1 installed on EC2
- [x] Airlayer semantic layer: 4 views + 1 topic, schema valid, executes via auto-join
- [x] Oxygen runtime live on EC2 — `oxy start` brings up Postgres container + web app on :3000; `oxy build` exits 0 in plain non-interactive ssh
- [x] Env vars in `/etc/environment` — `ANTHROPIC_API_KEY`, `OXY_DATABASE_URL`, plus `~/.local/bin` on PATH; documented in [SETUP.md](SETUP.md) §7
- [x] Answer Agent `.agent.yml` configured — minimal FR scope (no trust contract yet)
- [x] Chat UI accessible and answering questions correctly — verified in SPA at `http://oxygen-mvp.taildee698.ts.net:3000` after Session 25 pivot to `oxy start --local`. "How many 311 requests were opened in 2024?" returned 113,961 with execute_sql artifact + "Returned 1 row." + Citations (`main_gold.fct_311_requests` + `requests` Airlayer view) + analyst-honest Known limitations section. CLI `oxy run` path also intact across full bench 5/5 (Q1 113,961, Q2 49,782 YTD, Q3 top types match, Q4 block-code-padded NA sentinel surfaced, Q5 satisfaction 4.44/5 blended). Reboot survival proven Sessions 24 + 25.
- [x] Trust contract on agent (SQL + row count + citations in every response)  *(Plan 6 — STANDARDS §4.1 4/4)*
- [x] Admin DQ framework in place  *(2026-05-08 — D2 of overnight; 3 admin models, run.sh, load_dbt_results.py; verified across 2 consecutive runs)*

### MVP 1.5 — Post-Sign-off Hardening
- [x] Switch Answer Agent from Sonnet 4.6 to Opus 4.7 *(2026-05-11; commit `a5853d0` switched `config.yml` + `agents/answer_agent.agent.yml`; CLI bench 5/5 + SPA bench Q1–Q5 in single thread, no `ApiError`; rate-limit headroom 30K → 500K tokens/min; `agent-rate-limit-multi-turn-spa` limitation `mitigated-by-opus-4-7-migration`)*
- [x] Portal polish: Sonnet → Opus refs (3 places), `Last data point` + `Last pipeline run` stats added, stats grid responsive, trust page section max-width 1100 → 1400 *(2026-05-11)*
- [ ] Auto-refresh portal stats dates from DuckDB on `run.sh` *(hardcoded for now; should sed-substitute from `MAX(date_created_dt)` + run timestamp on each pipeline run; small Python script + run.sh step 7.5 pattern)*
- [ ] Somerville wards map as hero background *(Socrata wards dataset `ym5n-phxd` is blob-only, not exportable as GeoJSON; OpenStreetMap Overpass query returns errors; pragmatic path: render a stylized SVG outline manually from MassGIS shapefile or trace the city PDF at https://www.somervillema.gov/sites/default/files/ward-and-precinct-map.pdf; deferred for a focused pass)*
- [x] Public chat access via nginx Basic Auth at `/chat` *(2026-05-11; final design: auth-gate only `/chat` entry; SPA internal paths `/api`, `/assets`, `/home`, `/threads`, `/oxygen-*` proxy unauth (the SPA's streaming agent POST omits credentials, so gating those paths loops). bcrypt `analyst` credential in `/etc/nginx/.htpasswd` root:www-data 640 — NOT in repo, .gitignore hardened. Portal hero pill clickable. **Gate 4 PASSED**: Gordon SPA-tested in browser, asked "how many requests", agent returned 1,170,023 with execute_sql artifact + Citations, no second auth prompt. Trade-off recorded at `docs/limitations/chat-auth-basic-cleartext.md` — API-token-burn risk only, no data exposure; replaced by MVP 4's Magic Link + HTTPS)*

#### Plan 1a — Daily Incremental Refresh + Observability *(2026-05-11 — in progress)*
Foundation for Plan 1b. Architectural decisions resolved in chat: (A) Python owns `*_raw` admin tables; (B) systemd unit drops oxy dependency; (C) dlt-direct-to-DuckDB merge replaces filesystem Parquet; (D) preserve captured-exit pattern in run.sh; (E) /trust surfacing deferred to follow-on; (F) load_dbt_results lives in `dlt/`, no `check_drift.py` (drift via `dbt test --select admin`); (G) modified-field name TBD from SODA pre-flight.

- [x] Step 0 — Pre-flight: dlt 1.26.0 ✓ python-ulid installed ✓ bronze schema captured ✓ gold count 1,170,023 ✓ PK confirmed `id` (not `case_id`) ✓ **modified-field finding**: dataset has NO publisher-maintained per-row modified column; Socrata's `:updated_at` is republish-batch-level → switched plan from watermark+3-day-lookback to **full-pull + merge on `id`** per pre-flight recommendation (path 1)
- [x] Step 1 — Audit columns on bronze: `_extracted_at`, `_extracted_run_id`, `_first_seen_at`, `_source_endpoint` populated on 1,170,591 rows; 0 NULLs across all four; bronze.yml descriptions updated *(commit pending)*
- [x] Step 2 — Pipeline refactor: filesystem-Parquet → DuckDB direct, `dlt.destinations.duckdb`, write_disposition=merge on `id`, full pull (no watermark); bronze view repointed at `main_bronze.raw_311_requests_raw`; gold rebuilt; 19/19 tests pass; **2024 regression check: 113,961 (exact match to Plan 6 D3)**
- [x] Step 3 — `scripts/pipeline_run_start.py` + `scripts/pipeline_run_end.py` + Python-owned `main_admin.fct_pipeline_run_raw`; smoke-tested with manual run_id 01KRD6G8EHV0J4RJAM1XQWKWA3, INSERT + UPDATE both work; `run.sh` rewritten preserving captured-exit pattern (decision D) with trap-on-error → record failed status
- [x] Step 4 — `scripts/source_health_check.py` + Python-owned `main_admin.fct_source_health_raw`; smoke-tested, check_status=ok, source_row_count=1,170,591, 7 hours since `rowsUpdatedAt`, HTTP 200
- [x] Step 5 — End-to-end `./run.sh manual` validation: first attempt's `set +e ; cmd ; set -e` captured-exit tripped the ERR trap on bash 5.x (run logged as failed at stage `dbt_test_admin`); switched to the `cmd || rc=$?` idiom (POSIX-exempt from errexit), reverified via partial-run test on EC2 → all 10 stages execute, `run_status='partial'` recorded when admin tests fail. Three rows now in `main_admin.fct_pipeline_run_raw` (the 5s standalone test, the 770s broken-trap run kept as history, the 29s partial run with fix).
- [x] Step 6 — `systemd/pipeline-refresh.{service,timer}` deployed; `pipeline-refresh.timer` shows next-run **Tue 2026-05-12 10:00:00 UTC = 6:00 AM EDT** in `systemctl list-timers`. No `oxy.service` dependency.
- [x] Step 7 — `systemd/source-health-check.{service,timer}` deployed; `source-health-check.timer` shows next-run **Tue 2026-05-12 05:00:00 UTC** (top of next hour, 22 min after activation).
- [x] Step 8 — Two limitations entries written: `source-bulk-republish-no-per-row-modified.md` (honest documentation that source publishes in bulk with no per-row modified field) and `audit-columns-non-analytics.md` (the six underscore-prefixed metadata columns are not analytics). `docs/limitations/_index.yaml` regenerated: 10 → 12 active entries.
- [x] Step 9 — `ARCHITECTURE.md` gained "Pipeline & Observability" section + Run Order updated to 10 stages with captured-exit + trap detail; `CLAUDE.md` Run Order section synced; `SETUP.md` §5 added `python-ulid` to pip install, new §15 "Pipeline scheduling" with install/verify/manual-invoke/inspect snippets; `LOG.md` Active Decisions row for Plan 1a with full change set; `docs/sessions/session-29-...md` narrative written.
- [x] Step 10 — Commit `a0f4904` on `claude/nice-shtern-4d9efc` (20 files, +1015/-87). Local-only — push/merge to `main` pending Gordon's call.

#### Plan 1b — Column Profiling + Portal Documentation *(2026-05-12 — in progress)*
Architectural decisions resolved in chat: **1b/A** = Python-owned `fct_column_profile_raw` (same pattern as Plan 1a admin tables); **1b/D** = option (c) — keep `dbt/models/*/schema.yml` hand-written, surface profiles on a new dedicated `/profile` portal page driven by `fct_column_profile_raw`, never touch dbt's schema files programmatically.

- [x] Phase 1 — `scripts/profile_tables.py` + `main_admin.fct_column_profile_raw` (Python-owned); 75 columns profiled in 5.5s after adding `_dlt_*` + `*_raw` exclusion patterns
- [x] Phase 2 — `scripts/check_profile_staleness.py` reports `CURRENT` after fresh profile run; wired into run.sh stages 9b (`cmd || rc=$?` form) + 9c (conditional regen)
- [x] Phase 3 — `scripts/generate_profile_page.py` writes `portal/profile.html` (75 columns, 5 tables, 73KB); reads `schema.yml` for descriptions + `fct_column_profile_raw` for shape; dbt schema files never touched
- [x] Phase 4 — `scripts/generate_warehouse_erd.py` (8 models, 2 relationships from dbt `relationships:` tests; audit cols omitted) + `scripts/generate_semantic_layer_diagram.py` (1 topic, 4 views, 4 base tables)
- [x] Phase 5 — `scripts/generate_erd_page.py` assembles `portal/erd.html` with both Mermaid sources via jsdelivr CDN; `nginx/somerville.conf` gains `location = /profile` + `location = /erd`; reload tested. Portal nav (`portal/index.html`) extended with `/erd` and `/profile` links; live homepage verified
- [x] Phase 6 — `systemd/profile-tables.{service,timer}` deployed; `systemctl list-timers` shows next run **Sun 2026-05-17 06:00:00 UTC = 2:00 AM EDT**; `ExecStartPost` refreshes `/profile` page + deploys after each regen. No `oxy.service` dependency
- [x] Phase 7 — `ARCHITECTURE.md` (Pipeline & Observability extended; 5-route portal table); `SETUP.md` (§15 → 3 timers, run-order list bumped to 9b–9e); `CLAUDE.md` (Plan 1b workflow note with manual `profile_tables.py + generate_profile_page.py` after dbt model changes); `LOG.md` (Active Decisions row); `docs/sessions/session-30-...md` narrative written
- [x] Phase 8 — Commit `0a0a065` (2026-05-12 10:36 EDT) on `claude/eloquent-varahamihira-a0c106`

### MVP 2 — Visual Knowledge Products
- [ ] Airapp `.app.yml` with charts

### MVP 3 — Governance and Trust
- [ ] dbt Silver model with PII redaction
- [ ] dbt Gold model updated with dim_location
- [ ] Tailscale access control

### MVP 4 — Semantic Depth and Sharing
- [ ] Full Airlayer metric library
- [ ] Routing Agent configured

---

## Overnight Session — 2026-05-07 → 2026-05-08

### Deliverable 0 — Doc cleanup
- [x] Apply CLAUDE.md + ARCHITECTURE.md edits, commit, push
- [x] EC2 `git pull origin main` and verify commit landed

### Deliverable 1 — Gold dbt models
- [x] Query bronze on EC2 to confirm column names/types
- [x] Write `gold/dim_date.sql`
- [x] Write `gold/dim_request_type.sql`
- [x] Write `gold/dim_status.sql`
- [x] Write `gold/fct_311_requests.sql`
- [x] Add gold tests (unique/not_null/relationships)
- [x] `dbt run --select gold` and `dbt test --select gold` clean
- [x] Commit and push gold models

### Deliverable 2 — Airlayer CLI install
- [x] Install Airlayer CLI on EC2; `airlayer --version` works (0.1.1)
- [x] Sanity check `airlayer query --help` runs (CLI shape note logged)
- [x] Log version + system packages added to LOG.md
- [x] Commit LOG.md/TASKS.md update

### Deliverable 3 — Semantic layer
- [x] Create `semantics/views/{requests,request_types,statuses,dates}.view.yml`
- [x] Create `semantics/topics/service_requests.topic.yml`
- [x] Update `config.yml` to register `somerville` datasource (oxy 0.5.47 schema: `model_ref`/`key_var`)
- [x] ~~`oxy build` exits 0~~ — *gate downgraded 2026-05-08 07:31 ET. `oxy validate` (config syntax, exits 0) + `airlayer query -x` (real data, 5 rows) cover the intent; `oxy build` (vector embeddings) only matters once `oxy start` is up, which lands with the Answer Agent.*
- [x] `airlayer query ... -x` returns rows (5 rows, auto-join via entity match)
- [x] Commit and push semantic layer

---

## MVP 1 — 1st Data Product
**Goal:** Static data file → DuckDB → Airlayer → Answer Agent chat UI

### Scope statement
- Target user: city analyst, not general resident
- Goal: analyst asks Answer Agent a question, gets a correct answer with SQL + row count + citations, and can verify it independently
- Bar: extreme trustability — every answer is inspectable and reproducible
- Out of scope this MVP: charts, exports, follow-up suggestions, anomaly surfacing, /about page, long-form .qmd-style docs
- See [STANDARDS.md](STANDARDS.md) for "done done" criteria

### Repo Cleanup (Session 5)
- [x] Audit local Mac vs EC2 vs GitHub for missing source files
- [x] Recover `dlt/somerville_311_pipeline.py` into the repo (live EC2 copy)
- [x] Recover `dbt/dbt_project.yml` and `dbt/models/bronze/*` from EC2 backup
- [x] Update `bronze/raw_311_requests.sql` to mirror all 22 source columns per `docs/schema.sql`
- [x] Verify Bronze model builds and 5/5 tests pass on EC2
- [x] Add `dbt/profiles.yml` to `.gitignore`; remove repo-local profile alternative from `SETUP.md`
- [x] Confirm `dim_origin` and `portal/` already present in `ARCHITECTURE.md` and `TASKS.md`

### MVP 1 — Hardening for analyst trust

#### Plan 6 — Answer Agent + Trust Contract (2026-05-09 21:00 ET — closed)
Closes STANDARDS §4.1 (4/4) and §5.7 (4/4).
- [x] Pre-flight: agent yaml + limitations read; Oxygen runtime confirmed up (curl :3000 → 200; `oxy start` running as nohup since May 8 — not as systemd, that's a §3.2 row 4 gap for Plan 7); STANDARDS §7 open question resolved (partial native — runtime renders SQL+result; citations/row-count/limitations are prompt-enforced); CLI invocation = `oxy run agents/answer_agent.agent.yml "<question>"`
- [x] D1 — Trust contract in `agents/answer_agent.agent.yml` `system_instructions`: 4-section reply contract (Returned N rows / Answer / Citations / Known limitations); engineering-honest tone (no emoji, no marketing); limitations index loaded as `context.file` `docs/limitations/_index.yaml`; commit `b3b5217` + index-only follow-up
- [x] D1 follow-up — switched from full-bodies `*.md` glob to `_index.yaml` after Q3+Q5 first-attempt rate-limited at 30K tokens/min (full-body context too large); index pipeline (`scripts/build_limitations_index.py` + `run.sh` step 9/9) generates the index from frontmatter
- [x] D2 — Matching rule: substring of any `affects:` value appears in SQL or in cited views; prompt-only (no post-processing wrapper); verified Q4 surfaced `block-code-padded` + `location-ward-block-only` correctly with no false positives; verified Q5 surfaced `2024-survey-columns-sparse` + `survey-columns-on-fact` correctly
- [x] D3 — 5/5 test bench passed (transcripts in `scratch/plan6_test_bench/q[1-5]_*.md`): Q1 2024=113,961 ✓ (regression match), Q2 partial-year 49,782 ✓ (SQL correct; agent prose hallucinated "2025" — knowledge-cutoff issue, follow-on for prompt hardening), Q3 top-10 ✓ (Pothole at #10 with 21,393), Q4 block-level ✓ (with diligent NA-sentinel callout), Q5 satisfaction ✓ (76.0% Very Satisfied, both survey limitations surfaced, percentage math reconciled)
- [x] D4 — STANDARDS §4.1 4/4 + §5.7 4/4 flipped; STANDARDS §7 open question resolved; session 18 file; LOG.md updated; commits `b3b5217` (D1) + Plan 8/D1-followup commit + Plan 6 close commit

#### Plan 8 — Limitations Registry Expansion (2026-05-09 21:00 ET — closed)
Closes STANDARDS §4.4 row 2.
- [x] `2024-survey-columns-sparse.md` tightened from `affects: [requests]` (overfired on every requests-view query) to `affects: [accuracy, courtesy, ease, overallexperience]` (granular column names)
- [x] `location-ward-block-only.md` (warning, 2026-05-07; affects ward, block_code)
- [x] `survey-columns-on-fact.md` (info, 2026-05-07; affects accuracy, courtesy, ease, overallexperience — actual columns; brief had speculative names)
- [x] `dept-tags-as-booleans.md` (info, 2026-05-07; affects 8 boolean tag column names)
- [x] `bronze-varchar-source-cols.md` (info, 2026-05-07; affects bronze.raw_311_requests, main_bronze.raw_311_requests)
- [x] `open-status-not-just-open.md` (warning, 2026-05-07; affects open_requests — note: brief referenced is_open which doesn't exist in current schema, reframed around the open_requests measure semantics)
- [x] `open-requests-no-join-filter.md` (info, 2026-05-08; affects open_requests)
- [x] `current-year-partial.md` (warning, 2026-05-08; affects current_date sentinel)
- [x] `oxy-build-postgres-dependency.md` (info, 2026-05-08; affects deploy.oxy_build sentinel — does NOT auto-surface on analyst queries by design)
- [x] `scripts/build_limitations_index.py` reads `*.md` frontmatter (stdlib-only — no PyYAML dep); `docs/limitations/_index.yaml` generated with 10 active entries; `run.sh` step 9/9 wires it into the pipeline
- [x] Surfacing verified end-to-end via Plan 6 D3 test bench Q4 + Q5; STANDARDS §4.4 row 2 → [x]; session 18 file; LOG; commit

#### Plan 7 — MVP 1 Sign-off Sweep (2026-05-09 21:40 ET — closed)
Closed STANDARDS §5.8 last row; STANDARDS §6 walk landed 9/10 Foundations + 16/16 trust + 7/7 layers + 5/5 E2E smoke.
- [x] D1 — STANDARDS §6 walk: §3.2 (4/5 — systemd row open), §3.3 ✓, §4.5 (2/3 — repo-public row open), §5.1–5.8 all flipped with evidence (curl checks for /metrics, /docs, /trust live; dlt pipeline source URL + `4pyi-uqq6` + `replace` + `union_by_name=true` confirmed; bronze 25 descs + 1 unique + 3 not_null + 1 accepted_values; gold 51 descs + 4 unique + 7 not_null + 2 relationships + 1 accepted_values; semantic `oxy validate` 6/6 valid)
- [x] D2 — Portal copy refreshed and deployed: hero ("Somerville 311, queryable in plain English"; analyst-honest blurb stating SQL+row count+citations on every reply); stats (date range / source columns / documented limitations count); replaced /erd + /tasks asset cards (routes don't exist) with /trust + /metrics cards; "Built on Oxygen" prose detoxed to factual stack description; verified live via curl
- [x] D3 — Sign-off determination: 2 boxes still `[ ]`, both Gordon-decision-shaped (systemd-as-MVP1-requirement, repo-public). LOG.md Active Blockers section has the table. MVP 1 is **sign-off-ready pending these two decisions** — not auto-flipping.
- [x] D4 — Session file 19; LOG Plans Registry; commit `Plan 7 close`

#### Plan 5 D1 follow-on — Git pipe pattern coverage (2026-05-10 16:45 ET — closed)
Session 21. Root cause: `*` in allowlist patterns does not match `|`; piped git commands (`git log 2>&1 | head`) were prompting in unattended overnight sessions.
- [x] Root cause identified: `Bash(git *)` covers non-piped forms only — `|` is not matched by `*` in Claude Code patterns
- [x] Added `Bash(git * | *)` — single-pipe bare git forms (merge commit `997dc04`)
- [x] Added `Bash(git -C * * | *)` — single-pipe worktree-path forms (merge commit `997dc04`)
- [x] Added `Bash(git * | * | *)` — double-pipe fallback (merge commit `997dc04`)
- [x] Added `Bash(git rev-list *)` + `Bash(git -C * rev-list *)` — commit counting (merge commit `997dc04`)
- [x] Added `Bash(git ls-remote *)` + `Bash(git -C * ls-remote *)` — remote ref listing (merge commit `997dc04`)
- [x] Added `Bash(git branch *)` + `Bash(git -C * branch *)` — broad branch coverage (merge commit `997dc04`)
- [x] Removed duplicate `"Bash(bash *)"` entry from worktree `settings.json` (merge commit `997dc04`)
- [x] CLAUDE.md Allowlist policy + Bash Safety sections updated with pipe-coverage note (merge resolution)
- [x] Session 21 file, LOG.md, TASKS.md committed and pushed to `origin/claude/gifted-cartwright-9b6bac`

#### Plan 5 — Tech Debt Sweep (2026-05-10 09:55 ET — closed)
- [x] D1 — settings.local.json pruned to `{"permissions":{"allow":[]}}` (every pattern was redundant with tool-family allows in settings.json); added `Bash(bash *)` to settings.json so script invocations don't stall; CLAUDE.md "Allowlist policy" extended with "what belongs where" + periodic-prune subsection; commit `b274ae7`
- [x] D2 — `dbt/profiles.example.yml` shipped; SETUP.md §8 rewritten to reference cp+edit pattern; closes the machine-specificity gap noted in 2026-05-07 22:13 ET decision; commit `1f0d05d`
- [x] D3 — scratch/ hygiene check: only `plan6_test_bench/` exists (just-created in Session 18); no old runner files, no stale ad-hoc SQL; nothing to prune; commit `1f0d05d`
- [x] D4 — run.sh step-text consistency: already aligned in Session 18 when step 9 was added (1/9 through 9/9, plus 5b/9 sub-step); no drift to fix; verified via grep
- [x] D5 — doc reconciliation: CLAUDE.md Run Order section updated 7→9 steps (with 5b sub-step); ARCHITECTURE.md Run Order code block updated 7→9 steps with full bash-shape; ARCHITECTURE.md Portal routes table updated (/trust now Plan 4 done; /erd + /tasks marked deferred-from-MVP-1 + portal-card-removed); ARCHITECTURE.md "Process management" line corrected (Oxygen is nohup, not systemd — STANDARDS §3.2 row 4 open); TASKS.md "Deliverable B [~]" closed
- [x] D6 — Session 20 file; LOG.md updates; commit `Plan 5 close`; WAKE-UP BRIEF commit on top

#### Plan 9 rev 2 — Allowlist Coverage + Bash Safety Hook (2026-05-09 19:35 ET — closed)
- [x] Layer 0 audit: confirmed `defaultMode: acceptEdits`, bare `Read`/`Write`/`Edit`, `WebFetch(*)`, `Read(**/.env)` deny, `$schema` all intact from Plan 9 rev 1; no drift
- [x] Layer 1 allow merge: added `Bash(git *)` (bare) + `Bash(sudo ln *)` (broader); all rev 1 patterns preserved
- [x] Layer 1 deny merge: added `Read(~/.ssh/**)`, `Read(~/.gnupg/**)`, `Bash(launchctl *)`, `Bash(eval *)`, `Bash(curl * | bash*)`, `Bash(curl * | sh*)`, `Bash(wget * | bash*)`, `Bash(wget * | sh*)`
- [x] Layer 2 hook: `.claude/hooks/block-dangerous.sh` — blocks `&&`, `||`, naked `;`, `$(...)` (arithmetic `$((...))` exempt via `\$\([^(]` regex), `<()`, `>()`, leading `cd `, leading `export `; loop keywords carve-out via `sed -E 's/;[[:space:]]+(do|then|done|fi|else|elif)([[:space:]]|$)/ \1\2/g'` strip
- [x] Layer 2 wire: appended as second entry in `hooks.PreToolUse` (matcher Bash) — task-warning hook preserved
- [x] Layer 2 chmod: hook is executable (`-rwxr-xr-x`)
- [x] Layer 1 verify: `python3 -m json.tool .claude/settings.json` exits 0
- [x] Layer 3 CLAUDE.md: "Bash Safety" section landed between Rules and Naming Standards
- [x] Layer 4 audit: `scripts/check_allowlist_coverage.sh` rewritten — 11 idioms ran without prompting, 13/13 hook-deny/allow assertions passed
- [x] Session 17 file written ([docs/sessions/session-17-2026-05-09-plan-9-rev2-bash-safety-hook.md](docs/sessions/session-17-2026-05-09-plan-9-rev2-bash-safety-hook.md)); LOG.md Recent Sessions + Decisions updated; clean commit on `origin/main`

#### Plan 9 — Allowlist Coverage, Once and For All (2026-05-09 19:05 ET — closed)
- [x] Layer 0: structural audit + add `defaultMode: acceptEdits`, top-level `Read`/`Write`/`Edit`/`WebFetch(*)`, `autoMode.environment.allowNetwork: true`, `$schema`, `Read(**/.env)` deny  *(verified via `jq '.permissions.defaultMode, ."$schema", .autoMode.environment.allowNetwork'`)*
- [x] Layer 1: broaden allow patterns (verification idioms cohort) in `.claude/settings.json`  *(added wget/rsync/npm/pnpm/for/while/if/[/[[/cat/less/more/sed/cmp/yq/python3 -m json.tool/pwd/uptime/whoami; existing curl/jq/grep/head/tail/awk/find/stat already covered)*
- [x] Layer 1 verify: deny list intact; granular sudo allows preserved (no blanket `sudo *` deny); `python3 -m json.tool .claude/settings.json` exits 0  *(deny list 25 entries inc. new `Read(**/.env)`; granular sudo: nginx/systemctl/cp/mv/ln/chmod/chown/tail/cat/grep/sed-n still present)*
- [x] Layer 2: create `scripts/check_allowlist_coverage.sh` and run it clean (no prompts)  *(ran first pass clean — Code's running session picked up the new patterns mid-flight, no restart needed)*
- [x] Layer 3: CLAUDE.md — Allowlist `[x]` rule + general `[x]` evidence rule  *(under "LOG.md and Sessions Logging Protocol" section, after Transcript timestamps)*
- [x] Session file written; LOG.md Recent Sessions updated; Decisions logged; clean commit on `origin/main`  *(see commit hash in session note)*

#### Plan 0 — FR loose ends (2026-05-08 10:05 ET — closed)
- [x] Move `ANTHROPIC_API_KEY` and `OXY_DATABASE_URL` to `/etc/environment` (Option A — `~/.profile` empirically didn't reach non-interactive ssh)
- [x] Extend PATH in `/etc/environment` to include `/home/ubuntu/.local/bin` so `oxy`/`airlayer` resolve in plain ssh
- [x] Remove `export ANTHROPIC_API_KEY=...` line from `~/.bashrc`
- [x] Update [SETUP.md](SETUP.md) §7 (env vars) + §11 (systemd unit env vars + ExecStart path)
- [x] Update [CLAUDE.md](CLAUDE.md) "LLM Configuration" — current `model_ref`/`key_var` schema + two-var contract pointing at SETUP.md
- [x] Close `oxy build` deferred gate (Decisions Log + Blockers Log + MVP 1 caveat removed)
- [x] Flag `:3000` public exposure in Current Status — closes in Plan 1 (Tailscale)
- [x] Broaden `.claude/settings.json` + `settings.local.json` allowlist for `git -C * <write-op> *` and bare `git <write-op> *` patterns; deliberately omit `reset`, `push --force`, `branch`
- [x] Validation gate 1: `ssh oxygen-mvp 'echo $ANTHROPIC_API_KEY | head -c 14'` → `sk-ant-api03-E`
- [x] Validation gate 2: `ssh oxygen-mvp 'echo $OXY_DATABASE_URL'` → `postgresql://postgres:postgres@localhost:15432/oxy`
- [x] Validation gate 3: `ssh oxygen-mvp 'oxy build'` exit 0 (no `bash -ic`)
- [x] Validation gate 4: agent regression check — "How many 311 tickets were filed in 2024?" still returns 113,961

##### Plan 0 amendments — systemd Option (a) + Deliverable 7 allowlist restructure (2026-05-08 10:18 ET)
- [x] SETUP.md §11 systemd unit: Option (a) — `EnvironmentFile=/etc/environment` instead of explicit `Environment=` directives (single source of truth)
- [x] Capture pre-restructure allowlist state in LOG.md Decisions Log (settings.json: 112 allow / 66 git-related, settings.local.json: 51 allow, no deny)
- [x] D7a — `Edit(.claude/settings.local.json)` + `Write(.claude/settings.local.json)` auto-allowed (Code can self-amend)
- [x] D7b — tool-family wildcards: `Bash(git *)`, `Bash(git -C * *)`, `Bash(dbt *)`, `Bash(oxy *)`, `Bash(airlayer *)`, `Bash(python3 *)`, `Bash(duckdb *)`
- [x] D7b — removed redundant per-subcommand entries from settings.local.json (51 → 18 allow entries)
- [x] D7c — added `permissions.deny` array: `git reset`, `git push --force/-f`, `git branch -d/-D`, `rm -rf`, `sudo` (12 entries, both bare-`git` and `git -C`)
- [x] D7d — `python3 -m json.tool` validates both settings.json and settings.local.json
- [x] D7e — CLAUDE.md Rules: one-line allowlist policy referring to settings.local.json (auto) vs settings.json (Gordon-gated)
- [x] D7e — Decisions Log entry for the policy shift
- [ ] D7 validation: in next Code session, confirm a routine command (e.g. `git -C <worktree> commit`) proceeds without prompt; confirm a destructive command (e.g. `git reset --hard`) still prompts. Cannot validate in this session — Code reads allowlist at session start.

#### Tailscale (pulled forward from MVP 3) — Plan 1 in progress
- [x] Install Tailscale on EC2  *(2026-05-08, 1.96.4; `tailscale up --hostname=oxygen-mvp --ssh`; node IP 100.73.216.43; MagicDNS `oxygen-mvp.taildee698.ts.net` resolves)*
- [x] Authenticate Gordon's laptop and EC2 to same Tailnet  *(both visible in `tailscale status`: laptop 100.122.230.71, EC2 100.73.216.43)*
- [x] Repoint local `~/.ssh/config` `oxygen-mvp` alias from public IP → `oxygen-mvp.taildee698.ts.net`  *(2026-05-08; backup at `~/.ssh/config.bak.preTailscale`)*
- [x] Verify SSH works over Tailscale  *(D3 gate: `ssh oxygen-mvp 'echo ok'` → ok; verbose probe confirms `Authenticated to oxygen-mvp.taildee698.ts.net ([100.73.216.43]:22)`)*
- [x] Verify Oxygen :3000 reachable over Tailscale  *(curl from laptop: MagicDNS hostname → 200, Tailnet IP → 200; service bound to 0.0.0.0:3000)*
- [x] Update AWS security group: SSH and :3000 closed to public, port 80 stays open  *(2026-05-08, post-delete probes: Tailnet SSH ok, Tailnet :3000 = 200, public :3000 = curl timeout exit 28, public :80 = 200)*
- [ ] Update SETUP.md, CLAUDE.md, ARCHITECTURE.md to reflect new access pattern  *(also document nginx docroot = `/var/www/somerville` via `sites-enabled/somerville`, NOT `/var/www/html`)*
- [x] D4 — portal `/chat` link decision  *(2026-05-08; hybrid: dropped nav CTA + asset-card link, replaced hero CTA with non-link `Private beta` pill matching nav-badge styling; removed 3 stale `:3000` comments + dead `.nav-cta`/`.hero-cta` CSS; deployed to `/var/www/somerville/index.html`; live portal clean)*

#### dbt docs (production-strength documentation)
- [x] Audit all schema.yml files: every model has description, every column has description (no nulls)  *(2026-05-08 D1)*
- [x] Add bronze model + column descriptions  *(1/1 model + 24/24 cols)*
- [x] Add gold model + column descriptions  *(4/4 models + 47/47 cols)*
- [x] Add admin model + column descriptions  *(D2 — 3/3 models + all cols)*
- [x] Add `dbt docs generate` step to run.sh  *(step 6/7)*
- [x] Configure nginx /docs route to serve dbt/target/  *(alias fixed: dbt 1.11 emits index.html directly to dbt/target/, not a subdir; /home/ubuntu chmod 755 for www-data traversal)*
- [x] Verify /docs renders on portal  *(`curl http://18.224.151.49/docs/index.html` → 200, title "dbt Docs")*

#### Portal pages for trust
- [x] Build /metrics page generator (auto-generated from Airlayer YAML — every measure with definition and expanded SQL)  *(2026-05-08 D3 — `scripts/generate_metrics_page.py`; live at `/metrics`; 2 measures across 4 views)*
- [x] Build /trust page (driven by admin.fct_test_run — last run, pass/fail counts, test details, data freshness)  *(Plan 4 — `scripts/generate_trust_page.py`; live at `/trust`; 36 tests on the latest run; synthetic-fail render check verified green→red→green on 2026-05-09)*
- [x] Update portal/index.html nav: surface /docs, /metrics, /trust alongside /chat  *(Plan 4 — three route links added to `.nav-links`; chat handled via existing hero "Private beta" pill per Session 11/12 decision)*
- [ ] Update portal/index.html copy to reflect analyst persona (engineering-honest, not marketing)  *(Plan 7)*

#### Limitations registry
- [x] Decide location and format (open question in STANDARDS.md)  *(2026-05-08 D0 — Option b: `docs/limitations/` Markdown + YAML frontmatter)*
- [x] Document known 311 data limitations  *(Plan 8 — 10 active entries; index at `docs/limitations/_index.yaml` generated by `scripts/build_limitations_index.py` as run.sh step 9/9)*
- [ ] Surface limitations on /trust page  *(Plan 7 — `/trust` page is admin-DQ-driven today; surfacing limitations is a separate UI pass)*
- [x] Configure Answer Agent to reference limitations when relevant  *(Plan 6 D2 — agent reads `_index.yaml`, matches affects against SQL/cited views, surfaces matches in Citations + Known limitations sections; verified Q4+Q5 of D3 test bench)*

### Documentation — MVP 1 scope sharpening
- [x] Deliverable A: STANDARDS.md written, committed, pushed
- [x] Deliverable B: TASKS.md updates (scope statement, Hardening section, Answer Agent + Sign-off updates, marks done)  *(Plans 6/7/8/5 closed via the rev 2 batch — all relevant rows reconciled)*
- [ ] Deliverable C: LOG.md session entry + Decisions Log + Current Status

### Environment Setup
- [x] Provision EC2 instance (t4g.medium, Ubuntu 24.04 LTS ARM) — IP: 18.224.151.49
- [x] SSH in and install Docker (29.4.3)
- [x] Install Oxygen (0.5.47)
- [x] Install Python 3.12 and create virtual environment
- [x] Install Python packages: `dlt[duckdb]` 1.26.0, `dbt-core` 1.11.9, `dbt-duckdb` 1.10.1
- [x] Initialize GitHub repo and push all project files
- [x] Clone project repo and create `data/` directory
- [x] Set `ANTHROPIC_API_KEY` environment variable
- [x] Configure EC2 to pull from GitHub repo on each session  *(addressed by `CLAUDE.md` "Session Start on EC2" section per Session 5 follow-up)*
- [x] Configure dbt profile (`~/.dbt/profiles.yml`)
- [x] Create `config.yml` for Oxygen (model + database config) — landed in overnight session
- [x] Run `oxy start` and confirm UI loads at port 3000  *(2026-05-08 09:30 ET — Postgres container up, web app on :3000 returns 200, `oxy build` exits 0)*
- [ ] Persist `OXY_DATABASE_URL=postgresql://postgres:postgres@localhost:15432/oxy` so `oxy build` works in any shell  *(2026-05-08 09:32 ET — `oxy start` creates the container but doesn't export the URL; Session 7 worked around it inline. Add to `~/.bashrc` or have `run.sh` source it from `oxy status` output.)*
- [ ] Move `ANTHROPIC_API_KEY` and `~/.local/bin` (oxy, airlayer) exports out of `~/.bashrc` into `~/.profile` (or a sourced env file)  *(2026-05-08 09:32 ET — Ubuntu's default `.bashrc` early-returns for non-interactive shells, so plain `ssh oxygen-mvp 'cmd'` doesn't see the key or the binaries; Session 7 worked around with `bash -ic`. Fix at the source.)*

### Ingestion (dlt)
- [x] Identify Somerville 311 dataset ID on data.somervillema.gov — `4pyi-uqq6`, 1.17M rows, 22 columns
- [x] Profile API: confirmed access, volume per year, classification breakdown, date format
- [x] Write `dlt/somerville_311_pipeline.py` — filesystem destination, Parquet partitioned by year, replace disposition
- [x] Run pipeline and confirm Parquet files land in `~/oxygen-mvp/data/raw/`
- [x] Verify row count — 1,168,959 of 1,168,959 loaded

### Data Profiling & Quality (dbt — admin schema)
- [x] Query raw Parquet files on EC2 and extract full column list with types and sample values  *(via `information_schema.columns` Jinja introspection in fct_data_profile.sql)*
- [x] Create `admin` schema in `dbt_project.yml`  *(already present from Session 5; admin models populate it)*
- [x] Write `admin/fct_data_profile.sql` — column-level profiling, observational only
- [x] Write `admin/dim_data_quality_test.sql` — one row per defined test
- [x] Write `admin/fct_test_run.sql` — one row per test per run, sourced from `raw_dbt_results_raw`  *(landing table; no dbt-managed bronze view — design departure documented in session 13)*
- [x] Write `dlt/load_dbt_results.py` — loads `dbt/target/run_results.json` into `main_bronze.raw_dbt_results_raw` in DuckDB  *(plain duckdb, not dlt — simpler, no metadata-column pollution)*
- [x] Write `run.sh` — single entry point, correct run order, captures dbt test exit code without halting
- [x] Auto-generate baselines on first run — `certified_by = 'system'`  *(17 baselines: 12 yearly + 5 totals; is_incremental filter freezes them)*
- [x] Confirm baseline comparisons fail dbt run on drift beyond tolerance  *(2026-05-09 Plan 3 D3 — synthetic 30% perturbation on 2015 row count baseline; `dq_drift_fail_guardrail` singular test fired; final exit 1; baseline restored; arc preserved in `fct_test_run`)*

### Transformation (dbt — bronze schema)
- [x] Initialize dbt project (`dbt init`) in `dbt/` directory
- [x] Configure `dbt_project.yml` with all four schemas: bronze, silver, gold, admin
- [x] Configure `~/.dbt/profiles.yml` on EC2
- [x] Write `bronze/raw_311_requests.sql` — exact mirror, columns derived from actual Parquet data
- [x] Run `dbt run --select bronze` and confirm model builds
- [x] Run `dbt test --select bronze` — arrival checks only

### Transformation (dbt — gold schema)
- [x] Write `gold/dim_date.sql` — standard date spine
- [x] Write `gold/dim_request_type.sql` — sourced from actual column values
- [x] Write `gold/dim_status.sql` — sourced from actual column values
- [ ] Write `gold/dim_origin.sql` — sourced from actual column values  *(deferred — not in overnight scope)*
- [x] Write `gold/fct_311_requests.sql` — location fields denormalized, no `dim_location` yet
- [x] Run `dbt run --select gold` and confirm all models build
- [x] Add dbt tests: unique + not_null on all surrogate keys
- [x] Add dbt tests: accepted_values on status  *(classification/origin: deferred, surface in semantic layer instead)*

### Docs
- [x] Create `docs/schema.sql` — DDL source of truth (already written, needs committing)

### Portal
- [x] Install nginx on EC2
- [x] Deploy portal index.html at port 80 — verified live at http://18.224.151.49
- [x] Fix portal "Open Chat →" link — Plan 0.5 closed 2026-05-08 11:48 ET (3 hrefs repointed to `http://18.224.151.49:3000/`, nginx `location /chat` block removed; gates 1-4 green; gate 5 = Gordon's browser test)
- [ ] Add /tasks route — rendered TASKS.md
- [x] Add /erd route — ERD SVG from schema.sql *(closed by Plan 1b Phase 5, Session 30, commit `0a0a065` — shipped as Mermaid `erDiagram` from dbt `schema.yml` relationships tests rather than SVG from `schema.sql`; live at /erd. Plan B (2026-05-14) reconciled this row after investigation found the original framing was stale.)*
- [x] Add /docs route — dbt docs generate output *(closed by Plan 2 D1, Session 13 — dbt docs served at /docs/ via nginx alias; Plan A (2026-05-14) added `dbt/models/overview.md` orientation prose.)*

### Semantic Layer (Airlayer)
- [x] Review Airlayer docs (incl. https://github.com/oxy-hq/airlayer/blob/main/docs/schema-format.md)
- [x] Create `semantics/views/*.view.yml` + `semantics/topics/service_requests.topic.yml` (replaces old single-file `.sem.yml`)
- [x] Define initial views and dimensions (request type, status, opened date, ward, block_code)
- [x] Define initial measures (`total_requests`, `open_requests`)
- [ ] Define `avg days open` measure  *(deferred — needs `most_recent_status_date - date_created_dt` math, MVP 4 metric library)*
- [x] Airlayer schema valid (`airlayer validate` clean) and executes via auto-join (`airlayer query -x` returned 5 rows)
- [x] Confirm Airlayer loads without errors in Oxygen — `oxy validate` clean ("All 5 config files are valid"); `oxy build` deferred to Answer Agent session

### Answer Agent
- [x] Review Answer Agent docs: https://oxy.tech/docs/guide/learn-about-oxy/agents.md
- [x] Create `agents/answer_agent.agent.yml`
- [x] Configure `execute_sql` tool and Airlayer context block
- [x] Configure agent prompt to require SQL, row count, and citations in every response  *(Plan 6 D1 — STANDARDS §4.1; verified across 5/5 test bench)*
- [x] Test with 3–5 sample questions in Oxygen chat UI  *(2026-05-08 09:31 ET — FR smoke test: Test A 2024 = 113,961 ✓ exact match, Test B 2026 "this year" = 48,806 ✓ exact match, agent correctly resolved current year via `year(current_date)`)*
- [x] Confirm agent returns accurate answers  *(both smoke tests exact-match DuckDB ground truth)*
- [x] Test bench: 5 representative analyst questions, verify responses include SQL + row count + citation in every reply  *(Plan 6 D3 — 5/5 trust contract; transcripts in `scratch/plan6_test_bench/q[1-5]_*.md`)*

### MVP 1 Sign-off
- [ ] All checks in [STANDARDS.md](STANDARDS.md) MVP 1 sign-off checklist pass
- [ ] Analyst can ask "How many 311 requests opened in 2024?" and get an answer with SQL, row count, and citation
- [ ] Analyst can ask "Most common request types?" and get an answer with SQL, row count, and citation
- [ ] /trust page shows green for last pipeline run
- [ ] /metrics page lists all current measures with definitions
- [ ] /docs page renders dbt documentation with no missing descriptions

---

## MVP 2 — Visual Knowledge Products
**Goal:** The analyst describes a dashboard in chat; Builder Agent assembles it. Iterates by conversation, not by writing YAML.

- [ ] Review Airapp docs: https://oxy.tech/docs/guide/learn-about-oxy/data-apps.md
- [ ] Create `apps/somerville_dashboard.app.yml`
- [ ] Add chart: requests by type (bar)
- [ ] Add chart: requests over time (line)
- [ ] Add metric: total open requests
- [ ] Confirm agent can trigger dashboard components from chat
- [ ] MVP 2 sign-off: agent generates a chart in response to a chart request

---

## MVP 3 — Governance and Trust
**Goal:** The analyst trusts the underlying data without having to verify it themselves. Verified Queries badges, full medallion architecture, native agent testing.

- [ ] Write Silver model: `models/silver/stg_311_requests.sql`
  - [ ] Normalize field names
  - [ ] Cast types
  - [ ] Deduplicate
  - [ ] Redact PII fields (names, contact info)
- [ ] Promote location to `gold/dim_location.sql`
- [ ] Add dbt tests: unique keys and non-null checks on Silver
- [ ] Add dbt tests: business rule validation on Gold
- [ ] Update Airlayer to point to Gold layer
- [ ] Add Tailscale for access control (replacing open port 3000)
- [ ] MVP 3 sign-off: `dbt test` passes clean, PII confirmed redacted

---

## MVP 4 — Semantic Depth and Sharing
**Goal:** The analyst's findings move from personal to shared via Slack, MCP, A2A, BI tools, and public chat.

- [ ] Audit existing Airlayer metrics — identify gaps
- [ ] Expand `somerville_311.sem.yml` with full metric library
  - [ ] Response time metrics (avg days to close, SLA compliance)
  - [ ] Geographic dimensions (ward, neighborhood)
  - [ ] Department/category breakdowns
  - [ ] Year-over-year comparisons
- [ ] Review Routing Agent docs: https://oxy.tech/docs/guide/learn-about-oxy/routing-agents.md
- [ ] Create `agents/routing_agent.agent.yml` (`type: routing`)
- [ ] Configure routing to dispatch to answer agent
- [ ] Test routing with ambiguous queries
- [ ] MVP 4 sign-off: routing agent correctly dispatches 5 varied test queries
