#!/usr/bin/env bash
# Install this folder's unit files into /etc/systemd/system (Plan 53).
# Copies, not symlinks: a unit change pulled by scripts/deploy_from_git.sh takes
# effect only when someone runs this, never silently at the next reboot.
#
#   sudo systemd/install.sh          copy changed units, daemon-reload, enable timers
#   systemd/install.sh --check       list differences; exit 1 if any (no root needed)
set -euo pipefail
src=$(cd "$(dirname "$0")" && pwd)
dst=/etc/systemd/system
check=0; [ "${1:-}" = "--check" ] && check=1

changed=0
cd "$src"
for f in *.service *.timer */*.conf; do
    [ -f "$f" ] || continue
    if ! cmp -s "$f" "$dst/$f"; then
        changed=1
        echo "differs: $f"
        if [ $check -eq 0 ]; then
            install -d "$dst/$(dirname "$f")"
            install -m 644 "$f" "$dst/$f"
        fi
    fi
done

if [ $check -eq 1 ]; then exit $changed; fi
systemctl daemon-reload
for t in *.timer; do systemctl enable --quiet "$t"; done
echo "installed; daemon reloaded"
