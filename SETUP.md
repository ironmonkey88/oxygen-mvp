# SETUP.md — Environment Setup

Step-by-step setup for the Oxygen MVP on an AWS EC2 instance (Ubuntu 22.04 LTS).

---

## 1. Provision EC2 Instance

In AWS Console → EC2 → Launch Instance:

| Setting | Value |
|---|---|
| AMI | Ubuntu 22.04 LTS (64-bit ARM or x86) |
| Instance type | `t4g.medium` (ARM, 2 vCPU, 4 GB) — or `t3.medium` for x86 |
| Storage | 20 GB gp3 |
| Security group | SSH (22), HTTP (80), port 3000 inbound |

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

```bash
export ANTHROPIC_API_KEY=your_key_here
```

To persist across sessions, add to `~/.bashrc`:
```bash
echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.bashrc
source ~/.bashrc
```

---

## 8. Configure dbt Profile

Create `~/.dbt/profiles.yml` (user-local — never check this into the repo):

```yaml
somerville_311:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /home/ubuntu/oxygen-mvp/data/somerville.duckdb
      threads: 4
```

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
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/oxygen-mvp
ExecStart=/usr/local/bin/oxy start
Restart=always
Environment="ANTHROPIC_API_KEY=your_key_here"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable oxy
sudo systemctl start oxy

# Check status
sudo systemctl status oxy
```

---

## Run Order (Important)

DuckDB only allows one writer at a time. Always run in this order:

```bash
# 1. Ingest
cd dlt && python somerville_311_pipeline.py

# 2. Transform
cd dbt && dbt run

# 3. Serve
oxy start
```

Never run dlt or dbt while Oxygen is actively writing to the DuckDB file.
See `ARCHITECTURE.md` for details on the file locking constraint.

---

## Verify Everything Works

```bash
# dlt
python dlt/somerville_311_pipeline.py

# dbt
cd dbt && dbt debug && dbt run && dbt test

# Oxygen
oxy --version
curl http://localhost:3000   # Should return Oxygen UI
```

---

## Reference Links

- Oxygen Install: https://oxy.tech/docs/guide/deployment/install-oxy.md
- Oxygen AWS Guide: https://oxy.tech/docs/guide/deployment/hands-on/aws.md
- dbt-duckdb PyPI: https://pypi.org/project/dbt-duckdb/
- dlt PyPI: https://pypi.org/project/dlt/
