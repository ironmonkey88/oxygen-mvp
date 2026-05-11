> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Deploy on AWS

> Run Oxy on an Amazon EC2 instance

This guide deploys Oxy on a single EC2 instance using `oxy start`, which manages PostgreSQL and the Oxy process for you.

## 1. Launch an EC2 instance

In the [AWS Console](https://console.aws.amazon.com/) → **EC2** → **Launch instance**:

| Setting            | Value                                                     |
| ------------------ | --------------------------------------------------------- |
| **AMI**            | Ubuntu 22.04 LTS (64-bit ARM or x86)                      |
| **Instance type**  | `t4g.medium` (ARM, 2 vCPU, 4 GB) — or `t3.medium` for x86 |
| **Storage**        | 20 GB gp3                                                 |
| **Security group** | Allow SSH (22), HTTP (80), and port 3000 inbound          |

Note the **Public IPv4 address** once the instance is running.

## 2. Connect and install

SSH into your instance, then install Docker and Oxy:

```bash theme={null}
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Oxy
curl --proto '=https' --tlsv1.2 -sSf https://get.oxy.tech | sh
```

## 3. Set up your project

```bash theme={null}
# Clone existing project
git clone https://github.com/your-org/your-oxy-project.git
cd your-oxy-project

# Or initialize a new one
mkdir my-oxy && cd my-oxy
oxy init
```

## 4. Start Oxy

```bash theme={null}
oxy start
```

`oxy start` launches PostgreSQL in Docker and starts the Oxy server. Your instance is now running at `http://YOUR_PUBLIC_IP:3000`.

<Tip>
  To keep Oxy running after you close your SSH session, use a terminal multiplexer:

  ```bash theme={null}
  screen -S oxy
  oxy start
  # Detach with Ctrl+A, D
  ```
</Tip>

## 5. (Optional) Use an external database for production

When you're ready to use a managed database instead of the Docker-managed PostgreSQL:

```bash theme={null}
export OXY_DATABASE_URL="postgresql://user:password@your-rds-host:5432/oxy"
oxy serve
```

Use [Amazon RDS for PostgreSQL](https://aws.amazon.com/rds/postgresql/) for a fully managed option with automated backups and Multi-AZ support.

***

## Recommended instance types

| Team size  | ARM (best value)    | x86                |
| ---------- | ------------------- | ------------------ |
| 1–3 users  | `t4g.small` (2 GB)  | `t3.small` (2 GB)  |
| 3–10 users | `t4g.medium` (4 GB) | `t3.medium` (4 GB) |
| 10+ users  | `t4g.large` (8 GB)  | `t3.large` (8 GB)  |

## Next steps

* Set up a domain with HTTPS using [Caddy](https://caddyserver.com/) or nginx
* Enable [authentication](/deployment/environment#authentication)
* Switch to [multi-workspace cloud mode](/deployment/cloud-mode) for team access and GitHub integration
