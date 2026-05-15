# Dashboard Design Standard

> The template and approach for every Data App (`apps/*.app.yml`) in this
> project. Companion to [BUILD.md](BUILD.md) (construction logic) and
> [STANDARDS.md](STANDARDS.md) (done-done gates). The rat-complaints
> dashboard ([`apps/rat_complaints_by_ward.app.yml`](apps/rat_complaints_by_ward.app.yml))
> is the reference implementation.

---

## 1. Why this exists

MVP 2's analyst-outcome test is *"the analyst describes a dashboard in
chat; Builder Agent assembles it."* For that to produce something
trustworthy and consistent rather than an ad-hoc pile of charts, every
dashboard needs a shared skeleton. This document is that skeleton — the
thing a Builder Agent prompt points at, and the thing a reviewer checks
a finished `.app.yml` against.

A dashboard is not a chart collection. It is an argument: *here is a
situation, here is what matters about it, here is what you should take
away.* The structure below enforces that argument shape.

---

## 2. Every dashboard declares a purpose and an audience

Before any SQL is written, two sentences must be answerable. They go in
the dashboard's `description:` block and inform every downstream choice.

**Purpose** — the one question this dashboard exists to answer. Not a
topic ("rats"), a question ("are rat complaints being handled equitably
across wards, and is the problem growing?"). If the purpose needs an
"and," it is probably two dashboards.

**Audience** — who reads it and what they do next. A city analyst
writing a report needs different framing than a department head deciding
where to send crews. The audience determines tier depth (§3), how much
the takeaway interprets vs. states (§3, Tier 4), and what counts as
"recent" in the situational layer (§4).

Both go in the metadata comment block as well — see §6.

### 2.1 The business-analyst step (process rule)

When Gordon asks for a dashboard, the first move is not to write SQL or
sketch tiers. It is to **work as a business analyst** until the purpose
and audience are genuinely clear — clear enough to state in the two
sentences above without guessing.

This means:

- **Treat a dashboard request as a brief, not a spec.** "Build me a
  potholes dashboard" names a topic, not a purpose. The job is to draw
  out the question behind it.
- **Ask before building.** If purpose or audience is ambiguous, ask
  Gordon directly — what decision does this support, who is the reader,
  what would make it useful versus just present. A short clarifying
  exchange up front is cheaper than a wrong-shaped dashboard.
- **Propose the purpose sentence back.** Once there is enough to work
  with, state the purpose and audience explicitly and get confirmation
  before moving on. "So this is for department heads deciding crew
  allocation, and the question is whether response times are slipping
  in any ward — yes?" That confirmed sentence becomes the dashboard's
  spine.
- **Don't skip the step because the topic seems obvious.** The
  rat-complaints dashboard looked obvious too; the four investigative
  angles only became clear once the equity question was named. Obvious
  topics still have non-obvious purposes.

Only once the purpose and audience are confirmed does tier design (§3)
begin. If a request genuinely is unambiguous — Gordon states the
question and the reader plainly — the analyst step can be a single
confirming sentence rather than a back-and-forth. The rule is that the
clarity exists and is confirmed, not that there is always a long
conversation.

---

## 3. The base: a three-tier structure

Every dashboard has the same four-part base, in this order. The tiers go
from orientation to detail; the takeaway closes the argument.

### Tier 0 — Orientation (a `markdown` block)

One short paragraph: what this dashboard covers, the row count, the
coverage window, the source tables. The reader should know within five
seconds whether they are in the right place. This is also where the
purpose sentence (§2) gets stated plainly.

### Tier 1 — The headline (1–3 `table` or single-number blocks)

The one, two, or three numbers that *are* the situation. For rat
complaints: the total count. For a 311-overview dashboard: total
requests, percent closed, median resolution time. These are the numbers
the analyst will quote first. Keep it to three at most — a headline with
ten numbers has no headline.

### Tier 2 — Major KPIs (2–4 chart blocks)

The handful of breakdowns that explain the headline. Each one should map
to a sub-question a reader would naturally ask after seeing Tier 1.
"Total is 14,036" invites "across how many years?" (trend chart), "spread
how across wards?" (equity chart). Tier 2 charts are the load-bearing
analysis — pick them deliberately, one chart per real question.

### Tier 3 — Descriptive measures (as many blocks as needed)

The finer-grained cuts: distributions, secondary breakdowns, density-
adjusted views, sub-category splits. This is where the rat dashboard's
resolution-speed buckets and complaints-per-sq-km live. Tier 3 is for the
analyst who is now interested and wants to go deeper; it should not
compete with Tier 2 for attention. If a Tier 3 measure turns out to be
something every reader needs, promote it to Tier 2.

### Tier 4 — Takeaway (a closing `markdown` block)

Two to four sentences describing the overall situation in plain
language. Not a chart caption — a synthesis. *"Rat complaints have grown
roughly 3x since 2015. Ward 3 carries the highest density. Most closed
complaints resolve within a week, but a long tail of structural cases
sits open for years."* The takeaway is what the audience remembers; it
is the only tier that interprets rather than reports, and how far it
goes in interpreting depends on the audience declared in §2.

The existing trust footer (citations + known limitations) sits *after*
the takeaway. Tier 4 is the analytical close; the trust footer is the
accountability close. Both are mandatory — see §5.

---

## 4. Above the base: the recent-situation layer

The base answers "what is the overall situation." For most operational
topics — rats, potholes, crime — the reader also needs "what is
happening *now*." That is a distinct layer, and it sits above the base
(rendered first, since it is what an operational reader checks first).

### When to include it

Include the recent-situation layer when the topic is operational and
ongoing — anything where a department is actively responding and a
reader might act on a recent trend. Skip it for purely historical or
reference dashboards where "recent" is not a meaningful frame.

### What it contains

A compact version of the tier structure, windowed to a recent period:

- **Window.** Default to 90 days. The audience (§2) can justify a
  different window — 30 days for a fast-moving operational view, a full
  year for something seasonal. State the window explicitly in the
  block's title or intro; never leave the reader guessing what "recent"
  means.
- **Recent headline.** Volume in the window, and how it compares to the
  prior equivalent window (up 12%, down 4%). The comparison is the
  point — a bare recent number has no signal without it.
- **Recent trend.** A chart showing the shape of the window — weekly or
  daily buckets depending on volume. Enough to see whether the recent
  period is climbing, flat, or falling.
- **Emerging problems.** The honest "what might we be seeing" cut: which
  category, ward, or status is overrepresented in the recent window
  relative to the long-run base. This is the layer earning its place —
  it is the part that tells an operational reader where to look.

Keep this layer tight. It is a focused situational brief, not a second
full dashboard. If it grows past four or five blocks, the topic probably
deserves its own dedicated recent-focused dashboard.

---

## 5. Trust signals are mandatory, not optional

Every dashboard carries the same trust contract chat carries. This is a
hard gate, not a nice-to-have — the Plan 11 retro flagged that Builder
Agent does *not* add these unprompted, so the prompt must ask for them
explicitly and the reviewer must check for them.

Three signals, all three required:

1. **`last_refreshed`** — a task reading `MAX(run_completed_at)` from
   `main_admin.fct_pipeline_run_raw` where `run_status IN ('success',
   'partial')`, surfaced as a small table near the top.
2. **Citations** — a `markdown` block in the trust footer naming every
   source table and what each one contributed.
3. **Known limitations** — a `markdown` block in the trust footer
   listing every limitations-registry entry that applies to the data on
   this dashboard, by ID, with a one-line plain-language consequence and
   a link to `/trust`. If a chart excludes rows (NULL ward, open-only,
   partial year), the exclusion is named here.

A dashboard that renders charts but omits any of the three is not done.

---

## 6. The file contract

Two structural requirements every `.app.yml` must satisfy, both already
established in the project:

**Metadata comment block.** The `# === DASHBOARD METADATA === ... # ===
END DASHBOARD METADATA ===` block at the top of the file (the Plan 17 /
Session 45 contract). `scripts/generate_dashboards_listing.py` parses it
to build the `/dashboards` listing. Purpose and audience (§2) should be
reflected in `short_desc`. Required keys: `title`, `topic`, `short_desc`,
`row_caption`, `coverage`, `source_tables`, `limitations`,
`trust_signals`.

**ASCII-only.** No non-ASCII characters anywhere in the file — em-dashes,
en-dashes, arrows, curly quotes all break the SPA's base64 route decoder
(the `spa-render-atob-on-utf8-markdown` finding). Use `--`, `-`, `+`,
straight quotes. The pre-commit grep guard is
`grep -nP "[\x80-\xff]" apps/*.app.yml`.

---

## 7. The structure as a checklist

For a Builder Agent prompt, or a reviewer checking a finished file:

- [ ] Business-analyst step done — purpose and audience drawn out and
      confirmed with Gordon before tier design began (§2.1)
- [ ] Purpose stated as a single question; audience named — both in
      `description:` and reflected in `short_desc`
- [ ] Tier 0 — orientation markdown block (coverage, row count, sources)
- [ ] Tier 1 — headline: 1-3 numbers that are the situation
- [ ] Tier 2 — major KPIs: 2-4 charts, each answering one real
      sub-question
- [ ] Tier 3 — descriptive measures: finer cuts, subordinate to Tier 2
- [ ] Tier 4 — takeaway: 2-4 sentences synthesizing the overall
      situation
- [ ] Recent-situation layer (if operational): windowed headline +
      comparison, recent trend, emerging-problems cut; window stated
      explicitly
- [ ] Trust signals: `last_refreshed` task, citations block, known-
      limitations block — all three present
- [ ] Metadata comment block complete and accurate
- [ ] ASCII-only; grep guard clean
- [ ] `oxy validate` green

---

## 8. What this standard does NOT cover

- **Chart-type choice.** Bar vs. line vs. table is left to whoever
  builds the dashboard — the standard governs structure and argument,
  not visual encoding. Oxygen's `.app.yml` `display` schema is the
  reference for what is available.
- **Builder Agent prompt wording.** A separate prompt-template artifact,
  if/when one is written, would translate this standard into the
  opening-prompt shape Builder consumes. This document is the spec that
  prompt would point at.
- **Semantic-layer additions.** Whether a dashboard's measures should be
  inline SQL or promoted into `semantics/views/*.view.yml` is a
  case-by-case call, not a structural rule.
- **The `/dashboards` listing.** Covered by the Plan 17 generator and
  the metadata-block contract; this standard only requires that the
  metadata block be present and accurate.
