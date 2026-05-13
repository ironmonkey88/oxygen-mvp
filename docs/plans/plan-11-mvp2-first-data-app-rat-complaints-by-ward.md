# Plan 11 — MVP 2: First Data App — Rat Complaints by Ward

**Status:** scoping only. Execution pending Gordon's review of this
document.
**Type:** scoping document, not a plan execution. Code writes the plan
file; the construction work waits.
**Plan slot:** Plan 11 — next after Plan 10.

## Why this is a scoping document, not an execution

Plan 11 is the first plan after the [BUILD.md §7 opportunistic
principle](../../BUILD.md#the-opportunistic-principle) landed in
Plan 10. The principle has teeth: when a plan reaches for an Oxygen
primitive, pre-flight verifies that primitive produces the analyst
experience the plan assumes; if it doesn't, the plan stops and the
tool choice gets revisited.

Plan 11 reaches for Builder Agent + Data Apps in `oxy start --local`
mode. Neither is pre-flight-verified at this scale; the [MVP 1
retrospective](../retrospective/mvp1-lessons-learned.md#builder-agent-and-data-apps-in-local-mode)
explicitly names this as the first MVP 2 pre-flight task. If pre-flight
fails, the plan's shape changes significantly: in the worst case, Plan 11
becomes a hand-written `.app.yml` exercise with Builder Agent deferred,
and the analyst-experience claim for MVP 2 looks different than the
prompt-as-handed-off assumes.

Better to scope, hand back for Gordon's review, and let Gordon decide
whether to execute as-written or refine.

---

## Inputs (decided in Chat Session 31 / handoff — carry forward)

| Decision | Answer |
|---|---|
| **First dashboard topic** | Rat complaints by ward (analyst Question 1 — frequency, resolution speed, volume trend, service equity) |
| **Filter approach** | Inline in task SQL. Pre-flight verifies what "rat complaints" means in the data (likely `request_type LIKE '%rat%' OR LIKE '%rodent%'`; verify against `main_gold.dim_request_type`) |
| **Semantic-layer additions** | Builder Agent decides as it constructs. We do not pre-specify the new measures. |
| **Demo transcript** | Directional: opening prompt + sketch of Builder's expected high-level moves drafted upfront; actual conversation captured during construction; light retro comparing actual vs expected |
| **Portal surface** | Portal page lists the dashboard with a description; click-through opens the SPA where the Data App renders. Implies a `/dashboards` index page (or similar — Code's call on the route name) |
| **Trust signals on dashboard** | Full trust contract: last refreshed (from `fct_pipeline_run_raw.run_completed_at` + `run_status`); citations on each chart (source: `main_gold.fct_311_requests` + relevant view); relevant limitations from the registry (at minimum ward-bronze-only; survey-related limitations don't apply to this dashboard) |
| **Pre-flight off-ramp** | Code uses judgment. If Build mode in `--local` isn't reachable but a workaround produces the same analyst experience, document the gap in the limitations registry, tag the workaround as scaffolding-that-earns-its-keep, and continue. Hand-writing YAML is allowed as fallback, tagged for revisit when Builder Agent matures. |

These decisions carry forward without re-deciding. If pre-flight surfaces
a contradiction with one of them, the plan stops and the contradiction
goes back to Chat.

---

## Carry-forward open questions (not yet resolved; must be resolved
inline during execution)

Two questions from the prior handoff were not resolved in Chat. They
should NOT be pre-decided by Code. The plan flags both as gates within
specific phases:

1. **Neighborhood dimension scope.** The bronze data has ward + block
   code only (per
   [`docs/limitations/location-ward-block-only.md`](../limitations/location-ward-block-only.md)),
   not neighborhood. Do we keep this dashboard ward-only (matching the
   data) and defer neighborhood to MVP 3 alongside `dim_location` + the
   Silver layer? Or do we hand-roll a ward → neighborhood mapping inside
   the Data App's SQL task?
   - **Resolve before Phase 3** (directional transcript drafted).
   - Default for the prompt: ward-only, defer neighborhood — but Gordon
     decides.

2. **Demo transcript as portal artifact.** Does the captured Builder
   Agent transcript become a portal artifact (`/dashboards/rat-complaints/transcript.md`
   or similar — a "this is how this dashboard was made" view of the
   conversation)? Or does the transcript live in `docs/transcripts/`
   for internal use only?
   - **Resolve before Phase 5** (trust signal integration).
   - Default for the prompt: internal-only first; portal exposure
     deferred — but Gordon decides.

---

## Phases

### Phase 1 — Pre-flight verification of Builder Agent in `--local` mode

This is the load-bearing phase. If Builder Agent + Data Apps don't work
in `--local` mode, the plan changes shape. Gates derived from STACK.md
§1.8, [TASKS.md "Next Focus"](../../TASKS.md), and the
[retrospective](../retrospective/mvp1-lessons-learned.md#builder-agent-and-data-apps-in-local-mode):

| Gate | Test | Pass criterion | Workaround if fail |
|---|---|---|---|
| **G1: Latest Oxygen changelog reviewed** | Read `docs/oxygen-docs/changelog/2026-05-*.md` (any newer than 2026-05-07) | No Builder Agent or Data App regressions named; `--local` reachability not negated by a recent change | If the changelog flags a regression, stop and surface |
| **G2: Build mode reachable in chat panel** | Open the SPA at `http://18.224.151.49/chat` (Basic Auth) AND at `http://oxygen-mvp.taildee698.ts.net:3000` (Tailnet); look for the Build/Ask mode toggle | Toggle visible, "Build" selectable | Hand-write YAML; tag as scaffolding-that-earns-its-keep; file gap to Oxy as a customer-feedback finding |
| **G3: Builder can read project YAML files** | In Build mode, ask Builder to read `semantics/views/requests.view.yml` | Builder returns file content; no permission error | Same workaround as G2 — hand-write |
| **G4: Builder can propose edits with HITL approval** | In Build mode, ask Builder to add a no-op comment to a scratch YAML file in the workspace | `FileChangePending` event surfaces; Reject leaves the file untouched | Same workaround as G2 |
| **G5: Data Apps render in the SPA** | Create a one-task `.app.yml` (just `SELECT 1`); run `oxy run apps/<name>.app.yml`; open the app browser in the SPA | App renders without error; chart placeholder appears | Hand-write `.app.yml`; verify rendering CLI-side via `oxy run`; document SPA gap |
| **G6: Builder's `run_app` tool works** | In Build mode, ask Builder to run the scratch app | Builder calls `run_app`, surfaces the result back as conversational context | Hand-write the build → test → refine loop; tag as scaffolding |
| **G7: No multi-workspace wizard gates Build mode** | Sign into the SPA in `--local` mode fresh; navigate to chat; confirm no "Create organization" wizard | Wizard not shown | Stop. This is the Session 25 blocker recurring; revisit `--local` mode assumption with Gordon |

Each gate's result is logged in the session note + (for failures)
written as an entry under `docs/limitations/` with `affects:` keyed to
the relevant Oxygen surface so the Answer Agent's trust contract picks
up the gap.

**Gate budget:** If G2–G6 are all green, proceed. If 1–2 of G2–G6 fail,
proceed with documented workarounds. If G7 fails OR 3+ of G2–G6 fail,
stop and surface to Gordon.

### Phase 2 — Pre-flight verification of the data

Before any Builder Agent session, verify what "rat complaints" looks
like in the data. Goal: have a crisp answer ready when Builder asks
about the filter.

Queries to run (all against the EC2 DuckDB):

```sql
-- 1. What request types contain "rat" or "rodent"?
SELECT request_type_id, request_type, COUNT(*) AS n
FROM main_gold.fct_311_requests f
JOIN main_gold.dim_request_type rt ON f.request_type_id = rt.request_type_id
WHERE LOWER(rt.request_type) LIKE '%rat%'
   OR LOWER(rt.request_type) LIKE '%rodent%'
GROUP BY 1, 2
ORDER BY n DESC;

-- 2. Row count by ward for the matching types
SELECT ward, COUNT(*) AS n
FROM main_gold.fct_311_requests f
JOIN main_gold.dim_request_type rt ON f.request_type_id = rt.request_type_id
WHERE LOWER(rt.request_type) LIKE '%rat%'
   OR LOWER(rt.request_type) LIKE '%rodent%'
GROUP BY 1
ORDER BY ward;

-- 3. Volume trend by year
SELECT YEAR(date_created_dt) AS yr, COUNT(*) AS n
FROM main_gold.fct_311_requests f
JOIN main_gold.dim_request_type rt ON f.request_type_id = rt.request_type_id
WHERE LOWER(rt.request_type) LIKE '%rat%'
   OR LOWER(rt.request_type) LIKE '%rodent%'
GROUP BY 1
ORDER BY 1;

-- 4. Resolution time available? (need a closed_dt or equivalent)
DESCRIBE main_gold.fct_311_requests;
```

Outputs are captured in `scratch/plan11_preflight/` as `.txt` files
(gitignored, evidence only). Findings get summarized in the session
note. The crisp answer to feed to Builder Agent: `the filter is
request_type IN (X, Y, Z)` or `the filter is LIKE '%rat%' OR LIKE
'%rodent%'`.

**If the source has no resolution-time column** (the limitations
registry only documents ward-level limitations, not resolution-time
columns explicitly): note it, propose a derivation if a `closed_dt`
exists, defer the resolution-speed angle to a follow-on plan if not.

### Phase 3 — Directional demo transcript drafted

Write the opening prompt the analyst (or Code, depending on who runs
the actual session) will use. Sketch the expected Builder Agent moves —
directional, not prescriptive. The actual session is the source of
truth; this is the prediction the retro compares against.

Opening prompt candidate (refine before execution):

> *I want a dashboard about rat complaints in Somerville. Four angles:*
>
> *1. Frequency — how often do rat complaints come in?*
> *2. Resolution speed — how long do they take to close?*
> *3. Volume trend — has it changed over time?*
> *4. Service equity — does the rate vary by ward?*
>
> *The fact table is `main_gold.fct_311_requests`; the request-type
> dimension is `main_gold.dim_request_type`. Add whatever measures
> you need to the semantic layer at `semantics/views/`. I'll approve
> each file edit individually.*

Expected Builder moves (directional sketch):
1. Reads `dim_request_type` to find the filter
2. Reads `requests.view.yml` to see the existing measures
3. Proposes new measures — probably `avg_resolution_days` and
   `resolution_rate` (if a `closed_dt` exists; if not, only `total_requests`
   and `open_requests`)
4. Drafts edits to `semantics/views/requests.view.yml` for new measures;
   HITL approval per edit
5. Drafts `apps/rat_complaints_by_ward.app.yml` with 4 tasks (one per
   angle) + 4 display blocks (probably: bar chart, line chart, bar
   chart by ward, summary card)
6. Calls `run_app`; reads result; iterates
7. Presents charts in chat; offers refinements

This sketch is the prediction. The retro (Phase 8) compares actual
moves to this and notes the deltas.

**This phase resolves carry-forward Question 1** (neighborhood scope).
The prompt above defaults to ward-only; Gordon's decision goes here.

### Phase 4 — Builder Agent construction session

Run the session in the SPA's Build mode at the URL determined by
Phase 1 (probably the Tailnet URL since Basic Auth on `/chat` might
not be Build-mode-friendly — verify in Phase 1, gate G2).

Capture the full transcript verbatim. The Oxygen runtime should retain
it in the chat panel; export to `docs/transcripts/plan-11-rat-complaints-builder-session.md`
(create `docs/transcripts/` if it doesn't exist).

HITL approvals happen as the session runs. The analyst (or Code, per
the operator-of-the-session decision) reads each `FileChangePending`
and approves or rejects.

Outputs:
- `apps/rat_complaints_by_ward.app.yml` (Builder-drafted, analyst-approved)
- Edits to `semantics/views/requests.view.yml` for any new measures
- The captured transcript at `docs/transcripts/`

**Gate within phase 4:** If Builder Agent gets stuck — e.g., proposes
SQL that errors, can't reach `run_app`, the conversation loses thread —
note the failure mode and either work around it (rephrase, hand-edit
the file, hand-craft the SQL) or stop the session and surface to Gordon.

### Phase 5 — Trust signal integration

The analyst-experience claim for MVP 2 is *dashboards carry the same
trust contract chat carries.* Verify the dashboard surfaces:

- **Last refreshed** — from `main_admin.fct_pipeline_run_raw.run_completed_at`
  WHERE `run_status='success'` ORDER BY 1 DESC LIMIT 1. Either Builder
  Agent proposes a task for this, or the analyst prompts for it
  explicitly. Document which it was.
- **Citations** — each chart's "where this data comes from" line names
  the source view (`main_gold.fct_311_requests` + the relevant `.view.yml`)
- **Relevant limitations** — at minimum, [`location-ward-block-only.md`](../limitations/location-ward-block-only.md)
  is referenced on the ward-keyed charts. Survey limitations
  ([`2024-survey-columns-sparse.md`](../limitations/2024-survey-columns-sparse.md),
  [`survey-columns-on-fact.md`](../limitations/survey-columns-on-fact.md))
  do NOT apply to rat complaints and should not surface.

If Builder Agent didn't include trust signals on its own, the analyst
prompts for them in the same session. The retro (Phase 8) notes whether
Builder proposed trust signals unprompted — this is part of the
customer-feedback finding back to Oxy.

**This phase resolves carry-forward Question 2** (transcript as portal
artifact). Gordon's decision goes here. If the answer is "yes, expose
the transcript on the portal," add it as part of the `/dashboards`
listing in Phase 6.

### Phase 6 — Portal integration

Create the `/dashboards` index route (name is Code's call — could be
`/apps`, `/dashboards`, `/decks`; whichever aligns with the other
portal routes `/docs`, `/erd`, `/metrics`, `/profile`, `/trust`).

The listing entry for rat complaints:
- Title
- Short description (1-2 sentences)
- Last refreshed (read from `fct_pipeline_run_raw`)
- Click-through link to the SPA's Data App view (URL TBD by Phase 1
  verification — Tailnet or `/chat`-prefixed nginx route)

Generator pattern decision:
- **If the pattern matches** the existing `/metrics`, `/trust`,
  `/profile`, `/erd` generator pattern (script generates HTML from a
  YAML/SQL source of truth on each `./run.sh`), build a generator:
  `scripts/generate_dashboards_page.py`. Source of truth: `apps/*.app.yml`
  metadata. nginx config gains `location = /dashboards`.
- **If not** (e.g., only one dashboard for now, generator is premature),
  hand-write `portal/dashboards.html` for the first iteration. Queue
  the generator as a follow-up.

Generator-vs-hand-write is Code's call based on what shape the data
takes by Phase 6.

### Phase 7 — Honest limitations

Update or create entries under `docs/limitations/` for any gap
surfaced during construction. Candidates surfaced ahead of execution:

- **ward-only-not-neighborhood** — if Phase 3 defaults to ward-only,
  the existing `location-ward-block-only.md` covers this. No new entry.
- **builder-mode-local-gap-X** — if Phase 1 gate G2–G6 surfaces a gap,
  write an entry. Each gap is one entry with `affects:` keyed to the
  failing surface.
- **rat-no-resolution-time** — if Phase 2 reveals no `closed_dt` or
  equivalent, the resolution-speed angle gets deferred and a limitation
  entry documents the gap.

Run `scripts/build_limitations_index.py` after writing new entries so
`docs/limitations/_index.yaml` regenerates and the Answer Agent picks
up the new limitations on next start.

### Phase 8 — Light retro

Session note for Plan 11 execution includes a brief retro comparing
the actual Builder Agent session against the Phase 3 directional
sketch:

- What did Builder do that matched the sketch?
- What did it do differently?
- What was harder/easier than expected?
- What's worth feeding back to Oxy as customer feedback?
- Any new entries warranted for PRODUCT_NOTES.md?

This retro is the analyst's-eye-view input to PRODUCT_NOTES.md Entry 4
("The project as Oxy customer-feedback loop") and may surface follow-on
entries.

### Phase 9 — Sign-off

**Static-artifact gates:**
- [ ] `apps/rat_complaints_by_ward.app.yml` exists and validates via
  `oxy validate` (or `airlayer query -x` for any new view edits)
- [ ] `semantics/views/requests.view.yml` (or other view files) updated
  with whatever measures Builder proposed; descriptions on every new
  measure
- [ ] `docs/limitations/` entries exist for any gaps surfaced; `_index.yaml`
  regenerated
- [ ] `/dashboards` listing added (generated or hand-written)
- [ ] `docs/transcripts/plan-11-rat-complaints-builder-session.md`
  saved

**Live-functional gates (re-verified in the sign-off session per CLAUDE.md
verification-gates discipline):**
- [ ] Builder Agent constructed each of the four angles (transcript
  saved)
- [ ] Data App renders all charts in the SPA at the URL determined by
  Phase 1
- [ ] `/dashboards` page links resolve to the Data App
- [ ] `/trust` surfaces the ward-bronze-only limitation when the
  Answer Agent is queried about rat complaints (run a question against
  `oxy run agents/answer_agent.agent.yml` and confirm)
- [ ] "Last refreshed" on the dashboard reads accurately against the
  most recent successful row in `fct_pipeline_run_raw`

---

## Out of scope for Plan 11

- Additional dashboards beyond rat complaints (queued as follow-on plans)
- Clean `dim_location` / neighborhood dimension (deferred to MVP 3 —
  unless carry-forward Question 1 resolves otherwise)
- Survey-by-ward extension (queued as follow-on; decided in Chat that
  Q1 is the single anchor, not Q1 + survey)
- In-chat visual artifacts (deferred indefinitely)
- Resident-facing framing (deferred indefinitely per [BUILD.md §8](../../BUILD.md#8-scope-boundaries))
- The two carry-forward questions (neighborhood scope, transcript as
  portal artifact) — both are flagged inline; do NOT pre-decide

---

## Commit shape

- **Scoping commit (this session):** just this plan file + LOG.md +
  TASKS.md.
- **Execution commits (separate session, post-review):**
  - Phase 1 verification + limitations entries (one commit per gate
    that produces an artifact)
  - Phase 2 pre-flight findings (likely no commit — evidence is in
    `scratch/`)
  - Phase 4 outputs (`.app.yml` + view edits + transcript)
  - Phase 6 portal integration
  - Phase 7 final limitations sweep + `_index.yaml` regen
  - Phase 9 sign-off commit closing the plan

---

## Hand-back instructions

After this scoping document is committed and pushed, surface to Gordon
for review. Gordon decides:

1. Execute Plan 11 as written.
2. Refine specific phases before execution (especially the
   carry-forward questions).
3. Reshape the plan if the pre-flight assumptions look wrong.

No execution work happens until Gordon's review lands. The session note
for this scoping pass (Session 34) explicitly frames the deliverable
as "scoping only; execution pending review."

---

## Risk register (named so future-Code can re-check)

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Build mode not reachable in `--local` | medium | high — plan reshape | Phase 1 gates G2–G6; documented workarounds; gate budget |
| Multi-workspace wizard re-appears | low | very high — Session 25 redux | Phase 1 gate G7; hard stop |
| No `closed_dt` for resolution-time angle | medium | medium — angle deferred | Phase 2 query 4; deferral planned; limitations entry |
| Builder Agent proposes SQL that errors | high | low — iterate in-session | Documented in-phase workaround |
| Ward-only is wrong scope (Gordon wants neighborhood now) | low | medium — phase 3 reshape | Carry-forward Q1; resolved before Phase 3 |
| Transcript as portal artifact (carry-forward Q2) | low | low — extra Phase 6 work | Resolved before Phase 5 |
| `oxy validate` doesn't catch a runtime SPA rendering bug | medium | low — discovered in sign-off | Live-functional gate at Phase 9 |
