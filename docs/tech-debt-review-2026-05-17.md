# Tech-Debt & Quality-Gap Review — Oxygen MVP

**Date:** 2026-05-17 13:10 ET
**Scope:** entire stack as of `claude/bold-dirac-7b6669` (parent commit `a5616e0`, Plan 28 PHILOSOPHY.md landed)
**Method:** five-pass review (authority docs → code/config → infra/security → cross-cutting verification → consolidation). False positives from intermediate passes were checked against the actual files before landing here.
**Out of scope:** no code changes. This document is a punch list, not a patch.

---

## 0. Executive read

The project is in unusually good shape for an MVP-1-just-shipped codebase. The discipline around limitations, descriptions, verification gates, and authority-doc hierarchy is doing real work — most of what an audit would normally flag is already named in [docs/limitations/](limitations/) (34 entries) or queued in [TASKS.md](../TASKS.md). The medallion is clean, the trust contract is enforced in the agent's system prompt, and `run.sh` records every run into `main_admin.fct_pipeline_run_raw` with stage-level outcomes.

What this review surfaces are **two real bugs** (`/metrics` page renders invalid SQL for `average` measures; ward column is defined twice in two schema.yml entries), **one operational silent-failure path** (deploy_html swallows chown errors), **stale doc references** (CLAUDE.md still names Sonnet; project file structure lists agents and apps that don't exist), and a cluster of medium items where MVP 3 readiness will require explicit work (Silver layer, sudo-cp blast radius in the allowlist, missing security headers, no Python script tests). Nothing here blocks MVP 2; one item (`/metrics` SQL bug) violates a current STANDARDS.md §4.2 claim and should be fixed before the next sign-off sweep.

### Priority queue

| # | Finding | Severity | Where | Effort |
|---|---|---|---|---|
| 1 | `/metrics` page renders `AVERAGE(...)` (invalid SQL) for `average`-type measures | **High** | [scripts/generate_metrics_page.py:48](../scripts/generate_metrics_page.py) | 1 line |
| 2 | `deploy_html` silently swallows `chown` failures | **Medium-High** | [run.sh:48](../run.sh) | small |
| 3 | Allowlist `Bash(sudo cp *)` / `Bash(sudo mv *)` have unbounded blast radius | **Medium** | [.claude/settings.json:180-181](../.claude/settings.json) | small |
| 4 | Duplicate `ward` entries in gold/schema.yml (fct_311_requests + fct_crime_incidents) | **Low** | [dbt/models/gold/schema.yml:136,164,260,272](../dbt/models/gold/schema.yml) | small |
| 5 | CLAUDE.md "LLM Configuration" example shows `claude-sonnet-4-6`; reality is `claude-opus-4-7` | **Low (doc drift)** | [CLAUDE.md:309-314](../CLAUDE.md), [config.yml:2](../config.yml) | 1 edit |
| 6 | CLAUDE.md "Project File Structure" lists `routing_agent.agent.yml` and `somerville_dashboard.app.yml` that don't exist | **Low (doc drift)** | [CLAUDE.md:122,127](../CLAUDE.md) | 1 edit |
| 7 | `docs/schema.sql` claims "source of truth" but declares bare-name schemas (`bronze`, `gold`); runtime uses `main_bronze`/`main_gold`. Agent loads it as context. | **Medium (doc drift, agent-facing)** | [docs/schema.sql:6,16](schema.sql), [agents/answer_agent.agent.yml:14-17](../agents/answer_agent.agent.yml) | medium |
| 8 | `DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/..."` hardcoded across 12 scripts | **Low (EC2-only by design)** | dlt/*.py, scripts/*.py | medium |
| 9 | No Python tests anywhere — only one dbt singular test exists | **Medium** | repo-wide | large |
| 10 | nginx site lacks `X-Frame-Options`, `Content-Security-Policy`, `X-Content-Type-Options`, `HSTS` | **Low-Medium** | [nginx/somerville.conf:20-40](../nginx/somerville.conf) | small |
| 11 | `fct_test_run.sql` hardcodes year range `2015-01-01`–`2027-01-01` | **Low (calendar bomb)** | [dbt/models/admin/fct_test_run.sql:35-36](../dbt/models/admin/fct_test_run.sql) | small |
| 12 | `load_dbt_results.py` append-only; no dedup if `run_results.json` is processed twice | **Low** | [dlt/load_dbt_results.py](../dlt/load_dbt_results.py) | small |
| 13 | TASKS.md self-flagged: LOG.md Recent Sessions at 6 entries, should be 5 | **Low (hygiene)** | [TASKS.md:36](../TASKS.md) | trivial |
| 14 | `block-dangerous.sh` doesn't block backtick command substitution | **Low** | [.claude/hooks/block-dangerous.sh](../.claude/hooks/block-dangerous.sh) | small |
| 15 | Silver layer empty; PII redaction + type-casting + spatial-join work currently lives in Gold | **Known (MVP 3 scope)** | [dbt/models/](../dbt/models/) | large, planned |

---

## 1. Real bugs (action recommended)

### 1.1 `/metrics` page renders invalid SQL for `average` measures — **High**

[scripts/generate_metrics_page.py:48](../scripts/generate_metrics_page.py):

```python
elif mtype == "avg" and expr:
    select = f"AVG({expr})"
...
else:
    select = f"{mtype.upper()}({expr or '*'})"
```

The Airlayer vocabulary uses `average` (correct per [STACK.md](../STACK.md); confirmed at [permits.view.yml:102](../semantics/views/permits.view.yml) and [citations.view.yml:117](../semantics/views/citations.view.yml)). The script branches on the obsolete `avg`, so `average`-type measures fall through to the `else` and emit `AVERAGE(...)` — not a real SQL function.

This violates STANDARDS.md §4.2 row 3 ("Every measure renders with its expanded SQL"). It's a *display* bug — the SQL is never executed by the script — but the public `/metrics` page is part of the trust surface MVP.md calls "the opening note." An analyst reading `AVERAGE(vehicle_mph) AS average_vehicle_speed_on_speed_violations` will not trust the page.

**Fix shape:** rename the branch to `mtype == "average"` (one line). Add a third currently-affected measure path-check by re-running `python scripts/generate_metrics_page.py` and visually diff'ing `portal/metrics.html`.

### 1.2 `deploy_html` swallows chown failures — **Medium-High**

[run.sh:44-51](../run.sh):

```bash
deploy_html() {
    local src="$1"
    local dst="$2"
    if [ -e "$dst" ] && [ ! -w "$dst" ]; then
        sudo chown ubuntu:ubuntu "$dst" 2>/dev/null || true
    fi
    cp "$src" "$dst"
}
```

`|| true` masks any chown error. If passwordless sudo is misconfigured (e.g., sudoers entry was edited, sudo group membership changed), the chown fails silently and `cp` then fails — but the ERR trap fires and the run records `failed` with `error_stage=metrics_page`. The actual root cause (sudoers regression) is invisible.

**Worse:** if `dst` is *writable* (the common path), `cp` proceeds without any verification that the source file was generated. A Python generator that exits 0 without writing the file — possible if `yaml.safe_load` returns `None` for a malformed view — leaves the previous version in place and the run reports success. The trust surface goes stale without anyone knowing.

**Fix shape:** drop `|| true`. Add a precondition: `[ -f "$src" ] || { echo "ERROR: $src not generated"; exit 1; }`. Optionally write to a `.tmp` file and `mv` into place atomically.

### 1.3 Duplicate `ward` column entries in gold/schema.yml — **Low**

[dbt/models/gold/schema.yml](../dbt/models/gold/schema.yml) defines `ward` twice in each of two models:

- `fct_311_requests`: line 136 (description only) and line 164 (relationships test, no description)
- `fct_crime_incidents`: line 260 and line 272 (same shape)

dbt processes both — the relationships test is added correctly — so this is *not a functional bug*. But the schema.yml reads as if each column was defined twice with conflicting metadata, and a future merge that touches one entry will probably forget the other. Consolidate each pair into a single block (description + test).

---

## 2. Documentation drift (correctness items)

### 2.1 CLAUDE.md "LLM Configuration" example is stale

[CLAUDE.md:309-314](../CLAUDE.md):

```yaml
models:
  - name: claude-sonnet-4-6
    vendor: anthropic
    model_ref: claude-sonnet-4-6
```

[config.yml](../config.yml) actually uses `claude-opus-4-7`, and [TASKS.md:63](../TASKS.md) explicitly records the migration ("Switch Answer Agent from Sonnet 4.6 to Opus 4.7, 2026-05-11; commit `a5853d0`"). The agent file [agents/answer_agent.agent.yml:6](../agents/answer_agent.agent.yml) also references Opus.

**Fix:** rewrite the CLAUDE.md snippet to match reality. Add a one-line note that the Opus migration was driven by SPA rate-limit headroom (TASKS.md MVP-1.5 row).

### 2.2 CLAUDE.md "Project File Structure" lists files that don't exist

[CLAUDE.md:121-128](../CLAUDE.md) shows:

```
├── agents/
│   ├── answer_agent.agent.yml
│   └── routing_agent.agent.yml         ← does not exist
└── apps/
    └── somerville_dashboard.app.yml    ← does not exist (only rat_complaints_by_ward)
```

Routing Agent is MVP 4 scope per [BUILD.md §5](../BUILD.md). The dashboard slot lists `somerville_dashboard.app.yml` but only `rat_complaints_by_ward.app.yml` exists. **Fix:** strike the routing line; rename or generalize the apps placeholder.

### 2.3 `docs/schema.sql` declares bare-name schemas — **Medium** (agent-facing)

[docs/schema.sql:6,16](schema.sql) says `Schemas: bronze, gold, admin` and `CREATE SCHEMA IF NOT EXISTS bronze`. Runtime is `main_bronze` / `main_gold` / `main_admin` (the dbt-duckdb pattern of `default_schema + '_' + +schema`), as confirmed by every bronze/gold/admin model and [dbt_project.yml:22-32](../dbt/dbt_project.yml).

This matters because [agents/answer_agent.agent.yml:14-17](../agents/answer_agent.agent.yml) loads `docs/schema.sql` as DDL context, then the system_instructions override with "Gold tables live in the `main_gold` schema." The agent gets correct guidance, but it does so by *contradicting* the context it was given. A future maintainer reading schema.sql will reach for `bronze.raw_311_requests` and get a "table not found" surprise.

The file header also claims "Source of truth for all table definitions. ERD generated from this file." That second claim is no longer true — [scripts/generate_warehouse_erd.py](../scripts/generate_warehouse_erd.py) and friends read the live DuckDB and dbt schema.yml, not schema.sql. The file has demoted itself to "agent context" but the header hasn't updated.

**Fix shape options:**
- (a) Rewrite schema.sql to declare `main_bronze` / `main_gold` / `main_admin`, drop the "source of truth" claim, retitle as "DDL reference for the Answer Agent."
- (b) Drop schema.sql from agent context entirely; rely on the semantic-layer YAML already loaded as context.

(b) is the cleaner endpoint — the semantic layer is the authority per BUILD.md §3 Stage 3. (a) is the safe interim step.

---

## 3. Security & operational fragility

### 3.1 Allowlist `Bash(sudo cp *)` and friends are too broad — **Medium**

[.claude/settings.json:180-185](../.claude/settings.json):

```json
"Bash(sudo cp *)",
"Bash(sudo mv *)",
"Bash(sudo ln -s *)",
"Bash(sudo ln *)",
"Bash(sudo chmod *)",
"Bash(sudo chown *)",
```

There is a deny pattern `Bash(sudo chmod * /etc/*)` and `Bash(sudo chown * /etc/*)` (lines 247-248), but **no equivalent deny for `sudo cp ... /etc/*` or `sudo mv ... /etc/*` or `sudo ln -s ... /etc/*`**. A misuse like `sudo cp /tmp/x /etc/sudoers.d/x` would prompt only because the cp pattern is one of the broadest allows in the list.

These permissions exist because `nginx/somerville.conf` deployment writes into `/etc/nginx/sites-available/`. **Fix shape:** scope by target path (`Bash(sudo cp * /etc/nginx/*)`), then add `/etc/*` to the deny list for `cp`/`mv`/`ln`. Same blast-radius reduction Gordon already applied for chmod/chown.

Smaller adjacent items:
- Deny list has `Bash(rm -rf *)` and `Bash(rm -rfd *)` but not `Bash(rm -fr *)` (flag-order variant — works in GNU rm).
- `git push --force` and `git push -f` are denied but `git push --force-with-lease` is not. Lease form is safer but still rewrites remote refs; consider whether to add it.

### 3.2 `deploy_html` failure mode (cross-ref §1.2) — see above

### 3.3 `block-dangerous.sh` doesn't block backticks — **Low**

[.claude/hooks/block-dangerous.sh:42-46](../.claude/hooks/block-dangerous.sh) blocks `$(...)` but not legacy `` `...` `` command substitution. Modern shells rarely use backticks, and the upstream gist behaves the same way, so this is more polish than urgency. Add a fifth rule if desired.

### 3.4 nginx security headers absent — **Low-Medium**

[nginx/somerville.conf:20-40](../nginx/somerville.conf) sets `Cache-Control` but not `X-Frame-Options`, `Content-Security-Policy`, `X-Content-Type-Options`, or `Strict-Transport-Security`. The portal is public; clickjacking via iframe is the most realistic threat. CSP would mean inventorying the inline `<style>` blocks in the generated HTML — non-trivial. HSTS is moot until HTTPS lands (MVP 4 scope per BUILD.md §5).

Pragmatic interim: add `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff` (both one-liners). CSP and HSTS bundle with the MVP 4 Magic Link + HTTPS migration.

### 3.5 `/etc/environment` permissions — **needs verification on EC2**

[SETUP.md §7](../SETUP.md) places `ANTHROPIC_API_KEY` in `/etc/environment` for systemd `EnvironmentFile=` consumption (correct — `~/.bashrc` doesn't get sourced for non-interactive ssh). Default Linux mode for that file is 644 (world-readable). If a non-root local user (www-data, postgres) can read the file, the API key is exposed.

Untestable from this worktree. **Recommended check on next EC2 session:** `ls -l /etc/environment` — if mode is 644, run `sudo chmod 640 /etc/environment` and verify systemd still sources it (it should — systemd reads as root).

### 3.6 Other infra notes (deliberate tradeoffs, not findings)

- nginx `/api` proxy is unauthenticated; [chat-auth-basic-cleartext.md](limitations/chat-auth-basic-cleartext.md) documents the API-token-burn tradeoff and the MVP 4 migration plan. Acceptable.
- No DuckDB lock-wait in `run.sh`; pipeline assumes systemd timer + manual runs don't overlap. With `OnCalendar=06:00:00` daily and manual runs gated by Gordon's attention, the actual collision risk is low. Not worth engineering until it bites.
- Timer/pipeline coexistence with Oxygen is by design (the systemd unit comments name the rationale). DuckDB allows concurrent readers, only one writer — Oxygen reads, the pipeline writes — so the design is correct, but the assumption isn't called out in ARCHITECTURE.md as explicitly as it could be.

---

## 4. dbt project — narrower findings

The dbt project is the most polished part of the stack. Of the audit candidates flagged by the intermediate pass, only two survived verification:

- **Duplicate `ward` entries** (§1.3 above).
- **Hardcoded year window in `fct_test_run.sql`** lines 35-36 (`'2015-01-01'` to `'2027-01-01'`). Calendar bomb for the end of 2026. Trivial to extend; worth a single TASKS.md follow-up so it doesn't get forgotten in late Q4.

Findings flagged by the intermediate audit that turned out to be false on direct read:

| Claim | Reality |
|---|---|
| "Schema naming mismatch: `bronze` should be `main_bronze` in dbt_project.yml" | dbt-duckdb appends `+schema` to the default `main` profile. `+schema: bronze` produces `main_bronze` — the intended pattern, recorded in memory. |
| "`dim_date` has no tests" | [gold/schema.yml:13-15](../dbt/models/gold/schema.yml) has `not_null` + `unique` on `date_dt`. |
| "`dim_kpi_topic` has no tests" | [gold/schema.yml:478-507](../dbt/models/gold/schema.yml) has `not_null` + `unique` on `topic` plus `not_null` on every other column. |

Two genuine MVP-3-shaped observations (named here for completeness, not action):

- **Gold currently absorbs Silver-shaped work.** [fct_permits.sql](../dbt/models/gold/fct_permits.sql) does the spatial ward join; [fct_311_requests.sql](../dbt/models/gold/fct_311_requests.sql) does type casts at gold-build time. Per BUILD.md §3 the medallion convention is bronze=raw, silver=cleaned/typed, gold=denormalized. Currently bronze is raw and gold is "everything else." This is *acknowledged* (STANDARDS.md §5.3 stubs the Silver standard) but isn't currently flagged as a limitation — there's no `silver-deferred-gold-doing-double-duty.md` in [docs/limitations/](limitations/). Worth one, even if MVP 1's signoff explicitly accepted the gap.
- **PII redaction is upstream-applied for crime ([crime-bronze-restricted-from-analysis.md](limitations/crime-bronze-restricted-from-analysis.md)) but the project layer has no defense in depth.** That's a Silver thing; mention here for the MVP 3 prep.

---

## 5. Python scripts — patterns to clean before scaling

The scripts work and are clearly written. The patterns worth attention are the ones that won't survive growth:

- **No tests anywhere.** Only `dbt/tests/singular/dq_drift_fail_guardrail.sql` exists. None of the ~20 Python build scripts has a pytest fixture. Each generator's correctness is verified by running the pipeline end-to-end and visually checking the portal. Cheap test wins: parse the Airlayer YAML and assert every measure-type maps to an SQL-renderable branch (would have caught §1.1); assert every `.app.yml` parses and references real semantic-layer measures; assert `docs/limitations/_index.yaml` matches the actual `.md` files in the dir.
- **`DUCKDB_PATH = "/home/ubuntu/oxygen-mvp/data/somerville.duckdb"` duplicated across 12 files.** Acceptable today because EC2 is the only host, but a single shared constant (`scripts/_paths.py`, or an env-var fallback like `build_socrata_inventory.py:24` already uses) would make a future migration trivial. Not urgent.
- **Status string constants scattered.** `'success' / 'partial' / 'failed' / 'in_progress'` appear in pipeline_run_start.py, pipeline_run_end.py, generate_trust_page.py, and `run.sh` itself. A typo in any one place would silently corrupt run records. A `scripts/_run_status.py` module with `SUCCESS / PARTIAL / FAILED / IN_PROGRESS` constants would close it.
- **`load_dbt_results.py` is append-only.** Re-running the pipeline twice on the same `run_results.json` (a non-idempotent debugging step) would double-write. The script writes one row per dbt test per run; with `run_id` as a column, a dedup on `(run_id, test_id)` would make it safe.
- **`profile_tables.py` opens DuckDB without try/finally.** On exception the connection leaks until process exit — fine in practice (the process *does* exit) but signals a class of cleanup hygiene worth standardizing.

---

## 6. Operational ergonomics

- **TASKS.md self-flagged hygiene item.** [TASKS.md:36](../TASKS.md): "LOG.md Recent Sessions rotation — currently 6 entries (41-46); should be 5 max per the rule." Self-corrected after Session 52 rotation, but the queued line is stale and confusing. Strike it.
- **CLAUDE.md's "Project File Structure" section** doesn't list `nginx/`, `systemd/`, `PHILOSOPHY.md`, `PRODUCT_NOTES.md`, `DASHBOARDS.md`, `PROMPTS.md`, or several other artifacts now in the repo. The tree is from earlier MVP 1 and hasn't kept pace. Refresh.
- **`session-starter.md` and `slack-update-format.md`** live at repo root with no mention in any authority doc except their own headers. They probably should be either moved under `docs/` or named in the CLAUDE.md hierarchy so a fresh reader knows what they're for.
- **`docs/schema.sql` self-mismatch** (cross-ref §2.3). Same documentation-drift family.

---

## 7. What I checked and didn't find

For the record, so the next reviewer doesn't redo the work:

- **Hardcoded metrics in agent prompt / app YAML / scripts** — none. The semantic-layer-as-single-source-of-truth discipline is holding. The agent's system_instructions never restate a measure's SQL; it tells the agent which schemas to query and lets the views do the rest.
- **Secrets in repo** — none found in code, dlt, scripts, agents, apps, settings.json. `.htpasswd` is correctly out-of-repo. `.gitignore` covers `.env`.
- **`{{ ref() }}` discipline in dbt SQL** — clean. No models reference raw tables directly. Sources use `{{ source() }}`.
- **Description completeness in schema.yml** — every model and every column has a substantive description (not "TODO" / "tbd"). Bronze schema.yml runs ~600 lines of carefully-worded docs.
- **Topic ↔ view coupling** — every topic references existing views; no orphans.
- **Dashboard YAML structure** — `rat_complaints_by_ward.app.yml` follows the DASHBOARDS.md three-tier base + recent-situation + trust signals contract.
- **Trust contract enforcement** — [agents/answer_agent.agent.yml:23-72](../agents/answer_agent.agent.yml) imposes the row-count / answer / citations / limitations shape with explicit hard rules. Strong.
- **Verification gates per CLAUDE.md "Live-functional boxes" rule** — every `[x]` in STANDARDS.md §6 carries either a commit hash or a re-runnable verification command in the parenthetical.

---

## 8. Recommended sequencing

If you do nothing on the medium/low items, the MVP 1 → MVP 2 path is not at risk. But if you have a tidy-day, the rough order of value:

1. **Fix `/metrics` `average` rendering** (§1.1). One line. Restores STANDARDS.md §4.2 row 3 to honest.
2. **Tighten `deploy_html`** (§1.2). Drop `|| true`; assert source file exists; switch to write-temp-then-mv.
3. **CLAUDE.md doc-drift sweep** (§2.1, §2.2, §6 second bullet). 10 minutes; saves a future maintainer half a day of confusion.
4. **`docs/schema.sql` reconciliation** (§2.3). Choose: rewrite with `main_*` schemas + retitle, OR drop from agent context. Either way, file the limitation entry if not done in this pass.
5. **Allowlist scoping for `sudo cp` / `sudo mv` / `sudo ln`** (§3.1). 5-minute scope-narrowing exercise that closes a real foot-gun.
6. **Add the first Python script test** (§5 first bullet). The `average` bug would have been caught by `assert mtype in {"count","sum","average","min","max","count_distinct","median","custom"} for view in views for m in view.measures` — three lines. Set the precedent; let MVP 3 build on it.
7. **De-dup the gold ward entries** (§1.3) and **strike the stale TASKS.md line** (§6 first bullet). Both trivial.
8. **Add `X-Frame-Options` and `X-Content-Type-Options` to nginx** (§3.4). The other two headers wait for MVP 4 HTTPS.
9. **EC2 check: `/etc/environment` mode** (§3.5).
10. Everything below this point is medium-term: Silver layer (MVP 3 by design), Python test framework (incremental), DuckDB lock-wait (only if the collision actually happens), backtick blocking in the hook (polish).

---

## 9. What this review explicitly does *not* propose

To keep this report honest about its scope: this is a findings document, not a roadmap shift.

- **No new MVPs or feature scope.** Builder-CLI dashboards (Plan 18/19), MVP 3 survey curation (Plan 24), Slack/MCP/A2A (MVP 4) all remain on the queue Gordon already set.
- **No challenge to the configuration-over-custom-code default.** Every "Python script smell" above is a polish item, not an argument to rewrite something.
- **No challenge to the deferred-Silver decision.** MVP 1 sign-off accepted the trade-off explicitly; MVP 3 plans Silver. Surfaced here for context, not for re-litigation.
- **No security-theater additions.** CSP, HSTS, secrets-manager migration belong with the MVP 4 HTTPS pivot; pulling them forward would cost more than they save now.

---

*Generated 2026-05-17 13:10 ET by a five-pass review of the codebase at worktree `bold-dirac-7b6669` (parent `a5616e0`). All claims here were checked against the actual files; three findings from the intermediate audit were retracted as false positives (§4). The report is meant to be skimmable as a punch list and citable as evidence — every finding gives file:line.*
