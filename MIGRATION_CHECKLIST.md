# MIGRATION CHECKLIST — new Claude account + new laptop

> Tracker for the full migration. `[x]` = done, `[ ]` = to do.
> Detailed runbook: **`PROJECT_MIGRATION_2026-06-07.md`** (§9 = fresh-laptop setup, §3 = memory, §5–6 = EC2/access, §9d = allowlist). Cold-start handoff: **`docs/MIGRATION_SUMMARY.md`** (Plan 8 / oxygen Plan 50). Committed to both repos.
> **Last updated: 2026-06-17.**

---

## A. Preserve everything before the move (old laptop) — ✅ DONE
- [x] **All git work pushed** — verified *no* unpushed commits in either repo (2026-06-17). Nothing git-tracked is laptop-only.
- [x] **Migration reference docs written + committed + pushed** — `PROJECT_MIGRATION_2026-06-07.md` (root) + `docs/MIGRATION_SUMMARY.md` (Plan 8), both repos.
- [x] **Auto-memory captured** — `~/.claude` memory won't travel; all 16 facts reproduced in `PROJECT_MIGRATION §3`.
- [x] **Allowlist preserved** — the big `.claude/settings.json` (oxygen 342 / stack 235 lines) + `block-dangerous.sh` hook are **git-tracked** (clone restores them); gitignored `settings.local.json` snapshot captured in `PROJECT_MIGRATION` Appendix.
- [x] **Pending unstarted work preserved** — tech-debt-decision-register prompt at `oxygen-mvp/docs/prompts/_pending-tech-debt-decision-register.md`.
- [x] **In-flight state documented** — stack Plan 4 (branch pushed), oxygen PR #76, plan-number churn (`PROJECT_MIGRATION §4`).
- [x] **EC2 + Tailscale + access map documented** — `PROJECT_MIGRATION §5–§6`.

## B. Hand-carry the machine-local files (NOT in git — copy off old laptop)
- [ ] `~/.ssh/stackinaboxdemo.pem` (stack-in-a-box EC2 key) + the oxygen-mvp EC2 key
- [ ] `~/.config/sib/anthropic.key` + `~/.config/sib/tailscale.key`
- [ ] GitHub access for `ironmonkey88` (PAT or SSH key for `gh auth`)
- [ ] Decide EC2 disposition during the gap — keep both boxes running, or stop the **stack demo box** (`stack-in-a-box.taildee698.ts.net`; costs money; needed for Plan 4 dev)

## C. Accounts / services (none are Claude-tied — just re-auth on the new setup)
- [ ] New Claude account created (your trigger)
- [ ] GitHub `ironmonkey88` reachable from the new laptop (repos do **not** move — they stay on GitHub)
- [ ] Tailscale: new laptop joined to the `gordon@` / `taildee698.ts.net` tailnet
- [ ] Anthropic API key available to the new Claude Code (separate from the EC2 boxes' own keys in `/etc/environment`)

## D. New laptop setup (PROJECT_MIGRATION §9)
- [ ] Install: **Claude Code** (sign into new account), git, gh, Tailscale (, shellcheck)
- [ ] `mkdir -p ~/claude-projects` then clone BOTH to the exact paths:
  - [ ] `git clone https://github.com/ironmonkey88/oxygen-mvp.git ~/claude-projects/oxygen-mvp`
  - [ ] `git clone https://github.com/ironmonkey88/stack-in-a-box.git ~/claude-projects/stack-in-a-box`
- [ ] `gh auth login` (ironmonkey88)
- [ ] SSH keys → `~/.ssh/`, `chmod 400`
- [ ] Secrets → `~/.config/sib/`
- [ ] `git -C <repo> config http.postBuffer 524288000` if a binary-heavy push fails (known gotcha)

## E. Allowlist — verify it survived ⭐ (the thing not to lose)
- [x] **Committed allowlist confirmed git-tracked** (clones automatically) — `settings.json` + hook in both repos; path-portable (≤1 absolute path; same username carries it).
- [ ] After cloning, open Code in each repo and verify:
  - [ ] an allowlisted command (e.g. `git -C <repo> status`) runs **without** a prompt
  - [ ] a chained command (`echo a && echo b`) is **hook-denied** (proves `block-dangerous.sh` is active)
- [ ] (Optional) re-add the reusable `settings.local.json` patterns from `PROJECT_MIGRATION §9d`

## F. Reconstitute the Claude-side context (new account)
- [ ] Recreate the auto-memory facts (`PROJECT_MIGRATION §3`) in the new account's memory
- [ ] New Claude.ai web chat: feed it `PROJECT_MIGRATION_2026-06-07.md` (paste, or it reads the cloned repo) so it knows the two-repo discipline, roles, conventions, in-flight work
- [ ] Confirm the new chat/Code respects: don't-conflate-the-two-repos · bash-safety rules · autonomous-merge policy · PROMPTS.md workflow

## G. Verify fully migrated ("you're ready when…")
- [ ] Both repos: `git status` clean; local `main` == `origin/main`
- [ ] `gh pr list` works on both (oxygen **PR #76** visible)
- [ ] `tailscale status` shows both EC2 nodes; `ssh -i ~/.ssh/stackinaboxdemo.pem ubuntu@stack-in-a-box.taildee698.ts.net 'echo ok'` → `ok`
- [ ] Allowlist behaves (section E passes)
- [ ] A trivial Code task runs end-to-end without permission-prompt hell

## H. Resume the actual work (post-migration)
- [ ] **stack-in-a-box:** finish **Plan 4** (Phases 4/5/7 on the existing box; Phase 6 needs a fresh box) — branch `claude/plan-04-pin-gates-lockaware`, spec at its `docs/prompts/`
- [ ] **oxygen-mvp:** merge / iterate **PR #76** (Plan 47 tech-debt assessment)
- [ ] **oxygen-mvp:** start the **tech-debt decision register** — assign the real next plan # (~50; verify against the live LOG.md registry, don't guess) from `docs/prompts/_pending-tech-debt-decision-register.md`

## I. Optional cleanup (not blocking)
- [ ] Reconcile the two overlapping migration docs (`PROJECT_MIGRATION_2026-06-07.md` + `docs/MIGRATION_SUMMARY.md`) — pick one canonical or cross-link them
