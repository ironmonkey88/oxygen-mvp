---
session: 18
date: 2026-05-09
start_time: 19:40 ET
end_time: 21:05 ET
type: code
plan: plan-6
layers: [agent, gold, semantic, docs, infra]
work: [feature, hardening, docs, test]
status: complete
---

## Goal

Close two interlocked plans in the rev 2 overnight batch: Plan 6 (Answer Agent trust contract) and Plan 8 (limitations registry expansion). Plan 6 is the load-bearing MVP 1 sign-off blocker (STANDARDS §4.1 + §5.7); Plan 8 is its closing dependency (the trust contract surfaces real limitation entries, and without Plan 8 those entries don't exist).

## What shipped

- [agents/answer_agent.agent.yml](agents/answer_agent.agent.yml) — rewrote `system_instructions` to enforce the 4-section trust contract (Returned N rows / Answer / Citations / Known limitations); engineering-honest tone (no emoji, no marketing register); limitations index loaded via `context.file` `docs/limitations/_index.yaml`. Commit `b3b5217` (D1) + a follow-up commit that switched from full-body glob to index-only.
- [STANDARDS.md](STANDARDS.md) — §4.1 4/4, §4.4 row 2, §5.7 4/4 flipped `[x]`. §7 open question on native SQL+citation support resolved: partial native (runtime renders `SQL query:` / `Result:`; `Output:` is prompt-controlled).
- [docs/limitations/2024-survey-columns-sparse.md](docs/limitations/2024-survey-columns-sparse.md) — tightened `affects:` from `[requests]` (overfired) to `[accuracy, courtesy, ease, overallexperience]` (granular columns).
- 8 new entries under [docs/limitations/](docs/limitations/) — `location-ward-block-only.md`, `survey-columns-on-fact.md`, `dept-tags-as-booleans.md`, `bronze-varchar-source-cols.md`, `open-status-not-just-open.md`, `open-requests-no-join-filter.md`, `current-year-partial.md`, `oxy-build-postgres-dependency.md`. Granular `affects:` per entry.
- [scripts/build_limitations_index.py](scripts/build_limitations_index.py) — stdlib-only YAML emitter; reads `*.md` frontmatter, writes `docs/limitations/_index.yaml`. No PyYAML dep.
- [docs/limitations/_index.yaml](docs/limitations/_index.yaml) — generated; 10 active entries, ~2KB.
- [run.sh](run.sh) — added step 9/9 to rebuild the index after each pipeline run.
- [TASKS.md](TASKS.md) — Plan 6 + Plan 8 blocks closed; legacy MVP 1 rows for trust contract / test bench / limitations / agent reference all flipped.
- [scratch/plan6_test_bench/](scratch/plan6_test_bench/) (gitignored) — 5 transcripts: q1_2024_regression.md, q2_current_year_partial.md, q3_top_request_types.md, q4_top_blocks.md, q5_satisfaction.md. All five trust contract; Q2 has a flagged prose error (year hallucination).

## Decisions

- Trust contract is prompt-only — no post-processing wrapper. Oxygen runtime renders SQL + result table natively; Output: is fully prompt-controlled.
- Limitations registry consumed via generated index (`_index.yaml`), not full `*.md` glob. Full glob hit Anthropic 30K-tokens/min rate limit on multi-turn questions; index is ~2KB.
- `affects:` values are granular (column names, qualified `view.dim`, or sentinel tokens like `current_date`/`deploy.oxy_build`) — not blanket view names. Eliminates the `[requests]`-style false positives.
- Index pipeline lives in `run.sh` step 9/9, not a separate workflow — single source of truth, regenerates on every pipeline run.
- Test bench transcripts are gitignored evidence under `scratch/plan6_test_bench/`. Session file summarizes; analyst can re-run bench at any time to regenerate.
- Agent prose hallucinated "2025" for `year(current_date)` in Q2 — SQL was correct; prose mislabeled. Trust contract holds (receipts intact); flagged as a Plan 7 / Plan 5 D5 prompt-hardening follow-on.

## Issues encountered

**Rate limit at 30K input tokens/min on Q3 + Q5 first attempt.** Cause: full-body `docs/limitations/*.md` glob loaded ~10KB of registry into context per LLM call; Q3 and Q5 needed multi-turn agent flows that exceeded the budget. Fix: introduced `_index.yaml` (id+title+severity+affects+path triples, ~2KB) and switched the agent's `context.limitations` source. Q3 + Q5 succeeded on retry. Now also more sustainable as the registry grows.

**Q2 year hallucination.** Sonnet 4-6 prose said "2025" while SQL evaluated `year(current_date)` to 2026 (today is 2026-05-09; result was 49,782, consistent with one extra day past Session 7's 48,806). Receipts hold; prose misleads. Follow-on: prompt hardening to forbid stating a calendar year without having queried it. Tracked in LOG Decisions row + flagged in q2_current_year_partial.md transcript.

**Q4 prose duplicated a block_code in the answer text.** Result table is correct (5 distinct blocks); the agent's prose said "250173501081004" both 3rd and 4th place. Sloppy LLM output, not a contract failure — methodology still inspectable via the SQL+Result the runtime rendered.

**Brief vs schema column-name mismatch.** Brief specified `affects: [requests.satisfaction_rating, requests.satisfaction_comment]` for `survey-columns-on-fact.md`, but actual columns are `accuracy/courtesy/ease/overallexperience`. Brief was speculative; entry uses real names from `DESCRIBE main_gold.fct_311_requests`.

**Brief referenced `is_open` column that doesn't exist in current schema.** LOG row from 2026-05-07 documented an `is_open` design decision, but the column was never added to the gold fact (or was removed). Reframed `open-status-not-just-open.md` around the `open_requests` measure semantics instead.

## Next action

Plan 7 — MVP 1 Sign-off Sweep. Walk STANDARDS §6 checklist, refresh portal copy to engineering-honest tone, determine sign-off (or list blockers). Plan 5 — Tech Debt Sweep follows.
