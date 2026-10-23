#!/usr/bin/env bash
# Bring ~/oxygen-mvp to origin/main before the daily pipeline (Plan 53).
# pipeline-refresh.service runs this as ExecStartPre=, under the exclusive
# warehouse lock. Fast-forward only: if main cannot be fast-forwarded (a local
# edit, diverged history, an untracked file in the way) the tree is left alone,
# data/deploy_status.txt says why, the pipeline runs on the code already here,
# and scripts/hc_ping.sh turns the status into a /fail alert.
#
# Unit files are NOT applied here: if systemd/ differs from what is installed,
# the status says so and someone runs `sudo systemd/install.sh` after reading
# the diff.
set -uo pipefail
repo=/home/ubuntu/oxygen-mvp
status="$repo/data/deploy_status.txt"
cd "$repo" || exit 1
before=$(git rev-parse --short HEAD)

fail() {
    { echo "failed: $1"; echo "still on $before"; git status --short; } > "$status"
    cat "$status" >&2
    exit 0
}

git fetch --quiet origin main || fail "git fetch origin main"
git merge --ff-only --quiet origin/main || fail "fast-forward to origin/main $(git rev-parse --short origin/main)"
after=$(git rev-parse --short HEAD)

# Generated without the warehouse; the answer agent reads it.
.venv/bin/python scripts/build_limitations_index.py >/dev/null || fail "build_limitations_index.py after deploying $after"

if ! units=$(systemd/install.sh --check 2>&1); then
    { echo "failed: installed units differ from systemd/ at $after; run sudo systemd/install.sh"; echo "$units"; } > "$status"
    cat "$status" >&2
    exit 0
fi
echo "ok $before -> $after" | tee "$status"
