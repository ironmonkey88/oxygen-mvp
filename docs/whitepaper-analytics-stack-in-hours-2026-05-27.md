# Building an Analytics Stack in Hours, Not Quarters

**A white paper on the Oxygen MVP — proving the modern data stack collapses into a single integrated platform, on real public data, with extreme trustability as the bar.**

*Audience: analysts, analytics leaders, and data platform owners evaluating Oxygen against the modern data stack.*

---

## Executive summary

The conventional path to a working analytics stack — ingestion, warehouse, transformation, semantic layer, BI, and observability stitched together from five-to-seven separately licensed and integrated vendors — takes a strong team a quarter or more to stand up, and most of a calendar year to make trustworthy. In that quarter, the questions that motivated the build have already moved on. The analyst, who is supposed to be the protagonist of all of this, spends their expertise debugging joins.

This white paper documents a working alternative. Over roughly two weeks of single-developer effort with Claude Code, the Oxygen MVP put a complete, trustworthy, end-to-end analytics platform into production on the public Somerville 311 service-request dataset — 1.17 million records, a decade of history, all five stages of the Knowledge Product Pipeline live, with a public portal exposing the metric definitions, data-quality state, and known limitations to anyone who lands on it. An analyst can ask in natural language *"how many 311 requests were opened in 2024?"*, get back **113,961** rendered with the exact SQL that produced it, the row count returned, citations to the source tables and semantic-layer views, and any limitations from the registry that touched the answer.

That speed is not a function of cutting corners. It is a function of three deliberate moves: starting from the analyst's experience and working back to the data, building configuration-first against an integrated platform rather than custom code against integrations, and making *extreme trustability* — every answer ships with its receipts — the non-negotiable bar from day one. Speed and depth are not opposed; the disciplines that made the work fast are the same disciplines that made it trustworthy.

This paper interleaves two things in equal measure. The first is the framework: a synthesis of the [Analytics Platform Primer](#)'s Knowledge Product model, the Knowledge Hierarchy of Needs, the Working Backwards strategy, and the medallion architecture, all of which are general truths about building analytics platforms. The second is the MVP itself as a worked example: what got built, in what order, against what discipline, and why each decision was made the way it was. Read the framework if you want a method; read the MVP sections if you want proof; both are present so you can do either.

The thesis underneath both is simple. *The analyst leaves a session having done in an hour what used to take a week, and tells their friends.* That sentence — **"you have to try this"** — is the only externally checkable signal that the experience landed, and it is the compass every architectural decision in the MVP passes through.

---

## Part I — The framework

### 1. The protagonist is the analyst

The first claim of this work is that the analyst — not the executive who reads the dashboard, not the IT director who buys the platform — is the protagonist of an analytics platform. They carry deep subject-matter expertise and they do their work today in the shadow of technical constraints they didn't choose. They wait on a data engineer to land the source. They wait on an analytics engineer to model it. They wait on a BI developer to surface it. By the time their expertise can act, the question has moved on, and they have made peace with this because they had to.

Returning to that analyst the expectation that their expertise will carry the day is the mission. Every architectural, configuration, and scope decision the MVP makes is checked against a single question: *does this protect the analyst's path, or does it leak friction back in?*

That path has a recognizable shape — a five-phase emotional arc that an analyst moves through in a session when the platform is working:

1. **Relief.** The first verifiable answer lands with SQL, row count, and citation. The analyst sees they don't have to spot-check the platform. Shoulders drop.
2. **Momentum.** The second question comes faster than the first. The third faster still. They chase instincts they would normally suppress because the cost of chasing was too high.
3. **Ownership.** Halfway in, the answer is *theirs*. Their subject-matter judgment found it; their question framed it; the platform kept up. They stop thinking *about* the platform and start thinking *through* it.
4. **Pride.** They imagine showing this to the colleague who keeps asking for things the BI team won't build.
5. **Sharing.** The sentence comes out. They tell their friends.

Each phase has a technical precondition. Relief is impossible without extreme trustability — an answer that asks the analyst to *take its word for it* breaks the first phase, and without the first phase none of the rest happens. Momentum is impossible without a stable semantic layer behind the chat interface. Ownership is impossible without methodological transparency. Pride requires depth. Sharing requires that findings be expressible as something other than a screenshot.

The arc is also a deferral test. Anything that does not protect the path through it gets deferred, regardless of its engineering value on its own. Convenience is not the goal; agency is. Convenience is silent; agency produces the sentence.

### 2. The five stages of the Knowledge Product Pipeline

The primer's central organizing structure is the Knowledge Product Pipeline. A Knowledge Product is a data product designed for a specific decision — a lead-scoring dashboard, a service-equity report, a churn predictor. A dashboard *can be* a Knowledge Product; a dashboard *isn't automatically* one. The distinction matters because Knowledge Products depend on a chain of capabilities, and friction at any stage of the chain becomes friction the analyst feels.

| Stage | What it does for the analyst | What breaks without it |
|---|---|---|
| Get the data | Ingestion from source systems | No inquiry begins |
| Make it queryable | Warehouse + transformation into clean, modeled data | Every question is a multi-week project |
| Make it understandable | Semantic layer — entities, dimensions, measures, lineage, caveats | The analyst spends their expertise debugging joins |
| Make asking easy | Conversational interface backed by the semantic layer | Expertise lives behind SQL fluency, not domain fluency |
| Make sharing easy | Dashboards, Slack, MCP, A2A, BI integrations | Findings stay personal and the work doesn't compound |

The conventional modern data stack delivers these five stages with five-to-seven separate vendors — a Fivetran or dlt for ingestion, a Snowflake or BigQuery for the warehouse, a dbt for transformation, a Cube or dbt Semantic Layer for semantics, a Looker or Omni for BI, a Monte Carlo or Metaplane for observability, and increasingly a chat agent vendor for natural-language access. Each integration has its own auth, its own metadata model, its own update cadence, and its own way of defining a metric. The pathology that emerges from this is what the primer calls **metric drift**: the same metric name means different things in different tools because no single source of truth exists. The semantic layer is the discipline that prevents it; in a stitched stack, the semantic layer is one more vendor whose definitions can disagree with the others.

The argument for an integrated platform is not that integration is intrinsically better. It is that the integrated platform can carry one semantic layer through all five stages — ingestion knows what the entities are, the warehouse models them faithfully, transformation respects their grain, the agent queries them with citations, and the sharing surfaces all route back to the same definitions. Metric drift becomes structurally hard rather than constantly fought.

### 3. The Knowledge Hierarchy of Needs

The primer organizes platform requirements as a hierarchy where each level depends on the levels beneath it:

- **V. Coverage** — functional subject matter (e.g., 311 service requests across a decade).
- **IV. Usability** — accessibility and clarity; intuitive tools and a complete data catalog.
- **III. Reliability** — uptime and consistency; analytics that's there when the analyst is.
- **II. Quality** — accuracy and validation; testing prevents bad data from reaching decisions.
- **I. Security** — RBAC, data masking, controlled access at the base.

Compromise a foundational layer and everything above it loses meaning. An unreliable analyst tool teaches its users to distrust it; an unsecured one cannot be made public; an inaccurate one is worse than no tool at all because it produces confident wrong answers. The hierarchy is also a sequencing rule: do not invest in Coverage before Quality is real, and do not invest in Usability before Reliability holds. Most stacks invert this — they pursue Coverage and Usability because those are visible to leadership, and they accumulate Reliability and Quality debt that the analyst absorbs as friction.

The MVP's [STANDARDS.md](#) document maps Security, Reliability, and Usability directly to this hierarchy as its three "Foundational" sections, and treats each as a sign-off gate the project cannot ship past.

### 4. Working Backwards

The primer's strategic frame is **Working Backwards**: start from the business decision and work back to the data, rather than starting from available data and discovering what it can support. The shape:

> Business Problem → Hypothesis → Knowledge Product → Data.

The MVP applies this in the Somerville case as follows.

- **Business problem.** *Are 311 service requests being resolved fairly across Somerville's neighborhoods?* Service-delivery equity is one of the most consequential questions a city government, journalist, or researcher can ask of public data. The question is unambiguous, the stakes are real, and the answer changes how resources are allocated.
- **Hypothesis.** *There are measurable, non-random differences in how requests are handled across neighborhoods — in volume, resolution rate, resolution time, or service mix — large enough to inform policy.* Deliberately multi-angle, because the analyst doesn't yet know which dimension matters most.
- **Knowledge Product.** A chat-based analytics platform with a public portal, a semantic layer over the 311 data, dashboards built through conversation, and a trust contract on every answer.
- **Data.** Somerville's 311 SODA feed (1.17M rows since 2015), augmented with ward-polygon geography, and over time with crime, permits, traffic citations, the happiness survey, and ACS demographics.

The point of Working Backwards is not that it is more efficient — it is that it puts the decision in the seat of authority. A Knowledge Product reverse-engineered from a real question carries the right grain, the right dimensions, and the right caveats by construction. A Knowledge Product assembled from "what data we happen to have" usually does not.

### 5. The medallion architecture as assembly line

The primer's metaphor for the warehouse is a manufacturing assembly line. Raw materials arrive at a **Receiving Dock** (Bronze): data lands in its original format, with arrival and freshness checks but no transformation. Materials are cleaned at a **Parts Shop** (Silver): normalized, deduplicated, type-corrected, PII-redacted. Finished products leave the **Finished Product** stage (Gold): business logic applied, aggregations computed, the layer the semantic layer and the agents actually point at. A **Control Room** (Observability) watches the line at every stage.

The argument for the medallion is not aesthetic. It is that the layers have *different responsibilities*, and conflating them produces stacks that cannot answer "where did this number come from?" reliably. Bronze's responsibility is faithfulness — be byte-for-byte the source, so lineage works. Silver's responsibility is cleanup — produce consistent, governed data without yet imposing business logic. Gold's responsibility is business meaning — what counts as a "request," what counts as "resolved," which categories roll up where. Admin's responsibility is observation — what tests ran, what passed, what changed.

When the layers are honored, an analyst who finds a surprising number can walk the lineage in one direction (Gold → Silver → Bronze → source API) and find out exactly where the surprise originates. When they're not, the analyst is left in the dark, and trust collapses.

### 6. The analytics maturity lifecycle

The primer names four maturity stages a platform can reach:

| Stage | Question addressed | Typical surface |
|---|---|---|
| Descriptive | "What happened?" | Standardized reports, KPI dashboards |
| Diagnostic | "Why did it happen?" | Drill-down exploration, root-cause analysis |
| Predictive | "What will happen?" | Forecasting, propensity models |
| Prescriptive | "How can we make it happen?" | Suggested actions, optimization |

A platform that pursues Predictive before it has earned Descriptive is building on sand — the analyst cannot trust a forecast for a metric whose definition they're still arguing about. The MVP commits to Descriptive (MVP 1) and Diagnostic (MVPs 2–3) and stops there. Predictive and Prescriptive require modeling capabilities, stakeholder relationships, and risk tolerance the project does not yet claim. Naming what is out of scope is not a weakness; it is what makes the in-scope claim credible.

### 7. Why "extreme trustability" is the bar

A *trustworthy* answer asks the analyst to take the platform's word for it. An *extreme-trustability* answer hands over the receipts.

Every answer the MVP's agent emits ships with four artifacts:

1. The exact SQL it executed.
2. The row count it received.
3. Citations to the source tables and semantic-layer views.
4. Any limitations from the registry that the query touched.

This is the **trust contract**. It is enforced today by the agent's system instructions; the runtime renders the SQL and result table natively; the citation, row count, and limitations are prompt-enforced and surfaced as a structured four-section reply. The contract is the bar because Relief — the first phase of the emotional arc — is impossible without it. An analyst who has to spot-check the platform is doing two jobs and is not liberated.

There is a second-order effect worth naming. A trust contract that ships the SQL also ships the *methodology*. The analyst sees not just the number but the way the number was computed, and they can challenge, refine, or extend it. That moves the conversation from "do I believe this answer?" to "is this the right question?" — which is where the analyst's expertise actually adds value.

---

## Part II — The MVP as worked example

### 8. The dataset and the constraint

The MVP is built on the City of Somerville's 311 service-request feed via Socrata's SODA API: approximately 1.17 million requests across roughly ten years, refreshed continuously. The dataset is unmistakably real — survey columns are sparse in some years, classification taxonomies have shifted, the `block_code` field uses padded-space sentinels for unknown values, the `ward` field is null when geocoding failed, and the most recent year's data is always partial. None of this is hypothetical entropy; all of it is what real public data actually looks like.

That choice is load-bearing. A scrubbed demo dataset would prove only that the platform works on a scrubbed demo dataset. The Somerville feed proves it works on the kind of mess analysts actually encounter, which is the only kind of proof that matters to a prospect evaluating the stack against the modern data stack they already have.

The MVP is built by Gordon Wong (Oxy team) deliberately playing the role of the ideal Oxygen customer — an experienced Snowflake/dbt/Looker architect new to Oxygen. This is a role choice, not a staffing convenience. The voice of the analyst speaking authentically through the build does three things at once: it produces the demo, it surfaces product gaps with customer-shaped urgency, and it grounds Oxygen's feature roadmap in real use.

### 9. The stack — best-of-breed today, Oxygen-native at the destination

The MVP's current stack reflects a deliberate trajectory. Each layer is implemented with the best available tool today, and migrates onto Oxygen's native component when that component reaches production maturity.

| Layer | Today | Oxygen-native target | Migration trigger |
|---|---|---|---|
| Ingestion | **dlt** | Airway | Airway reaches public production maturity |
| Warehouse | **DuckDB** (embedded, single file) | Airhouse | DuckDB outgrows the workload, or Airhouse adds analyst-facing query capabilities |
| Transformation | **dbt Core** | Native SQL modeling inside the workspace | Feature parity with dbt Core for incremental models + tests + docs |
| Semantic Layer | **Airlayer** (`.view.yml`) | Already Oxygen-native | n/a |
| Agents (Answer, Routing, Builder) | **Oxygen-native** | Already Oxygen-native | n/a |
| Dashboards | **Airapp** (`.app.yml`) | Already Oxygen-native | n/a |
| Observability | Custom admin schema + `/trust` page | Native Oxygen Observability | Native Observability provides comparable coverage |
| Sharing (Slack, MCP, A2A, Looker) | **Oxygen-native** | Already Oxygen-native | n/a |

Two cross-cutting commitments hold the trajectory honest. First, **periodic review** — every plan kickoff checks Oxygen's changelog against the project's custom scaffolding, and asks deliberately whether to migrate now or wait. Second, **willingness to deprecate** — sunk cost is not a reason to keep custom scaffolding alive once an Oxygen primitive can produce a better analyst experience. The test is analyst experience, not calendar.

The deployment is intentionally modest: a single AWS EC2 instance (Ubuntu 24.04 LTS ARM), nginx serving the public portal on port 80, Oxygen on port 3000 behind Tailscale for the private chat surface, Claude Sonnet 4.6 via the Anthropic API as the LLM. The whole platform fits on one box. This is not because the workload demands so little — it does — but because *modesty is a feature*. A stack a single developer can stand up on a single box is a stack any team can reproduce; a stack that requires a Kubernetes cluster, a separate Postgres for state, and three SaaS subscriptions to demo is a stack that prospects discount because they cannot picture themselves running it.

### 10. The Knowledge Product Pipeline, instantiated

This section walks each of the five pipeline stages, names what the MVP constructed, and connects it back to the framework.

#### Stage 1 — Get the data

A dlt pipeline (`dlt/somerville_311_pipeline.py`) pulls the Somerville SODA endpoint on every run, materializing the response into DuckDB on a `merge` write disposition keyed on the source primary key `id`. Schema drift across years is handled by `union_by_name=true` at read time. The pipeline is declarative, idempotent, and re-runnable; a fresh ULID run identifier is generated per invocation and stamped onto every row touched, so any record traces back to the run that touched it.

Audit columns (`_extracted_at`, `_extracted_run_id`, `_source_endpoint`, `_first_seen_at`) live alongside the source columns, and the dlt metadata tables (`_dlt_pipeline_state`, `_dlt_loads`, `_dlt_version`) are retained at Bronze. Lineage is a property of the data, not a feature of a separate tool.

This is the primer's **Receiving Dock**, and its only job is faithfulness. No transformation, no judgment, no enrichment. Faithfulness at Bronze is what makes everything downstream verifiable.

#### Stage 2 — Make it queryable

A single embedded DuckDB warehouse (`data/somerville.duckdb`) holds the entire dataset, transformed by dbt Core through a medallion architecture:

- **Bronze** — `main_bronze.raw_311_requests` mirrors the source. 24 columns, 5 tests (1 unique, 3 not-null, 1 accepted-values), all VARCHAR-typed because the source is.
- **Silver** — stubbed; lands in MVP 3 alongside PII redaction, deduplication, and type casts. Until then the project goes Bronze → Gold directly, with the trade-off documented in the limitations registry as a first-class entry.
- **Gold** — `main_gold.fct_311_requests` (the fact table), plus dimensions `dim_date`, `dim_request_type`, `dim_status`. 14 tests (4 unique, 7 not-null, 2 relationships, 1 accepted-values). This is the layer the semantic layer and agents point at.
- **Admin** — `fct_data_profile` (observational column profiling), `dim_data_quality_test` (auto-seeded test baselines), `fct_test_run` (every test's pass/fail on every run), plus pipeline-run and source-health observability tables. This is the primer's **Control Room**.

The choice of DuckDB matters. For a workload of low millions of rows, an embedded warehouse is not a compromise — it is the right tool. There is no separate compute layer to provision, no cluster to right-size, no idle cost when the analyst is not querying. The whole warehouse is a single file. Backups are `cp`. The serializability constraint (only one writer at a time) is enforced by the project's `run.sh` pipeline orchestrator, which sequences ingest → transform → test → admin → docs in a single ordered run.

#### Stage 3 — Make it understandable

The semantic layer is **Airlayer** — `.view.yml` files defining entities, dimensions, and measures, grouped into `.topic.yml` business domains. The same schema feeds both Oxygen's built-in semantic engine (used by the agent at runtime) and the standalone Airlayer Rust CLI (used as a validation convenience). Write the YAML once; query from either.

MVP 1 ships four views (`requests` plus three dimensions) and a single topic (`service_requests`) with two measures (`total_requests`, `open_requests`). The point of MVP 1 is not breadth of coverage; it is establishing the discipline. The `/metrics` page on the public portal is **auto-generated from the Airlayer YAML** — there is no second place where measures are defined, ever. Metric drift is structurally impossible because there is structurally only one source of truth.

Sitting alongside the semantic layer is the **limitations registry**: Markdown files at `docs/limitations/` with YAML frontmatter (`id`, `title`, `severity`, `affects`, `since`, `status`) plus a prose body. Ten active entries cover everything from `block-code-padded` (the sentinel-value problem in the source) to `current-year-partial` (the most recent year always being incomplete) to `oxy-build-postgres-dependency` (an operational note about a deployment quirk). The registry is built into a generated `_index.yaml` by `scripts/build_limitations_index.py`; the agent loads the index at startup (not the full file bodies, which would blow the LLM's context window); and entries surface in the agent's reply when any `affects:` value matches a token in the executed SQL or a cited view.

The registry is the institutional-knowledge layer of the platform. Caveats are first-class artifacts, not footnotes. This is what makes the trust contract more than a structural commitment — it is the substrate the contract operates on.

#### Stage 4 — Make asking easy

The chat interface is an **Answer Agent** — a single `.agent.yml` file (`agents/answer_agent.agent.yml`) configured with the `execute_sql` tool against the DuckDB warehouse, the Airlayer topic loaded as context, the limitations index loaded as context, and a system-instruction prompt that enforces the four-section trust contract on every reply. The prompt forbids summarizing data into prose without the row count and citations; forbids stating a calendar year without first querying it (a hedge against LLM knowledge-cutoff drift); and forbids skipping limitations when an `affects:` value matches.

A representative interaction:

> **Analyst:** *How many 311 requests were opened in 2024?*
>
> **Agent (rendered in the chat surface):**
>
> ```sql
> SELECT count(*) AS request_count
> FROM main_gold.fct_311_requests
> WHERE year(date_created_dt) = 2024;
> ```
>
> Returned 1 row.
>
> **Answer:** 113,961 requests were opened in 2024.
>
> **Citations:** `main_gold.fct_311_requests`, `requests` (Airlayer view).
>
> **Known limitations:** None matched.

A more interesting interaction is one that surfaces a limitation. Asking for satisfaction scores from the 2024 survey returns the SQL, the row count, the answer (about 76% "Very Satisfied"), and a Known limitations section that names `2024-survey-columns-sparse` and `survey-columns-on-fact` by id, with one-sentence summaries and pointers to the full markdown entries. The analyst gets the answer *and* the context they need to decide whether to use it.

The bench Plan 6 ran during MVP 1 sign-off — five representative analyst questions — surfaced one real defect: a question about the current year had the SQL correct but the prose hallucinated the year as "2025" because the LLM's training cutoff disagreed with the database. The fix was to add a hard rule to the prompt forbidding the agent from stating a calendar year without querying for it. That is the project's discipline at work — the bench is not a checkbox, it is the mechanism that finds the bugs that only show up in real use.

#### Stage 5 — Make sharing easy

MVP 1 ships the **public portal** (`/`, `/docs`, `/erd`, `/metrics`, `/trust`, `/profile`, plus the gated chat at `/chat`). Each surface routes back to the same semantic layer and the same DuckDB. The portal's *strategic* role is the "opening note" of the analyst's experience — the first surface they land on, the first impression of the platform.

The portal's job is **recognition before articulation**. An analyst lands on it and immediately recognizes a serious knowledge platform. The surfaces it carries — *Data dictionary, Metrics, Trust* — match what mature analytics teams always wished they had; every surface earns its place by being live; the stack table names tools without explanation because the audience already knows them. The `/trust` page is green or red on the latest pipeline run, not narrative text. The `/metrics` page lists every measure with its expanded SQL. The `/profile` page surfaces per-column distinct counts, null percentages, and top-5 values. The `/erd` page renders the warehouse and semantic-layer diagrams as interactive Mermaid. The `/docs` page is the dbt-generated data dictionary, every column hand-described.

The portal **demonstrates rather than articulates**. It does not carry the language of the emotional arc or the project's mission statement. Putting those on a public surface would break the spell — public-facing analytics surfaces don't talk about their own framing. The portal demonstrates the project's commitments by *being* one of them.

Later MVPs add the other sharing surfaces: **Data Apps** (declarative `.app.yml` dashboards, built through conversation with Builder Agent) in MVP 2; **Slack integration**, **MCP server**, **A2A protocol**, and **Looker integration** in MVP 4. Each surface ships the same trust contract — the answer is the same and the citation chain is the same regardless of where the analyst is sitting.

### 11. The four-MVP roadmap

The build is sequenced as four nested MVPs, each delivering a complete Knowledge Product on Somerville 311 and each adding a stage of analyst maturity. The sequence is not arbitrary; each MVP earns the right to the next by satisfying the analyst-outcome test of its own.

| MVP | Tagline | Outcome | Layers added | Maturity stage | Status |
|---|---|---|---|---|---|
| 1 | First Knowledge Product | Analyst asks a question and gets a verifiable answer with SQL, row count, citation, and limitations | Ingestion + Warehouse + minimal Semantic Layer + Answer Agent + public portal | Descriptive | ✅ Signed off 2026-05-11 |
| 2 | Visual Knowledge Products | Analyst describes a dashboard in chat; Builder Agent assembles it. Iteration by conversation, not by hand-writing YAML | Data Apps + Builder Agent | Descriptive → early Diagnostic | Active |
| 3 | Governance and Trust | Analyst trusts the underlying data without verifying it themselves. Verified Queries badge the answers that ran from pre-approved SQL. Agent test bench catches regressions | Full Silver + Observability + Verified Queries + Agent testing framework | Full Diagnostic | Not started |
| 4 | Semantic Depth and Sharing | Analyst's findings move from personal to shared. A library of trusted metrics works across chat, Slack, BI, and other agents | Expanded Topics/Views + Slack + A2A + MCP + Looker | Diagnostic | Not started |

The roadmap is also a deferral instrument. Each MVP names what it *retires* — what custom scaffolding gets replaced by an Oxygen-native component as the platform's components mature. MVP 2 retires hand-curated chart configurations in favor of Builder Agent. MVP 3 retires the hand-rolled test bench in favor of native agent testing, the prompt-enforced trust signals on the most-asked questions in favor of Verified Queries badges, and possibly some of the admin DQ surface depending on the Observability evaluation. The trajectory is from "best-of-breed today" to "Oxygen-native at the destination," and every MVP moves it one step.

### 12. The disciplines that made the speed possible

Standing up a working analytics platform in roughly two weeks of single-developer effort is not a function of cutting corners. It is a function of disciplines applied so consistently they look invisible from outside.

**Configuration over custom code.** Wherever an Oxygen primitive can produce the desired analyst experience, the primitive is used. Custom Python or SQL exists only where it produces a measurably better experience than the available primitive — and is scoped for retirement the moment a primitive catches up. The `.view.yml`, `.topic.yml`, `.agent.yml`, and `.app.yml` files are the construction interface; the imperative code is the exception.

**Plan in chat; execute in code.** Every unit of work begins as a written prompt in conversation — the chat instance plans the work, names the outcome, lists the phases, and identifies the verification gates. The plan is then handed to Claude Code as a single `.md` file delivered downstream. Code's job is execution. This split keeps the planning rigor distinct from the execution speed, and produces an audit trail — every plan that ran is in `docs/prompts/`, every session that executed it is in `docs/sessions/`. A new analyst onboarding to the project can read the trail.

**Verification gates are split into static and live.** A static-artifact gate (a file exists; a `schema.yml` entry is committed; a config is in place) can be ticked once on a commit hash and stay ticked. A live-functional gate (the page renders; the test passes; the agent answers correctly) must reference a re-runnable verification command and be re-verified in the sign-off session — not inherited from earlier ticks. The split is the systems-engineering V-model applied honestly: verification ("was it built right?") and validation ("did it solve the real problem?") are different gates.

**Honest reporting over clean completion.** A documented partial outranks a fake-clean complete. A surfaced finding is a successful outcome, not a failure. When the agent's prose hallucinated a year, that was logged as a Plan 6 finding and the prompt was hardened against it. When the multi-workspace onboarding wizard failed to accept the existing DuckDB, that was logged as a Session 22 / Session 25 finding and the project pivoted to `oxy start --local`. The bias is toward stating partials accurately, not toward closing sessions cleanly.

**The compass is bidirectional.** The success test — *does this protect the path through the analyst's emotional arc?* — defers work in both directions. It deferred the `/about` page and post-MVP-1 chart/export features (not the first-encounter need). It also *pulled forward* Tailscale from MVP 3 to MVP 1 the moment the team realized an open `:3000` was leaking trust friction before the analyst had asked a question. Compass decisions are not always conservative; they are always grounded.

**Every plan kickoff reviews the Oxygen changelog.** Oxygen ships fast. Capabilities that didn't exist at kickoff (Builder Agent, multi-workspace mode, Magic Link auth, Verified Queries, Data Apps maturity) now reshape the roadmap. Every plan asks: does anything Oxygen shipped since the last plan supersede something we're about to build custom? The default answer is "evaluate and decide deliberately," not "leave it alone."

These disciplines are how a two-week build is also a trustworthy build. Pace and bar held simultaneously because the disciplines are how the work is organized, not an afterthought layered on top.

### 13. Data quality, in detail — the test taxonomy

The portal's `/trust` page is the analyst-facing surface of a deeper discipline that deserves a section of its own, because data quality is the single most common reason analytics platforms lose the trust of their users — and because the MVP's approach to it generalizes.

The MVP organizes tests into two categories.

**Technical tests** are tests derivable from the data model alone — no business knowledge required:

- **Primary-key uniqueness.** Every fact and dimension table has a primary key check. Warehouses like DuckDB, Snowflake, and BigQuery don't enforce uniqueness at write time (the performance cost is prohibitive), so the test runs at the end of every pipeline run.
- **Business-unique keys.** A surrogate primary key can be unique without the underlying record being meaningful. A `sale_id` might be a database-assigned integer, but the *business-unique* key is `(product_id, location_id, time, customer_id)`. Both keys are tested.
- **Not-null constraints.** Defined declaratively in `schema.yml`; tested automatically.
- **Referential integrity.** Every foreign key in a fact table has a corresponding row in the parent dimension. Orphan records — child rows without a matching parent — are the single most common source of "how many customers do we have?" disagreements across reports. They get caught at the test layer.
- **Domain and pattern validation.** Phone numbers, postal codes, license plates, email addresses — anything with a known shape gets shape-checked. This also doubles as PII detection: the same regex that validates an email is the regex that flags one accidentally landing in a public report.

**Business tests** require domain knowledge:

- **Known distributions.** "Monday volumes are usually within this range." When they're not, something has changed. Standard-deviation-based alerts catch the outliers.
- **Sanity constraints.** "Revenue should never be negative." Obvious, but it happens.
- **Drift guardrails.** The MVP's `dq_drift_fail_guardrail` singular test asserts that a synthetic perturbation to the source data correctly fails the relevant test downstream — meta-testing that the test framework itself still works.

A trick the MVP applies throughout: **every test should be a binary**. Instead of checking a value, check whether a property holds and write `true` or `false`. This makes the `/trust` page's green/red status immediately legible, makes failed-test history easy to chart, and makes the work easy to delegate. A wall of test text is intimidating; a dashboard of pass/fail signals is operable.

Test history is itself persisted. Every run, every test, every result lands in `admin.fct_test_run`. This means historical DQ analysis is possible: "uniqueness check on sales fails every Monday for some reason" is not a question you can answer without that history. And — perhaps more importantly — when an analyst raises a concern about the warehouse's reliability, the test history is *evidence*. "We've passed all tests for the last 14 days, and here's the chart" turns a credibility argument into a verifiable claim. That is the same pattern as the agent's trust contract, applied to the platform's own quality posture.

### 14. The portal in detail — opening note as architecture

The portal is the first thing the analyst sees; in the strict sense it is the only surface the project commits to keeping public throughout the build. Its design is worth a section because its strategic role is structurally different from the rest of the platform.

The portal's job is **recognition before articulation**. Five characteristics make that work.

1. **Familiar in shape.** The surfaces it carries — *Data dictionary, Metrics, Trust, ERD, Profile* — are what mature analytics teams always wished they had. They match the analyst's mental model of "what a serious platform looks like" without requiring an explanation.
2. **Impressive in execution.** Every surface earns its place by being live. The `/trust` page is green or red on the latest pipeline run, not a static screenshot. The `/metrics` page is auto-generated from the semantic-layer YAML. The `/profile` page is regenerated when the data shape drifts.
3. **Honest about limits.** A `/trust` block on the homepage names "10 documented limitations" as a positive signal of working maturity, not a hidden concession. The limitations registry has its own surface; analysts can see what the platform does not cover before they invest time asking.
4. **One scroll, not many pages.** Long pages with more scrolling are a better first experience than many nested pages where analysts get lost. The portal's primary surfaces are reachable in one or two clicks; the rest is supporting depth.
5. **Demonstrates rather than articulates.** The portal does not carry the language of the emotional arc, the compass, or the project's mission statement. Those live in `MVP.md` and `BUILD.md`. The portal *is* one of the project's commitments; the strategy docs are where the commitments are written down. Putting strategy language on a public analytics surface would break the spell.

The portal is also tuned by analyst reaction, not specified from a strategy doc up front. The Build Guide says *we construct a public portal.* The MVP doc says *what the portal is for.* The portal itself is iteratively refined against the reaction it produces — the analyst seeing the surface and thinking *"oh, these people get it."*

This separation is load-bearing. It means the portal can evolve continuously without requiring strategy doc updates, and the strategy can evolve without requiring portal redesigns. The two are coupled by the experience they target, not by direct dependency.

### 15. Personas, time grains, and abstraction direction

A question that comes up in nearly every analytics platform conversation: *who is this for, exactly?* The MVP's answer threads two needles.

The protagonist is the analyst — that is settled by mission. But the analyst is not the only person whose decisions the platform supports. There is also the store manager who needs to know whether to send someone home tonight. There is the executive who wants the quarterly view. There is the investor who only cares about the year-on-year trajectory.

The MVP's discipline here is **build from the bottom up, abstract upward**. The analyst's surfaces are granular — every measure with its expanded SQL, every test with its history, every limitation by id. Higher-up stakeholders get *abstractions of the same data*, not branches with separate definitions. A CEO dashboard is composed of measures already defined in the semantic layer, with QA checks ensuring the composite view reconciles to the detailed view. Revenue matches. Counts match.

The direction matters. It is easier to abstract upward from granular than to drill down from a composite — you cannot recompute an individual sale from an average. Working backwards from the executive view tempts the platform into shortcuts the analyst's view cannot afford. Working forwards from the analyst's view preserves the option.

Time grain is the other axis. A store manager thinks in hours and days ("how is tonight going?"). An analyst thinks in weeks and quarters. An investor thinks in years. The same data supports all three, but the *aggregations* and *defaults* differ. The semantic layer's job is to expose all three grains as first-class, with explicit definitions for what "this week" or "this quarter" mean and the canonical join paths to time dimensions.

Personas, in this frame, are not separate dashboards. They are *first-class nodes in the same graph as the data assets* — the architect, the analyst, the manager, the executive all consume from the same semantic layer, just at different abstraction levels. When a measure is added, the dependency analysis runs both ways: which dashboards need it, and which abstractions ought to surface it. The platform's job is to keep those relationships visible.

### 16. The Gordon-as-customer loop

A specific operational pattern the MVP uses, worth naming because it is reproducible: **Gordon-as-customer**.

The project is led by an Oxy team member (Gordon Wong) deliberately playing the role of the ideal Oxygen customer — an experienced Snowflake / dbt / Looker architect, new to Oxygen, building a real Knowledge Product on real data. This is not a staffing convenience; it is a structural choice.

Three things happen because of it:

1. **The demo is produced by the work that needs doing anyway.** Every plan is also a sales artifact, every session log is also a case study, every limitations entry is also a piece of evangelism about taking caveats seriously.
2. **Product gaps surface with customer-shaped urgency.** When the multi-workspace onboarding wizard couldn't accept the existing DuckDB file, that wasn't an internal QA issue — it was a customer pivot. The fix (the `--local` mode pivot) was documented as customer feedback to the Oxy product team alongside the project's own session log.
3. **Feature work gets grounded in real use.** Oxygen ships fast, and the velocity is real, but velocity without grounding produces drift. Gordon-as-customer is the grounding mechanism. The MVP's existence forces every Oxygen change to be evaluated against "does this make the analyst's experience better, or just different?"

A second loop nested inside the first: **chat-as-planner, code-as-executor**. The chat side of the project (this kind of conversation) plans, scopes, and writes the prompts that go to Claude Code. Code executes against the repo. The split is deliberate — planning rigor and execution speed are different modes, and confusing them produces work that is either over-engineered or under-considered. The plan is always a downloadable `.md` file delivered to Code; Code's job is to start from that plan, with Phase 0 always being "write this prompt verbatim to `docs/prompts/plan-NN-<slug>.md` on a new branch `claude/plan-NN-<slug>`" as the first commit. The audit trail is the work product.

A third loop, the slowest: **recursive understanding-checking**. Documents are fed back to the chat side, with the question *where has your understanding drifted from what's actually being built?* The chat side re-reads, identifies deltas, retunes. This is how the strategy docs (`MVP.md`, `BUILD.md`, `PHILOSOPHY.md`, `STANDARDS.md`) stay aligned with the code. Without this loop they would diverge silently; with it, they converge.

### 17. The repository as install path for a new analyst

The next milestone for the project — beyond MVP 2's Data Apps and Builder Agent work — is to **extract the build process into a repository a new analyst can use to stand up an empty warehouse on their own**. The artifact is not just the running Somerville instance; it is the *install path* to a new instance.

The shape of the install path:

- **An empty warehouse**, with the medallion schemas in place but no rows in them.
- **Sample data**, sufficient to demonstrate the pipeline end-to-end without committing the new analyst to a particular dataset.
- **One runnable report**, so the analyst sees a working trust-contract answer on their own data within minutes of cloning.
- **A configured Claude (or equivalent assistant)**, primed with the project's docs and conventions, so the analyst can ask *"what should I do next?"* and get a grounded answer — import a new schema, add queries, add QA checks, and so on.

The configured assistant is the load-bearing piece. It is not enough to ship a repo; the repo has to be *queryable* by the new analyst. Every project doc — `CLAUDE.md`, `MVP.md`, `BUILD.md`, `STACK.md`, `ARCHITECTURE.md`, `STANDARDS.md`, `DASHBOARDS.md`, `PROMPTS.md`, `PHILOSOPHY.md` — exists to be loaded as context for an assistant that will then explain to the new analyst what is already true about the project and what their next move could be. The recursive understanding-checking loop is what keeps those docs faithful enough to be the assistant's primer.

The install-path artifact is, in effect, the Knowledge Product Pipeline applied to *the act of building a Knowledge Product*. Get the configuration, make it queryable, make it understandable, make asking easy, make sharing easy. The same five stages. The same compass.

### 18. The Somerville reach — civic analytics as a side effect

A note on a side effect that is not the primary purpose of the project but is worth surfacing because it shapes how prospects respond to it.

Because the dataset is real, public, and locally relevant, the MVP has the natural shape of a civic analytics product. The Somerville rats problem, the broken-streetlight problem, the snow-removal complaints — these are real questions Somerville residents ask, and the platform happens to answer them. The cost of goods for the platform is low enough (one EC2 instance, one DuckDB file, Claude API calls) that releasing standardized civic-analytics products to neighboring cities — Cambridge, Everett, Malden, all of whom share the same patterns of complaint — is approximately free.

The strategic frame for that side effect, named carefully, is **open-core or customer-type tiering**. The civic surface is free or near-free; restaurant chains, retailers, and other commercial customers pay for the same platform on their data. The differentiation is not technical — it is who the customer is. This is speculative as a go-to-market frame, but it is consistent with the project's underlying conviction (from `PHILOSOPHY.md`) that an honest, complete picture of how a community is doing is itself a service to the people that community is made of. Civic analytics that compound across cities is the natural shape of that conviction, and it is a shape the platform happens to be ready for.

### 19. What the MVP is not

A final inventory, for clarity.

The MVP is **not a resident-facing news product**. Simplifying away the SQL, the row counts, and the limitations would break the surfaces that produce trust for the analyst. An `/about` page and resident-oriented framing are deferred indefinitely; they belong to a different project.

The MVP is **not a multi-city template**. The Somerville specificity is the point. Real data, real city, real stakes. A generic "311 analyzer" would be a worse demonstration because it would necessarily be shallower.

The MVP is **not a chat-only demo**. The framework's whole frame is that Knowledge Products depend on the full pipeline. A chat-only demo would prove only the surface.

The MVP is **not predictive or prescriptive**. Descriptive and Diagnostic are the maturity stages the project commits to. Predictive and Prescriptive require modeling capabilities and stakeholder relationships the project doesn't yet claim.

The MVP is **not a multi-tenant SaaS**. Single deployment, single dataset, single team. Multi-tenant readiness is a watch-item for MVP 4, not a primary commitment.

The MVP is **not a replacement for the analyst**. The platform amplifies expertise; it does not substitute for it. SQL fluency, domain knowledge, judgment about what question to ask next — these become *more* valuable in an Oxygen session, not less. The build deliberately avoids framings that suggest automation of the analyst's role. The analyst is the protagonist, and protagonists don't get automated.

---

## Part III — Implications for prospects evaluating Oxygen

### 20. What this means for analysts

If you are an analyst evaluating Oxygen, the MVP is built for you to test against your own work. The proposition is concrete:

- The first verifiable answer you get from the chat agent should hand over its SQL, row count, citation, and any relevant limitations. If it does not, the platform has failed its own bar — tell the team.
- The semantic layer should be the only place a metric is defined. If you find a measure with two definitions in two places, that is a regression — tell the team.
- The `/trust` page should be green or red based on the actual most-recent pipeline run, not on text someone wrote three months ago. If it is stale, that is a bug.
- The limitations registry should surface in your replies when the query touches a flagged area. If it does not, that is a Plan 6-class defect.

The bar is not "trustworthy." The bar is *extreme trustability*. Every claim is independently verifiable. The platform earns your trust by showing its work, not by asking you to take its word.

### 21. What this means for analytics leaders

If you are an analytics leader, the question to test is whether the integrated stack collapses your team's hand-off chain. The conventional stack has the analyst waiting on a data engineer (ingestion), an analytics engineer (modeling), and a BI developer (surfaces). The MVP's claim is that the analyst can complete the full loop themselves, with Builder Agent doing the construction work for the layers they would otherwise have to delegate.

Three observable signals that this is working:

1. **Cycle time on a new question collapses from days to minutes.** Not just the first question — the second, third, and tenth.
2. **Definitions stop diverging across surfaces.** "Active customer" means the same thing in chat, in a dashboard, in a Slack reply, and in a downstream agent.
3. **The trust posture moves from "explain why the data is right" to "the trust contract is right there."** Time spent justifying numbers turns into time spent acting on them.

The MVP's roadmap (the four nested MVPs) is also a deferral roadmap. It names what gets retired at each stage, which means the question for a leader is not "can we adopt all of this at once" but "where on the trajectory does our team start?" Most teams start somewhere in the middle — ingestion already works, the warehouse exists, the semantic layer is the gap. Oxygen's modular adoption is the framework's natural answer.

### 22. What this means for data platform owners

If you own the platform, the question is whether one integrated system can replace five-to-seven specialized vendors *without losing differentiated capability at any layer*. The MVP's evidence on this is mixed-but-promising:

- **Ingestion (dlt today, Airway eventually).** dlt is excellent and not at risk of replacement until Airway reaches feature parity. The migration trigger is documented; the project will evaluate, not assume.
- **Warehouse (DuckDB today, Airhouse eventually).** DuckDB is sufficient at this volume. For larger workloads, Airhouse's analyst-facing query capabilities will need to compete on more than just storage — observability and lineage matter.
- **Transformation (dbt Core today, native eventually).** dbt is the incumbent for good reasons. Replacement requires feature parity on incremental models, tests, and docs generation. Not soon.
- **Semantic Layer (Airlayer today).** Already Oxygen-native and the strongest surface of the platform. The same `.view.yml` schema serves both the runtime agent and the standalone validation CLI. Metric drift is structurally hard.
- **Agents (Answer, Routing, Builder).** Already Oxygen-native. The trust contract sits on the Answer Agent; the construction interface sits on Builder Agent.
- **Dashboards (Airapp).** Already Oxygen-native; built through conversation with Builder Agent from MVP 2 onward.
- **Observability.** Custom for now; native Oxygen Observability evaluated at MVP 3.
- **Sharing (Slack, MCP, A2A, Looker).** Already Oxygen-native.

The pattern across these: where Oxygen is native, the integration is clean and the metric-drift surface is closed. Where the project is still on best-of-breed external tools, migration is scoped and the trigger is documented. The trajectory is "best-of-breed today, Oxygen-native at the destination," and the project's track record on actually executing the migrations is what makes the trajectory credible.

### 23. The compass, restated

Every architectural decision the MVP makes passes through the same question: *does this protect the path through the analyst's emotional arc — relief, momentum, ownership, pride, sharing — or does it leak friction back in?*

The compass is also the test prospects should apply when evaluating the platform. Run the analyst exercise yourself. Ask a real question of the Somerville data. See whether the four-section reply lands. See whether you can verify the answer in less than thirty seconds. See whether the second question comes faster than the first.

If those things happen, the experience landed. If they don't, the project's job is to figure out why and fix it. That feedback loop is open by design.

---

## Closing

The conventional path to a working analytics stack takes a quarter. The Oxygen MVP showed it can take two weeks, on real public data, with extreme trustability as the bar, by collapsing five-to-seven vendor integrations into a single integrated platform held to the discipline of a single semantic layer.

That speed is not magic. It is the framework — Knowledge Products, the Hierarchy of Needs, Working Backwards, the medallion architecture, the Maturity Lifecycle — applied with two consistent commitments: the analyst is the protagonist, and every answer ships with its receipts.

The MVP is signed off on MVP 1; MVP 2 (Visual Knowledge Products) is active; MVPs 3 and 4 are scoped. The repo is being extracted into an install path so that a new analyst can stand up the same warehouse on their own, with sample data and a configured assistant primed by the project's docs.

If you are an analyst, an analytics leader, or a data platform owner: the test that matters is whether, after a working session with this platform, you find yourself telling a colleague *"you have to try this."* That sentence is the only externally checkable signal that any of this landed. Every decision in the project answers to it.

---

*Build authority docs: [MVP.md](#) (the why), [BUILD.md](#) (the how), [STACK.md](#) (the what), [PHILOSOPHY.md](#) (the why beneath the why), [STANDARDS.md](#) (the done-done gates), [ARCHITECTURE.md](#) (the component map).*

*Project repository: `ironmonkey88/oxygen-mvp`. Public portal: the Somerville Analytics site, hosted on AWS EC2 behind nginx.*

*This paper is a synthesis of the [Analytics Platform Primer](#) (general framework), the MVP's authority documents (project specifics), and a 2026-05-26 demo conversation walking the running platform end-to-end (worked-example detail).*
