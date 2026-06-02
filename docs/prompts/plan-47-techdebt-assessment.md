# Plan (oxygen-mvp) — Tech-Debt Assessment & Reduction Plan (INVESTIGATE & REPORT — do not refactor)

**Repo:** `ironmonkey88/oxygen-mvp`
**Branch:** `claude/plan-NN-techdebt-assessment` (assign the next plan number)
**Mode:** **Report-first.** Measure, analyze, and propose a prioritized debt-reduction plan. **Make no code changes to behavior in this plan** — the output is a findings doc + a proposed plan for Gordon to approve. Refactoring happens in a *later, approved* plan, not here.

---

## Phase 0 — Write this prompt to the repo (first commit)
Write this prompt verbatim to `docs/prompts/plan-NN-techdebt-assessment.md` on a new branch `claude/plan-NN-techdebt-assessment`. First commit on the branch. (MCP-direct-commit path is paused; Code owns prompt-file creation.)

---

## Why this plan exists
oxygen-mvp is ~7,300 lines of Python across 31 files, 28 dbt models, 299 commits / 46 plans. A structural review (from Chat) found: a **well-tested dbt/data layer** (90 not_null, 39 unique, 28 accepted_values, 17 relationships, + a singular guardrail) and **codified standards** (STANDARDS.md) — but two debt signals: **(1) no Python unit tests and no CI**, and **(2) no Python dependency management** (no root requirements.txt / pyproject / lockfile). The Python weight is concentrated in `generate_*_page.py` scripts (largest: 757, 580, 560, 506 lines), several Somerville-specific.

Critical nuance: **the data layer being well-*tested* does not mean it is well-*architected*.** A 46-plan incrementally-built warehouse risks "parallel play" — each plan adding models/pipelines in isolation without graph-level coherence. This plan assesses that explicitly (Phase 4) alongside the Python.

This is the right size to address debt: large enough that duplication and graph drift have likely set in, small enough to still refactor safely. The goal of *this* plan is to measure precisely and propose — not to fix.

---

## Phase 1 — Quantify duplication in the page-generation scripts, through a DRY-vs-WET lens
The hypothesis to **confirm or refute with evidence**, not assume: the ten-ish `generate_*_page.py` scripts share a common skeleton (DuckDB connect → query → render HTML chrome/nav/trust-footer → write to docroot) repeated per file, and could be substantially deduplicated into a shared module.

**Apply the DRY-vs-WET test explicitly — do not default to "dedupe everything."** The correct question is NOT "do these look similar?" but "**when one page's requirements change, do the others genuinely need to change too?**":
- Code that has **one reason to change** (DB connection, output-path logic, nav chrome, trust footer, error handling) → genuinely shared → DRY it into a helper.
- Code that has **independent reasons to change** (each page's specific queries and layout) → leave WET *as a deliberate choice*, and say so. A little duplication is far cheaper than the wrong abstraction.

Deliverables:
- List every `generate_*` / page-rendering script with LOC.
- Classify each chunk as one-reason-to-change (DRY candidate) vs independent-reason (keep WET). Quantify boilerplate vs page-specific.
- Estimate realistic post-dedup line count for the *plumbing* extraction only — not a fantasy "collapse everything" number.
- **Explicitly defend the WET parts.** A report saying "these 6 share plumbing worth extracting; these 4 are legitimately distinct and should stay separate" is the goal. Name the god-function/flag-soup risk that comes from forcing distinct pages through one framework.
- Determine whether `rendered_page.py` (560 lines) is *already* the intended shared helper. If so, the real finding may be "the helper exists but N scripts bypass it" — a cheap fix, not a new abstraction.

## Phase 2 — Test & CI gap assessment
- Confirm the Python test coverage gap (the dbt layer is tested; the Python isn't). Identify which Python modules are highest-risk-if-broken (the ones in the run.sh critical path, the trust-page generator, anything touching the F6 contract).
- Assess what a *minimum viable* Python test layer looks like: which modules need real unit tests vs which are adequately covered by the existing "rendered-page valid-HTML" check.
- Note the absence of CI (`.github/workflows`) and what a lightweight gate would cover (py_compile, the rendered-page checks, dbt build/test, `oxy validate`).
- **Tie-in to methodology R1** (test-the-contract, not just components): does oxygen have *any* end-to-end "agent answers a real query" gate, or only component checks? Report it. (This is also the R1 propagation item from the methodology whiteboard — fold the finding into both.)

## Phase 3 — Dependency hygiene
- Confirm there's no Python dependency declaration in oxygen. Produce the *actual* dependency set (what's imported across all .py) and propose a pinned `requirements.txt` — **cross-reference stack-in-a-box's already-pinned requirements.txt** (it pinned dlt/dbt/duckdb/ulid during extraction; reuse those pins where they match).
- Flag any version-sensitive imports (the python-ulid 1.x→3.x break is a known one).

## Phase 4 — Data-layer debt: dlt pipelines + dbt graph (first-class, NOT skipped)
For a data warehouse, the debt that hurts most long-term lives in the pipelines and the model graph — not the page generators. **Good dbt test coverage (which oxygen has) does NOT imply a well-architected graph.** Tests check "is the data correct"; they say nothing about "is the DAG well-shaped." Assess structure and lineage, not just the test count.

**The governing lens: is this a coherent "team effort" or "toddlers in parallel play"?** A 46-plan codebase built incrementally is at real risk of each plan having added its models/pipelines in isolation — N corners each solved their own way — without anyone stepping back to ask "is this still ONE coherent project?" Look specifically for that smell.

**dbt graph assessment:**
- **Layer discipline:** are bronze→silver→gold boundaries clean, or do models reach across layers (e.g. gold refs bronze directly, staging models doing business logic)?
- **Grain consistency:** is grain declared and consistent, or does it drift per model/author?
- **Composition vs duplication:** are there N different ways to compute the same measure? Logic copy-pasted across models that should share a macro or an upstream model? Multiple models that are near-dupes?
- **Materialization sanity:** are things tables that should be views/ephemeral, or vice versa? Any needlessly expensive rebuilds?
- **DAG shape:** fan-out joins, models doing too much, overly-deep or tangled lineage, orphan models.
- **Naming/convention coherence:** consistent prefixes, one naming scheme, or per-plan drift.
- **Macro reuse:** is shared SQL logic factored into macros, or re-expressed inline everywhere?

**dlt pipeline assessment:**
- Do the pipelines share a common pattern, or was each source handled ad hoc (parallel play at the ingestion layer)?
- Incremental/merge-key correctness: are merge keys right, or full-refresh where incremental is needed?
- Schema/type handling: brittle assumptions, silent coercion, untested extraction.
- Error handling + retry consistency across pipelines (note: stack-in-a-box added backoff-retry — does oxygen have an equivalent, or does each pipeline differ?).

**Output:** a coherence verdict for the data layer — "team effort" vs "parallel play," with specific examples — and prioritized structural fixes. This is likely the highest-value section of the whole assessment for someone deciding whether to *build on* (or clone) oxygen, because graph debt is exactly what a clone inherits wholesale and what makes a warehouse miserable to extend.

## Phase 4b — Broader code debt scan (lighter touch)
- Dead/Somerville-specific code that's entangled vs cleanly separable (relevant to any future extraction or personal fork).
- TODO/FIXME/HACK density; modules the LOG.md history flags as known-shortcut.
- Python coupling hotspots: what depends on what, where a change ripples. (Structural read is fine, no tooling required.)

## Phase 5 — Produce the prioritized reduction plan (the deliverable)
Write `docs/design/TECHDEBT_ASSESSMENT.md` containing:
- The measured findings from Phases 1–4b (with real numbers, not estimates-from-memory).
- The **data-layer coherence verdict** (Phase 4): team-effort vs parallel-play, with specific examples, for both the dbt graph and the dlt pipelines. Treat this as a headline finding, not an appendix.
- A **prioritized, sequenced** reduction plan with effort sizing per item, ordered by the correct dependency: **dependency pinning and a minimal Python test layer come FIRST** (you cannot safely refactor untested code), **then** structural/data-layer fixes and the page-generator dedup, **then** CI. State this ordering explicitly and why.
- For the page-gen dedup: a concrete proposed shape (shared helper interface, which scripts adopt it, which stay WET-by-choice) — a *proposal* for Gordon to approve, with the DRY-vs-WET reasoning and over-abstraction risk called out.
- For the data layer: proposed structural fixes ranked by build-on-ability impact, distinguishing "correctness is fine, structure needs work" from anything that affects data correctness.
- A clear "what NOT to do" section (don't abstract genuinely-distinct pages; don't refactor before tests exist; don't change data-layer *behavior* while restructuring — preserve the tested correctness).

## Phase 6 — Findings + PR
- Commit `TECHDEBT_ASSESSMENT.md`, update LOG.md / TASKS.md / session handoff.
- Open a PR. The PR description summarizes: the dedup opportunity (quantified), the test/CI gap, the dep-hygiene fix, and the proposed sequence — for Gordon to approve as one or more follow-up plans.

---

## Out of scope (critical)
- **No refactoring, no behavior changes, no file restructuring in this plan.** Investigate and propose only — across Python AND the data layer.
- The dbt/data layer is **assessed structurally** (Phase 4) but its **tested correctness must be preserved** — propose structural improvements, never changes that would alter the data the tests validate.
- No touching stack-in-a-box (cross-reference its requirements.txt read-only).
- Do not begin any approved reduction work until Gordon ratifies the plan.

## Done means
`TECHDEBT_ASSESSMENT.md` exists with measured (not assumed) findings: a DRY-vs-WET-reasoned page-gen dedup proposal that defends the WET parts, a test/CI gap analysis tied to methodology R1, a proposed pinned requirements.txt, a **data-layer coherence verdict (dbt graph + dlt pipelines: team-effort vs parallel-play) with structural fixes**, and a prioritized + correctly-sequenced reduction plan (tests/deps before any refactor) — all as proposals for Gordon's approval. PR open. Zero behavior changes.

---

## Execution notes (Code, plan-47)

Two completeness gaps were resolved with Gordon before execution (Session of 2026-06-02):

1. **EC2 read-only measurement is authorized.** Phase 3 (dep pins) and Phase 4 (dbt graph) are grounded in EC2 state: `pip freeze` for the ground-truth dependency set, and `dbt parse` / `dbt ls` / `manifest.json` + `run_results.json` timings for the graph verdict — all read-only, respecting DuckDB run-order locking. `pip freeze` on EC2 is the authoritative pin source; stack-in-a-box's `requirements.txt` is the cross-reference (not the other way round).
2. **Methodology R1 handling.** The shared `METHODOLOGY.md` whiteboard (home-of-record in stack-in-a-box) is **not yet instantiated in oxygen-mvp**. Its own sync governance is *Code-proposes / human-approves, never auto-committed*. So in this report-only plan, the R1 finding (does oxygen have an end-to-end "agent answers a real query" gate?) is **reported inside `TECHDEBT_ASSESSMENT.md`** and framed as the R1 propagation item; instantiating `METHODOLOGY.md` in oxygen-mvp + formally closing R1 is **recommended as a human-ratified follow-up**, not done here.

Plan number assigned: **47** (Plan 46 latest done; 41/42/45 reserved/in-flight).
