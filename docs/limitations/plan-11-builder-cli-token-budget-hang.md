---
id: plan-11-builder-cli-token-budget-hang
title: Builder Agent CLI hangs after answering "Continue with double budget"
severity: info
affects:
  - oxy agentic run --domain builder
since: 2026-05-13
status: active
---

# Builder Agent CLI hangs after answering "Continue with double budget"

Plan 11 Phase 4 surfaced a behavior in `oxy 0.5.47`: when Builder
Agent's run hits its token budget (default 4096) mid-generation and
suspends with an `awaiting_input` event asking *"The builder ran out
of token budget (4096 tokens). Continue with double the budget (8192
tokens)?"*, submitting the suggested answer via `oxy agentic answer
--answer "Continue with double budget" <RUN_ID>` returns success
("Answer submitted for run ...") but the run does not advance.
`oxy agentic events --after-seq <last>` returns 0 new events;
`oxy agentic inspect` reports `status: running` indefinitely;
`oxy agentic list` shows the run as `running`. The original
`oxy agentic run` process keeps holding a connection.

Verified end-to-end on 2026-05-13: run `197bbc81-5fb0-49c6-a65e-e4a9ba88650a`
suspended at seq 53, answer accepted at 22:42:56 UTC, no further
events through 23:30 UTC. `oxy agentic cancel` cleared the run.

## What works

The pre-suspend portion of the Builder run works perfectly:

- `read_file`, `search_files`, `execute_sql` tools all execute
- Multiple SQL verifications run against real data; results match
  ground-truth pre-flight queries exactly
- `propose_change` with `awaiting_input` + Accept/Reject via
  `oxy agentic answer` works for the standard HITL approval flow
  (verified in Plan 11 Phase 1 G4)

The hang is specific to the **token-budget-continuation** sub-state,
not to the general suspend/resume mechanism.

## Workaround

For Plan 11, the response was to:

1. Cancel the hung run via `oxy agentic cancel <RUN_ID>`
2. Use the verified queries Builder produced (visible in the JSONL
   output before the suspend) to hand-write the `.app.yml` file
3. Document the gap as a customer-feedback finding for Oxy

For future Builder Agent CLI use:

- Pre-budget for the expected output size by structuring questions
  so the file content stays under 4K tokens (this is hard for
  multi-task `.app.yml` files in practice)
- Avoid asking Builder to write large files in a single turn; ask
  for the skeleton, accept it, then ask for incremental additions
- Prefer the SPA's Build mode for large file authoring until this
  CLI behavior is fixed

## Resolution path

This is an Oxy customer-feedback finding. The CLI's
`agentic answer` for the token-budget suggestion accepts the answer
into state but doesn't trigger run-state-machine resume. Reported
to Oxy via the project's "customer-shaped use surfaces
customer-shaped feedback" loop. No project-side resolution needed
until Oxy ships a fix; track via Oxygen changelogs.
