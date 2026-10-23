#!/usr/bin/env bash
# Report a systemd unit's outcome to healthchecks.io (Plan 53). Called from the
# unit's ExecStopPost=, where systemd sets SERVICE_RESULT and EXIT_STATUS.
#
#   hc_ping.sh KEY UNIT [STATUS_FILE...]
#
# KEY picks the ping URL: HC_<KEY>=https://hc-ping.com/<uuid> in
# /etc/wong-way/healthchecks.env (root:ubuntu 640, never in git). No URL, no
# ping, exit 0. Pings /fail when the unit failed, or when any STATUS_FILE's first
# line is not "success" or "ok" (a partial pipeline run, a failed git deploy).
# The body carries the status files and the unit's last journal lines. This
# script never fails the unit it reports on.
set -u
key=${1:?key}; unit=${2:?unit}; shift 2
env_file=/etc/wong-way/healthchecks.env
# shellcheck disable=SC1090
[ -r "$env_file" ] && . "$env_file"
var="HC_${key}"
url=${!var:-}
if [ -z "$url" ]; then
    echo "hc_ping: $var not set in $env_file; not reporting"
    exit 0
fi

suffix=""
body=$(mktemp)
trap 'rm -f "$body"' EXIT
result=${SERVICE_RESULT:-success}
echo "$unit: result=$result exit=${EXIT_STATUS:-0}" >> "$body"
[ "$result" != "success" ] && suffix="/fail"
for f in "$@"; do
    [ -r "$f" ] || continue
    first=$(head -n 1 "$f")
    case "$first" in success|ok*) ;; *) suffix="/fail" ;; esac
    printf '\n== %s\n' "$f" >> "$body"; cat "$f" >> "$body"
done
if [ -n "$suffix" ]; then
    printf '\n== journal\n' >> "$body"
    journalctl -u "$unit" -n 30 --no-pager -o cat >> "$body" 2>/dev/null || true
fi
curl -fsS -m 10 --retry 3 -o /dev/null --data-binary @"$body" "$url$suffix" \
    && echo "hc_ping: reported ${suffix:-/success} for $unit" \
    || echo "hc_ping: could not reach healthchecks.io for $unit"
exit 0
