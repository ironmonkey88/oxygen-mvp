---
session: 62
date: 2026-05-23
start_time: 21:50 ET
end_time: 22:04 ET
type: code
plan: plan-37
layers: [infra, docs]
work: [hardening, docs]
status: complete
---

## Goal

Land Plan 36 audit's two-line-edit recommendations across three tracks in one PR. Track A: add the two `gh` Tier-1 patterns that close the every-PR-prompts papercut. Track B: remove the 4 redundant entries the audit named with evidence (which expand to 7 individual entries once the "git -C * log family" is enumerated). Track C: document the hook-precedes-auto-allow precedence Plan 36 inferred from a real denial event.

## What shipped

- **Track A** — `.claude/settings.json` adds `Bash(gh pr create *)` + `Bash(gh pr merge *)` after the existing `gh pr view/list/diff/checks/status` cluster (lines 89-94 region). Tracked-policy mismatch (CLAUDE.md autonomous-execution endorses both, settings.json was making Code prompt) now closed.
- **Track B** — 7 entries removed from `.claude/settings.json`: `Bash(ls *)`, `Bash(grep *)`, `Bash(cat *)`, `Bash(git -C * log)`, `Bash(git -C * log *)`, `Bash(git log)`, `Bash(git log *)`. Net change after Track A + B: −5 entries.
- **Track C** — `CLAUDE.md` "Known gotchas" subsection extended with a new 3-line bullet: "The bash safety hook fires *before* Claude Code's built-in auto-allow. A command whose leading token would normally auto-allow (`ls`, `grep`, `cat`, `git log`, etc.) will still be hook-denied if the command string contains a hook-blocked operator (`&&`, `||`, naked `;`, `$(...)`, `<()`, `>()`, leading `cd`, leading `export`)." Evidence pointer included.
- LOG.md Plans Registry row + Recent Sessions rotation (Session 57 → Earlier as halt-record one-liner) + Last Updated bump.
- TASKS.md Plan 37 row flipped `[~]` → `[x]`.
- Session file (this one).
- PR [#64](https://github.com/ironmonkey88/oxygen-mvp/pull/64), commit `<TBD>`.

## Decisions

None. Straightforward execution against Plan 36's named recommendations — every edit had explicit evidence from the audit's Phase 1 + Phase 2 + recommendations sections. No scope expansion beyond the 4 named redundant entries (which enumerated to 7 once the "git -C * log family" was unpacked into its 4 individual entries: with/without `-C`, with/without args).

## Issues encountered

None. Pre-flight halt-condition #3 reproduction (`ls /tmp 2>/dev/null || echo nofile`) confirmed hook precedes auto-allow exactly as Plan 36 inferred — the `||` operator triggered "Compound commands (&&/||) blocked" even though `ls` standalone would auto-allow via built-in. Post-removal smoke test (`ls /Users/gordonwong/claude-projects/oxygen-mvp/docs`, `grep -c "Plan" LOG.md`, `cat .gitignore`, `git -C ... log --oneline -3`) — all four executed silently with no prompts and no denials. Plan 36's redundancy claim verified in practice.

## Next action

Plan 38 (memory-to-file migrations for 5 candidates Plan 36 named) when the placement conversation feels timely — each is a real CLAUDE.md / PROMPTS.md section edit needing deliberate placement and wording, not bolt-on. Plan 24 (MVP 3 survey curation), Plans 18 + 19 (Builder-CLI dashboards), DBA Dashboard execution still queued.
