---
id: spa-no-deeplink-prepopulation
title: Oxygen SPA does not support URL-based question prepopulation
severity: low
affects:
  - portal
  - spa-chat
since: 2026-05-14
status: active
---

# Oxygen SPA does not support URL-based question prepopulation

The portal's "Try a question" section (homepage section 03) presents
question cards that should drop the user into `/chat` with the question
already in the input. The Oxygen SPA bundle at
`http://localhost:3000/assets/index-*.js` was inspected; it reads URL
params for `code`, `error`, `token`, `run_id`, etc., but none of `q`,
`message`, `prompt`, `question`, or any other key that would prefill
the chat input. There is no documented deep-link surface for
prepopulating a thread.

## Workaround

The portal copies the question text to the clipboard via
`navigator.clipboard.writeText()` before navigating to `/chat`, and
shows a brief toast ("Question copied — paste it in the chat"). The
analyst pastes (`⌘V` / `Ctrl+V`) once the chat input is focused. See
`portal/index.html` — the inline `<script>` at the bottom of the
section-03 block, and the `#copy-toast` element.

This is a UX workaround, not a functional fix. The originally desired
flow is "click question → chat runs it." We are at "click question →
clipboard primed → user pastes → user presses Enter."

## Resolution path

Revisit when Oxygen ships a deep-link surface for chat threads — e.g.,
`/chat?q=...` or a documented thread-creation endpoint that accepts an
initial message. Until then the clipboard workaround stands.

This limitation is environmental, not query-shape-driven — it does not
auto-surface on agent answers via `affects:` matching.
