---
session: 11
date: 2026-05-08
start_time: 11:35 ET
end_time: 11:48 ET
type: code
plan: plan-0.5
layers: [portal, infra]
work: [bugfix, infra]
status: complete
---

# Session 11 — Portal /chat fix (Plan 0.5)

## Goal
Make the portal chat link actually open the chat UI in a browser. Today's `/chat` href renders blank because nginx proxies the SPA HTML at `/chat` but not the `/assets/*.js` paths the HTML references.

## What shipped
- `portal/index.html` — three `href="/chat"` → `href="http://18.224.151.49:3000/"` with HTML comments noting the URL changes when Tailscale lands. Commit `6d76594`.
- EC2 nginx: removed `location /chat { ... }` block from `/etc/nginx/sites-available/somerville`; backed up old config to `somerville.bak.20260508`. `nginx -t` clean, `systemctl reload nginx` OK.
- EC2 deploy: `sudo cp portal/index.html /var/www/somerville/index.html`. Served HTML now has 3 `:3000` hrefs and 0 `/chat` hrefs.

## Decisions
None new — Option A decision captured in Decisions Log row dated 2026-05-08 11:30 ET (Session 9).

## Issues encountered
- **First curl test of `/chat` returned 200 right after `systemctl reload nginx`.** Race: nginx graceful reload keeps old workers serving until they finish; the curl ran in the same multi-command ssh and hit a worker still on the old config. Re-ran a few seconds later: 404, as expected. Resolution: gate-checking commands need to be in a separate ssh after `reload`, or use `restart` instead of `reload`. Logged for next time.

## Validation gates
1. `portal/index.html` has 3 `:3000` hrefs, 0 `/chat` hrefs — ✅
2. `grep -c 'location /chat' /etc/nginx/sites-available/somerville` returns 0 — ✅
3. `sudo nginx -t` exits 0 — ✅
4. `curl -I http://localhost/chat` returns 404 — ✅
5. Gordon's browser test: chat UI loads + 2024 question streams a response — pending

## Next action
Hand Plan 1 (Tailscale) to Code after Gordon confirms gate 5. Plan 1 Deliverable 4 will repoint these same hrefs to a Tailnet target.
