# Plan A + Plan B (revisited) + nginx cache fix — 2026-05-14

Follow-up to the [MVP 2 polish merged handoff](2026-05-14-mvp2-polish-merged.md). Closes the three queued items (session-starter, Plan A, Plan B) plus one infrastructure bug surfaced during deploy verification.

## Gate status

| Gate | State | Evidence |
|---|---|---|
| Session-starter reframed for project-knowledge search | merged | PR [#12](https://github.com/ironmonkey88/oxygen-mvp/pull/12) `29cfbc5` |
| Plan A — shared portal nav fragment + dbt docs orientation | merged | PR [#13](https://github.com/ironmonkey88/oxygen-mvp/pull/13) `62852dd` |
| Plan B reconciliation (wrong; superseded) | merged then corrected | PR [#14](https://github.com/ironmonkey88/oxygen-mvp/pull/14) `c7277a9` -- closed `/erd` from a stale doc-rot scan; should not have without verifying the rendered page |
| Plan B Option A — fix `/erd` Mermaid sizing (real fix) | merged | PR [#15](https://github.com/ironmonkey88/oxygen-mvp/pull/15) `7b88bce` |
| nginx `Cache-Control: no-cache` so deploys land on next refresh | merged | PR [#16](https://github.com/ironmonkey88/oxygen-mvp/pull/16) `a0780d6` |
| `./run.sh manual` | green | run_id `01KRKNY32W7GH5W89P9FW74TG9`, status `success`, 829s |
| 7 portal destinations content-verified | green | All carry the seven-link nav with correct active marker; `/erd` now renders both Mermaid diagrams at native size with horizontal scroll |

## What shipped

### Session-starter (PR #12)

`session-starter.md` reframed for the new reality: the `oxygen-mvp` repo is connected as Claude project knowledge, so Chat should pull `LOG.md`, `TASKS.md`, plans, session notes etc. directly via search rather than asking Gordon to paste. Connector refresh is manual + load-bearing — the new step 3 of "How to Start" requires Chat to confirm the newest LOG entry date matches today and flag a stale connector if not. Paste path kept as labeled fallback.

### Plan A — shared portal nav + dbt docs orientation (PR #13)

One canonical seven-link nav across all six static portal surfaces. Source of truth: `scripts/_nav.py` exports `nav_html(active: str) -> str` and a `NAV_CSS` constant. Generators import directly; hand-written pages (`portal/index.html`, `portal/dashboards.html`) use `<!-- BEGIN_NAV --> ... <!-- END_NAV -->` markers refreshed by the existing homepage + dashboards generators every pipeline run. Changing the link set in `_nav.py` updates all six pages on next `./run.sh`.

`dbt/models/overview.md` with a `{% docs __overview__ %}` block embedded by dbt as the `/docs/` landing. Plain-language orientation: what the dictionary is, what the warehouse contains (two topics), how it's organized (medallion in analyst terms), how to browse (left sidebar, model pages, lineage), honest gaps linked to `/trust`. Two back-to-portal links. Voice matches Plan 16 welcome content.

Stranded surfaces fixed: `/metrics` used to have 3 links, `/trust` 4. Both now carry the full seven. `Docs` → `Data dictionary` label split unified. Brand unified to "Somerville Analytics" + MVP 2 badge across all six pages.

### Plan B — revisited and fixed (PR #15)

This was the lesson-event of the session. The earlier Plan B closure (PR #14) had reasoned from generator state ("emits Mermaid for 14 models — current") without ever loading `/erd` in a real browser, and concluded "already current — no rebuild needed". Gordon caught it and rebriefed with hard constraints: load the actual page first, ground every conclusion in what's literally rendered.

Doing that found the real bug. Both Mermaid diagrams **do** render as SVG, but Mermaid 10's default `er.useMaxWidth: true` (plus the explicit `flowchart: { useMaxWidth: true }`) downscaled the ~2365px-wide warehouse ERD to fit container width, making text scale ~2× smaller than natural on desktop and ~7.8× smaller on mobile. The page CSS already had `.mermaid { overflow-x: auto }` — the author intended horizontal scrolling — but that style was dead code because the SVG sized itself to container.

**The fix:** one config change in `scripts/generate_erd_page.py` — set `useMaxWidth: false` on both `er` and `flowchart`. SVGs now render at natural 2365×1082 (warehouse) / 2171×407 (semantic) inside the existing scrollable container. Text font sizes confirmed at 12px (headers) and 10.2px (column labels) in a real browser DOM check.

### nginx cache header (PR #16)

After deploying the Plan B fix, Gordon's browser kept serving the old `/erd`. Diagnosis: the nginx config sent no `Cache-Control` header at all, so browsers fell back on heuristic freshness from `Last-Modified` — which can keep a stale copy for hours regardless of `Cmd+R`. Fixed by adding `add_header Cache-Control "no-cache, must-revalidate" always` at the server level. Browsers now revalidate every request via ETag/Last-Modified — 304 if unchanged, 200 with new bytes if changed. Cheap, and removes a whole class of "deploy looks invisible" bugs.

## Worth flagging

- **PR #14 was the exact failure mode the MVP 1 retrospective named.** "Verify the user journey, not the destination" — and I reasoned from artifact state instead of loading the page. Gordon's correction was warranted, and the rebrief's hard constraint ("load the page first, ground every conclusion in what's literally rendered") was exactly the right discipline. Worth noting because this is the second time this class of mistake has happened in two days (Session 41 atob misdiagnosis was the first). The pattern: when an artifact looks current, it's tempting to call the work done. The honest test is always at the user-facing surface, not one level removed. The nginx `Cache-Control` fix is itself an instance — it was the *deploy-verify* discipline that caught the missing header.

- **Plan B Option A vs Option B.** The fix was Option A only (one-line config change to Mermaid init). Option B from the investigation report — adding the missing `dim_ward ↔ fct_311_requests` dbt `relationships` test so the warehouse ERD's 311 side shows its ward edge — is **untouched**. The crime side has the test, the 311 side doesn't, so the ERD undercounts relationships by one. ~30 min of work if you want it scoped as a follow-up.

- **TASKS.md + ARCHITECTURE.md are still in PR-#14's wrong state** for `/erd` and `/docs`. PR #14 closed both as `[x]` and refreshed the nginx-routes table on the assumption that "/erd already shipped via Plan 1b" was the right read. After PR #15's actual fix, both rows really *are* in a shipped state — Plan 1b shipped the generator, PR #15 shipped the rendering. So PR #14's doc edits are now correct *in outcome* even though the reasoning that justified them was wrong-direction at the time. No further doc edit needed.

- **MVP 2 polish arc Phase 2 still deferred.** Sessions 46 (311 overall dashboard via Builder CLI) and 47 (rat dashboard iteration via Builder CLI) belong in a fresh Code thread per the [earlier handoff's](2026-05-14-mvp2-polish-merged.md) recommendation. The substrate is now even cleaner — Plan A's shared nav + Plan B's working `/erd` rendering both land underneath any future dashboard work.

## Next

Three concrete options:

1. **Move on to Sessions 46-47** (the Builder CLI dashboard work) in a fresh Code thread. The polish arc Phase 1 substrate is now complete and verified — homepage + welcome + ward map + dashboards generator + shared nav + dbt docs orientation + working `/erd` + healthy cache headers.

2. **Plan B Option B follow-up** — add the missing `dim_ward ↔ fct_311_requests` dbt `relationships` test, ~30 min. Tightens the warehouse ERD edge count and gives us a real data-quality test as a side effect.

3. **Something else.** Plan A + Plan B (revisited + fixed) + cache headers landed cleanly; nothing on this branch is blocking other work.

My recommendation: option 1 for the next substantive arc; option 2 only if you want the ERD strictly complete before moving on.

## Open PR queue: empty

All 5 PRs from this stretch merged. Branch chain clean.
