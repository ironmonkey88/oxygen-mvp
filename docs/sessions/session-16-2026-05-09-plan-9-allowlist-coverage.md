---
session: 16
date: 2026-05-09
start_time: 17:30 ET
end_time: 19:05 ET
type: code
plan: plan-9
layers: [infra, docs]
work: [hardening, infra, docs]
status: complete
---

## Goal

Eliminate allowlist-induced stalls on read-only and verification work for unattended sessions, without weakening the destructive-deny boundary.

## What shipped

- `.claude/settings.json` Layer 0 structural items: `$schema`, `permissions.defaultMode: "acceptEdits"`, top-level `Read`/`Write`/`Edit`/`WebFetch(*)` entries, top-level `autoMode.environment.allowNetwork: true`, `Read(**/.env)` in deny list.
- `.claude/settings.json` Layer 1 verification-idiom cohort: `Bash(wget *)`, `Bash(rsync *)`, `Bash(npm *)`, `Bash(pnpm *)`, `Bash(for * in *; do *; done)`, `Bash(while * do * done)`, `Bash(if * then * fi)`, `Bash([ * ])`, `Bash([[ * ]])`, `Bash(cat *)`, `Bash(less *)`, `Bash(more *)`, `Bash(sed *)`, `Bash(cmp *)`, `Bash(yq *)`, `Bash(python3 -m json.tool *)`, `Bash(pwd)`, `Bash(uptime)`, `Bash(whoami)`. Existing patterns (curl, jq, grep, head, tail, awk, find, stat, etc.) already covered — added only what was missing to avoid duplicates.
- Granular sudo allow list preserved (`sudo cp/mv/ln/chmod/chown/nginx/systemctl …`) — no blanket `sudo *` deny adopted; deploy-path steps in `run.sh` keep working unattended.
- Deny list intact + `Read(**/.env)` added: `git reset --hard *`, `git push --force/-f`, `git branch -d/-D`, `rm -rf *`, `sudo rm/dd/bash/sh/-i/-s`, `sudo chmod/chown /etc/*`, `aws *` all retained.
- `scripts/check_allowlist_coverage.sh` — exercises canonical idioms (curl, for-loop, grep+head+wc, date, find+stat, jq, sed -i with mac/linux portability, ssh oxygen-mvp). Ran clean, zero prompts.
- `CLAUDE.md` LOG Logging Protocol — added "Allowlist `[x]` rule" (commit hash for `.claude/settings.json` required) and "`[x]` evidence rule" (commit hash | command output | file path+lines).
- `CLAUDE.md` frontmatter `plan:` vocabulary extended to include `plan-6` … `plan-9` (was stale at `plan-5`; registry already has 6-8 queued).
- `TASKS.md` — new Plan 9 block under "MVP 1 — Hardening for analyst trust".

## Decisions

- Plan 9 lands as a dedicated, separately-committed plan rather than rolling into the in-progress rev 2 batch — D7b "regression" was the third allowlist-coverage incident (Sessions 13 `sed -i`, Session 14 partial-commit investigation, Session 15 `curl`+`for` compound). Pattern is structural; needs its own close-out.
- `defaultMode: "acceptEdits"` adopted at the `permissions` level — single setting that auto-accepts Edit/Write/Read for files in the project; high leverage for unattended runs without weakening Bash boundaries.
- `Bash(sed *)` is allowed despite Session 13 incident — Gordon's call: destructive-deny (`rm -rf`, `git reset --hard`, `sudo bash/sh`, `sudo rm/dd`) bounds the blast radius. `sed -i` on a tracked file is recoverable via `git restore`; on an untracked file it's a manual-typo class problem, not an allowlist class problem.
- `Bash(npm *)` / `Bash(pnpm *)` allowed prophylactically — agent and portal don't have Node deps today, but if they grow them, future sessions shouldn't stall on the first `npm install`.
- No blanket `sudo *` deny — Gordon's reference settings (different project) had one, but this project's `run.sh` deploy step legitimately uses `sudo cp/mv/ln/chmod/chown/nginx/systemctl …`. Granular allows + granular denies stay.

## Issues encountered

None. Layer 1 patterns added cleanly; Layer 2 script ran clean on first attempt — Code's running session picked up the new patterns mid-flight without requiring a session restart.

## Evidence

```
$ python3 -m json.tool .claude/settings.json >/dev/null && echo OK
OK

$ jq -r '.permissions.deny[]' .claude/settings.json | head -3
Read(**/.env)
Bash(git reset --hard *)
Bash(git reset --hard)

$ jq '.permissions.defaultMode, ."$schema", .autoMode.environment.allowNetwork' .claude/settings.json
"acceptEdits"
"https://json.schemastore.org/claude-code-settings.json"
true

$ ./scripts/check_allowlist_coverage.sh
=== curl ===
=== for-loop ===
=== grep + head + wc ===
=== date ===
=== find + stat ===
=== jq ===
=== sed -i (touch a tmpfile, edit it, remove it) ===
=== ssh to EC2 (Tailnet) ===
All idioms passed without prompting.
```

## Next action

Don't auto-chain. Read LOG.md to confirm last clean plan was Plan 4, check whether the rev 2 batch left behind any partial state, then either resume Plan 5 or do a recovery pass on whatever stalled.
