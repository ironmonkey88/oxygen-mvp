# Report — Plan 51: session-starter.md new-account cold-start block

**Status:** complete
**Date:** 2026-06-17
**Repo:** `oxygen-mvp` (this report) — sibling work landed as `stack-in-a-box` Plan 11.

## Plan numbers (both repos)

| Repo | Plan | Branch | PR |
|------|------|--------|----|
| `oxygen-mvp` | **51** | `claude/plan-51-session-starter-coldstart` | [#84](https://github.com/ironmonkey88/oxygen-mvp/pull/84) |
| `stack-in-a-box` | **11** | `claude/plan-11-session-starter-coldstart` | [#15](https://github.com/ironmonkey88/stack-in-a-box/pull/15) |

Slots resolved by boot-audit:
- **oxygen-mvp:** tail = 50; 41/42/45 reserved, 47 = open PR #76 → **51** next contiguous free.
- **stack-in-a-box:** tail = 10; Plan 4 reserved/in-flight → **11** next contiguous free.
No ambiguity; plan-number halt did not fire.

## Halt condition (migration docs present) — cleared

Before wiring, verified all three migration docs exist **and are git-tracked** at their named paths in **both** repos (`git ls-files`):
- `docs/MIGRATION_SUMMARY.md` ✅ (both)
- `MIGRATION_CHECKLIST.md` ✅ (both)
- `PROJECT_MIGRATION_2026-06-07.md` ✅ (both)

No file pointed at is missing; halt did not fire.

## What shipped

Per repo:
1. **Phase 0** — this prompt verbatim at `docs/prompts/plan-NN-session-starter-coldstart.md`.
2. **Cold-start block in `session-starter.md`** — a conditional section: "If you are a fresh Claude in a new account or on a new machine, start here; otherwise skip to How to Start Each Session." Names the trio in read-order (**MIGRATION_SUMMARY → CHECKLIST → PROJECT_MIGRATION**) with each doc's role, then hands off to the normal flow (LOG.md, TASKS.md). Placed: oxygen-mvp right after the title; stack-in-a-box right after the "Which repo is this?" callout — equivalent top-of-file positions, both before the start-each-session steps.
3. **LOG.md + TASKS.md** — Plans Registry row + Last Updated bump; Next Focus block.

## Verification (all static — nothing executes)

- Both `session-starter.md` files contain the cold-start block, **identically worded** — extracted-block `diff` clean (11 lines each). ✅
- The block names all three docs with correct paths, in the stated read-order, and is explicitly conditional on a new-account/new-machine restart. ✅
- Every path the block references resolves to a real, tracked file in that repo. ✅
- No other part of either `session-starter.md` was altered (each repo's diff: `session-starter.md` = +12 lines, single hunk). The two files remain intentionally **not** byte-identical overall. ✅
- LOG.md + TASKS.md updated in each repo. ✅

## Out of scope / notes

- **No new standalone doc** — consolidated into the existing `session-starter.md`, as directed.
- **Superseded prompt:** the earlier infra-install "zero-to-live setup runbook" prompt is treated as superseded by this consolidation decision; it was not run.
- **Pre-existing unrelated working-tree changes in oxygen-mvp** (a modified `docs/sessions/session-72-...md` and untracked `docs/ec2-account-migration-checklist.md` + `docs/quick-dives/`) were present at session start and are **outside this plan's scope** — deliberately **not** staged or committed here. Flagged for awareness.

## Halt conditions

None fired. Plan slots unambiguous; all three migration docs present and tracked in both repos.
