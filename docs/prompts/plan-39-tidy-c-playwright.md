# Prompt — Track C tidy-day + Track P Playwright targets_selector + Track D DBA dashboard v1.1

**Status:** reconstructed from session narrative — not the original Chat-issued prompt.
**Sources:** [`docs/sessions/session-64-2026-05-23-plan-39-tidy-c-playwright.md`](../sessions/session-64-2026-05-23-plan-39-tidy-c-playwright.md), [`TASKS.md`](../../TASKS.md) Plan 39 row, [`LOG.md`](../../LOG.md) Plans Registry row, [`docs/dba-dashboard-design-2026-05-17.md`](../dba-dashboard-design-2026-05-17.md) (Track D source), [`docs/design-reviews/playwright-targets-selector-smoke-2026-05-22/`](../design-reviews/playwright-targets-selector-smoke-2026-05-22/) (Track P smoke-test artifact).
**Reconstruction date:** 2026-05-24 by Plan 43 (prompt + report lineage).
**Confidence:** Track C scope is taken directly from Plan 38's session note where the items were named when deferred. Track P scope and the `targets_selector` API shape are grounded in the smoke-test artifact + STANDARDS.md §8 + `scripts/rendered_page.py` source. Track D scope as it landed in this prompt (before mid-session split) is *(reconstructed, medium confidence)* — the session note describes the split to Plan 40 in detail, so Track D's *intended* scope is well-attested but the original prompt's exact phrasing isn't preserved.

**Kind:** coding
**Date:** 2026-05-23
**Plan:** 39
**Scope:** branch deletes via `gh api`; `session-starter.md` edits; `dbt/models/bronze/schema.yml` + `dbt/models/gold/schema.yml` enrichment via `scratch/enrich_schema_yml.py`; `TASKS.md` stale entry removal; `scripts/rendered_page.py` extension; `STANDARDS.md` §8 + `CLAUDE.md` verification-gates rule 5 edits; `docs/design-reviews/playwright-targets-selector-smoke-2026-05-22/` new artifact. Track D scope below (substantial — see "Mid-execution split").
**Effort:** one session, ~2-3 hours for Tracks C + P; Track D adds 2-4 hours.
**Depends on:** Plan 38 (DBA dashboard v1 + Track C deferral) — merged. Track C items are explicitly the 4 deferred from Plan 38. Plan 33 (Playwright helper) — merged; Track P extends `scripts/rendered_page.py`. Plan 38's dashboard generator is the live system Track D mods + Track P smoke-tests against.

---

## Outcome

Three independent tracks land in one PR:

- **Track C** closes the 4 tidy-day items deferred from Plan 38 so the next round of focused work isn't carrying low-stakes cleanup as context debt.
- **Track P** makes Plan 33's `review_page()` helper useful for multi-element pages (dashboards, listings) — currently it's hardcoded to the back-link verification path; adding `targets_selector` opens it up.
- **Track D** ships DBA dashboard v1.1 — cost panel enhancement + source-health expansion from 1 to 6 datasets + design-doc revision + a Playwright verification that exercises the new `targets_selector` for real.

Tracks C + P + D in one PR is a deliberate choice — Track P is the helper the Track D verification needs, and Track C is opportunistic doc-only cleanup. If Track D scope escalates mid-execution beyond what fits in a single session window, the prompt explicitly allows a split.

## Context

**Track C — the 4 deferred items from Plan 38.** Plan 38's session note named them when Code surfaced that the Phase A + Phase B PR was already substantial and Track C should split:

- C1 — stale branch cleanup (anticipate ~6 stale `claude/*` branches from Plans 32-37).
- C2 — `session-starter.md` "Code's Operating Environment (Brief)" section.
- C3 — `dbt/models/*/schema.yml` `data_type:` annotations.
- C4 — TASKS.md item 13 stale LOG-rotation self-flag removal.

These are documentation-only and the session boot-audit will trigger off them if left to rot, so closing them in a dedicated PR is the right shape.

**Track P — Playwright helper enhancement.** Plan 33 shipped `scripts/rendered_page.py` with `test_page()` (assertion-based) and `review_page()` (capture-based for design reviews). `review_page()` was used in Plans 34 + 35 to verify dbt-docs back-link rendering. In Plan 38, the helper was used against the new DBA dashboard, but per-panel callouts didn't draw because the annotation selector was hardcoded to back-link elements. The fix: add a `targets_selector` parameter that takes a CSS selector (or list) and draws numbered callouts on each match.

Backward compatibility is load-bearing — Plan 33/34/35's back-link verification path must keep working unchanged. Default `targets_selector=None` preserves the old behavior.

**Track D — DBA dashboard v1.1.** The design doc (`docs/dba-dashboard-design-2026-05-17.md`) names v1.1 scope. Specifically:

- D1 cost panel enhancement: v1's C2 token-spend panel shows 7-day spend. v1.1 wants month-to-date + 30-day sparkline + burn-rate vs last month. Implementation needs sparkline rendering capability the generator doesn't have yet.
- D2 source-health expansion: v1's B1 panel covers 311 only. v1.1 wants all 6 sources (311 + crime + permits + traffic-citations + wards + at-a-glance) with per-dataset staleness thresholds reflecting documented refresh expectations. The prompt anticipates 3 separate scripts per data shape (Socrata API / ESRI / JSON). 5 new systemd timer + service pairs to install.
- D3 generator updates: cost panel (D1) integration; `data-panel-id` HTML attribute on each panel (Track P's `targets_selector` cascade will pick these up first); Group C layout restoration (something in v1 layout shifted the C panels — restore per design doc).
- D4 design doc revision: §0 revision-2 note; §3 Group B B1 updated for 6-source coverage; §3 Group C updated with C2 v1.1 spec; §11 marked C2 shipped.
- D5 Playwright verification using the new `targets_selector='[data-panel-id]'` to exercise both the helper enhancement and the new attribute.

**Mid-execution split clause.** If Track D's realistic scope (D1 + D2 + D3 + D4 + D5) pushes the session into "rushed end" territory, surface and split. Plan 40 would pick up Track D as a dedicated plan. The pattern from Plan 38 (Phase A + B in one plan, Track C deferred) is the precedent.

## Work

**Track C — tidy-day items.**

C1. Stale branch cleanup. Loop `gh api repos/<owner>/<repo>/branches` (paginated), for each branch that's merged-to-main and is not `main`: `gh api -X DELETE repos/.../git/refs/heads/<name>`. Use a `while read` loop. Surface the actual count if materially different from the anticipated ~6.

C2. `session-starter.md` extension. After "How We Work Together" section, before "Rules of Engagement", add new section "Code's Operating Environment (Brief)" with the 6 drift items:

- Autonomous PR-merge policy location (pointer to CLAUDE.md).
- 3-tier allowlist (Tier 1/2/3 + 2 not-tiers per Plan 36 audit).
- Bash safety rules + hook precedence (pointer to CLAUDE.md "Bash Safety" + "Known gotchas").
- EC2 dbt PATH gotcha (`/home/ubuntu/oxygen-mvp/.venv/bin/dbt` explicit).
- SCP → merge → pull lock (`git checkout --` first).
- `git push` HTTP 400 on large binary blobs (postBuffer 524288000).

Keep each item 2-3 lines. Pointer to canonical doc for full detail.

C3. `dbt/models/bronze/schema.yml` + `dbt/models/gold/schema.yml` `data_type:` enrichment. Write `scratch/enrich_schema_yml.py` that:

- Reads each schema.yml line-by-line with a state-machine (tracks `models:` section presence, current model, `columns:` section presence, current column).
- Queries DuckDB DESCRIBE for each model's columns to get types.
- Inserts `data_type: <type>` immediately after each column's `- name:` line.
- Preserves all existing content (descriptions, tests).

Run the script; verify `dbt parse` clean post-enrichment.

C4. Remove `TASKS.md` stale LOG-rotation self-flag entry (item 13 in tech-debt review). Also remove any adjacent stale items that self-document as removable.

**Track P — Playwright targets_selector enhancement.**

P1. Extend `scripts/rendered_page.py` `review_page()` signature:

```python
def review_page(
    url: str,
    output_dir: Path,
    focus: str | None = None,
    targets_selector: str | list[str] | None = None,  # NEW
) -> ReviewArtifact:
    ...
```

Default `targets_selector=None` preserves Plan 33/34 back-link behavior — the existing back-link probe runs and produces the same annotated output it always did.

P2. New `_SELECTOR_TARGETS_PROBE` JS function injected when `targets_selector` is provided. The function:

- Accepts an array of CSS selectors.
- For each selector, queries the page (`document.querySelectorAll`).
- For each match, returns `{boundingBox, label}`.
- Label derivation cascade (the P3 cascade):
  1. `data-panel-id` attribute if present.
  2. `id` attribute if present.
  3. First non-empty text node, truncated to ~30 chars.

P3. Annotation: draw numbered callouts on each target match's `boundingBox`. Same drawing primitive as the back-link annotation. Legend below the screenshot lists each callout number + its label.

P4. `STANDARDS.md` §8 "Rendered-page verification" — update the `review_page()` signature documentation; add `targets_selector` usage example.

P5. `CLAUDE.md` verification-gates rule 5 — add one sentence noting multi-element targets (`targets_selector="..."` for dashboards with many panels, etc.).

P6. Smoke test: run `review_page()` against the v1 DBA dashboard (`http://oxygen-mvp/admin/`) with `targets_selector='.panel'`. Confirm 10 numbered callouts on the panel grid. Labels will fall through to text-content fallback (panels don't have `data-panel-id` yet — that's a Track D D3 item).

P7. Commit the smoke-test artifact to `docs/design-reviews/playwright-targets-selector-smoke-2026-05-22/` (finding.md + annotated.png + raw evidence).

**Track D — DBA dashboard v1.1.**

D1. Cost panel enhancement. Delete v1's `panel_c2_token_spend` (7-day flat number). Replace with `panel_c2_cost`:

- Month-to-date Anthropic spend (sum `input_tokens * input_price + output_tokens * output_price` over current month).
- 30-day inline-SVG sparkline of daily spend.
- Burn-rate-vs-last-month delta (current month projected vs last month actual).

Pricing: use Opus 4.7 flat rates from `config.yml`. Document the flat-rate assumption (no model column on `messages`; single-model deployment) in a new limitations entry `docs/limitations/cost-panel-pricing-assumptions.md`.

D2. Source-health expansion. The prompt anticipates 3 separate scripts (Socrata API / ESRI / JSON) — pre-flight each source's metadata API shape before writing the loaders. Goal: per-dataset staleness check with thresholds reflecting documented refresh expectations. 5 new systemd timer + service pairs (crime + permits + traffic-citations + wards + at-a-glance) installed + enabled, staggered by 5 minutes to spread load.

D3. Generator updates:

- Integrate `panel_c2_cost` from D1.
- Add `data-panel-id` attribute to each panel element via `render_panel()`. All 10 panels (A1-D2) get the attribute.
- Restore Group C layout per design doc.

D4. Design doc revision (`docs/dba-dashboard-design-2026-05-17.md`):

- §0 — add revision-2 note.
- §3 Group B B1 — update for 6-source coverage.
- §3 Group C — update with C2 v1.1 spec.
- §11 — mark C2 shipped; C3 AWS still future.

D5. Playwright verification. Run `review_page()` against `http://oxygen-mvp/admin/` with `targets_selector='[data-panel-id]'`. Confirm 10 numbered callouts with clean data-panel-id labels (no fallback to text-content). Commit artifact to `docs/design-reviews/admin-dashboard-v1-1-2026-05-22/`.

## Verification

**Static-artifact gates (Track C):**

- `gh api repos/.../branches` shows `main` only post-cleanup (or surfaces the kept branches).
- `session-starter.md` has new "Code's Operating Environment (Brief)" section with 6 drift items.
- `dbt/models/bronze/schema.yml` + `dbt/models/gold/schema.yml` have `data_type:` keys on columns; total annotations within 10% of estimated 250.
- `dbt parse` exits clean post-enrichment.
- `TASKS.md` no longer has the stale LOG-rotation entry.

**Static-artifact gates (Track P):**

- `scripts/rendered_page.py` `review_page()` signature has `targets_selector` parameter with default `None`.
- `_SELECTOR_TARGETS_PROBE` JS function exists; P3 label cascade implemented.
- `STANDARDS.md` §8 updated with new parameter doc + example.
- `CLAUDE.md` verification-gates rule 5 updated.
- `docs/design-reviews/playwright-targets-selector-smoke-2026-05-22/` exists.

**Static-artifact gates (Track D):**

- `scripts/generate_admin_dashboard.py` has `panel_c2_cost` function; `panel_c2_token_spend` removed.
- `data-panel-id` attribute on all 10 panels.
- 5 new systemd timer + service pairs (`source-health-{crime,permits,traffic-citations,wards,at-a-glance}.{service,timer}`) installed + enabled.
- Per-dataset staleness thresholds defined in `scripts/source_health_check.py` (or its successor).
- `docs/dba-dashboard-design-2026-05-17.md` has §0 revision-2 note + §3 Group B/C revisions + §11 marked C2 shipped.
- `docs/limitations/cost-panel-pricing-assumptions.md` exists.

**Live-functional gates (Track P):**

- Backward compat: a `review_page()` call with `targets_selector=None` (or omitted) produces the same back-link annotated output Plan 33/34 produced.
- Smoke test: `review_page(url='http://oxygen-mvp/admin/', targets_selector='.panel')` produces 10 numbered callouts, labels via text-content fallback.

**Live-functional gates (Track D):**

- `http://oxygen-mvp/admin/` headline is YELLOW with ≥3 advisory items (4 expected: A2 streak, A3 duration, B1 expanded coverage real-stale, B2 dbt warn).
- All 6 sources visible in B1 panel.
- `panel_c2_cost` shows month-to-date spend with sparkline rendered.
- All 5 new source-health timers active in `systemctl list-timers`.
- Playwright artifact at `docs/design-reviews/admin-dashboard-v1-1-2026-05-22/` shows 10 callouts with clean `data-panel-id` labels.

## Halt conditions

- **Track P backward compat breaks.** If the existing back-link verification path produces different output after the signature change, halt + surface; do not commit.
- **Track C dbt parse fails post-enrichment.** Roll back the script's edits before commit.
- **Track D D1 cost calc has no source data.** If `messages` has no rows with `input_tokens`/`output_tokens` populated, halt and surface — the cost panel can't render.
- **Mid-execution scope blowout.** If Track D's realistic scope pushes the session into "rushed end" territory, surface the option to split Track D to Plan 40. Don't ship Track D rushed; the value is in the v1.1 polish, not in jamming it through.

## Out of scope

- **Multi-model cost calc.** v1.1 assumes single-model flat-rate (config.yml). Multi-model attribution waits for the messages table to grow a model column.
- **AWS cost panel (C3).** Design doc names it future-work — needs Cost Explorer API setup that's not in this plan's scope.
- **Two-way controls on the dashboard.** Still read-only.
- **HTTPS / magic-link auth on `/admin`.** Still Tailnet-only.

## Commit shape

Single PR holding Tracks C + P + D — jointly valuable (Track P is the helper Track D's D5 needs; Track C is opportunistic doc-only). If Track D splits mid-execution per the named clause, PR ships Tracks C + P and Track D becomes Plan 40 in a fresh thread.

Per CLAUDE.md autonomous-PR-merge policy: push → `gh pr create` → `gh pr merge --merge --delete-branch` autonomously if all gates pass.
