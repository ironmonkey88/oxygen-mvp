---
session: 3
date: 2026-05-07
start_time: 14:25 ET
end_time: 15:50 ET
type: code
plan: none
layers: [infra, ingestion]
work: [infra, feature]
status: complete
---

# Session 3 — EC2 provisioned, dlt pipeline designed

> Migrated from original LOG.md monolithic format. Preserved as-is.

## Original entry

**Accomplishments:**
- Provisioned EC2 instance: t4g.medium, Ubuntu 24.04 LTS ARM, us-east-2 (Ohio)
- Instance ID: i-0e08479a1e757c118, Public IP: 18.224.151.49
- Configured security group: SSH (22) locked to Gordon's IP; port 3000 open to all (MVP decision — public data)
- Installed Docker 29.4.3, Oxygen 0.5.47, Python 3.12.3
- Installed dlt 1.26.0, dbt-core 1.11.9, dbt-duckdb 1.10.1 in .venv
- Set ANTHROPIC_API_KEY in ~/.bashrc on EC2
- Configured SSH alias oxygen-mvp on local machine (~/.ssh/config)
- Configured .claude/settings.json: Stop hook for log reminders + permission allowlist
- Explored Somerville SODA API: confirmed access, identified dataset 4pyi-uqq6, profiled schema and volumes
- Designed dlt pipeline: filesystem destination → Parquet partitioned by year → DuckDB reads via read_parquet()
- Corrected volume estimate: 1.17M total rows, ~100-115k/year (not 20-30k as originally estimated)

**Decisions Made:**
- Use Ubuntu 24.04 LTS instead of 22.04
- Port 3000 open to all for MVP
- PEM key stored at ~/.ssh/oxygen-mvp-server.pem
- dlt filesystem destination (Parquet) instead of DuckDB destination
- Parquet partitioned by year (1 file/year)
- Load all classifications at Bronze; filter in Silver/Gold
- Use id as primary key with merge write disposition

**Blockers:** None.

**Next Action:** Initialize dbt project and build bronze model.
