# EC2 Cross-Account Migration Checklist

**Goal:** Back up the live `oxygen-mvp` EC2 instance and stand it back up in a **different AWS account**, with the portal, Oxygen chat, pipeline timers, and Tailscale access all working.

**Method:** AMI (full-image) clone — create an image of the running box, copy/share it to the destination account, launch from it, then re-create the account-scoped wrappers (security group, Elastic IP, IAM, Tailscale identity) that an image can't carry.

**This instance, for reference (from `SETUP.md`):**

| Property | Value |
|---|---|
| OS / arch | Ubuntu 24.04 LTS, ARM64 |
| Instance type | `t4g.medium` (2 vCPU, 4 GB) |
| Storage | single 20 GB gp3 root volume (no separate data volume) |
| Region | confirm — public IP `18.224.151.49` indicates **us-east-2 (Ohio)** |
| Public exposure | security group: **port 80 only** inbound from `0.0.0.0/0` |
| Private access | SSH + `:3000` over Tailscale (`oxygen-mvp.taildee698.ts.net`) |
| Services | `oxy.service` + 3 systemd timers (refresh / health / profile); nginx; Docker postgres container `oxy-postgres-data` |
| Secrets baked in | `/etc/environment` (`ANTHROPIC_API_KEY`, `OXY_DATABASE_URL`), nginx `/etc/nginx/.htpasswd` |

Because the box is a **single root volume**, one AMI captures everything: OS, the `~/oxygen-mvp` repo, `data/somerville.duckdb`, the Docker postgres volume under `/var/lib/docker`, systemd units, nginx config, and the baked-in secrets. There is no second volume to snapshot separately.

> **Two viable routes — pick one before starting.** This checklist is the **AMI clone** (fastest, carries exact state including the DuckDB file). The lighter alternative — provision a fresh instance in the new account, `git clone` the repo, re-run `SETUP.md`, and restore only `data/somerville.duckdb` from a snapshot — is more steps but gives a clean box with no inherited cruft or stale Tailscale/Docker state. If the data is regenerable from `./run.sh` (full pull), the fresh-instance route may be strictly better. The rest of this doc assumes the AMI route.

---

## Phase 0 — Pre-flight (do before touching anything)

- [ ] **Create the TASKS.md entry** for this migration and mark it `[~]`.
- [ ] **Confirm the source region** (Console top-right, or `aws ec2 describe-instances`). Note the **Availability Zone** too.
- [ ] **Confirm the destination AWS account ID** (12 digits) and the destination region.
- [ ] **CRITICAL — check EBS encryption + KMS key.** Inspect the root volume: is it encrypted, and with which KMS key?
  - **Unencrypted** → AMI sharing works directly. Simplest.
  - **Encrypted with the AWS-managed `aws/ebs` key** → cross-account sharing **will fail**. You must copy the AMI/snapshot to a **customer-managed KMS key (CMK)** first, then grant the destination account `kms:Decrypt`/`ReEncrypt` on that CMK. This is the #1 silent blocker — resolve it now, not mid-migration.
- [ ] **Decide on the Anthropic API key.** It travels inside the image via `/etc/environment`. Either accept that, or plan to **rotate it** post-migration (recommended if accounts have different owners).
- [ ] **Note current Elastic IP (if any).** It will **not** move. Public IP changes. Harmless for Tailscale-reached SSH/`:3000`, but matters for anything pointing at the public portal IP `18.224.151.49`.
- [ ] **Record the launch config** you'll need to re-pick in the new account: instance type (`t4g.medium`), AZ, key pair, and the security-group rule (port 80 in from `0.0.0.0/0`).

---

## Phase 1 — Quiesce the source instance

A crash-consistent image of a live DuckDB file can be half-written. Stop the writers first.

- [ ] SSH in over Tailscale: `ssh oxygen-mvp`.
- [ ] **Stop the pipeline timers** so no refresh fires mid-image:
  ```bash
  sudo systemctl stop pipeline-refresh.timer source-health-check.timer profile-tables.timer
  ```
- [ ] **Confirm nothing is mid-run** (dlt/dbt/oxy share the DuckDB file lock): `sudo systemctl status pipeline-refresh.service` should be inactive; no `./run.sh` in `ps`.
- [ ] **Stop Oxygen** so its DuckDB connections close cleanly: `sudo systemctl stop oxy.service`.
- [ ] **Commit + push any uncommitted repo state on EC2** (`cd ~/oxygen-mvp && git status`) so GitHub `main` remains the source of truth. The image is a convenience copy, not the canonical repo.
- [ ] **Best practice: stop the instance** before imaging (`aws ec2 stop-instances`) for a fully crash-consistent root volume. If downtime is unacceptable, AWS can image a running instance (it snapshots without reboot if you ask), but the stopped-instance image is the safe default for a one-time move.

---

## Phase 2 — Create the AMI (source account)

- [ ] Console: **EC2 → Instances → select → Actions → Image and templates → Create image.** Or CLI:
  ```bash
  aws ec2 create-image \
    --instance-id <SOURCE_INSTANCE_ID> \
    --name "oxygen-mvp-migration-2026-06-17" \
    --description "Full image for cross-account move" \
    --region <SOURCE_REGION>
  ```
- [ ] Wait until the AMI state is **`available`** (`aws ec2 describe-images --image-ids <AMI_ID>`). This also creates the backing EBS snapshot(s).
- [ ] Note the **AMI ID** and the **snapshot ID(s)** it created.

---

## Phase 3 — Get the image into the destination account

**If unencrypted (or already on a customer-managed CMK shared with the dest account):**

- [ ] **Share the AMI** with the destination account:
  ```bash
  aws ec2 modify-image-attribute --image-id <AMI_ID> \
    --launch-permission "Add=[{UserId=<DEST_ACCOUNT_ID>}]" --region <SOURCE_REGION>
  ```
- [ ] **Share the backing snapshot(s)** (AMI sharing alone is not enough — the snapshots must be shared too):
  ```bash
  aws ec2 modify-snapshot-attribute --snapshot-id <SNAPSHOT_ID> \
    --attribute createVolumePermission \
    --operation-type add --user-ids <DEST_ACCOUNT_ID> --region <SOURCE_REGION>
  ```
- [ ] **In the destination account, copy the shared AMI so the new account owns it** (recommended — removes the dependency on the source account, which could otherwise delete the AMI out from under you):
  ```bash
  aws ec2 copy-image --source-image-id <AMI_ID> \
    --source-region <SOURCE_REGION> \
    --region <DEST_REGION> --name "oxygen-mvp"
  ```

**If encrypted with the default `aws/ebs` key:**

- [ ] In the **source** account, `copy-image` the AMI onto a **customer-managed CMK** (re-encrypt step).
- [ ] Grant the **destination** account usage on that CMK (KMS key policy: add the dest account principal with `kms:Decrypt`, `kms:CreateGrant`, `kms:ReEncrypt*`, `kms:DescribeKey`).
- [ ] Share the re-encrypted AMI + snapshots (as above), then `copy-image` in the destination account (it can re-encrypt to a dest-account CMK during the copy).

---

## Phase 4 — Launch in the destination account

- [ ] **Create the security group** in the destination VPC: inbound **port 80 from `0.0.0.0/0` only**. (Optionally a temporary SSH-22-from-my-IP rule for first contact before Tailscale is up — remove it after.)
- [ ] **Create / import a key pair** in the destination account.
- [ ] **Launch from the copied AMI**: instance type `t4g.medium`, the destination VPC/subnet/AZ, the new SG, the new key pair.
- [ ] **Re-attach an equivalent IAM instance role** if the source had one (IAM roles are account-bound and do not travel).
- [ ] **(Optional) Allocate + associate an Elastic IP** in the destination account if you want a stable public IP for the portal.

---

## Phase 5 — Re-establish identity & access (the parts the image can't carry)

- [ ] **Tailscale.** The image carries stale `tailscaled` state from the old node, which will collide. Clean it and re-auth as a fresh node:
  ```bash
  sudo systemctl stop tailscaled
  sudo rm -f /var/lib/tailscale/tailscaled.state
  sudo systemctl start tailscaled
  sudo tailscale up        # follow auth URL; keep --ssh OFF (see CLAUDE.md / SETUP.md §12)
  ```
  - [ ] Note the new Tailnet hostname; **update your local `~/.ssh/config`** `oxygen-mvp` alias / `HostName` to point at it.
  - [ ] If you want to keep the exact `oxygen-mvp.taildee698.ts.net` name, remove the old node from the Tailscale admin console first and rename the new one.
- [ ] **Verify `/etc/environment` survived** (it's baked into the image):
  ```bash
  ssh oxygen-mvp 'echo $ANTHROPIC_API_KEY | head -c 14'   # sk-ant-api03-E
  ssh oxygen-mvp 'echo $OXY_DATABASE_URL'                 # postgres URL
  ```
  - [ ] **Rotate `ANTHROPIC_API_KEY` now** if the destination account is a different trust boundary, then update `/etc/environment` and restart `oxy.service`.

---

## Phase 6 — Bring services back up & verify

- [ ] **Pull latest repo state** (image may be slightly behind GitHub): `cd ~/oxygen-mvp && git pull origin main`.
- [ ] **Start Oxygen + confirm the Docker postgres container recreated** against the persistent `oxy-postgres-data` volume:
  ```bash
  sudo systemctl start oxy.service
  sudo systemctl status oxy.service        # should be active ~7s after docker is up
  ```
- [ ] **Re-enable + start the timers:**
  ```bash
  sudo systemctl start pipeline-refresh.timer source-health-check.timer profile-tables.timer
  sudo systemctl list-timers --all | grep -E 'pipeline-refresh|source-health|profile'
  ```
- [ ] **nginx:** confirm the `somerville` site is enabled and serving; reload if needed (`sudo nginx -t && sudo systemctl reload nginx`). `.htpasswd` travels in the image, so Basic Auth on `/chat` should still work.
- [ ] **Verification gate — prove it actually works (don't infer from "instance is running"):**
  - [ ] `curl -sI http://<NEW_PUBLIC_IP>/` → `200` (portal).
  - [ ] `curl -sI http://<NEW_PUBLIC_IP>/metrics` and `/trust` → `200`.
  - [ ] `http://oxygen-mvp.<tailnet>:3000/` reachable over Tailscale.
  - [ ] `/chat` prompts for Basic Auth and lands in the workspace.
  - [ ] Run one Answer Agent question end-to-end and confirm the **trust contract** (SQL + row count + citation) renders — prefer `scripts/rendered_page.py` for the SPA path per STANDARDS §8.
  - [ ] **Run `./run.sh` once manually** and confirm a clean end-to-end pipeline (dlt → dbt → admin → pages) with a fresh `RUN_ID`.

---

## Phase 7 — Cutover & cleanup

- [ ] **Update DNS / any external pointers** from the old public IP (`18.224.151.49`) to the new one (only matters if something external references it directly).
- [ ] **Update `SETUP.md` / `CLAUDE.md`** with the new region, public IP, and (if changed) Tailnet hostname.
- [ ] **Keep the source instance stopped (not terminated) for a grace period** — your rollback if the new box misbehaves. Terminate only after the destination has run clean for a few daily refresh cycles.
- [ ] **Decommission the source** when confident: terminate the instance, delete the old AMI + snapshots in the source account, release the old Elastic IP, remove the old Tailscale node.
- [ ] **Cost note:** retained AMIs/snapshots bill in both accounts until deleted. Clean up the migration AMI in the source account once the move is confirmed.
- [ ] Mark the TASKS.md entry `[x]` with the verification evidence.

---

## What does NOT travel in the AMI (re-create these)

| Resource | Why | Action |
|---|---|---|
| Security group | SG IDs are account-bound | Recreate (port 80 public only) |
| Elastic IP | Account-bound; public IP changes | Allocate new if you need a stable IP |
| IAM role / instance profile | Account-bound | Re-attach equivalent in dest |
| KMS encryption key | Default `aws/ebs` key can't cross accounts | Re-encrypt to a CMK shared with dest |
| Tailscale node identity | Stale `tailscaled.state` collides | Wipe state + re-auth as new node |
| Anthropic API key | Travels, but may cross a trust boundary | Rotate if accounts differ |

---

*Drafted 2026-06-17. Verify each AWS CLI command's flags against your CLI version; placeholders in `<ANGLE_BRACKETS>` must be filled before running.*
