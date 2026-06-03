# Report — Tech + test debt assessment

**Companion to:** [`plan-47-techdebt-assessment.md`](plan-47-techdebt-assessment.md)
**Session:** [69](../sessions/session-69-2026-06-03-plan-47-techdebt-assessment.md)
**PR:** [#76](https://github.com/ironmonkey88/oxygen-mvp/pull/76)
**Deliverable:** [`docs/design/TECHDEBT_ASSESSMENT.md`](../design/TECHDEBT_ASSESSMENT.md)
**Date:** 2026-06-03
**Status:** complete (report-only — proposal awaiting Gordon's ratification before any reduction work)

---

## Gate table

| Phase | Scope | Status | Where |
|---|---|---|---|
| 0 | Prompt written to repo + first commit | complete | `30c6368` (`docs/prompts/plan-47-techdebt-assessment.md`) |
| — | Prompt vetted for completeness before execution | complete | 2 blocking gaps surfaced + resolved (see below) |
| 1 | Page-gen DRY-vs-WET dedup analysis | complete | TECHDEBT_ASSESSMENT.md §1 |
| 2 | Test/CI gap + Methodology R1 tie-in | complete | §2 |
| 3 | Dependency hygiene + proposed pinned `requirements.txt` | complete | §3 |
| 4 | Data-layer coherence verdict (dbt graph + dlt pipelines) | complete | §4 |
| 4b | Broader code-debt scan | complete | §5 |
| 5 | Write `TECHDEBT_ASSESSMENT.md` with prioritized + sequenced plan | complete | §7 + §8 appendix |
| 6 | Commit + LOG/TASKS/session + open PR | complete | this PR ([#76](https://github.com/ironmonkey88/oxygen-mvp/pull/76)) |
| — | EC2 measurement | read-only only | `pip freeze` / `dbt parse` / `run_results.json` — no writes |
| — | Behavior changes | **none** | report-only by mandate |

## Shipped

- [`docs/design/TECHDEBT_ASSESSMENT.md`](../design/TECHDEBT_ASSESSMENT.md) — 8 sections. §0 exec summary + headline verdict; §1 page-gen DRY-vs-WET; §2 test/CI gap + R1; §3 dependency hygiene + proposed pinned `requirements.txt`; §4 data-layer coherence verdict; §5 broader scan; §6 scope honesty; §7 prioritized + sequenced 9-step plan + "What NOT to do"; §8 measured-numbers appendix.
- [Prompt file](plan-47-techdebt-assessment.md) — verbatim prompt + an "Execution notes (Code, plan-47)" section recording the two resolved gaps.
- This report.
- `LOG.md` — Plan 47 Plans Registry row; Last Updated bumped to 2026-06-03; Session 69 + the previously-missing Session 68 added to Recent Sessions; Sessions 64 + 63 rotated to Earlier Sessions.
- `TASKS.md` — Plan 47 row flipped `[~]` → `[x]`.
- [Session 69 file](../sessions/session-69-2026-06-03-plan-47-techdebt-assessment.md) — five-section body, controlled-vocabulary frontmatter.

## Headline verdict

The stack is a **coherent team-effort, not parallel play.** The debt is *missing safety infrastructure* + *un-factored duplication*, not architectural incoherence.

- **No safety net:** zero Python tests, no CI, no pinned dependency manifest, no automated end-to-end agent-contract (R1) gate.
- **Bounded duplication:** ~550–650 lines of full-HTML page-shell chrome collapsible across 6 generators. `_nav.py` already did the highest-value extraction. Flagged **against** over-abstraction — a small shared helper, not a base class.
- **One correctness-adjacent seam:** admin models hardcode `main_gold.*` / `main_bronze.*` instead of `ref()` (manifest shows zero dbt-tracked deps for them).
- **dlt:** disciplined copy-paste template, but zero retry/backoff anywhere (`tenacity` installed, unused).

## Measured (EC2 read-only, build `89d6ecc`)

- 31 canonical Python/SQL files / 7,271 LOC (worktree + scratch copies excluded).
- 26 dbt models: 7 bronze / 1 silver / 15 gold / 3 admin.
- 154 tests: 88 not_null / 29 unique / 24 accepted_values / 12 relationships / 1 singular.
- 0 project macros. 9 gold→bronze silver-skip edges. All models sub-second.
- Proposed pinned `requirements.txt`: 10 deps; pins = EC2 `pip freeze`; 4 shared pins match stack-in-a-box exactly; `python-ulid==3.1.0` hard-pin flagged for the 1.x→3.x API break.

## Worth flagging

- **The prompt was vetted before execution** (Gordon's "you are the coding expert, not Chat"). All premises verified true. Two blocking gaps surfaced and resolved: (1) Phase 4 needed EC2 manifest/timings but access was undefined → Gordon authorized read-only EC2 measurement; (2) the "methodology whiteboard / R1" had no locatable artifact → Gordon supplied METHODOLOGY.md. A third inversion was corrected: EC2 `pip freeze` is the authoritative pin source, with stack-in-a-box as a read-only cross-reference (not the reverse).
- **Measured numbers superseded the prompt's stale counts.** Prompt said 90/39/28/17 not_null/unique/accepted_values/relationships; the manifest gives 88/29/24/12 (+1 singular = 154). The report uses the measured figures.
- **LOC excludes worktree + scratch copies.** An initial `find` double-counted a 430-line `.claude/worktrees/` copy of the 757-line `generate_trust_page.py`. Those are gitignored local cruft, not repo debt.
- **R1 is reported, not instantiated.** Per the prompt's standing rule + METHODOLOGY's "Code-proposes / human-approves, never auto-committed," instantiating the agent-contract gate is recommended as a human-ratified follow-up, not auto-created in this plan.
- **PR opened and surfaced, not auto-merged.** The autonomous-merge policy applies to verified work; this is a *proposal* that explicitly states reduction work waits on Gordon's ratification, so it goes to review rather than straight to merge.

## Ready for more work — if §7 is ratified

The sequence is deliberately ordered so safety nets land before any refactor:

1. Pin dependencies (`requirements.txt` as proposed in §3).
2. Introduce a pytest harness (first Python tests in the project).
3. Wire CI + an automated agent-contract (R1) gate.
4. Factor `dlt/common.py` + add retry/backoff; introduce dbt macros; convert admin models to `ref()`.
5. Extract the shared page-shell helper (the bounded ~550–650 lines).
6. Expand `fct_data_profile` beyond its frozen 5 tables.
7. Continue silver / MVP 3 build-out.

None of this starts without Gordon's go on the §7 sequence.
