# Plan 10 — BUILD.md §7 Opportunistic Principle

**Status:** scoped + executed in the same plan-close session.
**Type:** doc-only plan, no construction work.
**Plan slot:** Plan 10 — next available in the registry after Plan 9 rev 2.

## Why this plan exists

Two doc-level edits to [BUILD.md §7](../../BUILD.md#7-disciplines-that-hold-the-work-together)
emerged from the MVP 2 planning conversation in Chat (Session 31 + the
prior handoff that fed it):

1. The current §7 implicitly defaults to *configuration over custom code*
   and *deprecate custom scaffolding when Oxygen catches up*. The MVP 1
   retrospective made it clear that this framing has the polarity wrong:
   custom scaffolding earns its keep when it produces a better analyst
   experience than the available Oxygen primitive, and Oxygen primitives
   earn their place by producing a better analyst experience than the
   custom version. Analyst experience leads; tool choice follows.

2. The "Builder Agent as the construction interface" subsection currently
   reads as *default = Builder Agent, fallback = hand-writing YAML*. The
   stronger framing — given that Builder Agent's coverage of the
   workspace is still maturing and `--local`-mode reachability isn't yet
   pre-flight-verified — is *Builder Agent earns this role by producing a
   better experience than hand-writing YAML, and where it doesn't yet,
   hand-writing is a deliberate tool choice, revisited as Builder Agent
   matures.*

Both edits codify a single principle: **the opportunistic principle**.
Land them in §7 and the principle becomes operational discipline alongside
the existing §7 subsections.

## What this plan does NOT do

- Does not edit [MVP.md](../../MVP.md). The opportunistic principle is a
  §7 BUILD.md discipline — *how* the work is constructed. MVP.md frames
  *what* the project is for; that framing is unchanged.
- Does not edit [STACK.md](../../STACK.md). STACK.md describes what
  Builder Agent is; §7 governs when to reach for it. Two different
  layers.
- Does not start Plan 11 work. Plan 10 closes cleanly first.

## Phases

### Phase 1 — Pre-flight

Re-read BUILD.md §7 in current form. Confirm the edits will land in the
right anchor positions and no other §7 subsection contradicts the
principle as drafted. The current §7 contains six subsections:

1. Configuration over custom code
2. Builder Agent as the construction interface
3. Airlayer is the single semantic source of truth
4. Verification gates for live-functional claims
5. Component Trajectory reviews at every plan kickoff
6. The compass

Subsection 1 is the one that the opportunistic principle inverts in
emphasis — "configuration over custom code" remains true as a default,
but it is no longer the *governing* default. Analyst-experience-leads is
the governing default; configuration over custom code is the heuristic
that usually serves it.

That's a re-ordering of emphasis, not a contradiction. The opportunistic
principle subsection lands *above* "Configuration over custom code" so
the framing reads top-down: experience leads → configuration usually
follows.

Subsection 2 (Builder Agent) gets the in-place rewrite.

Subsections 3–6 are unaffected; they each describe a specific operational
discipline (single semantic source of truth, verification gates,
Component Trajectory reviews, the compass) that the opportunistic
principle *operates through* rather than competes with.

If pre-flight surfaces a §7 contradiction not anticipated above, pause
and flag before writing.

### Phase 2 — Write the edits

Two edits, both to BUILD.md §7.

**Edit 1: insert new subsection at top of §7.**

Title: *The opportunistic principle.* Goes above "Configuration over
custom code." Drafted text:

> Analyst experience leads. Oxygen tech gets reached for when it
> accelerates the analyst's path through the emotional arc, when it
> replaces custom scaffolding with something measurably better for the
> analyst, or when extending the portal directly would cost more than
> adopting the native primitive. The criterion is analyst delight, not
> platform adherence.
>
> This inverts the default that earlier framings of this section
> implied. Custom scaffolding is not tagged-for-replacement-when-the-platform-catches-up;
> it is tagged-for-replacement-when-the-replacement-is-better-for-the-analyst.
> The Component Trajectory review at every plan kickoff (below) is the
> moment that judgment gets made — explicitly, with the analyst's
> experience as the test, not configuration-over-custom-code as the
> default.
>
> Two corollaries follow:
>
> 1. **Pre-flight verification has teeth.** When a plan reaches for an
>    Oxygen primitive (Builder Agent, Data Apps, Verified Queries,
>    Routing Agent), pre-flight verifies the primitive produces the
>    analyst experience the plan assumes. If it doesn't, the plan stops,
>    the gap gets named, and the tool choice gets revisited — not pushed
>    through.
> 2. **Custom scaffolding earns its keep.** The portal, the answer
>    agent's custom trust contract, the limitations registry, the
>    auto-generated `/metrics` and `/trust` pages — these stay because
>    they produce the analyst experience the project commits to. When an
>    Oxygen primitive can produce that same experience better, the
>    migration is scoped. When it can't, custom stays.
>
> The other disciplines in this section (configuration over custom code,
> semantic-layer-as-single-source-of-truth, verification gates, Component
> Trajectory) operate in service of the opportunistic principle, not as
> competing defaults.

**Edit 2: replace the Builder Agent subsection body in place.**

Title stays *Builder Agent as the construction interface.* Body
replacement:

> From MVP 2 onward, Builder Agent is the intended construction
> interface for the analyst — the analyst describes what they want,
> Builder Agent reads, modifies, and iterates on the project files.
> Under the opportunistic principle, Builder Agent earns this role by
> producing a better analyst experience than hand-writing YAML. Where it
> does, it's used. Where it doesn't yet — in a particular mode, against
> a particular file shape, at a particular maturity — hand-writing is
> not fallback but a deliberate tool choice, revisited as Builder Agent
> matures.

### Phase 3 — Reconcile the §7 section opener

The current §7 section opener reads: *"The architectural decisions above
don't enforce themselves. A handful of disciplines run across the entire
build and keep it coherent."*

That opener is compatible with the new subsection at the top; no change
required.

If after writing Edit 1 the section reads as a list-of-disciplines
without a clear lead, consider light glue prose between the opener and
"The opportunistic principle." Default: no glue — let the new subsection
be the §7 lead.

### Phase 4 — Verify the rest of BUILD.md is internally consistent

The opportunistic principle reframes §7's defaults; check that the rest
of BUILD.md doesn't contradict the new framing.

- **§4 Component Trajectory.** Mentions custom-scaffolding-as-stopgap
  twice — once as the trigger framing ("Migration trigger") and once in
  the cross-cutting commitments ("Custom scaffolding exists where
  Oxygen doesn't yet, not because we prefer custom — when the platform
  catches up, we migrate"). Both are slightly off from the new framing:
  the *governing* test is analyst-experience-better, not
  platform-catches-up. The §4 cross-cutting paragraph in particular
  could read as a counter-statement. Reconcile: update §4 commitment #2
  to align with the new principle.
- **§5 four-MVP build sequence.** Mentions BUILD.md §7 disciplines
  abstractly in scaffolding-retired blocks. No content there contradicts
  the principle; no edit needed.
- **§7 itself.** Subsection 1 (Configuration over custom code) reads
  fine if it sits below the new top subsection — it functions as a
  heuristic that usually serves analyst experience. Subsection 5
  (Component Trajectory reviews at every plan kickoff) phrases custom
  scaffolding as having "an expiration date." Soften: scaffolding has
  an expiration date *when an Oxygen primitive can produce a better
  analyst experience*, not on a calendar.
- **Glossary.** Builder Agent entry says "The construction interface
  from MVP 2 onward." That phrasing aligns with the new Edit 2 framing
  (Builder Agent is the *intended* construction interface, earns its
  role). No glossary edit needed.

Reconciliation edits in §4 and §7 subsection 5 are in scope for Plan 10
because they are the same conceptual shift as the new top subsection.
Limit scope strictly to those touches; do not expand into rewrites.

### Phase 5 — STANDARDS check

BUILD.md edits are *static-artifact* claims per the verification-gates
discipline (CLAUDE.md "Verification gates for `[x]` ticks"). Sign-off
gate: the edits exist in the committed file, the Markdown renders,
internal links still resolve.

- Render check: open BUILD.md in a Markdown previewer (Code's call —
  GitHub's rendering or local `pandoc` is fine) or scroll the raw file
  to confirm section structure looks right.
- Link check: confirm internal anchors (`#4-component-trajectory`,
  `MVP.md`, `STANDARDS.md`, `CLAUDE.md`) still resolve. The opportunistic
  principle subsection references "the Component Trajectory review at
  every plan kickoff (below)" — make sure the §4-§7 ordering is
  preserved.
- No live-functional verification needed.

### Phase 6 — LOG.md + TASKS.md updates

- LOG.md Plans Registry — add Plan 10 row, status `done`, closed in
  Session 33.
- LOG.md Active Decisions — add a row dated 2026-05-13 ET for
  "BUILD.md §7 opportunistic principle landed."
- LOG.md Recent Sessions — add Session 33 entry. Rotate oldest from the
  block if it now exceeds 5 entries (it will — Session 28 rotates to
  Earlier).
- LOG.md "Last Updated" line bumped to 2026-05-13.
- TASKS.md "Next Focus" — points at Plan 11 (scoping document, not yet
  executed).

### Phase 7 — Sign-off and commit

Single commit covering: `BUILD.md` edits, `docs/plans/plan-10-...md`,
LOG.md, TASKS.md, session file. Commit message names Plan 10 explicitly.
Push.

## Sign-off gates

Static-artifact only:

- [ ] BUILD.md §7 contains the new "The opportunistic principle"
  subsection at the top, above "Configuration over custom code"
- [ ] BUILD.md §7 "Builder Agent as the construction interface"
  subsection body replaced with the drafted text
- [ ] BUILD.md §4 cross-cutting commitment #2 reconciled with the new
  framing
- [ ] BUILD.md §7 "Component Trajectory reviews at every plan kickoff"
  subsection softened where it talks about expiration dates
- [ ] Internal Markdown links still resolve
- [ ] LOG.md Plans Registry row for Plan 10 = `done`
- [ ] LOG.md Active Decisions row for the opportunistic principle
- [ ] TASKS.md "Next Focus" pointing at Plan 11
- [ ] Session file at `docs/sessions/session-33-2026-05-13-plan-10-opportunistic-principle.md`
- [ ] Single commit pushed to remote

## Out of scope

- Changes to MVP.md, STACK.md, or the retrospective doc
- Code or pipeline changes
- Plan 11 work — comes in its own session
