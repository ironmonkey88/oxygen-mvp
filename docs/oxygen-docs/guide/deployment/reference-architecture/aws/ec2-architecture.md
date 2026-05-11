> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# EKS Deployment

> Deploy Oxy on Amazon Elastic Kubernetes Service

Deploy Oxy on EKS using the official Helm chart. This pairs well with RDS for PostgreSQL as the managed database.

## Prerequisites

* An EKS cluster ([eksctl quickstart](https://eksctl.io/getting-started/))
* `kubectl` configured for the cluster
* `helm` v3+
* An RDS PostgreSQL instance

## Create an RDS database

In the AWS Console → **RDS** → **Create database**:

* Engine: PostgreSQL
* Template: Production (or Dev/Test for smaller deployments)
* Instance class: `db.t4g.medium` is a good starting point
* Place in the **same VPC** as your EKS cluster

Note the endpoint, username, and password.

## Install Oxy

```bash theme={null}
helm repo add oxy https://oxy-hq.github.io/charts
helm repo update
```

Store your credentials as a Kubernetes Secret:

```bash theme={null}
kubectl create secret generic oxy-secrets \
  --from-literal=OXY_DATABASE_URL="postgresql://user:password@your-rds-endpoint:5432/oxy" \
  --from-literal=OPENAI_API_KEY="sk-..."
```

Create `values.yaml`:

```yaml theme={null}
envFrom:
  - secretRef:
      name: oxy-secrets

ingress:
  enabled: true
  className: alb
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
  hosts:
    - host: oxy.example.com
      paths:
        - path: /
          pathType: Prefix
```

Install:

```bash theme={null}
helm install oxy oxy/oxy -f values.yaml
```

## Upgrade

```bash theme={null}
helm repo update
helm upgrade oxy oxy/oxy -f values.yaml
```

## Next steps

* [Configure authentication](/deployment/environment#authentication)
* [Set up the GitHub App](/deployment/github-app) for multi-workspace mode
* Browse all chart options at [github.com/oxy-hq/charts](https://github.com/oxy-hq/charts)
