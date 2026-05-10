---
id: oxy-build-postgres-dependency
title: oxy build requires Postgres + OXY_DATABASE_URL
severity: info
affects:
  - deploy.oxy_build
since: 2026-05-08
status: active
---

# oxy build requires Postgres + OXY_DATABASE_URL

`oxy build` (which generates the vector embeddings the Answer Agent
uses for semantic search over views) requires a running Postgres
backing store plus the `OXY_DATABASE_URL` env var pointing at it. On
this project, that's `postgresql://postgres:postgres@localhost:15432/oxy`,
served by the container that `oxy start` brings up.

This is a deploy-time and reproducibility concern, not a query-time
one. The Answer Agent does not call `oxy build` per query, so this
limitation does not auto-surface against analyst questions; the
sentinel `affects:` value `deploy.oxy_build` will not match any
ordinary SQL or view reference.

## Impact

- A fresh-box clone-and-run will fail at the `oxy build` step unless
  Postgres is up and `OXY_DATABASE_URL` is exported.
- Any one-shot `oxy validate` / `oxy run` flow without `oxy start`
  having run first will skip embedding-dependent features (semantic
  view search).
- The Answer Agent's primary path (LLM + execute_sql tool against the
  semantic context) does not require embeddings, so the runtime works
  even when `oxy build` has not been run on this box.

## Workaround

For deploy on a fresh box:

1. `oxy start` to bring up the Postgres container.
2. Export `OXY_DATABASE_URL=postgresql://postgres:postgres@localhost:15432/oxy`
   (or persist via `/etc/environment` per [SETUP.md](../../SETUP.md) §7).
3. `oxy build` to generate embeddings.
4. `oxy run agents/answer_agent.agent.yml "<question>"` — works.

## Resolution path

None planned for MVP 1. This is upstream Oxygen architecture; the
workaround is well-trodden and documented in SETUP.md.
