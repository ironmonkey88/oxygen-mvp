#!/usr/bin/env bash
# Render every dbt Charts board under charts/ to static HTML and publish it
# to the portal at /boards/<name>/ (nginx's catch-all `location /` serves it).
#
# Run by systemd/dbt-charts-boards.service under a SHARED hold on
# data/.warehouse.lock (PR #92), so it never overlaps the pipeline's
# exclusive write. dct opens the DuckDB file read-only.
#
# dct lives in its own venv (~/.local/share/dbt-charts, linked at
# ~/.local/bin/dct), NOT in .venv: dbt-charts pins its own dbt-core.
#
# A board that fails to render leaves the previous page in place; the
# script exits non-zero so the failure shows in systemctl/journal.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
DCT="${DCT:-$HOME/.local/bin/dct}"
DOCROOT="${DOCROOT:-/var/www/somerville}"
export DO_NOT_TRACK=1

status=0
mkdir -p data/boards
for board in charts/*.yml; do
    name="$(basename "$board" .yml)"
    [ "$name" = "meta" ] && continue
    out="data/boards/${name}.html"
    if "$DCT" render "$board" --format html --output "$out"; then
        mkdir -p "$DOCROOT/boards/$name"
        cp "$out" "$DOCROOT/boards/$name/index.html.tmp"
        mv "$DOCROOT/boards/$name/index.html.tmp" "$DOCROOT/boards/$name/index.html"
        echo "deployed /boards/$name/"
    else
        echo "render failed: $board (previous page left in place)" >&2
        status=1
    fi
done
exit "$status"
