---
session: 14
date: 2026-05-08
start_time: 23:00 ET
end_time: 2026-05-09 08:36 ET
type: hybrid
plan: plan-3
layers: [admin, infra, docs]
work: [feature, bugfix, hardening, docs, test]
status: complete
---

# Session 14 — Plan 3 — MVP 1 Loose Ends + Doc Reconciliation

## Goal
Close out three hygiene-shaped tracks: harden the allowlist (after the Plan 2 "regression" surprise), reconcile the chat-introduced and Session-9-introduced plan numbering schemes, bring SETUP/CLAUDE/ARCHITECTURE/STANDARDS up to date with everything Plans 1 and 2 landed, and prove the drift-fail guardrail actually fires.

## What shipped
- **Pre-flight 0 — allowlist hardening + investigation.** Plan 3 list applied to settings.json: `Bash(pip install *)`, `Bash(bash -n *)`, `Bash(./run.sh *)`, `Bash(git -C * *)`, narrow `sudo cp/mv/ln -s/chmod/chown *`, plus `Bash(aws *)` denied. Investigation finding: Plan 0 D7b commit (`196cf28`) only added git write-op patterns — the tool-family wildcards and deny list it claimed to ship were never written to settings.json (they went into settings.local.json, gitignored). No active overwriter; root cause was a partial commit + a TASKS.md `[x]` based on settings.local-only changes. Commit `6e34fdc`.
- **Pre-flight 1 — clean baseline.** EC2 pulled, tailscale healthy, `./run.sh` clean (5/5 bronze+gold built, 19/19 tests pass, 3/3 admin built, run_results captured, /docs + /metrics regenerated, exit 0).
- **D1 — plan reconciliation.** No relabeling needed: Session 9 reserved slots 2–5 without scope; chat-introduced names ("Plan 2 — Admin DQ Overnight", "Plan 3 — MVP 1 Loose Ends + Doc Reconciliation", "Plan 4 — Trust Page + Answer Agent") fill those slots cleanly. Session 13 frontmatter `plan: none` → `plan: plan-2`; LOG.md row retitled. Session counter is canonical contiguous (Code-tracked); chat-side notes diverged after Session 6 because Code-led sessions weren't logged on chat's side. session-starter.md gets Rule 9 (plan naming convention). LOG.md gets a new Plans Registry section near the top. Commit `7346dde`.
- **D2 — doc reconciliation.** SETUP.md: §1 SG reflects current reality, new §12 Tailscale Access, new §13 Portal/nginx (docroot fact, /home/ubuntu chmod, in-repo nginx/somerville.conf as canonical config), Run Order rewritten around `./run.sh` with all 7 steps. CLAUDE.md: Run Order body refreshed (5→7 steps), Session Start gets Tailnet brief + --ssh=false caveat. ARCHITECTURE.md: Deployment Architecture revamped, new nginx config subsection, Portal routes table updated, Admin Schema design notes for surrogate-key departures + raw_dbt_results_raw landing-table reality, Run Order body refreshed. STANDARDS.md: §3.1 Security all [x], §3.3 Usability all [x], §4.2 Metrics all [x], §4.4 row 1 [x], §5.5 Admin 4/5 [x] + departure notes. New file: `nginx/somerville.conf` (canonical site config matching what's deployed). Commit `093b220`.
- **D2 follow-on — transcript-timestamp rule.** CLAUDE.md gets a new "Transcript timestamps" subsection in the LOG.md Logging Protocol: emit `[YYYY-MM-DD HH:MM ET] <label>` markers at the start of each deliverable, at any pause/blocker, and before any long-running command. Commit `e3a79bb`.
- **D3 — drift-fail verification.** Wired the seam first: new singular dbt test `dbt/tests/singular/dq_drift_fail_guardrail.sql` (returns rows when `fct_test_run.status='fail'` for the latest run_id), `run.sh` step 5b runs `dbt test --select admin`, final exit code is `max(bronze/gold-test-exit, admin-test-exit)`. Commit `0a4c53c`. Then verified end-to-end with synthetic perturbation — see Decisions / table below. Commit `ee4c488` ticks the last box in STANDARDS.md §5.5 and the matching TASKS.md row.

## Decisions
- Plan-naming convention adopted as Rule 9 of session-starter.md. Every plan = `Plan <number> — <content-bearing label>`.
- Session 9 plan sequence is canonical; chat-introduced names (Plan 2 / Plan 3 / Plan 4) fill the reserved slots — no conflict, no relabeling. Plan 5 slot still unscoped.
- Session counter is contiguous 1–N tracked by Code (authoritative). Chat-side planning notes diverged after Session 6; Code's record covers every work session.
- Allowlist "regression" was an incomplete implementation, not a regression. Plan 0 D7b commit only added git write-op patterns; tool-family wildcards and deny list never landed in committed settings.json until Session 13's `edb508d`. TASKS.md `[x]` was based on settings.local.json edits.
- nginx config: in-repo `nginx/somerville.conf` is now the canonical source of truth; deploy via `scp` + `sudo cp` + `sudo nginx -t` + `sudo systemctl reload nginx`.
- Admin DQ guardrail: drift-fail rows in `fct_test_run` flow to a non-zero pipeline exit via a singular dbt test (`dq_drift_fail_guardrail`) running in `run.sh` step 5b. Final exit = `max(bronze/gold-test-exit, admin-test-exit)`.
- Transcript-timestamp rule: Code emits one-line `[YYYY-MM-DD HH:MM ET] <label>` markers at deliverable starts, pauses/blockers, and before long-running commands.

## Issues encountered
- **Polling regex false positive on `ERROR=0`.** First D3 run-completion poll fired prematurely because `dbt test`'s summary line includes `ERROR=0`. Fixed by tightening the regex to match `===== run complete =====` (the literal final marker run.sh prints regardless of exit code) and `Traceback` for fatal failures. No data impact — just had to re-check state.

  ```
  # bad: ERROR=0 in summary lines false-positives
  grep -qE "run complete|Traceback|ERROR|FAILED"
  # good: matches the literal end-marker
  grep -qE "===== run complete =====|FATAL|Traceback"
  ```
- **First D3 perturbed run hit a transient SODA 500 in dlt step.** `requests_2016` got a 500 from `data.somervillema.gov` mid-pagination, killing the run before reaching admin. Environmental, not a guardrail issue. Retry succeeded.
- **Long pause overnight.** Pre-flight 1 ran at ~23:14 ET 2026-05-08; D3c didn't fire until 08:30 ET 2026-05-09 (~9-hour gap). The new transcript-timestamp rule (committed mid-session) will make this kind of gap visible in future transcripts.

## Drift-fail verification arc

Six-run history captured in `fct_test_run` for `baseline.raw_311_requests.year_2015.row_count`:

| run_id | actual | expected | variance | status | notes |
|---|---|---|---|---|---|
| ae7f3672… | 47686 | 47686 | 0% | pass | Plan 2 D2 first run |
| ce6e9c06… | 47686 | 47686 | 0% | pass | Plan 2 D2 idempotency check |
| a543634b… | 47686 | 47686 | 0% | pass | Plan 3 pre-flight 1 |
| 6d23f00f… | 47686 | 47686 | 0% | pass | Plan 3 D3b baseline (with new guardrail) |
| **1ec8b8a7… (perturbed)** | **47686** | **33380** | **42.86%** | **fail** | Plan 3 D3c — `expected_value` set to 33380; `dq_drift_fail_guardrail` failed; run.sh exit 1 |
| fedfdab8… (restored) | 47686 | 47686 | 0% | pass | Plan 3 D3d — baseline restored; guardrail passed; run.sh exit 0 |

Failure message format: `"variance 42.86% exceeds tolerance 1.00%"`. Whole arc is preserved as history (no cleanup of admin tables — that's the design).

## Next action
Hand Plan 4 — Trust Page + Answer Agent. The `/trust` page consumes `admin.fct_test_run` (now battle-tested across 6 runs including a synthetic-fail-and-recover); the agent trust contract delivers SQL + row count + citations on every response and surfaces limitations from `docs/limitations/`.
