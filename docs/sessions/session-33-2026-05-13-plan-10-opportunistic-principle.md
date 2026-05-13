---
session: 33
date: 2026-05-13
start_time: 00:45 ET
end_time: 01:05 ET
type: code
plan: plan-10
layers: [docs]
work: [docs]
status: complete
---

## Goal

Execute Plan 10 — encode the opportunistic principle as the lead
subsection of [BUILD.md §7](../../BUILD.md#7-disciplines-that-hold-the-work-together)
and rewrite the "Builder Agent as the construction interface"
subsection to match. Reconcile the two BUILD.md spots that contradicted
the new framing (§4 cross-cutting commitment #2, §7 Component
Trajectory reviews subsection).

## What shipped

- [`docs/plans/plan-10-buildmd-7-opportunistic-principle.md`](../plans/plan-10-buildmd-7-opportunistic-principle.md)
  — plan-file capturing why, what, phases, sign-off gates, out-of-scope.
- [`BUILD.md`](../../BUILD.md) §7 — new "The opportunistic principle"
  subsection inserted at the top of §7, above "Configuration over custom
  code." Names analyst experience as the lead criterion; lists two
  corollaries (pre-flight verification has teeth; custom scaffolding
  earns its keep); names the other §7 disciplines as operating in
  service of the principle, not as competing defaults.
- [`BUILD.md`](../../BUILD.md) §7 — "Builder Agent as the construction
  interface" subsection body replaced. Framing flipped from
  *default = Builder Agent, fallback = hand-writing YAML* to *Builder
  Agent earns the role by producing a better analyst experience; where
  it doesn't yet, hand-writing is a deliberate tool choice, revisited
  as Builder Agent matures.*
- [`BUILD.md`](../../BUILD.md) §4 commitment #2 ("Willingness to
  deprecate") — reconciled: scaffolding stays where it produces a
  better analyst experience; "platform-adherence is not a reason to
  deprecate one before its replacement is actually better."
- [`BUILD.md`](../../BUILD.md) §7 "Component Trajectory reviews at
  every plan kickoff" — softened: scaffolding has an expiration date
  when its replacement is actually better; "configuration over custom
  code" is the heuristic that usually serves analyst experience, not a
  rule that overrides it.
- LOG.md — Plans Registry row added for Plan 10 (`done`); Active
  Decisions row for the opportunistic principle; Recent Sessions block
  rotated; Last Updated bumped.
- TASKS.md — Plans Registry won't move; "Next Focus" rewritten to
  point at Plan 11 scoping (not Plan 11 execution — that comes after
  Gordon's review).

## Decisions

- **Opportunistic principle as the lead §7 subsection.** Goes above
  "Configuration over custom code." Configuration-over-custom-code
  remains true as a default heuristic but no longer as the governing
  default — analyst experience is. Names the rest of §7 (semantic-layer
  single source of truth, verification gates, Component Trajectory)
  as operating in service of the principle.
- **Builder Agent subsection rewrite is in-place, same title.** The
  title still names Builder Agent as the construction interface; the
  body explains *how* — by producing a better analyst experience, not
  by default fiat.
- **§4 and §7 subsection 5 reconciled inside Plan 10 scope.** Both
  spots phrased custom scaffolding as having an expiration date
  triggered by platform-catches-up; the opportunistic principle
  re-roots both triggers in analyst-experience-better. Limit scope
  strictly to those two touches; do not expand into a §4 rewrite.

## Next action

Plan 11 scoping document (first Data App via Builder Agent — rat
complaints by ward). Scoping only; execution pending Gordon's review.
