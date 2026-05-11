# Oxygen Docs — Local Mirror

Offline mirror of [oxy.tech/docs](https://oxy.tech/docs) — fetched 2026-05-11 from the canonical `.md` URLs via the AI-friendly index at https://oxy.tech/docs/llms.txt.

**Why this exists:** so this project's Code (and Claude Chat, via project knowledge) can `grep`/read Oxygen documentation without hitting the network, and so that snapshot-time content is version-controlled alongside the code that depends on it. When Oxygen ships a release that changes behavior, this mirror lags until refreshed — see "Refreshing" below.

**Provenance:** every file in this tree is a verbatim copy of the corresponding `.md` URL on oxy.tech, with no modifications. The directory structure mirrors the URL path after `/docs/`. The link rewrite for relative paths inside each page is not done — image and inter-page links resolve to oxy.tech, not local files.

## Structure

```
docs/oxygen-docs/
├── README.md            (this file)
├── llms.txt             (frozen index from oxy.tech)
├── guide/
│   ├── welcome.md
│   ├── prerequisites.md
│   ├── quickstart.md
│   ├── getting-started-agents/   (4 pages)
│   ├── learn-about-oxy/          (21 pages incl. semantic-layer subdir)
│   ├── api-keys/, authentication/ (5 pages)
│   ├── deployment/               (17 pages incl. reference-architecture)
│   ├── integrations/             (17 pages: data-sources, models, apps, a2a, v0)
│   ├── mcp-server/, migration/   (2 pages)
│   └── reference/                (7 pages: oxy-commands, env-variables, etc.)
└── changelog/                    (~42 dated weekly entries, 2025-04-03 → 2026-05-07)
```

## Refreshing

```bash
./scripts/fetch_oxygen_docs.sh
```

Curl-based, follows redirects, idempotent (re-fetch overwrites existing files). The URL list is frozen inline in the script — if oxy.tech adds new pages, update the list from `https://oxy.tech/docs/llms.txt` before re-running. Then commit any changes.

## Reading paths

For "where do I learn X?" questions:

| Topic | Start here |
|-------|------------|
| What Oxygen is | [guide/welcome.md](guide/welcome.md) |
| Setup from scratch | [guide/prerequisites.md](guide/prerequisites.md) → [guide/quickstart.md](guide/quickstart.md) |
| Writing an agent | [guide/getting-started-agents/](guide/getting-started-agents/) |
| Semantic layer concepts | [guide/learn-about-oxy/semantic-layer.md](guide/learn-about-oxy/semantic-layer.md) → [semantic-layer/](guide/learn-about-oxy/semantic-layer/) |
| Routing agents | [guide/learn-about-oxy/routing-agents.md](guide/learn-about-oxy/routing-agents.md) |
| Data apps (MVP 2) | [guide/learn-about-oxy/data-apps.md](guide/learn-about-oxy/data-apps.md) |
| Workflows | [guide/learn-about-oxy/workflows.md](guide/learn-about-oxy/workflows.md) |
| Config file shape | [guide/learn-about-oxy/config.md](guide/learn-about-oxy/config.md) |
| `oxy` CLI subcommands | [guide/reference/oxy-commands.md](guide/reference/oxy-commands.md) |
| `oxy start` behavior | [guide/reference/oxy-start.md](guide/reference/oxy-start.md) |
| Env vars Oxygen reads | [guide/reference/environment-variables.md](guide/reference/environment-variables.md) |
| AWS deployment recipes | [guide/deployment/hands-on/aws.md](guide/deployment/hands-on/aws.md) + [guide/deployment/reference-architecture/aws/](guide/deployment/reference-architecture/aws/) |
| DuckDB integration | [guide/integrations/data-sources/duckdb.md](guide/integrations/data-sources/duckdb.md) |
| MCP server usage | [guide/mcp-server/mcp-usage.md](guide/mcp-server/mcp-usage.md) |
| Release history | [changelog/](changelog/) (chronological, oldest first) |

## For Claude Chat

This directory lives on `origin/main` after commit. To pull it into Chat project knowledge:
1. Use Chat's "Add files" / "Connect repository" workflow on the `oxy-hq` / `ironmonkey88` GitHub source.
2. Or paste `https://github.com/ironmonkey88/oxygen-mvp/tree/main/docs/oxygen-docs` as a project knowledge source.
3. Or for one-off context, paste a specific file path like `docs/oxygen-docs/guide/learn-about-oxy/agents.md` into a Chat turn.

Chat and Code see the same mirror because both read from the same `origin/main` snapshot.
