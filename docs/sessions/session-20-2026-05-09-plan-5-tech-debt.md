---
session: 20
date: 2026-05-09
start_time: 21:45 ET
end_time: 09:55 ET
type: code
plan: plan-5
layers: [infra, docs]
work: [hardening, docs, refactor]
status: complete
---

## Goal

Close out the rev 2 overnight batch with a hygiene pass: settings reconciliation, dbt profiles example, scratch hygiene, run.sh step-text consistency, doc reconciliation. Bounded — no scope creep, no load-bearing refactors.

## What shipped

- [.claude/settings.local.json](.claude/settings.local.json) — pruned to `{"permissions":{"allow":[]}}`. Every accumulated pattern was redundant with a tool-family wildcard already in `settings.json`.
- [.claude/settings.json](.claude/settings.json) — added `Bash(bash *)` so script invocations don't stall (audit script, future build scripts). Bash Safety hook + destructive-deny list still bound the blast radius.
- [CLAUDE.md](CLAUDE.md) — Allowlist policy extended with three bullets: what belongs in `settings.json`, what belongs in `settings.local.json`, when to prune. Run Order section updated 7 → 9 steps with 5b sub-step.
- [dbt/profiles.example.yml](dbt/profiles.example.yml) — canonical template for `~/.dbt/profiles.yml`. Anyone provisioning a fresh box has a cp + edit path now.
- [SETUP.md](SETUP.md) — §8 rewritten to reference the example file instead of inlining the YAML.
- [ARCHITECTURE.md](ARCHITECTURE.md) — Run Order bash block updated 7 → 9 steps; Portal routes table updated (`/trust` Plan 4 done, `/erd` + `/tasks` deferred + portal-card-removed); Process management line corrected (Oxygen is `nohup oxy start`, not systemd).
- [TASKS.md](TASKS.md) — Plan 5 block closed; orphan `[~] Deliverable B` from "Documentation — MVP 1 scope sharpening" closed (the rev 2 batch made it a no-op).

## Decisions

- `settings.local.json` reset to empty allow array. Empty-by-default, accumulate only when a session genuinely needs a session-specific exception, prune again at the next tech-debt sweep.

## Issues encountered

None. Plan 5 was hygiene-shaped and stayed in scope. D3 (scratch hygiene) and D4 (run.sh step-text) were no-ops — scratch only had `plan6_test_bench/` from Session 18, and run.sh step text was already aligned in Session 18 when step 9 was added.

## Next action

Gordon decides on the two remaining MVP 1 sign-off boxes (§3.2 row 4 systemd, §4.5 row 1 repo-public). Once both flip, MVP 1 is signed off and the project moves to MVP 2 — Visual Data Product (Airapp charts and dashboards).
