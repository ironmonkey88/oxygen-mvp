---
session: 17
date: 2026-05-10
start_time: 14:38 ET
end_time: 15:00 ET
type: code
plan: plan-5
layers: [infra, docs]
work: [hardening, infra, docs]
status: complete
---

## Goal

Eliminate all remaining allowlist gaps causing overnight UI session stalls: fix the `autoMode.environment` schema error, universalize patterns that had drifted into local/worktree files, and reconcile all worktree settings files to mirror canonical local.

## What shipped

- `.claude/settings.json` — `autoMode.environment` fixed: object `{allowNetwork:true}` → `[]` (invalid schema per /doctor; "Expected array, but received object")
- `.claude/settings.json` — 6 patterns promoted from settings.local.json or worktree locals: `Skill(update-config)`, `Skill(update-config:*)`, `Bash(ssh -T git@github.com)`, `Bash(git init *)`, `Bash(git remote *)`, `Bash(./scripts/*.sh)`
- `.claude/settings.json` — explicit Write/Read for `.claude/settings.local.json` and `.claude/worktrees/*/.claude/settings.local.json` (belt-and-suspenders against the write-prompt stall that triggered Plan 5 D1)
- `.claude/settings.json` — `Bash(bash *)` promoted after coverage script run auto-added it to local mid-session (caught and promoted same pass)
- `.claude/settings.local.json` — reduced to canonical: `Read(//Users/gordonwong/.ssh/**)` + `mcp__Claude_in_Chrome__tabs_context_mcp` only; 18 redundant entries removed
- `.claude/worktrees/gifted-cartwright-9b6bac/.claude/settings.local.json` — reconciled to canonical local (was: `Bash(ssh oxygen-mvp *)` only)
- `.claude/worktrees/jovial-pasteur-8db9b1/.claude/settings.local.json` — reconciled to canonical local (was: 22-entry allow + 12-entry deny including `Bash(git *)` wildcard, `nc -zv` with hardcoded IP, 4 `echo` commands with hardcoded worktree paths)
- `.claude/worktrees/recursing-burnell-d31e2a/.claude/settings.local.json` — reconciled to canonical local (was: 23-entry allow including 5 `git -C <hardcoded-path>` session-specific entries)
- `CLAUDE.md` Rules — allowlist policy expanded from 1 sentence to three-tier rule: settings.json (universal/committed), settings.local.json (machine-specific/gitignored), worktree locals (mirror canonical local, never drift)
- Commits `6d101cc` (settings.json fixes), `6b0bc00` (CLAUDE.md), `4726183` (bash * promotion)
- `scripts/check_allowlist_coverage.sh` ran clean post-commit (zero prompts)

## Decisions

- `Bash(bash *)` promoted to settings.json (not just local) — coverage script auto-triggered local edit; pattern is universal; promoting immediately prevents re-accumulation in local.
- Worktree settings files are gitignored (`.claude/worktrees/` in `.gitignore`) — local-only state, correct; reconciliation takes effect immediately without a commit.
- `mcp__Claude_in_Chrome__tabs_context_mcp` preserved in canonical local and mirrored to all three worktree files — was only in jovial-pasteur; moved to canonical local since it's machine-specific (Chrome MCP tool), not session-specific. Gordon should prune if no longer needed.
- `Bash(git *)` broad wildcard in jovial-pasteur worktree NOT promoted to settings.json — deny list bounds it but that's not the reason: the project has opted for explicit tool-family wildcards + targeted patterns rather than a blanket git wildcard. The specific patterns we promoted (`git init *`, `git remote *`) cover the actual use cases.
- `autoMode.environment.allowNetwork` (the old object key) was cited in Session 16 session notes as a validated setting — it wasn't; it was a misconfigured object that happened to pass `python3 -m json.tool` but violated the JSON schema. The validated intent (network access in auto mode) is covered by existing session/tool-level permissions, not by this field.

## Next action

Resume Plan 5 — Tech Debt Sweep; confirm EC2 is on latest main (`git pull`) before any pipeline work.
