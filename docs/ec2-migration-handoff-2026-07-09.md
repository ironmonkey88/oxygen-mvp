# EC2 Cross-Account Migration — Handoff (2026-07-09 15:23 ET)

**For:** a fresh Claude Code session in Gordon's **new Claude account**, picking up an **in-progress** EC2 cross-account migration and then doing **development on the new instance**.

**Read order:** this doc → `docs/ec2-account-migration-checklist.md` (the full runbook) → `docs/MIGRATION_SUMMARY.md` (project-wide working agreements + in-flight state) → `CLAUDE.md` / `SETUP.md`. This doc is the **live state + remaining steps** for the migration specifically; the checklist is the generic procedure; MIGRATION_SUMMARY is how-we-work.

---

## TL;DR — where we are

Migrating the live `oxygen-mvp` EC2 instance from its **source AWS account** to a **new standalone destination account** via an **AMI clone**, staying in **us-east-2 (Ohio)** (chosen for Boston-area users + same-region = no cross-region copy).

**Done:** box quiesced + reconciled to clean `main`; AMI created; shared cross-account; copied into the destination account.
**Next action:** finish **Phase 4 — launch the instance** in the destination account, then **Phase 5 — re-auth Tailscale + verify env**, then **Phase 6 — bring services up + verification gate**.

⚠️ **The Somerville portal is currently DOWN.** The source box was quiesced (`oxy.service` + 3 timers stopped) and stopped for imaging. Service is not restored until the **new** instance is up (Phase 6). Prioritize Phases 4–6.

---

## Concrete facts & IDs (everything gathered so far)

| Item | Value |
|---|---|
| **Source instance** | `i-0e08479a1e757c118` · `t4g.medium` · ARM64 · Ubuntu 24.04 · 20 GB gp3 **unencrypted** root |
| Source region / AZ | **us-east-2 / us-east-2b** |
| Source public IP (old) | `18.224.151.49` |
| Source base AMI | `ami-0257f1929a4806405` |
| Source IAM role | **none** (box can't call AWS APIs itself — all AWS actions are Gordon-in-Console) |
| **Migration AMI** (source acct) | name `oxygen-mvp-migration-2026-07-09` · associated snapshot `snap-077c89280c426b63f` · shared with dest acct + **Allow EBS volume creation** ✅ |
| **Destination account** | `103444675041` (standalone, NOT in an Organization with source) |
| Destination region | **us-east-2** (same as source) |
| **Destination-owned AMI** | **`ami-0ef4ca592a4bf8ce3`** (copied, Available, owned by `103444675041`) |
| Key pair (dest) | `oxygen-mvp-dest` (.pem — **Gordon to confirm local path**, e.g. `~/.ssh/oxygen-mvp-dest.pem`, `chmod 400`) |
| Security group (dest) | `oxygen-mvp-sg` — inbound **HTTP 80 from 0.0.0.0/0** + **SSH 22 from My IP** (temp) |
| **New instance** | **id + public IP: TBD** — capture from Phase 4 launch |
| Encryption blocker | **N/A** — root volume unencrypted, so no KMS re-encrypt was needed |

**Repo state on the (old) box at handoff:** on `main`, clean, `HEAD = 50ca146`. The box had been parked on stale branch `claude/plan-44-...` behind main; reconciled to main before imaging. **The imaged 234 MB `somerville.duckdb` predates the survey silver/gold models** (main was 42 files / +4255 lines ahead of what the box had built) — the first `./run.sh` on the new box will build `stg_happiness_survey`, `fct_happiness_survey`, the survey dims, and the new semantics.

**TASKS.md:** the migration is tracked as a `[~]` entry under "Next Focus" (added 2026-07-09). Update it to `[x]` at Phase 7 with evidence.

---

## Remaining steps (copy-paste detail)

### Phase 4 — Launch (destination account, us-east-2) — IN PROGRESS

If not already launched:
1. **EC2 → AMIs** → select **`ami-0ef4ca592a4bf8ce3`** → **Launch instance from AMI.**
2. Name `oxygen-mvp` · type **`t4g.medium`** (ARM) · key pair **`oxygen-mvp-dest`**.
3. Network → Edit: default us-east-2 VPC · **Auto-assign public IP: Enable** · SG **`oxygen-mvp-sg`** (HTTP 80 anywhere + SSH 22 My IP).
4. Storage: inherited 20 GB gp3. **Launch.**
5. When **Running**, record **new instance ID + public IPv4**. Fill them into the table above and TASKS.md.

### Phase 5 — Re-establish identity & access (over the temp SSH-22 rule)

The image carries the **old node's Tailscale state** — it must be wiped and re-authed, or it collides with the source node. First connection uses the `.pem` over the temporary SSH-22 rule:

```bash
ssh -i ~/.ssh/oxygen-mvp-dest.pem ubuntu@<NEW_PUBLIC_IP>
```

Then on the box (write these to a scratch script + scp per the no-heredoc rule; don't chain with `;`/`&&`):
```bash
sudo systemctl stop tailscaled
sudo rm -f /var/lib/tailscale/tailscaled.state
sudo systemctl start tailscaled
sudo tailscale up            # follow the auth URL; keep --ssh OFF (SETUP.md §12 — it breaks /etc/environment loading)
```
- Remove the **old node** from the Tailscale admin console; rename the new node to `oxygen-mvp` if you want the `oxygen-mvp.taildee698.ts.net` name back.
- **Update local `~/.ssh/config`** `oxygen-mvp` alias → new Tailnet HostName (or new public IP).
- Verify env survived the image:
  ```bash
  ssh oxygen-mvp 'echo $ANTHROPIC_API_KEY | head -c 14'   # sk-ant-api03-E
  ssh oxygen-mvp 'echo $OXY_DATABASE_URL'                 # postgres URL
  ```
- **Consider rotating `ANTHROPIC_API_KEY`** — it traveled inside the image into a different AWS account. If rotating, update `/etc/environment` and restart `oxy.service`.
- Once Tailscale works, **remove the temporary SSH-22 rule** from `oxygen-mvp-sg` (leave port 80 only; :3000 stays Tailnet-only).

### Phase 6 — Bring services up + verification gate

```bash
cd ~/oxygen-mvp && git pull origin main          # image may be behind
sudo systemctl daemon-reload                      # units changed on disk during the pre-image pull
sudo systemctl start oxy.service                  # confirm the docker postgres container recreates (Requires=docker.service)
sudo systemctl start pipeline-refresh.timer source-health-check.timer profile-tables.timer
sudo systemctl list-timers --all | grep -E 'pipeline-refresh|source-health|profile'
sudo nginx -t && sudo systemctl reload nginx      # (run as two calls — no && on the box per bash-safety hook)
```
**Verification gate (re-run, don't infer from "instance running"):**
- `curl -sI http://<NEW_PUBLIC_IP>/` → 200 (portal); `/metrics`, `/trust` → 200.
- `http://oxygen-mvp.<tailnet>:3000/` reachable over Tailscale.
- `/chat` prompts Basic Auth and lands in the workspace (`.htpasswd` travels in the image).
- One Answer Agent question end-to-end with the **trust contract** (SQL + row count + citation) — prefer `scripts/rendered_page.py` per STANDARDS §8.
- **`./run.sh` once, end-to-end** — this builds the survey models missing from the imaged DuckDB; confirm a clean run with a fresh `RUN_ID`.

### Phase 7 — Cutover & cleanup

- Update `SETUP.md` + `CLAUDE.md` with the **new public IP** and (if changed) the **Tailnet hostname**; the old `18.224.151.49` references are stale.
- **Keep the source instance STOPPED** (not terminated) as rollback until the new box runs clean for a few daily cycles.
- Then decommission source: terminate the source instance, delete the `oxygen-mvp-migration-2026-07-09` AMI + `snap-077c89280c426b63f` in the source account, remove the old Tailscale node.
- Mark the TASKS.md migration entry **`[x]`** with verification evidence; write a session file per the LOG protocol.

---

## Gotchas specific to this box (carry these forward)

- **Tailscale `--ssh` stays OFF.** It bypasses OpenSSH's PAM stack and silently breaks `/etc/environment` env-var loading (PATH / `ANTHROPIC_API_KEY` / `OXY_DATABASE_URL` all missing in non-interactive ssh). SETUP.md §12.
- **`/etc/environment` is the env source of truth** — not `~/.bashrc` / `~/.profile` (neither is read by plain `ssh host 'cmd'`). Both vars must be present or `oxy` fails.
- **DuckDB single-writer lock:** dlt → dbt → oxy run sequentially via `./run.sh`. Never run `oxy build` / a manual dbt concurrently with the pipeline. ARCHITECTURE.md.
- **`oxy.service` needs Docker:** `Requires=docker.service` + `After=docker.service` — oxy brings up a postgres container on boot against the persistent `oxy-postgres-data` volume. Post-reboot it comes back ~7s after dockerd.
- **git push HTTP 400 on binary blobs:** fresh clones need `git -C <repo> config http.postBuffer 524288000` once (CLAUDE.md "Known gotchas").
- **GitHub access still works from the new box** — the repo's SSH deploy key travels in the image and the GitHub org (`ironmonkey88/oxygen-mvp`) is unchanged; only the AWS + Claude accounts changed. Verify with `git -C ~/oxygen-mvp pull` early.
- **nginx docroot is `/var/www/somerville` only** (the legacy `default` site is disabled). `/home/ubuntu` is `chmod 755` so www-data can traverse to serve `/docs`.

---

## After migration: developing on the new instance

Once Phase 6 is green, normal development resumes unchanged — the box is byte-identical to the old one:

- **Session start on EC2:** `cd ~/oxygen-mvp && git pull origin main` first, every session (GitHub `main` is source of truth; the box is downstream).
- **Run order:** always `./run.sh` (never dlt/dbt/oxy individually). `./run.sh daily` is what the timer passes.
- **Task discipline:** every piece of work needs a TASKS.md entry marked `[~]` before EC2 commands (enforced by a PreToolUse hook).
- **Bash safety (Code harness):** no `&&`/`;`/`||` chaining, no `$(...)`, no heredocs — write ad-hoc SQL/Python to `scratch/`, scp, run via simple `ssh host -f /tmp/foo`. CLAUDE.md "Bash Safety."
- **Autonomous merge policy:** verified work on this repo → push + PR + merge autonomously; pause for destructive ops / cross-repo PRs / partial-or-blocked status. CLAUDE.md "Autonomous PR-merge policy."
- **Project state:** MVP 2 active. See `LOG.md` (Plans Registry + status) and `TASKS.md` "Next Focus." Do NOT conflate with the sibling repo `stack-in-a-box` (separate ledger, NYC 311 smoke, no EC2).

**Update the `oxygen-mvp` alias:** the new account's local machine needs `~/.ssh/config` pointing `oxygen-mvp` at the new box (Tailnet HostName or public IP) + the `oxygen-mvp-dest.pem` key path. Until Tailscale is re-authed (Phase 5), reach the box via `ssh -i <pem> ubuntu@<NEW_PUBLIC_IP>` over the temp SSH-22 rule.

---

*Handoff written 2026-07-09 15:23 ET. The last thing done in the prior session was Phase 3 Step B (copied AMI `ami-0ef4ca592a4bf8ce3` available in the destination account, us-east-2). The immediate next action is Phase 4 launch.*
