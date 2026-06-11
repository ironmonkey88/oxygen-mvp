# Prompt A — Reconcile oxygen-mvp/PHILOSOPHY.md to APPROACH.md (creed + generalize "the resident is the measure")

**Kind:** coding (documentation)
**Repo:** `oxygen-mvp`
**Scope:** `PHILOSOPHY.md` only, plus LOG.md / TASKS.md per convention.
**Effort:** ~half a session. No code, no live gates.
**Depends on:** APPROACH.md (already landed, Plan 48).

---

## Phase 0 — write this prompt to the repo first

Before any other work, write this prompt **verbatim** to
`docs/prompts/plan-NN-philosophy-creed-reconcile.md` on a new branch
`claude/plan-NN-philosophy-creed-reconcile`. This file write is the first commit
on the branch. All subsequent phases proceed against that branch.

**Plan number:** claim the next available oxygen-mvp slot from LOG.md's Plans
Registry at fire time (Plan 48 is taken; Plan 47 is the tech-debt assessment).
**Before claiming, audit open/recent PRs** (`gh pr list --state all`) to confirm
the slot is free — this is the boot-audit step whose absence caused the 47/48
collision last session. Resolve `NN` before branching.

MCP-direct-commit path is paused; Code owns prompt-file creation.

---

## Outcome (required)

`oxygen-mvp/PHILOSOPHY.md` — the Somerville-specific convictions doc — is brought
into agreement with the cross-repo reference standard (`APPROACH.md`) on two
points it currently lags: (1) it gains the **empathy / honesty / optimism creed**
as the memorable one-line distillation of its synthesis, and (2) its phrase "the
resident is the measure" is explicitly framed as the **Somerville specialization**
of APPROACH.md's general "the people the work is about are the measure," so a
reader sees the instance-of relationship rather than a silent divergence. After
this, PHILOSOPHY.md states the project's central conviction in the same terms as
the standard above it, while keeping its sharper Somerville-specific language.

This prompt deliberately does **not** touch system humanism (§2.3, §5). That
split is deferred until oxygen-mvp has its own METHODOLOGY.md to receive the
build-discipline half; system humanism remains whole here as a conviction, which
is correct. Out of scope below restates this.

## Context (conditional)

- **The creed already exists in APPROACH.md** (the "What we believe" section:
  empathy = context is part of correctness; honesty = the rule the other two
  answer to; optimism = earned, a conclusion the evidence supports). PHILOSOPHY's
  §3 synthesis already contains all three ideas — "honesty is the non-negotiable"
  (honesty), "a partial picture is a distortion" + the pair-with-trend correction
  (optimism), "the resident is the measure" (empathy) — but never names them as
  the three-word creed, and its one-line form drops empathy. The work is to
  surface the creed as the distillation §3 has been missing, NOT to rewrite §3's
  substance.
- **APPROACH.md's creed line:** *"see the whole community honestly — the hard and
  the hopeful — because the people who live there deserve the full truth."*
  PHILOSOPHY's existing §3 one-liner is the city-specific version: *"See the whole
  city honestly — the hard and the hopeful — because the people of Somerville
  deserve nothing less than the truth, completely."* Keep the Somerville one as
  the instance; add the three-word creed (empathy/honesty/optimism) as the named
  frame above or alongside it.
- **"The resident is the measure"** appears in §3 (move 3) and §6.6. Both stay —
  "resident" is correct for the Somerville instance — but add a brief, explicit
  note (once, at the §3 occurrence is enough) that this is the Somerville form of
  APPROACH.md's general principle. A single clause like "(the Somerville-specific
  form of the standard's 'the people the work is about are the measure')" does it;
  don't belabor it.
- **Wiring is already done.** §1 of PHILOSOPHY.md and CLAUDE.md already describe
  PHILOSOPHY as "the Somerville-specific instance of APPROACH.md." Do not re-add
  pointers; they exist. This prompt is content reconciliation only.

## Work (required)

1. **Add the creed to §3.** Surface empathy / honesty / optimism as the named
   three-word distillation of the §3 synthesis. Tie each term to the move it
   already corresponds to (honesty → move 1; optimism → move 2; empathy → move 3 /
   "the resident is the measure"). Keep the existing three-move prose and the
   Somerville one-liner; the creed is added as the frame, not a replacement. Match
   the doc's existing voice (declarative, unhurried, no bullet-spam).
2. **Frame "the resident is the measure" as a specialization** at its §3
   occurrence — one clause naming it as the Somerville form of APPROACH.md's
   general principle. Leave §6.6's "resident" wording as-is (it's the instance
   doc; it's allowed to be specific), optionally with a back-reference to §3 if it
   reads naturally.
3. **Do not touch §2.3 or §5** (system humanism). Do not touch §4. Do not touch
   §6 principles other than the optional §6.6 back-reference.
4. **LOG.md + TASKS.md** per convention.

## Verification (required)

Static-artifact gates (documentation change; all static):

- PHILOSOPHY.md §3 names empathy, honesty, and optimism as the creed, mapped to
  the existing three moves.
- The Somerville one-liner is preserved (not deleted).
- "The resident is the measure" carries a one-clause note framing it as the
  Somerville specialization of APPROACH.md's general form.
- §2.3 and §5 are unchanged (verify by diff — no lines touched there).
- LOG.md / TASKS.md updated.

No live-functional gates.

## Halt conditions (conditional)

- If adding the creed surfaces a substantive contradiction between PHILOSOPHY §3
  and APPROACH.md's "What we believe" (beyond the known empathy-naming gap), halt
  and surface it rather than papering over — that's a principle-level
  reconciliation for human approval.
- If the plan-number slot is ambiguous after the PR audit, surface and ask.

## Out of scope (conditional)

- **System humanism split — explicitly deferred.** Do not divide §2.3 / §5, do
  not add a build-discipline pointer, do not remove anything about manufacturing
  operator expertise. System humanism stays whole here until oxygen-mvp has a
  local METHODOLOGY.md. (Tracked in the detailed design notes.)
- No edits to MVP.md, BUILD.md, ARCHITECTURE.md, or any operational doc.
- No new doc; no METHODOLOGY.md instantiation in this plan.

## Commit shape (required)

- Phase 0 prompt-file write is commit 1.
- Then PHILOSOPHY.md edit, then LOG/TASKS (docs commit without a gate).
- One PR; autonomous merge on green per repo policy.
- Step-9 report to sibling `docs/prompts/plan-NN-philosophy-creed-reconcile.report.md`
  before merge.

---

## Resolution (added by Code at execution, 2026-06-10)

- **Plan number → 49.** Boot audit run first (`gh pr list --state all`): Plan 48
  (APPROACH.md) merged; Plan 47 owned by the still-open tech-debt PR #76; Plans
  41/42/45 reserved-but-unused; no branch, PR, or registry row claims 49. Slot
  unambiguous; the plan-number halt condition did not fire.
