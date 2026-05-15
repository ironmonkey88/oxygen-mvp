# PROMPTS.md -- Chat-to-Code prompt standard

The shape every prompt Chat hands to Code takes, and the workflow Code
runs when it receives one. Companion to [CLAUDE.md](CLAUDE.md)
(operating instructions), [STANDARDS.md](STANDARDS.md) ("done done"
gates), and [DASHBOARDS.md](DASHBOARDS.md) (dashboard design).

---

## 1. Why this exists

Chat (Claude.ai) and Code (Claude Code) communicate through Markdown
prompts Gordon pastes from one thread into the other. The artifact is
the contract. If the artifact is well-shaped, the work is durable:
Chat's intent survives a session crash, Code's response is consistent
across executions, and a third reader (a future Chat session, a future
Code session, Gordon himself in a week) can pick the work back up
without reconstructing context from memory.

Two failure modes this standard prevents:

- **Underspecified intent.** A coding prompt that names a change without
  naming the business outcome forces Code to guess at scope. Guesses
  produce drift.
- **Inconsistent receipt.** Code's behavior on receiving a prompt has
  varied -- sometimes deep pre-flight, sometimes immediate execution,
  sometimes asking clarifying questions, sometimes not. A defined
  workflow on receipt closes that gap.

---

## 2. Two kinds of prompts

Every prompt Chat writes is one of two kinds. The kind is declared in
the prompt's header -- Code's receipt workflow branches on it.

### 2.1 Coding request

A prompt that asks Code to change the system -- write code, edit config,
run migrations, modify the warehouse, deploy. Anything that produces a
commit.

A coding request is wrapped in a business purpose. Code never receives
a bare technical instruction; it receives an outcome statement that
names what the change is for, then the technical scope that delivers
that outcome. The shape is borrowed from user stories without the
ceremony.

### 2.2 Information request

A prompt that asks Code to investigate the system -- read files, query
the warehouse, check live state, verify a claim, audit a condition. The
output is a written finding, not a commit.

An information request is wrapped in a question. Code never receives a
bare "tell me about X"; it receives the question that needs answering
and the decision the answer will inform.

---

## 3. The coding-request shape

Every coding prompt has these sections, in order. Sections marked
**(required)** are non-negotiable; **(conditional)** apply when relevant.

```
# Prompt -- <short imperative title>

**Kind:** coding
**Date:** YYYY-MM-DD
**Scope:** <files / directories / tables Code will touch>
**Effort:** <rough estimate -- minutes, hours, sessions>
**Depends on:** <prerequisite PRs or prompts, or "none">

---

## Outcome (required)

One paragraph answering: who benefits, and what changes for them. The
business or analyst purpose this work serves. Written in plain language
-- no SQL, no file paths, no Oxygen jargon. If Code couldn't restate
this paragraph to a non-technical reader, the outcome isn't yet clear.

Example:
> "An analyst landing on the /trust page can see whether the platform
> has been reliably refreshing -- not just whether today's run passed,
> but whether the last 30 runs passed. The new section is the
> at-a-glance answer to 'should I trust this data right now.'"

## Context (conditional)

State Code needs to know that isn't in the repo. Recent decisions,
findings from earlier sessions, screenshots, observed bugs. Omit if not
needed.

## Work (required)

The technical scope, broken into discrete items. Each item names what
changes, where, and why. Code references the Outcome to scope each
item -- anything that doesn't serve the Outcome is out of scope.

Items can be sequential phases (Phase A -> Phase B -> Phase C) when the
work has clear staging, or a flat list when it doesn't.

## Verification (required)

The conditions under which the work is complete. Distinguish
**static-artifact** verification (the file exists, the config is
committed, the schema.yml has the entry) from **live-functional**
verification (the page renders, the test passes, the chat agent answers
the question) -- the same distinction CLAUDE.md's `[x]` evidence rule
uses.

If a live-functional gate can't be checked in the session (Chrome MCP
not connected, EC2 unreachable), say so and document the diagnostic the
next session should run.

## Halt conditions (conditional)

When Code should stop and surface rather than barrel ahead. Examples:
"if the pre-flight finds the dataset has no usable grain, stop"; "if
the spatial join produces <95% ward coverage, stop and surface the
count." If no halt conditions are realistic, omit.

## Out of scope (conditional)

What Code does NOT do, even if natural-looking. Use this when the
Outcome could plausibly justify more work than intended. Bound the
blast radius.

## Commit shape (required)

How the work lands in git. Single commit vs commit-per-phase. Whether
the commit message names a Plan number (per CLAUDE.md "Name every
plan"). Whether artifacts get a PR or land directly. For multi-phase
work, name whether phases ship as **one PR holding all phases**
(jointly valuable) or **one PR per phase** (independently valuable).
```

**Optional but encouraged**

- Sequencing note if the prompt is part of a batch.
- Honest-finding clause when the work is the kind where a real finding
  (data quality, a stale dataset, a missing column) is more valuable
  than a clean completion. Naming this explicitly licenses Code to
  surface rather than paper over.

---

## 4. The information-request shape

Smaller and tighter than coding requests. No commit means no commit
shape, no out-of-scope guard, no halt conditions in most cases.

```
# Prompt -- <short interrogative title>

**Kind:** information
**Date:** YYYY-MM-DD
**Output:** <where the answer goes -- chat reply, a docs/ note, a
            session note, an inline file>

---

## Question (required)

The question that needs answering. One sentence ideally. If the
question is "is X true?", state it as a yes/no. If "what is the shape
of Y?", state it concretely.

## Decision this informs (required)

What Chat or Gordon will do with the answer. This is the equivalent of
the coding-request Outcome -- it tells Code why the answer matters and
how precise it needs to be.

Example:
> "Will inform whether the next prompt builds the dashboard against
> bronze (in-line spatial join) or waits on the gold layer landing."

## Where to look (conditional)

If the answer lives in specific files, tables, or routes, name them.
Omit if Code's own investigation is the point.

## Format (conditional)

If the answer needs a particular shape -- a count, a table, a yes/no
plus rationale -- name it. Omit for open-ended findings.
```

---

## 5. The workflow Code runs on receipt

Code does these steps, in this order, for every prompt -- coding or
information. The branch is on Step 3.

### Step 1 -- Read the header

Read Kind, Date, Scope (or Output), Effort, and Depends on. Confirm:

- The kind is declared. If not, ask Gordon before proceeding.
- The Depends-on PRs are merged. If any are open or unmerged, halt and
  surface. Do not start work on an unsatisfied dependency.
- The Scope (or Output) is bounded. If the scope reads "the whole
  portal" or "everything related to X," ask for narrowing before
  starting.

### Step 2 -- Verify state

Before any work, confirm Code is operating against current state:

- `git status` clean on the working branch (or expected dirty state
  understood).
- Local and EC2 main in sync -- `git -C <local> log -1 --oneline` and
  `ssh oxygen-mvp 'git -C oxygen-mvp log -1 --oneline'` match.
- The newest entry in `LOG.md` matches today's date, or the staleness
  is acknowledged.

If state is stale or out of sync, halt and surface. The prompt was
likely written against the state Chat believed was current; if main
has moved, the prompt may already be partially or fully addressed.

### Step 3 -- Branch on kind

**If the prompt is a coding request:** continue to Steps 4-9.

**If the prompt is an information request:** skip directly to Step 8
(Execute). Investigation is the execution. The output is a written
finding, posted where the prompt's Output section directs.

### Step 4 -- Restate the Outcome

In Code's first message back to Gordon (or in the session note if
working unattended), restate the Outcome in Code's own words. This is
the equivalent of the DASHBOARDS.md sec 2.1 business-analyst step: the
purpose must be confirmed in Code's understanding, not just present in
the prompt.

If Code's restatement materially differs from the prompt's Outcome,
that is a finding. Halt and surface -- the Outcome is unclear and needs
clarification before work begins.

### Step 5 -- Pre-flight

Confirm the technical assumptions the prompt is built on. Probe live
state where the prompt depends on it -- the SODA endpoint exists, the
gold table has the expected shape, the file the prompt asks Code to
edit is still where it expects it to be.

The pre-flight is the cheapest place to catch a bad assumption. A halt
at pre-flight costs minutes; a halt mid-execution costs hours.

If the pre-flight surfaces a hard finding -- the dataset isn't what we
thought, the table doesn't exist, the file's been moved -- halt and
surface per the prompt's Halt conditions or per general honest-reporting
discipline.

### Step 6 -- Plan the commit shape

Confirm the commit shape against the prompt's instruction. If the
prompt says "single commit" but the work naturally factors into phases,
surface the mismatch before starting -- don't silently rewrite the
commit structure.

For multi-phase work, plan which phases land in which commits. State
the plan before executing.

### Step 7 -- Execute

Do the work. Update TASKS.md as items complete per CLAUDE.md task
discipline. Emit transcript timestamps per CLAUDE.md timestamp rules.

Honor the prompt's Halt conditions and the standing honest-reporting
discipline. A surfaced finding is a successful outcome, not a failure.

**If something goes wrong during execution.** There are three shapes
this takes; Code recognizes which and responds accordingly:

- **A hard halt.** A pre-flight assumption is wrong, a dependency is
  missing, the Outcome can no longer be served by the planned Work, or
  a Halt condition fires. Stop. Do not commit. Do not try to recover
  by improvising scope. Move to Step 9 (Report back) and report the
  halt as the outcome -- the Status is `blocked` and the report names
  what blocked it and what unblocks it.
- **A partial.** Some items in the Work section landed cleanly; others
  failed or surfaced findings that require Chat or Gordon to make a
  call. Commit the items that landed (per Step 8 below); leave the
  items that didn't. Report-back Status is `partial` per item; the
  Worth-flagging section names the items that didn't land and why.
- **A recoverable miss.** A test failed, a deploy 404'd, an assumption
  about a column name was wrong, but the fix is within scope and Code
  can do it. Fix it. Do not silently rewrite scope -- if the fix
  changes the Work in a way the prompt didn't authorize, treat it as
  a partial and surface, not as a quiet recovery.

The honest-reporting discipline: a partial with a named finding is
worth more than a `complete` that papered over a problem. Code never
fakes a `[x]` to close a session cleanly.

### Step 8 -- Verify and commit

Verification and commits are interleaved, not sequential. The pattern:
verify each item against its gate before committing it; commit each
verified item as it lands; do not batch unverified items into one
commit hoping the gate clears at the end.

**Verification -- what counts as evidence.** Follow CLAUDE.md's
static-artifact vs live-functional distinction:

- **Static-artifact gates** -- the file exists, the config is committed,
  the schema.yml has the entry, the limitation file is there. Evidence
  is the artifact in the committed state. Re-runnable by `git show`.
- **Live-functional gates** -- the page renders, the test passes, the
  chat agent answers, `./run.sh manual` exits 0. Evidence is the
  command output, captured. Re-runnable by running the same command.

If a live-functional gate is blocked in this session (Chrome MCP not
connected, EC2 unreachable, an upstream dataset not yet ingested),
document the gap rather than skipping silently. The report-back's
Worth-flagging section names what wasn't verified and the diagnostic
the next session should run. Do not mark the item `complete` on a
blocked gate -- `partial` is the honest state.

**Commit timing -- when work lands in git.**

- **One commit per Work item by default.** Each item in the prompt's
  Work section corresponds to one logical commit. The commit message
  references the item.
- **Multi-phase work commits per phase.** When the prompt is structured
  as Phase A / Phase B / Phase C (e.g. the four-dataset overnight
  batch), commit after each phase that lands clean. A halt mid-batch
  leaves clean history of what shipped.
- **Code/config changes always require their verification gate to pass
  before commit.** If the gate doesn't pass, the change doesn't commit
  -- it stays in the working tree as a finding to surface.
- **Documentation-only changes commit without verification gates.**
  Edits to LOG.md, TASKS.md, session notes in `docs/sessions/`,
  handoffs in `docs/handoffs/`, limitations entries, and the like are
  documentation. They commit as part of the session's housekeeping,
  not gated on a test. The static-artifact evidence is the file
  existing in the committed state -- that's all the gate they need.
- **TASKS.md and LOG.md updates happen as work completes, not batched
  at end of session.** Per CLAUDE.md task discipline. These are
  documentation; commit as you go.

**Merge timing -- when work lands on main.**

- **The default unit of merge is the prompt.** A prompt produces a
  branch, a branch produces a PR, the PR merges to main when its Work
  section is satisfied. The prompt is the unit because the prompt
  carries the Outcome -- the Outcome is the test of whether the merge
  is justified.
- **PR opens when the first commit lands.** Not at the end. An open PR
  with one commit is a signal to Chat and Gordon that work is
  underway; an open PR is cheaper than a long-lived branch.
- **PR merges when the prompt's Verification section is fully passed
  OR the prompt's surfaced findings are documented and Gordon has been
  asked.** A partial completion does not auto-merge -- Gordon decides
  whether the partial is worth landing or whether the branch waits for
  the rest.
- **Multi-phase prompts have two valid merge shapes; the prompt picks
  one.** Both are legitimate; the choice depends on whether the phases
  are *independently valuable* or *jointly valuable*.
  - **One PR carrying all phases** -- phases are jointly valuable. The
    Outcome isn't served until all phases land. A halt mid-batch
    leaves an incomplete PR for Gordon to decide on. Example: a
    refactor that splits a model across three phases -- none of the
    phases is useful on its own.
  - **One PR per phase** -- phases are independently valuable. Each
    phase merges to main as it lands, on the strength of its own
    verification. A halt mid-batch leaves clean history of what
    shipped on main and what didn't. Example: the four-dataset
    overnight batch (Plans 24-27, PRs #24-#28) -- each dataset's
    bronze ingestion was usable as soon as it landed; no reason to
    block the others on the survey if the survey halted on its gate.
  The prompt's **Commit shape** section names which it expects. If
  the prompt doesn't say, Code asks before starting -- the question is
  "does Phase A serve the Outcome on its own, or only in combination
  with the other phases?" If on its own, per-phase PR. If only in
  combination, one PR.
- **Stacked PRs need their bases retargeted to main before merging.**
  Documented gotcha (LOG.md 2026-05-14 07:30 ET). When in doubt, merge
  only the top of the stack after rebasing.
- **Documentation-only PRs** (LOG/TASKS/handoff rotation, retro
  entries, glossary edits) can merge on the static-artifact gate
  alone. No live-functional verification required. They land when the
  documentation is correct.

### Step 9 -- Report back

After all execution, verification, commits, and merges (or after a
halt), Code emits one report back to Chat. **This report is the last
thing Code emits in the session.** No further chat messages, no
afterthoughts, no "one more thing." The report is the durable artifact
of the session -- Chat reads it to decide what's next; Gordon reads it
to know where the work stands; future sessions read it to reconstruct
what happened. If Code keeps talking after the report, the report isn't
the durable artifact anymore.

If Code realizes something after emitting the report, it goes into the
next session's report, not as a tail on this one.

**The report-back shape:**

```
## Gate table

| Scope | Status | PR |
|---|---|---|
| <item> | <complete|partial|blocked|deferred> | <PR# or commit hash> |

## Shipped

<bulleted list of what changed, with file paths and short rationale.
One bullet per merged item. Omit items that didn't land -- those go
under Worth flagging instead.>

## Worth flagging

<anything Chat or Gordon should know: findings, deferrals, quirks,
items that didn't land and why, decisions made under uncertainty,
live-functional gates that couldn't be verified this session.

This section is non-negotiable. If there is genuinely nothing to flag,
write "Nothing.". An empty Worth-flagging section is itself a signal.>

## Ready for more work -- natural next moves

<Code's read on what's next, given what just landed. Optional. Useful
when Code sees an obvious next move; honest to omit when there isn't
one. Chat decides the actual next move -- this section is input, not
direction.>
```

**Status vocabulary** (the same values appear in CLAUDE.md's session
frontmatter):

- `complete` -- Work item shipped and verified.
- `partial` -- Some sub-items landed; others didn't. The Worth-flagging
  section names the unfinished sub-items.
- `blocked` -- Work item halted before completion. The Worth-flagging
  section names what blocked it.
- `deferred` -- Work item intentionally not started this session (per
  Halt conditions, Out of scope, or a Chat/Gordon decision
  mid-session). The Worth-flagging section names why.

---

## 6. What this standard does NOT cover

- **The Chat side of the conversation.** This standard governs what
  Chat hands to Code and how Code receives it; it does not govern how
  Gordon and Chat decide what to build. That's upstream of the prompt.
- **Multi-prompt batches.** A batch of related prompts is a batch of
  prompts each following this standard. Cross-prompt sequencing notes
  are encouraged but not part of the prompt shape itself.
- **The handoff doc.** Session handoffs (the `docs/handoffs/*.md`
  files) remain Code's existing convention. They sit alongside this
  standard, not in tension with it.
- **Plan-numbered work.** When a prompt corresponds to a Plan number
  (per CLAUDE.md "Name every plan"), the prompt's commit-shape section
  names it. Plans themselves continue to be tracked in LOG.md's Plans
  Registry.

---

## 7. Migration

This standard takes effect on the date it merges. Prompts written
before it are not retroactively reshaped. Future prompts follow it.

Chat is expected to internalize the shape (as part of standing project
instructions) so it produces conforming prompts without Gordon
prompting for them. Code is expected to internalize the receipt
workflow so it runs the steps without being asked.

If a prompt arrives that doesn't conform, Code asks for it to be
reshaped -- the cost of a 60-second reshape upstream is much smaller
than the cost of misaligned work downstream.
