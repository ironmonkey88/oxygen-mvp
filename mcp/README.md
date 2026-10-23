# Civic Pulse SQL (MCP server)

Read-only SQL over the Somerville gold tables for Claude, as a remote MCP
server: `https://somerville.thewongway.co/mcp` (streamable HTTP, stateless,
JSON responses). No sign-in; the data is public and personal columns are
dropped before it gets here.

Tools: `query(sql)`, `list_tables()`, `describe_table(table)`.

## How the pieces fit

| Piece | Where | What it does |
|---|---|---|
| `scripts/build_ro_snapshot.py` | host, `civic-pulse-snapshot.service` | File-copies `data/somerville.duckdb` (no DuckDB lock), builds `/srv/civic-pulse/somerville_ro.duckdb` from an explicit column allow-list, renames it into place |
| `systemd/pipeline-refresh.service.d/civic-pulse-snapshot.conf` | host | `OnSuccess=` runs the snapshot after each green `pipeline-refresh` |
| `mcp/server.py` + `Dockerfile` | container `civic-pulse-mcp` | Serves the snapshot; mounts only `/srv/civic-pulse`, read-only |
| Compose service + Caddy route | `ironmonkey88/wong-way-server` | Builds this folder at a pinned commit; `/mcp` on `127.0.0.1:18438` |

## Guards

- DuckDB `read_only=True`, `enable_external_access=false`, extensions off, `lock_configuration=true`.
- DuckDB's parser must find exactly one `SELECT` statement (`WITH` parses as `SELECT`).
- 15 s timeout (`interrupt()`), 10,000-row cap with `truncated: true` and a `note`.
- 2 queries at a time, 1 GB DuckDB memory, 256 MB temp spill.
- Per-IP token bucket (burst 30, 1/s); 64 KB request bodies (server and Caddy).
- Allowed Host headers only (DNS-rebinding protection).

## Privacy

Not in the snapshot, by Gordon's decision 2026-10-12: `fct_permits.work_description`
(names, phones, emails in free text) and `fct_citations.address`, `latitude`,
`longitude`. A new table or column appears only when it is added to `ALLOWED`
in `scripts/build_ro_snapshot.py`.

## Install (host, once)

```bash
sudo install -d -o ubuntu -g ubuntu -m 755 /srv/civic-pulse
sudo cp systemd/civic-pulse-snapshot.service /etc/systemd/system/
sudo install -d /etc/systemd/system/pipeline-refresh.service.d
sudo cp systemd/pipeline-refresh.service.d/civic-pulse-snapshot.conf /etc/systemd/system/pipeline-refresh.service.d/
sudo systemctl daemon-reload
sudo systemctl start civic-pulse-snapshot.service
```

## Updating the server

Merge here, then bump the commit in wong-way-server's `compose.yml`
(`build.context` and `image` tag). The new tag is what makes compose rebuild.
