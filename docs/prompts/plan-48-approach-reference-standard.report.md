# Report — Plan 48: APPROACH.md as the cross-repo reference standard

**Status:** complete
**Date:** 2026-06-10
**Session:** 69
**Repo:** `oxygen-mvp` (Plan 48) · sibling `stack-in-a-box` (Plan 5)
**Prompt:** [`plan-48-approach-reference-standard.md`](plan-48-approach-reference-standard.md)
**PR (this repo):** https://github.com/ironmonkey88/oxygen-mvp/pull/78 (original landing, titled "Plan 47") + renumber follow-up PR (47 → 48)
**PR (sibling):** https://github.com/ironmonkey88/stack-in-a-box/pull/8 (Plan 5)

> **Plan-number note.** This work first merged as **Plan 47** (PR #78) before a
> collision was found with the older still-open PR #76 ("Plan 47: tech + test
> debt assessment"). Per Gordon's call it was renumbered **47 → 48** (the next
> free slot) in a follow-up PR; #76 keeps Plan 47. The branch name
> `claude/plan-47-approach-reference-standard` and PR #78's title are historical
> and unchanged.

---

## Outcome

`APPROACH.md` now exists at the root of both repos, byte-identical, as the
plain-language **reference standard** for how the project works. A reader who
wants "what does this project believe and how does it work" has one short doc;
future design decisions have a standard to check against. PHILOSOPHY.md is now
explicitly framed (in CLAUDE.md and session-starter.md) as the Somerville-
specific instance that specializes the standard.

## What shipped (this repo)

- `APPROACH.md` (new, root) — canonical merged body.
- `CLAUDE.md` — new "Reference standard (cross-repo, above the convictions)"
  tier above the Convictions/PHILOSOPHY.md entry; states the reconciliation
  rule.
- `session-starter.md` — parallel APPROACH.md bullet above the PHILOSOPHY.md
  bullet in "How We Work Together".
- `LOG.md` — Plans Registry Plan 48 row + Last Updated bump.
- `TASKS.md` — Plan 48 done entry in Next Focus.
- `docs/prompts/plan-48-approach-reference-standard.{md,report.md}` — prompt
  (Phase 0) + this report.

## Decisions

- **Plan numbers** — oxygen-mvp **48** (first landed as 47, then renumbered —
  see the Plan-number note above; 41/42/45 reserved, 47 taken by the older open
  PR #76); stack-in-a-box **5**, not 4 — Plan 4 there was already reserved for
  the retroactive Oxygen-version pin. Neither slot was ambiguous on `main`; the
  47 collision was an unmerged-PR claim the registry didn't yet show.
- **Canonical body delivery** — the prompt's "Canonical content" section was a
  placeholder; the attachment it referenced was not delivered. The body arrived
  separately in Chat, alongside an aligned Google Doc ("How-We-Build-Summary").
- **Merge (Gordon-approved)** — the pasted body and the Google Doc differed in
  three ways: title; a newcomer "start here" intro line (Doc only); the closing
  reconciliation paragraph (pasted body only, and required by Work item 5).
  Resolution: pasted body as base + the Doc's intro line, title kept per Phase
  0. Single human-approved deviation from pure-verbatim.
- **stack-in-a-box wiring** — that repo has no `session-starter.md`. Gordon
  chose to **create one** (mirroring oxygen-mvp's structure) and wire the
  pointer there, in addition to the CLAUDE.md reading-hierarchy tier.

## Verification (all static-artifact gates)

- `APPROACH.md` at both repo roots, identical body — `diff` returned empty.
- `CLAUDE.md` references APPROACH.md at the correct tier (above PHILOSOPHY.md) in
  both repos.
- `session-starter.md` references APPROACH.md in both repos (created in
  stack-in-a-box).
- No existing doc edited beyond the named wiring sites.
- LOG.md + TASKS.md updated in both repos.
- **Contradiction halt check:** both PHILOSOPHY.md files read in full and found
  compatible — each specializes the standard, no principle stated in conflict.
  Halt did not fire.

No live-functional gates — nothing executes.

## Out of scope (separate already-scoped prompts)

PHILOSOPHY.md generalization to APPROACH-compatible general language; the
empathy/honesty/optimism creed; the Sensemake/system-humanism methodology work.
No `.docx`/export tooling. No new doc beyond APPROACH.md + wiring.

## Next action

Land the sibling `stack-in-a-box` Plan 5 PR (parallel), then both merge. No
follow-up obligation from this plan.
