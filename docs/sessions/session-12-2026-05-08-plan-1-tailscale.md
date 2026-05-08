---
session: 12
date: 2026-05-08
start_time: 13:30 ET
end_time: 13:56 ET
type: code
plan: plan-1
layers: [infra, portal]
work: [feature, infra, hardening]
status: complete
---

# Session 12 — Plan 1 (Tailscale lockdown) D1-D4 closed

## Goal
Close the public `:3000` security gap by moving SSH and Oxygen behind Tailscale, then strip the now-broken public CTAs from the portal.

## What shipped
- Tailscale 1.96.4 installed on EC2; `tailscale up --hostname=oxygen-mvp --ssh`; node IP `100.73.216.43`; MagicDNS `oxygen-mvp.taildee698.ts.net` resolves
- Local `~/.ssh/config` `oxygen-mvp` HostName repointed `18.224.151.49` → `oxygen-mvp.taildee698.ts.net` (backup: `~/.ssh/config.bak.preTailscale`)
- D3 gate green: `ssh oxygen-mvp 'echo ok'` authenticated via `[100.73.216.43]:22`; `:3000` over Tailnet hostname + IP both 200 from laptop
- AWS SG inbound `:22` and `:3000` deleted by Gordon; post-delete probes confirm: Tailnet SSH ok, Tailnet `:3000` = 200, public `:3000` = curl timeout (exit 28), public `:80` = 200
- [portal/index.html](portal/index.html) hybrid update — dropped nav CTA + asset-card link, replaced hero CTA with non-link `Private beta` pill (`.hero-pill` matches `.nav-badge` styling); removed 3 stale Tailnet-link TODO comments + dead `.nav-cta` / `.hero-cta` CSS rules
- Portal deployed to `/var/www/somerville/index.html`; live md5 matches local; commit `ae20c94`

## Decisions
- Portal `/chat` link strategy: hybrid (drop nav + asset-card CTAs, replace hero CTA with `Private beta` pill) — keeps visual hierarchy at the page centerpiece without leaking the Tailnet hostname publicly
- SSH alias repoint targets MagicDNS hostname, not Tailnet IP — IP-stable across node re-registrations
- Tailscale SSH (`--ssh`) enabled alongside OpenSSH pubkey — belt-and-suspenders, no harm

## Issues encountered
- **First portal deploy went to the wrong docroot.** `cp` to `/var/www/html/index.html` reported success but live curl still returned old HTML.

  ```
  Last-Modified: Fri, 08 May 2026 15:48:26 GMT  ← Session 11 timestamp, not new
  md5(/var/www/html/index.html) = c9e467fc... (new)
  md5(curl localhost/)          = 4738c567... (old)
  ```

  Root cause: `nginx -T` showed the active site is `sites-enabled/somerville` with `root /var/www/somerville` — the `default` site's `root /var/www/html` is unused. Redeployed to `/var/www/somerville/index.html`; live md5 then matched. Removed the orphaned copy from `/var/www/html`. Worth documenting in SETUP.md alongside the access-pattern update.

## Next action
Update SETUP.md / CLAUDE.md / ARCHITECTURE.md to reflect the new access pattern (Tailscale-only for SSH and `:3000`; portal docroot at `/var/www/somerville`). Then resume the MVP 1 hardening backlog — trust contract pass on the Answer Agent, or admin DQ framework.
