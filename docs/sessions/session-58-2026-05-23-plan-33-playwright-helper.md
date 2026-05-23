---
session: 58
date: 2026-05-23
start_time: 14:43 ET
end_time: 15:10 ET
type: code
plan: plan-33
layers: [infra, docs]
work: [feature, infra, docs]
status: complete
---

## Goal

Close the rendered-surface-verification gap the MVP 1 retrospective named and Plan 32 paid for: ship a Playwright-driven helper that can run pass/fail assertions and produce grounded reviews of any public-URL page in the portal, and prove the capability by identifying the JavaScript Markdown library the dbt-docs SPA uses to render `block_contents` — the input Plan 34 needs.

## What shipped

- `scripts/rendered_page.py` (260 lines) with two entry points: `test_page(url, assertions, screenshot_path) -> TestResult` and `review_page(url, output_dir, focus) -> ReviewArtifact`, plus a CLI demo flag `--demo-inspect-dbt-docs-library`.
- EC2 install: `playwright==1.60.0` + `pillow==12.2.0` into `/home/ubuntu/oxygen-mvp/.venv`; Chromium 1223 at `~/.cache/ms-playwright/`. ARM64 install needed `sudo playwright install-deps` for system libs (libatk, libcups, libgtk family); halt-and-surface fired cleanly per prompt's named halt condition, Gordon approved the wrapper.
- `STANDARDS.md` §8 "Rendered-page verification" — when to use it, both entry-point shapes with one-line code examples, output-path convention, named non-goals.
- `CLAUDE.md` "Verification gates for `[x]` ticks" — new rule 5 pointing at the helper for live-functional gates touching visual surfaces.
- `docs/design-reviews/README.md` — what reviews are, what's in a review directory, when reviews happen, four review-shape categories (technical / design / regression / open-ended), honest-reporting discipline.
- Worked-example finding at `docs/design-reviews/dbt-docs-library-inspection-2026-05-22/`: `finding.md` + `annotated.png` + 5 evidence files (`screenshot.png`, `network-requests.json`, `window-globals.json`, `back-link-dom.json`, `rendered.html`).
- LOG.md Plans Registry row + Recent Sessions rotation (Sessions 52 + 53 moved to Earlier) + Last Updated bump.
- TASKS.md Plan 33 `[x]` row + Plan 34 placeholder `[ ]` row with the four named fix paths.
- `.claude/settings.json` carry-over from the earlier `/fewer-permission-prompts` skill run (5 read-only patterns: tailscale status × 2, mcp Chrome × 2, mcp Preview screenshot/inspect). Pruned duplicates from `settings.local.json`.
- Commit `<TBD>` on branch `claude/plan-33-playwright-helper`, PR `<TBD>`.

## Decisions

- **Halt-and-surface on `sudo playwright install-deps`** — prompt's halt condition #1 fired exactly as named ("Playwright install fails... halt and surface; don't fall back to a different browser silently"). Gordon picked the Playwright wrapper over the explicit apt list. Wrapper just runs `apt-get install` under the hood with the same package list. Standard ARM64 Chromium runtime deps; nothing exotic.
- **Follow prompt's literal directory name `dbt-docs-library-inspection-2026-05-22`** despite work landing 2026-05-23 ET. Prompt was explicit about the path; renaming after the fact is small if Gordon wants the date updated.
- **`review_page` writes a scaffolded `finding.md`; reviewer (Code) fills in the prose Finding section** — the helper can't synthesize prose, so it pre-fills all evidence sections and leaves a placeholder paragraph for the human/LLM to replace. The worked-example `finding.md` demonstrates the pattern.
- **Inline-bundle grep is the right fallback when window globals are empty** — the helper's `window` scan returned only 3 unrelated hits; the library is module-scoped in the inline 1.8MB bundle. Identification came from string-grepping `rendered.html` for library signatures (`marked` × 39 hits; `markdown-it`/`showdown`/`remark`/`commonmark`/`micromark` × 0). Pattern worth carrying forward for future SPA-bundle inspections.

## Issues encountered

- **ARM64 Chromium needed system libs.** First `playwright install chromium` failed at host-validation: `libatk1.0-0t64`, `libcups2t64`, `libgbm1`, etc. missing. Fixed by `sudo /home/ubuntu/oxygen-mvp/.venv/bin/playwright install-deps`. Took ~60 seconds; harmless debconf warnings about no controlling TTY. Subsequent `playwright install chromium` succeeded silently (no output on success).
- **No JavaScript bundle in network log** — only 8 requests captured by Playwright (document, manifest.json, catalog.json, third-party Snowplow, two AngularJS-template 404s, analytics pixel). Initially surprising. Resolution: dbt-docs inlines all JS into the 1.8MB `index.html`. Future SPA inspections should expect this pattern and grep the rendered HTML in addition to the network log.
- **AngularJS-template 404s as accidental signal.** Two requests for `/docs/{{ getIcon(item.type, 'on') }}` and `/docs/{{ getIcon(item.type, 'off') }}` (URL-encoded) — AngularJS template expressions that weren't substituted before being requested as URLs. Unambiguous AngularJS (1.x) signature. Not actively broken (dbt-docs works), but worth noting that this kind of "broken-looking" 404 is sometimes a positive identification signal.

## Next action

Plan 34 — back-link fix v2 — is now scopable. Gordon to write the prompt picking among the four fix paths named in `docs/design-reviews/dbt-docs-library-inspection-2026-05-22/finding.md`: (1) plain Markdown link form; (2) nginx `sub_filter` CSS injection; (3) post-`dbt docs generate` sed-replace; (4) drop the back-link entirely + add header-bar nav at nginx layer. Each has tradeoffs. Plan 24, Plans 18/19, DBA Dashboard execution still queued.
