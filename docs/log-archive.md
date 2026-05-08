# log-archive.md — LOG.md Rotation Overflow

> Decisions older than 30 days and resolved blockers move here from LOG.md.
> Append-only. Search via grep.

## Decisions Log (archived)

| Date | Decision | Rationale |
|------|----------|-----------|

## Blockers Log (resolved)

| Date | Blocker | Status | Resolution |
|------|---------|--------|------------|
| 2026-05-07 18:28 ET | Port 80 not open in AWS security group — portal unreachable from public internet | Resolved | Gordon added inbound HTTP rule (port 80, 0.0.0.0/0) in AWS console |
| 2026-05-08 07:22 ET | `oxy build` requires `OXY_DATABASE_URL` — config validation gate failed | Resolved 2026-05-08 10:05 ET | Gate downgraded in Session 5; fully resolved in Session 7 when `oxy start` brought Postgres up; documented in Session 8 |
