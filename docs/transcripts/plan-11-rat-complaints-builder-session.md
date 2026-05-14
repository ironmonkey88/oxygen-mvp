# Plan 11 Phase 4 — Builder Agent construction session

**Date:** 2026-05-13 22:32 → 23:30 UTC (suspended @ 22:42, cancelled @ 23:30 after token-budget hang)
**Run ID:** `197bbc81-5fb0-49c6-a65e-e4a9ba88650a`
**Domain:** `builder`
**Operator:** Code (overnight execution)
**Verbatim event log:** [`plan-11-builder-phase-4-raw-events.jsonl`](plan-11-builder-phase-4-raw-events.jsonl)

## Question posed

The opening prompt is captured verbatim in `/tmp/plan11_phase4_question.txt`
and reproduced in the JSONL event log. Three paragraphs naming the
four angles (frequency, resolution speed, volume trend, service
equity), the four-value rat-filter (with the trailing-space `School
Rodent Control` quirk), the five required source tables, the
resolution-time derivation guidance, and the trust-signals
expectations.

## What Builder did

The agent followed essentially the expected sequence from the
directional transcript. Per the JSONL event log:

1. **`search_files`** — found `apps/`, confirmed empty (no existing
   rat-complaints app)
2. **`read_file`** on `semantics/views/requests.view.yml` — 58 lines,
   confirmed the existing measures
3. **`read_file`** on `dbt/models/gold/schema.yml` (partial) —
   confirmed the column types in `fct_311_requests`
4. **`execute_sql`** four times against live data:
   - Total rat complaints: **14,036** (matches Phase 2 pre-flight)
   - Resolution-speed buckets (Builder's own bucket boundaries):
     0d=3,157 / 1-3d=2,827 / 4-7d=1,318 / 8-30d=989 /
     31-90d=418 / 91-365d=895 / 365+d=3,060
   - Volume by year: 2015–2026 matches Phase 2 ±5%
     (slight differences are timezone / refresh-cadence rounding)
   - Complaints by ward: 7 wards × counts, **plus Builder added
     `complaints_per_sqkm` on its own initiative** — Ward 1
     2,691@1003/sqkm, Ward 3 2,155@1694/sqkm (Ward 3 is densest
     for rats)
5. **`execute_sql`** once more — last_refreshed from
   `main_admin.fct_pipeline_run_raw` → `2026-05-12 04:18:17`
6. **Text generation toward the file write** — but Builder hit the
   4096-token output limit at seq 51 and suspended with
   `awaiting_input` asking *"Continue with double the budget
   (8192 tokens)?"*

## What didn't work

Submitted `oxy agentic answer --answer "Continue with double budget"`
at 22:42:56 UTC. The CLI confirmed `Answer submitted for run ...`
but the run did not resume. `oxy agentic inspect` reported
`status: running` indefinitely with no new events through 23:30 UTC.
The original `oxy agentic run` client process held a connection but
never received resume events. Cancelled the run via
`oxy agentic cancel`.

Documented in
[`docs/limitations/plan-11-builder-cli-token-budget-hang.md`](../limitations/plan-11-builder-cli-token-budget-hang.md)
as a customer-feedback finding for Oxy.

## Workaround taken — hand-write with Builder's verified queries

Per the Plan 11 gate-budget framing, hand-writing the `.app.yml` is
an explicit fallback. The file at
[`apps/rat_complaints_by_ward.app.yml`](../../apps/rat_complaints_by_ward.app.yml)
uses **Builder's exact SQL queries** (extracted from the JSONL event
log seq 28–45) reformatted into the Oxygen Data App schema. The
queries are not Code-invented — they're Builder-authored and
Builder-verified against live data.

Three things Builder would have done if the file-write hadn't hung,
that I had to add in the hand-write:

1. **Display block structure.** Builder's text generation had reached
   the point of "Now let me build the app file" but not produced
   YAML. I followed the directional transcript's expected shape:
   markdown intro, table for `last_refreshed`, table for total,
   bar_chart for ward (×2 — counts + density), line_chart for year,
   bar_chart for resolution buckets, markdown footer with citations
   + limitations.
2. **Trust signal markdown.** Citations footer and known-limitations
   footer were prompted in the opening question but Builder hadn't
   gotten to them.
3. **Plan 11 limitation refs.** The two new limitation IDs
   (`plan-11-builder-cli-token-budget-hang`,
   `dashboard-render-spa-only`) were written this session; the
   in-app markdown links to `location-ward-block-only` and the
   prose on the Open + In Progress 9.6% gap reference Plan 12's
   existing limitations.

## Retro (Phase 8)

### Matched the directional transcript

- 4 verification queries before file-write ✓ (directional sketch step 4)
- Filter validated against `dim_request_type` ✓
- Resolution-time derivation matched (`most_recent_status_dt -
  date_created_dt`) ✓
- Builder uses `execute_sql`, not a dedicated `run_app` tool ✓
  (the Phase 1 G6 finding — confirmed again in Phase 4)

### Diverged from the directional transcript

- **Builder added `complaints_per_sqkm`** on its own initiative.
  Smart addition: ward area_sqkm was in the data sources I listed,
  Builder picked up the analytic intent. Worth a 2nd bar chart for
  the density view. Surfaced in the final app.
- **Builder did NOT propose semantic-layer additions.** The
  directional sketch said "may suggest" new measures on
  `requests.view.yml`. The opening prompt explicitly said "Don't add
  any new measures to the semantic layer — keep all SQL inline."
  Builder respected that.
- **Builder DID NOT propose trust signals on its own** before
  hitting the budget. The directional sketch's prediction holds —
  trust signals come from analyst prompting, not Builder defaulting.
  This is the actionable customer-feedback for Oxy: Builder Agent
  should default-include trust signals on `.app.yml` proposals
  unless explicitly told not to.

### What was harder than expected

- **Token budget on `.app.yml`-sized files.** 4K tokens is enough
  for SQL-generation but not for a 4-task + 5-display Data App
  file. The CLI's "Continue with double budget" path was the right
  shape conceptually but executed into a state-machine hang.
- **Visual render verification.** Code overnight has no SPA access
  (Chrome MCP extension not connected). The Data App's chart
  rendering can only be confirmed by a human operator opening the
  SPA in a browser. Captured in
  [`dashboard-render-spa-only.md`](../limitations/dashboard-render-spa-only.md).

### What was easier than expected

- **Builder's data-verification accuracy.** Every query returned
  numbers consistent with my Phase 2 pre-flight (within
  refresh-rounding). Builder did real verification, not just
  pattern-matching to the prompt.
- **Builder Agent CLI is real.** Phase 1 G2–G6 framing assumed SPA
  access was the only path. Discovering `oxy agentic run --domain
  builder` works at the CLI was the load-bearing pre-flight win.

### Customer feedback for Oxy

1. **CLI hang on token-budget continuation.** State-machine
   resume bug. High-confidence finding; reported in
   `plan-11-builder-cli-token-budget-hang.md`.
2. **Builder should default-include trust signals on `.app.yml`
   proposals.** Citations + freshness + relevant limitations should
   be a Builder-side default, not analyst-prompted. The trust
   contract has earned its place.
3. **CLI rendering for Data Apps would close the operator-context
   gap.** A `oxy run apps/<name>.app.yml --output html` flag (or
   `oxy app render <name>`) would let CI / overnight Code workflows
   verify dashboards end-to-end. Currently SPA-only.

### Any new PRODUCT_NOTES.md entries?

Yes — implicit. The CLI-vs-SPA operator-context gap is the kind of
"self-extension" pattern PRODUCT_NOTES.md Entry 3 names. As Code's
ability to drive Builder via CLI matures, the "knowledge-graph
expansion" pattern (Entry 1) becomes more realistically scriptable.
Worth a future PRODUCT_NOTES update but not in Plan 11.
