# Oxygen MVP

# Strategic Analysis: Public-Facing MVP for Oxy.tech

## Executive Justification

This project initiates a public-facing Minimum Viable Product (MVP) leveraging **Oxygen's High-Performance Data Engine** to process non-deterministic, live data (Somerville 311 service requests). In a market skeptical of "gold-copy" vendor demos, using real-world data provides empirical proof of **Agentic Ops** and high-concurrency performance. By moving beyond static visualizations to a functional **chat-based utility**, Oxy reduces the "imagination gap" for technical prospects by demonstrating a completed, production-ready implementation.

This MVP is built by Gordon Wong (Oxy team) acting as the voice of the ideal Oxygen customer — an analytics expert evaluating Oxygen as a next-generation platform. The work doubles as pre-sales engineering, product evangelism, and product-management feedback to the Oxy team.

## Strategic Positioning

### The protagonist

The protagonist of this MVP is the data analyst. Not the executive who reads the dashboard. Not the IT director who buys the platform. The analyst — the person whose job is to answer questions with data, who has deep subject-matter expertise but works in the shadow of technical constraints they didn't choose.

### The constraint

Producing Knowledge Products requires a chain of capabilities: getting the data, making it queryable, making it understandable, making questions easy to ask, making answers easy to share. Today's analyst hits friction at every stage. They wait on a data engineer for ingestion, on an analytics engineer for modeling, on a BI developer for dashboards. By the time they can act on their subject-matter expertise, the question has moved on.

Oxygen unblocks every stage. Same analyst, same expertise, dramatically less friction in front of them.

### The desired outcome

The analyst leaves an Oxygen session having done in an hour what used to take a week. They feel their contribution magnified — their subject-matter judgment carrying weight that would previously have been spent debugging joins. They tell their friends: *"you have to try this."*

That sentence is the goal of this MVP.

### The experience

The desired outcome is produced by a specific experience the analyst has in a session. Not a feature, not a metric, but a sequence of phases the platform earns by behaving a certain way at each step:

1. **Relief.** The first verifiable answer lands with SQL, row count, and citation. The analyst sees they don't have to spot-check the platform. It isn't asking them to trust it — it's showing its work. Shoulders drop. Relief is impossible without extreme trustability; the bar exists to make this phase happen.

2. **Momentum.** The second question comes faster than the first. The third faster still. The analyst chases instincts they'd normally suppress because the cost of chasing was too high — debugging joins, waiting on a data engineer, second-guessing a metric definition. Curiosity floods back. A conversational interface backed by a stable semantic layer is what makes this phase happen.

3. **Ownership.** Halfway in, the answer is *theirs*. Their subject-matter judgment found it, their question framed it, the platform kept up. They're producing their own work, not consuming a vendor's output. This is the inflection — the analyst stops thinking *about* the platform and starts thinking *through* it.

4. **Pride.** They imagine showing this to the colleague who keeps asking for things the BI team won't build. They imagine being the person who had this first. The analyst becomes an advocate before the session ends.

5. **Sharing.** The sentence comes out. They tell their friends.

The arc is the bridge between "contribution magnified" and "you have to try this." It is what the project commits to producing — not a single feature, but a path. Extreme trustability is the bar because anything less breaks the first phase, and without the first phase none of the rest happens. Every architectural, design, and scope decision in this project answers to whether it protects the path through the arc or leaks friction back in.

### The compass

"You have to try this" is the cleanest test the project has because it cannot be gamed. You can't ship a feature that produces the sentence; you can only build the whole experience well enough that the sentence happens on its own. The sentence is also the only externally-checkable signal that the experience landed — if an analyst doesn't tell a colleague, the project hasn't done its job, regardless of what any internal metric says.

That makes the sentence a compass for every decision the project makes. Architectural, design, and scope choices all pass through the same question: *does this protect the path through the emotional arc, or does it leak friction back in?* Convenience is not the goal; *agency* is. Convenience is silent; agency produces sharing. The compass is also a deferral test — anything that doesn't protect the arc gets deferred, regardless of how much engineering value it has on its own. Scope discipline runs through the compass.

### The audience

Three concentric circles:

1. **Prospective Oxygen customers** — analysts, analytics leaders, data platform owners evaluating Oxygen against the modern data stack.
2. **The broader analytics community** — practitioners encountering a real Knowledge Product built on a recognizable dataset, with public materials they can learn from.
3. **The Oxy team itself** — using the MVP as a forcing function to identify product gaps, sharpen positioning, and ground feature work in real customer-shaped use.

## The opening note

Before the analyst asks a question, they land somewhere. The public-facing portal is that somewhere — the first impression of the project, the first surface the analyst sees, the opening note of the experience the project commits to creating.

The portal's job is recognition before articulation. An analyst lands on it and immediately recognizes a serious knowledge platform: familiar in shape because the surfaces it carries — *Data dictionary, Metrics, Trust* — match what mature analytics teams always wished they had; impressive in execution because every surface earns its place. The stats bar showing "10 documented limitations" signals a working platform without saying so. The asset cards each link to something live. The stack table names tools without explanation because the audience already knows them.

The portal demonstrates rather than articulates. It does not carry the language of the emotional arc, the compass, or the project's mission statement. Putting those on a public surface would break the spell — public-facing analytics surfaces don't talk about their own framing. The portal demonstrates the project's commitments by *being* one of them; this doc and the Build Guide are where the commitments are written down.

That separation is load-bearing. It means the portal is tuned by analyst reaction, not specified from a strategy doc. The Build Guide says *we construct a public portal.* This doc says *what the portal is for.* The portal itself is iteratively refined against the reaction it produces — the analyst seeing the surface and thinking *"oh, these people get it."*

The opening note also carries the relief phase of the arc forward before the analyst has even asked a question. The portal's trustability signals — the limitations registry visible, the metrics page auto-generated from the semantic layer, the `/trust` page green or red on the latest pipeline run — tell the analyst that the platform will continue to show its work after they engage. That preview is what makes the rest of the arc reachable.

## Primary Objectives

**For the analyst.** Make every stage of producing Knowledge Products dramatically easier — getting the data, making it queryable, making it understandable, making questions easy to ask and answer, and making findings easy to share. The analyst leaves an Oxygen session having done in an hour what used to take a week, and tells their friends: *"you have to try this."*

**For Oxy.** Four outcomes flow from the above:

1. **Demonstration of compounding value.** A real Knowledge Product built end-to-end on a recognizable dataset, with no custom platform code. Prospects see Oxygen as the system that unblocks every analyst workflow stage, not a chat-only tool.
2. **Public credibility.** Establishes Oxy as a serious entrant in modern analytics tooling by shipping a working example on a publicly understood dataset.
3. **Product feedback loop.** Live lab for observing how analyst-shaped users interact with Oxygen — Builder Agent, Semantic Layer, Data Apps, Verified Queries — and surfacing friction directly to the Oxy product team.
4. **Battle-testing.** Exercises Oxygen against the entropy of real public data, unpredictable user questions, and non-deterministic agent behavior. Hardens the platform under real load.

## The Knowledge Product Pipeline

Every Knowledge Product depends on a stack of underlying capabilities. Oxygen delivers all of them in a single, integrated platform — replacing what would otherwise be five-to-seven vendor integrations. The pipeline below maps the analyst's workflow to Oxygen's component surface.

| Workflow stage | Primer layer | Oxygen component |
|---|---|---|
| Get the data | Ingestion | Data sources (DuckDB, Postgres, Snowflake, BigQuery, etc.) |
| Make it queryable | Warehouse + Transformation | SQL modeling (dbt-style), SQL IDE |
| Make it understandable | Semantic Layer + Observability | Entities, Dimensions, Measures, Topics, Views; Ontology graph; Verified Queries; Observability metrics |
| Make asking easy | Knowledge Products (chat) | Agents (Answer, Routing, Agentic), Deep Research, Builder Agent |
| Make sharing easy | Knowledge Products (apps) | Data Apps, Slack integration, MCP server, A2A protocol |

Every layer above is shipping production functionality in Oxygen today. The MVP exercises all of them on Somerville 311 data, using configuration rather than custom code wherever possible.

## Implementation Roadmap (Nested MVPs)

Oxygen's modular architecture means analytics teams adopt incrementally. This MVP demonstrates that path: dlt + DuckDB + dbt Core for the upstream pipeline today, Oxygen for everything from the Semantic Layer downward. As Oxygen ships production-mature components for ingestion, warehouse, and transformation, the MVP migrates onto them. Best-of-breed today, Oxygen-native at the destination.

Four nested MVPs, each delivering a complete Knowledge Product on Somerville 311 data, each adding maturity along the analyst workflow. Built single-developer-with-Claude-Code, configuration over custom code, end-to-end working at every step.

### MVP 1: First Knowledge Product
*The analyst can ask questions of trustworthy data and get verifiable answers.*

| | |
|---|---|
| **Primer layers** | Ingestion + Warehouse + minimal Semantic Layer + Knowledge Product (chat) |
| **Oxygen components** | Semantic Layer (entities, dimensions, measures, topics, views), Answer Agent |
| **Maturity stage** | Descriptive |
| **Analyst outcome** | Asks a question in natural language, gets a verifiable answer with SQL, row count, and citation. Trusts the answer enough to put it in a report. |
| **Demo moment** | "How many 311 requests in 2024?" → 113,961, rendered with the SQL that produced it. |

### MVP 2: Visual Knowledge Products
*The analyst can build dashboards through conversation.*

| | |
|---|---|
| **Primer layers** | + Knowledge Product (apps) |
| **Oxygen components** | + Data Apps, Builder Agent |
| **Maturity stage** | Descriptive → early Diagnostic |
| **Analyst outcome** | Describes the dashboard they want; Builder Agent assembles it. Iterates by conversation, not by writing YAML. |
| **Demo moment** | "Show me service request volume by neighborhood, monthly, with a drill-down on top categories." Dashboard appears, fully configured, in chat. |

### MVP 3: Governance and Trust
*The analyst trusts the underlying data without having to verify it themselves.*

| | |
|---|---|
| **Primer layers** | + full Transformation, + Observability |
| **Oxygen components** | + Verified Queries, Observability metrics, agent testing framework (LLM-as-judge), full medallion architecture |
| **Maturity stage** | full Diagnostic |
| **Analyst outcome** | Sees verified-query badges on every reliable answer. Reaches root cause through guided exploration. Confidently shares findings without spot-checking the agent. |
| **Demo moment** | "Why did sidewalk repair requests spike in March?" → agent narrows from category to neighborhood to date range, each step verified, with the supporting query history one click away. |

### MVP 4: Semantic Depth and Sharing
*The analyst can package and share their findings, and others can build on them.*

| | |
|---|---|
| **Primer layers** | full Semantic Layer + Knowledge Product (sharing) |
| **Oxygen components** | + expanded Topics and Views library, Slack integration, A2A protocol, MCP server, Looker integration |
| **Maturity stage** | Diagnostic |
| **Analyst outcome** | A library of trusted metrics the team uses across surfaces (chat, Slack, BI tools). Findings shared as live, queryable artifacts — not screenshots. |
| **Demo moment** | Slack: "@oxygen what's our SLA performance this quarter?" → answer in-thread, with a link to the live dashboard, shareable to the next analyst who picks up the work. |

## Implementation & Data Volume Notes

- **Somerville 311 Volume:** ~1.16M requests across ~10 years of historical data, averaging ~117k/year. Bronze layer refreshed from the Somerville SODA endpoint.

- **Storage Architecture:** DuckDB on the EC2 instance is the source of truth — server-side, queried by Oxygen. DuckDB-Wasm is on the roadmap for the analyst-facing surface, where running queries in the browser delivers lightning-fast performance without round-tripping to the server.

- **Dev Strategy:** Builder Agent configures Oxygen's declarative components — Semantic Layer entities, dimensions, measures, topics, views, agents, and Data Apps — through conversation. The analyst describes what they want; Builder Agent reads, modifies, and iterates on the project files. Configuration over custom code is the default; imperative work is the exception.

- **Component Trajectory:** Architecture evolves with Oxygen. As production-mature components ship for ingestion, warehouse, and transformation, the project migrates onto them. Current upstream pipeline (dlt + DuckDB + dbt Core) is best-of-breed today; Oxygen-native at the destination.

## Challenges and Constraints

Strategic risks the project is watching:

- **Platform velocity.** Oxygen ships fast. Capabilities that didn't exist at kickoff (Builder Agent, multi-workspace mode, Magic Link auth, Verified Queries, Data Apps maturity) now reshape the roadmap. This is a feature, not a bug — but it requires periodic review of custom scaffolding for replacement opportunities, and willingness to deprecate work that newer Oxygen components supersede.

- **Component maturity.** The MVP depends on Oxygen components at varying maturity levels. The Semantic Layer and Answer Agent are production. Builder Agent, Verified Queries, and Data Apps are recent and evolving. Migration of upstream layers (ingestion, warehouse, transformation) onto Oxygen waits on those components reaching production maturity.

- **Demonstration surface.** The project needs to reach prospects, not just live on a private deployment. Public-facing access — authentication, exposure strategy, audience curation — is a continuous design question, not a one-time configuration.

- **Multi-tenant readiness.** As the demo audience expands beyond individual analysts to evaluation teams and prospect organizations, multi-workspace mode, member roles, and shared knowledge product surfaces become load-bearing. Right-sizing this against actual demand is ongoing.

- **Evangelism balance.** The project serves multiple goals — analyst demo, pre-sales reference, product feedback, public credibility. Scope discipline is required to avoid serving one goal at the expense of the others.

## Working Backwards: A Worked Example

The primer prescribes Working Backwards as the strategy for building Knowledge Products: start from the decision, work back to the data. The Somerville 311 MVP, walked through that framework:

### Business Problem

*Are 311 service requests being resolved fairly across Somerville's neighborhoods?*

Service-delivery equity is one of the most consequential questions a city government, journalist, or researcher can ask of public data. The question is unambiguous, the stakes are real, and the answer changes how resources are allocated and how the city is held accountable.

### Hypothesis

*There are measurable, non-random differences in how 311 requests are handled across neighborhoods — in volume, resolution rate, resolution time, or the mix of services delivered — and those differences are large enough to inform policy.*

This is a multi-angle hypothesis on purpose. An analyst investigating equity doesn't know in advance which dimension matters most. Volume disparities might reflect access (some neighborhoods report less because they trust the system less). Resolution time might reveal where the city is meeting its SLAs. Resolution rate might surface categories where reports go nowhere. Service mix might show different neighborhoods getting fundamentally different attention. The hypothesis is broad because the analyst's job is to narrow it.

### Knowledge Product

A conversational interface backed by trustworthy data, where the analyst can pose the umbrella question and follow the evidence through whichever angle the data surfaces. Every answer carries the SQL that produced it, the row count it returned, and a citation back to the source — so the analyst can verify and publish without spot-checking the platform.

The Knowledge Product is *not* a pre-built dashboard answering one of the angles. Pre-built dashboards anticipate questions. This Knowledge Product anticipates the analyst's curiosity instead.

### The Data

Somerville's public 311 service request dataset: ~1.16M requests across ~10 years, refreshed from the city's SODA endpoint. Each row carries a case category, a neighborhood and coordinate, an open timestamp, a close timestamp, and a status. From those columns, every angle of the hypothesis is testable.

### The Demonstration

The MVP demonstrates how this kind of investigation can be done. An analyst with a real question — service equity, or any equivalent business problem — does the work in an Oxygen-powered Knowledge Product, in conversation, in an hour, with their subject-matter expertise carrying the day instead of their SQL fluency.
