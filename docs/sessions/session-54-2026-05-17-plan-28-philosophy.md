---
session: 54
date: 2026-05-17
start_time: 10:15 ET
end_time: 10:50 ET
type: code
plan: plan-A
layers: [docs]
work: [docs]
status: complete
---

## Goal

Land PHILOSOPHY.md at repo root as the standing *why beneath the why* — three inspirations (Fix The News, Intelligent Optimism, system humanism), the synthesis (an honest full picture is itself a service to residents), the New Urban Mechanics institutional precedent, the systems-engineering discipline (V-model + requirements-first + lifecycle), and seven principles each tied to something already in the codebase. Plus the Plan 22 pattern of wiring it into the project's authority-doc hierarchy so future Code sessions see it by default.

## What shipped

- [PHILOSOPHY.md](../../PHILOSOPHY.md) — new at repo root, verbatim from Gordon's chat-side draft. Five-section arc (Inspirations → Synthesis → Precedent → Discipline → Principles), self-framed as foundational-not-authority: MVP.md and BUILD.md remain operational authorities on scope and "done"; PHILOSOPHY.md is the tiebreaker when a design question is genuinely open.
- [CLAUDE.md](../../CLAUDE.md) — reading hierarchy gains a new tier "Convictions (foundational, not authority)" inserted between the existing "Foundational" tier (Analytics_Platform_Primer.docx) and the existing "Strategic + construction" tier (MVP.md / BUILD.md / STACK.md). The tier label states explicitly that PHILOSOPHY.md is not operational, so future sessions can't accidentally promote it past MVP.md or BUILD.md on scope decisions.
- [session-starter.md](../../session-starter.md) — "How We Work Together" gains a PHILOSOPHY.md bullet parallel to the PROMPTS.md bullet landed in Plan 22, so Chat picks it up by default.
- [docs/PROJECT_BRIEF_5_11_26.md](../PROJECT_BRIEF_5_11_26.md) §10 reference map gains a row pointing at PHILOSOPHY.md for "the why beneath the why."
- [LOG.md](../../LOG.md) — Plans Registry +Plan 28 row; Recent Sessions adds this session, rotates Session 49 to Earlier Sessions as a one-liner.
- [TASKS.md](../../TASKS.md) — Plan 28 row flipped `[~]` → `[x]` with evidence.

## Decisions

- **PHILOSOPHY.md sits above MVP.md in CLAUDE.md's hierarchy but is explicitly labeled "not authority."** The doc itself frames this in §1: it's the thing decisions are *checked against*, not the thing that issues them. The new tier label "Convictions (foundational, not authority)" captures this — the convictions inform the operational docs but never override them. The order in CLAUDE.md now reads: Foundational (Analytics Platform Primer) → Convictions (PHILOSOPHY) → Strategic + construction authorities (MVP/BUILD/STACK) → Exploratory (PRODUCT_NOTES) → Operational.
- **Content-additive against existing authority docs.** PHILOSOPHY.md references MVP.md / BUILD.md / ARCHITECTURE.md / PROMPTS.md / STANDARDS.md / PRODUCT_NOTES.md as companions, but no existing doc was edited beyond the three wiring sites (CLAUDE.md, session-starter.md, PROJECT_BRIEF). Keeps the change reviewable as additive only.

## Issues encountered

Receipt-time ambiguity: the prompt arrived as a paste of fully-drafted Markdown with no PROMPTS.md header (no Kind / Scope / Outcome / Work). PHILOSOPHY.md self-identifies as a top-level doc and references the hierarchy explicitly, but "save only" vs "save + wire" was a real branch point. Used `AskUserQuestion` per PROMPTS.md §5 halt-and-surface — three options offered (save+wire recommended, save only, context only). Gordon picked save+wire. The receipt-workflow caught the ambiguity rather than guessing.

## Next action

Plan 24 (MVP 3 — Happiness Survey silver/gold curation), Plans 18 + 19 (Builder-CLI dashboards now buildable with all six datasets in gold + semantic), and the Oxy customer-feedback bundle remain queued. Two follow-ups that PHILOSOPHY.md itself names as not-yet-landed but committed-to:

- **§6.2 pair-with-trend dashboard standard.** "No stress metric ships as a bare current value — it ships with its multi-year trajectory." Will need a small addition to DASHBOARDS.md when the next Data App is built.
- **§6.2 "signs of progress" subtype of the findings library.** A first-class category in the findings library, parallel to the limitations registry, that surfaces genuine progress signals. New machinery; deferred until a concrete first finding makes the shape clear.

Both are explicit commitments §6 holds the project to, not slack-talk; flag them at the next plan kickoff.
