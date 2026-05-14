---
id: spa-render-atob-on-utf8-markdown
title: SPA atob InvalidCharacterError on /apps/* (resolved -- portal link bug, not an Oxygen limitation)
severity: info
affects:
  - portal/dashboards.html
since: 2026-05-14
status: resolved
resolved: 2026-05-14
---

# SPA atob InvalidCharacterError on /apps/* -- resolved, was a portal-link bug

## What we thought it was

Session 41 (Plan 11 visual-gate fix) and Session 42 (broader workspace
sweep) interpreted this `InvalidCharacterError` stack trace as an
Oxygen SPA limitation around UTF-8 in workspace files:

```
InvalidCharacterError: Failed to execute 'atob' on 'Window':
The string to be decoded is not correctly encoded.
    at Ip (...assets/index-uGZkA66J.js:4:84489)
    at ...assets/index-uGZkA66J.js:156:60512 (Object.useMemo)
```

The reasoning was: `Ip` calls `atob`, `atob` chokes on non-base64
input, non-ASCII bytes in workspace YAML/SQL break the encode/decode
pair somewhere server-side. Hypothesis fix: ASCII-ify all workspace
files the SPA might load. Session 41 did `apps/*.app.yml`; Session 42
widened to agents, semantic views, dbt models, schema.yml, dbt
tests, and the limitations index -- 22 files, 128 non-ASCII chars.

Neither fix made the error go away.

## What it actually was

Session 42 follow-up inspection of `assets/index-uGZkA66J.js`
revealed:

```js
function Ip(e){
  return decodeURIComponent(
    atob(e).split('').map(...)
  )
}
```

`Ip` is the SPA's standard "decode a base64-encoded URL path
parameter back to a UTF-8 path string" helper. The route definition
is:

```js
APP: e => `${workspaceRoot}/apps/${e}`
```

And callers build `e` with `Fp(t.path)` -- which `btoa`-encodes the
full file path. So the route is **`/apps/<base64(path)>`**, not
`/apps/<raw-name>`.

The portal's `/dashboards` page (`portal/dashboards.html`) was
linking to:

```
/apps/rat_complaints_by_ward
```

`rat_complaints_by_ward` contains underscores, which are not in the
base64 alphabet (`A-Z`, `a-z`, `0-9`, `+`, `/`, `=`). The SPA
extracted the segment as `pathb64`, passed it to `atob`, and threw.

Hypothesis test: open
`/apps/YXBwcy9yYXRfY29tcGxhaW50c19ieV93YXJkLmFwcC55bWw=`
(base64 of `apps/rat_complaints_by_ward.app.yml`) directly in the
browser. Dashboard rendered cleanly with all 4 charts + 2 tables +
trust signals. Root cause confirmed.

## Resolution

[`portal/dashboards.html`](../../portal/dashboards.html) `Open in
workspace` link was updated to use the base64-encoded path. This is
the actual SPA contract for the `/apps/:pathb64` route; matching it
is the fix.

## Lessons

- **The SPA route `/apps/:pathb64` expects a base64-encoded full
  file path** (e.g., `apps/rat_complaints_by_ward.app.yml` ->
  `YXBwcy9yYXRfY29tcGxhaW50c19ieV93YXJkLmFwcC55bWw=`). Future
  portal pages that link into the SPA must encode paths with `btoa`
  before constructing the URL. If/when the portal listing is
  auto-generated from `apps/*.app.yml` metadata, the generator must
  do this encoding step.

- **Read the stack frame, not just the function name.** The
  Session 41 diagnostic read `atob` -> "must be UTF-8". A two-minute
  inspection of `Ip`'s body would have shown it's a URL-param
  decoder, not a workspace-content decoder. The minified bundle is
  not opaque -- `grep atob` plus 200 chars of context was enough.

- **The Session 41 + 42 workspace ASCII-fies were unnecessary** but
  not harmful. The changes (em-dash -> `--`, arrows -> `->`, etc.)
  are semantically equivalent and didn't break anything, so they
  are not being reverted. The Session 41 entry suggested a
  `grep -nP "[\x80-\xff]" apps/*.app.yml` pre-commit guard; it was
  never wired up as an actual hook, and shouldn't be -- the
  underlying constraint was false.

## What this is NOT

This is NOT an Oxygen SPA limitation. The SPA is working as
designed. The bug was in our portal HTML.
