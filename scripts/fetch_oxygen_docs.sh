#!/usr/bin/env bash
# Mirror oxy.tech/docs into docs/oxygen-docs/ for offline grep + Chat project knowledge.
# URLs sourced from https://oxy.tech/docs/llms.txt (frozen below as of 2026-05-11).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$REPO_ROOT/docs/oxygen-docs"
mkdir -p "$DOCS_DIR"

# Read URL list from heredoc; one URL per line; blank lines and #-comments ignored.
URLS=$(cat <<'EOF'
# Welcome + Prerequisites + Quick Start
https://oxy.tech/docs/guide/welcome.md
https://oxy.tech/docs/guide/prerequisites.md
https://oxy.tech/docs/guide/quickstart.md

# Getting Started (Agents)
https://oxy.tech/docs/guide/getting-started-agents/set-up-project.md
https://oxy.tech/docs/guide/getting-started-agents/creating-your-first-agent.md
https://oxy.tech/docs/guide/getting-started-agents/providing-context.md
https://oxy.tech/docs/guide/getting-started-agents/test-your-agent.md

# Core Learning
https://oxy.tech/docs/guide/learn-about-oxy/agents.md
https://oxy.tech/docs/guide/learn-about-oxy/routing-agents.md
https://oxy.tech/docs/guide/learn-about-oxy/agentic-workflows.md
https://oxy.tech/docs/guide/learn-about-oxy/workflows.md
https://oxy.tech/docs/guide/learn-about-oxy/data-apps.md
https://oxy.tech/docs/guide/learn-about-oxy/config.md
https://oxy.tech/docs/guide/learn-about-oxy/context.md
https://oxy.tech/docs/guide/learn-about-oxy/context-graph.md
https://oxy.tech/docs/guide/learn-about-oxy/cache.md
https://oxy.tech/docs/guide/learn-about-oxy/debugging.md
https://oxy.tech/docs/guide/learn-about-oxy/modeling.md
https://oxy.tech/docs/guide/learn-about-oxy/observability.md
https://oxy.tech/docs/guide/learn-about-oxy/testing.md
https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer.md
https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer/dimensions.md
https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer/entities.md
https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer/measures.md
https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer/topics.md
https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer/views.md
https://oxy.tech/docs/guide/learn-about-oxy/semantic-layer/usage.md
https://oxy.tech/docs/guide/learn-about-oxy/semantic-model.md

# API & Authentication
https://oxy.tech/docs/guide/api-keys/API-Keys.md
https://oxy.tech/docs/guide/authentication/overview.md
https://oxy.tech/docs/guide/authentication/google.md
https://oxy.tech/docs/guide/authentication/magic-link.md
https://oxy.tech/docs/guide/authentication/okta.md

# Deployment
https://oxy.tech/docs/guide/deployment/overview.md
https://oxy.tech/docs/guide/deployment/install-oxy.md
https://oxy.tech/docs/guide/deployment/environment.md
https://oxy.tech/docs/guide/deployment/workspace-setup.md
https://oxy.tech/docs/guide/deployment/docker.md
https://oxy.tech/docs/guide/deployment/container-runtimes.md
https://oxy.tech/docs/guide/deployment/create-machine.md
https://oxy.tech/docs/guide/deployment/github-app.md
https://oxy.tech/docs/guide/deployment/cloud-mode.md
https://oxy.tech/docs/guide/deployment/kubernetes-helm.md
https://oxy.tech/docs/guide/deployment/kubernetes-raw.md
https://oxy.tech/docs/guide/deployment/hands-on/aws.md
https://oxy.tech/docs/guide/deployment/reference-architecture/aws/architecture.md
https://oxy.tech/docs/guide/deployment/reference-architecture/aws/ec2-architecture.md
https://oxy.tech/docs/guide/deployment/reference-architecture/aws/ecs-architecture.md
https://oxy.tech/docs/guide/deployment/reference-architecture/aws/step-by-step/ec2.md
https://oxy.tech/docs/guide/deployment/reference-architecture/aws/step-by-step/ecs.md

# Integrations
https://oxy.tech/docs/guide/integrations/overview.md
https://oxy.tech/docs/guide/integrations/a2a/overview.md
https://oxy.tech/docs/guide/integrations/v0/overview.md
https://oxy.tech/docs/guide/integrations/analytics/looker.md
https://oxy.tech/docs/guide/integrations/apps/slack.md
https://oxy.tech/docs/guide/integrations/data-sources/bigquery.md
https://oxy.tech/docs/guide/integrations/data-sources/clickhouse.md
https://oxy.tech/docs/guide/integrations/data-sources/domo.md
https://oxy.tech/docs/guide/integrations/data-sources/duckdb.md
https://oxy.tech/docs/guide/integrations/data-sources/motherduck.md
https://oxy.tech/docs/guide/integrations/data-sources/mysql.md
https://oxy.tech/docs/guide/integrations/data-sources/postgres.md
https://oxy.tech/docs/guide/integrations/data-sources/redshift.md
https://oxy.tech/docs/guide/integrations/data-sources/snowflake.md
https://oxy.tech/docs/guide/integrations/models/anthropic.md
https://oxy.tech/docs/guide/integrations/models/gemini.md
https://oxy.tech/docs/guide/integrations/models/ollama.md
https://oxy.tech/docs/guide/integrations/models/openai.md

# MCP & Migration
https://oxy.tech/docs/guide/mcp-server/mcp-usage.md
https://oxy.tech/docs/guide/migration/migration-guide.md

# Reference
https://oxy.tech/docs/guide/reference/oxy-commands.md
https://oxy.tech/docs/guide/reference/oxy-start.md
https://oxy.tech/docs/guide/reference/branch-configuration.md
https://oxy.tech/docs/guide/reference/database-sync.md
https://oxy.tech/docs/guide/reference/environment-variables.md
https://oxy.tech/docs/guide/reference/readonly-mode.md
https://oxy.tech/docs/guide/reference/semantic-layer-reference.md

# Changelog (chronological, oldest first)
https://oxy.tech/docs/changelog/2025-04-03.md
https://oxy.tech/docs/changelog/2025-04-10.md
https://oxy.tech/docs/changelog/2025-04-24.md
https://oxy.tech/docs/changelog/2025-05-07.md
https://oxy.tech/docs/changelog/2025-06-26.md
https://oxy.tech/docs/changelog/2025-07-03.md
https://oxy.tech/docs/changelog/2025-07-10.md
https://oxy.tech/docs/changelog/2025-07-17.md
https://oxy.tech/docs/changelog/2025-07-24.md
https://oxy.tech/docs/changelog/2025-07-30.md
https://oxy.tech/docs/changelog/2025-08-08.md
https://oxy.tech/docs/changelog/2025-08-21.md
https://oxy.tech/docs/changelog/2025-09-04.md
https://oxy.tech/docs/changelog/2025-09-12.md
https://oxy.tech/docs/changelog/2025-09-26.md
https://oxy.tech/docs/changelog/2025-10-24.md
https://oxy.tech/docs/changelog/2025-11-06.md
https://oxy.tech/docs/changelog/2025-11-14.md
https://oxy.tech/docs/changelog/2025-11-20.md
https://oxy.tech/docs/changelog/2025-11-27.md
https://oxy.tech/docs/changelog/2025-12-04.md
https://oxy.tech/docs/changelog/2025-12-11.md
https://oxy.tech/docs/changelog/2025-12-18.md
https://oxy.tech/docs/changelog/2025-12-25.md
https://oxy.tech/docs/changelog/2026-01-01.md
https://oxy.tech/docs/changelog/2026-01-08.md
https://oxy.tech/docs/changelog/2026-01-15.md
https://oxy.tech/docs/changelog/2026-01-22.md
https://oxy.tech/docs/changelog/2026-01-29.md
https://oxy.tech/docs/changelog/2026-02-05.md
https://oxy.tech/docs/changelog/2026-02-12.md
https://oxy.tech/docs/changelog/2026-02-26.md
https://oxy.tech/docs/changelog/2026-03-05.md
https://oxy.tech/docs/changelog/2026-03-12.md
https://oxy.tech/docs/changelog/2026-03-19.md
https://oxy.tech/docs/changelog/2026-03-26.md
https://oxy.tech/docs/changelog/2026-04-02.md
https://oxy.tech/docs/changelog/2026-04-09.md
https://oxy.tech/docs/changelog/2026-04-16.md
https://oxy.tech/docs/changelog/2026-04-23.md
https://oxy.tech/docs/changelog/2026-04-30.md
https://oxy.tech/docs/changelog/2026-05-07.md
EOF
)

count=0
failures=0
while IFS= read -r url; do
    [[ -z "$url" || "$url" =~ ^# ]] && continue
    # Strip the https://oxy.tech/docs/ prefix to derive local path
    relpath="${url#https://oxy.tech/docs/}"
    target="$DOCS_DIR/$relpath"
    mkdir -p "$(dirname "$target")"
    if curl -sLf "$url" -o "$target"; then
        count=$((count+1))
    else
        echo "FAIL: $url" >&2
        failures=$((failures+1))
    fi
done <<< "$URLS"

echo "Fetched $count pages, $failures failures."
echo "Tree:"
find "$DOCS_DIR" -type f -name '*.md' | sort | head -100
