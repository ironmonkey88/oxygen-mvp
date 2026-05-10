# STANDARDS.md — "Done Done" Spec by Layer

## 1. Purpose

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
- [ ] All pipeline steps idempotent
- [ ] Single entry point: `run.sh`
- [ ] Sequential DuckDB access enforced (`dlt → dbt → oxy`); no concurrent writers
- [ ] Oxygen runs as a `systemd` service
- [ ] Pipeline exit codes captured even when tests fail (run continues to record failures, then propagates failure)

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
- [ ] Answer Agent emits the SQL it executed on every response
- [ ] Answer Agent emits the row count returned on every response
- [ ] Answer Agent cites the source tables (and views/measures referenced) on every response
- [ ] Methodology is inspectable — never summarized away or paraphrased into prose

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
- [x] A limitations registry exists in the repo — see [`docs/limitations/`](docs/limitations/) (format resolved §7; populating is ongoing)  *(Plan 2 D0)*
- [ ] Limitations surfaced both on the portal and in agent responses when the query touches a flagged area  *(Plan 4 — `/trust` page + Answer Agent trust contract)*

### 4.5 Reproducible
- [ ] Repo is public (or at minimum clonable by collaborators)
- [ ] Pipeline runs end-to-end with one command (`./run.sh`)
- [ ] All transformations expressed declaratively (SQL, YAML) — no opaque scripts in the data path

---

## 5. Layer standards

### 5.1 Ingestion (dlt)
Pulls source data into Parquet files at `data/raw/`, ready for dbt to read.
**Done done when:**
- [ ] Source documented (URL, dataset ID, auth requirements) in the pipeline file
- [ ] Idempotent — write disposition (`replace` or `merge`) explicit in the pipeline
- [ ] Output format storage-agnostic — Parquet on filesystem, not DuckDB destination
- [ ] Row count verified against source after each run
- [ ] Schema drift handled (`union_by_name=true` for cross-year files where shape changes)

### 5.2 Bronze
Exact mirror of source — the receiving dock. No transforms.
**Done done when:**
- [ ] Exact mirror of source — no value transforms
- [ ] All source columns retained as `VARCHAR` (per `docs/schema.sql`)
- [ ] dlt metadata columns (`_dlt_load_id`, `_dlt_id`) retained for lineage
- [ ] Arrival checks only — `not_null` on PK, `not_null` on critical date columns, `accepted_values` on enum-like columns
- [ ] Model and column descriptions populated in `schema.yml`

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
- [ ] All models have model-level descriptions in `schema.yml`
- [ ] All columns have column-level descriptions — no nulls
- [ ] All surrogate/primary keys have `unique` + `not_null` tests
- [ ] All foreign keys to dims have `relationships` tests
- [ ] Business rule tests defined where applicable (`accepted_values` on bounded enums, range checks where natural)
- [ ] Models surfaced in `dbt docs`
- [ ] Models referenced from at least one `.view.yml` in the semantic layer

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
- [ ] All views have `description:` populated
- [ ] All dimensions have `description:` populated
- [ ] All measures have `description:` populated (this becomes the public definition on `/metrics`)
- [ ] Entities declared correctly — primary on PK, foreign on FK — for join inference
- [ ] `airlayer validate` exits 0
- [ ] `airlayer query -x` returns rows for at least one representative cross-view query
- [ ] `oxy validate` exits 0
- [ ] `oxy build` exits 0 *(deferred to the Answer Agent session per existing decision — `oxy start` brings up the Postgres backing store needed for embeddings)*

### 5.7 Agent (Answer Agent)
The interface — a research partner the analyst can trust.
**Done done when:**
- [ ] `.agent.yml` configured with `execute_sql` tool and Airlayer context block
- [ ] Agent prompt requires SQL, row count, and citations in **every** response (extreme trustability — this is the public commitment in §4.1)
- [ ] Test bench: 5 representative analyst questions answered correctly, with all three trust elements present in every response
- [ ] Limitations surfaced in responses when the query touches a flagged issue from the limitations registry

### 5.8 Knowledge Product (Portal)
Everything the analyst sees outside the chat — and the public window.
**Done done when:**
- [x] Portal hosted on EC2 at port 80 (nginx)  *(Session 4)*
- [x] Routes live: `/`, `/chat`, `/docs`, `/trust`, `/metrics`  *(Plan 4 — `/`, `/docs/`, `/metrics`, `/trust` all 200; `/chat` is Tailnet-only at `:3000` per Plan 1 D4 and is advertised via the hero "Private beta" pill rather than a public-route link)*
- [x] Nav reflects the analyst workflow: chat-first, with `/docs`, `/trust`, `/metrics` one click away  *(Plan 4 — three route links added to `portal/index.html` `.nav-links`; private-beta chat pill preserved on the hero)*
- [x] `/trust` is dynamic — driven by the admin schema, not static copy  *(Plan 4)*
- [x] `/metrics` is generated from Airlayer YAML, not hand-written  *(Plan 2 D3)*
- [ ] Copy is engineering-honest — not marketing-friendly  *(Plan 7 — portal copy refresh)*

---

## 6. MVP 1 sign-off checklist

Single flat checklist. Pulls from §3, §4, §5 — every box ticked before MVP 1 is called done.

**Foundations:**
- [ ] §3.1 Security: 5/5
- [ ] §3.2 Reliability: 5/5
- [ ] §3.3 Usability: 4/4

**Extreme trustability:**
- [ ] §4.1 Verifiability: 4/4
- [ ] §4.2 Public metric definitions: 3/3
- [x] §4.3 Live data quality: 4/4  *(Plan 4)*
- [ ] §4.4 Limitations registry: 2/2
- [ ] §4.5 Reproducibility: 3/3

**Layers:**
- [ ] §5.1 Ingestion (dlt): 5/5
- [ ] §5.2 Bronze: 5/5
- [ ] §5.4 Gold: 7/7
- [ ] §5.5 Admin (DQ): 5/5
- [ ] §5.6 Semantic (Airlayer): 7/7 (with `oxy build` deferred caveat)
- [ ] §5.7 Agent: 4/4
- [ ] §5.8 Knowledge Product (Portal): 6/6

**End-to-end smoke:**
- [ ] Analyst can ask "How many 311 requests were opened in 2024?" and receives a correct answer with SQL, row count, and citation
- [ ] Analyst can ask "What are the most common request types?" and receives a correct answer with SQL, row count, and citation
- [x] `/trust` page is green for the most recent pipeline run  *(Plan 4 — run_id `5a421e8d-55e4-4731-a3a2-50ea0e88a0ee`, 36/36 tests pass)*
- [ ] `/metrics` page lists every current measure with its expanded SQL and description
- [ ] `/docs` page renders dbt documentation with no missing model or column descriptions

---

## 7. Open questions

- **Limitations registry — location and format?** ✅ Resolved 2026-05-08 → Option (b) `docs/limitations/`. Markdown files with YAML frontmatter (`id`, `title`, `severity`, `affects`, `since`, `status`) and free-form prose body. See [`docs/limitations/README.md`](docs/limitations/README.md). The Answer Agent and `/trust` page consume from this single location.
- **Does Oxygen's Answer Agent natively support emitting SQL + row count + citations, or is it prompt-configured only?** ✅ Resolved 2026-05-09 (Plan 6 pre-flight) → **partial native, prompt-enforced.** The Oxygen runtime renders the executed SQL block and the result table automatically (the CLI prints `SQL query:` / `Result:` / `Output:` tri-sections; the SPA does the equivalent via the internal API on `127.0.0.1:3001`). The `Output:` section is fully prompt-controlled. Citations and explicit "Returned N rows" framing are not native — they live in the agent's `system_instructions` and are tested against the 5-question bench. Limitations registry is loaded as a static `context.file` glob (`docs/limitations/*.md`); refresh on agent restart.
- **Where does the `/metrics` page generator live?** ✅ Resolved 2026-05-08 → `scripts/generate_metrics_page.py`. Treated as build tooling: pure Python, reads `semantics/views/*.view.yml` and writes `portal/metrics.html`. Run.sh step 7/7 invokes it after `dbt docs generate` and copies the output to `/var/www/somerville/metrics.html`.
