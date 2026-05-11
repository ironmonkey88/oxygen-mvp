# Plan: Switch Answer Agent Model from Sonnet 4.6 to Opus 4.7

**For:** Code (next session, after MVP 1 sign-off)
**Status:** Ready to execute
**Estimated effort:** 30–60 minutes
**Prerequisite:** MVP 1 signed off; `oxy start --local` running; CLI bench + SPA bench both healthy on `claude-sonnet-4-6`

> **Hand-off note from Code, 2026-05-11:** Saved verbatim from Gordon's brief. MVP 1 was signed off in commit `a6038b6` (Session 25) — prerequisite is met. Execution awaits Gordon's direction on timing (now vs. next session vs. alongside MVP 1.5 public-chat-Basic-Auth work, which has its own plan at [`mvp-1.5-public-chat-via-nginx-basic-auth.md`](mvp-1.5-public-chat-via-nginx-basic-auth.md)).
>
> Relevant context: the `agent-rate-limit-multi-turn-spa` limitation entry (added 2026-05-11) documents the rate-limit issue this plan resolves. When this plan executes, that entry's status field can be updated to reflect mitigation by the Opus migration.

---

## Why this change

The Answer Agent currently runs on `claude-sonnet-4-6`. The Anthropic API account is Tier 1 with a 30,000 input-tokens/minute rate limit on Sonnet. SPA multi-turn conversations accumulate enough context (system prompt + semantic layer + limitations index + conversation history + result tables) to hit that cap within 3–4 turns of dense queries. Gordon hit it during initial SPA testing on a chart follow-up.

Tier upgrade options on the Anthropic console don't expose a self-serve "request increase" flow — only "Contact sales" — and current spend ($5.52 of $100/month) is too low to trigger auto-upgrade thresholds.

`claude-opus-4-7` has a 500K input-tokens/minute rate limit on Tier 1 — roughly 16× Sonnet's headroom. Quality is better than Sonnet 4.6 on instruction-following, multi-turn reasoning, and the kinds of context-heavy tasks the Answer Agent does. Cost per token is higher (~5×) but at current usage that's still trivial — projected to $25–30/month, well inside the $100 budget.

The Oxygen SPA's onboarding wizard defaulted to Opus 4.7 — this isn't coincidence. Anthropic ships rate limits that favor Opus at Tier 1 because per-token cost discourages abuse. Switching `config.yml` to Opus also aligns the CLI and SPA on a single model (eliminates the split the wizard would have introduced).

The only real tradeoff is latency — Opus typically streams at 30–50 tokens/sec vs Sonnet's 60–80. For analyst chat where reasoning quality matters more than raw speed, this is acceptable.

## Pre-flight

```bash
ssh oxygen-mvp

# Confirm current state — Sonnet 4.6 in config
grep -A 3 "model_ref" config.yml
# Expect: model_ref: claude-sonnet-4-6 (or claude-sonnet-4-6-20XXXXXX)

# Confirm Oxygen is running
sudo systemctl is-active oxy
# Expect: active

# Confirm SPA is reachable
curl -sI http://localhost:3000 | head -1
# Expect: HTTP/1.1 200 OK

# Capture baseline CLI bench output for comparison
oxy run agents/answer_agent.agent.yml "How many 311 requests were opened in 2024?"
# Expect: 113,961 with full trust contract
# Capture the full output for diff against post-switch
```

Gate: all pass. If anything fails, stop and diagnose before changing models.

## Step 1 — Back up config

```bash
cp config.yml config.yml.bak.pre-opus
```

## Step 2 — Update config.yml

Edit `config.yml`. Find the model definition. It should look something like:

```yaml
models:
  - name: anthropic-claude
    model_ref: claude-sonnet-4-6
    key_var: ANTHROPIC_API_KEY
```

(The actual `name` may differ — could be `default`, `claude`, or whatever the project named it. Use the existing name.)

Change `model_ref` to:

```yaml
model_ref: claude-opus-4-7
```

**Important:** check whether `agents/answer_agent.agent.yml` overrides the model anywhere. Grep for `model_ref` and `model:` in the agent file:

```bash
grep -E "model_ref|^model:" agents/answer_agent.agent.yml
```

If the agent specifies its own model, update it there too. If not, the `config.yml` change is enough.

## Step 3 — Verify config syntax

```bash
oxy validate
# Expect: 6/6 configs valid (or similar — clean validation pass)
```

If validation fails, restore from backup:

```bash
cp config.yml.bak.pre-opus config.yml
```

And diagnose before proceeding.

## Step 4 — Restart Oxygen

```bash
sudo systemctl restart oxy

# Wait for it to come up
sleep 5
sudo systemctl is-active oxy
# Expect: active

curl -sI http://localhost:3000 | head -1
# Expect: HTTP/1.1 200 OK

# Watch logs briefly for any model-loading errors
sudo journalctl -u oxy --since "1 minute ago" | tail -30
# Look for: clean startup, no API key errors, no model-not-found errors
```

Gate: Oxygen reloads cleanly with the new model.

## Step 5 — CLI bench re-verification

Run the 5-question bench. Each question should return correct, trust-contract-compliant results. Compare against the Sonnet baseline captured in pre-flight.

**Q1 — Counts.**

```bash
oxy run agents/answer_agent.agent.yml "How many 311 requests were opened in 2024?"
```

Expect: 113,961. Trust contract: SQL block, row count ("Returned 1 row."), citations, no false-positive limitations.

**Q2 — Year-aware counts.**

```bash
oxy run agents/answer_agent.agent.yml "How many 311 requests have been opened year-to-date?"
```

Expect: ~49,782 (YTD 2026 figure; may differ slightly on a fresh data refresh). Trust contract intact. Watch for: Opus should resolve "current year" via SQL (`year(current_date)`), not hallucinate from training data. Sonnet had to be prompted explicitly; Opus may handle this more naturally.

**Q3 — Categorical aggregation.**

```bash
oxy run agents/answer_agent.agent.yml "What are the most common request types?"
```

Expect top types: Welcome desk-information, Obtain a parking permit inquiry, Temporary no parking sign posting (or close — depends on current top-3 in fresh data). Trust contract intact.

**Q4 — Limitation surfacing (block_code NA).**

```bash
oxy run agents/answer_agent.agent.yml "What are the top 5 blocks by request volume?"
```

Expect: `NA` (15-char space-padded) at top with ~447,428 requests. Trust contract intact. **Critical:** limitations `block-code-padded` AND `location-ward-block-only` should both surface in the reply. If either is missing on Opus, that's a real finding — investigate before proceeding.

**Q5 — Limitation surfacing (sparse survey columns).**

```bash
oxy run agents/answer_agent.agent.yml "What's the average satisfaction across surveys?"
```

Expect: ~4.44/5 blended. Trust contract intact. **Critical:** limitations `2024-survey-columns-sparse` AND `survey-columns-on-fact` should both surface. Same investigation discipline if missing.

Gate: all 5 pass with trust contract intact.

**If any fail:**

* Different answer: is the underlying data different (data refresh occurred)? Confirm via DuckDB before blaming the model.
* Trust contract missing/incomplete: Opus may need a small prompt adjustment. Capture the exact failure mode and stop.
* Limitation surfacing missing on Q4/Q5: this is the most likely Opus-specific issue — Opus may handle the limitations index differently than Sonnet. Diff the reply prose against Sonnet baseline and decide whether the change is acceptable or requires prompt tuning.

If everything passes, proceed.

## Step 6 — SPA bench re-verification

Gordon does this. Code: hand off with: "Opus 4.7 active. CLI bench 5/5 passed. Try Q1-Q5 in the SPA at `http://oxygen-mvp.taildee698.ts.net:3000` (or via the Basic Auth route if MVP 1.5 has landed)."

Gordon:

1. Open the SPA (Tailnet or `/chat` route)
2. Start a fresh chat thread (don't carry the previous Sonnet conversation)
3. Ask each of Q1-Q5 in sequence in the same thread (this tests both trust contract and multi-turn context handling under Opus's larger rate limit)
4. Confirm:
   * All 5 answers correct (113,961 / ~49,782 / top types / NA at top / ~4.44/5)
   * Trust contract present on each (SQL, row count, citations, limitations where applicable)
   * No rate-limit errors — the whole thread should complete cleanly without ApiError red banners. This is the critical test; this is what the model switch is for.
5. Screenshot the thread for evidence

Gate: All 5 pass in a single thread without rate-limit interruption.

**If a rate limit appears anyway:** investigate. 500K tokens/min should be well above what 5 turns would consume. If it fires, something else is wrong (cache invalidation, prompt bloat, etc.) — capture and diagnose.

## Step 7 — Performance check

This is informational, not a gate. Note the latency difference Gordon experiences in the SPA:

* Sonnet 4.6 streams at roughly 60–80 tokens/sec — most answers complete in 5–15 seconds
* Opus 4.7 streams at roughly 30–50 tokens/sec — most answers complete in 10–25 seconds

For a typical bench answer (~200-400 output tokens), expect 5-10 seconds of additional latency on Opus. If it feels noticeably worse than acceptable, that's worth documenting as a tradeoff but not blocking.

## Step 8 — Update documentation

**config.yml.example**

If a sanitized example config exists in the repo, update it to show `claude-opus-4-7` as the default.

**LOG.md**

Add an Active Decisions row:

```
| 2026-05-NN | Switched Answer Agent from claude-sonnet-4-6 to
claude-opus-4-7 | Sonnet's 30K input-tokens/min Tier 1 rate limit
was being hit on SPA multi-turn conversations; Opus has 500K limit
on same tier (16x headroom). Quality improves; latency ~50% slower
per token; cost ~5x per token (still trivial at current spend).
Bench 5/5 re-verified on Opus across CLI and SPA. |
```

**ARCHITECTURE.md**

In the "Oxygen Component Reference" section, update the Answer Agent subsection if it names the model:

```
**Model:** Claude Opus 4.7 (claude-opus-4-7) via Anthropic API
(ANTHROPIC_API_KEY). Selected for 500K input-tokens/minute Tier 1
rate limit — Sonnet's 30K limit was insufficient for SPA multi-turn
conversations. Opus 4.7 also delivers stronger instruction-following
on the trust contract.
```

**Limitations registry**

If a `agent-rate-limit-multi-turn-context` entry was created earlier (when Gordon first hit the limit), update its status to `mitigated-by-opus-4-7-migration` or `resolved`. If no entry exists, no need to create one retroactively — the migration is documented in LOG.md.

**STANDARDS.md**

If §4.1 or §4.5 names the specific model in any "extreme trustability" criteria, update to `claude-opus-4-7`. Most likely the standards reference "the configured model" or similar — verify and update only where the model is specifically named.

**TASKS.md**

Add a brief row to whatever's tracking MVP 1.5 work:

```
- [x] Switch Answer Agent from Sonnet 4.6 to Opus 4.7
  - config.yml model_ref updated; bench 5/5 re-verified CLI + SPA;
  - rate limit headroom 30K → 500K tokens/min
```

## Step 9 — Reboot test (light)

To confirm the change persists across an oxy restart (not a full reboot — that's overkill for a config change):

```bash
sudo systemctl restart oxy
sleep 5
oxy run agents/answer_agent.agent.yml "How many 311 requests were opened in 2024?"
# Expect: 113,961 with trust contract on Opus
```

Gate: Q1 passes after restart.

## Step 10 — Commit

```
MVP 1.5: switch Answer Agent from Sonnet 4.6 to Opus 4.7

- config.yml model_ref: claude-sonnet-4-6 → claude-opus-4-7
- Anthropic Tier 1 rate limit on Sonnet (30K input tokens/min) was
  hit on SPA multi-turn conversations
- Opus 4.7 has 500K input tokens/min on Tier 1 (16x headroom)
- Quality improves on instruction-following + multi-turn reasoning
- Latency ~50% slower per token; cost ~5x per token (trivial at
  current spend — projected $25-30/month vs $100 budget)
- Bench 5/5 re-verified on Opus via both CLI and SPA
- No rate-limit interruptions in 5-question SPA thread
- ARCHITECTURE.md + LOG.md updated; config.yml.example synced

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## If anything fails: rollback

```bash
cp config.yml.bak.pre-opus config.yml
sudo systemctl restart oxy
sleep 5
oxy run agents/answer_agent.agent.yml "How many 311 requests were opened in 2024?"
# Expect: 113,961 (back on Sonnet)
```

Then regroup with Gordon on what failed.

## Out of scope

* Routing Agent / multi-model dispatch (e.g., Haiku for simple questions, Opus for complex). MVP 4 territory.
* Prompt re-tuning for Opus specifics. Only touch the prompt if bench reveals a real degradation.
* Tier upgrade request. Not needed; Opus solves the problem within Tier 1.
* Rate-limit registry entry update beyond status flip. Quick mark-as-resolved is enough; full retrospective writeup not needed.
* Performance benchmarking. Note the latency difference informally; no formal SLA work.

## Done done

* `config.yml` references `claude-opus-4-7`
* CLI bench Q1-Q5 all pass with trust contract intact
* SPA bench Q1-Q5 all pass in a single thread, no rate-limit errors
* Restart-survives test passes
* ARCHITECTURE.md, LOG.md, config.yml.example updated
* Single commit on main
* Gordon confirms the SPA chat experience is noticeably more reliable on multi-turn flows
