---
id: block-code-padded
title: block_code uses "NA" space-padded to 15 chars when unknown
severity: warning
affects:
  - requests.block_code
since: 2026-05-08
status: active
---

# block_code uses "NA" space-padded to 15 chars when unknown

In the Somerville 311 source feed, the `block_code` column is a fixed-width
VARCHAR(15). Real block codes are 15-digit census block identifiers like
`250173513001000`. When the block is unknown, the column holds the literal
two-character string `'NA'` padded with 13 trailing spaces to fill the
column width: `'NA             '`. The column is **never NULL** and never
whitespace-only.

As of 2026-05-09, **447,428 of 1,169,935 rows (~38%)** carry the unknown
sentinel.

## Impact

- `block_code IS NULL` never matches — there are no NULLs.
- `trim(block_code) = ''` never matches — the sentinel is `'NA'`, not blank.
- `block_code = 'NA'` (without trim) never matches — the value carries trailing
  whitespace.
- Naive distinct-block counts overstate the true number of physical blocks
  by one (the sentinel is counted as a distinct value).
- ~38% of rows have no resolvable location at the block level. Any
  block-level rollup that doesn't exclude the sentinel is reporting
  "Unknown" as the largest block.

## Workaround

Filter the sentinel out:

```sql
WHERE trim(block_code) <> 'NA'
```

Count distinct real blocks (excluding the sentinel):

```sql
COUNT(DISTINCT CASE WHEN trim(block_code) <> 'NA' THEN block_code END)
```

Find unknown-block rows:

```sql
WHERE trim(block_code) = 'NA'
```

## Resolution path

To be normalized in the Silver layer (MVP 3). `stg_311_requests` will
map the `'NA'` sentinel to NULL, and `block_code` will be trimmed.
After that, the Gold fact and the `requests` view inherit the clean
shape, and standard `IS NULL` filters work as analysts expect.

## History

- 2026-05-08 — Entry created with description: "space-padded strings (e.g. `\"   \"`)". The actual sentinel form was different.
- 2026-05-10 — Corrected after Plan 6 D3 Q4 surfaced `'NA'` as the top block with 447k rows. Verified via `scratch/check_block_sentinels.py`: zero NULLs, zero whitespace-only, 447,428 `'NA'`-padded, 722,507 real.
