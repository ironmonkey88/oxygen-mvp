# Report — Prompt + report lineage in `docs/prompts/`

**Companion to:** [`plan-43-prompt-report-lineage.md`](plan-43-prompt-report-lineage.md)
**Session:** [66](../sessions/session-66-2026-05-24-plan-43-prompt-report-lineage.md)
**PR:** [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70)
**Date:** 2026-05-24

---

## Gate table

| Scope | Status | PR |
|---|---|---|
| A1 — `docs/prompts/` + `README.md` | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| A2 — `plan-37-allowlist-edits.md` backfill | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| A2 — `plan-38-dba-dashboard.md` backfill | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| A2 — `plan-39-tidy-c-playwright.md` backfill | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| B1 — PROMPTS.md §5 Step 4 + Step 9 + §5.5 | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| B2 — CLAUDE.md "Receiving prompts from Chat" 4th bullet | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| B3 — session-starter.md "How We Work Together" + "Key Files to Know" | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| C1 — LOG.md Plans Registry row | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| C2 — TASKS.md row `[~]` → `[x]` | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| C3 — session file (Session 66) | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| C4 — LOG.md Last Updated bumped | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (`afca004`) |
| C5 — Reconcile with Plan 42 state | complete (no-op — Plan 42 not in flight) | n/a |
| Smoke test — Plan 43 prompt + report files exist | complete | [#70](https://github.com/ironmonkey88/oxygen-mvp/pull/70) (this commit) |

## Shipped

- **`docs/prompts/` directory created** with [`README.md`](README.md) defining filename convention (`plan-NN-<slug>.md` for prompts; sibling `.report.md` for reports), lifecycle, lineage chain, backfill policy, coexistence with `docs/handoffs/`, and a "what doesn't belong here" section that points at `docs/plans/`, `docs/design-reviews/`, `docs/audits/`, `docs/limitations/`.
- **Three backfilled prompts** with explicit `**Status:** reconstructed` notes at top citing sources + confidence:
  - [`plan-37-allowlist-edits.md`](plan-37-allowlist-edits.md) — sources: session-62 + audit + TASKS/LOG rows. Tracks A/B/C reconstructed from highly explicit session narrative.
  - [`plan-38-dba-dashboard.md`](plan-38-dba-dashboard.md) — sources: dba-dashboard-design-2026-05-17.md + session-63 + limitations entry + TASKS/LOG. §A2 halt-condition wording marked `(reconstructed, medium confidence)`.
  - [`plan-39-tidy-c-playwright.md`](plan-39-tidy-c-playwright.md) — sources: session-64 + smoke-test artifact + design doc (for Track D's intended scope). Track D's intended (pre-split) scope marked `(reconstructed, medium confidence)`.
- **Live Plan 43 prompt** at [`plan-43-prompt-report-lineage.md`](plan-43-prompt-report-lineage.md) — copied verbatim from the paste as the first execution step per the prompt's Notes-for-Code clause. This is the smoke test's input.
- **PROMPTS.md** §5 Step 4 amendment (when prompt arrived as file, restatement appends to the file as a `**Code's restatement:**` paragraph in addition to terminal); §5 Step 9 amendment (when prompt arrived as file, report writes to sibling `.report.md` in addition to terminal; typically last commit on PR branch before merge); new §5.5 subsection naming the convention with pointer to `docs/prompts/README.md`.
- **CLAUDE.md** "Receiving prompts from Chat" — 4th internalized bullet added (3 → 4 rules) describing the file convention with pointers to PROMPTS.md §5.5 + README.
- **session-starter.md** "How We Work Together" — new bullet pointing at `docs/prompts/` as sibling to the existing PROMPTS.md bullet. "Key Files to Know" Also-searchable paragraph — `docs/prompts/` added alongside `docs/plans/`, `docs/sessions/`, `docs/handoffs/`, `docs/limitations/`, `docs/transcripts/`.
- **LOG.md** — Plan 43 row added to Plans Registry at top of the recent reverse-chronological cluster (after Plan 32, before Plan 40); "Last Updated" bumped to 2026-05-24 17:57 ET; Session 66 Recent entry added; Session 61 rotated to Earlier per the 5-entry cap.
- **TASKS.md** — Plan 43 row added (initially `[~]`), then flipped `[x]` at session close.
- **Session file** at [`docs/sessions/session-66-2026-05-24-plan-43-prompt-report-lineage.md`](../sessions/session-66-2026-05-24-plan-43-prompt-report-lineage.md) — frontmatter conforming to CLAUDE.md sessions-logging-protocol vocabulary, five-section body.
- **This report file** — the smoke-test output, written as the last commit on the PR branch before merge per the new §5 Step 9 amendment.

## Worth flagging

- **Smoke-test convention is now production-tested.** The Plan 43 prompt itself exercised the new convention end-to-end on its own birth session: paste arrived → Code copied verbatim into the file as first execution step → all phases ran → this report file lands as the last commit before merge. Future prompts that arrive as files (via GitHub MCP when Gordon's settings wiring lands) will skip the "copy from paste" step and run the rest unchanged.
- **Plan 42 (memory-to-file migrations) needs to rebase on this plan's PROMPTS.md edits when it eventually runs.** Specifically, Plan 42 plans to absorb `feedback_chat_code_handoff.md` content into PROMPTS.md §5 or a new §6 — this plan added §5.5 in that region, so Plan 42's PROMPTS.md edits will need to account for the new structure. Halt condition #1 of Plan 43 (no concurrent Plan 42 PR) held throughout; Plan 42 remains reserved.
- **Reconstruction faithfulness was the main judgment call.** Each backfilled prompt is grounded in its session narrative for what was *delivered*; the prompt's exact original phrasing is inferred (medium confidence on §A2 halt-condition wording for Plan 38 and Track D scope for Plan 39). The `**Status:** reconstructed` note at the top of each file makes that distinction explicit. If Gordon spots a meaningful difference between any backfilled prompt and what he actually wrote, the fix is to revise the file in a follow-up commit and update the confidence marker — the convention supports that.
- **EC2 has pre-existing regen drift unrelated to this plan.** Boot audit found `docs/limitations/_index.yaml` + `portal/index.html` modified on EC2 (likely a `./run.sh` cycle between the 2026-05-24 handoff write and this session's open). This plan didn't touch EC2 or those files; the drift remains untouched and is a separate hygiene item.
- **Untracked `docs/quick-dives/builder-agent.md` was deliberately excluded from this PR.** It's a well-formed orientation note in the local working tree, not part of any commit. Likely queued for the verdict-first dashboard family work or a forgotten earlier commit. Gordon can decide commit / move / discard in a future session.

## Ready for more work — natural next moves

- **Plan 41 (DBA v1.2 calibration)** — best fired after a few weeks of v1.1 data accumulates so threshold-tuning is grounded in actual signal patterns.
- **Plan 42 (memory-to-file migrations)** — needs the deliberate placement + wording conversation per Plan 36's audit recommendation. Now that PROMPTS.md has the §5.5 region landed, Plan 42's `feedback_chat_code_handoff.md` absorption can target an adjacent placement.
- **First "real" prompt arriving via the new convention.** When Chat side commits a prompt directly to `docs/prompts/plan-NN-<slug>.md` (with or without GitHub MCP), Code can validate the full file-side path: Step 4 restatement appended to the file, Step 9 report written to the sibling `.report.md`, both in the same PR as the work commit. This plan's smoke test exercised the convention but the paste-arrival → copy-to-file step is the one that goes away when Chat commits directly.
- **Untracked `docs/quick-dives/builder-agent.md` decision** — small loose end on Gordon's side.
