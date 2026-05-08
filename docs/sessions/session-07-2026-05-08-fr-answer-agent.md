---
session: 7
date: 2026-05-08
start_time: morning ET
end_time: midday ET
type: code
plan: none
layers: [agent, semantic, infra]
work: [feature, test]
status: complete
---

# Session 7 — Functional requirement: Answer Agent end-to-end

## Goal
Get the Answer Agent running end-to-end so a user can open a chat and ask "How many tickets were filed this year?" — functional requirement only, trust contract deferred to NFR pass.

## What shipped
- `agents/answer_agent.agent.yml` — `claude-sonnet-4-6` + `execute_sql` against `somerville` datasource, context block injects topic + views + `docs/schema.sql`
- Oxygen runtime live on EC2 (oxy-postgres container, web app at :3000)
- Portal `/chat` confirmed proxying to Oxygen (`<title>Oxygen</title>`)
- Two commits: `f9b3b59` (agent), `5f91595` (docs)

## Decisions
- FR pass intentionally defers trust contract (SQL + row count + citations) to a follow-up — today's bar is "agent answers correctly"
- Test bench: 2024 (canonical regression) + 2026 ("this year" partial) — both must match direct DuckDB queries

## Issues encountered
None during execution. Three flags raised for next thread:
- `oxy build` needs `OXY_DATABASE_URL` even with `oxy start` running — should land in `~/.bashrc` or `run.sh`
- Ubuntu's `~/.bashrc` early-returns for non-interactive ssh — `oxy`/`ANTHROPIC_API_KEY` not visible without `bash -ic`
- Public `:3000` is open to the world — Tailscale work in TASKS.md will close that

## Validation gates (all green)
1. `oxy validate` exits 0 — "All 6 config files are valid"
2. `oxy build` exits 0 — embeddings built for answer_agent
3. `curl -I http://localhost:3000` — HTTP/1.1 200 OK
4. Test A (2024 full year) — agent 113,961 = DuckDB 113,961
5. Test B (2026 "this year") — agent 48,806 = DuckDB 48,806; used `year(current_date)`, framed as "So far this year"

## Next action
Trust contract pass (Plan 5) — but first close the three flags raised here.
