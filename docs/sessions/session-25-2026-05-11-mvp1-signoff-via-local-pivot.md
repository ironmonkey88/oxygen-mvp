---
session: 25
date: 2026-05-11
start_time: 18:00 ET
end_time: 17:40 ET
type: code
plan: plan-7
layers: [infra, agent, portal, docs]
work: [feature, bugfix, hardening, test, docs]
status: complete
---

## Goal

Resolve STANDARDS §5.8 row 2 (`Routes live: /chat`) — the last open box in the MVP 1 sign-off checklist — by getting a working chat agent in the SPA against Somerville 311 data, with Gordon as the user. Path-choice (from TASKS.md Next Focus at session start): option B, walk the multi-workspace onboarding wizard once, with option A (`oxy start --local`) as the fallback if B doesn't fit.

## What shipped

- **Pivot from `oxy start` (multi-workspace) to `oxy start --local` (single-workspace).** systemd unit's `ExecStart` line changed from `/home/ubuntu/.local/bin/oxy start` to `/home/ubuntu/.local/bin/oxy start --local`. Unit backed up to `/etc/systemd/system/oxy.service.bak.pre-local` before the change. `WorkingDirectory=/home/ubuntu/oxygen-mvp` makes `--local` root the workspace at the project directory.
- **SPA browser-tested end-to-end.** Gordon walked the SPA at `http://oxygen-mvp.taildee698.ts.net:3000`, asked "How many 311 requests were opened in 2024?", received 113,961 with full trust contract (execute_sql artifact + "Returned 1 row." + Citations: `main_gold.fct_311_requests` + `requests` (Airlayer view) + analyst-honest Known limitations section recognizing 2024 as a completed historical year and confirming no registry entries applied).
- **Reboot test passed.** `sudo reboot` → oxy systemd unit came back active 11 seconds after kernel up. oxy-postgres container recreated against the persistent `oxy-postgres-data` volume. CLI agent regression 113,961 post-reboot.
- **STANDARDS §5.8 row 2 flipped `[ ]` → `[x]`** with inline evidence. §6 §5.8 roll-up 5/6 → 6/6. §6 header note added: "MVP 1 signed off 2026-05-11."
- **LOG.md Current Status flipped to MVP 2.** Active MVP line, Phase line, Last Updated line all updated. Active Decisions row added for the sign-off + pivot rationale. Active Blockers replaced with "no active blockers" note plus the sign-off arc summary.
- **CLAUDE.md MVP Sequence** marks MVP 1 signed off 2026-05-11 (active) and MVP 2 active.
- **TASKS.md Sign-off Status MVP 1** chat-UI row flipped `[!]` → `[x]` with browser-test evidence. Next Focus section replaced with MVP 2 plan-scoping open questions.
- **ARCHITECTURE.md Process management** line updated to specify `--local` mode; new "Multi-workspace mode deferred to MVP 4" subsection added with the customer-feedback context.
- **SETUP.md §11** systemd unit ExecStart updated to `oxy start --local`; new "Why `--local`" + "Security note on `--local`" paragraphs added.

## Decisions

- **Pivot from B to A mid-execution.** Path-choice B (walk the multi-workspace wizard) at session start, abandoned after Gordon hit the wizard's DuckDB connection step. The wizard's DuckDB step only accepts CSV/Parquet uploads into a fresh `.db/` directory inside the workspace, producing flat tables named after the uploaded filenames. The project's stack — semantic layer, dbt models, agent context, limitations registry — all references `main_bronze.raw_311_requests` / `main_gold.fct_311_requests` (the medallion schema). The wizard's upload path would have produced a parallel DuckDB with a flat structure incompatible with the existing configs. Switching to `oxy start --local` (path-choice A) reads `config.yml` and the workspace directly with no wizard, satisfying the deployment shape without rebuilding the project.
- **Multi-workspace migration deferred to MVP 4.** Originally the plan was to keep multi-workspace mode running from MVP 1 forward, so MVP 4's sharing surfaces wouldn't require a migration. The wizard incompatibility closes that path. MVP 4 will need to return to multi-workspace mode and either: (a) use an Oxygen wizard with an "existing DuckDB" option by then, (b) build a tool that creates the workspace state programmatically, or (c) re-ingest from raw Parquet through the wizard upload, accepting the SPA-side DuckDB becomes a separate copy. None of this is MVP 1's problem; parked for MVP 4 scoping.
- **Brief's `oxy serve --local <path>` syntax was wrong.** The brief Gordon paste-handed-off specified `ExecStart=oxy serve --local /home/ubuntu/oxygen-mvp`. The CLI rejected this: `error: unexpected argument '/home/ubuntu/oxygen-mvp' found`. The actual flag form is `--local` with no value; the workspace path comes from `WorkingDirectory=`. Also, `oxy serve` requires `OXY_DATABASE_URL` reachable — it doesn't manage postgres itself. The correct command is **`oxy start --local`**, which both manages Docker postgres lifecycle and enables local mode. Discovered by reading `oxy serve --help` after the first systemd start failed; confirmed against `oxy start --help`. The dev-update doc has been superseded by what shipped.
- **Skipped saving SPA screenshots to repo.** Gordon shared the SPA workspace + 2024-question-reply screenshots in chat. The dev-update brief specified saving them to `docs/sessions/session-25-screenshots/`; not done because Code doesn't have the image files locally — they live in the chat transcript only. Verifiable on demand by re-asking the question in the SPA. Not blocking — the trust contract output is reproducible.

## Issues encountered

### Multi-workspace onboarding wizard incompatible with existing populated DuckDB

The wizard's DuckDB connection step (Step 2 of 5: LLM Provider → Data Warehouse → Schema Discovery → Table Selection → Build Workspace) offers four warehouse types (Snowflake, ClickHouse, BigQuery, DuckDB). Selecting DuckDB presents only an upload zone — no file-path input, no "I have an existing database" toggle, no advanced settings. Uploaded CSV/Parquet files land in a fresh `.db/` directory inside the workspace, becoming flat tables named after the filename. There is no path to skip the warehouse step.

For this project (1.17M rows, full medallion architecture, 4 Airlayer views + 1 topic, working Answer Agent), uploading raw Parquet would produce a parallel DuckDB whose table structure doesn't match what the semantic layer + agent + dbt models all reference. Pushing through would require rewriting the entire downstream stack — that's not a wizard walk, it's a project rebuild.

### Brief's command syntax was wrong; corrected via `--help` inspection

The dev-update doc specified `ExecStart=oxy serve --local /home/ubuntu/oxygen-mvp`. First systemd start after the change failed with `error: unexpected argument '/home/ubuntu/oxygen-mvp' found`. Inspection of `oxy serve --help` and `oxy start --help` revealed: `--local` is a flag (no value), the workspace comes from `WorkingDirectory=`/CWD, and `oxy serve` (without `start`) requires `OXY_DATABASE_URL` reachable independently. The corrected command is `oxy start --local`, which manages Docker postgres + enables local mode in one invocation.

## Verification evidence

```
$ ssh oxygen-mvp 'sudo systemctl status oxy --no-pager | head -10'
● oxy.service - Oxygen server
     Loaded: loaded (/etc/systemd/system/oxy.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-05-11 21:33:46 UTC; 11s ago
     CGroup: /system.slice/oxy.service
             └─1110 /home/ubuntu/.local/bin/oxy start --local

$ ssh oxygen-mvp 'curl -sI http://localhost:3000 | head -1'
HTTP/1.1 200 OK

$ ssh oxygen-mvp 'docker ps --filter "name=oxy-postgres" --format "{{.Names}} {{.Status}}"'
oxy-postgres Up 10 seconds

$ ssh oxygen-mvp 'oxy run agents/answer_agent.agent.yml \
                  "How many 311 requests were opened in 2024?"'
| 113961         |
Returned 1 row.
**Answer.** There were 113,961 311 requests opened in 2024, based on the
            `date_created_dt` field in the fact table. This is a full-year
            count for calendar year 2024.

# SPA browser test (Gordon, screenshots in chat transcript):
# - Workspace name "local" — confirms --local mode
# - answer_agent auto-registered and selected
# - "How many 311 requests were opened in 2024?" returned 113,961
# - Trust contract structurally complete:
#   - execute_sql tool artifact (click to view)
#   - "Returned 1 row." line
#   - Answer prose with the number
#   - Citations: main_gold.fct_311_requests, requests (Airlayer view)
#   - Known limitations: correctly notes no registry entries apply
```

## Customer-feedback finding for Oxy

**The multi-workspace onboarding wizard has no path for connecting to an existing populated DuckDB file.** The DuckDB connection step accepts only CSV/Parquet uploads into a fresh `.db/` directory; tables get flat names matching the uploaded filenames. Any user coming to Oxygen with a pre-built warehouse (a dbt project's output, an existing DuckDB, a SQL pipeline producing schema-organized tables) cannot use multi-workspace mode without re-ingesting through the upload zone and rewriting downstream configs to match the resulting table structure.

**Workaround:** `oxy start --local`, which bypasses the wizard and reads `config.yml` + the workspace directly. Single-workspace, guest-auth mode — fine for single-user demos, not fine for multi-tenant evaluation surfaces.

**Recommendation:** add a "connect to existing DuckDB file" option to the DuckDB warehouse connection step, taking a file path on disk. The same need likely applies to BigQuery/Snowflake/ClickHouse for users with pre-existing semantic layouts — schema-discovery should be a path, not just an upload zone.

**Strategic relevance to Oxy:** the wizard's design assumes a user persona that's different from the analyst persona MVP.md commits to — the analyst comes to Oxygen with the data already in hand (in our project's case, 1.17M rows of Somerville 311 already curated through dbt). Closing this gap broadens Oxygen's "first 30 minutes" experience for the dbt+DuckDB-aware user segment, which overlaps substantially with the modern-data-stack analyst Oxy is pitching against.

## Next action

MVP 2 plan-scoping. The first Code session in MVP 2 should: (1) verify Builder Agent is reachable in the SPA's `--local` mode (BUILD.md §7 names Builder Agent as the construction interface from MVP 2 forward); (2) scope the first Data App per the MVP.md Working Backwards example (service equity across neighborhoods, four investigative angles); (3) decide whether to ship MVP 1.5 (public chat via nginx Basic Auth, plan saved at [`docs/plans/mvp-1.5-public-chat-via-nginx-basic-auth.md`](../plans/mvp-1.5-public-chat-via-nginx-basic-auth.md)) before, alongside, or after the MVP 2 work. See TASKS.md "Next Focus" for the open scoping questions.
