---
session: 42
date: 2026-05-13
start_time: 23:00 ET
end_time: 23:55 ET
type: code
plan: plan-11
layers: [docs, portal]
work: [bugfix, docs]
status: complete
---

## Goal

Operator reported the `InvalidCharacterError: atob` error recurring
on `/apps/rat_complaints_by_ward` after Session 41's ASCII-fix of
the `.app.yml` was supposed to have resolved it. Diagnose properly,
fix properly.

## What shipped

- **First attempt (PR [#3](https://github.com/ironmonkey88/oxygen-mvp/pull/3), merged as `0fc956e`) -- wrong hypothesis.**
  Reasoned that the SPA loads other workspace files (agents, semantic
  views, dbt models) when rendering an app, so the atob bug must
  span more than `.app.yml`. Built `/tmp/asciify_workspace.py`,
  swept 22 files / 128 non-ASCII chars across `agents/`,
  `semantics/views/`, `dbt/models/**`, and `docs/limitations/_index.yaml`.
  Operator retested -- same error.
- **Real diagnosis.** Curled the SPA bundle from EC2
  (`/assets/index-uGZkA66J.js`, 2.27MB), grepped for `atob`, found:

  ```js
  function Ip(e){ return decodeURIComponent(atob(e).split('').map(...)) }
  APP: e => `${workspaceRoot}/apps/${e}`
  let n = Fp(t.path), r = APP(n)
  ```

  `Ip` is a UTF-8-safe base64 decoder; the SPA's `/apps/:pathb64`
  route expects a base64-encoded path. Callers always `Fp()` (btoa)
  the path before constructing the URL. The portal's `/dashboards`
  link sent the raw name `rat_complaints_by_ward`, whose underscores
  aren't in the base64 alphabet -- so `atob` threw.
- **Hypothesis test.** Sent operator the URL
  `/apps/YXBwcy9yYXRfY29tcGxhaW50c19ieV93YXJkLmFwcC55bWw=`
  (base64 of `apps/rat_complaints_by_ward.app.yml`). Operator
  confirmed it loaded cleanly.
- **Real fix (PR [#4](https://github.com/ironmonkey88/oxygen-mvp/pull/4), merged as [`0d2458b`](https://github.com/ironmonkey88/oxygen-mvp/commit/0d2458b)).**
  [`portal/dashboards.html:202`](portal/dashboards.html:202) `Open in workspace` link
  uses the base64-encoded path. Limitation entry
  [`docs/limitations/spa-render-atob-on-utf8-markdown.md`](docs/limitations/spa-render-atob-on-utf8-markdown.md)
  flipped to `status: resolved` with content rewritten to capture
  the real root cause + the diagnostic lesson. EC2 pulled +
  `sudo cp portal/dashboards.html /var/www/somerville/`; verified
  public portal serves the corrected URL. Operator confirmed.

## Decisions

- **The Session 41 + 42 workspace ASCII-fies are not being reverted.**
  Semantically equivalent to the originals, harmless, already in
  main. Reverting would be more churn for no functional gain. The
  retracted limitation entry explicitly notes the underlying
  constraint was false and the suggested grep guard should not be
  wired up.
- **Limitation entry retraction was written as a rewrite, not a
  deletion.** Future archaeology benefits from the "wrong hypothesis
  + how it was caught" lesson more than from a missing file. The
  entry now leads with "What we thought it was" / "What it actually
  was" and ends with "What this is NOT" (not an Oxygen SPA
  limitation). The Session 41 + 42 changes are documented as
  unnecessary-but-harmless, with the broken constraint explicitly
  named.

## Issues encountered

- **First-attempt PR #3 was based on a misread of the stack trace.**
  The diagnostic read `atob` -> "must be UTF-8 somewhere",
  assumed the input came from workspace content, and never
  inspected what `Ip` actually does. A two-minute look at `Ip`'s
  body (which is a literal URL-param decoder) would have caught
  this. Lesson: read the function body, not just the function
  name -- the minified bundle is not opaque,
  `grep atob /tmp/spa-bundle.js | head -200 chars` was enough.
- **Worktree was behind origin/main after PR #3 merged.**
  Branch `claude/plan-11-rat-complaints` at `44c2e94` (pre-PR #3),
  origin/main at `0fc956e` (post-PR #3). Stashed dirty changes
  for the real fix, fast-forwarded the worktree to main, created
  a fresh branch (`claude/spa-route-base64-fix`), restored the
  edits, regenerated `_index.yaml`, committed clean.

## Next action

Continue Plan 11 retro work / move on to whatever Gordon scopes
next. The `/apps/:pathb64` URL contract is now documented; any
future auto-generated portal listing must encode paths via `btoa`
before constructing the link. Three Oxy customer-feedback findings
(CLI token-budget hang + default trust-signal behavior gap +
no third item now -- the SPA UTF-8 "bug" is retracted) remain
queued in `docs/limitations/`; the bundle is ready to file as one
Oxy-side ticket when Gordon picks it up.
