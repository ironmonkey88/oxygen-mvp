"""Civic Pulse SQL: a read-only MCP server over the Somerville gold tables.

Serves /data/somerville_ro.duckdb, a snapshot built by
scripts/build_ro_snapshot.py. It never sees the production warehouse: the
container mounts only the snapshot folder, read-only.

Read-only is enforced twice: DuckDB opens the file with read_only=True and
external access off (no files, no httpfs, no ATTACH, no extension loads), and
DuckDB's own parser must find exactly one SELECT statement (WITH ... SELECT
parses as SELECT). Each query gets a fresh connection, so a new snapshot is
picked up without a restart, a 15 s timeout and a 10,000-row cap.

Public with no sign-in, so a per-IP rate limit sits in front of every request.
"""
import asyncio
import datetime as dt
import decimal
import os
import threading
import time
import uuid
from typing import Any

import duckdb
import uvicorn
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings

DB_PATH = os.environ.get("CIVIC_PULSE_DB", "/data/somerville_ro.duckdb")
PUBLIC_HOST = os.environ.get("CIVIC_PULSE_HOST", "somerville.thewongway.co")
SCHEMA = "main_gold"
QUERY_TIMEOUT_S = 15
MAX_ROWS = 10_000
MAX_SQL_CHARS = 20_000
MAX_BODY_BYTES = 64 * 1024
RATE_BURST = 30           # requests a client may send at once
RATE_PER_SECOND = 1.0     # sustained requests per second per client
CONCURRENT_QUERIES = 2    # the box has 2 cores and runs the pipeline too

DUCKDB_CONFIG = {
    "enable_external_access": False,
    "autoload_known_extensions": False,
    "autoinstall_known_extensions": False,
    "allow_community_extensions": False,
    "threads": 2,
    "memory_limit": "1GB",
    "temp_directory": "/tmp/duckdb",
    "max_temp_directory_size": "256MB",
}

server = MCPServer(
    name="civic-pulse-sql",
    title="Somerville Civic Pulse SQL",
    instructions=(
        "Read-only SQL (DuckDB dialect) over City of Somerville, MA open data: 311 requests, "
        "crime incidents, traffic citations, building permits, the happiness survey and city KPIs. "
        f"Tables live in schema {SCHEMA}, which is the default, so `SELECT ... FROM fct_311_requests` works. "
        "Start with list_tables, then describe_table. One SELECT or WITH statement per call; "
        f"{QUERY_TIMEOUT_S} s timeout; at most {MAX_ROWS:,} rows come back, so aggregate in SQL. "
        "Data refreshes daily; main_gold.snapshot_info says when. Some columns are withheld for "
        "privacy (permit work descriptions; citation street addresses and coordinates)."
    ),
)
_query_slots = asyncio.Semaphore(CONCURRENT_QUERIES)


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (uuid.UUID, dt.timedelta)):
        return str(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return str(value)


def _check_sql(sql: str) -> None:
    if not sql or not sql.strip():
        raise ToolError("sql is empty")
    if len(sql) > MAX_SQL_CHARS:
        raise ToolError(f"sql is longer than {MAX_SQL_CHARS} characters")
    try:
        statements = duckdb.extract_statements(sql)
    except duckdb.Error as exc:
        raise ToolError(f"could not parse sql: {exc}") from exc
    if len(statements) != 1:
        raise ToolError(f"send exactly one statement (got {len(statements)})")
    if statements[0].type != duckdb.StatementType.SELECT:
        raise ToolError(f"only SELECT / WITH queries are allowed (got {statements[0].type.name})")


def _run(sql: str, params: list[Any] | None = None, max_rows: int = MAX_ROWS) -> dict[str, Any]:
    """Run one read-only query on a fresh connection, with timeout and row cap."""
    if not os.path.exists(DB_PATH):
        raise ToolError("the data snapshot is not available yet; try again later")
    con = duckdb.connect(DB_PATH, read_only=True, config=DUCKDB_CONFIG)
    con.execute(f"SET search_path = '{SCHEMA}'")
    con.execute("SET lock_configuration = true")  # nothing below can SET the config back
    timed_out = threading.Event()

    def _interrupt() -> None:
        timed_out.set()
        con.interrupt()

    timer = threading.Timer(QUERY_TIMEOUT_S, _interrupt)
    started = time.monotonic()
    timer.start()
    try:
        cur = con.execute(sql, params or [])
        columns = [d[0] for d in cur.description]
        fetched = cur.fetchmany(max_rows + 1)
    except duckdb.Error as exc:
        if timed_out.is_set():
            raise ToolError(f"query timed out after {QUERY_TIMEOUT_S} s and was cancelled") from exc
        raise ToolError(f"{type(exc).__name__}: {exc}") from exc
    finally:
        timer.cancel()
        con.close()

    truncated = len(fetched) > max_rows
    rows = [dict(zip(columns, (_jsonable(v) for v in r))) for r in fetched[:max_rows]]
    result: dict[str, Any] = {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "truncated": truncated,
        "elapsed_ms": round((time.monotonic() - started) * 1000),
    }
    if truncated:
        result["note"] = f"Result truncated to the first {max_rows:,} rows. Aggregate or add LIMIT."
    return result


async def _guarded(sql: str, params: list[Any] | None = None) -> dict[str, Any]:
    async with _query_slots:
        return await asyncio.to_thread(_run, sql, params)


@server.tool()
async def query(sql: str) -> dict[str, Any]:
    """Run one read-only DuckDB SELECT (or WITH ... SELECT) against the Somerville gold tables.

    Returns {columns, rows: [{column: value}], row_count, truncated, elapsed_ms, note?}.
    At most 10,000 rows; 15 s timeout. Dates and timestamps come back as ISO-8601 strings.
    """
    _check_sql(sql)
    return await _guarded(sql)


@server.tool()
async def list_tables() -> dict[str, Any]:
    """List every table with its row count, column count and a one-line kind (fact or dimension)."""
    return await _guarded(
        "SELECT t.table_name, t.estimated_size AS row_count, t.column_count, "
        "CASE WHEN t.table_name LIKE 'fct_%' THEN 'fact' WHEN t.table_name LIKE 'dim_%' "
        "THEN 'dimension' ELSE 'metadata' END AS kind "
        "FROM duckdb_tables() t WHERE t.schema_name = ? ORDER BY kind, t.table_name",
        [SCHEMA],
    )


@server.tool()
async def describe_table(table: str) -> dict[str, Any]:
    """Columns of one table (name, type, nullable) plus its exact row count. Example: describe_table("fct_311_requests")."""
    cols = await _guarded(
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_schema = ? AND table_name = ? ORDER BY ordinal_position",
        [SCHEMA, table],
    )
    if not cols["rows"]:
        raise ToolError(f"no table {table!r} in {SCHEMA}; call list_tables")
    quoted = '"' + table.replace('"', '""') + '"'
    count = await _guarded(f"SELECT count(*) AS n FROM {SCHEMA}.{quoted}")
    return {"table": f"{SCHEMA}.{table}", "row_count": count["rows"][0]["n"], "columns": cols["rows"]}


class RateLimit:
    """Per-client token bucket. Caddy sets X-Forwarded-For to the real client IP."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self.buckets: dict[str, tuple[float, float]] = {}

    def _client(self, scope: dict[str, Any]) -> str:
        for name, value in scope.get("headers", []):
            if name == b"x-forwarded-for":
                return value.decode("latin-1").split(",")[0].strip()
        return (scope.get("client") or ("unknown", 0))[0]

    def _allow(self, client: str) -> bool:
        now = time.monotonic()
        if len(self.buckets) > 10_000:
            self.buckets = {k: v for k, v in self.buckets.items() if now - v[1] < 600}
        tokens, last = self.buckets.get(client, (RATE_BURST, now))
        tokens = min(RATE_BURST, tokens + (now - last) * RATE_PER_SECOND)
        if tokens < 1:
            self.buckets[client] = (tokens, now)
            return False
        self.buckets[client] = (tokens - 1, now)
        return True

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] == "http" and not self._allow(self._client(scope)):
            await send({"type": "http.response.start", "status": 429,
                        "headers": [(b"content-type", b"text/plain"), (b"retry-after", b"5")]})
            await send({"type": "http.response.body", "body": b"rate limited; slow down\n"})
            return
        await self.app(scope, receive, send)


app = RateLimit(server.streamable_http_app(
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
    max_request_body_size=MAX_BODY_BYTES,
    host="0.0.0.0",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[PUBLIC_HOST, "127.0.0.1:*", "localhost:*"],
        allowed_origins=[f"https://{PUBLIC_HOST}", "https://claude.ai", "https://*.claude.ai",
                         "http://127.0.0.1:*", "http://localhost:*"],
    ),
))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")),
                proxy_headers=False, server_header=False, log_level="info")
