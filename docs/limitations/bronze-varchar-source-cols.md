---
id: bronze-varchar-source-cols
title: Bronze keeps source columns as VARCHAR — no type coercion
severity: info
affects:
  - bronze.raw_311_requests
  - main_bronze.raw_311_requests
since: 2026-05-07
status: active
---

# Bronze keeps source columns as VARCHAR

`main_bronze.raw_311_requests` is an exact mirror of the Somerville
311 source feed. Every column is `VARCHAR`, including dates, IDs, and
numeric fields. Type casting and value normalization are deferred to
Silver (MVP 3) and Gold.

## Impact

- Querying bronze directly requires explicit casts:
  `CAST(date_created AS DATE)`, `CAST(id AS BIGINT)`, etc.
- Date filters using string comparison work for ISO-8601 dates only;
  any non-ISO source values will silently sort as text.
- Aggregations on numeric-looking columns must cast first or risk
  string concatenation.

## Workaround

Don't query bronze for analyst questions — query
`main_gold.fct_311_requests` and the gold dims, which carry typed
columns. Bronze exists for lineage and reprocessing, not analysis.

## Resolution path

Silver layer (MVP 3) will land typed, deduplicated, PII-redacted
versions of the source columns. Gold already has typed columns
inherited via Silver-then-Gold (today, via direct
bronze-to-gold transforms with explicit casts).
