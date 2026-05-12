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
- nginx config: `/chat`, `/assets`, `/api`, and `/favicon-logo.svg` locations all auth-gated and proxied to `localhost:3000`. `/chat` includes WebSocket upgrade headers for streaming agent replies. See [`nginx/somerville.conf`](../../nginx/somerville.conf).
- Portal routes (`/`, `/docs/`, `/metrics`, `/trust`) remain unauthenticated — the portal is the public window.
- Tailnet `:3000` access stays open (port 3000 closed at AWS SG, reachable only over Tailscale). The Basic Auth path is the *public* alternative; Tailnet remains the private path for the project team.

## Mitigation

Rotate the credential whenever a person who had it is no longer expected to have access. Never reuse it elsewhere. Treat chat access as low-stakes demo, not production-grade auth. Run:

```bash
sudo htpasswd /etc/nginx/.htpasswd analyst   # without -c — keeps file, updates password
```

Then notify anyone who had the old credential.

## Resolution

MVP 4 brings Magic Link auth + HTTPS via Oxygen multi-workspace mode, replacing this layer entirely. See `docs/plans/` for the MVP 4 scope when it's drafted. The wizard incompatibility with existing populated DuckDB (logged Session 25) is the prerequisite blocker for multi-workspace migration.
