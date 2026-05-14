---
id: spa-render-atob-on-utf8-markdown
title: Oxygen SPA fails to render Data Apps when .app.yml contains non-ASCII (UTF-8) characters
severity: warning
affects:
  - apps/*.app.yml
since: 2026-05-14
status: active
---

# Oxygen SPA fails to render Data Apps when .app.yml contains non-ASCII characters

The Oxygen SPA (`oxy 0.5.47`, web app served at port 3000) fails to
render a Data App page when the `.app.yml` source contains non-ASCII
UTF-8 characters. The failure surfaces in browser console as:

```
InvalidCharacterError: Failed to execute 'atob' on 'Window':
The string to be decoded is not correctly encoded.
    at Ip (...assets/index-uGZkA66J.js:4:84489)
    at ...assets/index-uGZkA66J.js:156:60512 (Object.useMemo)
```

The `atob` (base64-decode) call site suggests the SPA is base64-
decoding something derived from the app config server-side; the
non-ASCII bytes appear to break the encode/decode pair somewhere in
that chain.

## Minimal reproduction

Any `.app.yml` field containing a non-ASCII character (em-dash `—`,
en-dash `–`, smart quotes, arrows like `↔` or `→`, bullets, etc.)
in either prose (markdown blocks, descriptions, titles) or comments
(`#` lines within SQL bodies) appears to trigger the failure. The
field doesn't have to be a markdown display block — Plan 11 had
non-ASCII in `description:`, SQL comment lines, and display titles.

Plan 11 (Session 41, 2026-05-14) found 15 non-ASCII characters in
`apps/rat_complaints_by_ward.app.yml`:

- 10× em-dash (`—`, U+2014)
- 1× en-dash (`–`, U+2013)
- 4× left-right arrow (`↔`, U+2194)

Total 45 UTF-8 bytes outside the ASCII range. Stripping all of them
to ASCII equivalents (`--`, `-`, `+` respectively) restored rendering.

## Expected behavior

`.app.yml` is YAML, which is UTF-8 by spec. Valid UTF-8 in any field
(prose or otherwise) should render. The SPA should base64-encode
UTF-8 bytes correctly (e.g., `btoa(unescape(encodeURIComponent(str)))`
or equivalent) and decode the same on the consumer side.

## Workaround

ASCII-ify all `.app.yml` content:

| Source character | Replacement |
|---|---|
| `—` (em dash, U+2014) | `--` |
| `–` (en dash, U+2013) | `-` |
| `"` `"` (smart double quotes, U+201C/U+201D) | `"` |
| `'` `'` (smart single quotes, U+2018/U+2019) | `'` |
| `•` (bullet, U+2022) | `*` or `-` |
| `→` (right arrow, U+2192) | `->` |
| `↔` (left-right arrow, U+2194) | `+` or `<->` |
| ...any other non-ASCII | ASCII equivalent |

Pre-commit grep guard:

```bash
grep -nP "[\x80-\xff]" apps/*.app.yml
```

Returns non-empty if any non-ASCII byte is present.

## Customer-feedback for Oxy

Third Oxygen SPA bug surfaced in this project's customer-shaped use,
alongside:

- [`plan-11-builder-cli-token-budget-hang`](plan-11-builder-cli-token-budget-hang.md)
  (CLI state-machine doesn't resume on "Continue with double budget"
  answer)
- The default trust-signal behavior gap (Builder Agent should
  default-include trust signals on `.app.yml` proposals, not require
  explicit prompting — see
  [`docs/transcripts/plan-11-rat-complaints-builder-session.md`](../transcripts/plan-11-rat-complaints-builder-session.md))

All three are bundled in the project's "customer-shaped use surfaces
customer-shaped feedback" loop ([MVP 1 retrospective](../retrospective/mvp1-lessons-learned.md)),
ready to file as a single Oxy-side ticket.

## Resolution path

Oxy-side fix to the SPA's base64 encoding step. Until then, the
ASCII-only workaround is documented + can be enforced via the
pre-commit grep guard above. No project-side blocker.
