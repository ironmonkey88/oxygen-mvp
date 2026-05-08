---
session: 8
date: 2026-05-08
start_time: 10:00 ET
end_time: ~11:00 ET
type: code
plan: plan-0
layers: [infra, docs]
work: [hardening, infra, docs]
status: complete
---

# Session 8 — Plan 0: FR loose ends

## Goal
Close four flags from FR pass: env vars not visible to non-interactive SSH, `OXY_DATABASE_URL` undocumented, public `:3000` flagged in LOG.md, allowlist still pausing on `git -C *` write ops.

## What shipped
- EC2: `/etc/environment` now has `ANTHROPIC_API_KEY`, `OXY_DATABASE_URL`, extended PATH (`~/.local/bin`); `~/.bashrc` no longer holds the API key
- `SETUP.md` §7 (env-var contract + `/etc/environment` recipe), §11 (systemd unit gets both vars + `ExecStart` fixed)
- `CLAUDE.md` "LLM Configuration" — current `model_ref`/`key_var` schema + two-var table; fixes the stale snippet from Session 5
- LOG.md: Session 8 entry, Decisions Log + Blockers Log updated, `:3000` security gap flagged in Current Status
- TASKS.md: Plan 0 subsection under MVP 1 Hardening
- Allowlist: broad `git -C * <op> *` + `git <op> *` patterns added to both `.claude/settings.json` and `.claude/settings.local.json`. Reset/force-push/branch deliberately omitted.
- Commits: `e5e94e3` (env vars + docs + log + tasks), `196cf28` (allowlist)

## Decisions
- `/etc/environment` is canonical for SSH-visible env vars on this box (Option A from three options analysis); single-user EC2 makes the system-file-owned-by-root downside trivial
- systemd unit gets explicit `Environment=` directives (Option B from sub-decision); two sources of truth but isolation; document the duplication in SETUP.md
- `oxy build` deferred gate from 2026-05-08 07:31 ET fully resolved — embeddings built successfully during FR pass
- Allowlist: tool-family-allow + destructive-deny pattern is the frame; per-subcommand allowlisting is a treadmill

## Issues encountered
- **Plan's `~/.profile` premise was wrong.** Empirical test (`PLAN0_TEST_VAR`) confirmed Ubuntu non-interactive SSH does not source `~/.profile` (login-shell only) or `~/.bashrc` (early-return guard). Resolution: switched to `/etc/environment` per Gordon's call. Logged divergence + rationale.
- **Plans that touch environment-specific mechanisms must verify assumptions in pre-flight.** Two prior occurrences (Airlayer-bundled-into-Oxygen claim, `~/.profile` claim) confirm this is a real failure mode. Now baked into Plan 1 pre-flight.

## Validation gates (all green)
1. `ssh oxygen-mvp 'echo $ANTHROPIC_API_KEY | head -c 14'` — `sk-ant-api03-E` (no `bash -ic`)
2. `ssh oxygen-mvp 'echo $OXY_DATABASE_URL'` — `postgresql://postgres:postgres@localhost:15432/oxy`
3. `ssh oxygen-mvp 'oxy build'` — Build complete, exit 0
4. Agent answers 2024 question — 113,961 (matches FR pass exactly)
5. LOG.md no unresolved overnight blockers — 2026-05-08 07:22 ET row marked "Fully resolved 10:05 ET"
6. `.claude/settings.json` valid JSON + new write-op patterns — both files validated

## Next action
Plan 0.5 (portal `/chat` fix), then Plan 1 (Tailscale).
