---
session: 6
date: 2026-05-08
start_time: 09:02 ET
end_time: unknown
type: planning
plan: none
layers: [docs]
work: [planning, docs]
status: complete
---

# Session 6 — MVP 1 scope sharpening

## Goal
Sharpen MVP 1 around a single experience — analyst asks Answer Agent a question, gets a verifiable answer, trusts it enough for a public report. Capture "done done" spec in a new STANDARDS.md so the bar is auditable, not narrative.

## What shipped
- Created `STANDARDS.md` at repo root — single-file spec, 7 sections: Purpose, Target user, Foundational standards (Security/Reliability/Usability), Extreme trustability, Layer standards, MVP 1 sign-off checklist, Open questions
- Updated `TASKS.md`: added MVP 1 Scope statement subsection, "Hardening for analyst trust" section (Tailscale, dbt docs, /metrics + /trust, limitations registry), Answer Agent SQL+row count+citations requirement, replaced MVP 1 Sign-off with STANDARDS.md-anchored checklist
- Marked "Configure EC2 to pull from GitHub" `[x]` (already addressed by CLAUDE.md "Session Start on EC2")
- Replaced ~25 ultra-specific allowlist entries with broad patterns: `Bash(git -C * <subcommand> *)` for write ops, `Bash(dbt|oxy|airlayer|duckdb|python3 *)` for data tooling. Did not allow `git reset *` or `git push --force *`.

## Decisions
- Target persona for MVP 1 is **city analyst**, not general resident — power user, reads SQL, iterates
- Trust bar raised from "trustworthy" to **extreme trustability** — citations, SQL, row counts visible in every agent response
- **Tailscale pulled forward from MVP 3 to MVP 1** — operational necessity (Gordon's IP changes) plus :3000 should close to public
- STANDARDS.md is the spec for "done done" — no duplication in CLAUDE.md/ARCHITECTURE.md
- `/trust` page is dynamic (driven by `admin.fct_test_run`), not static narrative
- `/metrics` page auto-generated from Airlayer YAML — never hand-written
- `/about` page deferred (resident-facing, not the MVP 1 persona)
- Long-form `.qmd` docs deferred — `dbt docs` with full descriptions sufficient
- Exports, charts, follow-up suggestions, anomaly surfacing all deferred to MVP 2+

## Issues encountered
None.

## Next action
Gordon picks the next thread — likely Tailscale (low effort, unblocks daily SSH/Oxygen) or dbt docs population (analyst-trust foundation).
