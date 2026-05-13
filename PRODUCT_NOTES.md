# PRODUCT_NOTES.md — Exploratory Product Notebook

## Purpose

**Is:** an exploratory notebook for product ideas surfaced during MVP work.
Loose, additive, low-ceremony. Captures thinking before it matures into
roadmap. Entries here are hypotheses, not commitments.

**Isn't:** roadmap, vision-as-authority, or scope. [MVP.md](MVP.md) and
[BUILD.md](BUILD.md) remain the operational authorities; this doc informs them
but doesn't govern them.

**Reading guidance:** read for orientation and inspiration; do not plan
against it. If a notebook idea and MVP.md or BUILD.md disagree, the
authoritative doc wins. Anything here that lands as a real commitment moves
into MVP.md or BUILD.md and gets a pointer recorded below.

**Lifecycle:** entries are *exploratory* by default. They can move to:
- *queued for plan* — a plan is being scoped against the idea
- *committed* — the idea has landed in MVP.md or BUILD.md; pointer recorded
- *superseded* — a later idea replaced this one; pointer to the successor

Status is tracked on each entry's `Status:` line. Dated `Last updated:` line
makes drift obvious.

---

## Entry 1 — Knowledge-graph expansion

The analytics agent routes unanswerable questions to a chief-researcher
agent that finds and brings in missing data sources (e.g. ACS demographics
by ward, crime statistics, weather data). Today this is human-in-the-loop:
Gordon recognizes the gap during a Chat session, decides whether it's worth
pursuing, and tells Code to ingest the new source. The "ingest a new data
source" step is already operationalized via the dlt pipeline pattern — see
[dlt/somerville_311_pipeline.py](dlt/somerville_311_pipeline.py) as the
template.

The agentic version would have the analytics agent surface the gap
explicitly ("I can't answer this without crime data; should I request it?")
and route to a specialized agent that handles source discovery, schema
mapping, ingestion, and integration into the semantic layer. HITL approval
lives at the "bring in this new data source" boundary — the same shape as
Builder Agent's per-file approval, scaled to a higher-stakes commitment.

The trust contract would extend to include data provenance: where did this
dataset come from, when was it added, who/what brought it in, what trust
signals does it carry (or fail to carry). The limitations registry already
has the shape for this — institutional knowledge with YAML frontmatter —
and would extend naturally to include provenance entries.

Likely lands in MVP 5+ territory; not yet on the four-MVP roadmap. Connects
to MVP 4's Routing Agent (Oxygen primitive that dispatches between
specialized agents — currently scoped for routing between answer agents on
different topics, but the same primitive supports operational routing).

Status: exploratory
Last updated: 2026-05-13

---

## Entry 2 — Component-graph expansion

An architect-shaped agent does build-vs-borrow analysis when new platform
functionality is needed (data profiling, DQ testing, observability, etc.).
Searches the open-source landscape, compares against current project
scaffolding, proposes adoption or build with a written rationale. BUILD.md
§7's Component Trajectory review at every plan kickoff is the
human-discipline version of this; the agentic version makes it a runtime
capability.

Today this is operational practice — Gordon and Claude evaluate options at
plan kickoffs. Extending it from "Oxygen-native replacements" (current §7
scope) to "broader open-source ecosystem" is a near-term human discipline
change, then eventually agentic.

Two concrete near-term applications already on the queue:

- **Data-inventory utility design.** Evaluate DataHub, OpenMetadata,
  ydata-profiling, Soda Core, Great Expectations' profilers, and LLM-based
  dataset summarization options before scoping the custom build. The
  utility itself (content-level enumeration of what the data contains, not
  column-level statistics) is queued; the build-vs-borrow analysis is the
  part this entry is about.
- **DQ test framework expansion at MVP 3.** Evaluate Elementary (dbt-native
  observability + DQ extension) as a Component-Trajectory candidate against
  the existing `admin.fct_test_run` + `/trust` page + `dq_drift_fail_guardrail`
  scaffolding. Elementary covers anomaly detection, freshness monitoring,
  test result tracking, and a UI; project scaffolding covers test results
  + drift guardrails + a custom trust surface. Worth a systematic
  comparison before MVP 3's DQ scope grows.

Status: exploratory
Last updated: 2026-05-13

---

## Entry 3 — Self-extension as the meta-pattern

Knowledge-graph and component-graph expansion share a single reflex: the
platform extends to meet questions it can't yet answer. The analytics agent
doesn't just answer questions about the data — eventually, it directs the
system's own growth in response to analyst demand.

Worth naming as a pattern even before either capability is built. May
eventually warrant changes to MVP.md (the analyst's Ownership phase in the
emotional arc would extend to include "the system grew to meet my question"
— a richer Ownership than today's "I built the dashboard"). May also
warrant changes to BUILD.md (self-extension as a first-class construction
principle alongside configuration-over-code, semantic-layer-as-single-source-of-truth,
etc.).

Not yet. The MVP doesn't depend on it; it would be over-commitment at this
stage. Naming it here keeps the pattern visible for when the capabilities
mature.

Status: exploratory
Last updated: 2026-05-13

---

## Entry 4 — The project as Oxy customer-feedback loop

Already named in [docs/retrospective/mvp1-lessons-learned.md](docs/retrospective/mvp1-lessons-learned.md)
under "Customer-shaped use carries customer-shaped context and produces
customer-shaped feedback." Each capability this project builds because
Oxygen doesn't yet ship it natively is a candidate primitive for Oxygen
itself.

Examples surfaced so far in MVP 1:

- The limitations registry pattern (institutional-knowledge layer with YAML
  frontmatter, surfaced via `/trust` and via agent context)
- The auto-generated `/metrics`, `/trust`, `/profile`, `/erd` portal
  surfaces (single source of truth → multiple analyst-facing views)
- Column profiling (`scripts/profile_tables.py` + `main_admin.fct_column_profile_raw`)
- The trust contract enforcement pattern in the Answer Agent (system
  instructions that demand row count, citations, limitations on every reply)

Forward candidates surfaced during MVP 2 scoping:

- A content-level data inventory utility (entry 2)
- An architect-agent for build-vs-borrow analysis (entry 2)
- A chief-researcher agent for data ingestion (entry 1)

Keeping these visible is part of the project's strategic value to Oxy,
independent of any single MVP deliverable. The multi-workspace wizard /
existing-DuckDB feedback from Session 25 was the first concrete instance of
this loop closing — feedback delivered, ticket filed.

Status: committed (project-strategic, not product-feature) — see [docs/retrospective/mvp1-lessons-learned.md](docs/retrospective/mvp1-lessons-learned.md)
Last updated: 2026-05-13

---

## Naming conventions

Used consistently from here forward; will appear in future MVP planning if
and when the capabilities mature.

- **Knowledge graph** — the surface of data sources, dimensions, measures,
  topics, and institutional knowledge (limitations registry, provenance)
  that the analytics agent reasons over. *Knowledge-graph expansion* (Entry
  1) names the agentic capability that grows this surface in response to
  unanswerable questions.
- **Component graph** — the surface of platform components (ingestion,
  warehouse, transformation, semantic layer, observability, DQ, agents,
  apps) the project assembles to deliver Knowledge Products.
  *Component-graph expansion* (Entry 2) names the agentic capability that
  evaluates and proposes new components.
- **Self-extension** (Entry 3) — the meta-pattern: the platform extends
  itself to meet questions it can't yet answer. Knowledge-graph expansion
  and component-graph expansion are two surfaces of the same reflex.
