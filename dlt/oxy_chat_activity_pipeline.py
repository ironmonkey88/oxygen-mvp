"""Oxygen chat-activity ingestion pipeline.

Reads from the `oxy-postgres` Docker container that `oxy start --local`
provisions (50+ tables; multi-tenant schema, mostly empty in --local mode
beyond 1 org / 1 workspace / 1 user). Joins `messages` × `threads` at
message grain and lands the denormalized result into
`main_admin.fct_chat_activity_raw` via dlt merge-on-`message_id`.

Per Plan 38 Phase A1's schema inspection
(docs/design-reviews/chat-state-schema-inspection-2026-05-22.md):
- `messages.content` is plain text (not encrypted)
- `messages.input_tokens` + `messages.output_tokens` are populated and
  unlock Anthropic-spend tracking that the design doc had cut from v1
  as "Admin API blocked"
- `threads.title` + `threads.input` + `threads.output` are plain text
  varchar; `references` (text) holds citations

Tables produced in `main_admin`:
  - fct_chat_activity_raw (dlt-owned, merge target, one row per message)
  - _dlt_pipeline_state, _dlt_loads, _dlt_version (dlt metadata)

Audit columns injected per row:
  - _extracted_at      TIMESTAMP   when this run extracted the row
  - _extracted_run_id  TEXT (ULID) which pipeline run produced this state
  - _source_endpoint   TEXT        Postgres URL the row came from

Idempotency: merge on `message_id` (UUID PK on `messages`). Running twice
doesn't double-count. Re-runs DO pick up newly-added messages from chat
activity since the last run and DO update token-count attribution for any
in-flight message that finished between runs (unlikely in --local mode but
correct behavior).

Usage:
    python dlt/oxy_chat_activity_pipeline.py [RUN_ID]
"""
import sys
from datetime import datetime, timezone
from typing import Iterator

import dlt
import psycopg2
from ulid import ULID

DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"
PG_URL = "postgresql://postgres:postgres@localhost:15432/oxy"
SOURCE_ENDPOINT = "postgresql://localhost:15432/oxy:public.messages+threads"


JOIN_QUERY = """
    SELECT
        m.id            AS message_id,
        m.thread_id     AS thread_id,
        m.is_human      AS is_human,
        m.content       AS content,
        m.created_at    AS message_created_at,
        m.input_tokens  AS input_tokens,
        m.output_tokens AS output_tokens,
        t.title         AS thread_title,
        t.source        AS thread_source,
        t.source_type   AS thread_source_type,
        t.user_id       AS thread_user_id,
        t.created_at    AS thread_created_at
    FROM messages m
    JOIN threads t ON m.thread_id = t.id
"""


def fetch_chat_activity(run_id: str, extracted_at: datetime) -> Iterator[dict]:
    """Query the oxy-postgres join + inject audit columns per row."""
    conn = psycopg2.connect(PG_URL)
    try:
        cur = conn.cursor()
        cur.execute(JOIN_QUERY)
        cols = [desc[0] for desc in cur.description]
        count = 0
        for row in cur:
            d = dict(zip(cols, row))
            # UUIDs as str so duckdb stores them as TEXT (consistent with
            # the project's other admin tables and dbt-friendly).
            d["message_id"] = str(d["message_id"])
            d["thread_id"] = str(d["thread_id"])
            if d["thread_user_id"] is not None:
                d["thread_user_id"] = str(d["thread_user_id"])
            d["_extracted_at"] = extracted_at
            d["_extracted_run_id"] = run_id
            d["_source_endpoint"] = SOURCE_ENDPOINT
            yield d
            count += 1
        print(f"  fetched {count} chat messages (joined with threads)", flush=True)
    finally:
        conn.close()


def main() -> int:
    run_id = sys.argv[1] if len(sys.argv) > 1 else str(ULID())
    extracted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    print(f"\n=== oxy_chat_activity pipeline run {run_id} ===")
    print(f"  extracted_at: {extracted_at.isoformat()}Z (UTC)")
    print(f"  source:       {SOURCE_ENDPOINT}")
    print(f"  destination:  duckdb @ {DUCKDB_PATH} :: main_admin.fct_chat_activity_raw")

    @dlt.resource(
        name="fct_chat_activity_raw",
        primary_key="message_id",
        write_disposition="merge",
    )
    def _resource():
        yield from fetch_chat_activity(run_id, extracted_at)

    pipeline = dlt.pipeline(
        pipeline_name="oxy_chat_activity",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="main_admin",
    )
    info = pipeline.run(_resource())
    print(f"\nload info: {info}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
