---
id: block-code-padded
title: block_code padded with spaces when unknown
severity: info
affects:
  - requests.block_code
since: 2026-05-08
status: active
---

# block_code padded with spaces when unknown

In the Somerville 311 source feed, the `block_code` column uses
space-padded strings (e.g. `"   "`) when the block is unknown, rather
than NULL. This means `block_code IS NULL` filters never match, and a
naive `COUNT(DISTINCT block_code)` includes the padded sentinel as a
distinct value.

## Impact

- "Unknown block" requests are not counted as missing data by standard
  null-checks
- Distinct-block counts overstate the true number of physical blocks
  by one
- Joins on `block_code` still work correctly because both sides carry
  the padded form

## Workaround

Filter for unknown block:

```sql
WHERE trim(block_code) = ''
```

Count distinct real blocks:

```sql
COUNT(DISTINCT NULLIF(trim(block_code), ''))
```

## Resolution path

To be cleaned in the Silver layer (MVP 3). `stg_311_requests` will
normalize blank/padded `block_code` to NULL, after which the Gold
fact and the `requests` view inherit the clean shape.
