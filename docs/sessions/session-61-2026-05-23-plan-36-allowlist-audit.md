---
session: 61
date: 2026-05-23
start_time: 20:10 ET
end_time: 20:20 ET
type: code
plan: plan-36
layers: [docs]
work: [docs]
status: complete
---

## Goal

Audit the current 3-tier allowlist structure documented in CLAUDE.md "Allowlist policy" and inventory commands getting denied during normal Code operation. Information request per PROMPTS.md §2 — single report at `docs/audits/allowlist-audit-2026-05-22.md`; edits are a separate follow-up Plan if the report justifies them.

## What shipped

- **Report** at [`docs/audits/allowlist-audit-2026-05-22.md`](docs/audits/allowlist-audit-2026-05-22.md) covering: (1) Phase 1 structure tier-by-tier (3 user-configurable + 2 additional surfaces); (2) Phase 2 denial inventory from 15 transcripts; (3) recommendations grouped into the three prompt-named buckets; (4) worth-flagging.
- **Scanner** at `scratch/scan_denials.py` — parses JSONL transcripts for hook-deny patterns + permission-denied result entries, categorizes by structural reason, dedupes by session.
- **TASKS.md updates:** Plan 35 row flipped `[~]` → `[x]` (carry-over from Session 60); Plan 36 marked done with audit summary; Plan 37 reserved (the 2 `gh` Tier-1 additions); Plan 38 reserved (the 5 memory-to-file migrations).
- LOG.md Plan 36 row + Session 61 Recent Sessions entry + Last Updated bump.

## Decisions

- **Split the follow-up into Plan 37 + Plan 38 rather than one combined plan.** Plan 37's content (two one-line allowlist additions, both already endorsed by CLAUDE.md's autonomous-execution policy) is small and immediate. Plan 38's content (five memory files → real CLAUDE.md / PROMPTS.md sections) needs deliberate placement and wording — that's a real conversation, not bolt-on. Gordon's call on whether to combine, but the split lets the easy wins land before the harder discussion.

## Issues encountered

None. Boot-audit clean (portal/index.html drift now committed via Session 60's PR #61). Scanner ran cleanly on all 15 recent transcripts. Live probes all auto-allowed. The denial-inventory data was unambiguous: 96% hook denials, 4% real permission denials, all real denials correctly catching destructive ops.

## Next action

Plan 37 (two `gh` allowlist additions) when Gordon wants them. Plan 38 (memory-to-file migrations) when the placement conversation feels timely. The audit report sits in `docs/audits/` as durable reference until Plan 38 either consumes the memory files or explicitly decides to leave them as memory-only. Plan 24, Plans 18/19, DBA Dashboard execution still queued unchanged.
