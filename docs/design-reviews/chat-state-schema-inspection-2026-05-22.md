# Chat-state schema inspection — Plan 38 Phase A1

_Inspected 2026-05-23 23:18 ET by Code on EC2 (Session 63). This document is Phase A1's output per the Plan 38 prompt; commits ahead of any loader work to freeze the schema in writing before any design assumption hardens around an unverified shape._

## Where chat state lives

The Oxygen `--local` deployment on EC2 **does NOT** keep chat state in `.oxy_state/` (which holds only per-execution app result snapshots, gitignored per Plan 34 B2). It also does NOT use `~/.local/share/oxy/observability.duckdb` for chat content (that file holds telemetry / run observability, separate concern).

**Chat state lives in a Docker-managed Postgres container** named `oxy-postgres`, image `postgres:18-alpine`, exposed on `0.0.0.0:15432→5432/tcp`. Connection string is the standard `OXY_DATABASE_URL` documented in CLAUDE.md "LLM Configuration": `postgresql://postgres:postgres@localhost:15432/oxy`. This is the same Postgres that `oxy start --local` provisions and that `oxy build` / `oxy serve` connect to. In `--local` mode the schema is fully provisioned but most rows are absent — single-tenant, single-user, no multi-workspace data.

## Full Postgres schema (51 tables)

`docker exec oxy-postgres psql -U postgres -d oxy -c "\dt"` returns **51 tables**. Categorized:

- **Chat core (4):** `messages`, `threads`, `users`, `artifacts`
- **Agentic runtime (5):** `agentic_runs`, `agentic_run_events`, `agentic_run_suspensions`, `agentic_task_outcomes`, `agentic_task_queue`, `agentic_workflow_state`
- **Tenant model (8):** `organizations`, `org_invitations`, `org_members`, `org_secrets`, `workspaces`, `workspace_members`, `git_namespaces`, `github_accounts`
- **A2A (agent-to-agent) (4):** `a2a_artifacts`, `a2a_messages`, `a2a_tasks`, `a2a_task_status`
- **Slack integration (8):** `slack_channel_defaults`, `slack_installations`, `slack_oauth_states`, `slack_seen_events`, `slack_threads`, `slack_user_links`, `slack_user_preferences`, plus one more
- **Observability (5):** `observability_intent_classifications`, `observability_intent_clusters`, `observability_metric_usage`, `observability_spans`, plus `logs`
- **Testing (5):** `test_case_human_verdicts`, `test_project_runs`, `test_run_cases`, `test_run_sequences`, `test_runs`
- **Secrets / config (5):** `api_keys`, `secrets`, `settings`, `checkpoints`, `analytics_run_extensions`
- **Migrations (4):** `seaql_migrations`, `seaql_migrations_analytics`, `seaql_migrations_orchestrator`, `seaql_migrations_workflow`
- **Misc (3):** `runs`, `run_sequences`, `tasks`

This is **substantially richer than the design doc anticipated**. Design doc §12.1 framed the open question as "a `--local` deployment vs. multi-workspace will have different shapes" — the actual finding is the schema is **identical** between modes; what differs is the data within (rows).

## Row counts in `--local` mode (as of 2026-05-23 23:18 ET)

```
 messages | threads | users | workspaces | orgs | agentic_runs | runs | logs 
----------+---------+-------+------------+------+--------------+------+------
      102 |      16 |     1 |          1 |    1 |            5 |    0 |   31
```

- 102 chat messages spread across 16 threads (avg ~6.4 messages/thread)
- Single tenant (1 org / 1 workspace / 1 user)
- 5 agentic runs (presumably from `oxy run` invocations)
- 0 `runs` table rows; 31 `logs` entries
- 8 Slack tables all empty (Slack not connected in `--local`)
- A2A tables all empty
- Test tables all empty

The data spans **2026-05-11 → 2026-05-22** (11 days). Earliest message timestamp aligns with the Sonnet 4.6 → Opus 4.7 migration date (Plan 1.5).

## `messages` table schema (the C1 panel's primary source)

```
Column          Type                       Nullable  Default
id              uuid                       not null  
content         text                       not null  
is_human        boolean                    not null  
thread_id       uuid                       not null  
created_at      timestamp with time zone   not null  CURRENT_TIMESTAMP
input_tokens    integer                    not null  0
output_tokens   integer                    not null  0
```

PK: `id`. FK: `thread_id → threads(id) ON DELETE CASCADE`. Referenced by `artifacts(message_id)`.

**`content` is plain text — not encrypted.** Confirmed by sampling 3 most-recent messages: content reads as cleartext human prompts ("format v1 and v2 as markdown for easy copy and paste") and assistant responses ("Here are both reports formatted as clean, copy-paste-ready markdown..."). The `encryption_key.txt` file under `~/.local/share/oxy/` is presumably for the `secrets` / `org_secrets` tables, not message bodies.

**`input_tokens` + `output_tokens` are populated.** This is the big finding. Sample row:

| `is_human` | `input_tokens` | `output_tokens` | `content_sample` |
|---|---|---|---|
| `f` (assistant) | 60,215 | 7,427 | "Here are both reports formatted as clean, copy-paste-ready markdown..." |
| `t` (human) | 0 | 0 | "format v1 and v2 as markdown for easy copy and paste" |
| `f` (assistant) | 209,635 | 7,155 | "I'll dig into ticket-type segmentation with SPC, then bring in crime stats..." |

Human messages have 0/0 (they don't consume API tokens; the input is their prompt text, the model's input is what gets the token-count attribution). Assistant messages have real input/output token counts attributed to whichever model the agent uses (Opus 4.7 per `config.yml`).

**Aggregate so far (all 102 messages, 11 days):**

```
total_in | total_out | opus_in_usd | opus_out_usd 
---------+-----------+-------------+--------------
 2511668 |     79651 |       37.68 |         5.97
```

At Opus 4.7 prices ($15/M input, $75/M output), that's **~$43.65 total spend** on the chat agent across 11 days. **This data was supposedly inaccessible per the design doc's v2 scope-cut** ("Anthropic Admin API blocked the original scope" — design doc §0). It turns out the data lives in chat-state, not in any Admin API surface.

## `threads` table schema (sessions)

```
Column          Type                       Nullable  Default
id              uuid                       not null
title           varchar                    not null
input           varchar                    not null
output          varchar                    not null
source          varchar                    not null
created_at      timestamp with time zone   not null  CURRENT_TIMESTAMP
references      text                       not null
source_type     varchar                    not null  ''
user_id         uuid                       nullable
is_processing   boolean                    not null  false
project_id      uuid                       not null  '00000000-0000-0000-0000-000000000000'
sandbox_info    json                       nullable
```

Sample rows:

| `title_sample` | `source` | `source_type` | `created_at` |
|---|---|---|---|
| "look at tickets year over year and run..." | `agents/answer_agent.agent.yml` | `agent` | 2026-05-22 21:34 |
| "what's the most recent data in the database" | `agents/answer_agent.agent.yml` | `agent` | 2026-05-21 20:13 |
| "How many 311 calls happened in 2025" | `agents/answer_agent.agent.yml` | `agent` | 2026-05-17 12:27 |

`source` identifies which agent serves the thread. All 3 sampled threads point at `agents/answer_agent.agent.yml` — the project's primary chat-facing agent. The `references` column likely holds the citations Oxygen renders as trust contract output; not inspected at row-level.

`title`, `input`, `output` are all plain-text varchar — not encrypted. The `input` column captures the initial human prompt; `output` captures the agent's final response synopsis.

## Halt-condition triage against §A2

The prompt named three halt conditions for A1. Triaged:

1. **"No chat-state store found."** ✗ NOT TRIGGERED — store found (Postgres `oxy` database, ~52 tables, populated with real data).

2. **"Schema is significantly more complex than the design doc anticipated."** ⚠️ PARTIALLY TRIGGERED — the *full* schema is 51 tables vs. the design doc's implicit ~2-3-table mental model. BUT the *subset* needed for C1 panel (just `messages` + `threads`) is exactly the simple shape the design doc anticipated. The prompt's halt-options (drop session-count, infer sessions from time gaps, defer C1) don't apply because sessions DO exist cleanly via `threads.id`. So this halt fires "soft" — it's a structural surprise but doesn't break C1 design.

3. **"Schema reveals data the design doc didn't plan for and that matters."** ✅ TRIGGERED — `messages.input_tokens` + `messages.output_tokens` are populated and unlock an actual Anthropic-spend cost-proxy that the design doc explicitly cut from v1 ("Anthropic Admin API blocked the original scope"). The data was always there; the design doc's v2 scope cut was over-conservative. The prompt names "Anthropic API spend buried in metadata" verbatim as a §A3 halt trigger.

## Implications for Phase A loader design

The minimal loader that satisfies design doc §3 Group C's C1 panel:

```sql
SELECT id, thread_id, is_human, created_at, input_tokens, output_tokens
FROM messages
```

Plus:

```sql
SELECT id, title, source, source_type, created_at
FROM threads
```

That's 7 + 5 = 12 columns to land in `main_admin.fct_chat_activity_raw` (plus a `loaded_at` audit column). All plain-text. Idempotent on (`messages.id`, `threads.id`) UUIDs.

**Token-cost panel scope decision is the gating question for proceeding to A3:** does Plan 38's v1 include a token-spend panel (deviating from design doc §0's "cost panels cut" decision) or stay strict to design doc scope (load tokens to bronze but don't surface in v1 UI)?

## Open decisions surfaced to Chat (halt-and-surface)

1. **Token-spend panel scope.** Three options enumerated below.
2. **Loader source.** Postgres-via-Docker-exec or Postgres-direct-via-Python (psycopg2)? The latter is cleaner for dlt-style ingestion; needs psycopg2 installed in the venv. Connection target is `localhost:15432` from EC2 (Docker port-forwarded).
3. **Idempotency strategy.** Merge on UUIDs (clean) or upsert on `(thread_id, created_at)` (also clean given UUIDs but slightly redundant). Pick at A3.
4. **Adjacent-table loading.** Load only `messages` + `threads`, or also `agentic_runs` / `logs` for future panels? Recommendation: minimal load now (just 2 tables), expand at v1.1 if needed.

## Status

**HALT-AND-SURFACE at A1, pending Chat decision on token-spend scope.** Schema inspection committed; loader (A3), dbt model (A4), and verification (A5) wait on the v1-vs-v1.1 scope decision. Phase B (dashboard generator) gated on Phase A completion — does not proceed.

Track C tidy-day items are independent of the Phase A halt; Code's call on whether to ride them alongside or split into a follow-up PR per the prompt's "Out of scope" clause on Phase B halts.
