# Prompt — Prompt + report lineage in `docs/prompts/`

**Kind:** coding
**Date:** 2026-05-24
**Plan:** 43 (per LOG.md Plans Registry: Plan 41 reserved for DBA v1.2 calibration, Plan 42 reserved for memory-to-file migrations, Plan 43 is the next contiguous slot)
**Scope:** new `docs/prompts/` directory; edits to `PROMPTS.md`, `CLAUDE.md`, `session-starter.md`, `LOG.md`, `TASKS.md`
**Effort:** one session, ~1-2 hours
**Depends on:** Nothing currently in-flight. Plan 42 (memory-to-file migrations) is still reserved, not started — so its planned PROMPTS.md edit (`feedback_chat_code_handoff.md` content into §5 or a new §6) hasn't landed yet. **This plan and Plan 42 must not run concurrently.** Run them serially in either order; whoever ships second rebases on whoever shipped first.

---

## Outcome

Chat-issued prompts and Code-issued reports become durable, lineage-bearing artifacts in the repo rather than transient paste-buffer text. An analyst (or Gordon, or a future Chat session) can find what was asked for in Plan N and what came back from Plan N as two files in a known directory, both indexed by project knowledge, both diffable in git. The current loop — Chat writes a prompt, Gordon pastes it into Code, Code executes, Code reports back in terminal, Gordon pastes the report into Chat — survives intact for sessions that don't use the new convention, but a new shape opens up: Chat writes the prompt to a file (eventually committed via the GitHub MCP connector being added in Phase 1 of this initiative); Code reads it from disk; Code writes a sibling report file on completion. The paste loop becomes optional; the lineage chain (plan slot → prompt file → session file → report file → PR) becomes explicit and greppable.

## Context

This plan is the materialization phase of a conversation about smoothing the Chat ↔ Code handoff. The decision was: connect GitHub MCP to this Claude project (Phase 1, Gordon's settings work), establish the prompt-and-report file convention in the repo (this plan, Phase 2), and defer the autonomous-Code-runner question (Phase 3) until we've lived in the new shape for some sessions.

A few things to know that shaped this prompt:

- **Prompts get lost today.** They live in Chat scrollback; once pasted, they're hard to find. The lineage `Plan N → prompt → session → report → PR` is implicit, reconstructed by inference from LOG.md rows and session files.
- **The current paste loop has two pains, only one of which a file fixes.** The error-proneness of copy-paste was actually a phantom (paste is fine for short prompts and reports). The lineage pain is real and is what this plan addresses.
- **Plan 42 also touches PROMPTS.md.** Specifically, `feedback_chat_code_handoff.md` is slated to be absorbed into PROMPTS.md §5 or a new §6 per the Plan 36 audit at `docs/audits/allowlist-audit-2026-05-22.md`. Plan 42 hasn't been scoped or executed yet — it's still reserved in TASKS.md. If Plan 42 ships before this one, this plan's PROMPTS.md edits land on top of Plan 42's. If this one ships first, Plan 42 will see a slightly evolved PROMPTS.md when it runs. Either ordering is fine; the constraint is **don't run them concurrently** — open PRs against the same §5/§6 region would conflict.
- **GitHub MCP may or may not be live on Chat side.** Gordon is wiring it up in parallel. The new convention works whether MCP is connected or not — without MCP, prompts get to the repo the old way (download .md from Chat, `git add`, commit); with MCP, Chat commits them directly. The file convention is the same either way.
- **Backfill is part of scope.** Three recent prompts (37, 38, 39) get reconstructed from their session narratives and LOG rows and committed to the new directory with a clear "reconstructed" note. They give the directory a real corpus to look at from day one.

## Work

**Phase A — establish the directory and convention.**

A1. Create `docs/prompts/` with a `README.md` that names the convention. Cover:

- **Filename pattern.** `plan-NN-<slug>.md` for the prompt; `plan-NN-<slug>.report.md` for the report. Slug matches LOG.md Plans Registry slug where one exists.
- **What goes in the prompt file.** The full PROMPTS.md-shaped prompt (header + Outcome + Work + Verification + Halt conditions + Out-of-scope + Commit shape). Verbatim what Chat would otherwise paste.
- **What goes in the report file.** Code's report-back from PROMPTS.md §5 Step 9 — the gate table, Shipped, Worth flagging, Ready for more work. Same content as the terminal report-back; the file is the durable home for it.
- **Lifecycle.** Prompt commits → Code executes per PROMPTS.md §5 → Code commits report alongside → cycle complete. The prompt file is "consumed" when its sibling report file exists.
- **Lineage chain.** plan slot in LOG.md Plans Registry ↔ `docs/prompts/plan-NN-<slug>.md` ↔ `docs/sessions/session-NN-YYYY-MM-DD-plan-NN-<slug>.md` ↔ `docs/prompts/plan-NN-<slug>.report.md` ↔ PR #.
- **Backfill policy.** Reconstructions are marked at the top: `**Status:** reconstructed from session narrative — not the original Chat-issued prompt.` Going forward, prompts land verbatim from Chat.
- **Coexistence with `docs/handoffs/`.** Handoffs are end-of-thread Code → Chat summaries spanning multiple plans; prompt+report files are per-work-item. Both stay.

A2. Backfill three reconstructed prompts:

- `docs/prompts/plan-37-allowlist-edits.md` — Track A (gh PR/merge Tier-1 additions), Track B (7 redundant entries removed), Track C (hook-precedence note in CLAUDE.md "Known gotchas"). Source: `docs/sessions/session-62-2026-05-23-plan-37-allowlist-edits.md`, `docs/audits/allowlist-audit-2026-05-22.md`, TASKS.md Plan 37 row.
- `docs/prompts/plan-38-dba-dashboard.md` — Phase A (chat-state integration, halt-gated; `dlt/oxy_chat_activity_pipeline.py`, `main_admin.fct_chat_activity_raw`) + Phase B (dashboard generator + nginx Tailnet-only `/admin` + systemd 15-min timer + Playwright). Source: `docs/dba-dashboard-design-2026-05-17.md`, `docs/sessions/session-63-2026-05-23-plan-38-dba-dashboard.md`, TASKS.md Plan 38 row.
- `docs/prompts/plan-39-tidy-c-playwright.md` — Track C (4 tidy-day items: stale-branch cleanup, session-starter Code-Operating-Environment section, schema.yml data_type annotations, TASKS item 13), Track P (Playwright `targets_selector` parameter on `scripts/rendered_page.py`), Track D (DBA v1.1, ultimately split to Plan 40 mid-execution). Source: `docs/sessions/session-64-2026-05-23-plan-39-tidy-c-playwright.md`, TASKS.md Plan 39 row.

Each reconstruction follows PROMPTS.md §3 shape. Each carries the reconstruction note at top. Reports for these are NOT backfilled — only the prompts. (The session files already hold the report-equivalent content; backfilling reports would be busywork without lineage value.)

**Phase B — wire the convention into the authority documents.**

B1. `PROMPTS.md` §5 (the 9-step receipt workflow) update:

- Step 4 (restate the Outcome): if the prompt arrived as a file in `docs/prompts/`, Code's restatement can be added as a `**Code's restatement:**` paragraph appended to the prompt file before execution begins. If the prompt arrived via paste (no file), behavior is unchanged.
- Step 9 (report back): if the prompt was a file in `docs/prompts/`, Code writes the report to the sibling `.report.md` file in addition to (not instead of) emitting it in terminal. If the prompt was pasted, behavior is unchanged.
- Add a short §5.5 or end-of-§5 subsection naming the file convention and pointing at `docs/prompts/README.md`.

B2. `CLAUDE.md` "Receiving prompts from Chat" subsection update:

- Add a fourth internalized bullet: *"Prompts may arrive as files in `docs/prompts/plan-NN-<slug>.md` rather than as pasted text. When they do, execution still follows PROMPTS.md §5, with Step 4's restatement and Step 9's report-back additionally written to the file (see PROMPTS.md §5 updated subsection and docs/prompts/README.md)."*
- Do not relocate the existing three bullets; the convention is additive.

B3. `session-starter.md` "How We Work Together" section update:

- Add a bullet naming `docs/prompts/` as the durable home for Chat-issued prompts and Code-issued reports. Keep it short — one sentence pointing at `docs/prompts/README.md`. The existing PROMPTS.md bullet stays; this is a sibling reference.
- Also add `docs/prompts/` to the "Key Files to Know" "Also searchable and worth pulling on demand" paragraph alongside `docs/plans/`, `docs/sessions/`, `docs/handoffs/`, `docs/limitations/`, `docs/transcripts/`. Session-starter is the door future Chat sessions come through — they need to know the directory exists.

**Phase C — LOG/TASKS housekeeping.**

C1. `LOG.md` Plans Registry row for Plan 43.
C2. `TASKS.md` Plan 43 row flipped `[~]` → `[x]` at session end.
C3. Session file at `docs/sessions/session-NN-2026-05-24-plan-43-prompt-report-lineage.md` (next contiguous session number — Code resolves; Session 65 was the last logged).
C4. `LOG.md` "Last Updated" bumped.
C5. Reconcile with Plan 42 state at the end: if Plan 42 has shipped between this plan starting and ending, surface the merge-conflict region (PROMPTS.md §5/§6) in the Worth-flagging section.

## Verification

**Static-artifact gates:**

- `docs/prompts/README.md` exists, names the filename convention, lifecycle, lineage chain, and backfill policy.
- `docs/prompts/plan-37-allowlist-edits.md`, `docs/prompts/plan-38-dba-dashboard.md`, `docs/prompts/plan-39-tidy-c-playwright.md` exist, each with the reconstruction note at the top, each shaped per PROMPTS.md §3.
- `PROMPTS.md` §5 updates landed: Step 4 amendment, Step 9 amendment, new subsection naming the file convention.
- `CLAUDE.md` "Receiving prompts from Chat" has the new fourth bullet.
- `session-starter.md` "How We Work Together" has the new bullet pointing at `docs/prompts/`, and "Key Files to Know" mentions the directory.
- `LOG.md` Plans Registry has the Plan 43 row, "Last Updated" is bumped.
- `TASKS.md` Plan 43 row exists and is flipped `[x]` at end.

**Live-functional gate:**

- One smoke test of the new convention: this very prompt (Plan 43) commits to `docs/prompts/plan-43-prompt-report-lineage.md` as part of the work (either Gordon commits it before Code starts, or Code copies it from wherever it landed locally as the first execution step). Code's report-back at session end writes to `docs/prompts/plan-43-prompt-report-lineage.report.md` per the new convention. If the report file exists at session end and contains the gate table, the new convention worked end-to-end on its own birth session. If the prompt arrived only via paste with no file, Code surfaces that and the smoke test moves to the next plan instead.

## Halt conditions

- **Plan 42 in flight.** If a PR for Plan 42 (memory-to-file migrations) is open or merging when this plan starts, halt at Step 2 and surface — running both against §5/§6 concurrently will conflict. Either wait for Plan 42 to merge and rebase, or pause this plan until Plan 42 settles.
- **Plan 42's PROMPTS.md changes already merged with a materially different §5/§6 shape** than this prompt assumes. Halt at Step 4 (restate), surface the conflict, wait for Chat to revise the prompt.
- **Pre-flight finds the directory already exists with prior content** (it shouldn't — this is a net-new directory). If so, halt and surface; Chat needs to know why.
- **The smoke test (Verification live-functional gate) can't be run** because the prompt arrived only via paste, not as a file in `docs/prompts/`. Don't fake the gate; surface this in the report-back as a partial.

## Out of scope

- **Phase 3 — autonomous Code-runner.** GitHub Actions watching `docs/prompts/`, headless Claude Code execution, autonomous PR opening. That's a separate plan, deferred until the file convention has lived in real sessions for some number of cycles.
- **GitHub MCP connector setup on Chat side.** Gordon's settings work, not a repo change. Mentioned in Context for completeness; this plan doesn't depend on MCP being live.
- **Backfilling reports for plans 37, 38, 39.** Session files already hold the report-equivalent content. Reconstructing reports would be busywork without lineage value.
- **Reformatting older session files** to match the new convention. Session files stay as they are; the new convention adds files, doesn't reshape existing ones.
- **Auto-resolving the most-recent-unconsumed-prompt question** (i.e., logic that picks the right file when Code starts a session). That's an orchestration concern that belongs with Phase 3.

## Commit shape

Single PR holding the full plan. Phase A (directory + backfill) and Phase B (authority doc wiring) and Phase C (housekeeping) are jointly valuable — splitting would leave the directory orphaned without docs pointing at it, or docs pointing at a non-existent directory. Commit message names Plan 43.

Per CLAUDE.md autonomous PR-merge policy: push → `gh pr create` → `gh pr merge --merge --delete-branch` autonomously on this repo once verification gates pass. Pause conditions per CLAUDE.md (partial / blocked / halt conditions firing / cross-repo / destructive / message-sending) — none of which apply to this doc-and-convention plan.

---

## Notes for Code

- **This prompt is the first prompt under the new convention.** Whether it arrives via paste or via file commit, the work itself establishes the directory it should have lived in. If it arrived as a file at `docs/prompts/plan-43-prompt-report-lineage.md`, the smoke test (Verification §) is automatic — Code writes the report to the sibling file at end. If it arrived via paste, Code copies the prompt verbatim into `docs/prompts/plan-43-prompt-report-lineage.md` as the first execution step and proceeds.
- **Reconstruction faithfulness.** The three backfilled prompts (37/38/39) should be as faithful to the originals as session narratives + design docs + LOG rows + TASKS rows allow. Code is reconstructing, not designing. If a section of a backfilled prompt has to be guessed because the source material doesn't cover it, mark it `*(reconstructed, low confidence)*` inline rather than invent confident text. The reconstruction note at the top of each backfilled prompt should be explicit about what's reconstructed vs what's certain from sources.
- **No new functionality in PROMPTS.md.** Step 4 amendment and Step 9 amendment are *additive* — they describe new file-side behavior when prompts arrive as files. The existing terminal behavior is unchanged. Same for the new subsection: it documents the convention, doesn't change how PROMPTS.md §1-4 work.
- **Report-back vocabulary alignment.** PROMPTS.md §5 Step 9's report-back shape uses sections `Gate table / Shipped / Worth flagging / Ready for more work`. The original draft of this prompt named the sections slightly differently ("Decisions, Issues encountered, Status, Next"); the README in A1 should use PROMPTS.md's canonical names so the convention stays consistent with the existing standard.
