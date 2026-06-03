# Tech & Test Debt Assessment — oxygen-mvp

**Plan:** 47 · **Mode:** investigate & report (zero behavior changes) · **Date:** 2026-06-02
**Author:** Claude Code · **Status:** proposal for Gordon's approval — no reduction work has begun.

> Everything below is **measured**, not estimated-from-memory. Python LOC from `wc -l` on the
> canonical tree (excluding `.venv`, gitignored `.claude/worktrees/`, and `scratch/`). dbt graph
> facts from `manifest.json` produced by a read-only `dbt parse` on EC2 (build `89d6ecc`); test
> counts and model timings from that manifest + the `run_results.json` in `target/`. Dependency
> set from `pip freeze` on EC2's `.venv` (Python 3.12.3) cross-referenced against the actual
> `import` graph. Raw artifacts: `scratch/plan47_ec2/` + `scratch/plan47_*.py` (gitignored).

---

## 0. Executive summary

| Area | Verdict | Severity |
|---|---|---|
| **dbt model graph** | **Coherent team-effort, paused mid-roadmap** — not parallel play | Low (structure), one correctness-adjacent seam |
| **dlt pipelines** | **Disciplined template applied by copy-paste** — coherent intent, duplicated implementation | Medium (resilience gap) |
| **Page-gen scripts** | Real but **bounded** dedup opportunity (~550–650 lines of chrome); most `generate_*` scripts are WET-by-right | Low |
| **Python tests** | **Zero** unit tests; the run.sh critical path is untested code | **High** |
| **CI** | **None** (`.github/` absent) | Medium |
| **Dependency mgmt** | **None** (no `requirements.txt`/`pyproject`/lock) — reproducibility rests on one EC2 venv | **High** |
| **R1 (test-the-contract)** | **No automated agent-answers-a-real-query gate** anywhere; verified manually at sign-offs only | Medium |

**Headline:** This is a *coherent* codebase, not a pile of parallel play. The data layer was built to one
template by one disciplined hand over 46 plans — uniform naming, declared grain on every fact, a
consistent surrogate-key idiom, and explicit "deferred to MVP 3" markers where corners were knowingly
cut. The debt is **not architectural incoherence**; it is **missing safety infrastructure** (no Python
tests, no dep pinning, no CI, no end-to-end contract gate) plus **un-factored duplication** (no dbt
macros, no `dlt/common.py`, un-extracted HTML page chrome). That distinction drives the whole plan: the
cheap, high-leverage wins are the *missing nets* (deps + tests + CI), not a refactor.

**Correctly-sequenced reduction order (detail in §7):** **(1) pin dependencies → (2) minimal Python test
layer → (3) CI gate → (4) structural dedup (dbt macros, `dlt/common.py`, page-chrome helper) → (5) finish
the medallion (silver) as its own MVP-3 plan.** You cannot safely refactor untested code, so deps + tests
come first; the refactors are gated behind them.

---

## 1. Page-generation scripts — DRY vs WET (Phase 1)

**Baseline:** `scripts/` is 6,274 LOC (the bulk of the project's Python); `dlt/` is 997. The hypothesis —
that the `generate_*_page.py` scripts share a repeated skeleton — is **partly confirmed, partly refuted**,
and the refutation matters as much as the confirmation.

### What's measured

| Script | LOC | Output | DuckDB | Uses `_nav`? | Inline chrome | DRY target? |
|---|---|---|---|---|---|---|
| `generate_trust_page.py` | 757 | `portal/trust.html` | yes (ro) | yes (nav+CSS) | ~190 | **yes** |
| `generate_admin_dashboard.py` | 580 | `/var/www/.../admin/` | yes (ro) | **no — inlines own** | ~90 | **yes (also fixes nav drift)** |
| `generate_somerville_info_page.py` | 506 | `portal/about.html` | yes (ro) | yes | ~150 | **yes** |
| `generate_profile_page.py` | 379 | `portal/profile.html` | yes (ro) | yes | ~95 | **yes** |
| `generate_homepage_summary.py` | 385 | marker-patch `index.html` | yes (ro) | nav only | none (regex patch) | no (structurally different) |
| `generate_erd_page.py` | 338 | `portal/erd.html` | no | yes | ~120 | **yes** |
| `generate_socrata_inventory_page.py` | 273 | `docs/*.md` (markdown) | yes (ro) | n/a | none | no (not HTML) |
| `generate_dashboards_listing.py` | 241 | marker-patch `dashboards.html` | no | nav only | none | no (marker patcher) |
| `generate_metrics_page.py` | 236 | `portal/metrics.html` | no | yes | ~95 | **yes** |
| `generate_wards_svg.py` | 230 | `.svg` | yes (ro) | n/a | none | no (SVG) |
| `generate_per_tier_erd.py` | 163 | `.mmd` ×3 | no | n/a | none | no (mermaid) |
| `generate_warehouse_erd.py` | 154 | `.mmd` | no (reads manifest) | n/a | none | no (mermaid) |
| `generate_semantic_layer_diagram.py` | 107 | `.mmd` | no (reads YAML) | n/a | none | no (mermaid) |
| `_nav.py` | 128 | shared nav lib | — | (is the helper) | — | — |
| `rendered_page.py` | 560 | **Playwright verifier** | — | — | — | **not a generator** |

### Findings

1. **`rendered_page.py` is NOT the intended shared page helper.** It is a Playwright/Pillow rendered-DOM
   *verification* tool (`test_page()` / `review_page()` — see STANDARDS.md §8). It renders existing URLs to
   assert on them; it never emits portal HTML. The "the helper exists but scripts bypass it" hypothesis is
   **false** — they're unrelated concerns. Don't conflate them.

2. **`_nav.py` already captured the single highest-value extraction** — the nav fragment + `NAV_CSS` are
   imported by 7 generators. This is the DRY win that *was* made, and it was the right one.

3. **The un-extracted remainder is the page shell**, not the nav: the `<!doctype>`→`<head>`→`@font-face`(×4)
   →`:root` token block→base `body`/`a` CSS is **byte-identical** across `metrics`/`trust`/`profile`/`erd`/
   `about` (verified by grepping the shared `--green: #1e4d2b` token + font-face lines). Each full-HTML
   generator also re-rolls the same `connect(read_only=True)` + "DB missing → skip" guard and the same
   `OUT_PATH.write_text(...)` tail. That's ~90–110 duplicated lines per full-page generator.

4. **The one real nav-duplication offender is `generate_admin_dashboard.py`** — it bypasses `_nav.py` and
   inlines its own divergent chrome/footer/CSS. Migrating it onto a shared shell both dedups ~90 lines *and*
   fixes a live nav inconsistency.

### DRY-vs-WET verdict (the part that matters)

Apply the test — *"when one page's requirements change, do the others need to change too?"*:

- **DRY (one reason to change) — extract these:** the page shell (head + font-face + `:root` tokens + base
  CSS + nav injection + write-tail) and a `db_connect_readonly()` context manager. When the brand font, the
  color tokens, or the read-only connect guard changes, **all** full-HTML pages must change together. That is
  genuine shared plumbing. **~550–650 lines collapse**, concentrated in **6 scripts** (`trust`, `about`,
  `profile`, `erd`, `metrics`, `admin_dashboard`).

- **WET (independent reasons to change) — leave these alone, deliberately:** every script's **SQL queries**
  and its **page-specific `<main>` markup + component CSS** (`.measure-card`, ERD mermaid scaffold, the trust
  page's contract tables). The `.mmd`/`.svg`/`.md`/`.yaml` emitters (`warehouse_erd`, `per_tier_erd`,
  `semantic_layer_diagram`, `wards_svg`, `socrata_inventory`, `build_limitations_index`) match the
  `generate_*` *name* but share **no page chrome** — forcing them through an HTML shell would be the wrong
  abstraction. The two **marker-patchers** (`homepage_summary`, `dashboards_listing`) are structurally
  different (they regex-patch hand-written HTML) and save only ~15 lines each — not worth it.

> **Over-abstraction risk to call out explicitly:** the temptation after seeing "10 `generate_*` files" is a
> single `PageGenerator` framework that every script subclasses. **Don't.** That produces a god-function with
> flag-soup (`is_markdown`, `has_db`, `emit_svg`, `patch_mode`…) to accommodate 4 genuinely-distinct output
> formats. The correct shape is a *small, optional* `portal_page.py` helper (`page_shell(title, body, active,
> extra_css)` + `db_connect_readonly()`) that the **6 full-HTML generators import** — and the other 7 scripts
> simply don't call. A helper you can ignore, not a base class you must inherit.

---

## 2. Test & CI gap (Phase 2)

- **Python unit tests: zero.** No `test_*.py` / `*_test.py` anywhere in the canonical tree; no `pytest`/
  `unittest` in the dependency set. The **dbt layer is well-tested (154 tests — see §4), but every line of
  Python is untested.**
- **Highest-risk-if-broken Python** (untested, on the critical path):
  - `scripts/pipeline_run_start.py` / `pipeline_run_end.py` — own the run-observability records; a silent
    break corrupts `fct_pipeline_run_raw`.
  - `dlt/load_dbt_results.py` — hand-writes typed DDL + `int()`/`float()` casts; a parse change drops DQ rows.
  - `scripts/generate_trust_page.py` (757 LOC) — renders the **F6 trust contract** surface; the largest,
    most user-trust-bearing script, with zero coverage.
  - `scripts/source_health_check.py` (parameterized across 6 sources) and `scripts/profile_tables.py`.
- **Minimum-viable test layer** (proposal, not built here): pure-function unit tests for the
  parsing/transform helpers in `load_dbt_results.py`, `source_health_check.py`, `build_limitations_index.py`,
  and `profile_tables.py` (these have testable logic and no rendering). The **page generators are adequately
  covered by the existing rendered-page valid-HTML check** (`rendered_page.py`) — they don't all need unit
  tests; they need the rendered-page gate to actually *run in CI*. So: unit-test the data/parse helpers;
  rely on rendered-page checks for the HTML emitters.
- **CI: none.** No `.github/workflows`. A lightweight gate would cover, in order of cost/value:
  `python -m py_compile` (catches syntax breaks instantly), `bash -n run.sh`, `dbt parse` + `oxy validate`
  (config integrity, no warehouse needed), the new pytest layer, and — where a warehouse is reachable —
  `dbt build` + the rendered-page checks.

### R1 — test-the-contract (methodology whiteboard)

**Finding:** oxygen-mvp has **no automated end-to-end "agent answers a real query" gate.** Verified by
grep — neither `run.sh` (stages 0–10 are all dlt/dbt/page-generation steps) nor any `.sh`/`.py` invokes
`oxy run agents/answer_agent.agent.yml`. The agent contract is exercised **only manually**, at MVP sign-offs,
with transcripts pasted into TASKS.md (per STANDARDS §6 + CLAUDE.md verification-gates rules). `oxy validate`
checks YAML syntax — it does **not** prove a live answer returns. This is **exactly the R1 gap** the shared
`METHODOLOGY.md` predicts ("a verify suite that checks components can pass while the actual product is
broken").

**Handling (per pre-flight decision with Gordon):** `METHODOLOGY.md` is **not yet instantiated in
oxygen-mvp**, and its own governance is *Code-proposes / human-approves, never auto-committed*. So this report
**records the R1 finding** but does **not** create/edit the whiteboard. **Recommended human-ratified
follow-up:** instantiate `METHODOLOGY.md` in oxygen-mvp and close R1 by adding a single canned-question gate
(`oxy run … "How many 311 requests were opened in 2024?"` asserting `113961`) to the CI layer above.

---

## 3. Dependency hygiene (Phase 3)

**Confirmed:** no `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, or lockfile anywhere.
Reproducibility currently rests entirely on the **one** hand-built `.venv` on EC2. A fresh clone (new machine,
a worktree, a teammate, a future personal fork) has **no declared way to reconstruct the environment** — this
is the single biggest portability/reproducibility risk in the repo.

**Actual third-party import set** (from `grep` across canonical `.py`, with install counts):
`duckdb` (18), `python-ulid`→`ulid` (10), `requests` (9), `dlt` (7), `PyYAML`→`yaml` (6),
`psycopg2-binary`→`psycopg2` (1), `playwright` (1), `pillow`→`PIL` (1). Plus `dbt-core` + `dbt-duckdb` as
CLI runtime deps (not imported).

**Proposed pinned `requirements.txt`** (versions = what's *actually installed and working* on EC2 per
`pip freeze`; **cross-referenced against `stack-in-a-box/requirements.txt`** — the four pins it shares match
oxygen's installed versions **exactly**):

```
# Runtime deps for oxygen-mvp Python (pins = EC2 .venv, Python 3.12.3, verified working).
# Cross-referenced against stack-in-a-box/requirements.txt; shared pins are identical.
dlt[duckdb]==1.26.0       # ingestion (matches stack-in-a-box)
dbt-core==1.11.9          # transformation CLI (matches stack-in-a-box)
dbt-duckdb==1.10.1        # dbt adapter (matches stack-in-a-box)
duckdb==1.5.2             # warehouse client (stack pins >=1.1.0; we hard-pin the working build)
python-ulid==3.1.0        # run IDs — see version note below (matches stack-in-a-box)
PyYAML==6.0.3             # semantic-layer + config parsing
requests==2.33.1          # Socrata SODA pulls + source-health checks
psycopg2-binary==2.9.12   # oxy chat-activity loader (Postgres) — NOT in stack-in-a-box
playwright==1.60.0        # rendered-page verification helper — NOT in stack-in-a-box
pillow==12.2.0            # screenshot annotation in rendered_page.py — NOT in stack-in-a-box
```

**Version-sensitive flag — `python-ulid`:** EC2 runs **3.1.0**, i.e. the project already lives on the far
side of the known 1.x→3.x API break. Any `requirements.txt` **must hard-pin `==3.1.0`** (not `>=1`) or a
fresh install could resolve to a 1.x line whose `ulid` API differs and break run-ID generation across every
pipeline. This is the one pin where "just install latest" is actively dangerous.

> Note: `tenacity==9.1.4` is present in the venv (transitive via dbt) — a retry library is *already
> installed* but **unused** by the pipelines. Relevant to §4's resilience gap: adding backoff costs no new
> dependency.

---

## 4. Data-layer coherence verdict (Phase 4) — the headline

### dbt graph: **coherent team-effort, paused mid-roadmap**

Authoritative facts from `manifest.json`: **26 models** (7 bronze · 1 silver · 15 gold · 3 admin),
**154 tests** (88 not_null, 29 unique, 24 accepted_values, 12 relationships, 1 singular), **0 project
macros**. Materializations are sane (bronze=view, gold=table, admin=incremental). Every model builds
**sub-second** in `run_results.json` (slowest = `fct_data_profile` at 0.24s) — **there is no
expensive-rebuild problem**, so materialization choices are immaterial to cost.

**This is NOT parallel play.** Strong coherence signals: uniform `raw_`/`stg_`/`fct_`/`dim_` prefixes across
all layers; **every fact declares its grain** in a header comment; one consistent `md5(...)` surrogate-key
idiom; one consistent "passthrough bronze, casts deferred to silver/gold (MVP 3)" pattern stated verbatim in
model headers; plan-numbered narrative in comments. Different *subjects* (crime, permits, citations, survey,
kpi) were each added in their own plan — but added **to the same template**, which is the opposite of N
corners each solving it their own way.

**The real seams (structure, not correctness):**

1. **Silver is 1/6 built.** Only the happiness survey has a silver model (`stg_happiness_survey`). For the
   other five subjects, **gold reads bronze directly** — the manifest confirms **9 gold→bronze edges that
   skip silver** (`fct_311_requests`, `fct_crime_incidents`, `fct_citations`, `fct_permits`,
   `fct_somerville_kpi`, and the `dim_date`/`dim_request_type`/`dim_status`/`dim_ward` dims). Type-casts,
   trims, and PII handling that belong in silver currently live in gold **by deliberate, documented
   deferral**. The medallion has a hole; it's a planned hole, not an accident.

2. **No macros (`dbt/macros/` absent).** The same SQL idiom is re-expressed inline everywhere: `md5(...)`
   surrogate keys in 7 models; the VARCHAR→timestamp date-cast in ~5 places; `nullif(trim(ward),'')`
   ward-trim duplicated in `fct_crime_incidents` + `fct_citations`. For 26 models this is borderline, but it
   is the clearest "no shared-infrastructure pass was ever made" signal.

3. **`fct_data_profile` froze at 5 tables** while gold grew to 15 — it profiles only 311 + 4 originals and
   never expanded as crime/permits/citations/survey/kpi landed. A pure accretion-lag artifact.

**Correctness-adjacent (the one fix worth prioritizing):**

4. **Admin models hardcode physical table names instead of `ref()`.** The manifest proves it: all three admin
   models have **zero dbt-tracked upstream nodes** (`fct_data_profile` nodes=`[]`, `dim_data_quality_test`
   nodes=`[]`, `fct_test_run` refs only its sibling). They read `main_gold.*` / `main_bronze.*` as literal
   strings, so **dbt does not know admin depends on gold/bronze** — those DAG edges are invisible. Correctness
   currently rests on `run.sh` stage ordering (stage 5 admin after stage 2 gold), not on dbt's own
   resolution. A future `dbt build` reorder or partial run could profile/baseline **stale** tables with no
   error. (The `raw_dbt_results_raw` hardcode *is* justified — it's dlt-written mid-run and genuinely
   sourceless; the gold/bronze refs are not.)

### dlt pipelines: **a disciplined template applied by serial copy-paste**

8 files in `dlt/` (997 LOC). The 6 Socrata pipelines are **template clones** — `add_audit_columns` is
**byte-identical** across all six; the pagination loop, module-constant block, and `dlt.pipeline()` setup are
duplicated verbatim with only the dataset id / column list / table name / merge key swapped (docstrings even
say "Adapted from `somerville_crime_pipeline.py` — same shape"). Merge keys are sensible (`id`, `incnum`,
`citationnum`, `message_id`); full-pull-no-watermark is a **documented** choice (sources have no per-row
modified field), not an oversight. Coherent *intent*, duplicated *implementation*.

**The three real dlt debts:**

1. **Zero retry/backoff anywhere — a uniform resilience gap.** No pipeline has any transient-failure handling;
   the only resilience is `resp.raise_for_status()` + a fixed `timeout=60`. A single flaky Socrata page aborts
   the whole daily systemd run (311 alone paginates ~1.17M rows over ~24 requests). It's at least *uniformly*
   absent — and `tenacity` is already installed (§3), so a shared retry helper adds no dependency.
2. **No shared module.** Every file re-implements `fetch_all`, `add_audit_columns`, `post_merge_first_seen`,
   `main`. A `dlt/common.py` would collapse ~80% of every Socrata file — and is the natural home for the
   missing retry.
3. **Hardcoded absolute `DUCKDB_PATH`** (`/home/ubuntu/...`) in the Socrata files makes them non-portable
   across machines/worktrees; the two non-Socrata files compute it from `REPO_ROOT` instead — same job, two
   conventions (`oxy_chat_activity` and `load_dbt_results` also drift on connect idiom + exit convention).

**Coherence verdict for the data layer as a whole: team-effort, not parallel play.** The debt is *unfinished
medallion + un-factored shared SQL/Python + an unmodeled admin dependency edge + an absent retry layer* — all
consistent with one coherent build paused at MVP 2, **not** with incoherent accretion. **A clone would inherit
a clean, legible graph** — which is the good news for any future extraction.

---

## 5. Broader code-debt scan (Phase 4b)

- **TODO/FIXME/HACK density: effectively zero.** One match in the whole canonical tree, and it's prose inside
  a docstring string literal (`generate_socrata_inventory_page.py:40`), not a real code marker. Known
  shortcuts live in LOG.md / the limitations registry, not as inline debt — consistent with the disciplined
  style.
- **Somerville-specific vs separable:** the dlt Socrata template, `_nav.py`, `rendered_page.py`,
  `pipeline_run_*`, `source_health_check.py`, and the admin DQ pattern are all **cleanly source-agnostic**
  (this is precisely what stack-in-a-box extracted). The Somerville coupling is concentrated in dataset ids,
  the gold dims, and portal copy — entangled at the *data* layer, separable at the *plumbing* layer.
- **Coupling hotspots:** `_nav.py` is the most-imported local module (7 generators) — a deliberate, healthy
  hub. The hardcoded `DUCKDB_PATH` string is the most-duplicated literal. No alarming ripple-risk coupling.
- **Local hygiene (not committed debt):** `.claude/worktrees/` holds stale, *divergent* copies of the
  generators (e.g. `generate_trust_page.py` is 757 lines canonical vs 430 in one worktree). Both
  `.claude/worktrees/` and `scratch/` are **gitignored**, so this is **not** repo debt — but it is local
  working-directory cruft worth a `git worktree prune` / manual cleanup pass.

---

## 6. What this assessment did NOT do (scope honesty)

- No behavior changes, no refactors, no file restructuring. The only writes this plan made: this document,
  the prompt file, and TASKS/LOG/session housekeeping.
- EC2 interaction was **read-only** (`pip freeze`, `dbt parse`, copy `manifest.json`/`run_results.json`) — no
  pipeline run, no DB write, no DuckDB lock contention.
- Did not instantiate `METHODOLOGY.md` (human-approved per its own governance — see §2).

---

## 7. Prioritized, sequenced reduction plan (proposal)

**Ordering principle, stated explicitly:** *you cannot safely refactor untested code, and you cannot
reconstruct an environment you can't pin.* So **safety infrastructure precedes every refactor.** Deps + tests
+ CI first; dedup and medallion-completion last, behind those nets.

| # | Item | Why now | Effort | Risk if skipped |
|---|---|---|---|---|
| **1** | **Pin `requirements.txt`** (§3, ready to commit) | Reproducibility floor for everything else; a clone is unbuildable today | **S** (~1h) | Env drift; no fresh-install path |
| **2** | **Minimal pytest layer** for the data/parse helpers (`load_dbt_results`, `source_health_check`, `build_limitations_index`, `profile_tables`) | These are pure-function, high-risk, on the run.sh path; tests must exist *before* any refactor touches them | **M** (~4–6h) | Silent breakage of observability/DQ records |
| **3** | **Lightweight CI** (`.github/workflows`): `py_compile` + `bash -n` + `dbt parse` + `oxy validate` + pytest; add the **R1 canned-agent-query gate** | Cheap, catches regressions every push, closes R1 | **M** (~3–4h) | Regressions land silently between sessions |
| **4** | **Extract `dlt/common.py`** (`fetch_all`, `add_audit_columns`, audit cols, **+ a `tenacity` retry wrapper**) and de-hardcode `DUCKDB_PATH` | Highest data-layer leverage; fixes the uniform resilience gap; ~80% of each Socrata file collapses | **M** (~4–6h) | Daily refresh stays fragile to one flaky API page |
| **5** | **dbt macros** for the recurring idiom (`md5` surrogate key, date-cast, ward-trim) | Removes the inline-duplication signal; no behavior change (same SQL) | **S–M** (~2–4h) | Drift as more models are added |
| **6** | **Fix admin `ref()`** — replace `main_gold.*`/`main_bronze.*` literals with `ref()` (keep the justified `raw_dbt_results_raw` hardcode) | The one correctness-adjacent seam; makes admin DAG edges real | **S–M** (~2–4h) | Stale-table baselining under a `dbt build` reorder |
| **7** | **`portal_page.py` page-shell helper** adopted by the **6 full-HTML generators only** (§1) | ~550–650 lines collapse; fixes admin nav drift; *bounded* by design | **M** (~4–6h) | Chrome edits must be made in 6 places |
| **8** | **Expand `fct_data_profile`** from 5 to all 15 gold tables | Closes the accretion lag | **S** (~1–2h) | Profiling silently under-covers the warehouse |
| **9** | **Finish the medallion — silver layer** for the 5 bronze-direct subjects | Biggest *structural* item; belongs to the existing **MVP 3** roadmap, not this debt pass | **L** (own plan) | Casts/PII stay in gold (already the documented MVP-2 state) |

Items **1–3 are the high-value core** and could be one small follow-up plan. **4–8** are a second
"structural dedup" plan (all behavior-preserving). **9 is already on the roadmap as MVP 3** — flagged here for
completeness, not proposed as debt work.

### What NOT to do

- **Don't build a `PageGenerator` base class / framework.** Extract a small *optional* shell helper for the 6
  HTML pages; leave the 7 non-HTML / marker-patch scripts WET. Forcing 4 output formats through one class is
  the wrong abstraction (flag-soup god-function).
- **Don't refactor before items 1–2 land.** No tests + no pins = no safety net.
- **Don't change data-layer *behavior* while restructuring.** The 154 dbt tests certify *correctness today*;
  the silver/macro/`ref()` work must preserve the exact data those tests validate. Restructure the graph, not
  the numbers.
- **Don't dedup the dlt *merge keys / write dispositions*** — the per-source differences (`merge` vs
  `replace`, the column lists, `$select` presence) are deliberate and documented. Extract the *plumbing*, keep
  the per-source *contract*.
- **Don't treat the gitignored worktree/scratch copies as code to fix** — they're local cruft to prune, not
  repo debt.

---

## 8. Measured-numbers appendix

- Canonical Python: **31 files, 7,271 LOC** (`scripts/` 6,274 + `dlt/` 997). Excludes `.venv`, gitignored
  `.claude/worktrees/`, `scratch/`.
- dbt: **26 models** (bronze 7 / silver 1 / gold 15 / admin 3), **1,217 LOC** of model SQL, **154 tests**
  (88 not_null / 29 unique / 24 accepted_values / 12 relationships / 1 singular), **0 project macros**,
  **7 sources**. Materializations: 7 view / 16 table / 3 incremental. **9 gold→bronze silver-skip edges.**
  All models build sub-second.
- Python: **3.12.3** on EC2. Third-party deps: 10 (8 imported + dbt-core/dbt-duckdb CLI). **No** dependency
  declaration of any kind in the repo.
- Tests/CI: **0 Python tests, 0 CI workflows, 0 automated agent-contract gate.**
- TODO/FIXME/HACK in canonical code: **1** (a docstring string, not a real marker).
- EC2 build measured: `89d6ecc`. Raw artifacts: `scratch/plan47_ec2/` (gitignored).
