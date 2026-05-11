# SETUP.md — Environment Setup

Step-by-step setup for the Oxygen MVP on an AWS EC2 instance (Ubuntu 22.04 LTS).

---

## 1. Provision EC2 Instance

In AWS Console → EC2 → Launch Instance:

| Setting | Value |
|---|---|
| AMI | Ubuntu 24.04 LTS (64-bit ARM) |
| Instance type | `t4g.medium` (ARM, 2 vCPU, 4 GB) — or `t3.medium` for x86 |
| Storage | 20 GB gp3 |
| Security group | HTTP (80) inbound from `0.0.0.0/0` only. **Do not open SSH (22) or 3000 publicly** — they ride over Tailscale (see §12). For the very first connection (before Tailscale is up), open SSH (22) to your IP only, and remove the rule once Tailscale is verified working. |

Note the Public IPv4 address.

---

## 2. Connect and Install Docker

```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
```

---

## 3. Install Oxygen

```bash
bash <(curl --proto '=https' --tlsv1.2 -LsSf https://get.oxy.tech)

# Verify
oxy --version
```

---

## 4. Set Up Python Environment

**Use Python 3.12.** This is the binding constraint across dlt and dbt-duckdb.

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv -y

# Create virtual environment in project root
python3.12 -m venv .venv
source .venv/bin/activate

# Verify
python --version   # Should show 3.12.x
```

---

## 5. Install Python Packages

```bash
pip install "dlt[duckdb]" dbt-core dbt-duckdb
```

**Package versions (as of project start):**
- dlt: supports Python 3.9–3.13; install with `[duckdb]` extra for DuckDB destination
- dbt-core: requires ≥ 1.8.x
- dbt-duckdb: requires Python ≥ 3.10, DuckDB ≥ 1.1.x

**Do not pin DuckDB separately.** Let dbt-duckdb manage it to avoid version conflicts.

---

## 6. Clone Project

```bash
git clone https://github.com/your-org/oxygen-mvp.git
cd oxygen-mvp

# Create data directory for DuckDB file
mkdir -p data
```

---

## 7. Set Environment Variables

Two env vars are required at runtime:

| Var | Value | Used by |
|---|---|---|
| `ANTHROPIC_API_KEY` | your Anthropic API key | Oxygen Answer Agent |
| `OXY_DATABASE_URL` | `postgresql://postgres:postgres@localhost:15432/oxy` | `oxy build`, `oxy serve` (the Postgres container `oxy start` brings up) |

**Put them in `/etc/environment`, not `~/.bashrc` or `~/.profile`.** sshd reads `/etc/environment` via PAM at session setup, so plain `ssh ec2 'cmd'` sees the vars without needing a login-shell wrapper. `~/.bashrc` doesn't work (early-returns for non-interactive shells); `~/.profile` doesn't work (login-shell only). Format is literal `KEY=VALUE` — no `export`, no shell expansion.

```bash
sudo tee -a /etc/environment <<'EOF'
ANTHROPIC_API_KEY=your_key_here
OXY_DATABASE_URL=postgresql://postgres:postgres@localhost:15432/oxy
EOF

# Also extend PATH so oxy/airlayer in ~/.local/bin are visible to non-interactive ssh.
# Edit the existing PATH= line in /etc/environment to include /home/ubuntu/.local/bin.
sudo sed -i 's|/snap/bin"|/snap/bin:/home/ubuntu/.local/bin"|' /etc/environment
```

Verify in a fresh ssh session (NOT the one you used to set them — env loads at session start):

```bash
ssh ec2 'echo $ANTHROPIC_API_KEY | head -c 14'   # should print sk-ant-api03-E
ssh ec2 'echo $OXY_DATABASE_URL'                   # should print the postgres URL
ssh ec2 'oxy --version'                            # should resolve oxy on PATH
```

---

## 8. Configure dbt Profile

The repo ships [`dbt/profiles.example.yml`](dbt/profiles.example.yml) as a template. Copy it into place and edit the `path:` for your environment:

```bash
mkdir -p ~/.dbt
cp dbt/profiles.example.yml ~/.dbt/profiles.yml
# edit ~/.dbt/profiles.yml — set `path:` to the absolute DuckDB file location
```

The live `~/.dbt/profiles.yml` is intentionally user-local and is **not** checked into the repo (machine-specific paths). The example file is the canonical template; if its shape changes, update the example, then re-copy on the affected boxes.

The profile name must match the `profile:` field in `dbt/dbt_project.yml`.

Verify dbt can connect:
```bash
cd dbt
dbt debug
```

---

## 9. Configure Oxygen

Create `config.yml` in the project root:

```yaml
models:
  - name: claude
    vendor: anthropic
    model: claude-sonnet-4-6

databases:
  - name: somerville
    type: duckdb
    path: data/somerville.duckdb
```

---

## 10. Start Oxygen

```bash
oxy start
# Launches PostgreSQL in Docker + Oxygen server
# Available at http://YOUR_PUBLIC_IP:3000
```

---

## 11. Run as a Persistent Service (Recommended)

So Oxygen survives SSH disconnects and reboots:

```bash
sudo tee /etc/systemd/system/oxy.service <<EOF
[Unit]
Description=Oxygen server
After=network.target docker.service
Requires=docker.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/oxygen-mvp
ExecStart=/home/ubuntu/.local/bin/oxy start --local
Restart=always
RestartSec=10
# Inherit env vars from /etc/environment — keeps the systemd unit and
# non-interactive ssh sessions on the same source of truth. systemd does
# not read /etc/environment by default; EnvironmentFile= does the work.
EnvironmentFile=/etc/environment

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable oxy
sudo systemctl start oxy

# Check status
sudo systemctl status oxy
```

**Why `After=docker.service` + `Requires=docker.service`:** `oxy start` brings up a Docker postgres container as part of its boot. If systemd starts oxy before dockerd is ready (post-reboot), oxy crashes attempting to create the container. The `Requires=` ensures dockerd is up; `After=` orders oxy after it. Verified Session 24 reboot test — oxy comes back ~7 seconds after kernel up, including container recreation against the persistent `oxy-postgres-data` volume.

**Why `--local`:** the `oxy start --local` flag runs in single-workspace mode rooted at the current working directory (the `WorkingDirectory=` line above), with guest authentication and no organization creation. This bypasses Oxygen's multi-workspace onboarding wizard, which currently has no path for connecting to an existing populated DuckDB — the wizard's DuckDB step accepts only CSV/Parquet uploads into a fresh `.db/` directory. For a project arriving with a pre-built medallion DuckDB (this one), `--local` is the supported deployment shape. Multi-workspace mode (`oxy start` without `--local`) is the long-term target for MVP 4's sharing surfaces and public chat via Magic Link auth, but requires either an Oxygen wizard with an "existing DuckDB" option or a programmatic workspace-creation tool. See Session 25 narrative for the customer-feedback writeup.

**Security note on `--local`:** the `--local` flag disables authentication entirely (guest mode). Do not expose `:3000` on a non-loopback interface without a reverse proxy that restricts access. In this deployment, Tailscale serves as the de facto reverse proxy — `:3000` is closed at the AWS security group and reachable only over the Tailnet. MVP 1.5 (planned, see [docs/plans/](../docs/plans/)) adds nginx Basic Auth in front of the SPA for controlled public exposure as an interim solution.

---

## 12. Tailscale Access (private SSH and `:3000`)

After Plan 1 (Tailscale lockdown), public SSH and port 3000 are closed at the AWS security group; all access rides over Tailscale. To connect from a new device:

```bash
# 1. Install Tailscale (mac: brew install --cask tailscale-app | linux: curl -fsSL https://tailscale.com/install.sh | sh)
# 2. Sign in to the same Tailnet (taildee698.ts.net) as the EC2 node
tailscale up                       # follow the auth URL

# 3. SSH via the alias (set up ~/.ssh/config to point oxygen-mvp at the Tailnet hostname)
ssh oxygen-mvp                     # routes via 100.73.216.43 (MagicDNS: oxygen-mvp.taildee698.ts.net)
```

Required `~/.ssh/config` entry:

```
Host oxygen-mvp
    HostName oxygen-mvp.taildee698.ts.net
    User ubuntu
    IdentityFile ~/.ssh/oxygen-mvp-server.pem
    StrictHostKeyChecking no
```

**Tailscale SSH (`--ssh` flag) is intentionally OFF** on the EC2 node. It bypasses OpenSSH's PAM stack, which silently breaks `/etc/environment` env-var loading (PATH/`ANTHROPIC_API_KEY`/`OXY_DATABASE_URL` all missing in non-interactive SSH). Re-enable only when there's a real driver (multi-device, teammate) and rebuild the env-var path properly at the same time.

`:3000` (Oxygen chat) is reachable from any Tailnet peer at `http://oxygen-mvp.taildee698.ts.net:3000/`. Public portal at port 80 is intentionally public (`http://18.224.151.49/`).

---

## 13. Portal and nginx

Portal lives at `portal/index.html` in the repo and is deployed to nginx's docroot at `/var/www/somerville/`. The dbt docs at `/docs`, the metrics catalog at `/metrics`, and the project portal at `/` all serve from this nginx.

**Quirks worth knowing:**

- Active site is `sites-enabled/somerville → sites-available/somerville`. The legacy `default` site is **not enabled** — its `root /var/www/html` directive is unused. Don't deploy there. nginx docroot is `/var/www/somerville` (only).
- `/home/ubuntu` is `chmod 755` (was 750 by default). nginx's www-data must traverse it to serve `dbt/target/index.html` from the in-repo location for the `/docs` route. Subdirs like `~/.ssh` keep their own 700.
- Canonical nginx site config lives in repo at [`nginx/somerville.conf`](nginx/somerville.conf). Edit there, then deploy:

  ```bash
  scp nginx/somerville.conf oxygen-mvp:/tmp/somerville.conf
  ssh oxygen-mvp 'sudo cp /tmp/somerville.conf /etc/nginx/sites-available/somerville \
              && sudo nginx -t \
              && sudo systemctl reload nginx'
  ```

- Portal HTML deploy follows the same pattern — `portal/index.html` and `portal/metrics.html` are the in-repo sources; deploy by copying to `/var/www/somerville/`. `run.sh` step 7 deploys `metrics.html` automatically; `index.html` is deployed by hand when changed.

---

## Run Order (Important)

**Before any work on EC2, pull first:** `cd ~/oxygen-mvp && git pull origin main`. GitHub `main` is the source of truth — EC2 is downstream. See CLAUDE.md "Session Start on EC2" for details.

The pipeline has a single entry point: **`./run.sh`** at the repo root. Never invoke `dlt`, `dbt`, or `oxy` directly from the shell — `run.sh` activates the project venv, enforces the right order, captures the dbt-test exit code without halting, and ends with admin-table population and `/docs`/`/metrics` regeneration.

```
./run.sh
```

The seven steps:

1. `python dlt/somerville_311_pipeline.py`
2. `dbt run --select bronze gold`
3. `dbt test --select bronze gold` *(exit captured, do not halt)*
4. `python dlt/load_dbt_results.py` *(append run_results.json to `main_bronze.raw_dbt_results_raw`)*
5. `dbt run --select admin`
6. `dbt docs generate` *(regenerates `/docs`)*
7. `python scripts/generate_metrics_page.py` + deploy *(regenerates `/metrics`)*

Final exit code = the captured `dbt test` exit so a failing test surfaces but admin tables still get populated.

DuckDB only allows one writer at a time, so don't run `oxy build` or `oxy start` operations that touch the DuckDB file in parallel with `./run.sh`. See `ARCHITECTURE.md` for the file locking constraint.

---

## Verify Everything Works

```bash
ssh oxygen-mvp 'cd ~/oxygen-mvp && ./run.sh'    # full pipeline, end-to-end
curl http://18.224.151.49/                       # portal (public)
curl http://18.224.151.49/docs/index.html        # dbt docs
curl http://18.224.151.49/metrics                # metrics catalog
ssh oxygen-mvp 'curl -sI http://localhost:3000'  # Oxygen chat (Tailnet only — won't work from public internet)
```

---

## Reference Links

- Oxygen Install: https://oxy.tech/docs/guide/deployment/install-oxy.md
- Oxygen AWS Guide: https://oxy.tech/docs/guide/deployment/hands-on/aws.md
- dbt-duckdb PyPI: https://pypi.org/project/dbt-duckdb/
- dlt PyPI: https://pypi.org/project/dlt/
