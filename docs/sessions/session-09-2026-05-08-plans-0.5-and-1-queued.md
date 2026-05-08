---
session: 9
date: 2026-05-08
start_time: 11:30 ET
end_time: unknown
type: planning
plan: none
layers: [docs]
work: [planning, docs]
status: complete
---

# Session 9 — Plan 0 closure + Plans 0.5 and 1 queued

## Goal
Close out Plan 0 feedback, queue next two threads in correct order, capture meta-lessons (environment-specific assumptions, allowlist permissions) before more plans get written.

## What shipped
- Confirmed Plan 0 closed end-to-end: all 6 validation gates green, FR pass intact (2024 regression returns 113,961)
- Plan 0.5 (portal `/chat` fix) — Option A from Code's diagnosis: repoint portal links to `http://18.224.151.49:3000/`, remove broken `location /chat` nginx block, redeploy, browser smoke-test. Standalone, ~10 min.
- Plan 1 (Tailscale) — added pre-flight section "verify environment-specific assumptions before destructive steps." Closes public `:3000` gap. Explicit gates that SSH and `:3000` over Tailscale must work *with successful command execution* before AWS security group changes.
- Plan 1 Deliverable 4 chains to Plan 0.5: updates portal `/chat` link to whatever Tailnet target Gordon chooses

## Decisions
- Sequencing locked: Plan 0.5 → Plan 1 → Plans 2, 3, 4, 5
- Plans touching environment-specific mechanisms (SSH shell modes, systemd inheritance, nginx proxy semantics, Tailscale/Ubuntu networking, Oxygen runtime) must call out assumptions in pre-flight and verify empirically before destructive steps
- Portal `/chat` link points directly to `:3000` for MVP 1; subdomain (Option C) deferred to MVP 2 or post-Tailscale
- Plan 1 Deliverable 4 surfaces an open question for Gordon at execution time: Tailnet IP vs MagicDNS hostname vs other for the portal link target

## Issues encountered
- **Allowlist iteration history was a sustained productivity drag.** Sessions 5, 8, and 9 all touched allowlist tuning. Each round triggered by Code pausing mid-flow on commands that should have been routine. Pauses cost wall-clock time and the ability to leave Code unattended. Per-command allowlisting is a treadmill — every new tool/flag/path generates a fresh prompt, the file accretes, protection erodes because nobody audits a 60-entry allowlist. Plan 0 Deliverable 7 (tool-family-allow + destructive-deny) is the first version that addresses the underlying frame. Verification in next session.

## Next action
Hand Plan 0.5 to Code. After it lands and Gordon confirms in browser, hand Plan 1.
