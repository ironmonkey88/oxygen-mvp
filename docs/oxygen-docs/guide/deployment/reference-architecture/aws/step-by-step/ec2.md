> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Kubernetes Quick Start

> Get Oxy running on any Kubernetes cluster in minutes

This guide gets Oxy running on any Kubernetes cluster. For cloud-specific instructions (EKS, GKE), see the sidebar.

## 1. Add the Helm repository

```bash theme={null}
helm repo add oxy https://oxy-hq.github.io/charts
helm repo update
```

## 2. Create a secret for your credentials

```bash theme={null}
kubectl create secret generic oxy-secrets \
  --from-literal=OXY_DATABASE_URL="postgresql://user:password@your-db-host:5432/oxy" \
  --from-literal=OPENAI_API_KEY="sk-..."
```

## 3. Install

```bash theme={null}
helm install oxy oxy/oxy \
  --set envFrom[0].secretRef.name=oxy-secrets
```

## 4. Access the UI

```bash theme={null}
kubectl port-forward svc/oxy 3000:3000
```

Open `http://localhost:3000`. Set up an ingress when you're ready to expose it publicly — see the [Kubernetes Helm guide](/deployment/kubernetes-helm) for ingress examples.

## 5. Upgrade

```bash theme={null}
helm repo update
helm upgrade oxy oxy/oxy -f values.yaml
```

## Full chart reference

All available options are documented at [github.com/oxy-hq/charts](https://github.com/oxy-hq/charts).
