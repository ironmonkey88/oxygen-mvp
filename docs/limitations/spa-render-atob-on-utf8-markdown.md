---
id: spa-render-atob-on-utf8-workspace
title: Oxygen SPA fails to render when ANY workspace file contains non-ASCII (UTF-8) characters
severity: warning
affects:
  - apps/*.app.yml
  - agents/*.agent.yml
  - semantics/views/*.view.yml
  - semantics/topics/*.topic.yml
  - dbt/models/**/*.sql
  - dbt/models/**/schema.yml
  - dbt/tests/**/*.sql
  - docs/limitations/_index.yaml
since: 2026-05-14
status: active
---

# Oxygen SPA fails to render when ANY workspace file contains non-ASCII characters

The Oxygen SPA (`oxy 0.5.47`, web app served at port 3000) fails to
render when **any** workspace file the SPA loads contains non-ASCII
UTF-8 characters — not just `.app.yml` files. Originally surfaced
as an `.app.yml`-only issue in Plan 11 Session 41; a follow-up
recurrence (Session 42, on the same /apps/rat_complaints_by_ward
click-through after the Session 41 fix) showed the SPA also chokes
on em-dashes in semantic-layer view YAMLs, the answer-agent prompt,
dbt model SQL comments, dbt `schema.yml` descriptions, dbt singular
tests, and the limitations index. 128 non-ASCII chars across 22
project files all had to be stripped.

The failure surfaces in browser console as:

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

Any workspace file the SPA loads — `.app.yml`, `.agent.yml`,
`.view.yml`, `.topic.yml`, dbt model SQL, dbt `schema.yml`, dbt
singular tests, `docs/limitations/_index.yaml` — containing any
non-ASCII character (em-dash `—`, en-dash `–`, smart quotes, arrows
like `↔` or `→`, bullets, section sign `§`, ellipsis `…`, etc.) in
any field (prose, comments, descriptions, titles) appears to trigger
the failure.

**Plan 11 Session 41 (initial)** found 15 non-ASCII chars in
`apps/rat_complaints_by_ward.app.yml` and stripped them — rendering
returned for direct `.app.yml`-only loads, but the click-through
from the portal's `/dashboards` listing to the SPA still failed
because the SPA also loads the workspace context (semantic views,
agent yaml, dbt models) when rendering an app.

**Session 42 (broader fix)** scanned all SPA-readable workspace files
and found 128 non-ASCII chars across 22 files:

| File family | Files | Non-ASCII chars |
|---|---|---|
| `apps/*.app.yml` | 1 | 15 (Session 41) |
| `agents/*.agent.yml` | 1 | 8 |
| `semantics/views/*.view.yml` | 6 | 11 |
| `dbt/models/*/*.sql` | 9 | 17 |
| `dbt/models/*/schema.yml` | 3 | 83 |
| `dbt/tests/singular/*.sql` | 1 | 2 |
| `docs/limitations/_index.yaml` | 1 | 5 |

All swept to ASCII equivalents (`--`, `-`, `+`, `->`, `...`, `sect.`,
straight quotes) via a single script. Rendering returned for the
click-through path post-sweep.

## Expected behavior

`.app.yml` is YAML, which is UTF-8 by spec. Valid UTF-8 in any field
(prose or otherwise) should render. The SPA should base64-encode
UTF-8 bytes correctly (e.g., `btoa(unescape(encodeURIComponent(str)))`
or equivalent) and decode the same on the consumer side.

## Workaround

ASCII-ify **all SPA-readable workspace files**, not just `.app.yml`:

| Source character | Replacement |
|---|---|
| `—` (em dash, U+2014) | `--` |
| `–` (en dash, U+2013) | `-` |
| `"` `"` (smart double quotes, U+201C/U+201D) | `"` |
| `'` `'` (smart single quotes, U+2018/U+2019) | `'` |
| `•` (bullet, U+2022) | `*` or `-` |
| `→` (right arrow, U+2192) | `->` |
| `↔` (left-right arrow, U+2194) | `+` or `<->` |
| `…` (ellipsis, U+2026) | `...` |
| `§` (section sign, U+00A7) | `sect.` |
| ...any other non-ASCII | ASCII equivalent |

Pre-commit grep guard covering all SPA-readable surfaces:

```bash
grep -lnPr "[\x80-\xff]" \
  apps/ \
  agents/ \
  semantics/ \
  dbt/models/ \
  dbt/tests/ \
  docs/limitations/_index.yaml \
  config.yml \
  2>/dev/null
```

Returns non-empty if any non-ASCII byte is present in any
SPA-readable file. A pre-commit hook should fail the commit when
this command produces output.

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
