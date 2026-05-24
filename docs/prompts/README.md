# `docs/prompts/` — Chat-issued prompts and Code-issued reports

Durable, lineage-bearing home for the work-item-sized artifacts that flow between Chat and Code: the prompt Chat writes, and the report Code writes back when the work lands.

Companion to [PROMPTS.md](../../PROMPTS.md) (the prompt shape and Code's 9-step receipt workflow) and [CLAUDE.md](../../CLAUDE.md) §"Receiving prompts from Chat" (operating instructions).

---

## Why this directory exists

Prompts and reports used to live only in chat scrollback. Once pasted, they were hard to find. The lineage `Plan N → prompt → session → report → PR` was implicit, reconstructed by inference from LOG.md rows and session files.

This directory makes that chain explicit and greppable. A future Chat session, Gordon in a week, or anyone reading the repo cold can find what was asked for in Plan N and what came back from Plan N as two files in a known directory, both indexed by project knowledge, both diffable in git.

The existing paste loop (Chat writes a prompt → Gordon pastes it into Code → Code executes → Code reports back in terminal → Gordon pastes the report into Chat) survives intact for sessions that don't use this convention. The file convention is **additive**, not a replacement.

---

## Filename convention

Two files per plan, sibling to each other:

| File | Holds |
|---|---|
| `plan-NN-<slug>.md` | The full Chat-issued prompt, verbatim |
| `plan-NN-<slug>.report.md` | Code's report-back from PROMPTS.md §5 Step 9 |

Where:

- `NN` is the plan number from the LOG.md Plans Registry (`37`, `38`, etc.). Pad to two digits when the number is single-digit (`plan-07-foo.md`).
- `<slug>` is the kebab-case content-bearing label from the same Plans Registry row. Examples: `allowlist-edits`, `dba-dashboard`, `tidy-c-playwright`, `prompt-report-lineage`. The slug should match the session file's slug for the same plan when one exists, so `grep` on the slug pulls the full chain.

---

## What goes in the prompt file

The full PROMPTS.md-shaped prompt: header + Outcome + Context (when relevant) + Work + Verification + Halt conditions + Out of scope + Commit shape. Verbatim what Chat would otherwise paste into Code's terminal.

Coding prompts use [PROMPTS.md §3](../../PROMPTS.md#3-the-coding-request-shape) shape. Information prompts use [§4](../../PROMPTS.md#4-the-information-request-shape) shape.

---

## What goes in the report file

Code's report-back from [PROMPTS.md §5 Step 9](../../PROMPTS.md#step-9----report-back). The four sections are:

- **Gate table** — one row per Work item, with `Status` (`complete` / `partial` / `blocked` / `deferred`) and PR # or commit hash.
- **Shipped** — bulleted list of what changed, file paths included, one bullet per merged item.
- **Worth flagging** — anything Chat or Gordon should know: findings, deferrals, quirks, items that didn't land and why, decisions made under uncertainty, live-functional gates that couldn't be verified this session. Non-negotiable — write `Nothing.` if there is genuinely nothing.
- **Ready for more work — natural next moves** — Code's read on what's next, given what just landed. Optional. Useful when there's an obvious next move; honest to omit when there isn't.

Same content as the terminal report-back Code emits at session end. The file is the durable home for it; the terminal output is the conversational copy.

---

## Lifecycle

1. **Prompt commits** to `docs/prompts/plan-NN-<slug>.md`. Either Chat commits it directly (via GitHub MCP if connected) or Gordon downloads the prompt as Markdown from Chat and commits it the old way. If Code's session opens with the prompt arriving via paste only, Code copies the prompt verbatim into the file as the first execution step (preserves the convention for after-the-fact lineage).
2. **Code executes** per PROMPTS.md §5 — read header, verify state, branch on kind, restate Outcome (Step 4), pre-flight, plan commit shape, execute, verify and commit, report back.
3. **Code commits the report** to the sibling `plan-NN-<slug>.report.md`. Typically as the last commit on the PR branch before merge, so the PR carries both the prompt edit (if Code wrote it) and the report.
4. **PR merges per CLAUDE.md autonomous-merge policy** (or pauses per the named pause conditions).
5. **Cycle complete** when the report file exists in the merged state.

A prompt file is "consumed" when its sibling report file exists. Until then, the prompt is open.

---

## Lineage chain

For any plan N with a slug `<slug>`, the full chain is:

```
LOG.md Plans Registry "Plan N — <label>"
  ↔ docs/prompts/plan-NN-<slug>.md       (Chat's intent)
  ↔ docs/sessions/session-NN-YYYY-MM-DD-plan-NN-<slug>.md   (the session narrative)
  ↔ docs/prompts/plan-NN-<slug>.report.md   (Code's report-back)
  ↔ PR #N (the GitHub PR)
```

Each link is searchable by the slug or the plan number. `grep -l "plan-43" docs/` returns every file in the chain.

---

## Backfill policy

Reconstructed prompts (prompts authored after the fact from session narratives + LOG rows + design docs, because the original Chat-issued prompt was never committed) carry an explicit note at the top:

```markdown
**Status:** reconstructed from session narrative — not the original Chat-issued prompt.
**Sources:** docs/sessions/session-NN-YYYY-MM-DD-<slug>.md, LOG.md Plans Registry row, <other source files>.
**Reconstruction date:** YYYY-MM-DD by Plan M (the plan that did the reconstruction).
**Confidence:** sections marked `*(reconstructed, low confidence)*` inline are inferred where source material doesn't cover them; everything else is grounded in the named sources.
```

Going forward (post-Plan 43), prompts land verbatim from Chat and don't need a reconstruction note.

Reports are **not** backfilled. The session file for a plan already holds the report-equivalent content (Goal / What shipped / Decisions / Issues encountered / Next action). Reconstructing reports would be busywork without lineage value.

---

## Coexistence with `docs/handoffs/`

Both directories stay; they hold different things:

| Directory | Holds | Scope |
|---|---|---|
| `docs/prompts/` | Per-work-item prompts and reports | One plan, one session-or-less |
| `docs/handoffs/` | End-of-thread Code → Chat summaries | Multiple plans, multiple sessions, a whole chat thread |

A handoff is what Code writes at the end of an extended Chat thread to brief the next thread. It's a summary, not a prompt or report. The two conventions don't overlap and don't conflict.

---

## What this directory does NOT hold

- **Plan documents.** Canonical plan docs (when a plan is large enough to warrant one) live in `docs/plans/`. The prompt file may reference a plan doc; it isn't a plan doc.
- **Design reviews.** Multi-artifact design-review packages (Playwright captures, finding writeups, screenshots) live in `docs/design-reviews/`.
- **Audits.** Information-request reports that produce a standalone artifact live in `docs/audits/`. (The prompt that asked for the audit can still live here; the audit output goes there.)
- **Limitations.** The limitations registry lives in `docs/limitations/`.

When in doubt, the rule is: this directory holds the work-item-sized artifacts that flow *between* Chat and Code. Other directories hold artifacts that exist for their own sake.
