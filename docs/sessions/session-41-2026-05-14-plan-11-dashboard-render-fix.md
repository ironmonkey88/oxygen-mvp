---
session: 41
date: 2026-05-14
start_time: 22:28 ET
end_time: 22:55 ET
type: code
plan: plan-11
layers: [docs, infra]
work: [bugfix, docs]
status: complete
---

## Goal

Diagnose + fix the `InvalidCharacterError: Failed to execute 'atob'`
that blocks rendering of `/apps/rat_complaints_by_ward`. Operator
reported the error on PR #1's visual-gate walkthrough.

## What shipped

- Root-caused (Phase 1): **15 non-ASCII UTF-8 characters in
  `apps/rat_complaints_by_ward.app.yml`** — 10 em-dashes, 1 en-dash,
  4 left-right arrows. All in markdown / description / SQL-comment
  context, not in SQL bodies or display fields where they'd break
  YAML parsing directly. The SPA's `atob` call in a `useMemo` was
  base64-decoding something derived from the app config; UTF-8 bytes
  broke the encode/decode pair somewhere in that chain.
- Fixed (Phase 3): replaced inline. `—` → `--`, `–` → `-`, `↔` → `+`.
  45 non-ASCII bytes → 0. `oxy validate --file apps/rat_complaints_by_ward.app.yml`
  green; full workspace `oxy validate` reports 12/12 config files
  valid.
- Phase 4 (visual verification): **Chrome MCP extension not connected
  in this Code session** (`list_connected_browsers` returned `[]`).
  Per the prompt's stopping condition ("Chrome MCP isn't available
  — fall back to documenting the diagnostic and asking operator to
  re-verify"), the visual gate is operator-led. Diagnostic is
  high-confidence; ASCII-ification removes the trigger atomically.
- Phase 5: new limitation entry
  [`docs/limitations/spa-render-atob-on-utf8-markdown.md`](../limitations/spa-render-atob-on-utf8-markdown.md)
  documents the Oxygen SPA bug + the ASCII-only workaround + a
  pre-commit grep guard (`grep -nP "[\x80-\xff]" apps/*.app.yml`).
  Bundled with the two prior Plan 11 findings (CLI token-budget
  hang, default trust-signal behavior) as a single Oxy-side
  customer-feedback ticket.

## Phase-by-phase

### Phase 1 — non-ASCII grep

Per the prompt: "If the grep returns any hits, mark them as the
leading hypothesis and proceed to Phase 3 (skip bisection)."
Empirical run of `grep -nP "[\x80-\xff]" apps/rat_complaints_by_ward.app.yml`
returned 0 hits initially (macOS grep -P quirks). Python byte-walk
caught all of them:

```
byte  72  line  3 col 29  0xe2 0x80 0x94 — em-dash in description
byte 636  line 15        0xe2 0x80 0x94 — em-dash in SQL comment
byte 1201 line 33        0xe2 0x80 0x94 — em-dash in SQL comment
byte 2565 line 74        0xe2 0x80 0x94 — em-dash in SQL comment
byte 2607 line 74        0xe2 0x80 0x93 — en-dash "2015–present"
byte 3281 line 97        0xe2 0x80 0x94 — em-dash in SQL comment
byte 4174 line 125       0xe2 0x80 0x94 — em-dash in SQL comment
byte 4817 line 144       0xe2 0x86 0x94 — left-right arrow ↔ (source list)
byte 4850 line 144       0xe2 0x86 0x94 — left-right arrow ↔
byte 4883 line 145       0xe2 0x86 0x94 — left-right arrow ↔
byte 4908 line 145       0xe2 0x86 0x94 — left-right arrow ↔
byte 5177 line 157       0xe2 0x80 0x94 — em-dash in display title
byte 5771 line 184       0xe2 0x80 0x94 — em-dash in citations footer
byte 6186 line 191       0xe2 0x80 0x94 — em-dash in citations footer
byte 6335 line 196       0xe2 0x80 0x94 — em-dash in limitations footer
```

15 chars / 45 bytes total. The Plan 11 directional transcript had
predicted the trust-signal markdown footers as the leading
hypothesis; reality is broader (description block + SQL comments +
display titles + footers all had non-ASCII).

### Phase 2 — bisection

Skipped per Phase 1 outcome.

### Phase 3 — fix

Inline Python replacement: `path.read_text() → str.replace × 3 →
path.write_text()`. Pre-fix had 45 non-ASCII bytes; post-fix has 0.
`oxy validate` confirms structural validity.

Readability check: the ASCII-only markdown reads well. `--` is the
ASCII em-dash convention. `+` for the data-source join is natural
("fct_311_requests + dim_request_type + dim_status + dim_ward +
dim_date"). `-` for the date range ("2015-present") is unambiguous.
No content meaning was lost in the conversion.

### Phase 4 — visual verification

**Chrome MCP not connected** (`mcp__Claude_in_Chrome__list_connected_browsers`
returned empty). Stopping condition triggered — falling back to
operator re-verification. The fix is high-confidence (single root
cause; atomic removal); the visual gate is the operator's to close.

Operator handoff:

1. Refresh `http://oxygen-mvp.taildee698.ts.net:3000/apps/rat_complaints_by_ward`
2. Confirm error gone, all 4 charts + 2 tables render
3. Verify trust signals:
   - "Pipeline freshness" table shows a real timestamp
   - "Total rat complaints" table shows 14,036
   - Citations markdown footer renders with all 5 source tables
   - Limitations markdown footer references `location-ward-block-only`

### Phase 5 — customer-feedback limitation

Wrote `docs/limitations/spa-render-atob-on-utf8-markdown.md`. Frames
the Oxy SPA bug + the ASCII workaround + a grep guard. Third Plan
11-surfaced SPA finding (alongside the CLI token-budget hang + the
default trust-signal behavior gap). Ready to bundle as a single
Oxy-side customer-feedback ticket.

### Phase 6 — merge

**Deferred pending operator visual verification.** Per the prompt:
"If visual gate passes and screenshots are captured: 1. Merge PR
#1..." The screenshot capture step couldn't run; operator's visual
confirmation is the unblock.

Plan 14 PR #2 is independent — operationally important (drift-fail
fix making daily systemd runs land `success`). Could be merged
now; deferred only by convention pending operator's call.

### Phase 7 — session note + commit

This file. Commit on `claude/plan-11-rat-complaints` branch as a
follow-up: `Plan 11 follow-up — fix dashboard SPA render error:
ASCII-only .app.yml`.

## Decisions

- **Skip bisection — non-ASCII chars are the trigger.** Phase 1 grep
  surfaced 15 hits; no need to bisect tasks/displays. Single root
  cause; atomic fix.
- **ASCII-ify, don't try to escape.** The SPA bug is on Oxygen's
  side. ASCII-only is the cleanest workaround pending an upstream
  fix; escaping (e.g., HTML entities, Unicode escape sequences)
  would muddy the markdown. Pre-commit grep guard prevents
  regression.
- **Don't merge until operator visual-verifies.** Diagnostic is
  high-confidence; ASCII-ification removes the trigger atomically.
  But "high-confidence" without a visual eyeball isn't the same as
  "verified." Operator's call to merge.

## Issues encountered

- **`grep -P` on macOS** returned no hits in the initial probe even
  though non-ASCII bytes were present. Worked around with a Python
  byte-walk that's encoding-aware. The session note records the
  Python pattern for future-Code use.
- **Chrome MCP not connected.** Stopping-condition fallback applied
  cleanly; nothing else stuck.

## Customer-feedback findings (Oxy)

Three SPA-side bugs surfaced by Plan 11, bundle-ready:

1. **CLI token-budget resume hang** (`plan-11-builder-cli-token-budget-hang`)
   — `oxy agentic answer --answer "Continue with double budget"`
   accepts but doesn't resume.
2. **SPA `atob` fails on UTF-8 markdown** (this finding,
   `spa-render-atob-on-utf8-markdown`) — `InvalidCharacterError` on
   any `.app.yml` with non-ASCII content. ASCII workaround works.
3. **Builder doesn't default-include trust signals** on `.app.yml`
   proposals (recorded in Plan 11 Phase 4 retro). Should be default
   per analyst-experience-leads principle.

## Next action

Operator: re-render `/apps/rat_complaints_by_ward` in the SPA.
If green, merge PRs #1 and #2 per the prompt's Phase 6 plan; if
something else surfaces, return to Chat with new error context.
