# Prompt — Add a new-account cold-start block to session-starter.md (both repos)

**Kind:** coding
**Date:** 2026-06-17
**Scope:** `oxygen-mvp` and `stack-in-a-box` — add one new section near the top of each repo's `session-starter.md` that orients a fresh Claude arriving in a new account, pointing to the existing migration-doc trio in read-order. Consolidation only — no new standalone doc. LOG.md / TASKS.md per repo convention.
**Effort:** small; documentation only, pointer wiring.
**Depends on:** the migration trio already exists (`PROJECT_MIGRATION_2026-06-07.md`, `MIGRATION_CHECKLIST.md`, `docs/MIGRATION_SUMMARY.md`) — all merged. No new content is authored; this points to them.

---

## Phase 0 — write this prompt to the repo first (do this before any other work)

Before any other work, write this prompt **verbatim** to
`docs/prompts/plan-NN-session-starter-coldstart.md` on a new branch
`claude/plan-NN-session-starter-coldstart`. This file write is the first commit
on the branch. All subsequent phases proceed against that branch.

**Plan number:** claim the next available slot per **each** repo's LOG.md Plans
Registry at fire time — resolve `NN` before branching; do not assume a number.
Boot-audit the registry first (stack-in-a-box is now at Plan 10; oxygen-mvp's tail
has reserved-but-unused slots — respect them). Each repo gets its own plan number;
note both in the report. If ambiguous in either repo, halt and surface before
branching.

The MCP-direct-commit path is paused; you own prompt-file creation.

---

## Outcome (required)

A fresh Claude opening either repo in a **new account** self-orients correctly on
the first read, without the operator having to explain the migration. The
existing `session-starter.md` is already the Claude-orientation doc — it carries
read-order, the Chat/Code split, the Rules of Engagement, and the
start-each-session boot sequence. The one gap: it points to
`docs/MIGRATION_SUMMARY.md` but not to the other two migration docs
(`PROJECT_MIGRATION_2026-06-07.md` — the deep runbook; `MIGRATION_CHECKLIST.md` —
the tracker). A Claude landing post-migration should know all three exist and
which to read when.

This is **consolidation, not addition.** Do not create a new standalone
orientation file. Add a short, clearly-scoped block to the existing
`session-starter.md` in each repo that names the three migration docs in
read-order and states plainly that it only applies to a new-account / fresh-laptop
restart (a normal continuing session ignores it).

## Context (conditional)

- The three migration docs and their roles (state them this way in the block):
  - **`PROJECT_MIGRATION_2026-06-07.md`** (repo root) — the detailed runbook:
    the two-repo discipline, roles, the auto-memory facts (§3), live EC2 + access
    (§5–6), fresh-laptop setup (§9), the allowlist (§9d). Read this for *how to
    stand the environment back up*.
  - **`MIGRATION_CHECKLIST.md`** (repo root) — the tracker: checkbox state across
    the whole move, and the index that points into the runbook. Read this to
    *see what's done and what's left*.
  - **`docs/MIGRATION_SUMMARY.md`** — the cold-start handoff: who Gordon is, how
    Chat and Code work, project state, first-session checklist. Read this
    *first* — it's the fastest path to being useful.
- Read-order for a brand-new-account Claude: **MIGRATION_SUMMARY → CHECKLIST →
  PROJECT_MIGRATION (as needed)**, then the normal session-starter flow (LOG.md,
  TASKS.md).
- The block must be explicitly conditional — a continuing session in the
  established account should not re-run migration steps. Frame it: "If you are a
  fresh Claude in a new account or on a new machine, start here; otherwise skip to
  [the normal start-each-session steps]."
- Keep both repos' `session-starter.md` consistent in this block's wording. Note:
  the two session-starter files are **not** byte-identical overall (each has its
  own repo callout, status, file table). Only this new block should be worded
  identically; adapt nothing else. (This differs from APPROACH.md, which *is*
  byte-identical — do not try to make the whole files match.)

## Work (required)

1. **In `stack-in-a-box/session-starter.md`**, add the cold-start block. Place it
   immediately after the "Which repo is this?" callout and before "Who You Are
   Talking To" (so a migrating Claude hits it first), or in the nearest natural
   slot if that placement reads poorly — your judgment, but it must come before
   the start-each-session steps.
2. **In `oxygen-mvp/session-starter.md`**, add the identically-worded block,
   placed in the equivalent position for that repo's structure.
3. **Verify** each repo's three migration docs exist at the paths the block names
   (don't point at a file that isn't there).
4. **LOG.md + TASKS.md** updates per repo convention.

## Verification (required)

Static-artifact gates (documentation; all static):

- Both `session-starter.md` files contain the cold-start block, identically
  worded in the block itself.
- The block names all three migration docs with correct paths, in the stated
  read-order, and is explicitly conditional on a new-account/new-machine restart.
- Every path the block references resolves to a real file in that repo.
- No other part of either `session-starter.md` was altered.
- LOG.md / TASKS.md updated in each repo.

No live-functional gates — nothing executes.

## Halt conditions (conditional)

- If any of the three migration docs is missing at its expected path in either
  repo, **halt and surface** — do not point at a nonexistent file, and do not
  create the missing doc here.
- If the next plan number is ambiguous in either registry, surface and ask.

## Out of scope (conditional)

- **No new standalone orientation/runbook file.** This consolidates into the
  existing `session-starter.md`.
- No changes to the migration docs themselves.
- No attempt to make the two `session-starter.md` files byte-identical overall.
- No `.docx` export.
- The earlier infra-install "zero-to-live setup runbook" prompt is **superseded
  by this decision** — that was an infrastructure-install doc; the operator chose
  consolidation into session-starter instead. If that prompt is still queued and
  unstarted, do not run it; if asked, surface that it was superseded.

## Commit shape (required)

- Phase 0 prompt-file write is commit 1 on the branch.
- Then: the stack-in-a-box block, the oxygen-mvp block, then LOG/TASKS — per Work
  item.
- Commit messages name the plan number.
- One PR per repo. Report both plan numbers and PR links in the sibling
  `docs/prompts/plan-NN-session-starter-coldstart.report.md` before merge.
