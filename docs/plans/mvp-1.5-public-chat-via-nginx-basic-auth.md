# Plan: Public Chat Access via nginx Basic Auth (MVP 1.5)

**For:** Code (next session, after MVP 1 sign-off)
**Status:** Ready to execute — DO NOT START until prerequisites cleared
**Estimated effort:** 1–2 hours
**Prerequisite:** MVP 1 signed off; `oxy start --local` running; portal serving at port 80; SPA reachable at Tailnet `:3000`

> **Hand-off note from Code, 2026-05-11:** This plan is saved verbatim from Gordon's pasted brief. As of save time, MVP 1 sign-off is still gated on:
> 1. SPA browser gate 3 (Gordon asks "How many 311 requests were opened in 2024?" via `http://oxygen-mvp.taildee698.ts.net:3000` and confirms 113,961 with full trust contract)
> 2. Reboot test gate 4 (`sudo reboot` and verify oxy comes back on its own)
> 3. Close-out ritual (STANDARDS §6 header note, LOG Current Status flip, CLAUDE.md MVP Sequence flip, TASKS.md sign-off section all `[x]`)
>
> Do not execute this MVP 1.5 plan until those three are done. The systemd unit on EC2 is already running `oxy start --local` (pivoted from the multi-workspace wizard attempt, which had no path for existing populated DuckDB — see `agent-rate-limit-multi-turn-spa` limitation entry context for related notes).

---

## Goal

Expose Oxygen's chat SPA publicly at `http://18.224.151.49/chat`, gated by nginx Basic Auth with a single shared credential. Visitor lands on the portal hero, clicks "Try the chat," gets a browser auth prompt, enters credentials, lands in a working SPA chat session.

Same-site experience. Single URL (`18.224.151.49`), no separate hostnames, no port-3000 in any visible link. The portal and the chat live at the same origin.

## Why this scope, and not more

We considered HTTPS + proper SSO (4–16 hours) and rejected it as too much work for MVP 1. We're accepting three explicit tradeoffs:

1. **HTTP cleartext.** No TLS. Credentials and traffic visible to any on-path observer. Browsers will show "Not secure."
2. **Single shared credential.** Anyone with `analyst` + the password has full agent access. No per-user accounts, no audit trail, no granular revocation.
3. **Will be thrown away in MVP 4.** Proper auth (Magic Link + HTTPS) lands with MVP 4's sharing surfaces. This MVP 1.5 work is deliberately disposable scaffolding.

This is documented as `chat-auth-basic-cleartext` in the limitations registry (Step 7 below) so the tradeoff is recorded explicitly, not implicit.

The credential is treated as fully disposable — fresh per demo, never reused elsewhere, rotated on any concern.

## What you're building

```
Public internet
       ↓ (port 80, HTTP)
   18.224.151.49
       ↓
   nginx (already running)
       ├─ /              → /var/www/somerville/index.html (portal, no auth)
       ├─ /docs/         → /var/www/somerville/docs/ (no auth)
       ├─ /metrics       → /var/www/somerville/metrics.html (no auth)
       ├─ /trust         → /var/www/somerville/trust.html (no auth)
       └─ /chat          → proxy to localhost:3000 (Basic Auth)
           + any SPA asset paths it needs
                          ↓
                    Oxygen SPA at :3000
                    (Tailnet stays accessible too;
                     no AWS SG changes needed)
```

The portal stays as the opening note. The chat link in the hero (currently a static "Private beta" pill) becomes a real link to `/chat`. Visitors get an auth prompt, then the workspace.

## Pre-flight

Before starting:

```bash
ssh oxygen-mvp

# Confirm Oxygen is running and SPA is reachable
sudo systemctl is-active oxy
# Expect: active
curl -sI http://localhost:3000 | head -1
# Expect: HTTP/1.1 200 OK

# Confirm nginx is running and current sites are healthy
sudo systemctl is-active nginx
# Expect: active
curl -sI http://localhost/ | head -1
# Expect: HTTP/1.1 200 OK
curl -sI http://localhost/docs/ | head -1
# Expect: HTTP/1.1 200 OK
curl -sI http://localhost/metrics | head -1
# Expect: HTTP/1.1 200 OK
curl -sI http://localhost/trust | head -1
# Expect: HTTP/1.1 200 OK

# Back up the existing nginx config for rollback
sudo cp /etc/nginx/sites-available/somerville /etc/nginx/sites-available/somerville.bak.pre-chat-auth

# Confirm apache2-utils is installed (or install it)
which htpasswd || sudo apt-get install -y apache2-utils
```

Gate: all checks pass. If anything fails, stop and diagnose.

## Step 1 — Create the htpasswd credential

```bash
# Generate the htpasswd file with username 'analyst'
sudo htpasswd -c /etc/nginx/.htpasswd analyst
# Prompts for password twice — generate a fresh random string here, do not reuse

# Set ownership and permissions (root readable, www-data readable, world unreadable)
sudo chown root:www-data /etc/nginx/.htpasswd
sudo chmod 640 /etc/nginx/.htpasswd

# Verify
sudo cat /etc/nginx/.htpasswd
# Expect: analyst:$apr1$... (bcrypt or md5-apr1 hash)
ls -la /etc/nginx/.htpasswd
# Expect: -rw-r----- 1 root www-data
```

**Critical**: record the password securely (1Password, password manager, or wherever Gordon stores rotating shared secrets). Do NOT commit it to the repo. Do NOT include it in commit messages or session logs.

When sharing access with someone, send the URL + username + password through a secure channel (Signal, encrypted email, password-manager share).

## Step 2 — Discover SPA asset paths

This is the brittle part. Budget 30–60 minutes.

The Oxygen SPA at `:3000` uses absolute paths for its assets. When proxied at `/chat`, those paths won't route correctly unless nginx has explicit location blocks for each.

You need to enumerate every base path the SPA requests. Two approaches:

**Approach A (recommended, more reliable):** Use the browser's DevTools.

From a Tailnet-connected machine:

1. Open `http://oxygen-mvp.taildee698.ts.net:3000` in Chrome/Firefox
2. Open DevTools → Network tab
3. Reload the page with cache disabled (Cmd-Shift-R / Ctrl-Shift-R)
4. Click around the workspace — load the chat, click into a thread, send a message, view an agent
5. In the Network tab, sort by URL
6. List every unique base path the SPA fetches from. Look for paths like:
   * `/static/...` or `/assets/...` or `/_next/...` (static assets — CSS, JS, fonts, images)
   * `/api/...` or `/v1/...` (API endpoints)
   * `/auth/...` or `/login/...` (auth flows — should NOT exist since `--local` mode is guest)
   * WebSocket connections (`ws://...` or `wss://...`) — note these specifically
   * Any other prefixes you see

Write the list down. Likely 3–6 unique base paths.

**Approach B (fallback, less reliable):** Inspect the SPA's HTML.

```bash
curl -s http://localhost:3000/ | grep -oE 'src="[^"]*"|href="[^"]*"' | sort -u
```

This shows the static asset references in the initial HTML, but misses paths loaded dynamically via JavaScript after page load. Use A if at all possible.

Record the result in the session log for future reference. If Oxygen updates its SPA structure, this list will need refreshing.

## Step 3 — Add /chat location and asset proxies to nginx

Edit `/etc/nginx/sites-available/somerville`. Add the following inside the existing `server { ... }` block (probably below the existing location blocks):

```nginx
# Main chat entry point — auth-gated
location /chat {
    auth_basic "Somerville Analytics — Private Beta";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # Strip the /chat prefix when proxying
    rewrite ^/chat/?(.*)$ /$1 break;
    proxy_pass http://localhost:3000;

    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # WebSocket support (required for SPA streaming + chat updates)
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}

# SPA asset paths — must also be auth-gated and proxied to :3000
# Add a block for EACH unique base path discovered in Step 2.
# Examples (replace with the actual paths from your discovery):

location /static {
    auth_basic "Somerville Analytics — Private Beta";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /api {
    auth_basic "Somerville Analytics — Private Beta";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}

# ... add additional blocks for each base path discovered in Step 2
```

Important constraints:

* DO NOT make these locations world-readable. Every SPA asset path needs `auth_basic` — without it, unauthenticated visitors could fetch `/static/main.js` directly even though `/chat` is gated. The asset paths must be gated too.
* DO NOT conflict with existing locations. If a SPA asset path happens to match an existing portal route (e.g., the SPA uses `/docs` — unlikely but possible), Code needs to call this out and resolve the conflict before proceeding.
* Watch for `/api` collision. If the portal or any future portal route uses `/api`, this needs disambiguation.

Test the config syntax:

```bash
sudo nginx -t
# Expect: syntax is ok; test is successful
```

If syntax fails, do NOT reload. Fix the config first.

Reload nginx:

```bash
sudo systemctl reload nginx
```

## Step 4 — Verify auth prompts and SPA loads

**Gate 1:** Auth prompt appears.

```bash
# Without credentials: expect 401
curl -sI http://localhost/chat | head -1
# Expect: HTTP/1.1 401 Unauthorized

# With credentials: expect 200 (proxied to :3000)
curl -sI -u analyst:<password> http://localhost/chat | head -1
# Expect: HTTP/1.1 200 OK
```

**Gate 2:** From the public IP.

```bash
# From an external machine (your laptop, off Tailnet)
curl -sI http://18.224.151.49/chat | head -1
# Expect: HTTP/1.1 401 Unauthorized

curl -sI -u analyst:<password> http://18.224.151.49/chat | head -1
# Expect: HTTP/1.1 200 OK
```

**Gate 3:** Portal stays accessible without auth.

```bash
curl -sI http://18.224.151.49/ | head -1
# Expect: HTTP/1.1 200 OK
curl -sI http://18.224.151.49/docs/ | head -1
# Expect: HTTP/1.1 200 OK
curl -sI http://18.224.151.49/metrics | head -1
# Expect: HTTP/1.1 200 OK
curl -sI http://18.224.151.49/trust | head -1
# Expect: HTTP/1.1 200 OK
```

**Gate 4:** SPA loads in a real browser end-to-end. (Gordon does this part.)

Code hands off to Gordon: "Public chat ready. Try `http://18.224.151.49/chat` in a fresh incognito window. Username `analyst`, password [share via secure channel]."

Gordon:

1. Opens fresh incognito window (no Tailnet, no cached auth)
2. Navigates to `http://18.224.151.49/chat`
3. Expects: Browser shows Basic Auth prompt with realm "Somerville Analytics — Private Beta"
4. Enters `analyst` + password
5. Expects: SPA loads cleanly. No 404s in DevTools Network tab for assets. Workspace appears. Chat surface is accessible.
6. Tests the 2024 question: "How many 311 requests were opened in 2024?" → expect 113,961 with full trust contract.
7. Screenshots: auth prompt, loaded SPA, the 2024 reply with trust contract.

**If Gate 4 fails** (404s on assets, SPA doesn't render, chat doesn't work):

* Check DevTools Network tab for which paths returned 404
* Add nginx location blocks for those paths (probably missed during Step 2 discovery)
* `sudo nginx -t && sudo systemctl reload nginx`
* Retry the browser load

## Step 5 — Update the portal hero

Edit `portal/index.html`. Find the hero section's "Private beta" pill:

```html
<span class="hero-pill">Private beta</span>
```

Replace with:

```html
<a href="/chat" class="hero-pill">Private beta — try the chat →</a>
```

(Or whatever copy lands well. "Try the chat" is direct; alternatives: "Sign in", "Demo access", "Open chat".)

The `.hero-pill` CSS should already style anchors and spans similarly. If hover state isn't there for `<a>`, add it:

```css
a.hero-pill:hover {
    background: var(--green-pale-hover, var(--green-pale));
    text-decoration: none;
}
```

Deploy via the standard pipeline:

```bash
./run.sh  # syncs portal/index.html to /var/www/somerville/ as a final step
```

Verify in browser: `http://18.224.151.49/` shows the pill as a clickable link; clicking goes to `/chat` and prompts for auth.

## Step 6 — AWS Security Group: confirm port 80 only

No SG changes needed. Port 80 is already open publicly. Port 3000 stays Tailnet-only (nginx proxies to `localhost:3000`, which doesn't traverse the SG).

```bash
# Verify SG state — port 3000 should be CLOSED publicly
curl -sI --max-time 5 http://18.224.151.49:3000/ 2>&1 | head -5
# Expect: connection timeout or refused (port 3000 is not publicly reachable)
```

## Step 7 — Add limitations registry entry

Create `docs/limitations/chat-auth-basic-cleartext.md`:

```markdown
---
id: chat-auth-basic-cleartext
title: Public chat behind nginx Basic Auth — credentials in cleartext (HTTP only)
severity: medium
affects: [public-chat-surface, /chat]
since: MVP 1.5
status: accepted-tradeoff
---

The public chat surface at `/chat` is gated by nginx Basic Auth with a
single shared credential. The portal site is HTTP-only (no TLS), so
credentials and traffic travel in cleartext between the visitor's
browser and EC2.

This is an accepted tradeoff for MVP 1.5 controlled-distribution demos:

- The credential is treated as fully disposable — fresh per demo cycle,
  never reused, rotated on any concern.
- The audience is curated; the URL is shared via secure channels only.
- Modern browsers show "Not secure" in the URL bar; visitors are expected
  to understand the private-beta context.
- Anyone with the credential has full agent access (no per-user
  accounts, no audit trail, no granular revocation). Single-credential
  rotation revokes all access at once.

**Mitigation:** rotate the credential whenever a person who had it is
no longer expected to have access; never reuse it elsewhere; treat
chat access as low-stakes demo, not production-grade auth.

**Resolution:** MVP 4 brings Magic Link auth + HTTPS via Oxygen
multi-workspace mode, replacing this layer entirely.
```

Run the limitations index regeneration (step 9/9 of `run.sh`) so the agent picks up the new entry.

## Step 8 — Documentation updates

**ARCHITECTURE.md** — add a subsection under "Deployment Architecture":

```markdown
**Public chat access (MVP 1.5).** The Oxygen SPA at port 3000 is
publicly proxied through nginx at `/chat`, gated by nginx Basic Auth
(`/etc/nginx/.htpasswd`, single shared credential `analyst`). SPA asset
paths required for the SPA to load (`/static`, `/api`, etc. — see
nginx config) are also auth-gated and proxied to `localhost:3000`.

This is deliberately scaffolded — HTTP cleartext, no TLS, single
credential — and gets replaced in MVP 4 by Magic Link auth + HTTPS
via Oxygen multi-workspace mode. See `docs/limitations/chat-auth-basic-cleartext.md`
for the tradeoff statement.
```

**SETUP.md** — add a new section "§13. Public chat access":

```markdown
## §13. Public chat access (MVP 1.5)

The Oxygen SPA is exposed publicly at `http://<public-ip>/chat`, gated
by nginx Basic Auth. To set up on a fresh deployment:

1. Install apache2-utils: `sudo apt-get install apache2-utils`
2. Create the htpasswd file:
   `sudo htpasswd -c /etc/nginx/.htpasswd analyst`
3. Set permissions: `sudo chown root:www-data /etc/nginx/.htpasswd && sudo chmod 640 /etc/nginx/.htpasswd`
4. Add the `/chat` location + SPA asset proxies to `/etc/nginx/sites-available/somerville` (see committed config for the canonical pattern)
5. Reload nginx: `sudo nginx -t && sudo systemctl reload nginx`
6. Test from external IP: `curl -sI http://<public-ip>/chat` → 401; with `-u analyst:<password>` → 200

The htpasswd file is NOT committed to the repo. To rotate the
credential: `sudo htpasswd /etc/nginx/.htpasswd analyst` (without
`-c` — keeps the file, updates the password). Inform anyone who had
the old credential.
```

**LOG.md** — add a row to Active Decisions:

```markdown
| 2026-05-NN | Public chat access added via nginx Basic Auth at /chat
(MVP 1.5) | Same-site experience for demos; HTTP cleartext + single
shared credential explicitly accepted as throwaway scaffolding;
proper auth (Magic Link + HTTPS) lands in MVP 4 |
```

**TASKS.md** — add a new section "MVP 1.5 — Public Chat Access" with all bullets ticked, or fold into a "MVP 1 Follow-ups" section if cleaner. Mark complete.

## Step 9 — Commit

DO NOT commit the htpasswd file or the password. The file is at `/etc/nginx/.htpasswd` on EC2 only.

Add `.htpasswd` to `.gitignore` if not already there (defensive):

```bash
echo ".htpasswd" >> .gitignore
echo "*.htpasswd" >> .gitignore
```

Commit:

```
MVP 1.5: public chat access via nginx Basic Auth at /chat

- nginx /chat location proxies to :3000, gated by Basic Auth
- SPA asset paths (/static, /api, etc.) also auth-gated and proxied
- Portal hero pill becomes clickable link to /chat
- chat-auth-basic-cleartext limitation registry entry documents the
  HTTP-cleartext + single-credential tradeoff
- ARCHITECTURE.md + SETUP.md §13 updated; LOG Active Decisions row added
- Credential stored on EC2 only (/etc/nginx/.htpasswd, not in repo)
- Tradeoff: HTTP, no TLS, single shared credential. Replaced by
  MVP 4's Magic Link auth + HTTPS.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Out of scope (do NOT do in this plan)

* **HTTPS / TLS.** Deferred. If Gordon wants HTTPS later, that's a separate plan involving a domain + Let's Encrypt + nginx TLS config.
* **Per-user accounts.** Single shared credential is the explicit choice.
* **Magic Link auth.** MVP 4 territory.
* **Cloudflare Access or oauth2-proxy.** Out of scope; we chose Basic Auth as the minimal path.
* **Portal copy refresh beyond the hero pill.** The roadmap section, stack table, asset cards stay as-is. (Portal refresh against MVP.md's "opening note" framing is a separate piece of work.)
* **AWS SG changes.** Port 3000 stays closed; port 80 was already open.
* **Rate-limit increase request from Anthropic.** Separate operational task; doesn't block this work.

## If anything fails

**nginx config syntax error.** Don't reload. Fix the config (compare against the backup at `/etc/nginx/sites-available/somerville.bak.pre-chat-auth`), re-test with `nginx -t`, then reload.

**SPA doesn't load through /chat (assets 404).** DevTools Network tab will show which paths failed. Add nginx location blocks for each.

**Auth prompt doesn't appear at all.** Check the `auth_basic_user_file` path matches the htpasswd file location. Check file permissions (`640` with `root:www-data`).

**Port 3000 is now accessible publicly.** Re-check AWS SG. The change shouldn't have affected this, but if it did, restore the SG to "port 3000 closed publicly."

**Rollback.** Restore `/etc/nginx/sites-available/somerville` from the backup at `somerville.bak.pre-chat-auth`. Reload nginx. Portal hero reverts to the static pill (revert `portal/index.html` separately).

## Done done

* `http://18.224.151.49/` serves the portal without auth
* `http://18.224.151.49/chat` returns 401 without credentials
* `http://18.224.151.49/chat` with `analyst:<password>` returns the SPA
* SPA loads cleanly through the proxy (no asset 404s in DevTools)
* 2024 question via SPA chat returns 113,961 with full trust contract
* Other portal routes (`/`, `/docs/`, `/metrics`, `/trust`) unaffected
* Port 3000 remains closed publicly (Tailnet still works for direct access)
* Limitations registry entry committed; ARCHITECTURE.md + SETUP.md updated
* Credential rotation procedure documented in SETUP.md §13
* htpasswd file NOT in repo; password stored in Gordon's password manager

When all green, hand off to Gordon: "MVP 1.5 done. Public chat live at http://18.224.151.49/chat with credential [shared securely]. Anything to demo to in the next two weeks?"
