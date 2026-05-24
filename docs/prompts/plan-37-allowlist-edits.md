# Prompt — gh Tier-1 additions + redundancy cleanup + hook precedence note

**Status:** reconstructed from session narrative — not the original Chat-issued prompt.
**Sources:** [`docs/sessions/session-62-2026-05-23-plan-37-allowlist-edits.md`](../sessions/session-62-2026-05-23-plan-37-allowlist-edits.md), [`docs/audits/allowlist-audit-2026-05-22.md`](../audits/allowlist-audit-2026-05-22.md), [`TASKS.md`](../../TASKS.md) Plan 37 row, [`LOG.md`](../../LOG.md) Plans Registry row.
**Reconstruction date:** 2026-05-24 by Plan 43 (prompt + report lineage).
**Confidence:** Tracks A/B/C scope, file paths, and verification gates are taken directly from the session narrative and audit recommendations. The Outcome paragraph and the rhetorical framing are *(reconstructed, medium confidence)* — the substance is right (close Plan 36's named recommendations) but the original prompt's exact wording isn't preserved anywhere.

**Kind:** coding
**Date:** 2026-05-23
**Plan:** 37
**Scope:** `.claude/settings.json`, `CLAUDE.md`
**Effort:** one short session, ~15 minutes
**Depends on:** Plan 36 (allowlist audit) — merged. Audit report at `docs/audits/allowlist-audit-2026-05-22.md` carries the named recommendations this plan executes.

---

## Outcome

Code stops getting prompted on the two `gh` commands the autonomous-PR-merge policy already endorses (`gh pr create` and `gh pr merge`), the seven settings.json entries that Plan 36 confirmed are redundant against Claude Code's built-in auto-allow get removed, and the bash-safety-hook-fires-before-auto-allow precedence inferred during Plan 36 gets recorded in CLAUDE.md "Known gotchas" so the next session that hits it doesn't have to re-discover the pattern. Each of the three tracks is a tiny edit; the value is closing the friction Plan 36 named explicitly.

## Context

Plan 36 (Session 61) ran an information-request audit of the 3-tier allowlist + 2 additional permission surfaces. The audit produced [`docs/audits/allowlist-audit-2026-05-22.md`](../audits/allowlist-audit-2026-05-22.md). Two of its recommendations are tiny one-line edits suitable for a short follow-up plan; the other recommendation (memory-to-file migrations for 5 candidates) wants a deliberate placement conversation and is parked as a separate reserved plan.

The two one-line edits:

- **Tracked-policy mismatch (Track A).** CLAUDE.md "Receiving prompts from Chat → Autonomous PR-merge policy" endorses `gh pr create` + `gh pr merge --merge` as part of the autonomous flow, but `.claude/settings.json` doesn't include them, so every PR cycle prompts. The audit recommended adding `Bash(gh pr create *)` and `Bash(gh pr merge *)` after the existing `gh pr view/list/diff/checks/status` cluster.
- **Redundancy cleanup (Track B).** The audit identified 4 entries in `.claude/settings.json` that are fully redundant against Claude Code's built-in auto-allow: `ls`, `grep`, `cat`, and the "git log family." The "git log family" enumerates to 4 individual entries (with/without `-C`, with/without args), so total redundant entries to remove = 7.

Track C is a documentation-only addendum, also from Plan 36:

- **Hook-precedence note (Track C).** Plan 36 inferred during its denial-event audit that the bash safety hook fires *before* Claude Code's built-in auto-allow — i.e., a command whose leading token would normally auto-allow (`ls`, `grep`, etc.) still gets hook-denied if the command string contains a hook-blocked operator. This precedence isn't documented in Claude Code upstream; the inference was solid (real denial event for `ls .../worktrees/ 2>/dev/null || echo "no"`) but should be captured in CLAUDE.md "Known gotchas" so it's discoverable.

## Work

**Track A — gh Tier-1 additions.**

A1. Add to `.claude/settings.json` `permissions.allow`, after the existing `gh pr view/list/diff/checks/status` cluster:

```
Bash(gh pr create *)
Bash(gh pr merge *)
```

These activate immediately on save — `settings.json` is re-read per tool call, so this same session's PR cycle exercises them as the live-functional gate.

**Track B — redundancy cleanup.**

B1. Remove these 7 entries from `.claude/settings.json` `permissions.allow`:

```
Bash(ls *)
Bash(grep *)
Bash(cat *)
Bash(git -C * log)
Bash(git -C * log *)
Bash(git log)
Bash(git log *)
```

Net change after Tracks A + B: −5 entries.

B2. Smoke-test post-removal with a small bouquet of commands that should now auto-allow silently via Claude Code's built-in:

- `ls <some-path>`
- `grep -c <pattern> <file>`
- `cat <some-file>`
- `git -C <path> log --oneline -3`

If any of the four prompts, the redundancy claim was wrong and the entry has to go back.

**Track C — hook-precedence note.**

C1. Extend `CLAUDE.md` "Known gotchas" subsection with a new entry covering the hook-fires-before-auto-allow precedence. Include:

- The behavior in one sentence.
- The list of hook-blocked operators (`&&`, `||`, naked `;`, `$(...)`, `<()`, `>()`, leading `cd`, leading `export`).
- The practical implication: don't reach for `command || fallback` thinking "ls would auto-allow, the `||` should be fine" — the hook gets a vote first.
- An evidence pointer (the real denial event from Plan 36's audit).

## Verification

**Static-artifact gates:**

- `.claude/settings.json` contains `Bash(gh pr create *)` and `Bash(gh pr merge *)` — `git show HEAD:.claude/settings.json | grep -F 'Bash(gh pr create *)'` returns a match (per CLAUDE.md allowlist `[x]` evidence rule).
- `.claude/settings.json` no longer contains any of the 7 named redundant entries — `git show HEAD:.claude/settings.json | grep -F 'Bash(ls *)'` returns no match (etc. for each).
- `CLAUDE.md` "Known gotchas" subsection has the new hook-precedence entry, with the operator list and the practical-implication framing.

**Live-functional gates:**

- Pre-flight reproduction of halt-condition #3 (see below): `ls /tmp 2>/dev/null || echo nofile` is hook-denied for the `||` even though `ls` standalone would auto-allow. Confirms Plan 36's precedence inference.
- Post-Track-B smoke test: 4 commands (`ls`, `grep -c`, `cat`, `git -C * log --oneline -3`) all execute silently post-removal — no prompts, no denials.
- Live test of Track A: this PR's own `gh pr create` + `gh pr merge --merge --delete-branch` calls happen without prompts. `settings.json` is re-read per tool call, so the additions activate within this session.

## Halt conditions

1. **Track A patterns already present.** If `Bash(gh pr create *)` or `Bash(gh pr merge *)` already exist in `.claude/settings.json` (e.g., added by a parallel session), surface and skip the addition — don't dedupe by removing the other entry.
2. **Track B smoke test fails.** If any of the 4 smoke-test commands prompts post-removal, restore that specific entry and surface as a partial. Don't assume the redundancy claim was wrong for all 7 entries — check each.
3. **Hook precedence reproduction fails.** If `ls /tmp 2>/dev/null || echo nofile` *doesn't* get hook-denied for `||`, Plan 36's inference was wrong and the Track C note shouldn't be written. Halt and surface.

## Out of scope

- **Memory-to-file migrations.** The 5 candidates Plan 36 named (boot-audit checklist, git+SSH gotchas, no-SSH-heredocs, chat-handoff format, settings.json editing freedom) need a deliberate placement + wording conversation and are reserved as a separate plan.
- **Broader allowlist restructuring.** Plan 36 didn't recommend any structural changes to the 3-tier model; this plan doesn't either.
- **Hook code changes.** The hook precedence is a documentation observation, not a behavior change. The hook stays as-is.

## Commit shape

Single PR holding all three tracks. Each track is small and they share a single PreToolUse-hook live-test cycle (the PR's own merge), so splitting would be ceremony without value. Commit message names Plan 37.

Per CLAUDE.md autonomous-PR-merge policy: push → `gh pr create` → `gh pr merge --merge --delete-branch` autonomously. Live test of Track A *is* the merge cycle.
