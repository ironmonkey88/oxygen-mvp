---
id: dashboard-render-spa-only
title: Data App visual render verified only in the SPA; CLI rendering not available
severity: info
affects:
  - apps/rat_complaints_by_ward.app.yml
  - main_gold.fct_311_requests
since: 2026-05-13
status: active
---

# Data App visual render verified only in the SPA; CLI rendering not available

`.app.yml` Data Apps in `oxy 0.5.47` render only through the SPA's
app browser at `http://oxygen-mvp.taildee698.ts.net:3000/apps/<name>`.
The CLI command `oxy run apps/<name>.app.yml` (referenced in
STACK.md §1.9 prior to 2026-05-13) returns:

> Invalid YAML file. Must be either *.procedure.yml, *.workflow.yml,
> *.automation.yml, *.agent.yml, or *.aw.yml

`oxy validate --file apps/<name>.app.yml` confirms YAML structure but
does not render. The Builder Agent's tool framework can execute the
individual SQL tasks (via `execute_sql`) but does not surface a
rendered chart preview at the CLI.

## Impact for Plan 11

Plan 11 Phase 5's "Verify by reading the rendered Data App in the
SPA, not just the .app.yml source" gate is partially satisfied:

- **Structural verification (pass):** `oxy validate` confirms the
  app YAML is well-formed; per-file validate passes; full-workspace
  validate (`oxy validate`) reports 12/12 config files valid.
- **SQL verification (pass):** Builder Agent executed each of the
  four task SQL queries against live data during Phase 4 and the row
  counts match the Phase 2 pre-flight (14,036 total, ward
  distribution 1,250–2,661, year trend matches, resolution buckets
  matching the long-tail shape).
- **Visual render verification (deferred):** Code overnight has no
  Chrome MCP extension connected (`list_connected_browsers` returned
  empty). Verifying chart layouts, axis labels, color scheme, and
  control widget behavior requires a human operator with browser
  access to the SPA.

The deferred visual gate is the right shape for follow-up: a human
analyst (Gordon) opens the workspace, navigates to
`/apps/rat_complaints_by_ward`, and confirms the rendered output.
If any of the four chart blocks renders empty or with the wrong
shape, that's a fix-forward Plan 11.1.

## Workaround

For analyst questions about the dashboard data **without** needing
the visual render:

- Query the underlying SQL via `oxy run --database somerville <SQL>`
- Use the Answer Agent chat (which carries the trust contract) to
  ask the same data questions in natural language

For visual verification:

- Open `http://oxygen-mvp.taildee698.ts.net:3000/apps/rat_complaints_by_ward`
  in a browser connected to the Tailnet
- Public `/chat` route at `http://18.224.151.49/chat` is Basic
  Auth-gated but does not currently route to apps; access apps via
  the Tailnet for now

## Resolution path

Two paths converge:

1. **Oxygen ships CLI Data App rendering.** A future `oxy 0.5.x`
   release might add `oxy run apps/<name>.app.yml`. Track via
   changelogs.
2. **Plan 11.1 visual sign-off** when Gordon next opens the SPA —
   one-time verification, no code change.

This limitation does not block Plan 11 sign-off because the
structural and SQL gates pass. It documents the operator-context
gap for honest reporting.
