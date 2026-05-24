---
id: chat-activity-local-state-only
title: Chat-activity tracking is whatever the local oxy-postgres container holds
severity: advisory
affects:
  - chat
  - admin_dashboard
  - fct_chat_activity_raw
  - panel-c1
  - panel-c2
since: 2026-05-23
status: active
---

# Chat-activity tracking limited to local-state contents

## The finding

The DBA dashboard's chat-activity panels (C1: conversations / messages /
sessions / sparkline; C2: token usage + Anthropic-spend proxy) read from
`main_admin.fct_chat_activity_raw`, which is loaded from the
`oxy-postgres` Docker container that `oxy start --local` provisions on
EC2. Per Plan 38 Phase A1's schema inspection
(`docs/design-reviews/chat-state-schema-inspection-2026-05-22.md`),
all chat content — messages, threads, token attribution — lives in
that container's Postgres instance.

## What this means in practice

- **The dashboard's chat numbers reflect only what's currently in the
  local container.** If the container is recreated (e.g.,
  `docker rm oxy-postgres && docker run ...` during an Oxygen
  re-install), its data is gone and the dashboard's C1/C2 panels reset
  to zero. The container's volume should be persistent across normal
  restarts, but a deliberate teardown loses chat history.
- **`--local` mode doesn't sync chat state anywhere.** Multi-workspace
  Oxygen deployments would route chat through the same Postgres but
  also through Oxygen Cloud's persistence layer; in `--local` the local
  Postgres is the only copy. There's no off-EC2 backup of chat state
  today; if the EC2 instance is replaced the chat history doesn't
  carry over.
- **The C2 token-spend numbers are a project-side proxy, not Anthropic's
  ground truth.** The `messages.input_tokens` + `messages.output_tokens`
  columns are populated by Oxygen at message-send time, presumably from
  the API response's `usage` block. They should match what Anthropic
  bills for Code-issued conversations against the Answer Agent, but
  this hasn't been cross-checked against the Anthropic console.
- **Container teardown is the load-bearing risk.** If chat-state goes
  away, the C1 sparkline goes flat at zero with no banner explaining
  why. v1.1 should consider a "container restart detected"
  data-unavailable annotation in the panel.

## Mitigation

Not actively mitigated. The realistic mitigation is "don't tear down
the oxy-postgres container without thinking about it" — a one-time
note, not a load-bearing process control. If chat history becomes
operationally important (e.g., audit / compliance), the right move is
to add a backup-to-S3 step to systemd's pipeline-refresh cycle.

## Verification

The limitation surfaces when:

```sh
docker exec oxy-postgres psql -U postgres -d oxy -c "SELECT COUNT(*) FROM messages"
```

returns substantially fewer rows than the dashboard's all-time message
count would suggest, or when the `MIN(created_at)` against `messages` is
recent (indicating a container reset). Cross-check with
`docker inspect oxy-postgres` to see when the container was created.

## Related

- Schema inspection: [`docs/design-reviews/chat-state-schema-inspection-2026-05-22.md`](../design-reviews/chat-state-schema-inspection-2026-05-22.md)
- Loader: [`dlt/oxy_chat_activity_pipeline.py`](../../dlt/oxy_chat_activity_pipeline.py)
- DBA dashboard design: [`docs/dba-dashboard-design-2026-05-17.md`](../dba-dashboard-design-2026-05-17.md) §10
