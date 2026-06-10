# Report — Plan 47: APPROACH.md as the cross-repo reference standard

**Status:** complete
**Date:** 2026-06-10
**Session:** 69
**Repo:** `oxygen-mvp` (Plan 47) · sibling `stack-in-a-box` (Plan 5)
**Prompt:** [`plan-47-approach-reference-standard.md`](plan-47-approach-reference-standard.md)
**PR (this repo):** https://github.com/ironmonkey88/oxygen-mvp/pull/78
**PR (sibling):** see `stack-in-a-box` Plan 5 PR (linked in that repo's report)

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
- `LOG.md` — Plans Registry Plan 47 row + Last Updated bump.
- `TASKS.md` — Plan 47 done entry in Next Focus.
- `docs/prompts/plan-47-approach-reference-standard.{md,report.md}` — prompt
  (Phase 0) + this report.

## Decisions

- **Plan numbers** — oxygen-mvp **47** (41/42/45 reserved, 46 highest used);
  stack-in-a-box **5**, not 4 — Plan 4 there was already reserved for the
  retroactive Oxygen-version pin. Neither ambiguous; plan-number halt did not
  fire.
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
