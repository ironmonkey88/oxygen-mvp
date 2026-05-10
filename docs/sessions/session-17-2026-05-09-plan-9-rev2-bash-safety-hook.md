---
session: 17
date: 2026-05-09
start_time: 19:18 ET
end_time: 19:35 ET
type: code
plan: plan-9
layers: [infra, docs]
work: [hardening, infra, docs]
status: complete
---

## Goal

Replace Plan 9 rev 1's allow-pattern-only fix with the structural fix: a PreToolUse hook that denies risky shell *shapes* (chains, command/process substitution, leading `cd`/`export`) so the allowlist no longer has to model compound commands.

## What shipped

- [.claude/hooks/block-dangerous.sh](.claude/hooks/block-dangerous.sh) — PreToolUse hook on `Bash`. Denies `&&`, `||`, naked `;`, `$(...)` (arithmetic `$((...))` exempt), `<()`/`>()`, leading `cd `, leading `export `. Loop-keyword carve-out: `; (do|then|done|fi|else|elif)` stripped before `;` check, so `for`/`while`/`if` work as single tool calls.
- [.claude/settings.json](.claude/settings.json) — appended new hook to `hooks.PreToolUse` (matcher Bash) alongside the existing task-warning hook (not replacing it). Added `Bash(git *)` bare and `Bash(sudo ln *)` to allow. Added `Read(~/.ssh/**)`, `Read(~/.gnupg/**)`, `Bash(launchctl *)`, `Bash(eval *)`, `Bash(curl * | bash*)`, `Bash(curl * | sh*)`, `Bash(wget * | bash*)`, `Bash(wget * | sh*)` to deny. All Plan 9 rev 1 patterns preserved.
- [CLAUDE.md](CLAUDE.md) — new "Bash Safety" section between Rules and Naming Standards. Documents the hook, the rules Code should follow, and the activation-timing nuance (settings re-read per tool call → hook is live mid-session, not just on next session start).
- [scripts/check_allowlist_coverage.sh](scripts/check_allowlist_coverage.sh) — rewritten. Section 1: 11 idiom checks (curl, for/while/if, pipes, date, find/stat, jq, sed -i, python3 json.tool, ssh oxygen-mvp). Section 2: 13 hook-deny/allow assertions. Built via `jq -n --arg c "$cmd"` for proper JSON escaping.
- [TASKS.md](TASKS.md) — Plan 9 rev 2 block added under MVP 1 Hardening, all `[x]`.
- [LOG.md](LOG.md) — Plans Registry row, Recent Sessions entry, 4 decisions, Last Updated → 2026-05-09 19:35 ET. Session 12 rotated to Earlier Sessions.

## Decisions

- Structural fix, not more allow patterns — allowlist syntax cannot match compound commands; the hook is the right layer.
- Loop-keyword carve-out in the hook regex — strips `; (do|then|done|fi|else|elif)` before checking for chains, so `for ... ; do ... ; done` etc. pass.
- Allow merge, not allow replace — handoff plan would have dropped ~40 current patterns (airlayer, duckdb, gh pr, run.sh, granular nginx sudo); kept all rev 1 patterns and added 2 allows + 8 denies on top.
- Append hook, not replace existing PreToolUse entry — task-warning hook on `ssh oxygen-mvp` retained as a sibling entry.

## Issues encountered

First audit run failed on the "command sub" assertion. Cause: the original assertion built JSON via shell string interpolation (`"{\"command\":\"$cmd\"}"`), and the test's `cmd` value `echo \$(date)` produced an invalid JSON escape `\$` that jq couldn't parse cleanly. Fix: switched to `jq -n --arg c "$cmd" '{tool_name:"Bash",tool_input:{command:$c}}'` so jq handles all JSON escaping. Second run passed 24/24.

Also caught: the "while loop" assertion as-handed had a leading `i=0;` that the hook (correctly) denied — `; while` is not in the loop-keyword carve-out. Rewrote to `while false; do echo never; done` — single statement, exempt via `; do` and `; done` strip.

## Next action

State-check the rev 2 chat batch (Plan 4 was the last clean functional plan close in Session 15). Resume with Plan 5 — Tech Debt Sweep, or recovery on whatever stalled before Plan 9 rev 1 was inserted.
