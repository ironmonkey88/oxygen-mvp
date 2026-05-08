# Limitations Registry

Known data and model limitations for the Somerville 311 platform. Each
limitation is one Markdown file with YAML frontmatter for structured fields
(consumed by the Answer Agent and the `/trust` page) followed by free-form
prose.

## File format

```
docs/limitations/<slug>.md
```

Filename slug must match the `id` frontmatter field.

## Frontmatter schema

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | slug (kebab-case) | yes | Unique. Matches filename minus `.md`. |
| `title` | string | yes | Human-readable name. |
| `severity` | enum | yes | One of `info`, `warning`, `critical`. |
| `affects` | list of strings | yes | View / measure / dimension names (e.g. `requests`, `requests.block_code`, `requests.total_requests`) or the literal `["all"]`. |
| `since` | YYYY-MM-DD | yes | Date the limitation became known. |
| `status` | enum | yes | `active` or `resolved`. Resolved entries stay in the registry as history. |

## Body

Free-form Markdown. Recommended structure:

- **What the limitation is** — concrete description
- **Impact** — what it breaks or biases for downstream consumers
- **Workaround** — query patterns or guardrails to apply
- **Resolution path** — if planned (e.g. "fixed in Silver, MVP 3"); otherwise state none

## Severity guide

- `info` — quirky but harmless if known; consumers should be aware
- `warning` — biases or distorts results in a specific direction; document workaround
- `critical` — answers from the agent are likely to be wrong without explicit handling

## Consumers

- **`/trust` page** (built next session) — renders `status: active` entries grouped by severity
- **Answer Agent** — references entries when a query touches an `affects` target

Until those are wired up, the registry stands as a flat reference for
contributors and reviewers.
