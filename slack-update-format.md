# Slack Daily Update — Format Spec

Canonical spec for the **"slack daily update"** command. Versioned here so the format itself is editable via prompt, not buried in Claude project instructions.

## Trigger

When Gordon says **"slack daily update"** or **"slack update for [date]"** in a Chat session, produce a status report following this spec.

## Source of content

Pull the last ~24 hours of activity from project knowledge — search `LOG.md`, recent files in `docs/handoffs/`, recent files in `docs/sessions/`. Do **not** ask Gordon to paste anything.

**Staleness check first.** Before writing the report, verify `LOG.md`'s newest entry date looks consistent with the current date. If it's clearly older (e.g. Code has obviously landed commits since the last visible entry, or the date is days behind), say so and stop — produce no report. A confidently-wrong update is worse than no update. The fix is for Gordon to refresh the `oxygen-mvp` connector in the Claude UI and re-issue the command.

## Structure

Two sections only:

1. **Today** — bullet list of what landed in the last ~24 hours. The section header carries the current date, formatted like `Thursday, May 14th — Today`. The list ends with one final bullet that is a single-line status summary (PRs merged, remotes in sync, pipeline green, etc.).
2. **Next** — bullet list of what's queued for the next session or the next short window. Same bullet rules.

No other sections. No preamble. No closing line.

## Voice + formatting rules

- **Outcome-first.** Describe what an analyst can now do or see, not the PR-by-PR mechanics. Lead with capability, not implementation.
- **Plain language.** Readable by a non-technical stakeholder. No internal jargon (no "PR #14", "stacked-merge gotcha", "marker-bounded sections", "Mermaid useMaxWidth", etc.) unless absolutely necessary — and if it is, translate the term inline.
- **Bullets only.** No sub-bullets, no nested lists.
- **No bold inside bullets.** No `**…**`. Use plain prose.
- **One line per bullet.** No wrapping. No multi-sentence bullets.
- **Slack-paste-clean.** Markdown bullets render correctly in Slack. Avoid characters that mangle in Slack's renderer.

## Required behavior after the report

If any bullet references something that went wrong (a bug, a misdiagnosis, a wrong-direction change, a rollback), flag those separately **after** the report — outside the Today / Next sections — so Gordon can decide whether to soften them for a leadership audience versus a working-team audience.

Format the flag as a short note labelled clearly, e.g. *"Honesty flag — bullet 3 references a wrong-direction change that was corrected mid-session. Working-team version is fine as written; leadership version may want softer language."* Do not edit the report itself.

## Worked example

A sample report for an imagined day:

> **Thursday, May 14th — Today**
>
> - The platform homepage now welcomes new analysts with an honest overview of what the data covers and what kinds of questions they can ask.
> - Every page on the portal carries the same navigation, so analysts no longer get stranded on a page with no way out.
> - The data dictionary now opens with a plain-language explanation of what's in the warehouse, instead of dropping the analyst into raw dbt output.
> - The schema diagram page is readable for the first time — diagrams render at full size with horizontal scrolling.
> - Deploys now reflect immediately on browser refresh, removing a class of "the change didn't land" confusion.
> - Five changes merged to main, deployed to the live site, pipeline running green.
>
> **Next**
>
> - Add the missing relationship edge to the warehouse diagram so it shows the full ward-to-311 join.
> - Pick up the next round of dashboard work — a 311 overview and a rat-dashboard iteration, both via the Builder Agent, in a fresh session.

*Honesty flag — one of today's changes was a wrong-direction doc edit that closed a route as "shipped" before the route's render bug was actually fixed. The follow-up fix made the closure correct in outcome, but the reasoning was off at the time. The Today bullet glosses this. Working-team audiences may want a sentence acknowledging the misstep; leadership audiences likely don't.*

## What this spec does NOT cover

- Anything Slack-side (channel, formatting tokens specific to Slack apps, threading). Gordon pastes the output into Slack manually.
- Weekly or monthly summaries — those are a separate command if/when needed.
- Code-side action; this is purely about what Chat produces.
