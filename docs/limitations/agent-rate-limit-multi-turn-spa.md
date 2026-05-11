---
id: agent-rate-limit-multi-turn-spa
title: SPA multi-turn conversations may hit Anthropic 30K input tokens/min cap
severity: medium
affects:
  - spa-chat
  - multi-turn-conversations
since: 2026-05-11
status: known
---

# SPA multi-turn conversations may hit Anthropic 30K input tokens/min cap

The SPA accumulates conversation context across turns. After 3–5 turns of dense queries (each carrying a result table, surfaced limitations, citations, and the agent's reply prose), per-turn context approaches the 30,000 input-tokens-per-minute Anthropic API rate limit on `claude-sonnet-4-6`. When hit, the agent returns a `rate_limit_error` and the user sees a red `ApiError` in the chat.

## Impact

- Multi-turn analyst sessions in the SPA can stall mid-investigation, breaking the **momentum** phase of the emotional arc MVP.md commits to protecting.
- The error message in the SPA is API-shaped, not analyst-shaped — the user sees raw `ApiError(...)` text rather than a graceful "wait a moment" hint.
- The CLI path (`oxy run agents/...`) is one-shot per call and does not accumulate context across calls, so this limitation does not apply there.

## Workaround

Any one of these unblocks the analyst:

- **Wait ~60 seconds.** The 30K/min cap is rolling; new tokens free up as the window slides.
- **Start a fresh chat thread.** The new thread resets accumulated context to zero.
- **Request a tier-2 rate-limit increase from Anthropic.** Tier 2 raises the cap to 80,000 input tokens/min — substantially more headroom for multi-turn dense queries.

Encountered empirically 2026-05-10 (Session 24) during Q4+Q5 bench reruns. CLI hit it under parallel-batch load; SPA expected to hit it under normal multi-turn use given how much each turn carries (semantic-layer context + view files + limitations index + the running conversation).

## Resolution path

Three options, in increasing order of effort:

- (a) Tier-2 rate-limit increase from Anthropic — operational, no code change.
- (b) Prompt-side trimming — reduce per-turn context by pruning older turns or summarizing the conversation tail. Requires understanding what Oxygen's runtime considers part of "context" for each agent call.
- (c) Token-budget awareness in the agent prompt — have the agent self-monitor and pre-emptively trim or compress when approaching the cap. Speculative; depends on Oxygen runtime support for token introspection mid-conversation.

None planned for MVP 1. The limitation is documented so future analyst sessions know what they're seeing when it fires. Status is `known` (registry directory present, but does NOT auto-surface on queries via the agent's affects-match — this is environmental, not query-shape-driven).
