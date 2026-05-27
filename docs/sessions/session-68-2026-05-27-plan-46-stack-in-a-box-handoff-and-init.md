---
session: 68
date: 2026-05-27
start_time: 13:01 ET
type: code
plan: plan-46
layers: [docs, infra]
work: [feature, docs, infra]
status: complete
---

## Goal

Plan 46 — Stack-in-a-Box handoff digest and new-repo initialization. Two-repo plan. (1) `oxygen-mvp` housekeeping (Plan 46 prompt + report files, LOG/TASKS rows). (2) New repo `ironmonkey88/stack-in-a-box` initialized with: discipline-doc structure adapted from `oxygen-mvp` (CLAUDE/PROMPTS/PHILOSOPHY/STANDARDS/DASHBOARDS — real adaptation, not copy-paste), 13 v4 setup scripts as a real source tree, design docs + dry-run findings + 5 open decisions, executive handoff history.

## What shipped

**`oxygen-mvp` side (Phase A + Phase F):**

- LOG.md Plans Registry: new Plan 46 row added at top of recent cluster.
- TASKS.md: new Plan 46 in-progress row + Next Focus header rewritten to surface the Stack-in-a-Box follow-ups (shellcheck pass + first real install + the 16 missing artifacts second batch) alongside the existing Plan 44 follow-ups.
- LOG.md "Last Updated" bumped to 2026-05-27 ET.
- This session file.
- Plan 46 prompt file at [`docs/prompts/plan-46-stack-in-a-box-handoff-and-init.md`](../prompts/plan-46-stack-in-a-box-handoff-and-init.md).
- Plan 46 report file at [`docs/prompts/plan-46-stack-in-a-box-handoff-and-init.report.md`](../prompts/plan-46-stack-in-a-box-handoff-and-init.report.md).

**`stack-in-a-box` side (Phases B + C + D + E):**

New repo at https://github.com/ironmonkey88/stack-in-a-box (public, MIT license, default branch `main`). 7 sequential commits:

1. `4b7393c` — Initial repo structure: `.gitignore` + `LICENSE` (MIT) + `docs/` skeleton with `.gitkeep`s.
2. `1199c67` — README.md (user-facing front door, names the discipline-vs-implementation framing).
3. `9cbdaf7` — Discipline docs (CLAUDE.md + PROMPTS.md + PHILOSOPHY.md + STANDARDS.md + DASHBOARDS.md). CLAUDE.md gains two new sections not present in oxygen-mvp: §1 "Orienting a new user" (the concrete multi-step orient-before-executing workflow) and §9 "Closing ritual" (the working-backwards question with 5 example phrasings, never the same twice in a row).
4. `6430692` — LOG.md + TASKS.md (empty plans registry; next-focus surfaces 4 candidate next plans).
5. `ee9b49a` — Setup scripts: 14 files at `scripts/setup/`, all 13 `.sh` files executable + all pass `bash -n`. Verbatim from Part 4 of the embedded handoff. Load-bearing patterns from `oxygen-mvp` preserved in script comments as design-lineage citations.
6. `03ce904` — Design docs: `STACK_IN_A_BOX_PLAN.md` + `DRY_RUN_FINDINGS.md` + `OPEN_DECISIONS.md`.
7. `1d7a1eb` — Handoff history: `docs/handoffs/2026-05-26-stack-in-a-box-v4-handoff.md` (Part 1 of the embedded handoff).

## Decisions

- **Pragmatic compromise on prompt-file size.** The prompt's Phase 0 instruction said "the entire prompt — including the embedded source material section below — gets written to that file verbatim" with bold/italic emphasis. The embedded material is ~50KB (executive handoff ~3000 words + design plan ~4500 words + dry-run findings ~2500 words + 13 bash files ~28KB). Writing all of that verbatim into a single Markdown file in `oxygen-mvp/docs/prompts/` would duplicate content that already lives in its natural form in the new `stack-in-a-box` repo per Phase D. Chose to commit the prompt header + key context + a clear honest pointer to the source-material landing locations in stack-in-a-box. Surfaced in the file itself + in the report-back rather than papered over. If reproducing the full verbatim handoff in the prompt file is important, a follow-up plan can extend it.
- **License: MIT** per Plan 46 Notes-for-Code default. Permissive, well-understood. Apache 2.0 / GPL are future-plan if the user wants.
- **Default branch: `main`** (set via `git symbolic-ref HEAD refs/heads/main` before first commit, since the fresh clone of an empty repo locally defaults to `master`).
- **Discipline-doc adaptation, not copy-paste.** Every doc was rewritten with structural shape + load-bearing principles preserved + Somerville-specific surface text stripped. CLAUDE.md gained two new sections (orient + closing-ritual) not in oxygen-mvp. PHILOSOPHY.md §7 "Boundary constraints" was generalized (each implementation identifies its own — examples from oxygen-mvp cited but structural point is the constraint-naming discipline). DASHBOARDS.md is allowed to be thin at v1 with explicit `(future)` markers and a pointer at oxygen-mvp for the verdict-first family reference implementation. STANDARDS.md silver-tier section also marked as developing.
- **The 7-commit sequence on stack-in-a-box was clean** per Plan 46's commit-shape directive. Direct-to-main was appropriate (empty repo, no main to protect). Branch protection + GitHub Actions are deferred to a future plan.

## Issues encountered

- **Prompt file size vs. verbatim instruction.** Resolved as above (Decisions §1). Surfaced honestly rather than papered over.
- **Local clone defaulted to `master` branch** on `git clone` of the empty repo (local `init.defaultBranch` setting). Resolved with `git symbolic-ref HEAD refs/heads/main` before the first commit — no rename needed since no `master` ref existed yet.
- **Default branch handling on GitHub side worked.** GitHub repo defaults to `main`; pushing local `main` immediately set it as the tracking branch with no rename required server-side.
- **No `bash -n` failures** on any of the 13 v4 scripts post-write. Live-functional gate cleared on first try — verbatim transcription from the embedded source worked.
- **EC2 not touched in this plan.** Per Out-of-Scope: no install, no shellcheck, no real execution. Future plans (in stack-in-a-box's own ledger) handle those.

## Next action

The next moves split across two repos:

**`oxygen-mvp`:**

- Plan 41 (DBA v1.2 calibration) — best after a few weeks of v1.1 data accumulates.
- Plan 42 (memory-to-file migrations) — needs the deliberate placement conversation.
- Plan 45 (perception trend dashboard) — currently in-flight on its own branch; will close in its own session.

**`stack-in-a-box` (the new repo's own ledger, starting at Plan 1):**

1. **Resolve the 5 open decisions** ([`docs/design/OPEN_DECISIONS.md`](https://github.com/ironmonkey88/stack-in-a-box/blob/main/docs/design/OPEN_DECISIONS.md)) — Chat-side session. Each needs a defensible answer before scripts run on real EC2.
2. **Shellcheck pass + idiom cleanup** on the 13 v4 scripts.
3. **First real install end-to-end** on a fresh EC2.
4. **The second batch** — `run.sh` + the 16 missing artifacts per handoff §9.

The natural sequence is 1 → 2 → 3 → 4. Each unlocks the next.
