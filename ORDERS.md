# ORDERS — Civic Pulse work inbox

New work arrives here as `## <YYYY-MM-DD>-<id> [OPEN] <title>` sections, appended at the bottom. Whoever builds
(a box session or a cloud session with this repo) pulls, works every OPEN order oldest first, and moves it
`[OPEN]` → `[DOING]` → `[DONE <commit>]`, or `[BLOCKED]` with what's needed, writing the reply under the order.
New sources use the Yu Bei checklist (`docs/yu-bei.md`), ids `yb-<source>`. Tech-debt orders from audits use `td-`.
This is Civic Pulse only: nothing here touches Gordon's personal warehouse (stack-in-a-box METHODOLOGY R21).

## 2026-11-20-td-1 [OPEN] Freshness tests and a stated schedule for every source
From `docs/audits/2026-11-20-warehouse-quality.md` C1/C2. Add dbt source freshness to every bronze source at its real
cadence (311 daily; crime and citations monthly, both now ending 2026-10-19; at-a-glance and the survey on their
publish schedule). Put at-a-glance and the survey in `run.sh` or a timer with the schedule written down. A stale source
must show on /trust and in the run alert. Verify on the box.

## 2026-11-20-yb-permits [BLOCKED] Switch permits to the live dataset nneb-s3f7
From the audit C1 and Thirsty Scholar (2026-11-20). `dlt/somerville_permits_pipeline.py` reads `vxgw-vmky`, which stopped
at 2023-05-15. Replace with `nneb-s3f7` (Applications for Permits and Licenses) through the Yu Bei checklist, into the new
silver layer. Blocked on Gordon: (1) may permit addresses appear in gold / the public MCP snapshot, or are they removed in
silver like other personal data? (2) keep the 2015-2023 history from `vxgw-vmky` alongside?

## 2026-11-20-td-2 [OPEN] Silver layer for 311 (R19), gold names kept as views
From the audit C3/C5. Build silver for 311: typed, deduped, keyed to conformed dimensions (date, ward, Census block,
street name from Census TIGER, request type, status), `quality` column with unit-tested rules, plausibility bounds,
silver→gold reconciliation and known-answer tests. Move the dimensions to silver. Keep every current gold table name
as a view over silver so the MCP snapshot, evals and Wheelhouse keep working. Then crime, citations, permits.
