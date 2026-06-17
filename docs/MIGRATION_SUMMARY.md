# Project Migration Summary — Oxygen Civic Analytics

**Purpose of this document:** This is a cold-start handoff for a fresh Claude Chat in a new account. It captures everything needed to resume the project, with emphasis on state that lives *outside* the repos (working agreements, in-flight status, deferred decisions, and the reasoning behind them). The repos are the source of truth for code and authority documents; this document is the source of truth for *how we work* and *where we left off*. Read it, then read the live repo files before reasoning — never reason from this summary alone where the repo can be checked.

*Snapshot date: 2026-06-17. The in-flight items below are accurate as of that date; the first action in any new session is to verify them against the live `LOG.md` in each repo.*

---

## 1. Who and what

**Operator:** Gordon — data and analytics executive (25+ years), interdisciplinary foundation in psychology, philosophy, cognitive science. Self-described ADHD that drives toward fundamentals and "deep grammar" (structural isomorphisms across domains) over surface detail. Not formally trained in software engineering; frequently arrives at established concepts independently. **Standing instruction: do not over-weight his phrasing — research the formalized literature and return the canonical version of the idea he is gesturing at.**

**Mission:** "I help people achieve their goals through better decisions." Applied across consulting/advisory and civic analytics, with a barbell model: consulting funds passion-driven civic projects. Oriented toward greenfield problems (civic analytics, SMB first-BI, personalized healthcare) where the AI cost-collapse opens previously unaffordable decision-support.

**The project:** A civic analytics platform advising Oxygen (oxy.tech), a friend's company building a three-layer data platform (infrastructure / world-model semantic-ontology layer / agentic intelligence). The flagship instance is built on Somerville 311 service-request data (~1.17M rows, ten years). Benchmark: the build cost ~$120 in infra/API plus ~40 hours, all open-source tooling — work that previously needed three people over three months plus commercial licenses.

**Collaborator:** Virginia — onboarding analyst, translating the demo for commercial customer contexts.

---

## 2. Where the repos are

Both on GitHub under the **`ironmonkey88`** account:

| Repo | Role |
|------|------|
| `ironmonkey88/oxygen-mvp` | Somerville-specific civic analytics instance. **Currently at MVP 2.** Discovers and proves features. |
| `ironmonkey88/stack-in-a-box` | Generic, cross-repo foundation extracted from oxygen-mvp, genericized for distribution. |

**Repo relationship (settled architecture):** oxygen-mvp discovers and proves features → stack-in-a-box extracts the working foundation, genericized → a *future* Personal Data Warehouse repo will be a downstream leaf that consumes freely but contributes back only via occasional deliberate "big lift" architecture-level harvesting, **not** continuous sync.

**Stack:** DuckDB, dbt, dlt, Oxygen CLI, Python, local web UI.
**Infrastructure:** EC2 `t4g.medium`, Ubuntu 24.04 arm64, for stack-in-a-box; single-node, small-scale. (oxygen-mvp runs on its own EC2 instance reachable over Tailscale.)

**Oxygen docs mirror:** `oxygen-mvp/docs/oxygen-docs/` is an offline, version-controlled mirror of oxy.tech/docs. Refresh via `./scripts/fetch_oxygen_docs.sh`. Use it to grep Oxygen docs without hitting the network.

---

## 3. Authority-document hierarchy (read these first in any new session)

Both repos are governed by a layered set of authority documents. **The reference standard is `APPROACH.md`** (cross-repo, implementation-free, byte-identical in both repos) — other docs reconcile *against* it periodically, not the reverse.

| Doc | Role |
|-----|------|
| `APPROACH.md` | Cross-repo reference standard. Both philosophy docs reconcile against it. Implementation-free. Title line: "How We Build — our approach." |
| `CLAUDE.md` | Operating behavior / rules. Where operational rules live (not philosophy). |
| `PHILOSOPHY.md` | Conviction layer — the creed and principles. In oxygen-mvp this is the Somerville-specific instance that specializes APPROACH.md. |
| `METHODOLOGY.md` | Build discipline — rules R1–R8. Exists in stack-in-a-box; **oxygen-mvp's own METHODOLOGY.md is not yet instantiated** (open work). |
| `PROMPTS.md` | Prompt shape conventions. |
| `session-starter.md` | What a fresh Chat reads to bootstrap. |
| `LOG.md` | Plan numbering (Plans Registry) and current status. The authoritative project record. |
| `TASKS.md` | Task tracking (drives the "todos" command). |
| `docs/PROJECT_BRIEF_5_11_26.md` | Project brief (oxygen-mvp); §10 holds a reference map. |
| `docs/prompts/` | Prompt + report lineage: every plan's prompt at `plan-NN-<slug>.md` with sibling `.report.md`. |

**Established repo-reading strategy (use this, don't over-fetch):**
- Three-file targeted read: `PROMPTS.md` (prompt shape) + `LOG.md` (plan numbering + status) + a philosophy/design doc (mission alignment).
- Read root directory via `path: "/"` for structural assessment.
- **If `LOG.md` shows an in-flight plan with a queued prompt already written, stop — do not draft a competing build artifact.**
- GitHub reads use `Github 2:get_file_contents` with `owner`, `repo`, `path`.

---

## 4. How we work together — the non-negotiable disciplines

These are the working agreements. They are partly in the repos and partly only here. **Honor all of them from message one.**

### Chat/Code split (core discipline)
- **Chat** (the session type a fresh general-purpose Claude chat plays) handles **architecture, design, and judgment**.
- **Code** (a separate Claude instance) handles **all file writes and commits**. Chat never writes repo files directly.
- Chat/Code is a *flagged example* of the decide-then-build principle — **not** the principle itself. Don't elevate it to doctrine.

### MCP-direct-commit path is PAUSED
- The GitHub MCP connector approval gate blocks file writes. **Code owns prompt-file creation until further notice.**

### Phase 0 (goes into every Chat-drafted prompt, verbatim)
Every prompt Chat drafts must open with this Phase 0:

> **Phase 0 (do this first).** Before any other work, write this prompt verbatim to `docs/prompts/plan-NN-<slug>.md` on a new branch `claude/plan-NN-<slug>`. This file write is the first commit on the branch. All subsequent phases proceed against that branch. Assign the real plan number from the `LOG.md` Plans Registry tail — do not guess it; if the next contiguous slot is ambiguous, halt and surface before branching.

(Session 47 in oxygen-mvp caught Chat guessing the wrong slot — read the registry, don't infer. The registries contain reserved-but-unused slots; do not claim a reserved one.)

### Plan discipline
- Plan-numbered branches: `claude/plan-NN-<slug>`.
- Plans tracked in `LOG.md` Plans Registry; each repo numbers from its own registry.
- Prompt + report lineage in `docs/prompts/` (Plan 43 convention in oxygen-mvp): `plan-NN-<slug>.md` + sibling `.report.md`.

### Delivery format (strict)
- **All Chat-to-Code prompts are delivered as downloadable `.md` files, never inline in chat.**
- **All Slack daily updates are delivered as downloadable `.md` files, never inline in chat.**

### Trigger commands the operator uses
- **"slack daily update"** → follow the format in `slack-update-format.md` (the repo file is the spec; the instruction line is the trigger). Deliver as a downloadable `.md`.
- **"todos"** → show the most recently *finished* tasks from `TASKS.md` plus the upcoming ones.
- **"read the session starter"** → read `session-starter.md` at the start of every chat.

### Working style (match this)
- Direct, decisive, aphoristic. He makes calls fast once options are framed.
- Pushes back on scope creep and wrong abstractions immediately.
- **Read before reasoning** — ground in actual repo files, not memory or assumptions.
- In interview/exploration contexts: short Q&A — short questions, answers drive the next question, no multi-question dumps. Hold synthesis until enough data is gathered.
- Simpler, more familiar terminology always wins over precise jargon for reader-facing text.
- Somerville/resident is illustrative-not-definitional in cross-repo docs.

---

## 5. What's already landed (recent merged work)

- **`APPROACH.md`** established as cross-repo reference standard (stack-in-a-box Plan 5 / oxygen-mvp Plan 48, merged 2026-06-10; byte-identical).
- **Three-term creed** in `PHILOSOPHY.md` (both repos): empathy (context is structural, not tonal), honesty (the constraint the other two answer to), optimism (earned progress over the counterfactual, correcting the negativity bias complaint-feeds inherit by construction). Inspirations: Fix The News, Intelligent Optimism. (stack-in-a-box Plan 6; oxygen-mvp Plan 49 reconciliation.)
- **System humanism reclassified** from philosophical strand to methodology: build-discipline half → `METHODOLOGY.md`; conviction half stays in `PHILOSOPHY.md`.
- **Sensemaking (Klein's Data-Frame Theory)** adopted as project SOP — the scientific method in two tiers: **hypothesis** (working, provisional, always labeled) and **result** (full trust-contract cost). Terminology locked as hypothesis/result for reader self-explanatoriness.
- **Capability-to-scope law:** the altitude of command rises with the capability-to-scope ratio of the executor (unifies Situational Leadership, hardware-abstraction tradeoffs, control-theory altitude).
- **Declarative-first design** framed as an accessibility strategy. Airplane/elevator/oncology ladder is the canonical illustration.
- **`METHODOLOGY.md` rules R1–R8** in stack-in-a-box. Code split R7 into R7/R8 (declarative/reconciliation and idempotency as separately-testable). R5–R8 carry "Pending-propagation" rows to oxygen-mvp for when its METHODOLOGY.md is instantiated.

---

## 6. Active / in-flight state (verify against `LOG.md` before acting)

**stack-in-a-box:**
- **Plan 4** (Oxygen 0.5.54 pin + contract-level gates + `flock`+retry DuckDB contention handling + smoke resilience + clean-box confirmation) was the open "next" item, running/verified through Phase 3 on metal at last close. Confirm its status in `LOG.md` first thing. Design decisions confirmed: DuckDB contention = flock+retry now, snapshot-swap deferred to a data-driven threshold; smoke default = small; SODA resilience = existing retry plus idempotent-merge resume for unattended refreshes.
- Plan 3 completed: first install on real EC2 metal, all 10 `bootstrap.sh` steps green, six install bugs fixed (incl. the F6 trust-contract blocker where the Oxygen duckdb connector needed `path:` not `dataset:`). F6 contract fired live on metal. PR #7 reviewed mergeable.

**Trust contract (non-negotiable, live on metal):** every agent reply ships **SQL, row count, citations, and limitations-registry entries**. This is the verification gate that prevents abductive reasoning from laundering speculation — including within Klein's frame loop.

**oxygen-mvp:** MVP 2. Plan 49 last done (2026-06-10). Reserved-but-unused slots exist in the registry (e.g. Plan 41 DBA v1.2 calibration, Plan 42 memory-to-file migrations) — do not claim a reserved slot for new work.

**Designed but not yet confirmed merged (verify in `docs/prompts/` and the registry):**
- **Tech-debt decision register:** five authority-document changes — new `TECH_DEBT_LEDGER.md` (repo root); new `PHILOSOPHY.md` §6.8 principle ("sustained productivity is the asset"); new `CLAUDE.md` "Evaluating tech debt" rule; conditional "Tradeoff rationale" section in `PROMPTS.md` §3; pointer wiring in `session-starter.md` and `PROJECT_BRIEF §10`. (oxygen-mvp open PR #76 was the tech-debt-assessment thread holding the Plan 47 slot.)
- **Dependency pinning** (pure outsource; versions from live `pip freeze` on EC2; F6 contract as reproducibility gate) and **Python test layer** (four-area threat model as binding spec — T1 limitations-index integrity, T2 page-generator output correctness, T3 pipeline-run identity/provenance, T4 staleness false-current; Code forbidden from inventing coverage targets). Sequenced pinning-first.

---

## 7. On the horizon (tracked, not yet started)

- **oxygen-mvp `METHODOLOGY.md`** — instantiation still open. The system-humanism split in `oxygen-mvp/PHILOSOPHY.md` is deferred until this exists; R6's propagation row names this as its destination.
- **`PRODUCT_NOTES` tech-inspiration list** — MotherDuck Flights, Posit open-source stack (incl. ggsql for declarative visualization).
- **Personal Data Warehouse repo** — downstream leaf concept for a future session.
- **Desktop/local analytics application concept** — MVP-0 framing complete; scoped as **not-a-plan**, not to be started until stack-in-a-box Plan 3 is fully resolved. (Concept writeup committed to `stack-in-a-box/docs/concepts/`.)
- **ggsql integration spike** — four-part investigation: confirm rendering contract, add hidden feature-flagged route with lazy-loaded WASM, update agent prompt with ggsql grammar, use Oxygen's existing SQL execution path. Primary unknown: whether Oxygen's chart artifact renderer is Vega-Lite-compatible.
- **Plausibility-layer port** (from evaluating sibling repo `camharris93/sediment`): port the L6 fan-out + value-sanity plausibility checks into oxygen-mvp's query path with adversarial tests, to mechanize the trust gate; plus the structural external-reader rejection in the read-only guard. Offered but not yet drafted as a Plan.

---

## 8. Key learnings and principles (the durable rules)

- **Trust contract is non-negotiable:** SQL + row counts + citations + limitations on every agent reply.
- **Verify suites can pass while the actual contract is broken** (stack-in-a-box METHODOLOGY R1): component-level passing is not sufficient evidence the end-to-end contract holds.
- **Declarativeness is an accessibility strategy:** engineered through a constrained data layer, semantic standardization, and tests driving reconciliation.
- **Capability-to-scope law:** altitude of command rises with the capability-to-scope ratio of the executor — applies to agent design, system architecture, and human delegation alike.
- **Hypothesis vs. result discipline:** all provisional frames labeled as hypotheses; results carry full trust-contract cost.
- **Outsource/dig-in sorting rule:** fully delegate execution tasks where "done" is precisely specifiable and verifiable; own the threat model and judgment calls where the agent's output would be unverifiable.
- **Tech-debt triage requires recorded rationale:** every decision — including deliberate deferrals and accepts — logged with reasoning so the process compounds and transfers.
- **ROI lens for tech debt — four criteria:** impairing final quality; impairing ability to deliver; recurring productivity tax; mental load on the team.
- **"Appealing because I know it" ≠ "best for the functionality":** separate familiarity bias from architectural fit when evaluating technology.
- **Parallel-run reconciliation over big-bang cutover:** for infrastructure replacement (e.g., elementary vs. home-grown DQ stack), run in parallel with explicit tie-out mapping, discrepancy attribution, and a named decommission criterion to prevent permanent drift. (Four functional DQ criteria: consistent testing, history of test results, trend detection, provable testing.)
- **Read the function body, not the function name** (oxygen-mvp Session 42): the minified bundle is not opaque; diagnose from the code, not the symbol.

---

## 9. Frameworks and references in play

- **Methodology/theory:** Klein's Data-Frame Theory of Sensemaking; Working Backwards; Knowledge Product Pipeline; Knowledge Hierarchy of Needs (Security → Quality → Reliability → Usability → Coverage); Analytics Maturity Lifecycle (Descriptive → Diagnostic → Predictive → Prescriptive); Situational Leadership; Daniel Pink's *Drive*; Arthur Brooks' happiness macronutrients.
- **Product-philosophy inspirations:** Fix The News, Intelligent Optimism, MotherDuck Flights, Posit open-source stack.
- **Foundational doc in project knowledge:** the **Analytics Platform Primer** (establishes Working Backwards, the Knowledge Product Pipeline, the Knowledge Hierarchy of Needs, medallion assembly-line architecture, the Analytics Maturity Lifecycle). Re-attach this to the new project's knowledge.

---

## 10. First-session checklist for the new account

1. Re-attach project knowledge: the **Analytics Platform Primer** and the **Oxygen docs mirror** (or point at `github.com/ironmonkey88/oxygen-mvp/tree/main/docs/oxygen-docs`).
2. Confirm the **GitHub connector** is authorized in the new account (Chat reads repo files via `Github 2:get_file_contents`; the MCP-direct-commit path remains paused).
3. Re-establish the trigger commands and Phase-0 prompt discipline in the new chat's setup ("slack daily update", "todos", "read the session starter") — these were hand-wired instructions, not repo state. §4 has the exact text.
4. Read `session-starter.md`, then the three-file targeted read (`PROMPTS.md` + `LOG.md` + a philosophy doc) on whichever repo the next piece of work touches.
5. **Check `LOG.md` for stack-in-a-box Plan 4 status** before drafting anything — it was in-flight at last close.
6. Confirm whether the tech-debt register and the pinning/test-layer plans have merged since (check `docs/prompts/` and the registry).
