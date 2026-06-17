# PROJECT MIGRATION SUMMARY — 2026-06-07

> **Purpose.** Gordon is moving this project to a **new Claude account / different email**.
> This document hands the new Claude chat (architect) and Claude Code (executor)
> everything needed to restart cold — especially the state that is **NOT in the
> GitHub repos**: in-flight branches, the auto-memory, live EC2 + access, and
> pending decisions. An identical copy is committed to both repos.
>
> **Read this first, then each repo's `CLAUDE.md`.**

---

## 0. The single most important fact

**The GitHub repos, the EC2 boxes, the SSH keys, and Tailscale are NOT tied to the
Claude account.** They live under the **`ironmonkey88` GitHub account**, on AWS, and
on Gordon's Mac. Moving Claude accounts does **not** move any of them. What is lost
in the move is only the **Claude.ai chat history** and possibly the **Claude Code
auto-memory** (see §4). Everything else just needs the new account to *authenticate*
to it (`gh auth login`, same machine or copy keys — see §7).

---

## 1. The two repos (don't conflate them)

There are **two independent repos** that share a methodology but diverge in code.
This distinction is load-bearing — conflating them has burned time before.

| | **oxygen-mvp** | **stack-in-a-box** |
|---|---|---|
| What | Somerville civic-analytics build (the real product) | Generic, dataset-agnostic analytics-stack *template* extracted from oxygen-mvp's patterns |
| Local path | `/Users/gordonwong/claude-projects/oxygen-mvp` | `/Users/gordonwong/claude-projects/stack-in-a-box` |
| GitHub | `https://github.com/ironmonkey88/oxygen-mvp` | `https://github.com/ironmonkey88/stack-in-a-box` (public, MIT) |
| Dataset | Somerville 311 / crime / permits / citations / at-a-glance / happiness survey | NYC 311 *smoke* data (`erm2-nwe9`) |
| `main` HEAD (2026-06-07) | `fcafaae` — Plan 49 (PHILOSOPHY creed reconcile) | `c61484a` — Plan 7 (METHODOLOGY R5–R8) |
| Stage | 4-MVP sequence, **MVP 2 active** | Plans 1–3 + 5–7 merged; **Plan 4 in-flight (unmerged)** |
| Plan ledgers | own LOG.md / TASKS.md / `docs/prompts/plan-NN-*` | own LOG.md / TASKS.md / `docs/prompts/` |

Each repo's `CLAUDE.md` opens with a "Which repo is this?" callout. **Follow the
CLAUDE.md of whichever repo you're in.** Their plan numbers, MVP sequences, smoke
datasets, and EC2 hosts are separate — never import one's into the other.

---

## 2. Roles & working style

- **Gordon = the architect.** He plans in the **Claude.ai web chat**, role-plays a
  non-technical department head, and **directs in chat only — he does not type into
  files**. Code does all file/repo/EC2 work.
- **Claude Code = the executor.** Receives prompts (often pasted plan specs, or files
  in `docs/prompts/plan-NN-*.md`), runs the **PROMPTS.md §5 workflow** (restate
  outcome → pre-flight → execute → verify → commit → report).
- **Gordon's background:** experienced Snowflake/dbt/Looker architect, newer to
  Oxygen. Lead explanations with dbt/Looker analogies; explain how Oxygen differs.

---

## 3. The auto-memory (NOT in the repos — may be lost in the move)

Claude Code keeps file-based memory at
`~/.claude/projects/-Users-gordonwong-claude-projects-oxygen-mvp/memory/` (17 files).
This is **machine-local under `~/.claude`** and **keyed to the oxygen-mvp path**. If
the new account reuses the same `~/.claude` on the same Mac, it persists; if not,
**it is lost** — so the durable facts are reproduced here. Recreate them as memory in
the new account if `~/.claude` doesn't carry over.

- **User profile:** dbt/Looker/Snowflake architect new to Oxygen — lead with analogies.
- **Two sibling repos — don't conflate** (see §1).
- **User role: no typing** — Gordon directs in chat; Code does all file work.
- **EC2-first workflow** — all code/data runs on EC2; the local dir is docs only.
- **dbt-duckdb schema naming** — schemas are `main_bronze` / `main_gold` / `main_admin`, not bare `bronze`/`gold`.
- **Autonomous execution** — push + open PR + merge are autonomous for *verified* work *on the same repo*; **pause** for destructive ops, schema decisions, cross-repo PRs, and message-sending.
- **settings.json editing** — Code may proactively edit `.claude/settings.json` to allowlist read-only commands.
- **Bash command form** — use `git -C <path>`, never `cd && git`; **never chain with `&&` / `;` / `|`** (a safety hook denies them and the allowlist won't match); always `git commit -F <file>`, never inline `-m`.
- **No SSH heredocs** — write ad-hoc SQL/Python to `scratch/`, scp, then run via a simple `ssh ... -f /tmp/foo`.
- **Chat↔Code handoff format** — end-of-thread summary = gate table + Shipped + Worth flagging + Next.
- **Verify quantitative claims** — numbers in briefs/LOG rows are hypotheses; query the warehouse before propagating them into user-facing artifacts.
- **No parallel Code session** — Gordon doesn't run a second Code; unfamiliar commits are Code's own from earlier, not another author.
- **Git + SSH gotchas** — scp→pull needs `git checkout --` first; the local hook scans SSH command *strings* (use a scratch wrapper); a worktree can't checkout `main` if the parent has it (use `-b <new> origin/main`).
- **90-second boot audit** — at session start: `gh pr list`, local fetch + log vs `origin/main`, EC2 `git status` — catches cross-session drift.
- ⚠️ **`project_status.md` in memory is STALE** (it still says "MVP 1 sign-off blocked"). Ignore it; the live status is in each repo's `LOG.md`.

---

## 4. In-flight / unmerged work (NOT fully in `main`)

### 4a. stack-in-a-box **Plan 4** — pin + contract gates + lock-aware refresh + clean-box (IN-FLIGHT)
- **Branch:** `claude/plan-04-pin-gates-lockaware` (pushed to origin — safe across the move). **NOT merged.** Plans 5–7 (docs) leapfrogged it.
- **Prompt:** committed at `stack-in-a-box/docs/prompts/plan-04-pin-gates-lockaware.md` (full spec + Code's restatement).
- **DONE & verified on the Plan-3 EC2 (commits on the branch):**
  - `3947b7b` Phase 2 — **pin Oxygen `0.5.54`** in `scripts/setup/03_install_oxygen.sh` via `OXY_VERSION` + a verify-gate assertion that the installed version matches the pin.
  - `ae6024e` Phase 3 — **contract-level gates (methodology R1):** `oxy validate` gate in step 09 before the smoke run, and a **live agent-query gate** in step 10 (asks the agent a canned question *through oxy*, asserts a trust-contract answer — catches the Plan-3 "green but every query broken" class).
  - `6feb655` — fix: script 03 **restarts a running `oxy.service` after a reinstall** (reinstalling the binary while the service runs left it on a deleted inode holding an abnormal DuckDB RW lock — found during Phase-3 verification).
- **PENDING (not built):**
  - **Phase 4** — lock-aware refresh (methodology R2): wrap `run.sh`'s write in an exclusive `flock`; read-side retry-with-backoff; instrument **writer `lock_held_seconds`** (via `scripts/pipeline_run_end.py` → `main_admin.fct_pipeline_run_raw`) and **reader retry-wait** into the admin schema; name a data-driven upgrade threshold in `IMPROVEMENTS_BACKLOG.md` (snapshot/atomic-swap deferred to that trigger). Only re-enable `--now` timer activation if flock+retry is proven; else keep boot-deferred.
  - **Phase 5** — flip `SMOKE_MODE` default `medium` → **`small`** (10k; `medium`/~250k hit live NYC-311 SODA read-timeouts) in `dlt/smoke_test_pipeline.py` + `scripts/setup/09_first_run.sh`; then verify **unattended defer-and-resume** (force a mid-run failure, confirm idempotent merge-on-`unique_key` resumes clean).
  - **Phase 7** — portal items: (1) keep the basic portal as the simple default; (2) dbt-docs `/docs/` "← Back to portal" link via a `{% docs __overview__ %}` block with a **plain-Markdown** link (dbt-docs sanitizes raw HTML — see CLAUDE.md §10); (3) static `portal/about.html` + an "About" item in `scripts/_nav.py`, synced by `run.sh` like `index.html` (no generator) — documents *the template + how to customize it*.
  - **Phase 6** — **clean-from-scratch confirm on a FRESH `t4g.medium`** (Plan 3 was fix-and-resume on one box). **BLOCKED on Gordon provisioning a new box.** Confirm step 08's `enable` (no `--now`) line actually runs (Plan 3 hit the "already enabled" branch). If clean: remove the CLAUDE.md §1 install caveat entirely.
  - **Phase 8** — findings + `IMPROVEMENTS_BACKLOG.md` threshold values + LOG/TASKS/session + open the PR.
- **Agreed dev model:** build/verify Phases 4/5/7 on the **existing Plan-3 box**; use a **fresh box** only for Phase 6.

### 4b. oxygen-mvp **Plan 47** — tech + test debt *assessment* (report-only) — **OPEN PR #76**
- Branch `claude/plan-47-techdebt-assessment`, last updated 2026-06-03. Open, unmerged. Awaiting review/merge. This is the *assessment*; the *decision register* below is its sibling.

### 4c. oxygen-mvp **tech-debt decision register + four-lens discipline** — **NOT STARTED**
- A documentation/discipline plan Gordon specced on 2026-06-05. Halted at Phase 0 because the plan number was ambiguous. **Full prompt preserved at `oxygen-mvp/docs/prompts/_pending-tech-debt-decision-register.md`.**
- **Plan number:** numbers churned (47 = the open PR #76; 48 = APPROACH renumber; 49 = PHILOSOPHY creed). **Next free is likely ~50 — read the live LOG.md Plans Registry and assign it; do not guess** (Phase 0 explicitly halts on this).

### 4d. Other unmerged branches
Both repos carry old feature branches; treat `main` as truth and ignore stale branches (a `gh pr list` + branch-vs-main audit at boot catches drift — see §3 boot audit).

---

## 5. Live infrastructure (EC2 — running, costing money)

Both boxes are reached over **Tailscale** (tailnet `taildee698.ts.net`, account `gordon@`). The Mac is a tailnet node. **Tailscale `--ssh` is intentionally OFF** on both (it preempts OpenSSH and breaks `/etc/environment` env loading).

| | **oxygen-mvp EC2** | **stack-in-a-box EC2 (the "Plan 3 box")** |
|---|---|---|
| Reach | Tailscale alias `oxygen-mvp` → `oxygen-mvp.taildee698.ts.net` | `stack-in-a-box.taildee698.ts.net` (Tailnet IP `100.81.97.55`; public IP was `18.219.78.136`) |
| Public ports | 80 only (portal); SSH + :3000 closed at the AWS SG | 80 only; **22 + 3000 closed** at the SG |
| Oxygen | (per repo) | **0.5.54** (pinned by Plan 4) |
| Warehouse | Somerville data, `data/somerville.duckdb` | NYC 311 smoke, `data/stack.duckdb`, populated (10k smoke rows) |
| Notes | the production box | a **demo box** stood up in Plan 3 — used as the Plan 4 dev box. Carries install scaffolding in `~/`: `launch_bootstrap.sh`, `ask_agent.sh`, `run_oxy.sh`, and **`~/.sib-secrets/`** (the real Anthropic + Tailscale keys, mode 600). |

⚠️ **Cost / cleanup:** both EC2 instances appear to be running. Decide whether to keep
the stack-in-a-box demo box (needed for Plan 4 dev) or stop/terminate it. If
repurposing it, remove `~/.sib-secrets/`.

---

## 6. Access & secrets (machine-dependent — copy these IF the Mac also changes)

If staying on the **same Mac**, these persist and only the Claude account changes —
just `gh auth login` under the new account. If moving to a **new machine**, copy:

- **SSH keys** (`~/.ssh/`): `stackinaboxdemo.pem` (the stack-in-a-box box). The
  oxygen-mvp box key is also under `~/.ssh/` (the repo's `settings.local.json`
  allowlists `Read(//Users/gordonwong/.ssh/**)`). `chmod 400` after copying.
- **Local secret files:** `~/.config/sib/anthropic.key`, `~/.config/sib/tailscale.key`
  (real keys used to stand up the stack box).
- **Tailscale:** ensure the new machine is logged into the same tailnet (`gordon@` /
  `taildee698.ts.net`), else the EC2 hostnames won't resolve.
- **GitHub:** `gh auth login` as / with access to `ironmonkey88`.
- **Anthropic API key:** the EC2 boxes hold their own real keys in `/etc/environment`.
  The Claude Code session key is separate (and was proxied via a custom
  `ANTHROPIC_BASE_URL` — Claude Code's own; not the box key).

---

## 7. Conventions the new Code must follow (mostly in-repo — pointers)

- **Authority:** each repo's `CLAUDE.md` is the operating contract. Read it first.
- **Prompts:** `PROMPTS.md` (both repos) — the coding/info prompt shapes + the §5
  9-step receipt workflow + the `docs/prompts/plan-NN-*.md` + `.report.md` convention.
- **Methodology (shared, cross-repo):** `METHODOLOGY.md` (root of both repos) — the
  distilled engineering rules **R1–R8** + the Code-proposes / human-approves sync
  process. R1–R4 are install/infra rules from Plan 3/4; R5–R8 are reasoning/build
  disciplines. **The first oxygen→stack sync pass (auditing R1–R3 against oxygen's
  code) is a pending, human-ratified step — report-only, do not auto-apply.**
- **Convictions:** `PHILOSOPHY.md` (+ `APPROACH.md` reference standard in stack);
  not operational authority but consult for tiebreakers.
- **Bash safety hook:** no `&&`/`;`/`|` chains, no `$(...)`, no leading `cd`, no
  shell redirects to create files; one command per call; `git -C` + `git commit -F`.
- **Autonomous-merge policy:** push/PR/merge autonomously for *verified* same-repo
  work; **pause** for cross-repo, destructive ops, message-sending, or unverified
  live-functional gates. (Plan 3/4 install PRs were surfaced for review, not
  auto-merged, per their prompts.)

---

## 8. First-session checklist for the new account

1. `gh auth login` (access to `ironmonkey88`); confirm Tailscale is up (`tailscale status` shows both EC2 nodes).
2. In each repo: `git fetch`, confirm local `main` == `origin/main` (oxygen `fcafaae`, stack `c61484a` as of this doc — both will have moved on if work continued).
3. `gh pr list` on both repos — expect oxygen **PR #76 (Plan 47 assessment)** still open unless merged.
4. Recreate the §3 memory facts in the new account's memory if `~/.claude` didn't carry over.
5. Decide the immediate thread:
   - **Finish stack-in-a-box Plan 4** (Phases 4/5/7 on the existing box; Phase 6 needs a fresh box) — branch `claude/plan-04-pin-gates-lockaware`, spec at its `docs/prompts/`.
   - **Merge or iterate oxygen PR #76** (tech-debt assessment).
   - **Start the tech-debt decision register** (`docs/prompts/_pending-tech-debt-decision-register.md`; assign the real next plan number ~50).
6. Decide EC2 disposition (keep the stack demo box for Plan 4 dev, or stop it — §5).

---

## 9. Fresh sibling setup — from zero (NEW LAPTOP + new account)

This move is **both a new Claude account and a new Mac.** Nothing local carries over
automatically — but most of what matters is in GitHub. Steps:

### 9a. Install tooling on the new Mac
- **Claude Code** (the CLI harness) + sign in to the new Claude account.
- **git**, **gh** (GitHub CLI), **Tailscale** client. (Python 3.12 optional — the
  local dir is docs-only per the EC2-first workflow; pipelines run on EC2.)
- Optional: **shellcheck** (used to lint the stack-in-a-box setup scripts).

### 9b. Clone both repos to the exact expected paths
Paths are load-bearing — the auto-memory key and various docs assume `~/claude-projects/<repo>`:
```
mkdir -p ~/claude-projects
git clone https://github.com/ironmonkey88/oxygen-mvp.git      ~/claude-projects/oxygen-mvp
git clone https://github.com/ironmonkey88/stack-in-a-box.git  ~/claude-projects/stack-in-a-box
```

### 9c. Authenticate & reconnect
- `gh auth login` — access to **`ironmonkey88`**.
- **Tailscale:** log into the `gordon@` tailnet; `tailscale status` must show both EC2 nodes (`oxygen-mvp`, `stack-in-a-box`), else the hostnames won't resolve.
- **SSH keys → `~/.ssh/`:** copy `stackinaboxdemo.pem` (stack box) + the oxygen-mvp box key from the old Mac; `chmod 400` each.
- **Secrets → `~/.config/sib/`:** copy `anthropic.key` + `tailscale.key` if continuing stack-in-a-box installs.
- **Large-push gotcha:** on fresh clones, if a `git push` fails with HTTP 400 / "remote end hung up" on a binary-heavy commit, set once per repo: `git -C <repo> config http.postBuffer 524288000`.

### 9d. The allowlist — what migrates, what to recreate ⭐ (the thing not to lose)
**The bulk is already safe — it is git-tracked and arrives with `git clone`, zero manual work:**
- `<repo>/.claude/settings.json` — the universal allowlist (**oxygen 342 lines, stack 235 lines**).
- `<repo>/.claude/hooks/block-dangerous.sh` — the bash-safety hook.

These are committed in BOTH repos. Cloning restores them verbatim. **This is ~95% of the painstaking work and needs nothing.**

**Recreate only if you want them (per-machine, gitignored, NOT cloned):**
- `<repo>/.claude/settings.local.json` — per-machine scratch (SSH-key Read path, one-off
  commands, local MCP tool names). Policy: load-bearing patterns belong in the committed
  `settings.json`, so this file is mostly disposable. Its one durable entry —
  `Read(//Users/gordonwong/.ssh/**)` — has the **same path** on the new Mac (same username),
  so even that copies cleanly. stack-in-a-box has no local file. The oxygen-mvp local file's
  full contents are snapshotted in the **Appendix** below so nothing is lost; most entries are
  one-off session commands you can ignore. The useful patterns to re-add as you go:
  `Read(//Users/gordonwong/.ssh/**)`, `Bash(gh repo *)`, `Bash(gh api *)`, `Bash(brew *)`,
  `Bash(pip3 install *)`, `Bash(tailscale ping *)`, `WebSearch`.
- `~/.claude/settings.json` (user-global) — **UI prefs only** (theme, notifications). No
  allowlist content; nothing to migrate. (For reference it was: `theme: dark`,
  `remoteControlAtStartup: true`, `agentPushNotifEnabled: true`, `inputNeededNotifEnabled: true`.)

**Verify the allowlist survived:** open Code in each repo and (1) run an allowlisted command
(e.g. `git -C <repo> status`) — should NOT prompt; (2) try a chained command (`echo a && echo b`)
— should be **hook-denied** (proves `block-dangerous.sh` is active). If both hold, the allowlist
is fully restored.

### 9e. You're ready when…
- Both repos cloned under `~/claude-projects/`; `git status` clean; local `main` == `origin/main`.
- `gh pr list` works on both (oxygen PR #76 visible).
- `tailscale status` shows both EC2 nodes; `ssh -i ~/.ssh/stackinaboxdemo.pem ubuntu@stack-in-a-box.taildee698.ts.net 'echo ok'` returns `ok`.
- In Code: allowlisted commands don't prompt; chained commands are hook-denied.
- The §3 memory facts are recreated in the new account's memory (new `~/.claude`).

---

## Appendix — `oxygen-mvp/.claude/settings.local.json` snapshot (2026-06-07)

Verbatim copy of the gitignored per-machine allowlist, preserved so nothing is lost.
**Most entries are one-off session commands** (SSH to the stack box during Plan 3/4) and
are safe to ignore; the reusable patterns are listed in §9d. No secrets — paths + command
patterns only.

```json
{
  "permissions": {
    "allow": [
      "Read(//Users/gordonwong/.ssh/**)",
      "Bash(gh repo *)",
      "Bash(gh api *)",
      "Bash(brew list *)",
      "Bash(brew install *)",
      "Bash(pip3 install *)",
      "Bash(tailscale ping *)",
      "WebSearch",
      "Bash(command -v aws)",
      "Bash(env)",
      "mcp__2da45f02-7adc-4c48-a12b-fcbef7788140__get_file_metadata",
      "mcp__2da45f02-7adc-4c48-a12b-fcbef7788140__read_file_content"
    ],
    "_note": "Curated to the reusable patterns. The live file also held ~35 one-off, fully-qualified session commands (ssh ... ubuntu@stack-in-a-box ... 'bash launch_bootstrap.sh --only NN', specific mkdir/cp/grep/find/shellcheck invocations against absolute stack-in-a-box paths) — all disposable scratch from the Plan 3/4 install work; do not migrate. The committed .claude/settings.json is the durable allowlist."
  }
}
```

---

*Authored by Claude Code on 2026-06-07 from live repo + memory + EC2 state. Identical
copy committed to both repos at root. If anything here disagrees with a repo's live
`LOG.md`/`CLAUDE.md`, the live repo files win — this is a point-in-time snapshot.*
