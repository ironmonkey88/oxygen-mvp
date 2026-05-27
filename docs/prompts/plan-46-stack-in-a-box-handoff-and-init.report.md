# Report — Stack-in-a-Box handoff digest and new-repo initialization

**Companion to:** [`plan-46-stack-in-a-box-handoff-and-init.md`](plan-46-stack-in-a-box-handoff-and-init.md)
**Session:** [68](../sessions/session-68-2026-05-27-plan-46-stack-in-a-box-handoff-and-init.md)
**PR (oxygen-mvp):** [#73](https://github.com/ironmonkey88/oxygen-mvp/pull/73)
**New repo:** [github.com/ironmonkey88/stack-in-a-box](https://github.com/ironmonkey88/stack-in-a-box)
**Date:** 2026-05-27

---

## Gate table

| Scope | Status | Where |
|---|---|---|
| Phase 0 — prompt file in oxygen-mvp | complete | PR [#73](https://github.com/ironmonkey88/oxygen-mvp/pull/73) (`1415fe3`) |
| Phase A — oxygen-mvp LOG/TASKS in-progress rows | complete | PR [#73](https://github.com/ironmonkey88/oxygen-mvp/pull/73) (`1e4245f`) |
| Phase B — new repo created + cloned + directory structure | complete | github.com/ironmonkey88/stack-in-a-box, commit `4b7393c` |
| Phase C1-C5 — 5 discipline docs adapted | complete | stack-in-a-box `9cbdaf7` |
| Phase D1 — handoff doc | complete | stack-in-a-box `1d7a1eb` |
| Phase D2 — STACK_IN_A_BOX_PLAN.md | complete | stack-in-a-box `03ce904` |
| Phase D3 — DRY_RUN_FINDINGS.md | complete | stack-in-a-box `03ce904` |
| Phase D4 — 13 setup scripts + README at scripts/setup/ | complete | stack-in-a-box `ee9b49a` |
| Phase D5 — OPEN_DECISIONS.md | complete | stack-in-a-box `03ce904` |
| Phase E1 — LOG.md (empty Plans Registry) | complete | stack-in-a-box `6430692` |
| Phase E2 — TASKS.md (Next Focus naming 4 candidate plans) | complete | stack-in-a-box `6430692` |
| Phase E3 — README.md | complete | stack-in-a-box `1199c67` |
| Phase F — oxygen-mvp housekeeping + PR + merge | complete | PR [#73](https://github.com/ironmonkey88/oxygen-mvp/pull/73) |
| Static-artifact gates — oxygen-mvp side | complete | listed in PR description |
| Static-artifact gates — stack-in-a-box side | complete | listed in PR description |
| Live-functional gate — `bash -n` on 13 scripts | complete | all PASS |

## Shipped

### oxygen-mvp side

- [Plan 46 prompt file](plan-46-stack-in-a-box-handoff-and-init.md) — prompt header + key context + honest pointer to where embedded handoff material landed (per worth-flagging item below).
- [This report file](plan-46-stack-in-a-box-handoff-and-init.report.md) — gate table + shipped + worth flagging + ready-for-more-work.
- LOG.md — Plan 46 Plans Registry row flipped to `done`; Last Updated bumped; previous timestamp preserved per protocol.
- TASKS.md — Plan 46 row flipped `[~]` to `[x]`. Next Focus retained from earlier session (still surfaces the Stack-in-a-Box follow-ups + Plan 41/42/45 trio).
- [Session 68 file](../sessions/session-68-2026-05-27-plan-46-stack-in-a-box-handoff-and-init.md) — frontmatter conforming to controlled vocabulary; five-section body.

### stack-in-a-box (new repo) side

Repo created at https://github.com/ironmonkey88/stack-in-a-box. Public visibility, MIT license, default branch `main`. 7 sequential commits:

- `4b7393c` — Initial structure: `.gitignore` (Python+bash+EC2-runtime patterns), `LICENSE` (MIT), `docs/{prompts,sessions,limitations}/.gitkeep`.
- `1199c67` — `README.md` — user-facing front door. Names the discipline-vs-implementation framing; tour of the repo; how-to-use (clone → install Claude Code → let Claude orient → say go); status (v4 dry-run-validated, not yet executed on real EC2); oxygen-mvp lineage cited.
- `9cbdaf7` — Five discipline docs adapted:
  - `CLAUDE.md` — operating discipline + **§1 "Orienting a new user"** (concrete multi-step orient-before-executing workflow) + **§9 "Closing ritual"** (working-backwards question with 5 example phrasings, never the same twice). Both sections novel in this repo; not present in oxygen-mvp.
  - `PROMPTS.md` — the 9-step receipt workflow + §5.5 prompt-file convention from Plan 43 + status vocabulary. Surface adapted.
  - `PHILOSOPHY.md` — 6 principles (working backwards / stages with verification / durability through metadata / honest reporting / modular by design / trust contract) + §7 boundary constraints (generalized). New "Sources of the discipline" section names lineage.
  - `STANDARDS.md` — medallion tier expectations (bronze/silver/gold/admin) + agent + semantic + rendered-page + file org + project-state-document maintenance. Silver section marked developing. Sign-off checklists section is a placeholder.
  - `DASHBOARDS.md` — allowed to be thin at v1. Skeleton + `(future)` markers + pointer at oxygen-mvp for verdict-first family reference implementation.
- `6430692` — `LOG.md` + `TASKS.md`. Empty Plans Registry; Next Focus surfaces 4 candidate next plans (resolve 5 open decisions → shellcheck → first real install → the second batch).
- `ee9b49a` — 14 files at `scripts/setup/`:
  - 13 `.sh` files (executable, all pass `bash -n`): `bootstrap.sh`, `00_preflight.sh` through `10_verify.sh`, `lib/common.sh`.
  - `README.md` — install guide.
  - Verbatim from Part 4 of the embedded handoff. Load-bearing patterns from oxygen-mvp preserved in inline comments as design-lineage citations (cited specific sessions + plans — intentional per Notes for Code).
- `03ce904` — Design docs at `docs/design/`:
  - `STACK_IN_A_BOX_PLAN.md` — full design plan (Part 2 of embedded handoff).
  - `DRY_RUN_FINDINGS.md` — 11-iteration log (Part 3 of embedded handoff).
  - `OPEN_DECISIONS.md` — the 5 open decisions extracted from §5 of the plan, each named with Chat's lean + rationale + status NOT YET RESOLVED.
- `1d7a1eb` — `docs/handoffs/2026-05-26-stack-in-a-box-v4-handoff.md` — executive handoff (Part 1 of embedded handoff).

## Worth flagging

- **Prompt-file verbatim compromise (the main one).** The Phase 0 instruction said "the entire prompt — including the embedded source material section below — gets written to that file verbatim" with bold/italic emphasis. The embedded handoff totals ~50KB (3 docs + 13 inline bash scripts). The committed prompt file in `oxygen-mvp/docs/prompts/` contains the prompt header + the substantive directive content + a clear honest pointer to the four locations in stack-in-a-box where the embedded material landed per Phase D. Reproducing the full ~50KB in two places would duplicate content already preserved in its natural form. Surfaced in the file itself (final section) + here. If preserving the verbatim self-contained nature is important, a follow-up plan can extend the file.
- **Discipline-doc adaptation was real intellectual work, not sed.** Every doc preserved structural shape + load-bearing principles + the discipline's earned wisdom (the captured-exit pattern, the 4-section trust contract, the §5.5 prompt-file convention, etc.) while replacing Somerville-specific surface text. CLAUDE.md gained two genuinely new sections (orient + closing-ritual) that don't exist in oxygen-mvp. DASHBOARDS.md is allowed to be thin at v1 with explicit `(future)` markers — honest about what isn't there yet.
- **Sizing held.** Per the Notes-for-Code instruction not to bloat CLAUDE.md just because of the new sections: stack-in-a-box's CLAUDE.md ends up shorter than oxygen-mvp's overall (the Somerville-specific weight stripped exceeds the orient + closing-ritual additions). PHILOSOPHY went down too. STANDARDS down. DASHBOARDS substantially down (allowed to be thin).
- **The 7-commit sequence on the new repo was clean.** Direct-to-main commits were appropriate per the prompt's commit-shape clause (no main to protect on day 1; branch protection is a future plan).
- **Plan 45 (perception trend dashboard) was untouched.** Per the prompt's Depends-on note, Plan 45 is unrelated and on its own branch. This plan's oxygen-mvp touch was housekeeping-only.
- **Local + EC2 not affected for stack-in-a-box.** Per Out-of-Scope: no install was attempted, no EC2 was provisioned, no shellcheck run. Those are future plans in the new repo's own ledger starting at Plan 1.

## Ready for more work — natural next moves

### In `oxygen-mvp`

1. **Plan 41** (DBA v1.2 calibration) — best after a few weeks of v1.1 data.
2. **Plan 42** (memory-to-file migrations) — needs the deliberate placement conversation. Can now target placement adjacent to PROMPTS.md §5.5.
3. **Plan 45** (perception trend dashboard) — currently in-flight on its own branch; will close in its own session.

### In `stack-in-a-box` (the new repo's own ledger starts at Plan 1)

1. **Resolve the 5 open decisions** ([`OPEN_DECISIONS.md`](https://github.com/ironmonkey88/stack-in-a-box/blob/main/docs/design/OPEN_DECISIONS.md)) — Chat-side session. Each decision needs a defensible answer before scripts run on real EC2.
2. **Shellcheck pass + idiom cleanup** on the 13 v4 scripts. Lower-hanging fruit; might bundle with decision resolution.
3. **First real install end-to-end** on a fresh EC2 instance. Budget 90 minutes.
4. **The second batch** — `run.sh` + the 16 missing artifacts per handoff §9.

The natural sequence is 1 → 2 → 3 → 4. Each unlocks the next.
