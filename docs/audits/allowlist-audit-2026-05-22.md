# Allowlist audit — 2026-05-22

_Plan 36 / Session 61, written 2026-05-23 by Code. Information request per
PROMPTS.md §2 — produces this report; edits are a separate follow-up._

## Bottom line up front

The 3-tier user-configurable allowlist exists exactly as documented in
CLAUDE.md "Allowlist policy". Across the last 15 transcripts (~10 days,
2,514 Bash tool-use calls), there were **3 real permission-denial events**
— all `git branch -d` / `git branch -D` against worktree branches, all
correctly caught by the existing destructive-deny entries. **52 of 55**
denial events were structural hook denials catching Code's own forbidden
shell shapes (chained commands, semicolons in SSH-quoted strings, command
substitution). The allowlist itself is well-tuned for current usage; the
biggest leverage is in **memory-to-file migration** of five policies that
currently live only in Code's session memory, per the Plan 29 durability
lesson.

## Phase 1 — Current structure

### The three user-configurable tiers (as documented)

CLAUDE.md "Allowlist policy" (lines 219–224) names three tiers. All three
exist as described.

#### Tier 1 — `.claude/settings.json` (committed, git-tracked)

- **Where:** repo root, 339 lines, JSON with top-level `permissions.allow`
  array (≈200 entries) and `permissions.deny` array (≈70 entries).
- **Schema:** Claude Code's settings schema (`$schema` declared on line 2).
  Patterns are command-prefix glob strings inside parens — e.g.,
  `"Bash(git -C * status)"`, `"Bash(curl *)"`, `"mcp__Claude_Preview__preview_screenshot"`.
  `*` is a wildcard within a single argument position. Patterns are
  exact-string matched to the leading token; the wildcard does *not*
  cross `|` (CLAUDE.md "Allowlist policy" pipe-coverage clause).
- **What it contains (by category):**
  - **Tool primitives (write/edit/read/web):** `Read`, `Write`, `Edit`,
    `WebFetch(*)`.
  - **EC2 access:** `Bash(ssh oxygen-mvp *)`, `Bash(scp *)`, `Bash(ssh -o * oxygen-mvp *)`, `Bash(ssh -v ...)`.
  - **Read-only Unix utilities (~30 patterns):** `ls *`, `grep *`, `find *`, `cat *`,
    `head *`, `tail *`, `wc *`, `jq *`, `sort *`, `uniq *`, `awk *`, `sed *`,
    `cut *`, `column *`, `xxd *`, `lsof *`, `file *`, `cmp *`, `less *`, `more *`,
    `tree *`, `du *`, `df *`, `stat *`, `diff *`, `shasum *`, `md5 *`,
    `comm *`, `yq *`, `rg *`, `fd *`, plus `date` / `date *` / `pwd` /
    `uptime` / `whoami` / `echo *` / `printf *` / `test *` / `touch *`.
  - **Git (read-only, mutating, and piped variants — ~40 patterns):**
    `git -C * <subcmd>` for every common subcommand × `Bash(git *)` and
    `Bash(git -C * *)` catch-alls × explicit pipe forms
    `Bash(git * | *)`, `Bash(git -C * * | *)`, `Bash(git * | * | *)`.
  - **gh (PR/issue inspection only — 14 patterns):** `gh pr view *`,
    `gh pr list`, `gh pr diff *`, `gh pr checks *`, `gh pr status`,
    `gh issue view/list`, `gh run view/list`, `gh repo view *`,
    `gh auth status`. **Notable absence:** no `gh pr create *` or
    `gh pr merge *` — the autonomous PR-merge policy depends on them
    and they prompt per session.
  - **Data tooling:** `dbt *`, `oxy *`, `airlayer *`, `duckdb *`,
    `python *`, `python3 *`, `bash *`, `pip install *`, `pip list *`,
    `pip show *`, `pip freeze *`, `aws *`, `aws * | *`, `aws * | * | *`.
  - **Sudo (scoped):** `sudo nginx *`, `sudo systemctl reload/status/restart nginx`,
    `sudo systemctl daemon-reload`, `sudo tail * /var/log/nginx/*`,
    `sudo cat /etc/nginx/*`, `sudo grep * /etc/nginx/*`,
    `sudo sed -n * /etc/nginx/*`, `sudo cp|mv|ln /etc/{nginx,systemd/system}/*`,
    `sudo chmod *`, `sudo chown *`.
  - **Shell-loop constructs (carved out by hook + matcher):**
    `for * in *; do *; done`, `while * do * done`, `if * then * fi`,
    `[ * ]`, `[[ * ]]`.
  - **Run pipeline:** `Bash(./run.sh)`, `Bash(./run.sh *)`,
    `Bash(./scripts/*.sh)`.
  - **Plan 33+ additions (read-only):** `Bash(tailscale status)`,
    `Bash(tailscale status *)`, `mcp__Claude_Preview__preview_screenshot`,
    `mcp__Claude_Preview__preview_inspect`,
    `mcp__Claude_in_Chrome__tabs_context_mcp`,
    `mcp__Claude_in_Chrome__list_connected_browsers`.
  - **Plus `Read`/`Write` allowlist entries for `.claude/settings.local.json`** in this repo and in worktrees.
- **What it denies (~70 patterns):**
  - **PII / credentials:** `Read(**/.env)`, `Read(~/.ssh/**)`, `Read(~/.gnupg/**)`.
  - **Destructive git:** `git reset --hard *`, `git reset --hard`,
    `git push --force *`, `git push -f *`, `git push --force-with-lease *`,
    `git branch -d *`, `git branch -D *`, and `git -C *` variants of each.
  - **Destructive filesystem:** `rm -rf *`, `rm -rf /*`, `rm -rfd *`,
    `rm -fr *`, `sudo rm *`, `sudo dd *`.
  - **Sudo system-wide:** `sudo chmod * /etc/*`, `sudo chown * /etc/*`,
    `sudo cp|mv|ln * /etc/*`, `sudo bash *`, `sudo sh *`, `sudo -i`,
    `sudo -s`.
  - **AWS destructive:** ~20 patterns covering `terminate-*`,
    `stop-instances`, `delete-*`, `modify-*` across EC2 / S3 / S3API /
    IAM / RDS / CloudFormation / Lambda / Route53 / KMS / Secrets Manager.
  - **Shell injection (`curl|wget | bash/sh`):** `curl * | bash*`,
    `curl * | sh*`, `wget * | bash*`, `wget * | sh*`.
  - **Other:** `launchctl *`, `eval *`.

- **Changing it:** requires a commit (Gordon-reviewed-and-merged per
  CLAUDE.md). Evidence rule: a TASKS.md `[x]` for any allowlist change
  must include `git show HEAD:.claude/settings.json | grep -F '<pattern>'`.

#### Tier 2 — `.claude/settings.local.json` (per-machine, gitignored)

- **Where:** repo root, gitignored at `.gitignore` line 35.
- **Schema:** identical JSON shape to Tier 1 — `permissions.allow` array.
- **Current content (post-Plan-34 prune):**
  ```json
  { "permissions": { "allow": [
      "Read(//Users/gordonwong/.ssh/**)",
      "Bash(gh repo *)"
  ]}}
  ```
  Both entries are intentional: SSH key path (machine-specific path
  format) and a `gh repo *` wildcard Gordon added for the
  `oxygen-mvp-workstation-bundle` work.
- **What it contains:** machine-specific patterns only. CLAUDE.md
  explicitly says: "anything load-bearing should already be covered by a
  tool-family wildcard in `settings.json`."
- **Changing it:** Code may self-amend freely. Prune drift whenever it
  accumulates.

#### Tier 3 — `.claude/worktrees/*/.claude/settings.local.json` (also gitignored)

- **Where:** under each worktree dir; the `.claude/worktrees/` parent
  itself is gitignored at `.gitignore` line 36.
- **Schema:** same JSON shape.
- **What it should contain:** an exact mirror of Tier 2.
- **Drift behavior:** worktree drift IS the bug per CLAUDE.md. The
  project hasn't tripped on this recently because most of the active
  worktrees from earlier sessions have closed out, but it's a real risk
  whenever multiple long-lived worktrees coexist.

### Two additional surfaces that affect what reaches the allowlist matcher

These are NOT tiers, but they shape what the user sees as "an allowlist
denial" in practice. Worth knowing for an honest read of the structure.

#### Bash safety hook — `.claude/hooks/block-dangerous.sh`

A PreToolUse hook that runs BEFORE the allowlist matcher. Denies
**shell structure** that the allowlist syntax can't express:

- `&&` or `||` chains → "Compound commands blocked"
- `;` separating commands (with carve-outs for `do`/`then`/`done`/`fi`
  loop keywords) → "Semicolon-separated commands blocked"
- `$(...)` command substitution (arithmetic `$((...))` exempt)
  → "Command substitution blocked"
- `<(...)`, `>(...)` process substitution → "Process substitution blocked"
- Leading `cd ` (must use `git -C` or absolute paths instead)
- Leading `export VAR=`
- Shell redirects to create files (`echo > foo`, `cat <<EOF > foo`)

Hook exits 0 always; deny is signalled via `hookSpecificOutput` JSON.
**The hook scans the literal command string regardless of whether the
chain executes locally or via SSH** — `ssh oxygen-mvp 'cmd1 && cmd2'`
is denied because of the `&&`. Tonight's denial scan showed this
catching real Code mistakes 52 times in the last 10 days.

#### Built-in auto-allow (Claude Code source)

Not in `.claude/settings.json` — baked into Claude Code itself. Per the
`fewer-permission-prompts` skill documentation:

- **Always auto-allowed (any args):** ~40 commands including `cat`,
  `head`, `tail`, `wc`, `stat`, `ls`, `find`, `cd`, `echo`, `printf`,
  `true`, `false`, `sleep`, `which`, `type`, `expr`, `test`, `seq`,
  `cut`, `paste`, `tr`, `column`, `tac`, `rev`, `fold`, `nl`, `id`,
  `uname`, `free`, `df`, `du`, `locale`, `groups`, `nproc`, `basename`,
  `dirname`, `realpath`, `readlink`, `diff`, `getconf`, `tsort`, `pr`,
  `cal`, `uptime`, `strings`, `hexdump`, `od`, `comm`, `cmp`, `fmt`,
  `expand`, `unexpand`, `numfmt`.
- **Auto-allowed zero-arg:** `pwd`, `whoami`, `alias`.
- **Auto-allowed safe flags:** `xargs`, `file`, `sed` (read-only),
  `sort`, `man`, `help`, `netstat`, `ps`, `base64`, `grep`, `egrep`,
  `fgrep`, `sha256sum`, `sha1sum`, `md5sum`, `tree`, `date`, `hostname`,
  `info`, `lsof`, `pgrep`, `tput`, `ss`, `fd`, `fdfind`, `aki`, `rg`,
  `jq`, `uniq`, `history`, `arch`, `ifconfig`, `pyright`.
- **All git read-only subcommands** (`git status`, `git log`, `git diff`, `git show`, `git blame`, `git branch`, `git tag`, `git remote`, `git ls-files`, `git ls-remote`, `git config --get`, `git rev-parse`, `git describe`, `git stash list`, `git reflog`, `git shortlog`, `git cat-file`, `git for-each-ref`, `git worktree list`).
- **All gh read-only subcommands.**
- **Docker read-only subcommands** (`docker ps`, `docker images`, `docker logs`, `docker inspect`).

These never appear in any settings file — they're hardcoded into the
matcher. Many of the patterns in this project's `settings.json` (e.g.,
`Bash(ls *)`, `Bash(grep *)`, `Bash(cat *)`, `Bash(jq *)`, the
`Bash(git -C * log)` family) are redundant against the built-in
auto-allow. Not load-bearing redundancy; just historical accretion.

### Precedence rules

Order of evaluation, observed and inferred:

1. **Built-in auto-allow** (silent allow, never prompts).
2. **`deny` patterns in any tier** (silent deny — though in practice the
   `deny` list lives only in Tier 1 / `settings.json`). The destructive
   patterns explicitly named in deny do block before any allow pattern
   can match.
3. **Bash safety hook** (deny via hookSpecificOutput, with the
   structural reasons named above).
4. **`allow` patterns in any tier** (silent allow; tiers stack
   additively).
5. **No match** → permission prompt to user.

Where this could be ambiguous: the relative order of #1 vs #3 isn't
formally documented. In practice the hook runs as a PreToolUse hook
which fires before the matcher evaluates allow/deny, but built-in
auto-allow may short-circuit even earlier. Tonight's denial scan caught
hook denials on commands that would have been built-in auto-allowed if
written without chains (e.g., `ls ... 2>/dev/null || echo "no"` would
have auto-allowed `ls`, but the `||` triggers the hook first). So #3
beats #1 — the hook gets a vote even on auto-allowed commands.

### Policies currently in memory rather than on file

These memory files contain durable project policy (not session state or
profile data) that arguably belongs in a committed CLAUDE.md /
PROMPTS.md / STANDARDS.md section per Plan 29's durability lesson.
Flagged here; migration is a separate decision in §3 recommendations.

| Memory file | What it covers | File-home candidate |
|---|---|---|
| `feedback_session_boot_audit.md` | 90-second four-check boot audit; step 4 has the portal/index.html drift-check extension from Plan 34 B1 | CLAUDE.md new "Session Boot Audit" subsection or extension of "Session Start on EC2" |
| `feedback_git_ssh_gotchas.md` | Three workarounds: scp→pull lock (`git checkout --` first), bash hook scans SSH-quoted strings (use scratch-wrapper), worktree can't `checkout main` if parent has it (use `-b <new> origin/main`) | CLAUDE.md "Known gotchas" section (postBuffer note already there from Plan 34 B3) |
| `feedback_no_ssh_heredocs.md` | Write ad-hoc SQL/Python to `scratch/`, scp, run via `ssh ... -f /tmp/foo.sql` rather than heredocs over ssh | CLAUDE.md "Bash Safety" or "Known gotchas" |
| `feedback_chat_code_handoff.md` | End-of-thread summary format: gate table + Shipped + Worth flagging + Next | PROMPTS.md §5 or a new §6 |
| `feedback_settings_json.md` | Code is free to edit `.claude/settings.json` proactively to allowlist read-only commands | CLAUDE.md "Allowlist policy" sub-bullet |

Memory files that are correctly memory-resident (NOT migration candidates):

- `user_profile.md`, `user_role_no_typing.md` — user-specific profile data.
- `project_status.md` — point-in-time project state; rotates as project evolves.
- `feedback_log_updates.md` — single one-line rule, but already redundantly covered by CLAUDE.md "LOG.md and Sessions Logging Protocol".
- `feedback_ec2_workflow.md` — covered by CLAUDE.md "Run Order".
- `feedback_autonomous_execution.md` — explicitly a pointer to CLAUDE.md (correctly externalized).
- `feedback_bash_command_form.md` — fully covered by CLAUDE.md "Bash Safety".
- `feedback_no_parallel_code_session.md` — workflow context, not project policy.
- `feedback_verify_quantitative_claims.md` — could go in STANDARDS.md, but it's about Code's epistemic discipline rather than project gates; debatable.
- `project_dbt_duckdb_schema_naming.md` — fully covered by CLAUDE.md "Naming Standards".

## Phase 2 — Denial inventory

### Evidence source 1: JSONL transcripts (last 10 days, 15 files, 2,514 Bash calls)

Scanner: `scratch/scan_denials.py`. Counts hook denials by structural
category and surfaces real permission-denial events with the original
command.

**Total tool_results with `is_error: true`:** 200. Most are non-denial
errors (file-not-found, network failures, dbt build errors, etc.).
Of those, 55 are denial events:

| Category | Count | Sessions | Example |
|---|---|---|---|
| Hook: Semicolon `;` | 31 | 6 | `ssh oxygen-mvp 'python3 -c "import json; m=json.load(...); doc=..."'` |
| Hook: Compound `&&` / `\|\|` | 21 | 7 | `ls .../worktrees/ 2>/dev/null \|\| echo "no worktrees dir"` |
| Hook: Command substitution `$()` | 2 | 2 | `git -C .../worktrees/... push -u origin claude/handoff...` (had `$(date ...)` embedded) |
| **Allowlist: explicit deny** | **3** | **1** | `git -C .../worktrees/... branch -d claude/asciify-workspace-spa-fix` and two siblings (all destructive branch deletes) |

**Read of this distribution:**

- 96% of denial events are HOOK denials — Code writing forbidden shell
  shapes despite CLAUDE.md "Bash Safety" explicitly forbidding them.
  This is a *Code behavior issue*, not an allowlist gap. The single
  most-frequent pattern is `;` inside SSH-quoted strings (`ssh foo
  'python3 -c "...;..."'`), which the bash hook catches because it
  scans the literal command string regardless of where it executes.
  The fix is already in memory (`feedback_no_ssh_heredocs.md` and
  `feedback_git_ssh_gotchas.md` both name the scratch-wrapper pattern)
  and in CLAUDE.md "Bash Safety". Code keeps writing it anyway and
  the hook keeps catching it.
- The 3 real permission denials are all `git branch -d` / `git branch -D`
  — explicitly in `settings.json` deny list (lines 242–245). Working
  exactly as designed.

### Evidence source 2: Live probes

Ran 9 representative read-only commands as separate Bash tool calls;
recorded whether they succeeded cleanly. (Live probes can't distinguish
"auto-allow" from "user-approved-on-prompt" — both look like success
in the tool result. So this confirms the auto-allow set works for the
named commands without confirming where the allow happens.)

| Command | Result | Likely allow source |
|---|---|---|
| `ls /Users/gordonwong/claude-projects/oxygen-mvp` | ✅ output | built-in auto-allow OR `Bash(ls *)` in Tier 1 |
| `pwd` | ✅ output | built-in auto-allow (zero-arg) OR `Bash(pwd)` in Tier 1 |
| `git -C ... log --oneline -3` | ✅ output | built-in git read-only auto-allow OR `Bash(git -C * log *)` in Tier 1 |
| `head -3 README.md` | ✅ (file-not-found error, not denial) | built-in auto-allow OR `Bash(head *)` in Tier 1 |
| `find docs -name "session-60-*.md"` | ✅ output | built-in auto-allow OR `Bash(find *)` in Tier 1 |
| `grep -c "Plan" LOG.md` | ✅ output | built-in auto-allow (safe flags) OR `Bash(grep *)` in Tier 1 |
| `tail -3 LOG.md` | ✅ output | built-in auto-allow OR `Bash(tail *)` in Tier 1 |
| `cat .gitignore \| head -3` | ✅ output | piped form needs Tier 1 `Bash(... \| ...)` since built-in doesn't cover pipes |
| `git -C ... status -s` | ✅ output | built-in git read-only OR Tier 1 |
| `git -C ... diff --stat` | ✅ output | built-in git read-only OR Tier 1 |

No live probe surfaced a denial. The auto-allow set + Tier 1 patterns
cover all the read-only commands a normal session needs.

### Cross-check: known recent prompts (not denials) from session memory

Tonight's audit can't easily distinguish prompts from auto-allows in the
transcripts (both render as successful tool calls). Session 57's earlier
`/fewer-permission-prompts` skill run captured the prompt-but-approved
class explicitly via the `settings.local.json` deltas Gordon had pinned:

- `tailscale status` (now in Tier 1 after Plan 33-skill addition).
- `gh pr create *` (still prompts every PR creation).
- `gh pr merge *` (still prompts every merge).
- `ls -la /tmp/...` (auto-allowed in principle via `Bash(ls *)`, but
  Gordon's local had pinned an exact form — possible matcher quirk
  with leading flags; not load-bearing).

The `gh pr create *` / `gh pr merge *` prompt pattern is the operational
papercut most worth fixing — every autonomous push-PR-merge cycle
(several per session) prompts twice. The autonomous-execution policy in
CLAUDE.md explicitly endorses these flows; the allowlist doesn't yet
permit them.

## Recommendations

### Tier-1 additions (`.claude/settings.json`, committed)

Two patterns are clearly load-bearing across sessions and worth elevating:

1. **`Bash(gh pr create *)`** — every autonomous PR-creation cycle hits
   this. Mutating (creates a PR), but the autonomous-execution policy in
   CLAUDE.md "Receiving prompts from Chat → Autonomous PR-merge policy"
   explicitly endorses it for this repo. Single-line addition.

2. **`Bash(gh pr merge *)`** — same logic. The destructive variants
   (`--force-with-lease`-equivalents for merges) don't exist in `gh`;
   the worst-case `gh pr merge --merge --delete-branch` is exactly the
   intended autonomous flow.

Both are tracked-policy mismatches: CLAUDE.md says do these autonomously,
but `settings.json` makes Code prompt for them. Fixing this is one of
Plan 37's clearest line items.

### Tier-2 additions (`.claude/settings.local.json`, per-machine)

None recommended from this audit. Tier 2 is already pruned to two
intentional entries; nothing in the denial evidence suggests new
machine-specific patterns are needed.

### Memory-to-file migrations (Plan 29 durability)

Five memory files cover durable project policy that arguably belongs in
CLAUDE.md / PROMPTS.md:

1. **`feedback_session_boot_audit.md`** → CLAUDE.md new "Session Boot
   Audit" subsection. The 90-second four-check audit is a session-start
   discipline that every Code instance should follow, not just ones
   that happen to have my memory. The step-4-extension (portal/index.html
   drift check) added in Plan 34 B1 makes this even more load-bearing.
2. **`feedback_git_ssh_gotchas.md`** → CLAUDE.md "Known gotchas" (extend
   the section Plan 34 B3 added). The three workarounds (scp→pull lock,
   SSH-string scan, worktree main-checkout block) are real footguns
   that any new Code session would hit immediately.
3. **`feedback_no_ssh_heredocs.md`** → CLAUDE.md "Bash Safety" or a
   sibling subsection. The scratch-wrapper pattern is the right answer
   to the most-frequent hook denial (semicolons in SSH-quoted strings,
   31 hits tonight).
4. **`feedback_chat_code_handoff.md`** → PROMPTS.md §5 (or new §6). The
   end-of-thread report shape (gate table + Shipped + Worth flagging
   + Next) is already the de-facto standard.
5. **`feedback_settings_json.md`** → CLAUDE.md "Allowlist policy" as a
   sub-bullet. Currently a single one-liner saying "Code may edit
   `settings.json` proactively for read-only patterns" — easily
   absorbed.

### Single most impactful denial

**The `;`-in-SSH-quoted-strings hook denial pattern** (31 events across
6 sessions, the largest category). The friction is from Code repeating
the same mistake despite the workaround being documented in two places
(memory + CLAUDE.md "Bash Safety"). **Not an allowlist gap** — fixing
this is a Code-discipline issue, not a settings change.

Within actual allowlist gaps, the most impactful is `gh pr create *` /
`gh pr merge *` (Tier 1 additions above) — every PR cycle prompts
unnecessarily despite the autonomous-execution policy endorsing it.

## Worth flagging

- **The "3-tier" framing is real but incomplete.** Two surfaces outside
  the tiers shape what the user actually sees: the bash safety hook
  (catches structural denials BEFORE the matcher) and Claude Code's
  built-in auto-allow (allows ~70 read-only commands WITHOUT any
  settings entry). About a third of Tier 1's read-only utility patterns
  (`Bash(ls *)`, `Bash(grep *)`, `Bash(cat *)`, `Bash(jq *)`, the
  `Bash(git -C * log)` family) are redundant against the built-in
  auto-allow. Not load-bearing redundancy — historical accretion. Not
  worth pruning unless Plan 37 needs the space for clarity.
- **The hook + auto-allow precedence isn't formally documented.** I
  inferred order #1 (auto-allow) < #3 (hook) from a denial event where
  `ls ... 2>/dev/null || echo "no"` was hook-denied for `||` despite
  `ls` being auto-allowed. The hook gets a vote even on auto-allowed
  commands. Worth a one-line note in CLAUDE.md "Allowlist policy" or
  "Bash Safety" if Plan 37 touches that area.
- **No halt conditions fired.** The 3-tier structure exists as
  CLAUDE.md describes; denial inventory had real evidence (55 events);
  recommendations are all in `settings.json` / memory scope (no
  external-system blockers).
- **Code-recommendation on Plan 37 timing:** the two Tier-1 additions
  (`gh pr create *`, `gh pr merge *`) are obvious one-line edits that
  fix the most-frequent operational papercut. Drafting Plan 37 to land
  them is low-risk and high-yield. The memory-to-file migrations are
  more substantive (each is a real CLAUDE.md / PROMPTS.md edit) — those
  are worth a real conversation about placement and wording before
  drafting. Suggested split: Plan 37 = the two `gh` additions (small,
  immediate); Plan 38 (or 37b) = memory-to-file migrations (larger,
  deliberate). Gordon's call on whether to combine or separate.
