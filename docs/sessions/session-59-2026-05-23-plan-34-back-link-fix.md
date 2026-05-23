---
session: 59
date: 2026-05-23
start_time: 15:20 ET
end_time: 15:40 ET
type: code
plan: plan-34
layers: [semantic, portal, docs]
work: [bugfix, docs]
status: complete
---

## Goal

Close Plan 32's halted back-link story by trying Approach #1 (plain Markdown) per Plan 33's marked.js + sanitize:true finding. Verify via the Plan 33 Playwright helper. Fall through to Approach #4 (nginx-layer nav) only if #1 fails. Plus three carry-over drift items: B1 portal/index.html regen-not-committed pattern, B2 `.oxy_state/apps/` untracked dir, B3 `git http.postBuffer` finding from Plan 33.

## What shipped

- **Track A — Approach #1 succeeded.** Top back-link in `dbt/models/overview.md` changed from bare `<a href="/" style="display:inline-block;padding:8px 16px;...">← Back to Somerville Analytics portal</a>` to plain Markdown `[← Back to Somerville Analytics portal](/)`. Re-ran `dbt docs generate` on EC2 (already serves from `/home/ubuntu/oxygen-mvp/dbt/target/` via nginx alias `/docs`).
- **Three sub-gates verified via Plan 33 helper** at `http://18.224.151.49/docs/`:
  1. DOM check — `back-link-dom.json` records `kind: "anchor"` with `outerHTML: <a href="/">← Back to Somerville Analytics portal</a>`.
  2. Visual distinction — link color `rgb(0, 187, 187)` (cyan) vs body text `rgb(94, 102, 108)` (gray); display `inline` vs `block`; font-weight identical (400) but color carries the signal cleanly.
  3. Navigation — separate `test_page()` invocation with a click-and-verify-URL assertion: `[PASS] click navigated from /docs/ to 'http://18.224.151.49/'`.
- **Design review committed** at `docs/design-reviews/back-link-fix-plan-34-2026-05-22/`: `finding.md` + `annotated.png` (callout 1 on the cyan top link, callout 2 on the still-broken bottom literal-text) + `post-click-screenshot.png` (capture of the portal home after click navigation) + 5 raw-evidence files.
- **Track B B1** — boot-audit memory `feedback_session_boot_audit.md` step 4 extended: if `portal/index.html` shows as modified, `wc -l` the diff and decide per session whether the daily systemd regen is worth committing (newer data — row count grew, latest pipeline time advanced) or rolling back (identical/unchanged). Auto-commit-and-push from systemd was explicitly rejected on blast-radius grounds — credentials-in-systemd is too much for a hygiene fix.
- **Track B B2** — `.oxy_state/` added to `.gitignore`. Inspection confirmed `.oxy_state/apps/data/rat_complaints_by_ward/` holds 8+ UUID-named per-execution parquet snapshots (<2KB each) plus a hash-named YAML — clearly local cache state, not repo-worthy.
- **Track B B3** — new "Known gotchas" subsection in `CLAUDE.md` after "Bash Safety", capturing: `git push` HTTP 400 + remote-end-hung-up on commits with large binary blobs → `git config http.postBuffer 524288000`. EC2's local clone already has this set as of Plan 33; fresh local clones need to re-set it.
- LOG.md Plan 34 row in Plans Registry + Recent Sessions rotation (Session 54 → Earlier) + Last Updated bump.
- TASKS.md Plan 34 row marked `[~]` mid-session; will close as `[x]` in the next session's first read (no need to re-edit if the LOG row is the canonical record).

## Decisions

- **Three sub-gates were sufficient evidence to ship Approach #1.** The prompt's gate definition allowed "different color OR font-weight." Cyan vs gray is unambiguous color contrast — no need to add font-weight differentiation or push for a more emphatic style. The Playwright helper's computed-style capture made this a clean yes.
- **B1 went option 2 (boot-audit checklist) over option 1 (systemd auto-commit).** Per prompt's lean + Code's reading: auto-commit-from-systemd would need committed credentials, GitHub authentication in the systemd unit's environment, and a decision about what to do when the daily run produces a no-op regen (extra noise commits). Boot-audit catches the drift at the natural decision point — a human looking at the run output — with zero new infrastructure.
- **Bottom back-link left untouched per prompt scoping.** Same source `<a>` form, same `kind: literal-text` rendering. A consistency follow-up would apply the same plain-Markdown shape; flagged in Worth flagging but not done here.

## Issues encountered

None. Each step matched the prompt's expected flow: pre-flight clean (Playwright 1.60.0 + Pillow 12.2.0 + Chromium 1223 still on EC2, /docs/ live 200, branch off origin/main); helper invocation produced the expected evidence shape; all three sub-gates passed on first attempt.

## Next action

Plan 35 (allowlist audit, slot reserved). Bottom back-link of `dbt/models/overview.md` is still in the broken-render state — applying the same plain-Markdown shape would be a small consistency follow-up; flagged for Gordon. Plan 24 MVP 3 survey curation, Plans 18 + 19 Builder-CLI dashboards, DBA Dashboard execution still queued.
