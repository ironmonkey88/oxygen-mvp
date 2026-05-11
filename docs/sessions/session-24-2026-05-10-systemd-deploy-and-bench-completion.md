---
session: 24
date: 2026-05-10
start_time: 23:20 ET
end_time: 00:15 ET
type: code
plan: plan-7
layers: [infra, agent, docs]
work: [feature, hardening, test, docs]
status: complete
---

## Goal

Resume the overnight brief after the Session 22/23 wake-up. Close the gaps in earlier coverage: re-run the bench questions I skipped (Q2/Q4/Q5), run `./run.sh` end-to-end (re-verify §4.5 row 2 against the new standard), ship Session C D1 (Oxygen systemd deploy + reboot test) and D2 (§4.5 row 1 repo-clonable tick). Determine MVP 1 sign-off status against the new verification-gates standard.

## What shipped

- **Bench re-verification 5/5** via `oxy run`:
  - Q1 (2024 → 113,961, full trust contract) — pre-reboot AND post-reboot
  - Q2 (YTD 2026 → 49,782 with `year(current_date)` resolution + `current-year-partial` limitation)
  - Q3 (top request types → Welcome desk-information / Obtain a parking permit inquiry / Temporary no parking — matches Session 18)
  - Q4 (top 5 blocks → `NA` sentinel 447,428 correctly flagged as space-padded-to-15-chars; both `block-code-padded` and `location-ward-block-only` surfaced)
  - Q5 (survey averages → Accuracy 4.39 / Courtesy 4.67 / Ease 4.63 / Overall 4.28, blended 4.44/5.0; both `2024-survey-columns-sparse` and `survey-columns-on-fact` surfaced)
- `./run.sh` end-to-end clean (re-verifies §4.5 row 2): all 9 steps run, bronze/gold tests exit 0, admin tests exit 0 including `dq_drift_fail_guardrail` PASS at new baseline 1,169,935 rows, final exit 0. /trust regenerated at 36/36 pass.
- **Oxygen systemd unit deployed** ([`/etc/systemd/system/oxy.service`](SETUP.md)) with hardened ordering: `After=network.target docker.service`, `Requires=docker.service`, `EnvironmentFile=/etc/environment`, `Restart=always RestartSec=10`. `systemctl enable` symlinked into `multi-user.target.wants`.
- **Reboot test PASSED.** `sudo reboot` → instance came back, oxy systemd unit active 7s after kernel up, oxy-postgres container recreated bound to persistent `oxy-postgres-data` volume, user record from Session 22 (`local-user@example.com`) survived intact. Curl :3000 → 200 OK. CLI agent regression → 113,961 with full trust contract.
- [STANDARDS.md](STANDARDS.md): §3.2 row 4 (systemd) `[ ]` → `[x]` with full evidence; §6 §3.2 roll-up 4/5 → 5/5; §4.5 row 1 (repo-public) `[ ]` → `[x]` with pre-authorised team-clonable reinterpretation; §6 §4.5 roll-up 2/3 → 3/3; §4.5 row 2 inline evidence appended with Session 24 run.sh timestamp.
- [SETUP.md](SETUP.md) §11: systemd unit updated with `After=docker.service Requires=docker.service RestartSec=10` + a "Why" paragraph explaining the ordering (oxy-postgres container creation requires dockerd up first).
- [TASKS.md](TASKS.md) MVP 1 chat-UI row: evidence appended with full 5/5 bench + volume persistence proof.

## Decisions

- Hardened the systemd unit beyond SETUP.md §11's original recipe — added `After=docker.service` / `Requires=docker.service` / `RestartSec=10`. Reasoning: `oxy start` brings up the postgres container; without explicit dependency on dockerd, post-reboot oxy could race ahead of docker and crash. Verified the hardened shape via reboot test before sign-off. SETUP.md §11 updated to match.
- MVP 1 sign-off close-out **NOT auto-ticked.** Per the brief's gate ("If any box is still open OR any live-functional box can't be re-verified, STOP and surface"), §5.8 row 2 (`/chat`) remains open from Session 23 — Gordon's UI-walkthrough-or-CLI-reinterpretation call. Every other §6 box is `[x]` with re-verified evidence in this session.
- Volume persistence claim **proven empirically**, not assumed. The reboot test specifically checks that the `local-user@example.com` record survives, not just that oxy comes back up. This closes Session 22's open theory: container teardown by `oxy start` kill does NOT lose data (named volume detaches and reattaches cleanly); container recreation on reboot does NOT lose data either; whatever wiped Oxygen state between Session 7 and tonight was a non-routine event, not a structural fragility.

## Validation evidence

```
$ ssh oxygen-mvp 'sudo systemctl status oxy --no-pager | head -5'
● oxy.service - Oxygen server
     Loaded: loaded (/etc/systemd/system/oxy.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-05-11 03:39:22 UTC; 9s ago

$ ssh oxygen-mvp 'sudo systemctl is-enabled oxy'
enabled

$ ssh oxygen-mvp 'curl -sI http://localhost:3000 | head -1'
HTTP/1.1 200 OK

$ ssh oxygen-mvp 'cd ~/oxygen-mvp && oxy run agents/answer_agent.agent.yml \
                  "How many 311 requests were opened in 2024?"' | grep 113961
| 113961         |

$ ssh oxygen-mvp 'docker exec oxy-postgres psql -U postgres -d oxy \
                  -c "select count(*), max(created_at) from users;"'
 count |              max
-------+-------------------------------
     1 | 2026-05-11 00:54:24.007341+00
                                        ← survived reboot (created Session 22)
```

## Issues encountered

### Anthropic 30K/min rate limit on Q5 — first two attempts mid-evening

Q5 (survey averages) is the heaviest question in the bench because the agent runs multiple queries against the survey columns. Two attempts (during the parallel Q4+Q5 batch, and a retry ~75 seconds later) hit the rate limit on the retry phase of the react loop — the first query result came back valid both times, but the trust-contract reply couldn't be assembled. After the reboot validation completed (~10 min later — rate limit fully cleared), Q5 ran clean with full trust contract. Recommendation: don't parallel-batch bench questions; sequential is well within the 30K/min window. This is a runtime constraint, not an agent regression.

## Next action

MVP 1 sign-off is blocked on one Gordon decision: **§5.8 row 2 (`/chat`)** — walk the UI wizard at `oxygen-mvp.taildee698.ts.net:3000` and re-tick on a passing SPA query, OR reinterpret as definitively CLI-only and re-tick with inline note. Every other box is `[x]` with re-verified evidence. When Gordon's call lands, the close-out is the documented one-shot edit in the brief: STANDARDS §6 header note, LOG Current Status flip, CLAUDE.md MVP Sequence flip, TASKS.md sign-off section all-`[x]`.
