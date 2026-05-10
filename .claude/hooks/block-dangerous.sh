#!/usr/bin/env bash
# PreToolUse hook for the Bash tool. Denies structurally-risky shell shapes
# that the allowlist syntax can't express (compound commands, command/process
# substitution, leading cd/export). The allowlist still handles per-command
# allow/deny; this hook handles shell *structure*.
#
# Carve-outs vs. the upstream gist (pixelitobenito/claude-code-security-settings):
#   - Loop keywords (do/then/done/fi/else/elif) after `;` are exempt so that
#     `for ... ; do ... ; done`, `while ... ; do ... ; done`, and
#     `if ... ; then ... ; fi` work as single tool calls.
#   - `$((arith))` is exempt from the `$(...)` block.
#
# Exit 0 always; deny is signalled via the JSON hookSpecificOutput payload.

INPUT=$(cat 2>/dev/null) || exit 0
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)

[ "$TOOL_NAME" != "Bash" ] && exit 0

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$COMMAND" ] && exit 0

REASON=""

# 1. Block && and || compound chains.
if echo "$COMMAND" | grep -qE '&&|\|\|'; then
  REASON="Compound commands (&&/||) blocked. One command per tool call."
fi

# 2. Block ; that introduces a new command. Strip allowed shell-keyword
#    semicolons first (`; do`, `; then`, `; done`, `; fi`, `; else`, `; elif`),
#    then if any `;` remains, deny.
if [ -z "$REASON" ]; then
  STRIPPED=$(echo "$COMMAND" | sed -E 's/;[[:space:]]+(do|then|done|fi|else|elif)([[:space:]]|$)/ \1\2/g')
  if echo "$STRIPPED" | grep -qE ';'; then
    REASON="Semicolon-separated commands blocked. One command per tool call. (for/while/if loops are exempt.)"
  fi
fi

# 3. Block command substitution $(...) but NOT arithmetic $((...)).
#    Match `$(` followed by any non-`(` character.
if [ -z "$REASON" ]; then
  if echo "$COMMAND" | grep -qE '\$\([^(]'; then
    REASON="Command substitution \$(...) blocked. Run the inner command first, then use the result."
  fi
fi

# 4. Block process substitution.
if [ -z "$REASON" ]; then
  if echo "$COMMAND" | grep -qE '<\(|>\('; then
    REASON="Process substitution blocked. Write to a temp file instead."
  fi
fi

# 5. Block commands that start with `cd `.
if [ -z "$REASON" ]; then
  if echo "$COMMAND" | grep -qE '^cd[[:space:]]'; then
    REASON="Commands starting with cd blocked. Use absolute paths or git -C instead."
  fi
fi

# 6. Block bare `export VAR=...` (inline `VAR=value command` is fine).
if [ -z "$REASON" ]; then
  if echo "$COMMAND" | grep -qE '^export[[:space:]]'; then
    REASON="export blocked. Use inline VAR=value command prefixing instead."
  fi
fi

if [ -n "$REASON" ]; then
  jq -n --arg reason "$REASON" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
fi

exit 0
