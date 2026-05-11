> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# DuckDB

A `duckdb` database entry can be added by specifying `type: duckdb` in your
[`~/.config/oxy/config.yml` file](/learn-about-oxy/config). The `dataset`
field should point to the directory where your data is stored. We run `SET
file_search_path = '{}'` within duckdb against the path you provide before any
query.

# Sample config entry

```yaml theme={null}
databases:
  - name: local
    type: duckdb
    dataset: /Users/robertyi/repos/oxykelihi/.db/
```
