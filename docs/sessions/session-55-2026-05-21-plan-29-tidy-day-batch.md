---
session: 55
date: 2026-05-21
start_time: 08:55 ET
end_time: 16:05 ET
type: code
plan: plan-A
layers: [bronze, gold, semantic, agent, portal, infra, docs]
work: [bugfix, hardening, docs]
status: complete
---

## Goal

Close items 1–7 (plus the inserted §3.5 credential check as item 8) from the 2026-05-17 tech-debt review in one tidy-day batch.

## What shipped

- `docs/tech-debt-review-2026-05-17.md` landed as the Plan 29 spec (commit `c88f8de`). Five-pass review, 15 priority items, three false positives from intermediate audits retracted by direct verification.
- Item 1 (`33569fa`) — `scripts/generate_metrics_page.py:48` `mtype == "avg"` → `mtype == "average"`. EC2 live regen of `portal/metrics.html` confirmed `AVG(` × 2, `AVERAGE(` × 0; both affected measures (`average_permit_value`, `average_vehicle_speed_on_speed_violations`) now render valid SQL. STANDARDS.md §4.2 row 3 restored to honest.
- Item 2 (`5bb3761`) — `run.sh` `deploy_html` tightened: source-file precondition added, `|| true` mask removed from `sudo chown`, atomic `.tmp + mv` write. Four scenarios smoke-tested locally (happy / atomic-cleanup / missing-source-refusal / stale-preserve).
- Item 3 (`be3cfdc`) — `dbt/models/gold/schema.yml` `ward` entries consolidated for both `fct_311_requests` and `fct_crime_incidents`. EC2 `dbt parse` + `dbt test --select fct_311_requests fct_crime_incidents` → 19/19 PASS, both `relationships_fct_*_ward__ward__ref_dim_ward_` tests intact.
- Item 4 (`60a1454`) — CLAUDE.md "LLM Configuration" snippet refreshed to `claude-opus-4-7` + Sonnet→Opus migration note.
- Item 5 (`83744be`) — CLAUDE.md "Project File Structure" tree refreshed: dropped non-existent `routing_agent.agent.yml` + `somerville_dashboard.app.yml`; added missing root-level docs (MVP/BUILD/STACK/STANDARDS/DASHBOARDS/PROMPTS/PHILOSOPHY/PRODUCT_NOTES), missing dirs (`nginx/`, `systemd/`, `scripts/`), missing subtrees (`docs/limitations/`, `docs/sessions/`, expanded dlt set, scripts/, dbt/tests/singular/), and re-annotated `docs/schema.sql` as agent-context (not source of truth).
- Item 6 (`75de3c2`) — `docs/schema.sql` rewritten with `main_bronze`/`main_gold`/`main_admin` (3 schema declarations, 24 `CREATE TABLE` statements, 8 `REFERENCES` clauses, plus the inline comment references). Header retitled "DDL reference for the Answer Agent" with explicit "NOT the authoritative source of truth" framing. Endpoint (a) chosen over (b) because semantic-layer views only enumerate query-relevant columns; schema.sql's full column shape (audit, lineage, survey, dept-tag blocks) is still load-bearing context. One stale filename reference corrected (`crime-data-pii-unredacted-in-bronze.md` → `crime-bronze-restricted-from-analysis.md`).
- Item 7 (`cb64e15`) — `.claude/settings.json` `sudo cp/mv/ln` allows scoped to `/etc/nginx/*` + `/etc/systemd/system/*`; broad `/etc/*` denies added for cp/mv/ln/ln-s. Adjacent: `Bash(rm -fr *)` (flag-order variant) and `Bash(git push --force-with-lease *)` (+`-C *` variant) added to deny. JSON validated. Allowlist `[x]` evidence: `git show HEAD:.claude/settings.json | grep -F 'Bash(sudo cp * /etc/nginx/*)'` and the `/etc/*` deny both return matches.
- Item 8 (EC2-side) — `/etc/environment` was mode 644 (world-readable). `sudo chmod 640 /etc/environment`; `oxy.service` restarted; `/api/health` returns `{"status":"healthy","database":{"connected":true}}` after a 25-second postgres-container bootstrap. ANTHROPIC_API_KEY still sourced (systemd reads as root; group `root` retains read access; world stripped).
- Cross-cutting: one agent smoke query on EC2 confirmed Item 6 didn't break the trust contract — `oxy run agents/answer_agent.agent.yml "How many 311 requests were opened in 2024?"` returned **113,961** rendered with `main_gold.fct_311_requests`, "Returned 1 rows.", Citations block (`main_gold.fct_311_requests` + `requests` view + `source-bulk-republish-no-per-row-modified` limitation), and Known limitations section.

## Decisions

- **Item 6 endpoint (a) over (b).** The review preferred (b) (drop schema.sql from agent context entirely). Picked (a) because the semantic-layer view YAMLs only list query-relevant columns (~6 per view), while schema.sql carries the full column shape per table (audit columns, lineage columns, dept-tag blocks, survey columns) — context the agent actually uses when an analyst asks about an off-view dimension. (b) remains a future option after a column-context migration into the view layer; that migration is out of scope here.
- **Item 7 scope kept tight.** The two legitimate `sudo cp/mv/ln` target families today are `/etc/nginx/*` and `/etc/systemd/system/*`. Scoped allows to those two; if a third legit target surfaces in a future deployment, the prompt-out reveals it and the allowlist grows deliberately rather than by accretion. Halt condition for over-narrow allows: surface as a finding, don't re-broaden.
- **Item 3 scope kept tight.** Reviewed `fct_permits` (lines 399 + 411) and `fct_citations` (561 + 577) — same split-entry pattern for ward, not flagged by the review. Left untouched; noted in commit message as a follow-up for a future dbt-schema-hygiene pass.
- **Item 8 mode chosen as 640, not 600.** 600 (root-only) would prevent any group access; 640 keeps the `root` group readable. systemd reads `EnvironmentFile=` as root either way, so 640 is sufficient for the threat model (strip world; keep root + root-group). If a future audit requires 600, that's a one-character change.

## Issues encountered

- `rewrite_schema_sql.py` regex `\b(bronze|gold|admin)\.([a-z_]+)` over-matched inside a comment line and converted `unredacted-in-bronze.md` to `unredacted-in-main_bronze.md`. The referenced filename was already stale (the actual limitation file is `crime-bronze-restricted-from-analysis.md`). Fixed inline; lesson logged here, not propagated to a standalone limitation.
- `python3 -m json.tool /path > /dev/null` was the JSON validator I reached for; works fine but the `&&`-chain in the original intent was hook-blocked. Single tool call resolved.
- Initial agent-smoke probe (`/api/health` immediately after `systemctl restart oxy.service`) returned a connection-refused — postgres container takes ~25s to bootstrap. Second probe (after `sleep 25`) was clean. Not an issue with the chmod; documented for future restart sequencing.

## Next action

PR `claude/bold-dirac-7b6669` against `main` — autonomous push/PR/merge per standing policy. After merge, the next `./run.sh` will be the first real exercise of (a) the tightened `deploy_html` precondition, (b) the corrected `/metrics` SQL rendering deployed to `/var/www/somerville/metrics.html`, and (c) the new allowlist scoping (the actual nginx/systemd sudo paths in the pipeline). Queued follow-ups from the review's items 8–15 (DUCKDB_PATH centralization, Python script tests, nginx security headers, fct_test_run calendar bomb, load_dbt_results dedup, TASKS.md stale-line cleanup, backtick blocker, Silver layer) remain for separate sessions.
