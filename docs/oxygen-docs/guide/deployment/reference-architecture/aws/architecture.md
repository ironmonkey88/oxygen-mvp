> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Kubernetes Deployment

> Deploy Oxy on Kubernetes using the official Helm chart

The recommended way to run Oxy in production on Kubernetes is via the official Helm chart, available at [github.com/oxy-hq/charts](https://github.com/oxy-hq/charts).

## Prerequisites

* A Kubernetes cluster (EKS, GKE, AKS, or any CNCF-conformant cluster)
* `kubectl` configured against your cluster
* `helm` v3+
* A PostgreSQL database (RDS, Cloud SQL, Supabase, or self-hosted)

## Install

```bash theme={null}
helm repo add oxy https://oxy-hq.github.io/charts
helm repo update
```

Create a `values.yaml` with your configuration:

```yaml theme={null}
env:
  OXY_DATABASE_URL: "postgresql://user:password@your-db-host:5432/oxy"
  OPENAI_API_KEY: "sk-..."

# Optional: expose via LoadBalancer or configure an Ingress below
service:
  type: ClusterIP
```

Install the chart:

```bash theme={null}
helm install oxy oxy/oxy -f values.yaml
```

## Access Oxy

Port-forward to access the UI locally while you set up ingress:

```bash theme={null}
kubectl port-forward svc/oxy 3000:3000
```

Open `http://localhost:3000`.

## Ingress

Add an ingress block to your `values.yaml` to expose Oxy publicly:

```yaml theme={null}
ingress:
  enabled: true
  className: nginx          # or alb, traefik, etc.
  hosts:
    - host: oxy.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: oxy-tls
      hosts:
        - oxy.example.com
```

Then upgrade:

```bash theme={null}
helm upgrade oxy oxy/oxy -f values.yaml
```

## Configuration

All Oxy environment variables can be set under `env:` in `values.yaml`. See the [Environment reference](/deployment/environment) for the full list.

For secrets, use a Kubernetes Secret and reference it:

```yaml theme={null}
envFrom:
  - secretRef:
      name: oxy-secrets
```

Create the secret:

```bash theme={null}
kubectl create secret generic oxy-secrets \
  --from-literal=OXY_DATABASE_URL="postgresql://..." \
  --from-literal=OPENAI_API_KEY="sk-..."
```

## Upgrade

```bash theme={null}
helm repo update
helm upgrade oxy oxy/oxy -f values.yaml
```

## Uninstall

```bash theme={null}
helm uninstall oxy
```

## Next steps

* [Configure authentication](/deployment/environment#authentication)
* [Set up the GitHub App](/deployment/github-app) for multi-workspace mode
* Browse all chart options at [github.com/oxy-hq/charts](https://github.com/oxy-hq/charts)
