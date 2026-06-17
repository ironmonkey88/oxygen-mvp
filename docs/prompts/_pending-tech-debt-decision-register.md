# PENDING PROMPT — Tech-debt decision register + four-lens evaluation discipline

> **Status: NOT STARTED. Plan number NOT yet assigned.** This prompt arrived via
> chat on 2026-06-05 and was halted at its own Phase 0 because the next plan
> number was ambiguous (Plan 47 was already taken by the open tech-debt-*assessment*
> PR #76). Numbers have since churned (47 = tech+test debt assessment, PR #76 open;
> 48 = APPROACH renumber; 49 = PHILOSOPHY creed). **Before executing, read the live
> LOG.md Plans Registry tail and assign the real next number — likely ~50 — do not
> guess.** Preserved here because the originating chat conversation is lost in the
> 2026-06-07 Claude-account migration. This is a *register/discipline* plan, distinct
> from the *assessment* in PR #76 (they are siblings in the same batch).

---

**Kind:** coding · **Date:** 2026-06-05 · **Effort:** one session · **Depends on:** none

**Scope:** `TECH_DEBT_LEDGER.md` (new, repo root), `PHILOSOPHY.md` (§6 — one new principle), `CLAUDE.md` (reading hierarchy + one new rule), `PROMPTS.md` (§3 — one optional section), `session-starter.md` ("How We Work Together"), `docs/PROJECT_BRIEF_5_11_26.md` (§10 reference map), `LOG.md`, `TASKS.md`

## Outcome
The department head triages tech debt by a deliberate standard — does it impair the quality of what's delivered, the ability to deliver, is it a recurring productivity tax, is it mental load — and wants the *reasoning* behind each triage decision recorded so the process compounds. After this work, the four-lens evaluation is a named, shared discipline and every triage decision (including deliberate decisions NOT to fix) is recorded in one terse, auditable register. Payoff: the team can audit its own calibration later, the triage standard transfers to anyone who joins (Virginia onboarding), and deferrals read as choices not misses.

## The four lenses (the rubric, verbatim)
1. **Final quality** — impairing the delivered product? Distinguish *current* (live defect residents see) vs *latent* (correct today, can regress).
2. **Ability to deliver** — impairing ability to ship? Distinguish *recurring tax* vs *discrete cliff* (zero cost until a specific moment, then large).
3. **Productivity tax** — recurring cost on every related change?
4. **Mental load** — tiring for the team — carried weight of unmeasured risk?

## Two seed decisions (start the register with these)
- **Python test layer for the application glue** — Final quality: **current** (limitations index feeds the trust contract; silent corruption → resident gets a confident wrong answer). Ability to deliver: moderate. Productivity tax: **high, ongoing** (every glue change needs manual re-verification). Mental load: **heaviest**. Verdict: **fix-now**. Trigger: n/a (already prioritized).
- **Python dependency pinning** — Final quality: **latent**. Ability to deliver: **discrete cliff** (zero cost until next box stand-up, then 20-min → half-day). Productivity tax: low. Mental load: low-grade. Verdict: **fix-first-as-enabler** (the test layer needs a pinned env; pinning is the ~30-min prerequisite). Trigger: a box stand-up becomes imminent.

## Work (six phases)
- **Phase 0:** write this prompt verbatim to `docs/prompts/plan-NN-tech-debt-decision-register.md` on branch `claude/plan-NN-tech-debt-decision-register` (NN = the real next number from the registry — halt if ambiguous).
- **Phase 1 — `TECH_DEBT_LEDGER.md` at repo root.** One rolling, screen-scannable file. Sections: Purpose (what it is / is not — not a backlog, TASKS.md is the tracker; supersedes `docs/tech-debt-review-2026-05-17.md` which stays as historical record); the four lenses verbatim with current/latent + recurring/cliff distinctions; verdict vocabulary (`fix-now`, `fix-when` + trigger, `accept` + reason, plus the `fix-first-as-enabler` variant); a register table (Item | Final quality | Ability to deliver | Productivity tax | Mental load | Verdict | Change trigger | Dated) seeded with the two decisions. **Terseness guardrail (write it into Purpose):** four one-line scores + a verdict per item; the moment an entry wants a paragraph per lens it is failing its own test.
- **Phase 2 — PHILOSOPHY.md §6.8 "Sustained productivity is the asset."** In the established §6 "principle + *Lives in:*" pattern. The project optimizes for *sustained* output (the vector between raw output and quality), not bursts; tech debt is evaluated deliberately against quality/delivery/productivity/mental-load and the reasoning is recorded so the process compounds. *Lives in:* the four-lens discipline + `TECH_DEBT_LEDGER.md`; the allowlist tool-family frame (Session 9); honest-reporting (§6.3). Additive only — do not renumber the existing seven principles. The balancing happens *inside* the bounds §5 sets (privacy, trust contract, honesty are not productivity variables).
- **Phase 3 — CLAUDE.md:** add `TECH_DEBT_LEDGER.md` to the Operational tier; add a Rule "Evaluating tech debt" (score against the four lenses, record the decision; a deferral/accept is a valid recorded outcome; point at PHILOSOPHY §6.8).
- **Phase 4 — PROMPTS.md §3:** add a conditional "Tradeoff rationale" section to the coding-request shape (name the four-lens score + verdict inline when a prompt closes/pays down debt). Additive; don't disturb required sections.
- **Phase 5 — Pointer wiring:** `session-starter.md` "How We Work Together" bullet; `docs/PROJECT_BRIEF_5_11_26.md` §10 reference-map row.
- **Phase 6 — Registry/tracker housekeeping:** LOG.md Plans Registry row + Active Decisions row + Recent Sessions; TASKS.md row.

## Halt conditions
- If PHILOSOPHY §6 numbering drifted from §6.1–§6.7, confirm the next free slot rather than forcing §6.8.
- If PROJECT_BRIEF §10 reference map is gone/renamed, surface rather than invent.
- If any edit would change a *required* PROMPTS.md section or reorder PHILOSOPHY principles, halt — all edits additive.

## Out of scope
- Migrating `docs/tech-debt-review-2026-05-17.md` contents into the register (register starts with the two seeds only).
- Any automated gate/hook wiring.
- The pinning + test-layer prompts themselves (separate plans; this only *records* their triage as seeds).
- `METHODOLOGY.md` (stack-in-a-box engineering rules — deliberately a separate register).

## Commit shape
Single PR, six phases (commit-per-phase ok). Documentation-only — merges on the static-artifact gate.
