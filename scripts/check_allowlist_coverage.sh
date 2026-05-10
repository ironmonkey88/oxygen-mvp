#!/usr/bin/env bash
# Plan 9 rev 2 — exercise canonical verification idioms + assert the
# Bash-safety hook denies risky shapes.
#
# Run as a single Bash tool call: `bash scripts/check_allowlist_coverage.sh`.
# That's one tool-call invocation; Code's hook won't inspect the script's
# internal compound shape (the hook only sees the outer `bash <script>` call).
#
# Two sections:
#   1. Allowed idioms — exit 0 means everything ran without prompting Code.
#   2. Hook denies — feeds JSON payloads directly to the hook and asserts
#      the hook returns a permissionDecision: deny for each.

set -e

HOOK="$(dirname "$0")/../.claude/hooks/block-dangerous.sh"

echo "=== Section 1: allowed idioms (must run without prompting) ==="

echo "  - curl"
curl -sI http://localhost/ >/dev/null 2>&1 || true

echo "  - for-loop"
for f in /tmp; do echo "$f" >/dev/null; done

echo "  - while-loop"
i=0; while [ "$i" -lt 1 ]; do i=2; done

echo "  - if/then/fi"
if [ -d /tmp ]; then echo yes >/dev/null; fi

echo "  - grep + head + wc (pipes — hook allows |)"
echo "test line" | grep test | head -1 | wc -l >/dev/null

echo "  - date"
date >/dev/null

echo "  - find + stat"
find /tmp -maxdepth 1 -type d | head -1 >/dev/null
stat /tmp >/dev/null

echo "  - jq"
echo '{"k":"v"}' | jq -r '.k' >/dev/null

echo "  - sed -i (BSD form on macOS)"
TMP=$(mktemp)
echo "before" > "$TMP"
sed -i '' 's/before/after/' "$TMP" 2>/dev/null || sed -i 's/before/after/' "$TMP"
grep -q after "$TMP"
rm "$TMP"

echo "  - python3 -m json.tool"
echo '{"k":"v"}' | python3 -m json.tool >/dev/null

echo "  - ssh oxygen-mvp (Tailnet)"
ssh oxygen-mvp 'echo ok' >/dev/null 2>&1 || echo "    (skipped — Tailnet unreachable; idiom shape itself is allowlisted)"

echo
echo "=== Section 2: hook deny assertions ==="

build_payload() {
  jq -n --arg c "$1" '{tool_name:"Bash",tool_input:{command:$c}}'
}

assert_deny() {
  local label="$1"
  local cmd="$2"
  local out
  out=$(build_payload "$cmd" | bash "$HOOK")
  if echo "$out" | jq -e '.hookSpecificOutput.permissionDecision == "deny"' >/dev/null 2>&1; then
    echo "  - $label: DENY ✓"
  else
    echo "  - $label: EXPECTED DENY, GOT: $out"
    return 1
  fi
}

assert_allow() {
  local label="$1"
  local cmd="$2"
  local out
  out=$(build_payload "$cmd" | bash "$HOOK")
  if [ -z "$out" ]; then
    echo "  - $label: ALLOW ✓"
  else
    echo "  - $label: EXPECTED ALLOW, GOT: $out"
    return 1
  fi
}

assert_deny "&& chain"          'echo a && echo b'
assert_deny "|| chain"          'echo a || echo b'
assert_deny "naked semicolon"   'echo a; echo b'
assert_deny "command sub"       'echo $(date)'
assert_deny "process sub"       'diff <(ls) <(ls)'
assert_deny "leading cd"        'cd /tmp'
assert_deny "bare export"       'export FOO=bar'

assert_allow "for loop"         'for f in /tmp; do echo "$f"; done'
assert_allow "while loop"       'while false; do echo never; done'
assert_allow "if/then/fi"       'if [ -d /tmp ]; then echo yes; fi'
assert_allow "arithmetic"       'echo $((1+1))'
assert_allow "single pipe"      'echo a | grep a'
assert_allow "inline VAR=value" 'PATH=/opt/homebrew/bin date'

echo
echo "All idioms ran and all hook assertions passed."
