# MVP 2 polish arc — merged + verified — 2026-05-14

Update to the [Sessions 43-45 handoff](2026-05-14-sessions-43-to-45.md). Three of five sessions shipped, merged to main, pipeline re-verified end-to-end. Sessions 46-47 (Builder CLI dashboards) still deferred to a fresh Code thread.

## Gate status

| Gate | State | Evidence |
|---|---|---|
| Plan 15 — Home page dataset summary | merged | PR [#6](https://github.com/ironmonkey88/oxygen-mvp/pull/6) `8e31355` |
| Plan 16 — Welcome content + ward map | merged | PR [#7](https://github.com/ironmonkey88/oxygen-mvp/pull/7) (content rode in via #8) |
| Plan 17 — /dashboards auto-generator | merged | PR [#8](https://github.com/ironmonkey88/oxygen-mvp/pull/8) `941def1` |
| Sessions 43-45 docs (notes + LOG.md) | merged | PR [#9](https://github.com/ironmonkey88/oxygen-mvp/pull/9) `421da94` |
| Plan 16 SVG-path bugfix | merged | PR [#10](https://github.com/ironmonkey88/oxygen-mvp/pull/10) `47622c0` |
| EC2 main sync | green | `47622c0` |
| `./run.sh manual` | green | `run_status=success`, exit 0, 883s, run_id `01KRK45QRKQHKD58EVDV43VMF3` |
| Homepage dynamic stats live | green | 1.17M / 22.3K / 7 wards / 21 limitations / latest 2026-05-13 / last run 2026-05-14 |
| /dashboards listing live | green | rat-complaints card generated from `.app.yml` metadata block |
| Ward map SVG served | green | `image/svg+xml`, 19.9KB at `/somerville-wards-background.svg` |
| Plan 18 (311 overview) | deferred | Builder CLI session — fresh thread |
| Plan 19 (rat iteration) | deferred | Builder CLI session — fresh thread |

## What's now live on the public portal

`http://18.224.151.49/` shows the refreshed homepage. New sections:

1. **Hero** — refreshed subtitle mentions both 311 + crime; nav badge MVP 2; pill points at `/chat`
2. **Stats grid** — auto-refreshed by `scripts/generate_homepage_summary.py` on every pipeline run
3. **What's in the data** (new) — two topic cards (`service_requests` + `public_safety`) with row count, date range, key dim coverage, per-topic active-limitation count linked to `/trust`
4. **What you can ask** (new) — 6 example questions: 4 chat prompts + 2 dashboard pointers
5. **Welcome** (new) — intro + "How to use this" (chat, dashboards, surfaces) + "The trust contract" (4 receipts)
6. **What's not yet possible** (new) — 6 honest gaps with `/trust` links: sub-ward geography, demographic correlations, survey signal, sub-month crime, sharing surfaces, verified queries
7. **Platform surfaces** — expanded 4 → 7 cards
8. **Ward map background** — stylized SVG of all 7 wards, opacity 0.45, peeks behind the hero/welcome area
9. **Roadmap** — MVP 2 active, MVP 1 dim
10. **`/dashboards`** — listing now auto-generated from `apps/*.app.yml` metadata; adding a new dashboard surfaces automatically

## Worth flagging

- **Stopped at Sessions 43-45 boundary, not Session 47.** Brief said stop after 47; honest stop condition was "Anything that contradicts a load-bearing assumption" — load-bearing assumption was that 5 sessions fit one Code thread at quality. Sessions 43-45 were mechanical (generator + HTML + run.sh wiring, same pattern). Sessions 46-47 need interactive Builder CLI + Chrome MCP visual verification — qualitatively different modes. Better to stop with 4 verified PRs than ship 5 where Builder-CLI ones might need retraction (the Session 41 lesson, recursively).

- **Stacked-PR base-ref gotcha during merge.** When merging #6 → #7 → #8 in sequence, GitHub does *not* auto-update dependent PRs' base refs. Merging #7 right after #6 sent its content to the orphaned `claude/plan-15-*` branch, not main. Recovered by retargeting #8's base to main directly — #8's branch (top of stack) already carried #6+#7+#8 content, so a single merge brought everything in. Documented in LOG.md Active Decisions. Lesson for future stacked PRs: retarget each PR's base to main before merging, OR just merge the top of the stack.

- **SVG path-collision bug (caught + fixed in this thread).** Homepage CSS referenced `/assets/somerville-wards-background.svg`, but nginx's `location /assets` proxies to the Oxygen SPA at localhost:3000. The static SVG request got the SPA's index.html back as HTML — status 200, so my generator's curl-status check missed it. Renamed to `/somerville-wards-background.svg` (top-level), added explicit deploy in run.sh, verified `Content-Type: image/svg+xml`. PR #10 includes the meta-lesson: future portal-asset verification needs to check Content-Type or grep the body for a known marker, not just status code.

- **Customer-feedback queue unchanged.** Still 2 findings (Builder CLI token-budget hang + default trust-signal behavior gap). Sessions 46-47 will likely add 1-2 more.

## Next

Three options, same as the earlier handoff:

1. **Spin a fresh Code thread for Sessions 46-47** (recommended). Hand off the original 5-session brief + the two handoff docs. Fresh attention on the Builder CLI work + Chrome MCP visual verification. The substrate (Plans 15-17) is now deployed and verified, so the new thread builds on green.
2. **Review the merged surfaces in a browser, then schedule Sessions 46-47.** Read `http://18.224.151.49/`. If the welcome / dataset cards / ward map all read well, queue the Builder CLI sessions for a later thread.
3. **Pick something else.** The polish arc Phase 1 (which is what landed) is genuinely a meaningful upgrade; Sessions 46-47 are additive but not blocking anything.

## Open PR queue: empty

All 5 PRs from this work merged. Nothing waiting for review.
