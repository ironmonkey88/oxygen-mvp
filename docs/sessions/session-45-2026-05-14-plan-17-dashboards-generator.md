---
session: 45
date: 2026-05-14
start_time: 06:00 ET
end_time: 07:00 ET
type: code
plan: plan-17
layers: [portal, docs]
work: [feature, refactor]
status: complete
---

## Goal

Generate `/dashboards` listing from `apps/*.app.yml` metadata on every pipeline run so future dashboards auto-surface. Third session of the MVP 2 polish arc.

## What shipped

- Metadata contract: each `.app.yml` carries a leading `# === DASHBOARD METADATA === ... # === END DASHBOARD METADATA ===` comment block (parsable as YAML after stripping `# ` prefix). Fields: title, topic, short_desc, row_caption, coverage, source_tables, limitations, trust_signals
- `oxy validate` confirms 12/12 configs valid post-retrofit -- comment-block keeps metadata invisible to Oxygen, no unknown-key rejection risk
- [`scripts/generate_dashboards_listing.py`](../../scripts/generate_dashboards_listing.py): walks `apps/*.app.yml`, parses metadata block (falls back to `name:` + first paragraph of `description:` if absent), computes base64-encoded `/apps/:pathb64` URL (Session 42 fix), rewrites marker-bounded listing in `portal/dashboards.html` between `BEGIN_DASHBOARDS_LISTING` / `END_DASHBOARDS_LISTING`. ~50ms
- Retrofit: [`apps/rat_complaints_by_ward.app.yml`](../../apps/rat_complaints_by_ward.app.yml) gains the metadata block; `portal/dashboards.html` hand-edited rat card replaced with marker-bounded generator output; footnote updated
- `run.sh` new stage 8c/10 between homepage summary (8b) and portal sync. Adds explicit `deploy_html` for `dashboards.html` to nginx docroot
- PR [#8](https://github.com/ironmonkey88/oxygen-mvp/pull/8) opened, originally stacked on PR #7 (chain: #6 -> #7 -> #8)

## Decisions

- **Comment-block metadata, not top-level YAML keys.** Avoids any risk of Oxygen's `.app.yml` schema rejecting unknown keys. The comment-block is fully bulletproof: Oxygen sees pure comments, generator parses YAML after stripping `# `. Validated by `oxy validate` 12/12 post-retrofit.
- **Generator has graceful fallback.** Apps without a metadata block still render via `name:` + first paragraph of `description:`. Builder Agent's future drafts that don't include the block yet still surface on `/dashboards` -- a separate session can backfill metadata.

## Issues encountered

- **Double-escape bug in trust-signals span.** First-pass generator used `escape(" &middot; ".join(...))` which converted `&middot;` to `&amp;middot;`. Operator visual would have read it as literal text. Fixed by escaping items before joining with the literal entity: `" &middot; ".join(escape(s) for s in trust_signals)`. Caught during pull-back inspection, fixed in the same session.

## Next action

End of MVP 2 polish arc Phase 1 (Sessions 43-45). Phase 2 (Sessions 46-47, Builder CLI dashboards) deferred to a fresh Code thread per the honest-reporting discipline -- the Builder CLI interactive sessions are qualitatively different from the mechanical generator work of 43-45 and risk quality drop in a context-heavy thread. See [handoff-2026-05-14-sessions-43-to-45.md](/Users/gordonwong/handoff-2026-05-14-sessions-43-to-45.md).
