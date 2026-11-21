# Yu Bei (預備) for Civic Pulse: adding a new source, source -> bronze -> silver

Civic Pulse's checklist for adding a source (2026-11-20, from stack-in-a-box METHODOLOGY R18-R22 and the
wong-way-warehouse version). Prefix `yb-`: orders are titled `<date>-yb-<source>` in `ORDERS.md` here. Intake happens in
chat with the `yu-bei` skill (target: Civic Pulse), usually from a pick in a Thirsty Scholar report. Scope stops at silver;
gold marts, metrics and Wheelhouse pages are separate orders. Never write into or join with Gordon's personal warehouse (R21).

Rules:
1. **Standards first.** Read this file, `CLAUDE.md`, `STANDARDS.md`, stack-in-a-box `NAMING.md` and METHODOLOGY R9-R22
   before writing anything.
2. **Ask first, build once.** The order carries the answers. If something is missing, mark it `[BLOCKED]` with one line
   per question. Don't guess.
3. **One order per source**, worked to `[DONE <commit>]`. Fixes are later commits under the same order.
4. **Copy the closest existing source** (`dlt/somerville_311_pipeline.py` for a daily incremental SODA feed).

## What the order must contain
- **Who uses it and for what question**: the stakeholder, the Thirsty Scholar question ids, the value/cost score.
- **Source**: URL and dataset id, owner, licence, how it arrives (SODA API, file, other), auth (public or the credential
  file name only).
- **Freshness**: the source's real cadence and lag; whole history or incremental; how deletes and republishes show up.
- **Grain and natural key**, timezones, geography (address / Census block / tract / ward).
- **Personal data**: names, addresses, plates, free text. Removed in silver; never in gold, the snapshot or any page.
- **Agreed names** (NAMING.md): source slug, bronze table, silver model(s), conformed dimensions it joins to.
- **Known quirks**, and a sample under `docs/<source>/` (no personal data).

## Build checklist
1. **Read the data first** (CLAUDE.md §7): column names from the data, not the API docs.
2. **`dlt/somerville_<source>_pipeline.py`**: dataset URL and id in the file, explicit write disposition, Parquet into
   `data/raw/`, row count checked against the source's `count(*)`. Append-by-load where the source republishes (R10).
3. **Bronze**: passthrough view, all source columns, dlt lineage columns, natural-key test at `severity: warn`
   (raw never fails a run, R9), **source freshness** at the real cadence, descriptions on every column.
4. **Silver** (R19): typed (`TRY_CAST`), deduped, personal data removed, keyed to conformed dimensions (date, ward,
   Census block, street), a `quality` column (ok/suspect/invalid/missing), grain test at `error`, `relationships` to
   every dimension, `accepted_values` on the quality column, every column described.
5. **Unit tests** for every rule; **plausibility** bounds for every measure.
6. **Snapshot what the source forgets** (R17): if it reports only current state, add a dbt snapshot now.
7. **Limitations**: one entry in `docs/limitations/` per quirk that survives into silver.
8. **`run.sh`**: add the pipeline (or a stated schedule) so it refreshes; the trust page picks it up.
9. **Evals**: at least two known-answer questions in `evals/questions.yaml` for the new data.

## Verify (on the box, against real data)
- Full `run.sh` green or an honest `partial`; tests recorded on /trust.
- **Raw-SQL cross-check** (R15): one row count and one total straight from bronze, compared to silver; explain any gap.
- Reply under the order: bronze and silver row counts, quality-flag counts, test results, the cross-check, what waits on
  Gordon. An honest `partial` beats a clean-looking `DONE`.
