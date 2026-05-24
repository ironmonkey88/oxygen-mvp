# Handoff for next Code session — 2026-05-24

Written at end of an extended multi-prompt thread covering Plans 32–40
(Sessions 57–65 in the project record). Much of what previous handoffs
carried as "gotchas to remember" has been promoted to `CLAUDE.md` /
`session-starter.md` / memory files during this thread — this doc
intentionally doesn't repeat that content. Focus is on what's specific
to picking up *next*.

## Boot sequence

`session-starter.md` → "Code's Operating Environment (Brief)" + the
`feedback_session_boot_audit` memory now carry the canonical 4-check
audit. Run it first. Plan 34's B1 step-4-extension (the
`portal/index.html` drift check) is part of step 4 — apply per the
checklist.

## Current state at session end

- **`origin/main` at `986c9d3`** (Plan 40 merge). Local + EC2 both
  fast-forwarded.
- **0 open PRs.**
- **EC2 working tree clean** — no `portal/index.html` drift, no
  untracked accretions. `.oxy_state/` is gitignored as of Plan 34.
- **DBA dashboard `/admin` live** (Tailnet-only at `http://oxygen-mvp/admin/`):
  - Platform: YELLOW
  - 4 advisory items: A2 streak 12/13 days, A3 duration +30% vs 30d
    median, **B1 2/6 sources non-healthy (crime + traffic-citations
    both 26 days stale — real signal, see below)**, B2 117/118 dbt
    tests + 1 warn
  - C2 cost panel: $43.65 month-to-date (Opus 4.7 flat-rate); no
    burn-rate-vs-last-month baseline until June 1 (project's first
    chat was 2026-05-11)
  - All 10 panels carry `data-panel-id="A1"`..`"D2"` attributes; the
    Plan 33 helper's `targets_selector='[data-panel-id]'` path is
    proven (Plan 39 P + Plan 40 D3)
- **6 source-health timers active**: 311 + crime + permits +
  traffic-citations + wards + at-a-glance. Each fires hourly at
  different minute offsets (0, 5, 10, 15, 20, 25) to spread load.

## What landed since the 2026-05-21 handoff

- **Plans 32–35 — the back-link saga.** Plan 32 halted (`<div>` wrap
  didn't fix the dbt-docs rendering). Plan 33 built the
  rendered-page Playwright helper + identified marked.js with
  `sanitize: true` as the root cause. Plan 34 + 35 shipped plain
  Markdown for both back-links (top in Plan 34, bottom in Plan 35).
- **Plan 36 — allowlist audit** (information request) at
  `docs/audits/allowlist-audit-2026-05-22.md`.
- **Plan 37 — gh Tier-1 additions + redundancy cleanup + hook
  precedence note.**
- **Plan 38 — DBA dashboard v1** (Phase A chat-state integration +
  Phase B generator/nginx/systemd). Phase A halt-and-surfaced on the
  Anthropic-spend finding (`messages.input_tokens` columns exist).
- **Plan 39 — Track C tidy-day + Playwright `targets_selector`.** 41
  stale branches deleted; `data_type` annotations across bronze +
  gold schema.yml; `targets_selector` parameter added to
  `review_page()`. Track D split to Plan 40.
- **Verdict-first dashboard family design doc** at
  `docs/dashboard-family-design-2026-05-22.md`. Doc-only PR #67. No
  plan numbers claimed yet — implementation plans will assign at
  fire time per the project's slot-resolution discipline.
- **Plan 40 — DBA dashboard v1.1.** Cost panel replacement (MTD +
  sparkline + burn-rate), B1 expanded 1→6 sources, design doc
  revised, Playwright verification.

## Plans queued / reserved

In TASKS.md "Next Focus" order:

- **Plan 41 (reserved):** DBA v1.2 calibration. Staleness thresholds
  on B1 may be too tight — crime + traffic-citations being 26 days
  stale is *real* (source's actual cadence is what it is, not the
  daily-refresh the project assumed). Two routes: (a) relax the
  per-dataset threshold, (b) update the corresponding limitations
  entries to document the actual cadence. Also A3 duration trend's
  ±20% threshold is too tight at project scale — one slow run
  triggers yellow. **Best fired after a few weeks of v1.1 data
  accumulates so calibration is grounded in actual signal patterns,
  not v1.1 day-one snapshot.**
- **Plan 42 (reserved):** Memory-to-file migrations per Plan 36 §3.
  5 candidates documented in TASKS.md. Thrice-deferred (was Plan 38,
  then 40, then 41, now 42). Wants a deliberate placement +
  wording conversation, not bolt-on.
- **Plan 24 (reserved, MVP 3):** Happiness Survey silver/gold
  curation. Plan 23 Phase D halted on the cross-wave-presence gate
  (8/50 columns survived). Plan 24 picks it up as a dedicated MVP 3
  plan covering wave-key harmonization + k-anonymity gates +
  weighting.
- **Plans 18 + 19 (deferred):** Builder-CLI dashboards. Each wants
  its own fresh Code thread with interactive Builder CLI session.
- **Verdict-first dashboard family (no plan numbers yet):** seven
  named plans in the family design doc §10 (template infrastructure,
  Rat DB v2, Crime categorization, Crime 360, housing ingestion,
  environmental ingestion, Top to Bottom). Heavy strategic
  build-out; each piece needs its own prompt.

## Decisions waiting on Gordon

1. **Crime + traffic-citations staleness:** are these sources
   actually monthly-or-sparser refresh (in which case the threshold
   should match) or genuinely lagging upstream (in which case the
   panel's YELLOW is the right signal)? Either way the limitations
   entries need a check. Folds into Plan 41.
2. **Verdict-first dashboard family kickoff timing:** the design
   doc landed without plan slots reserved. Implementation is
   substantial (7+ plans, multiple data ingestions blocking the
   capstone Top to Bottom page). Pick a starting point when ready —
   the template infrastructure is the natural first plan.
3. **Plan 41 vs Plan 42 ordering:** Plan 41 benefits from waiting
   for data accumulation; Plan 42 benefits from a quiet thread.
   Either can fire first when the time feels right.

## Patterns worth carrying forward

- **Mid-session scope split worked twice this thread.** Plan 38
  deferred Track C to Plan 39; Plan 39 deferred Track D to Plan 40.
  Both splits were surfaced via `AskUserQuestion` mid-execution
  when scope-creep became real. The pattern: when a sub-track's
  realistic time pushes the session into "rushed end" territory,
  surface the option to split rather than ship lower-quality work.
- **The Plan 33 / 39 / 40 stack — Playwright helper + `targets_selector`
  + `data-panel-id` attributes — is mature.** Future dashboard work
  should default to this verification path (helper + per-panel
  callouts via data-panel-id). The pattern produced clean evidence
  artifacts in PRs #65 (v1), #66 (smoke), #68 (v1.1).
- **Pre-flight investigation has produced "the prompt's premise
  was wrong" findings twice recently** (Plan 38 Phase A schema
  inspection; Plan 40 D2 Socrata-API uniformity). Both got
  surfaced cleanly via halt-and-surface or design-call commit
  framing. The honest answer to "the prompt assumed X but the
  data shows Y" is to surface the gap before committing to X's
  implementation.
- **`gh pr merge --merge --delete-branch`** as the routine merge
  command has eliminated the stale-branch accumulation Plan 39 C1
  found 41 of. Keep this discipline; future cleanups should be
  zero or near-zero.

## Receipt-workflow reminder

The receipt-workflow lesson from Plan 28 (and now in
`feedback_chat_code_handoff` memory) keeps producing value: when a
paste arrives without a PROMPTS.md header, `AskUserQuestion`
beats guessing intent. This thread used it at least 4 times —
Plan 36's PR-shape question, Plan 38's token-spend scope, Plan 39's
C3 effort question, Plan 39's Track D split, the dashboard family
design doc save-only-vs-wire question. Every one resolved cleanly
because the option to halt and ask is now muscle memory.

## Two-line summary if Gordon's resuming cold

You closed Plan 40 at 2026-05-24 10:28 ET. Next eligible plan
number is 41 (DBA v1.2 calibration, best after data accumulates).
DBA dashboard live YELLOW with real-stale findings from B1 6-source
expansion. Verdict-first family design doc is ready to be picked
up whenever; no plan number claimed.
