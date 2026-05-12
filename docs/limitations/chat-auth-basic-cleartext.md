---
id: chat-auth-basic-cleartext
title: Public chat behind nginx Basic Auth — credentials in cleartext (HTTP only)
severity: medium
affects:
  - public-chat-surface
  - /chat
since: 2026-05-11
status: accepted-tradeoff
---

# Public chat behind nginx Basic Auth — credentials in cleartext (HTTP only)

The public chat surface at `/chat` is gated by nginx Basic Auth with a single shared credential. The portal site is HTTP-only (no TLS), so credentials and traffic travel in cleartext between the visitor's browser and EC2.

This is an accepted tradeoff for MVP 1.5 controlled-distribution demos:

- The credential is treated as fully disposable — fresh per demo cycle, never reused, rotated on any concern.
- The audience is curated; the URL is shared via secure channels only.
- Modern browsers show "Not secure" in the URL bar; visitors are expected to understand the private-beta context.
- Anyone with the credential has full agent access (no per-user accounts, no audit trail, no granular revocation). Single-credential rotation revokes all access at once.

## Implementation

- `/etc/nginx/.htpasswd` (root:www-data 640) — single `analyst` user, bcrypt hash (`-B` flag), NOT in repo. `.gitignore` blocks `.htpasswd` and `*.htpasswd` defensively.
- nginx config: **only `/chat` is auth-gated** (entry-point gate). SPA internal paths (`/api`, `/assets`, `/home`, `/threads`, `/favicon-logo.svg`, `/oxygen-*.svg/gif/png`) all proxy to `localhost:3000` **without auth**. The plan's original design (auth on every proxied path) didn't survive contact with reality — the SPA's streaming agent POST (`/api/.../threads/<id>/agent`) omits Basic Auth credentials from the request, so nginx 401'd, browser re-prompted, user re-entered the password, fetch still omitted creds → loop. Moving auth to `/chat`-only resolves the loop. See [`nginx/somerville.conf`](../../nginx/somerville.conf).
- Portal routes (`/`, `/docs/`, `/metrics`, `/trust`) remain unauthenticated — the portal is the public window.
- Tailnet `:3000` access stays open (port 3000 closed at AWS SG, reachable only over Tailscale). The Basic Auth path is the *public* alternative; Tailnet remains the private path for the project team.

**Revised risk surface** (compared to the plan's original "auth on every path" design): anyone who discovers `/api/*` URL patterns directly could query the agent without `/chat` auth. This is an API-token-burn risk, not a data-exposure risk (the SPA's API surface is internal workspace plumbing, all on one Oxygen instance). Mitigated by:

- Anthropic spend cap on Gordon's account (currently $5.52 of $100/month; Opus 4.7's 500K input-tokens/min Tier 1 limit also caps catastrophic burn rate).
- The `/chat` URL is the surface that gets shared with prospects; `/api/*` URL patterns only emerge from inside the SPA after login.
- Tailnet `:3000` remains the project-team path; the public Basic Auth route is for demos, not for project work.
- Rotate the credential on any concern about who has it.

## Mitigation

Rotate the credential whenever a person who had it is no longer expected to have access. Never reuse it elsewhere. Treat chat access as low-stakes demo, not production-grade auth. Run:

```bash
sudo htpasswd /etc/nginx/.htpasswd analyst   # without -c — keeps file, updates password
```

Then notify anyone who had the old credential.

## Resolution

MVP 4 brings Magic Link auth + HTTPS via Oxygen multi-workspace mode, replacing this layer entirely. See `docs/plans/` for the MVP 4 scope when it's drafted. The wizard incompatibility with existing populated DuckDB (logged Session 25) is the prerequisite blocker for multi-workspace migration.
