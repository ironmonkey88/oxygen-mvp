# BUILD.md — Oxygen MVP Build Guide

> **What this is.** The bridge between *what we're building* and *why* — the construction logic that ties the [primer](docs/Analytics_Platform_Primer.docx) (foundational frame) to the project as a whole. This guide is durable: it does not track progress or status. For *what's built today*, read [TASKS.md](TASKS.md) and [LOG.md](LOG.md). For *strategic positioning and audience*, read [MVP.md](MVP.md). For *done-done criteria* by layer, read [STANDARDS.md](STANDARDS.md). This guide answers the higher-level questions those docs assume: why this stack, why this sequence, why these disciplines, and what every architectural decision is ultimately for.

---

## 1. Mission

The mission of this project is to prove that **Oxygen turns a week of analyst work into an hour, on real data, in public.**

The protagonist is the data analyst — not the executive who reads the dashboard, not the IT director who buys the platform. The analyst is the person whose job is to answer questions with data, who carries deep subject-matter expertise, and who today does that work in the shadow of technical constraints they didn't choose. They wait on a data engineer for ingestion, on an analytics engineer for modeling, on a BI developer for dashboards. By the time they can act on their expertise, the question has moved on. They've made peace with it because they had to.

This project returns to that analyst the expectation that their expertise will carry the day.

[MVP.md](MVP.md) defines the experience this project commits to creating: the emotional arc the analyst moves through in a session (relief → momentum → ownership → pride → sharing), the role of the public portal as the opening note of that experience, and the success test for the whole project — an analyst saying *"you have to try this"* to a colleague, unprompted. BUILD.md inherits MVP.md's compass — *does this protect the path through the arc, or does it leak friction back in?* — as the single question every architectural, configuration, and scope decision in this guide passes through. For the strategic framing, read MVP.md; this guide is how every layer is constructed to deliver on it.

### Why "extreme trustability" is the bar

A trustworthy answer asks the analyst to take our word for it. An extreme-trustability answer hands over the receipts — the SQL, the row count, the citation, the known limitations. Relief is impossible without this; an analyst who has to spot-check the platform is doing two jobs and is not liberated. Trust is the gate the entire emotional arc walks through. If we miss it, nothing downstream works.

### Why Gordon-as-customer

The build is led by Gordon Wong (Oxy team) playing the ideal Oxygen customer — an experienced Snowflake/dbt/Looker architect new to Oxygen. This is a deliberate role, not a staffing convenience. The voice of the analyst speaking authentically through the build does three things at once: it produces the demo, it surfaces product gaps with customer-shaped urgency, and it grounds Oxy's feature work in real use. The mission of the project includes hardening Oxygen against real-world entropy and feeding that learning back into the platform.

---

## 2. Foundation — the primer's frame, applied

The [Analytics Platform Primer](docs/Analytics_Platform_Primer.docx) is the conceptual foundation; this guide assumes it. Two of its frames carry through every part of the build.

### The Knowledge Product Pipeline

Every Knowledge Product depends on a chain of capabilities:

| Stage | What it does | Why it matters to the analyst |
|---|---|---|
| Get the data | Ingestion from source systems | Without it, no inquiry begins |
| Make it queryable | Warehouse + transformation into clean, modeled data | Without it, every question is a project |
| Make it understandable | Semantic layer — entities, dimensions, measures, topics, views, definitions, lineage, caveats | Without it, the analyst spends their expertise debugging joins |
| Make asking easy | Conversational interface backed by the semantic layer — agents | Without it, expertise lives behind SQL fluency, not domain fluency |
| Make sharing easy | Dashboards, Slack, MCP, A2A, BI integrations | Without it, findings stay personal and the work doesn't compound |

Friction at any stage is friction the analyst feels. The platform's job is to keep all five stages working — and Oxygen's claim is that it can deliver every stage in a single integrated system rather than five-to-seven separately integrated vendors. This MVP exercises every stage to demonstrate the claim.

### The Knowledge Hierarchy of Needs

The primer organizes platform requirements as a hierarchy where each level depends on the levels beneath:

- **V. Coverage** — functional subject matter (e.g., 311 service requests across a decade)
- **IV. Usability** — accessibility and clarity; intuitive tools, complete data catalog
- **III. Reliability** — uptime and consistency; analytics that's there when the analyst is
- **II. Quality** — accuracy and validation; testing prevents bad data from reaching decisions
- **I. Security** — RBAC, data masking, controlled access

Compromise a foundational layer and everything above it loses meaning. An unreliable analyst tool teaches its users to distrust it; an unsecured one cannot be made public. The hierarchy is what [STANDARDS.md](STANDARDS.md) §3 ("Foundational standards") maps to — Security, Reliability, and Usability are foundational because the rest of the build is contingent on them holding.

This project also borrows the primer's **Analytics Maturity Lifecycle** — Descriptive → Diagnostic → Predictive → Prescriptive — as the trajectory along which the four MVPs progress. MVP 1 is Descriptive ("what happened?"). MVPs 2-3 advance into Diagnostic ("why did it happen?"). Predictive and Prescriptive are explicitly out of scope; they require modeling capabilities and a stakeholder relationship this project doesn't claim.

---

## 3. The build — Knowledge Product Pipeline instantiated

For each of the five pipeline stages, this section names *what we're constructing* and *why*. It is the architectural commitment, not the build status.

### Stage 1 — Get the data

**What it does for the analyst.** Without ingestion working, the analyst's inquiry never begins. The Somerville 311 dataset must be live, current, and shaped enough to query.

**What we construct.** A dlt pipeline pulling Somerville's SODA endpoint on every run, materializing the raw response as partitioned Parquet on disk. Schema drift across years is handled at read time by `union_by_name=true` in the warehouse layer. The pipeline is declarative, idempotent, and re-runnable.

**Architectural role.** This is the **Bronze** layer's source — the receiving dock. The pipeline's only job is to faithfully copy the source. No transformation, no judgment, no enrichment. Faithfulness here is what makes everything downstream verifiable.

### Stage 2 — Make it queryable

**What it does for the analyst.** Without a queryable warehouse, every question becomes a multi-week engineering project. With one, the analyst can iterate.

**What we construct.** A single embedded warehouse (DuckDB) holding all 311 data, transformed through a medallion architecture by dbt Core:

- **Bronze** — exact mirror of the source. VARCHAR columns retained, no value transforms, dlt metadata preserved for lineage. Arrival checks only (`not_null` on the primary key, `accepted_values` on enum-like columns). This is the primer's "Receiving Dock."
- **Silver** — cleaned, typed, deduplicated, PII-redacted. This is the primer's "Parts Shop." Silver lands in MVP 3 alongside governance; until then, the project goes Bronze → Gold directly, with the trade-offs that implies named in the limitations registry.
- **Gold** — business-ready facts and dimensions. The fact table (`fct_311_requests`) plus dimensions (`dim_date`, `dim_request_type`, `dim_status`). This is the primer's "Finished Product" — the only layer the semantic layer and agents point at.
- **Admin** — assertional and observational tables for data quality. Profile snapshots per run, baselined test definitions, parsed test results. This is the primer's "Control Room."

**Architectural role.** The warehouse is the source of truth on EC2 — queried by Oxygen at runtime, the destination for every pipeline step. DuckDB-Wasm is on the roadmap for an analyst-facing browser-side query surface, where lightning-fast in-browser queries eliminate the server round-trip and reinforce the momentum phase of the emotional arc.

### Stage 3 — Make it understandable

**What it does for the analyst.** Without a semantic layer, every measure is a SQL snippet someone wrote once and may or may not still mean what it meant. With one, definitions are stable, lineage is visible, and caveats travel with the metric. The primer calls the missing-semantic-layer pathology "metric drift," and it is the single biggest source of analyst distrust in conventional stacks.

**What we construct.** An Airlayer semantic layer — `.view.yml` files defining entities, dimensions, and measures; `.topic.yml` files grouping views into business domains. The exact same schema feeds both Oxygen's built-in semantic engine (which agents query at runtime) and the standalone Airlayer Rust CLI (a shell-based validation and testing tool). Write the YAML once, query from either.

The semantic layer's job is not only to define metrics. It is to carry institutional knowledge — the limitations registry sits alongside it. Each limitation is a Markdown file with YAML frontmatter (`id`, `severity`, `affects`, `since`, `status`) plus prose. The agent loads the index at startup and surfaces matched entries in its replies. Caveats are first-class artifacts, not footnotes.

**Architectural role.** This is the analyst's source of truth for what every number means. The `/metrics` page on the portal is auto-generated from the YAML — there is no second place where measures are defined, ever. The agent's trust contract is anchored in citations back to this layer.

### Stage 4 — Make asking easy

**What it does for the analyst.** Without a conversational interface, expertise that should be expressed in questions ("are requests being handled fairly across neighborhoods?") gets expressed in SQL ("`SELECT ward, COUNT(*) ... GROUP BY ...`"). The cost of asking constrains the curiosity. With chat backed by the semantic layer, the curiosity comes back.

**What we construct.** An Answer Agent (`.agent.yml`) with two primary tools: `execute_sql` (write and run SQL against DuckDB) and `semantic_query` (let the semantic layer plan the query). Its system instructions enforce the trust contract: every reply contains the row count returned, the answer, a citations block naming the views/measures used, and any limitations from the registry that the query touched. The runtime renders the executed SQL natively, so the methodology is always visible.

A Routing Agent dispatches to the right specialized agent or workflow once the semantic layer grows beyond a single topic. This lands in MVP 4 with the expanded library.

The Builder Agent — Oxygen's project-file copilot — is the construction tool for the rest of the build. From MVP 2 onward, the analyst describes what they want and Builder Agent reads, modifies, and iterates on the project files. The analyst never hand-writes YAML.

**Architectural role.** This is where the emotional arc happens. The interface is the surface; the trust contract is what makes the surface earn its claim.

### Stage 5 — Make sharing easy

**What it does for the analyst.** Findings that stay personal don't compound. The analyst's work needs to land where the work already lives — in dashboards, in Slack, in BI tools, in other agents' context.

**What we construct.** Multiple surfaces sharing the same semantic layer and the same data:

- **Data Apps** — declarative `.app.yml` dashboards, built through conversation with Builder Agent. Live, queryable, not screenshots. Lands in MVP 2.
- **Slack integration** — native Oxygen Slack bot; `@oxygen` mentions return answers with inline SQL artifacts. Lands in MVP 4.
- **MCP server** — exposes agents, workflows, semantic topics, and SQL files as tools to other AI assistants. Lands in MVP 4.
- **A2A protocol** — programmatic agent-to-agent interrogation. Lands in MVP 4.
- **Looker integration** — bridges to existing BI infrastructure where it exists. Lands in MVP 4 if relevant.
- **Public portal** — the public window for the project; static pages plus dynamic `/metrics`, `/trust`, `/docs`, and (eventually) public chat behind Magic Link auth. The portal's *strategic* role — why it looks the way it does, why it carries familiar-but-impressive surfaces, why it's tuned by analyst reaction rather than specified up front — is defined in [MVP.md](MVP.md) under "The opening note." This guide constructs the portal; MVP.md says what it's for.

**Architectural role.** Every sharing surface routes back to the same semantic layer and the same DuckDB. The promise is consistency across surfaces: ask in chat, ask in Slack, ask via MCP — the answer is the same and the citation chain is the same. This is what protects the metric-drift problem the primer warned about.

---

## 4. Component Trajectory

> **Best-of-breed today, Oxygen-native at the destination.**

Oxygen's modular architecture is designed for incremental adoption. The build reflects that: each layer is implemented with the best available tool today, and migrates onto Oxygen's native component when that component reaches production maturity. The trajectory matters because it protects two commitments at once — the project ships working today, and the project demonstrates Oxygen's full surface area at the destination.

The primer's "Oxygen" column maps each platform layer to a forward-looking product name (Airway, Airhouse, Airform, Airlayer, Airapp, AirAgent, Airtraffic). Some of those are public today; others are roadmap. The trajectory below names the migration plan for each.

| Layer | Best-of-breed today | Oxygen-native target | Migration trigger | Migration shape |
|---|---|---|---|---|
| Ingestion | dlt | Airway | Airway reaches public production maturity | Replace `dlt/somerville_311_pipeline.py` with an Airway pipeline config; preserve the SODA endpoint and Parquet shape; verify row counts unchanged |
| Warehouse | DuckDB (single file, embedded) | Airhouse | DuckDB outgrows the workload, OR Airhouse provides analyst-facing query capabilities DuckDB cannot | Single migration window; medallion structure preserved; run all dbt models against the new warehouse and verify gold row counts |
| Transformation | dbt Core | Native dbt-style SQL modeling inside the Oxygen workspace | Feature parity with dbt Core for incremental models + tests + docs generation | Move dbt project files into the workspace's modeling directory; preserve schema.yml descriptions; re-run tests |
| Semantic Layer | Airlayer (standalone CLI + Oxygen built-in engine) | Already Oxygen-native | n/a — already at destination | Standalone CLI remains as a validation convenience; the `.view.yml` schema is the same |
| Agents (Answer, Routing, Builder) | Oxygen-native | Already Oxygen-native | n/a — already at destination | — |
| Dashboards | Airapp (Data Apps) | Already Oxygen-native | n/a — built natively from the start | Builds in MVP 2 |
| Observability | Custom admin schema + `/trust` page | Native Oxygen Observability | Native Observability provides comparable assertional + observational coverage | Migration evaluated in MVP 3; admin tables may persist for project-specific assertions even after migration |
| Sharing surfaces (Slack, MCP, A2A, Looker) | Oxygen-native | Already Oxygen-native | n/a — built natively from MVP 4 onward | — |

**Two cross-cutting commitments hold the trajectory honest:**

1. **Periodic review.** Every plan kickoff checks the Oxygen changelog against this project's custom scaffolding. When a native component reaches production maturity for something we've built custom, the question is asked: do we migrate now, or wait? The default answer is "evaluate and decide deliberately," not "leave it alone."

2. **Willingness to deprecate.** The project is built single-developer with Claude Code, configuration over custom code. Custom scaffolding exists where Oxygen doesn't yet, not because we prefer custom — when the platform catches up, we migrate. Sunk cost is not a reason to keep a custom thing alive.

---

## 5. The four-MVP build sequence

The build proceeds in four nested MVPs, each delivering a complete Knowledge Product on Somerville 311 and each adding a stage of analyst maturity. The sequence is not arbitrary; each MVP earns the right to the next by satisfying the analyst-outcome test of its own.

### MVP 1 — First Knowledge Product

**Outcome.** The analyst can ask a natural-language question about Somerville 311 and get a verifiable answer with SQL, row count, and citation. They trust the answer enough to put it in a report. The emotional arc reaches **relief**.

**Layers built.** Ingestion + Warehouse + minimal Semantic Layer + Knowledge Product (chat).

**Configuration produced.** A working pipeline (`run.sh`), the medallion schemas (bronze + gold + admin), a starting semantic layer (4 views + 1 topic + 2 measures), an Answer Agent with the trust contract enforced, and a public portal (strategic role defined in [MVP.md](MVP.md)) exposing the metric definitions, data-quality state, and limitations registry.

**Scaffolding retired.** None — this is the foundation.

**Maturity stage.** Descriptive ("what happened?").

**Demo moment.** *"How many 311 requests in 2024?"* → 113,961, rendered with the SQL that produced it.

### MVP 2 — Visual Knowledge Products

**Outcome.** The analyst describes a dashboard in chat ("Show me service request volume by neighborhood, monthly, with a drill-down on top categories") and Builder Agent assembles it. They iterate by conversation, not by hand-writing YAML. The emotional arc reaches **momentum** and begins approaching **ownership** — their conversational instructions become deliverable artifacts.

**Layers added.** Data Apps (dashboards) + Builder Agent (construction interface).

**Configuration produced.** `.app.yml` dashboard files generated by Builder Agent, additional measures and computed dimensions in the semantic layer (resolution time, response-time bands), and a Data Apps surface accessible from the portal. The first dashboard is the one the Working Backwards example needs — service equity across neighborhoods, with the four investigative angles (volume, resolution rate, resolution time, service mix) one click apart.

**Scaffolding retired.** Hand-curated chart configurations; Builder Agent does the construction. The analyst's role moves from constructor to product designer.

**Maturity stage.** Descriptive → early Diagnostic. Drill-down arrives.

**Demo moment.** *"Show me service request volume by neighborhood, monthly, with a drill-down on top categories."* → Dashboard appears, fully configured, in chat.

### MVP 3 — Governance and Trust

**Outcome.** The analyst trusts the underlying data without having to verify it themselves. Verified Queries badge the answers that ran from pre-approved SQL. Agent test bench (LLM-as-judge) catches regressions before the analyst does. The full medallion architecture (Silver lands here) closes the PII gap and lets dimensions like neighborhood become first-class. The emotional arc reaches **ownership** in full — the analyst is producing publishable work without spot-checking.

**Layers added.** Full Transformation (Silver layer) + Observability + Verified Queries + Agent testing framework.

**Configuration produced.** Silver dbt models with PII redaction, deduplication, type coercion; a refreshed Gold layer with `dim_location` (neighborhood + coordinates); `.sql` files registered as Verified Queries for the highest-trust analyst questions; `.agent.test.yml` files running under `oxy test` for regression coverage; an evaluation of Oxygen's native Observability against the existing admin DQ surface.

**Scaffolding retired.** Hand-rolled test bench in `scratch/`; replaced by native agent testing framework. Prompt-enforced trust signals for the most-asked questions; replaced by Verified Queries badges. Possibly some of the admin DQ surface, depending on the Observability evaluation.

**Maturity stage.** Full Diagnostic ("why did it happen?"). Guided exploration arrives.

**Demo moment.** *"Why did sidewalk repair requests spike in March?"* → Agent narrows from category to neighborhood to date range, each step verified, with the supporting query history one click away.

### MVP 4 — Semantic Depth and Sharing

**Outcome.** The analyst's findings move from personal to shared. A library of trusted metrics works across chat, Slack, BI tools, and other agents. Findings are live, queryable artifacts — not screenshots. The emotional arc reaches **pride** and **sharing** — the analyst is the person who had this first, and they're showing colleagues.

**Layers added.** Expanded Topics and Views library + Routing Agent + Slack integration + MCP server + A2A protocol + Looker integration (where relevant) + public chat surface via Magic Link auth.

**Configuration produced.** A full semantic layer covering operational and resident-facing slices of 311 (departments, time-of-day, response-time SLAs, category trees); a Routing Agent dispatching to the right specialized agent; a Slack bot deployed to a real workspace; an MCP server exposing the project as tools to other AI assistants; an A2A endpoint live; public chat behind Magic Link.

**Scaffolding retired.** Tailnet-only access for the chat surface — public auth replaces it. The portal's "Private beta" framing becomes a real CTA.

**Maturity stage.** Diagnostic, deepened. Predictive and Prescriptive are explicitly out of scope for this project.

**Demo moment.** Slack: *"@oxygen what's our SLA performance this quarter?"* → answer in-thread, with a link to the live dashboard, shareable to the next analyst who picks up the work.

---

## 6. Working Backwards — the Somerville 311 application

The primer prescribes **Working Backwards** as the strategy for building Knowledge Products: start from the decision, work back to the data. The Somerville 311 application of that framework gives this project its substantive content — what the analyst is actually doing in a session.

### Business problem

*Are 311 service requests being resolved fairly across Somerville's neighborhoods?*

Service-delivery equity is one of the most consequential questions a city government, journalist, or researcher can ask of public data. The question is unambiguous, the stakes are real, and the answer changes how resources are allocated and how the city is held accountable. It also generalizes — every city government and every public agency has a version of this question for its own service delivery.

### Hypothesis

*There are measurable, non-random differences in how 311 requests are handled across neighborhoods — in volume, resolution rate, resolution time, or the mix of services delivered — and those differences are large enough to inform policy.*

The hypothesis is multi-angle on purpose. An analyst investigating equity doesn't know in advance which dimension matters most:

- **Volume disparities** might reflect access (some neighborhoods report less because they trust the system less)
- **Resolution time** might reveal where the city is meeting its SLAs
- **Resolution rate** might surface categories where reports go nowhere
- **Service mix** might show different neighborhoods getting fundamentally different attention

The analyst's job is to narrow the hypothesis — to follow the evidence through whichever angle the data surfaces.

### The Knowledge Product

A conversational interface backed by trustworthy data. The analyst poses the umbrella question and follows the evidence through whichever angle the data supports. Every answer carries the SQL that produced it, the row count it returned, and a citation back to the source. The analyst verifies and publishes without spot-checking the platform.

The Knowledge Product is *not* a pre-built dashboard answering one of the angles. Pre-built dashboards anticipate questions; this Knowledge Product anticipates the analyst's curiosity. Dashboards arrive in MVP 2 as the analyst's *output* (their findings packaged for sharing), not as the platform's pre-baked answer.

### The data

Somerville's public 311 service request dataset: roughly 1.16 million requests across about ten years, refreshed from the city's SODA endpoint. Each row carries a case category, a neighborhood and coordinate, an open timestamp, a close timestamp, and a status. From those columns, every angle of the hypothesis is testable.

### Semantic-layer scope across the MVPs

The semantic layer expands in service of the Working Backwards hypothesis. Across the four MVPs:

- **MVP 1** establishes the spine: `requests`, `request_types`, `statuses`, `dates`. Two foundational measures (`total_requests`, `open_requests`). Enough to support the descriptive question ("how many in 2024?").
- **MVP 2** adds the measures dashboards need: resolution time, response-time bands, category groupings. Computed dimensions on the fact (resolution duration, time-of-day). Enough to surface the four investigative angles visually.
- **MVP 3** adds Silver-driven dimensions — `dim_location` with neighborhood and coordinate — that the equity question fundamentally needs. PII redaction unlocks the neighborhood-level slice that bronze cannot provide cleanly.
- **MVP 4** rounds out the library: departments, SLA targets, response-time percentiles, time-of-day patterns, complaint resolution rates. Routing across multiple topics (operational, resident-facing, equity-focused).

### The demonstration

The MVP demonstrates how this kind of investigation can be done. An analyst with a real question — service equity, or any equivalent business problem — does the work in an Oxygen-powered Knowledge Product, in conversation, in an hour, with their subject-matter expertise carrying the day instead of their SQL fluency. The Working Backwards example is the *shape* of every session the platform supports, not a single canned story.

---

## 7. Disciplines that hold the work together

The architectural decisions above don't enforce themselves. A handful of disciplines run across the entire build and keep it coherent.

### Configuration over custom code

Oxygen is a declarative platform. The build uses YAML and SQL configuration wherever Oxygen supports it; custom code (Python scripts, custom agents, hand-written application logic) is the exception, reserved for places Oxygen does not yet have a native primitive. Every time custom scaffolding goes in, it's tagged for replacement when the Oxygen-native path catches up. See [Component Trajectory](#4-component-trajectory) above.

### Builder Agent as the construction interface

From MVP 2 onward, the construction interface for the analyst is Builder Agent. The analyst describes what they want; Builder Agent reads, modifies, and iterates on the project files. Hand-writing `.view.yml`, `.app.yml`, or `.agent.yml` is fallback, not default. This is what protects the *ownership* phase of the emotional arc — the analyst's conversational instructions are what produce the artifact.

### Airlayer is the single semantic source of truth

Every metric the analyst sees — in chat, on the portal, in dashboards, in Slack, in any future surface — is defined exactly once, in the semantic layer's `.view.yml` files. Never hardcoded in SQL queries, never duplicated in app configs, never restated in agent prompts. This is the primer's defense against "metric drift," and it is non-negotiable. The `/metrics` page is auto-generated from the YAML; if a measure isn't in the semantic layer, it doesn't exist on the portal.

### Verification gates for live-functional claims

Standards-completion claims fall into two categories:

- **Static-artifact claims** (a file exists, a description is in `schema.yml`, a config compiles): can be ticked once and stay ticked, anchored to a commit.
- **Live-functional claims** (the chat answers correctly, the `/trust` page is green, `./run.sh` completes end-to-end): must reference a re-runnable verification command, and **must be re-verified in the sign-off session** for each MVP — not inherited from earlier ticks.

State-gated routes (anything that requires a user account, an org, or runtime state to function) require either a fresh walkthrough or an explicit reinterpretation note. This discipline exists because live-functional claims decay; point-in-time verification doesn't persist. See [CLAUDE.md](CLAUDE.md) "Verification gates for `[x]` ticks" for the operational rule.

### Component Trajectory reviews at every plan kickoff

Every plan begins with a check against the Oxygen changelog. New native components are evaluated against existing custom scaffolding. When the native option has caught up, migration is scoped explicitly — not deferred indefinitely. Custom scaffolding has an expiration date; the question is when, not whether.

### The compass

Every architectural, configuration, and scope decision in this guide passes through MVP.md's compass — *does this protect the path through the emotional arc, or does it leak friction back in?* — before it lands. Layer-by-layer choices in §3, migration triggers in §4 Component Trajectory, MVP-by-MVP construction in §5, scope deferrals in §8: all of them. The compass is articulated in MVP.md; here, it is the operational test.

---

## 8. Scope boundaries

What this project deliberately is **not**, and why. Each boundary protects the analyst arc by keeping the work focused on what produces "you have to try this."

**Not a resident-facing dashboard.** The protagonist is the analyst, not the resident. A resident-facing site would simplify away the SQL, the row counts, and the limitations — exactly the surfaces that produce trust for the analyst. An `/about` page and resident-oriented framing are deferred indefinitely; they belong to a different project.

**Not a multi-city template.** The Somerville 311 specificity is the point. Real data, real city, real stakes. A generic "311 analyzer" would be a worse demonstration of Oxygen because it would necessarily be shallower. Other cities adopting this pattern is a downstream consequence, not a build goal.

**Not a chat-only demo.** The primer's whole frame is that Knowledge Products depend on the full pipeline — ingestion, warehouse, transformation, semantic layer, agents, sharing. A chat-only demo would prove only the surface. This project demonstrates Oxygen unblocks every analyst workflow stage, not just the last one.

**Not predictive or prescriptive analytics.** The primer names four maturity stages; this project commits to Descriptive (MVP 1) and Diagnostic (MVPs 2-3). Predictive and Prescriptive require modeling capabilities and stakeholder relationships this project doesn't claim. Service equity is investigated, not predicted.

**Not a multi-tenant SaaS.** Single deployment, single dataset, single team. Multi-tenant readiness is a watch-item (MVP 4 may need shared knowledge product surfaces for evaluation teams), not a primary commitment.

**Not a replacement for the analyst.** The platform amplifies expertise; it does not substitute for it. SQL fluency, domain knowledge, judgment about what question to ask next — these become *more* valuable in an Oxygen session, not less. The build deliberately avoids framings that suggest automation of the analyst's role; the analyst is the protagonist, and protagonists don't get automated.

---

## 9. Glossary

Terms used in this build, anchored to the primer and Oxygen documentation where applicable.

**Knowledge Product** — *(primer)* A data product designed for a specific decision, not just a data display. Built from the full pipeline (ingestion through sharing), not just one layer. A dashboard *can be* a Knowledge Product; a dashboard *isn't automatically* one.

**Working Backwards** — *(primer)* The strategy of starting from the business decision and working back to the data, rather than starting from available data and discovering what it can support. Defines: business problem → hypothesis → Knowledge Product → data.

**Knowledge Hierarchy of Needs** — *(primer)* The five-level dependency stack for analytics platforms: Security (I) → Quality (II) → Reliability (III) → Usability (IV) → Coverage (V). Compromising a foundational layer invalidates everything above it.

**Analytics Maturity Lifecycle** — *(primer)* Descriptive ("what happened?") → Diagnostic ("why?") → Predictive ("what will?") → Prescriptive ("how to make it happen?"). This project covers Descriptive and Diagnostic.

**Medallion Architecture** — *(primer)* Bronze (raw mirror) → Silver (cleaned and standardized) → Gold (business-ready). The dbt project follows this. Silver lands in MVP 3.

**Metric Drift** — *(primer)* The pathology where the same metric name means different things in different tools because no single source of truth exists. The semantic layer prevents it.

**Extreme trustability** — *(project)* The bar this project commits to for the analyst experience. Every answer hands over the receipts — SQL, row count, citation, limitations — so the analyst verifies without spot-checking the platform.

**Trust contract** — *(project)* The agent's response shape. Every reply includes row count, answer, citations, and known limitations from the registry. Enforced today by system instructions; convergent with Oxygen's native Verified Queries surface.

**Limitations registry** — *(project)* The first-class institutional-knowledge layer. Markdown files with YAML frontmatter at `docs/limitations/`, surfaced by the agent and the `/trust` page when queries touch flagged areas. Caveats are artifacts, not footnotes.

**Verified Queries** — *(Oxygen)* Pre-written `.sql` files registered with the platform; the agent executes them as-is when a user's question matches, bypassing LLM generation. Results badged "Verified" in the UI. Native trust signal layered onto the trust contract.

**Airway, Airhouse, Airform, Airlayer, Airapp, Airtraffic, AirAgent** — *(primer / Oxygen)* The forward-looking per-layer product names in Oxygen's modular stack: Ingestion (Airway), Warehouse (Airhouse), Transformation (Airform), Semantic Layer (Airlayer), Business Intelligence (Airapp), Observability (Airtraffic), Analytics Agent (AirAgent). Public availability varies; see [Component Trajectory](#4-component-trajectory).

**Builder Agent** — *(Oxygen)* The project-file copilot. Reads, writes, and iterates on `.view.yml`, `.app.yml`, `.agent.yml`, and other workspace files through conversation. The construction interface from MVP 2 onward.

**Answer Agent** — *(Oxygen)* The standard chat agent type, configured via `.agent.yml`. Uses `execute_sql` and `semantic_query` tools to respond to analyst questions.

**Routing Agent** — *(Oxygen)* Dispatches user questions to the right specialized agent or workflow using vector embeddings. Lands in MVP 4 when the semantic layer warrants routing.

**Data Apps** — *(Oxygen)* Declarative dashboards via `.app.yml`. Built through conversation with Builder Agent from MVP 2.

**The arc / emotional arc** — *(project, defined in [MVP.md](MVP.md))* The experiential progression an analyst moves through in a session: relief → momentum → ownership → pride → sharing. Bridges "contribution magnified" to "you have to try this." Referenced throughout BUILD.md as the experience every layer is constructed to deliver.

**The compass** — *(project, defined in [MVP.md](MVP.md))* The test every architectural, configuration, and scope decision passes: *does this protect the path through the emotional arc?* Operationally applied in §7 of this guide.

---

*This guide is the durable construction logic. For progress, status, or what's built today, see [TASKS.md](TASKS.md) and [LOG.md](LOG.md). For strategic positioning, see [MVP.md](MVP.md). For done-done criteria, see [STANDARDS.md](STANDARDS.md). For operational instructions, see [CLAUDE.md](CLAUDE.md) and [SETUP.md](SETUP.md).*
