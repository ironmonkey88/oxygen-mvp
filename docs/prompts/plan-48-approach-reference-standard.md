# Prompt — Land APPROACH.md as the project's reference standard

**Kind:** coding
**Date:** 2026-06-10
**Scope:** `oxygen-mvp` and `stack-in-a-box` — new `APPROACH.md` at each repo root; pointer wiring in each repo's `CLAUDE.md` and `session-starter.md`; LOG.md / TASKS.md updates per repo convention. One canonical Markdown body, identical in both repos.
**Effort:** ~1 session (documentation + wiring; no code, no live gates).
**Depends on:** none.

---

## Phase 0 — write this prompt to the repo first (do this before any other work)

Before any other work, write this prompt **verbatim** to
`docs/prompts/plan-NN-approach-reference-standard.md` on a new branch
`claude/plan-NN-approach-reference-standard`. This file write is the first
commit on the branch. All subsequent phases proceed against that branch.

**Plan number:** claim the next available plan slot per each repo's LOG.md
Plans Registry at fire time — resolve `NN` before branching; do not assume a
number. Because this lands in **both** repos, each repo gets its own plan number
from its own registry; note both numbers in the branch's report.

The MCP-direct-commit path is paused; Code owns prompt-file creation.

---

## Outcome (required)

The project gains a single, plain-language **reference standard** describing how
we work — our principles (empathy, honesty, optimism; the trust contract;
hypothesis-then-result; decide-then-build; declarative/reconciliation) and the
reasoning behind them — written so anyone, including a non-technical newcomer or
a commercial onboarding analyst, can understand it. Its purpose is to **keep the
project honest and consistent**: every other document should be compatible with
it, and we periodically reconcile the detailed docs against it. It is
deliberately free of implementation specifics (no named tools as load-bearing,
no Chat/Code as definitional, no Somerville/resident as definitional) so it
stays true across both repos and as the stack evolves. After this lands, a
reader who wants to know "what does this project actually believe and how does
it work" has one short doc to read, and future design decisions have a standard
to check against.

## Context (conditional)

- This doc sits at the **same altitude as METHODOLOGY.md**: a shared artifact
  meant to exist in **both** `oxygen-mvp` and `stack-in-a-box`, kept consistent
  via the same Code-proposes / human-approves, eventually-consistent posture.
  The body is identical in both repos at landing time.
- It sits **above** PHILOSOPHY.md in the convictions hierarchy: PHILOSOPHY.md is
  the Somerville-specific *instance* of this general standard. APPROACH.md is the
  reference standard; PHILOSOPHY.md specializes it. They must not contradict —
  if they do, that is a finding to surface, not to silently resolve.
- The canonical body is provided in full below (see "Canonical content"). It was
  authored and refined in Chat; **transcribe it, do not rewrite it.** Minor
  mechanical fixes only (e.g. link targets). If anything in it reads as
  conflicting with existing PHILOSOPHY.md / METHODOLOGY.md wording, surface the
  conflict in the report rather than editing the body to resolve it.
- Filename is `APPROACH.md` at repo root. If you believe a different name serves
  the hierarchy better, surface it as a recommendation — do not rename
  unilaterally.

## Work (required)

1. **Create `APPROACH.md` at the root of `oxygen-mvp`** with the canonical body
   below, verbatim.
2. **Create `APPROACH.md` at the root of `stack-in-a-box`** with the identical
   canonical body.
3. **Wire `oxygen-mvp` pointers:**
   - `CLAUDE.md` reading hierarchy: add a tier for APPROACH.md **above** the
     "Convictions (foundational, not authority)" PHILOSOPHY.md entry, labeled so
     it's clear this is the cross-repo reference standard that PHILOSOPHY.md
     specializes. State the reconciliation relationship (principles disagreement
     → APPROACH wins; how-it's-done disagreement → operational doc wins).
   - `session-starter.md`: add an APPROACH.md pointer parallel to the existing
     PHILOSOPHY.md / PROMPTS.md bullets, so Chat picks it up by default.
4. **Wire `stack-in-a-box` pointers:** the equivalent CLAUDE.md and
   session-starter.md (or nearest equivalent) entries for that repo's structure.
   If stack-in-a-box's doc layout differs, adapt the wiring to match its
   conventions and note the adaptation.
5. **Establish the reconciliation relationship in writing** (the closing
   paragraph of the canonical body already states it; ensure the CLAUDE.md tier
   label in each repo is consistent with it).
6. **LOG.md + TASKS.md** updates in each repo per that repo's conventions.

## Verification (required)

Static-artifact gates (this is a documentation change; all gates are static):

- `APPROACH.md` exists at the root of both repos with identical body content
  (verify by diff — the bodies should match modulo nothing; they are the same
  file).
- Each repo's `CLAUDE.md` references APPROACH.md in the reading hierarchy at the
  correct tier (above PHILOSOPHY.md where PHILOSOPHY.md exists).
- Each repo's `session-starter.md` references APPROACH.md.
- No existing doc was edited beyond the wiring sites named in Work items 3–4.
- LOG.md and TASKS.md updated in each repo.

No live-functional gates — nothing executes.

## Halt conditions (conditional)

- If transcribing the canonical body surfaces a **substantive contradiction**
  with existing PHILOSOPHY.md (oxygen-mvp) or PHILOSOPHY.md / METHODOLOGY.md
  (stack-in-a-box) — e.g. a principle stated differently — **halt and surface
  the specific conflict.** Do not edit the canonical body to paper over it, and
  do not edit the existing doc. This is exactly the kind of reconciliation that
  is human-approved, not auto-resolved.
- If the next plan number is ambiguous in either repo's registry, surface and
  ask rather than guessing.

## Out of scope (conditional)

- **No edits to PHILOSOPHY.md or METHODOLOGY.md** in this plan. Reconciling
  PHILOSOPHY.md to use APPROACH-compatible general language (e.g. generalizing
  "the resident is the measure"), and adding the empathy/honesty/optimism creed
  and the Sensemake/system-humanism methodology work, are **separate, already-
  scoped prompts** that follow this one. This plan only *introduces* the
  reference standard and wires it in.
- No `.docx` generation or export tooling. The shareable Word version is
  produced Chat-side; the repo holds the Markdown source of truth only.
- No new doc beyond APPROACH.md and the wiring edits.

## Commit shape (required)

- Per-repo work; each repo gets its own plan number, branch, and PR.
- Phase 0 prompt-file write is commit 1 on the branch.
- Then: APPROACH.md creation, then wiring edits, then LOG/TASKS — committed per
  Work item (documentation-only changes commit without a gate).
- Commit messages name the plan number.
- Default unit of merge is the prompt; one PR per repo. Open the PR when the
  first commit lands; merge when Verification passes.
- Write the Step-9 report to the sibling
  `docs/prompts/plan-NN-approach-reference-standard.report.md` before merge, in
  each repo. Report both repos' plan numbers and PR links.

---

## Canonical content — transcribe verbatim into `APPROACH.md` (both repos)

> Everything between the rule below and the end of this prompt is the literal
> file body. Begin the file at the `# How We Build — our approach` heading.

---

<!-- BEGIN APPROACH.md BODY -->

(See the attached `APPROACH.md` file delivered alongside this prompt — its
contents are the verbatim body. If this prompt is read standalone, the body is
reproduced in full below.)

<!-- The full body is included as a separate file in this handoff:
     APPROACH.md. Code should use that file's contents directly as the
     canonical body for both repos. -->

---

## Resolution (added by Code at execution, 2026-06-10)

The verbatim prompt above is reproduced as received. Three things were resolved
in-session and are recorded here so this lineage file is self-contained.

1. **Plan numbers.** Resolved against each repo's Plans Registry at fire time:
   - `oxygen-mvp` → **Plan 48**. (Initially landed as "Plan 47" — branch
     `claude/plan-47-approach-reference-standard`, merged PR #78. A plan-number
     collision was then found with the older, still-open PR #76 ("Plan 47: tech
     + test debt assessment"), which had the prior claim on 47. Per Gordon's
     call this work yielded and was renumbered 47 → 48 — the next genuinely-free
     slot — in a follow-up PR. Root cause: `gh pr list` was not run at session
     start, so the open-PR claim on 47 was missed; the registry on `main` showed
     46 as the highest.)
   - `stack-in-a-box` → **Plan 5** (Plans 1–3 done; **Plan 4 is already
     reserved** for the retroactive Oxygen-version pin, so 4 was not free).
   Neither slot was ambiguous *on `main`*; the collision was an unmerged-PR
   claim the registry didn't yet show.

2. **Canonical body delivery.** The "Canonical content" section above is a
   placeholder — the attachment it points to was not delivered with the prompt.
   The body arrived separately in Chat, and an aligned Google Doc
   ("How-We-Build-Summary",
   `docs.google.com/document/d/1UOffW2wVhG4fiAgj_c35kn-GVCgppYD--AuHS8Bk1t4`) was
   also supplied with the instruction "write this doc to the repo as well." The
   two were the same document with three differences: the Google Doc carried a
   newcomer "start here" intro line and dropped the closing reconciliation
   paragraph; the pasted body carried the reconciliation paragraph (which Work
   item 5 relies on) and no intro line; titles differed.

3. **Merge decision (Gordon, in-session).** Use the pasted body as the base
   (keeps the closing reconciliation paragraph), add the Google Doc's newcomer
   intro line, and keep the title `# How We Build — our approach` per Phase 0's
   explicit heading instruction. This is the single deviation from pure-verbatim
   and was human-approved. The merged result is the body that landed in
   `APPROACH.md` in both repos — see that file for the canonical text.

**Halt-condition check (contradiction).** Both PHILOSOPHY.md files were read in
full and found compatible with APPROACH.md — each is a specialization, not a
contradiction. The contradiction halt condition did not fire.
