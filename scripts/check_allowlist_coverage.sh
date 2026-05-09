#!/usr/bin/env bash
# Plan 9 — exercise canonical verification idioms.
# If Code prompts on any line, the allowlist is missing that pattern.
# Run this whenever .claude/settings.json changes; expect zero prompts.

set -e

echo "=== curl ==="
curl -sI http://localhost/ >/dev/null 2>&1 || true

echo "=== for-loop ==="
for f in /tmp; do echo "$f" >/dev/null; done

echo "=== grep + head + wc ==="
echo "test line" | grep test | head -1 | wc -l >/dev/null

echo "=== date ==="
date >/dev/null

echo "=== find + stat ==="
find /tmp -maxdepth 1 -type d | head -1 >/dev/null
stat /tmp >/dev/null

echo "=== jq ==="
echo '{"k":"v"}' | jq -r '.k' >/dev/null

echo "=== sed -i (touch a tmpfile, edit it, remove it) ==="
TMP=$(mktemp)
echo "before" > "$TMP"
sed -i '' 's/before/after/' "$TMP" 2>/dev/null || sed -i 's/before/after/' "$TMP"
grep -q after "$TMP"
rm "$TMP"

echo "=== ssh to EC2 (Tailnet) ==="
ssh oxygen-mvp 'echo ok' >/dev/null

echo "All idioms passed without prompting."
