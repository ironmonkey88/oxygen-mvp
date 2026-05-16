---
session: 51
date: 2026-05-16
start_time: 12:30 ET
end_time: 14:24 ET
type: code
plan: plan-A
layers: [docs, portal]
work: [feature, docs]
status: complete
---

## Goal

Bring column-level detail back to `/erd` as four per-tier `erDiagram` blocks below the existing tier flowchart, after PR #44 traded inline columns for tier grouping in the warehouse diagram. Strictly additive — the flowchart stays exactly as-is at the top of the page.

## What shipped

- **`scripts/generate_per_tier_erd.py`** — new generator. Reads `dbt/models/{bronze,silver,gold,admin}/schema.yml`, emits one `portal/erd-tier-<tier>.mmd` per populated tier. Each .mmd contains an `erDiagram` with entities (omitting underscore-prefixed audit columns), generic `text` type tokens (schema.yml carries no `data_type` field), and within-tier FK arrows from `relationships:` tests. Empty tiers (silver) emit no .mmd — the page generator substitutes a styled HTML placeholder instead, since Mermaid 10.x doesn't render a zero-entity erDiagram cleanly.
- **`scripts/generate_erd_page.py`** — extended. Adds a "Column-level detail by tier" divider after the existing flowchart, then four per-tier sections in medallion order. Each section has a tier-color badge (matching the flowchart's classDef colors), heading + subtitle, lede caption, and either the Mermaid `erDiagram` block or the empty-tier placeholder.
- **`run.sh`** stage 9e now calls `generate_per_tier_erd.py` between `generate_warehouse_erd.py` and `generate_semantic_layer_diagram.py`. Future runs keep the per-tier .mmd files in sync as new models land.
- **`portal/erd-tier-bronze.mmd`**, **`portal/erd-tier-gold.mmd`**, **`portal/erd-tier-admin.mmd`** committed alongside the existing `erd-warehouse.mmd` and `erd-semantic-layer.mmd`.

Counts:
- Bronze: 7 models, 0 within-tier FKs.
- Silver: 0 models (placeholder rendered).
- Gold: 12 models, 9 within-tier FKs.
- Admin: 3 models, 0 within-tier FKs.

## Decisions

- **Audit columns omitted from the per-tier erDiagrams.** Underscore-prefixed lineage columns (`_extracted_at`, `_dlt_id`, etc.) appear on most tables and add noise without analyst value. They remain documented in `/docs/` and on `/profile`, and the `audit-columns-non-analytics` limitation entry already flags the choice. Applied consistently across all four tiers.
- **Silver renders as HTML placeholder, not an empty Mermaid block.** A zero-entity `erDiagram` doesn't render cleanly in Mermaid 10.x. The placeholder is a styled `<div>` with the tier's accent color matching the flowchart's classDef, dashed border, and a one-line "(no tables yet — the Silver tier lands with MVP 3 survey curation)" caption. When Plan 24 lands its first silver model, the generator will emit a real .mmd for Silver and the placeholder is replaced automatically — no further ERD work needed.
- **Generic `text` type token for every column.** schema.yml's column entries carry `name`, `description`, and `data_tests` — but not `data_type`. Source DDL types live in `docs/schema.sql`. Mermaid requires a type token per column line; `text` is the honest generic placeholder.

## Issues encountered

- **First generator draft dropped 6 of 9 gold FK arrows.** Pre-flight had confirmed 9 `relationships:` tests in schema.yml, but my initial generator only emitted 3 arrows. Root cause: my column-de-duplication logic was too aggressive — schema.yml's docs convention places relationships-only entries as a second `- name: <col>` block below the main one (an artifact of how I wrote the Plan-23 schema entries: column-with-description first, FK-test-only second). My code skipped the second block as a "duplicate," losing the relationships tests that live there. Fix: keep the dedup on column-body output (so entities don't render the same column line twice), but always scan every entry for FK tests regardless of dedup. Post-fix: 9/9 FK arrows surface correctly. Worth flagging as a pattern for any future schema.yml parser — don't dedupe at the entry level, dedupe at the output level.
- **Operator visual-render gate stays open.** Static-artifact gates all pass (generators emit valid .mmd, page HTML renders, curl returns 200, content includes all four tier sections). Visual confirmation that Mermaid actually draws each tier diagram + the flowchart still renders correctly = standard SPA-render walkthrough pattern (`dashboard-render-spa-only`). Gordon clears via browser hard-refresh.

## Next action

The Silver placeholder is wired to auto-populate when Plan 24 (MVP 3 — Happiness Survey silver/gold curation) lands its first silver model. No further ERD work required for that. Other natural next moves remain: Plans 18 + 19 (Builder-CLI dashboards) and Plan 24 (MVP 3 survey curation) — both already drafted as fresh-thread prompts.
