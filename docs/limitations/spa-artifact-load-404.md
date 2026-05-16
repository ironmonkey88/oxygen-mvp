---
id: spa-artifact-load-404
title: Oxygen SPA "Unable to load the selected artifact" — backend returns 404 on artifact retrieval
severity: warning
affects:
  - chat
  - answer_agent
since: 2026-05-16
status: active
---

# SPA artifact viewer can't load `execute_sql` artifacts

## The finding

Probed 2026-05-16 in nginx access logs: after the Answer Agent runs
`execute_sql` and returns a successful response ("Returned N rows."),
the SPA's right-pane artifact viewer fetches the artifact from:

```
GET /api/00000000-0000-0000-0000-000000000000/artifacts/<artifact-uuid>?branch=
```

This request returns **HTTP 404** from the Oxy backend (proxied
through nginx without modification). nginx routing is correct —
other endpoints with the same `/api/00000000-.../` prefix (threads,
agents, thread-message-POST) return 200 cleanly. Only the
`/artifacts/<id>` endpoint 404s.

The SPA retries the request several times (observed 9+ retries in ~20
seconds in one log sample) and then displays "Unable to load the
selected artifact. Please check your connection or try again later."
with a Retry button. The agent's text response, citations, and
limitations are still visible in the conversation pane — the trust
contract partially works — but the analyst can't see the actual SQL
query or result table.

## Consequence for the analyst

- The chat agent's textual answer is unaffected: "Ward 6 had the most
  traffic citations in 2025 with 1,940 citations" still displays
  correctly.
- The SQL artifact (the actual `SELECT ward, COUNT(*) FROM …`
  statement) is not visible in the SPA's right pane.
- Citations and limitations still surface — those don't depend on
  the artifact endpoint.
- The user gets the answer but can't audit the query.

## Workaround

- Use `oxy run agents/answer_agent.agent.yml "<question>"` from the
  CLI (e.g. via Tailnet SSH or local clone). The CLI prints the full
  SQL, results table, and trust contract inline — no separate
  artifact endpoint involved.
- Both Plan 23 cumulative-verification chat agent test questions
  succeeded this way in Session 50 (`/docs/sessions/
  session-50-2026-05-16-plan-23-cumulative-verification.md`).

## What we know about the root cause

- The artifact UUID in the failing request matches what `execute_sql`
  emitted (verified by reading the agent's response markdown — the
  artifact reference is in the response, the SPA picks up the UUID,
  but retrieval 404s).
- The same `/api/00000000-.../threads/<id>` endpoint returns 200 —
  the prefix is routed correctly.
- The workspace UUID `00000000-0000-0000-0000-000000000000` is a
  zero-UUID placeholder consistent with `oxy start --local`
  single-workspace mode.
- This is the second Oxy-backend bug surfaced through end-to-end
  testing this week (the first was the `df-interchange` Rust panic
  on no-match WHERE; see Session 50 narrative).

## Resolution path

Upstream — file as Oxy customer feedback. Likely candidates for the
backend bug:

- Artifact persistence layer not writing/reading from the workspace-
  zero-UUID directory consistently.
- Artifacts stored in-memory but the SPA fetches via a different
  in-memory pool than the agent wrote to.
- A version mismatch between the bundled SPA's artifact-fetch URL
  pattern and the backend's route handler.

Not blocking MVP 2 — the analyst-facing answer text is intact. Worth
fixing for MVP 3 (Verified Queries depend on artifact retrieval
being reliable).
