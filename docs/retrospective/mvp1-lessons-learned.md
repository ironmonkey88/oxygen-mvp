# MVP 1 — Lessons Learned

Written: 2026-05-12. Covers Sessions 1–30 — MVP 1 sign-off (Session 25) plus the
two post-sign-off plans that hardened the foundation for MVP 2: MVP 1.5
(Opus 4.7 migration + public chat at `/chat`), Plan 1a (daily incremental refresh
+ observability), Plan 1b (column profiling + `/erd` + `/profile` portal
routes).

This document is a durable artifact, not a session note. It is written for
someone joining the project six months from now and for the parts of the Oxy
team that don't see every commit. The session archive at
[`docs/sessions/`](../sessions/) carries blow-by-blow narrative; this document
carries the lessons that should outlast any single session.

---

## What we learned about Oxygen

### Multi-workspace vs `--local` mode

The single biggest pivot of MVP 1 was the move from `oxy start`
(multi-workspace, wizard-gated) to `oxy start --local` (single-workspace,
guest auth, reads `config.yml` directly). The multi-workspace onboarding wizard
asks new users to create an organization, attach a workspace, and connect a
data source — and the data-source step accepts CSV/Parquet uploads into a
fresh `.db/` directory, not a path to an existing populated DuckDB. We came
to Oxygen with a 1.17M-row medallion warehouse already built; the wizard had
no path for that shape of user.

`--local` mode bypasses the wizard entirely. It treats the workspace as the
unit of orchestration, manages the Docker Postgres lifecycle, and serves
guest-auth chat against whatever the `config.yml` datasource points at. SPA
browser-tested at `oxygen-mvp.taildee698.ts.net:3000`, the chat agent returns
113,961 for "2024 requests" with full trust contract — exactly the analyst
outcome MVP 1 was scoped against.

`--local` is now the canonical deployment mode for the project. MVP 4 will
require revisiting multi-workspace because Magic Link auth, Slack/MCP/A2A
sharing surfaces, and HTTPS routing all live there. By then, hopefully Oxygen
will ship a path for the "existing warehouse" user — we logged the finding
as Oxy customer feedback at Session 25 sign-off.

### Builder Agent and Data Apps in `--local` mode

The MVP 2 dependency we haven't yet pre-flight-verified is whether Builder
Agent (the agent that constructs `.app.yml` dashboards by conversation) is
available and functional in `--local` mode. The Procedures/Agents surface
in the SPA renders fine for the Answer Agent; whether Builder Agent appears
identically — or requires a multi-workspace org context — is the first thing
MVP 2's pre-flight needs to confirm. Flagging it here so the next plan-scoping
session doesn't assume it.

### Platform velocity is real

Verified Queries, Data Apps, Slack integration, MCP server, A2A protocol all
shipped during or right before this project. Capabilities we couldn't have
used a month ago are now production. The MVP 4 sharing surfaces depend on
features that landed while we were building MVP 1.

The discipline this implies: review the Oxygen changelog at every plan
kickoff. Treat the platform's surface as a moving target. A plan written
against last month's capabilities can over-build today.

### Rate limits matter more than expected

Tier 1 Anthropic Sonnet 4.6 at 30K input tokens/min was insufficient for SPA
multi-turn conversations. The trust contract loads the limitations index
(~2KB) plus all view files plus the Airlayer schema into context on every
turn; three to five dense turns hit the rate limit. We saw it first as
`ApiError` banners in the SPA mid-conversation.

Migration to Opus 4.7 (500K tokens/min on the same tier, 16× headroom)
resolved it. Quality went up on instruction-following and multi-turn
reasoning. Latency went up ~50% per token but the agent makes fewer follow-up
calls, so end-to-end response time is roughly equivalent. Cost is up ~5× per
token but the absolute spend is trivial — $5–6/month current, projected
$25–30/month.

The lesson is broader than this one migration: when an LLM-backed agent feels
slow or flaky on multi-turn, look at the rate-limit headers before assuming
prompt or tool issues.

---

## What we learned about the build pattern

### Configuration over custom code held up

Most of MVP 1's deliverables are YAML. `.view.yml` for the semantic layer.
`.topic.yml` for the topic graph. `.agent.yml` for the Answer Agent's trust
contract. `dbt/models/*/schema.yml` for column descriptions. systemd unit
files for service orchestration. nginx config for portal routing.

Custom Python lives at the seams: `run.sh` (pipeline orchestration),
`scripts/generate_*_page.py` (portal page generators for `/metrics`,
`/trust`, `/erd`, `/profile`), `scripts/pipeline_run_{start,end}.py` (run
observability), `scripts/profile_tables.py` (column profiling). None of
these replace Oxygen's primitives; they're scaffolding around them.

When Oxygen's primitives mature — when, say, native dbt-modeling support
lands, or when admin observability gets a first-class shape — the scaffolding
migrates onto them. Per BUILD.md §4, the project commits to that migration.
The hand-written code today is the cost of being a customer ahead of the
platform; the migration is what makes the project Oxygen-native at the
destination.

### Documentation-as-deliverable pays compounding interest

Every column in every table has a description. Every limitation is a `.md`
file in `docs/limitations/`. Every plan that touched a model updated the
corresponding schema entries. The portal's `/docs`, `/erd`, `/metrics`,
`/profile`, `/trust` routes all auto-generate from those source files.

The consequence: adding a column means updating one description. The agent
sees it (via the limitations index), the analyst sees it (via `/docs` and
`/profile`), the trust page sees it (via the schema graph), the ERD sees it
(via dbt's `relationships:` tests). Single source of truth, five surfaces.

This is the discipline most analytics teams skip and then regret. It is also
durable infrastructure, not nice-to-have polish — Plan 1b's `/profile` and
`/erd` routes were under-2-second incremental work because the primitives
they needed were already in place.

### Verification gates prevented a real regression

Session 22 surfaced a problem: STANDARDS §5.8 row 2 ("Routes live: /chat")
had been marked `[x]` based on Session 7's Answer Agent FR pass — a CLI test
against `oxy run`. By Session 22, the SPA chat surface had decayed (postgres
had 0 organizations, the only user was a test account, the route returned
the "Create organization" wizard rather than a working chat). The `[x]` was
still there. The artifact (the agent YAML) hadn't changed; the runtime had.

We codified the distinction in CLAUDE.md's "Verification gates for `[x]`
ticks" subsection (Session 23): static-artifact boxes stay ticked across
sessions; live-functional boxes must re-verify in the close-out session.
At every MVP sign-off, every live-functional box re-verifies — not
inherited from earlier sessions. The cost is seconds; the cost of a
false-green is months of trust debt.

That standard is now project-wide. Plan 1a + 1b both re-verified the bench
against the new baseline as part of their close.

### Plan-scoping in Chat, execution in Code

Long-form planning, design tradeoffs, and architectural decisions happen in
Chat with full context. Code executes against discrete, well-scoped plans.
The boundary keeps each tool in its strength zone.

Plans should be self-contained — Code can pick up a plan from a fresh
session without re-deriving context. Plans should name decisions explicitly
(usually as letters: 1a/A, 1a/B, …) so when execution hits an ambiguity
the resolution is locatable. Plans should call out pre-flight verification
of any environment-specific assumption, because two prior plans broke on
exactly that gap (Airlayer bundling, `~/.profile` env-var loading).

The plan archive at [`docs/plans/`](../plans/) is now a durable artifact in
its own right. New plans inherit the format.

---

## What we learned about Gordon-as-customer

### Real friction surfaces real product feedback

The multi-workspace wizard incompatibility is a genuine product finding for
Oxy, not a bug in our implementation. The "rate limit on Sonnet 4.6 was
hitting Tier 1 SPA multi-turn" is another. The "dbt's `models/**/*.yml`
globbing blocks auto-generated `schema.yml`" is a third (resolved in
Plan 1b/D as option (c) — `schema.yml` stays hand-written, profile data
lives on its own `/profile` portal route).

These findings are exactly what running the platform as a real customer
produces. Internal use doesn't surface them — internal users know workarounds,
have access to the engineers who can fix things, and don't carry an existing
warehouse into the wizard. Customer-shaped use carries customer-shaped
context and produces customer-shaped feedback. That's the loop the project
exists to close.

### The compass works

The success test from MVP.md is one sentence — *"you have to try this"* —
spoken by an analyst to a colleague. Not a feature checklist, not an
engagement metric. The architecture, the trust narrative, the portal opening
note, the scope discipline all answer to it. Decisions consistently passed
the test: does this protect the path through Relief → Momentum → Ownership →
Pride → Sharing, or does it leak friction back in?

A few examples of the compass deferring work:
- `/about` page deferred. Not the analyst persona's first-encounter need.
- Charts/exports/follow-up suggestions deferred to MVP 2+. The first
  experience is a single, well-trusted Q&A loop.
- Long-form `.qmd` docs deferred. dbt docs renders the column dictionary;
  more depth is bloat at MVP 1.

The compass also pulled work forward — Tailscale moved from MVP 3 to MVP 1
the moment we realized open `:3000` was leaking trust friction before any
question was asked. Compass decisions are bidirectional.

### Speed and depth aren't opposed

Two weeks of compounding work — chat agent, public chat at `/chat`, daily
self-running pipeline, trust dashboard, column profiling, ERD, limitations
registry, daily run observability — without cutting corners on documentation
or trust standards. The pace and the bar held simultaneously.

The disciplines that made that possible: planning rigorously in Chat before
writing any code; deferring everything not in the current plan's scope;
reviewing the Oxygen changelog at every plan kickoff; treating documentation
as a deliverable, not an afterthought; sweeping tech debt on a regular cadence
(Plan 5).

---

## What we'd do differently

### Smaller initial plan sizes

Some plans grew to 5,000–6,000 words. Code executes them fine, but the
authoring cost is non-trivial and the reading cost compounds for anyone
joining mid-stream. Plans 2 onward should aim for 2,000–3,000 words —
pattern-establishing rigor in the first three plans of a new MVP, then
trusting Code to fill in defaults from established patterns. This plan
itself is about 1,600 words; that's a comfortable shape.

### Earlier pivot triggers

The multi-workspace wizard attempt cost real time (Session 22 surfaced the
state, Session 25 tried walking the wizard, hit the data-source-upload-only
gate, and pivoted to `--local`). With hindsight, a 30-minute pre-flight on
"can the wizard consume our existing DuckDB" would have caught it.

The new rule, going into MVP 2: pre-flight verifies the assumed path
actually works, not just that prerequisites exist. "DuckDB has data" is not
the same as "the wizard accepts a path to existing DuckDB." Empirical, not
inferential.

### Plan numbering established earlier

The `plan-NN-descriptor.md` convention drifted across several plans before we
locked it in (Session 9, Rule 9). Earlier plans live under inconsistent
filenames. The cosmetic fix has been deferred indefinitely — conventions
established at project start, not retroactively, would have kept the file
tree clean. For MVP 2, the convention is in place from day one.

---

## What's load-bearing for what comes next

Future plans reference this section. Each dependency is named once; if it
breaks, the plan that depends on it stops working.

- **Builder Agent + Data Apps (MVP 2)** depends on `--local` mode supporting
  the Builder Agent surface. **Not yet pre-flight-verified.** First MVP 2
  task.
- **First Data App scoping (MVP 2)** depends on the semantic layer growing a
  resolution-time measure and a resolution-time-band dimension. Both are
  small, but they're prerequisites — Builder Agent constructs against the
  semantic layer.
- **Verified Queries (MVP 3)** depends on the agent test bench moving from
  hand-rolled `scratch/plan6_test_bench/` to `.agent.test.yml` + `oxy test`.
  Plan-as-handed-off for MVP 3 should explicitly retire the hand-rolled
  bench.
- **Full medallion + Silver (MVP 3)** depends on Plan 1a's incremental
  refresh pattern. ✓ now in place; `_extracted_at` audit columns let Silver
  reconcile inserts vs. updates.
- **PII redaction (MVP 3)** depends on Silver landing. The redaction list is
  small (names, emails, phones) but the pattern needs to be set before Gold
  rebuilds on top of Silver.
- **Slack + MCP + A2A (MVP 4)** depends on returning to multi-workspace
  mode. Risk known; resolution path open (either Oxygen ships a path for
  existing warehouses, or we walk the wizard with a fresh DuckDB and migrate
  data into it).
- **Magic Link auth (MVP 4)** depends on multi-workspace mode AND HTTPS.
  Current Basic Auth at `/chat` is intentional throwaway scaffolding,
  retired by MVP 4.

---

## Takeaway

MVP 1 proved the platform unblocks every analyst workflow stage — get,
query, understand, ask, answer, share. The analyst leaves a session with
a verifiable answer in their hands, not a vendor's output. The trust
contract makes that answer inspectable; the limitations registry makes the
caveats explicit; the `/trust` page makes the pipeline state visible.

MVP 2 proves the analyst can *construct*, not just *consume*. The same
analyst, in the same hour, builds the dashboard their team has been waiting
on the BI developer for. That is the next test of the compass.
