# Project Brief — Oxygen MVP (Somerville 311)

> **For Claude Chat:** this is a single self-contained snapshot of the project as of 2026-05-11. Paste into project knowledge (or read top-to-bottom) before doing any planning work. The repo has many narrative files (`LOG.md`, `docs/sessions/*.md`, etc.) — this brief synthesizes them so you don't have to read them all to be useful. If something in another repo file contradicts this brief, this brief is the authoritative summary as of the date above; check `LOG.md` for newer state.

---

## 0. Elevator pitch

A public-facing analytics MVP that proves Oxygen as the analyst's platform. **Built by Gordon Wong (Oxy team) playing the ideal Oxygen customer** — an experienced dbt/Looker/Snowflake architect new to Oxygen. The work doubles as pre-sales engineering, product evangelism, and product-management feedback to Oxy. Dataset is Somerville 311 (~1.17M service requests across ~10 years). The bar is "extreme trustability" — every agent answer hands over the SQL, row count, and citations so the analyst can verify and publish without spot-checking the platform.

Full strategic framing in [MVP.md](../MVP.md). Audience, protagonist, and the four-nested-MVP roadmap all live there.

---

## 1. What's actually been built

| Layer | Status | What runs today | Where in repo |
|---|---|---|---|
| Ingestion (dlt) | ✅ Production | SODA endpoint → Parquet, 1,169,935 rows (2015–2026), `union_by_name=true` cross-year merge | [dlt/somerville_311_pipeline.py](../dlt/somerville_311_pipeline.py) |
| Bronze (dbt) | ✅ Production | `main_bronze.raw_311_requests`, 24 columns, 5 tests (1 unique + 3 not_null + 1 accepted_values), dlt metadata retained | [dbt/models/bronze/](../dbt/models/bronze/) |
| Silver | ⏸ Deferred to MVP 3 | Standards stubbed in STANDARDS.md §5.3; PII redaction + dedup + type casts will land then | — |
| Gold (dbt) | ✅ Production | `main_gold.fct_311_requests` + dims `dim_date`, `dim_request_type`, `dim_status`; 14 tests (4 unique, 7 not_null, 2 relationships, 1 accepted_values) | [dbt/models/gold/](../dbt/models/gold/) |
| Admin (DQ) | ✅ Production | `fct_data_profile` (observational), `dim_data_quality_test` (auto-seeded baselines), `fct_test_run` (parsed dbt results); drift-fail guardrail proven by synthetic perturbation | [dbt/models/admin/](../dbt/models/admin/) |
| Semantic Layer (Airlayer) | ✅ Production | 4 views (`requests`, `request_types`, `statuses`, `dates`) + 1 topic; `oxy validate` clean (6/6 configs) | [semantics/](../semantics/) |
| Answer Agent | ✅ Production | Trust contract enforced: 4-section reply (row count / answer / citations / known limitations); 10 active limitation entries surfaced via index match; year-hallucination guard added; **5/5 bench re-verified 2026-05-10** | [agents/answer_agent.agent.yml](../agents/answer_agent.agent.yml) |
| Routing Agent | ⏸ Deferred to MVP 4 | Scoped; not implemented | — |
| Data Apps / Builder Agent | ⏸ MVP 2 | Not started; this is the next MVP per the roadmap | — |
| Portal (nginx) | ✅ Production | `/` (hero + engineering-honest copy), `/docs/` (dbt docs generate output), `/metrics` (auto-generated from `.view.yml`), `/trust` (admin-DQ-driven) all return 200 | [portal/index.html](../portal/index.html), [nginx/somerville.conf](../nginx/somerville.conf) |
| Pipeline orchestration | ✅ Production | `./run.sh` 9-step: dlt → dbt bronze/gold → tests → load_dbt_results → dbt admin → drift-fail test → docs → /metrics → /trust + portal sync → limitations index | [run.sh](../run.sh) |
| Limitations registry | ✅ Production | `docs/limitations/*.md` (10 active entries) + auto-generated `_index.yaml` consumed by the agent for affects-match surfacing | [docs/limitations/](limitations/) |
| Infra (Oxygen runtime) | ✅ Production | `oxy.service` systemd unit (hardened with `After=docker.service`/`Requires=docker.service`/`RestartSec=10`); reboot test PASSED with volume persistence proven | [SETUP.md §11](../SETUP.md) |
| Infra (network) | ✅ Production | EC2 t4g.medium, us-east-2, public IP 18.224.151.49 (port 80 portal); SSH + `:3000` Tailnet-only via `oxygen-mvp.taildee698.ts.net` | [SETUP.md §12](../SETUP.md) |
| Allowlist + Bash Safety hook | ✅ Production | Three-tier policy (committed `settings.json` = universal; `settings.local.json` = per-machine; worktree locals mirror canonical local); `.claude/hooks/block-dangerous.sh` denies risky shell shapes | [.claude/settings.json](../.claude/settings.json), [CLAUDE.md](../CLAUDE.md) §Bash Safety + §Allowlist policy |
| Oxygen docs mirror | ✅ Production | 120 pages from oxy.tech/docs mirrored locally for offline grep + Chat project knowledge | [docs/oxygen-docs/](oxygen-docs/) |

---

## 2. MVP 1 sign-off status

**One open box.** Everything else green with re-verified evidence (the new verification-gates standard requires live-functional boxes to re-pass at sign-off, not inherit from earlier sessions — this happened in Session 23+24).

| §6 row | Status | Notes |
|---|---|---|
| Foundations 10/10 | ✅ | §3.1 5/5 (security, Plan 1), §3.2 5/5 (reliability, **systemd closed Session 24**), §3.3 4/4 (usability) |
| Trustability 16/16 | ✅ | §4.1 4/4 (agent trust contract), §4.2 3/3 (metric definitions), §4.3 4/4 (`/trust` page), §4.4 2/2 (limitations registry), §4.5 3/3 (**repo-clonable closed Session 24**) |
| Layers 6/7 | ⚠️ | §5.1/5.2/5.4/5.5/5.6/5.7 all `[x]`; **§5.8 row 2 (`/chat`) is the open box** (5/6) |
| E2E smoke 5/5 | ✅ | 2024 question → 113,961, top types Q3 match Session 18, /trust green 36/36, /metrics lists measures, /docs renders dbt docs |

### The one open decision

**STANDARDS §5.8 row 2 — `Routes live: /chat`** is `[ ]`. Two reasons:
1. Port-80 `/chat` returns 404 (nginx route was removed in Plan 1 D4 when chat went Tailnet-only).
2. The Tailnet `:3000` SPA renders the "Welcome to Oxygen / Create organization" onboarding screen because postgres has 0 orgs — Session 22 surfaced this. The only user record is a `local-user@example.com` from Gordon's 2026-05-10 20:54 ET sign-up attempt; orgs were never created.

**The CLI path is healthy.** `oxy run agents/answer_agent.agent.yml "<question>"` returns the right answer with full trust contract. Bench was re-verified 5/5 in Sessions 23+24 (Q1 2024=113,961, Q2 YTD 49,782, Q3 top types match, Q4 NA sentinel surfaced, Q5 satisfaction 4.44/5 blended).

**Gordon's call:**
- (a) Walk the UI wizard in a browser at `oxygen-mvp.taildee698.ts.net:3000`, create the org, connect the somerville datasource, register the agent, ask the 2024 question, confirm 113,961, re-tick on a passing SPA query.
- (b) Reinterpret §5.8 row 2 as definitively CLI-only — for MVP 1, the analyst persona's chat experience is `oxy run`; the SPA is out of scope. Re-tick with inline note in STANDARDS.

Either decision triggers the documented one-shot close-out: STANDARDS §6 header note "MVP 1 signed off 2026-05-11", LOG Current Status → MVP 2, CLAUDE.md MVP Sequence flip, TASKS.md sign-off section all `[x]`.

---

## 3. The four-MVP roadmap (per MVP.md)

Each MVP is a complete Knowledge Product on Somerville 311 data, adding maturity along the analyst workflow.

| MVP | Tagline | Adds | Status |
|---|---|---|---|
| MVP 1 | First Knowledge Product (descriptive) | Ingestion + Warehouse + Semantic Layer + Answer Agent | ✅ All but one box; one Gordon decision away |
| MVP 2 | Visual Knowledge Products (descriptive → early diagnostic) | Data Apps + Builder Agent | ⏸ Not started |
| MVP 3 | Governance and Trust (full diagnostic) | Verified Queries + Observability + full medallion (silver + PII) | ⏸ Not started |
| MVP 4 | Semantic Depth and Sharing (diagnostic) | Expanded Topics/Views library + Slack + A2A + MCP + Looker | ⏸ Not started |

**Demo moment for MVP 1:** "How many 311 requests in 2024?" → 113,961, rendered with the SQL that produced it. Achieved via CLI; SPA pending §5.8 row 2 decision above.

---

## 4. The verification gates standard (load-bearing recent change)

Session 22 surfaced a problem: STANDARDS §6 boxes had been ticked on point-in-time verification that didn't persist. Session 7's "Chat UI accessible and answering questions correctly" was `[x]` on 2026-05-08; tonight (2026-05-10) the SPA chat had 0 orgs and rendered the onboarding screen. Nothing in the workflow had caught the regression.

Session 23 codified the fix as a CLAUDE.md subsection — "Verification gates for `[x]` ticks":

- **Static-artifact boxes** (a file, a config, a description in `schema.yml`) can be ticked once on a commit hash and stay ticked.
- **Live-functional boxes** ("chat answers correctly", "/trust page green", "`./run.sh` end-to-end") must reference a re-runnable verification command, and **must be re-verified in the sign-off session** — not inherited from earlier ticks.
- Auth/state-gated routes (the `/chat` case) require either a UI walkthrough or an explicit inline reinterpretation note.

This is enforced from now on. Session 23's retroactive sweep flipped §5.8 row 2 because it failed the standard.

---

## 5. Recent work timeline (last 7 sessions)

| Session | Date | What | Status |
|---|---|---|---|
| 17 | 2026-05-09 | Plan 9 rev 2 — Bash Safety hook + allowlist refinement | ✅ |
| 18 | 2026-05-09 | Plans 6 + 8 — trust contract + limitations expansion (10 entries) | ✅ |
| 19 | 2026-05-09 | Plan 7 — MVP 1 sign-off sweep (portal copy refresh, 23/25 `[x]`) | ✅ |
| 20 | 2026-05-09 → 10 | Plan 5 — tech debt sweep (settings reconcile, dbt profiles.example, doc reconciliation) | ✅ |
| 21 | 2026-05-10 | Plan 5 D1 follow-on — git pipe pattern coverage (allowlist fix) | ✅ |
| 22 | 2026-05-10 evening | Oxygen state recon — found 0 orgs in postgres; halted at browser-only onboarding | ⚠️ Stopped at clean blocker |
| 23 | 2026-05-10 evening | Verification-gates standard codified; retroactive sweep flipped §5.8 row 2 | ✅ |
| 24 | 2026-05-10 → 11 | Systemd deploy + REBOOT TEST PASS + bench 5/5 re-verified + `./run.sh` clean + §3.2/§4.5 closed | ✅ |
| (this) | 2026-05-11 morning | MVP.md added at repo root; oxy.tech/docs mirrored to `docs/oxygen-docs/`; aws allowlist enabled; daily $10 spend budget prepped | 🔄 In progress |

---

## 6. Stack at a glance

| Concern | Tool / file | Notes |
|---|---|---|
| Ingestion | dlt (Python, `[duckdb]` extra) | Parquet on filesystem, partitioned by year, `replace` disposition per year-resource |
| Warehouse | DuckDB (single file at `data/somerville.duckdb` on EC2) | Source of truth; locked sequentially by dlt → dbt → oxy per CLAUDE.md "Run order" |
| Transformation | dbt Core 1.11.9 + dbt-duckdb 1.10.1 | bronze + gold + admin schemas; profiles.example shipped in repo |
| Semantic Layer | Airlayer 0.1.1 (`oxy validate`) | `.view.yml` + `.topic.yml` files; entities/dimensions/measures/topics/views per Oxygen schema |
| Agent | Answer Agent (`.agent.yml`) running on Oxygen 0.5.47 | Trust contract is prompt-enforced; runtime renders SQL + result-table natively; limitations index loaded as `context.file` |
| LLM | Claude Sonnet 4.6 via `ANTHROPIC_API_KEY` | Configured in `config.yml` `model_ref: claude-sonnet-4-6`, `key_var: ANTHROPIC_API_KEY` |
| Portal | nginx on EC2 port 80 | Static `portal/index.html` + dynamic `/metrics`, `/trust`, dbt docs alias |
| Auth/network | Tailscale (Tailnet `taildee698.ts.net`) for SSH + `:3000`; AWS SG closes both publicly | OpenSSH only (Tailscale SSH disabled — broke `/etc/environment` env-var loading) |
| Infra orchestration | systemd unit `oxy.service` | `After=docker.service Requires=docker.service`, `EnvironmentFile=/etc/environment`, `Restart=always RestartSec=10` |
| Pipeline orchestration | `./run.sh` (9-step) | Single entry point; sequential lock contract; final exit = max(bronze-gold-test, admin-test) |

---

## 7. Key decisions Gordon's made (curated from LOG.md)

These shape the project and are not up for renegotiation unless explicitly raised:

**Architecture:**
- DuckDB as warehouse (zero-config, sufficient for 1.17M rows)
- dlt for ingestion (Python-native, mature) over Airway (not yet evaluated)
- dbt Core for transformation (deep Gordon expertise) over Airform (April 2026, too new)
- Airlayer as semantic source of truth (`.view.yml` only); never hardcode metrics in SQL or app configs
- DuckDB-Wasm on the roadmap for analyst-facing browser-side queries (MVP 2+)
- Parquet on filesystem (storage-agnostic) over DuckDB destination

**Modeling:**
- Snake case everywhere; `_dt` for dates/timestamps; `is_` for booleans; `pct_` for percentages; `_count` for counts
- Primary keys: `<table>_id` (md5 hash); `_sk` surrogate keys reserved for MVP 3+
- Gold location: ward + block_code only (bronze has no street-level data); dim_location deferred to MVP 3
- PII redaction at Silver only (never bronze, never gold) — required for MVP 3 sign-off

**Process / operations:**
- `./run.sh` is the single pipeline entry point — never run dlt/dbt/oxy individually
- EC2 pulls from main at session start (CLAUDE.md "Session Start on EC2")
- Tailscale is intentionally OpenSSH-only (Tailscale SSH disabled — silently broke env-var loading via PAM)
- nginx docroot is `/var/www/somerville` (NOT `/var/www/html` — default site isn't enabled)
- Three-tier allowlist policy: committed `settings.json` = universal; per-machine `settings.local.json` = local exceptions; worktree locals mirror canonical local; destructive subcommands explicitly denied
- Bash Safety hook denies risky shell shapes (`&&`, `;`, `$()`, `<()`, `>()`, leading `cd`/`export`) with loop-keyword + arithmetic carve-outs

**Trust + sign-off:**
- Bar is "extreme trustability," not "trustworthy" — analyst sees the receipts on every answer
- Agent prompt: never state a calendar year in prose without querying it (`year(current_date)` first; learned from Q2 hallucinating "2025" when current was 2026)
- Verification-gates standard: live-functional boxes re-verify in the sign-off session, not inherited
- Limitation registry uses index file (`_index.yaml`), not full bodies — full-body context blew past the 30K/min input-token rate limit; index is ~2KB

---

## 8. Things that look ambiguous if you're reading the repo cold

| Thing | What's actually true |
|---|---|
| `TASKS.md` shows "Chat UI accessible and answering questions correctly" as `[!]`, but STANDARDS.md §4.1 and §5.7 show agent trust contract as `[x]` 4/4. Contradiction? | Not a contradiction. The **CLI agent path** is `[x]` (Plan 6 D3 5/5 bench; re-verified Session 23+24). The **SPA chat UI** is `[!]` because the web frontend at `:3000` needs an org created. TASKS.md row is about the SPA experience; STANDARDS rows are about the agent's behavior (which works via CLI). The verification-gates standard now makes this distinction explicit. |
| "Plans 6/7/8 are closed" in LOG.md but a "Plan 7" is still referenced as the active sign-off plan | Plans are closed in the sense that their Code-actionable work is done. Plan 7's "sign-off close-out" task remains open because §5.8 row 2 is the one open box. The Plans Registry table is the source of truth on plan status. |
| There are TWO session files labeled "session 17" | Yes — merge artifact from the gifted-cartwright branch landing on main. Both are real history (17-rev2-bash-safety-hook and 17-allowlist-cleanup); the numbering wasn't renamed. Not blocking anything; would be a future cosmetic fix. |
| `Bash(aws *)` was in the **deny** list until 2026-05-11 morning — now in **allow** list with 27 destructive denies | Recent change (commit `0afaa15`). Allows Cost Explorer / Budgets / describe-* reads; denies terminate/delete/modify/iam-writes. Permission cache means it takes effect next Code session. |
| ARCHITECTURE.md says "Oxygen is `nohup oxy start`" in one place | Stale comment. As of Session 24, Oxygen runs as a systemd service (`oxy.service`). SETUP.md §11 has the current recipe. |
| `oxy-postgres` container — does it survive `oxy start` being killed? | Yes — the named docker volume `oxy-postgres-data` persists. Killing `oxy start` removes the container but the volume detaches and re-attaches on next start. **Verified empirically Session 24:** user record from Session 22 survived a full instance reboot. |
| Why did the "chat UI" appear to "regress" between Session 7 and Session 22? | Probably never actually worked end-to-end via the SPA. Session 7's "chat UI" claim in TASKS.md was likely CLI-based testing mislabeled, or the volume got wiped between sessions. Session 22 found 0 orgs; the only user record was from Gordon's tonight signup. STANDARDS §5.8 row 2 had been satisfied via the "Private beta pill" reinterpretation, not via end-to-end SPA verification. This is the case-in-chief for the verification-gates standard. |

---

## 9. What's intentionally NOT in MVP 1 (so don't try to scope-creep)

Deferred to MVP 2+:
- Charts, dashboards, exports, drill-downs (MVP 2 — Data Apps + Builder Agent)
- Follow-up suggestions, anomaly surfacing (MVP 2+)
- PII redaction, full medallion architecture (MVP 3 — Silver layer + Governance)
- `dim_location` with neighborhood/lat/long/address (MVP 3 — depends on PII redaction)
- Verified Queries badges (MVP 3)
- LLM-as-judge agent testing framework (MVP 3)
- Slack integration, A2A, MCP server, Looker integration (MVP 4)
- Full Topics + Views library, response-time SLA metrics (MVP 4 — Routing Agent + expanded semantic layer)
- `/about` page, long-form `.qmd` docs (deferred — analyst persona doesn't need them)

---

## 10. Reference map (which file for what)

| Need | Read |
|---|---|
| Strategic positioning, audience, the four-MVP roadmap | [MVP.md](../MVP.md) |
| Project instructions for Claude Code | [CLAUDE.md](../CLAUDE.md) |
| Architecture decisions, component map, data flow, constraints | [ARCHITECTURE.md](../ARCHITECTURE.md) |
| Environment setup, install commands, config files, systemd unit | [SETUP.md](../SETUP.md) |
| "Done done" spec by layer + MVP 1 sign-off checklist | [STANDARDS.md](../STANDARDS.md) |
| Current status, recent sessions, active blockers, decisions log | [LOG.md](../LOG.md) |
| Task tracker (Sign-off Status + per-MVP task blocks) | [TASKS.md](../TASKS.md) |
| Per-session narratives | [docs/sessions/](sessions/) |
| Data limitations (10 entries) + the index the agent consumes | [docs/limitations/](limitations/) |
| Oxygen docs mirror (120 pages from oxy.tech) | [docs/oxygen-docs/](oxygen-docs/) |
| Oxygen source code (Rust, private but gh-authenticated) | https://github.com/oxy-hq/oxygen-internal |
| Claude Code Oxygen skills | https://github.com/oxy-hq/skills |
| Source DDL (DDL source of truth) | [docs/schema.sql](schema.sql) |
| Older decisions + resolved blockers | [docs/log-archive.md](log-archive.md) |

---

## 11. Reading paths for common questions

**"What did the last week of work accomplish?"** → LOG.md "Recent Sessions" (5 most recent with 5-line summaries) + Plans Registry table.

**"Why did we decide X?"** → LOG.md "Active Decisions" table (30-day rolling window), or grep `docs/sessions/*.md` for the topic.

**"How is the agent's trust contract enforced?"** → [agents/answer_agent.agent.yml](../agents/answer_agent.agent.yml) `system_instructions` block; STANDARDS.md §4.1 + §5.7 for the spec.

**"What's the bar for MVP 1 sign-off?"** → STANDARDS.md §6 + Active Blockers in LOG.md.

**"How does the limitations registry work?"** → [docs/limitations/README.md](limitations/README.md) for format; [scripts/build_limitations_index.py](../scripts/build_limitations_index.py) for the index generator (run.sh step 9/9).

**"What does `./run.sh` actually run?"** → SETUP.md "Run Order" + CLAUDE.md "Run Order" + [run.sh](../run.sh) itself; ARCHITECTURE.md has the rationale for the lock-contention ordering.

**"How do I add a new limitation entry?"** → Drop a `.md` file in `docs/limitations/` with YAML frontmatter (`id`, `title`, `severity`, `affects`, `since`, `status`); run.sh step 9/9 regenerates the index automatically. Agent will pick it up on next `oxy start` reload.

**"Is the project on or off systemd?"** → On systemd as of Session 24. `sudo systemctl status oxy` is the authoritative check.

---

## 12. Open questions for Gordon (Chat: these are the unanswered items)

1. **STANDARDS §5.8 row 2** — UI walkthrough OR CLI-only reinterpretation? (sign-off blocker)
2. **MVP 2 scope** — when sign-off lands, what's the first Data App to build? "Service request volume by neighborhood, monthly, with drill-down" is the MVP.md demo-moment phrasing — is that the first target?
3. **Demonstration surface** — MVP 1 closes; how to invite prospects in? Tailnet doesn't scale to multi-tenant evaluation. Multi-workspace mode + Magic Link auth are recent Oxygen features; using either of them is its own scoped piece of work.
4. **Repo public flip** — currently private + team-clonable (Session 24 reinterpretation). When does it actually go public? Tied to demonstration-surface decisions above.
5. **AWS spend alert** — $10/day budget prepped in [scratch/aws_budget_setup.md](../scratch/aws_budget_setup.md); needs Gordon to paste the one-line apply command, or wait for next Code session.

---

**Last updated:** 2026-05-11 morning ET
**Source of truth for newer changes:** [LOG.md](../LOG.md) "Current Status" + "Recent Sessions"
**This brief refreshed by:** Code, per Gordon's request to give Chat a single review document
