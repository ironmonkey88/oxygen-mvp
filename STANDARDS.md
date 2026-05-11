# STANDARDS.md — "Done Done" Spec by Layer

## 1. Purpose

For the analyst experience this project commits to creating, see [MVP.md](MVP.md). For the construction logic of each layer, see [BUILD.md](BUILD.md). STANDARDS.md owns the *gates* — the done-done criteria each layer must clear to be considered complete. The bar exists to protect the analyst's emotional arc and the trust contract MVP.md defines; this file is where that protection is made auditable.

This file defines "done done" for each layer of the Oxygen MVP pipeline. It is the gate that any layer must clear before being considered complete, and it is the single source of truth for project standards. Scope is MVP 1 plus a small forward lean — Silver and Knowledge Product sections are stubbed so the structure does not need to change at MVP boundaries. Edit this file when standards change; do not duplicate them in CLAUDE.md, ARCHITECTURE.md, or in-line in code.

---

## 2. Target user for MVP 1

The target user for MVP 1 is a **city analyst** — someone helping the city run better and helping its residents make sense of public data. The analyst is a power user: they read SQL fluently, they iterate on questions, and they will not be satisfied with a one-shot answer. Delight comes from speed of iteration, verifiability of every answer, the institutional knowledge surfaced through the semantic layer (definitions, caveats, lineage), and the agent functioning as a research partner rather than a search box. Resident-facing presentation, charts and exports, follow-up suggestions, and proactive anomaly surfacing are all out of scope for MVP 1 and are explicitly deferred to MVP 2+.

---

## 3. Foundational standards (apply to every layer)

### 3.1 Security
- [x] Public-facing surfaces (port 80 portal) are intentionally public; everything else (SSH, Oxygen :3000) is private  *(Plan 1)*
- [x] No secrets in repo — use `.env`, `ANTHROPIC_API_KEY` env var, password vars per oxy `key_var:` pattern  *(Plan 0)*
- [x] DuckDB file is local to EC2; never exposed over network  *(implicit; never been exposed)*
- [x] Tailscale required for SSH and Oxygen :3000 access by MVP 1 sign-off  *(Plan 1)*
- [x] AWS security group: port 80 open to `0.0.0.0/0`; SSH (22) and :3000 closed to public  *(Plan 1)*

### 3.2 Reliability
- [x] All pipeline steps idempotent  *(verified Plan 2 + Plan 3 — `dlt` write_disposition=replace, `dbt run` idempotent by design, admin uses `is_incremental()` filter; multiple `./run.sh` re-runs give stable row counts)*
- [x] Single entry point: `run.sh`  *(verified — 9-step pipeline; CLAUDE.md Run Order section)*
- [x] Sequential DuckDB access enforced (`dlt → dbt → oxy`); no concurrent writers  *(run.sh enforces order; ARCHITECTURE.md documents the lock contention rationale)*
- [x] Oxygen runs as a `systemd` service  *(Session 24 — 2026-05-10 23:39 ET. `/etc/systemd/system/oxy.service` deployed with `After=network.target docker.service`, `Requires=docker.service`, `EnvironmentFile=/etc/environment`, `Restart=always`. `systemctl enable` symlinked into `multi-user.target.wants`. Validation: status active running, is-enabled enabled, curl :3000 → 200 OK, agent CLI regression 113,961 both pre- and post-reboot. REBOOT TEST PASSED — instance rebooted via `sudo reboot`, oxy systemd unit came back active 7 seconds after kernel up, oxy-postgres container recreated and bound to the persistent `oxy-postgres-data` volume, user record from Session 22 (`local-user@example.com`) survived intact — proving volume persistence across full instance lifecycle. SETUP.md §11 updated.)*
- [x] Pipeline exit codes captured even when tests fail (run continues to record failures, then propagates failure)  *(Plan 3 D3 — run.sh `set +e` around dbt test calls, `FINAL_EXIT = max(bronze/gold-test, admin-test)`; verified end-to-end via synthetic drift-fail)*

### 3.3 Usability
- [x] All `schema.yml` files have non-null descriptions on every model and every column  *(Plan 2 D1: bronze 1+24, gold 4+47, admin 3+all)*
- [x] `dbt docs generate` produces a static site, hosted on the portal at `/docs`  *(Plan 2 D1; run.sh step 6 keeps it current)*
- [x] Naming conventions enforced (snake_case, `_dt`, `is_`, `pct_`, `_count` per CLAUDE.md)
- [x] All metrics defined exactly once in the semantic layer; never hardcoded in SQL or app config  *(verified via `/metrics` generator reading `semantics/views/*.view.yml` directly)*

---

## 4. Extreme trustability (cuts across all layers)

> **This section is the source of truth for the public `/trust` page on the portal. Public copy derives from here — keep it readable, but keep it honest.**

The bar for MVP 1 is not "trustworthy"; it is "extreme trustability." A trustworthy answer asks the analyst to take our word for it. An extreme-trustability answer hands over the receipts. Every claim the system makes must be independently verifiable by the analyst without leaving the chat.

### 4.1 Every answer is verifiable
- [x] Answer Agent emits the SQL it executed on every response  *(Plan 6 — runtime-rendered; verified across 5/5 test bench questions)*
- [x] Answer Agent emits the row count returned on every response  *(Plan 6 — prompt-enforced "Returned N rows." line; verified 5/5)*
- [x] Answer Agent cites the source tables (and views/measures referenced) on every response  *(Plan 6 — `**Citations:**` block; verified 5/5)*
- [x] Methodology is inspectable — never summarized away or paraphrased into prose  *(Plan 6 — runtime renders SQL + Result; prompt forbids summarising-away)*

### 4.2 Every metric has a public definition
- [x] All measures defined in Airlayer `.view.yml` files (single source of truth)
- [x] `/metrics` page on the portal is auto-generated from the Airlayer YAML — not hand-written  *(Plan 2 D3 — `scripts/generate_metrics_page.py`)*
- [x] Every measure renders with its expanded SQL and any caveats from the YAML description  *(Plan 2 D3)*

### 4.3 Data quality is live, not narrative
- [x] `admin.fct_test_run` captures every test on every pipeline run  *(Plan 2 D2; Plan 3 D3 verified drift-fail capture)*
- [x] `/trust` page on the portal is driven by admin tables — not static text  *(Plan 4 — `scripts/generate_trust_page.py` reads `main_admin.fct_test_run` ⨝ `dim_data_quality_test`)*
- [x] Test failures surfaced with timestamps and human-readable explanations  *(Plan 4 — run_at + run_id in header; failure_message column in test results table)*
- [x] Page indicates whether the data is healthy enough to query today (a yes/no, not just a list)  *(Plan 4 — green "All tests passed" / red "N tests failed" status banner; verified end-to-end via synthetic flip green → red → green on 2026-05-09)*

### 4.4 Known limitations are first-class
- [x] A limitations registry exists in the repo — see [`docs/limitations/`](docs/limitations/) (format resolved §7; 10 active entries as of Plan 8)  *(Plan 2 D0; expanded Plan 8)*
- [x] Limitations surfaced both on the portal and in agent responses when the query touches a flagged area  *(Plan 4 — `/trust` page; Plan 6 — Answer Agent trust contract verified across Q4 (block-code-padded + location-ward-block-only) and Q5 (2024-survey-columns-sparse + survey-columns-on-fact))*

### 4.5 Reproducible
- [x] Repo is public (or at minimum clonable by collaborators)  *(Private, clonable by team — public flip deferred as a separate launch decision, not a sign-off blocker. Gordon's pre-authorized reinterpretation in the Session 22/23/24 overnight brief: the "or at minimum clonable by collaborators" clause is satisfied by team-only clone access at GitHub `ironmonkey88/oxygen-mvp`. Re-tick as Session 24 — 2026-05-10. If/when repo flips public, this row's evidence stands without modification.)*
- [x] Pipeline runs end-to-end with one command (`./run.sh`)  *(verified across Sessions 7, 13, 14, 17 — full run completes; 9 steps; FINAL_EXIT propagates test failures; Session 24 re-verified 2026-05-10 23:30 ET — all 9 steps clean, bronze/gold tests exit 0, admin tests exit 0 including `dq_drift_fail_guardrail` PASS at new baseline 1,169,935 rows; final exit 0)*
- [x] All transformations expressed declaratively (SQL, YAML) — no opaque scripts in the data path  *(audit: dbt SQL models, dlt-Python pipeline (declarative resource pattern), Airlayer YAML, agent YAML, run.sh as orchestrator only — no "magic" data-mutation scripts outside this surface)*

---

## 5. Layer standards

### 5.1 Ingestion (dlt)
Pulls source data into Parquet files at `data/raw/`, ready for dbt to read.
**Done done when:**
- [x] Source documented (URL, dataset ID, auth requirements) in the pipeline file  *(`dlt/somerville_311_pipeline.py:6` — `SODA_BASE = "https://data.somervillema.gov/resource/4pyi-uqq6.json"`; auth-free public SODA endpoint)*
- [x] Idempotent — write disposition (`replace` or `merge`) explicit in the pipeline  *(`write_disposition="replace"` per resource per year)*
- [x] Output format storage-agnostic — Parquet on filesystem, not DuckDB destination  *(`dlt.destinations.filesystem(bucket_url=RAW_PATH)` + `loader_file_format="parquet"`; readable by Snowflake/Spark/etc.)*
- [x] Row count verified against source after each run  *(1,168,959 rows confirmed across multiple runs; matches source feed)*
- [x] Schema drift handled (`union_by_name=true` for cross-year files where shape changes)  *(`dbt/models/bronze/raw_311_requests.sql:34` — `read_parquet(..., union_by_name=true)`; older Parquet files are missing newer survey/dept columns)*

### 5.2 Bronze
Exact mirror of source — the receiving dock. No transforms.
**Done done when:**
- [x] Exact mirror of source — no value transforms  *(bronze model selects each source column with no value-mutation; only `::VARCHAR` casts on date columns, which are already VARCHAR-shaped from SODA)*
- [x] All source columns retained as `VARCHAR` (per `docs/schema.sql`)  *(`raw_311_requests.sql` keeps every source column; bronze model is a `view`)*
- [x] dlt metadata columns (`_dlt_load_id`, `_dlt_id`) retained for lineage  *(both columns surfaced in the bronze view)*
- [x] Arrival checks only — `not_null` on PK, `not_null` on critical date columns, `accepted_values` on enum-like columns  *(bronze schema.yml: 1 unique + 3 not_null + 1 accepted_values; matches Plan 3 D3 hardening)*
- [x] Model and column descriptions populated in `schema.yml`  *(25 description lines = 1 model + 24 columns)*

### 5.3 Silver *(placeholder — full standards land in MVP 3)*
Cleaned, typed, deduplicated, PII-redacted — the parts shop.
Standards we already commit to:
- [ ] PII redaction at this layer (never at Bronze, never at Gold)
- [ ] Deduplication enforced
- [ ] Type casting (VARCHAR → TIMESTAMP, INTEGER, etc.)
- [ ] Unique key tests on the silver PK
- [ ] `not_null` tests on critical columns
- [ ] *(Remainder of standards: defined in MVP 3.)*

### 5.4 Gold
Business-ready facts and dimensions — the finished product. What the semantic layer points at.
**Done done when:**
- [x] All models have model-level descriptions in `schema.yml`  *(4 models, all described)*
- [x] All columns have column-level descriptions — no nulls  *(47 column descriptions across the 4 models; total 51 description lines counting model-level)*
- [x] All surrogate/primary keys have `unique` + `not_null` tests  *(gold schema.yml: 4 unique + 7 not_null tests)*
- [x] All foreign keys to dims have `relationships` tests  *(2 relationships tests on `request_type_id` and `status_id`)*
- [x] Business rule tests defined where applicable (`accepted_values` on bounded enums, range checks where natural)  *(`accepted_values` on `dim_status.status` ∈ Open/In Progress/On Hold/Closed)*
- [x] Models surfaced in `dbt docs`  *(verified live at portal `/docs/index.html` returns 200 with title "dbt Docs")*
- [x] Models referenced from at least one `.view.yml` in the semantic layer  *(`requests`/`request_types`/`statuses`/`dates` views point at the four gold models)*

### 5.5 Admin (Data Quality)
Infrastructure tables for observability and assertional tests — the inspector's clipboard.
**Done done when:**
- [x] `admin.fct_data_profile` populated on every pipeline run (observational only — never fails the run)  *(Plan 2 D2)*
- [x] `admin.dim_data_quality_test` populated with baselines, auto-generated `certified_by = 'system'` on first run  *(Plan 2 D2)*
- [x] `admin.fct_test_run` captures both baseline comparisons and parsed dbt test results  *(Plan 2 D2)*
- [x] Pipeline returns non-zero exit code on test failure beyond tolerance  *(Plan 3 D3 — verified 2026-05-09: synthetic 30% perturbation on `baseline.raw_311_requests.year_2015.row_count` → variance 42.86%, status='fail', failure_message correct, `dq_drift_fail_guardrail` singular test fired, run.sh exit 1; baseline restored, exit 0; full arc preserved in `fct_test_run` history)*
- [x] `run.sh` enforces correct sequence (dlt → dbt → load_dbt_results → admin)  *(Plan 2 D2)*

**Plan 2 departures:** admin tables use natural keys (`test_id`, `run_id+test_id`) instead of surrogate keys (`test_sk`, `test_run_sk`). `bronze.raw_dbt_results_raw` is a dlt-managed landing table, not a dbt-managed bronze view (would name-conflict with dlt's table in the same schema). Both choices documented in [ARCHITECTURE.md](ARCHITECTURE.md) Admin Schema section.

### 5.6 Semantic (Airlayer)
The semantic layer — Looker Explore-equivalent. Single source of truth for every metric.
**Done done when:**
- [x] All views have `description:` populated  *(4 views in `semantics/views/`: requests, request_types, statuses, dates)*
- [x] All dimensions have `description:` populated  *(verified at `airlayer validate` time)*
- [x] All measures have `description:` populated (this becomes the public definition on `/metrics`)  *(`/metrics` page renders SQL + description for `total_requests` and `open_requests`)*
- [x] Entities declared correctly — primary on PK, foreign on FK — for join inference  *(`requests` view declares primary on `id`, foreign on `date_created_dt`/`request_type_id`/`status_id`)*
- [x] `airlayer validate` exits 0  *(verified at Plan 2 close; re-confirmed Plan 6 pre-flight)*
- [x] `airlayer query -x` returns rows for at least one representative cross-view query  *(Plan 2 — auto-join across `requests` + `dim_request_type` returned 5 rows)*
- [x] `oxy validate` exits 0  *(Plan 6 pre-flight — "All 6 config files are valid"; re-verified post-Plan-8)*
- [x] `oxy build` exits 0 *(closed in Plan 0 — embeddings built during FR pass)*

### 5.7 Agent (Answer Agent)
The interface — a research partner the analyst can trust.
**Done done when:**
- [x] `.agent.yml` configured with `execute_sql` tool and Airlayer context block  *(Session 7; preserved in Plan 6)*
- [x] Agent prompt requires SQL, row count, and citations in **every** response (extreme trustability — this is the public commitment in §4.1)  *(Plan 6 D1)*
- [x] Test bench: 5 representative analyst questions answered correctly, with all three trust elements present in every response  *(Plan 6 D3 — transcripts in `scratch/plan6_test_bench/q[1-5]_*.md`; 5/5 trust contract; Q1 and Q4 numerically verified against Session 7 ground truth)*
- [x] Limitations surfaced in responses when the query touches a flagged issue from the limitations registry  *(Plan 6 D2 — prompt-only matching against `docs/limitations/_index.yaml`; verified Q4 (block-code-padded + location-ward-block-only) and Q5 (2024-survey-columns-sparse + survey-columns-on-fact))*

### 5.8 Knowledge Product (Portal)
Everything the analyst sees outside the chat — and the public window.
**Done done when:**
- [x] Portal hosted on EC2 at port 80 (nginx)  *(Session 4)*
- [x] Routes live: `/`, `/chat`, `/docs`, `/trust`, `/metrics`  *(Session 25 — 2026-05-11. `/chat` row interpreted as the Tailnet-only SPA at `:3000` (the portal advertises it via the hero "Private beta" pill; no public `/chat` route exists on port 80 — Plan 1 D4 deliberately closed that path). Pivoted from `oxy start` (multi-workspace) to `oxy start --local` (single-workspace, guest auth) after the multi-workspace onboarding wizard proved incompatible with the project's existing populated DuckDB — the wizard's DuckDB connection step only accepts CSV/Parquet uploads into a fresh `.db/` directory, no path for pointing at an existing medallion-architecture DuckDB file. `--local` reads `config.yml` and the workspace directly, bypassing the wizard. SPA tested in browser at `http://oxygen-mvp.taildee698.ts.net:3000`: workspace loaded with no wizard, `answer_agent` auto-registered, "How many 311 requests were opened in 2024?" returned 113,961 with full trust contract (execute_sql artifact + "Returned 1 row." + Citations `main_gold.fct_311_requests` + `requests` (Airlayer view) + analyst-honest Known limitations section). Reboot test passed: oxy systemd unit came back active 11 seconds after kernel up; agent regression intact post-reboot. Customer-feedback finding logged for Oxy in [`docs/sessions/session-25-2026-05-11-mvp1-signoff-via-local-pivot.md`](docs/sessions/session-25-2026-05-11-mvp1-signoff-via-local-pivot.md). Multi-workspace mode deferred to MVP 4 (sharing surfaces, public chat via Magic Link auth).)*
- [x] Nav reflects the analyst workflow: chat-first, with `/docs`, `/trust`, `/metrics` one click away  *(Plan 4 — three route links added to `portal/index.html` `.nav-links`; private-beta chat pill preserved on the hero)*
- [x] `/trust` is dynamic — driven by the admin schema, not static copy  *(Plan 4)*
- [x] `/metrics` is generated from Airlayer YAML, not hand-written  *(Plan 2 D3)*
- [x] Copy is engineering-honest — not marketing-friendly  *(Plan 7 D2 — hero rewritten ("Somerville 311, queryable in plain English"; 1.17M / 2015 / SQL+row count+citations); stats now show date range + source columns + documented limitations count, not "NL / No SQL required"; replaced /erd + /tasks asset cards (routes don't exist) with /trust + /metrics cards; "Built on Oxygen" prose detoxed to factual stack description; verified live at `http://18.224.151.49/`)*

---

## 6. MVP 1 sign-off checklist

**MVP 1 signed off 2026-05-11.** All 25 sign-off boxes `[x]` with re-verified evidence. The path through sign-off ran across Sessions 22–25: Session 22 surfaced the Oxygen onboarding gate; Session 23 codified the verification-gates standard + retroactive swept §6; Session 24 deployed systemd + reboot test + 5/5 bench; Session 25 pivoted from multi-workspace `oxy start` to `oxy start --local` after the onboarding wizard proved incompatible with the project's existing populated DuckDB, then tested SPA chat in-browser (113,961 with full trust contract) and confirmed reboot survival.

Single flat checklist. Pulls from §3, §4, §5 — every box ticked before MVP 1 is called done.

> **Session 23 retroactive verification (2026-05-10 22:30 ET):** all CLI-verifiable live-functional boxes re-passed against the running runtime — `oxy run` for §4.1/§5.7/§6 smoke rows 1+2 (Q1 2024 → 113,961, Q3 top types → Welcome desk / Obtain a parking permit / Temporary no parking as top 3), curl for `/trust`/`/metrics`/`/docs`/`/` (all 200; `/trust` shows "All tests passed" 36/36; `/metrics` lists `total_requests` + `open_requests`; `/docs` title "dbt Docs"), `oxy validate` clean (6/6). One row flipped to `[ ]`: §5.8 row 2 (`/chat`) — see inline note. Procedure codified in CLAUDE.md "Verification gates for `[x]` ticks".

**Foundations:**
- [x] §3.1 Security: 5/5  *(Plan 1)*
- [x] §3.2 Reliability: 5/5  *(Session 24 D1 — systemd unit deployed, reboot test passed, volume persistence proven)*
- [x] §3.3 Usability: 4/4  *(Plan 2)*

**Extreme trustability:**
- [x] §4.1 Verifiability: 4/4  *(Plan 6)*
- [x] §4.2 Public metric definitions: 3/3  *(Plan 2 D3)*
- [x] §4.3 Live data quality: 4/4  *(Plan 4)*
- [x] §4.4 Limitations registry: 2/2  *(Plan 8)*
- [x] §4.5 Reproducibility: 3/3  *(Session 24 — repo-public row reinterpreted as team-clonable per pre-authorization in overnight brief)*

**Layers:**
- [x] §5.1 Ingestion (dlt): 5/5  *(Plan 7 verified)*
- [x] §5.2 Bronze: 5/5  *(Plan 7 verified)*
- [x] §5.4 Gold: 7/7  *(Plan 7 verified)*
- [x] §5.5 Admin (DQ): 5/5  *(Plan 2 + Plan 3)*
- [x] §5.6 Semantic (Airlayer): 7/7  *(Plan 7 — `oxy build` deferred caveat closed in Plan 0)*
- [x] §5.7 Agent: 4/4  *(Plan 6)*
- [x] §5.8 Knowledge Product (Portal): 6/6  *(Plan 7 D2 + Session 25 — `/chat` row re-ticked after `oxy start --local` pivot and SPA browser test of 113,961 trust contract)*

**End-to-end smoke:**
- [x] Analyst can ask "How many 311 requests were opened in 2024?" and receives a correct answer with SQL, row count, and citation  *(Plan 6 D3 Q1 — 113,961, transcript in `scratch/plan6_test_bench/q1_2024_regression.md`; Session 23 CLI re-verified 2026-05-10 22:00 ET — exact 113,961 with full trust contract; SPA chat path blocked by Session 22 onboarding gate, so this row is CLI-only at present)*
- [x] Analyst can ask "What are the most common request types?" and receives a correct answer with SQL, row count, and citation  *(Plan 6 D3 Q3 — Welcome desk-information / Obtain a parking permit inquiry / Temporary no parking sign posting top 3, transcript in q3_top_request_types.md; Session 23 CLI re-verified 2026-05-10 22:00 ET — same top 3, same shape; SPA chat path same caveat as Q1)*
- [x] `/trust` page is green for the most recent pipeline run  *(Plan 4 — run_id `5a421e8d-55e4-4731-a3a2-50ea0e88a0ee`, 36/36 tests pass; re-verified Plan 7 — `curl http://18.224.151.49/trust` → 200; Session 23 re-verified 2026-05-10 22:05 ET — banner-label "All tests passed", 36 pass chip)*
- [x] `/metrics` page lists every current measure with its expanded SQL and description  *(Plan 7 verified — `curl http://18.224.151.49/metrics` shows `total_requests` and `open_requests` with `<pre class="sql"><code>` SQL blocks; Session 23 re-verified 2026-05-10 22:05 ET)*
- [x] `/docs` page renders dbt documentation with no missing model or column descriptions  *(Plan 7 verified — `curl http://18.224.151.49/docs/index.html` returns 200 with title "dbt Docs"; no missing descriptions per Plan 2 D1; Session 23 re-verified 2026-05-10 22:05 ET — title "dbt Docs", 1.8MB body)*

---

## 7. Open questions

- **Limitations registry — location and format?** ✅ Resolved 2026-05-08 → Option (b) `docs/limitations/`. Markdown files with YAML frontmatter (`id`, `title`, `severity`, `affects`, `since`, `status`) and free-form prose body. See [`docs/limitations/README.md`](docs/limitations/README.md). The Answer Agent and `/trust` page consume from this single location.
- **Does Oxygen's Answer Agent natively support emitting SQL + row count + citations, or is it prompt-configured only?** ✅ Resolved 2026-05-09 (Plan 6 pre-flight) → **partial native, prompt-enforced.** The Oxygen runtime renders the executed SQL block and the result table automatically (the CLI prints `SQL query:` / `Result:` / `Output:` tri-sections; the SPA does the equivalent via the internal API on `127.0.0.1:3001`). The `Output:` section is fully prompt-controlled. Citations and explicit "Returned N rows" framing are not native — they live in the agent's `system_instructions` and are tested against the 5-question bench. Limitations registry is loaded as a static `context.file` glob (`docs/limitations/*.md`); refresh on agent restart.
- **Where does the `/metrics` page generator live?** ✅ Resolved 2026-05-08 → `scripts/generate_metrics_page.py`. Treated as build tooling: pure Python, reads `semantics/views/*.view.yml` and writes `portal/metrics.html`. Run.sh step 7/7 invokes it after `dbt docs generate` and copies the output to `/var/www/somerville/metrics.html`.
