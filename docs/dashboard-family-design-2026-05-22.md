# Verdict-First Trend Dashboard Family — Design Document

**Status:** design phase (no implementation yet)
**Date:** 2026-05-22
**Author:** Chat session with Gordon
**Audience for the dashboards in this family:** residents of Somerville
**Companion docs:** [DASHBOARDS.md](../DASHBOARDS.md), [PHILOSOPHY.md](../PHILOSOPHY.md), [BUILD.md](../BUILD.md), [docs/dba-dashboard-design-2026-05-17.md](dba-dashboard-design-2026-05-17.md)

---

## 0. What this document is

A design specification for a family of three resident-facing dashboards
and one collection-of-dashboards page that share a single underlying
template:

- **Rat DB v2** — "Is the rat problem near me getting better or worse?"
- **Crime 360** — "What kinds of crime happen where I live, and how has
  that changed?"
- **Somerville from Top to Bottom** — "How is Somerville changing over
  time across the dimensions that matter to residents?" (a collection
  of dimension-cards, each backed by a template-conforming dashboard)

All three were specified through an extended business-analyst step (per
DASHBOARDS.md §2.1) that resolved purpose and audience before any
visual design began. The four cross-cutting answers from that step are
the foundation of the template:

1. Every dashboard answers a **change-over-time** question
2. Every dashboard is **resident-facing**, not operator-facing
3. Every dashboard answers **one focused question well** (not
   comprehensive at the cost of focus)
4. Every dashboard **says it directly** — the primary output is a
   sentence, not a chart, with the chart as substantiation

These four together produce a dashboard idiom this project does not yet
have, and one that DASHBOARDS.md does not yet describe. Section 9 of
this document proposes the standards-doc update needed to accommodate
the family.

---

## 1. Purpose and audience per dashboard (per DASHBOARDS.md §2.1)

The business-analyst step produced three sentences. Each becomes the
spine of one dashboard.

**Rat DB v2.** Purpose: "Is the rat problem near me getting better or
worse?" Audience: Somerville residents wondering whether their block
(or neighborhood, or ward) is improving or worsening over time. They
arrive with anxiety, curiosity, or comparative interest ("is my area
unusually bad?"); they leave with a calibrated answer.

**Crime 360.** Purpose: "What kinds of crime happen where I live, and
how has that changed?" Audience: Somerville residents trying to
understand the actual crime picture in their area, with the variation
across crime types preserved (because "crime is up" without
type-breakdown is almost always misleading).

**Somerville from Top to Bottom.** Purpose: "How is Somerville changing
over time across the dimensions that matter to residents?" Audience:
residents wanting a synthetic read on the city's trajectory across the
dimensions that shape daily life. Not a comprehensive census; a curated
multi-dimensional verdict.

Each dashboard's purpose is a *direct question with a direct expected
answer*. The dashboard's job is to produce that answer, not to display
relevant numbers and leave synthesis to the reader.

---

## 2. The four design commitments

These were settled during the business-analyst step and bind every
dashboard in the family.

### 2.1 Verdict-first

The primary output of each dashboard is a sentence. "Rats in Ward 3 are
GETTING WORSE." "Property crime in Davis Square is STABLE." The charts
exist to substantiate the sentence; the sentence is not a caption for
the chart.

This inverts the conventional civic-dashboard ordering, which shows
data first and leaves synthesis to the reader. The motivation is the
honest-reporting principle from PHILOSOPHY.md §6.3 applied to user
experience: residents arrive with a question; the dashboard's first
duty is to attempt an answer.

### 2.2 Four-state verdict vocabulary

Every verdict resolves to one of four states:

- **better** — the trend is improving by the operative significance rule
- **worse** — the trend is degrading by the operative significance rule
- **stable** — the trend is not changing meaningfully
- **unclear** — the data does not support a meaningful verdict (small
  n, regime change, contradictory signals, ambiguous category boundary)

"Unclear" is first-class. It is not a failure mode or a fallback. It
is the right answer when it is the right answer. Saying "unclear"
honestly is more valuable than forcing a verdict the data does not
support.

### 2.3 Universal time anchor: trailing 12 months vs 5-year average

The comparison frame is the same for every dashboard:

- **Current window:** the trailing 12 months
- **Baseline:** the average of the prior 5 years' same-period values
  (or 5-year mean for non-seasonal metrics)

This is conservative, smooths noisy years (pandemic disruptions,
weather-driven anomalies, regime changes), and is explicable in one
sentence: *"The last year, compared to how the last five years usually
look."*

Per-metric overrides are allowed in the Methodology Note (§3.4) where a
metric's character demands it (e.g., highly seasonal metrics may
explicitly compare same-month windows), but the default anchor is the
shared frame.

### 2.4 Mixed significance approach

Whether a change is "meaningful" is computed using either:

- **Statistical test** where n is large enough to support it (Mann-Kendall
  trend test, Welch's t-test against the baseline, or equivalent —
  selection per the operative metric)
- **Heuristic threshold** where n is too small for statistical tests
  (e.g., percentage-change threshold of ±15% with the threshold itself
  disclosed)

Which approach was used for any given verdict is **disclosed in the
methodology note**. Residents can calibrate trust accordingly. A
verdict that says "this is statistically significant at p < 0.05" is
making a different claim than one that says "this exceeds our 15%
heuristic threshold."

This is the honest-reporting principle applied at the analytical
layer: the dashboard is making editorial calls; the calls are visible.

---

## 3. The template — four-block vertical stack

Every dashboard in this family lays out as four vertical blocks, in
order. Layout is fixed; content varies per dashboard.

### 3.1 Header

A persistent header containing:

- Dashboard name and one-line purpose statement
- **Locality selector** — defaults to city-wide; prominent "pick your
  ward" affordance immediately visible. Additional granularities
  (neighborhood, block) appear here per dashboard's locality model.
- **Time anchor display** — explicit text noting the comparison frame
  in use: "Comparing June 2025 – May 2026 to 2021–2025 average."
- Standard portal chrome (logo link, navigation, footer continues
  per portal pattern)

### 3.2 Verdict

A single visual block containing:

- An **icon** representing the verdict state (see §4 on color)
- A **verdict sentence**, in the form: *"[Metric] in [Locality] are
  [VERDICT-STATE]."* Optionally followed by 1-2 sentences of plain
  context (*"Up substantially over the last 12 months compared to the
  5-year average."*)

The verdict is the largest single element on the page. Reading the
verdict block should take fewer than five seconds.

The verdict prose **does not carry methodology nuance**. It states the
verdict cleanly. The "why" lives in §3.4.

### 3.3 Evidence

Two charts:

- **Primary trend chart.** The 12-month window's monthly counts as a
  line; the 5-year baseline as a shaded band behind it. The visual
  encoding of the verdict — if the line sits clearly above or below
  the band, the verdict is mechanically justified.
- **Comparison chart.** "Your area vs city average" when a ward is
  selected; "all wards ranked" when city-wide is selected. The two
  forms answer slightly different sub-questions ("is my area unusual?"
  vs "where is this concentrated?") and the swap is automatic from
  the locality selector.

No more, no fewer. Two charts is the focused-question commitment
expressed as visual restraint.

### 3.4 Methodology note (HOW WE DECIDED)

A small but persistent prose block, 2-4 sentences, containing:

- Which significance approach was applied (statistical test name and
  p-value, or heuristic threshold value)
- The time windows used (explicit dates)
- For an "unclear" verdict: a one-line reason ("Marked 'unclear'
  because n=14 in this period, below our 30-count threshold for the
  trend test")
- A link to a full methodology page (`/dashboards/methodology` or
  equivalent) carrying the family-level explanation

The methodology note is small, readable in 10 seconds, and the only
place the trust nuance lives. The verdict sentence stays clean
because the methodology note carries the work.

---

## 4. Color and iconography

The verdict icon uses one of two color systems depending on the metric.

### 4.1 Alarm colors (default)

For metrics where "up" or "down" has clear emotional valence and
residents bring conventional reading habits:

- **Better** — green ↓ (or ↑ if "more" is good, e.g., parks volunteers)
- **Worse** — red ↑ (or ↓ if "less" is bad)
- **Stable** — yellow →
- **Unclear** — gray ?

The alarm colors are appropriate when the "direction is bad" reading
is uncontroversial. Rat complaints up: bad. Housing affordability
down: bad. 311 response times up: bad. These metrics use alarm colors.

### 4.2 Neutral colors (Crime specifically)

Crime carries a uniquely loaded reading. Red ↑ for "violent crime up
12%" is alarm-coded even when the increase is small and the verdict is
calibrated. The dashboard ends up communicating "panic" when its
analytical verdict is "modest increase, within historical range."

Crime 360 uses a **neutral palette**:

- **Better** — navy ↓
- **Worse** — orange ↑
- **Stable** — gray →
- **Unclear** — light gray ?

The verdict sentence still says "GETTING WORSE" when that is the
calibrated answer; the visual does not amplify it into alarm. This is
the editorial-voice commitment from §1 applied at the visual layer.

### 4.3 Per-metric overrides (Top to Bottom)

Some Top-to-Bottom dimensions have ambiguous valence (e.g., "population
growth" — good or bad depending on resident perspective). Those
dimensions default to **neutral colors** unless the specific dimension
has a clear consensus reading.

---

## 5. Locality

### 5.1 Default

Every dashboard opens on **city-wide** view with a prominent "pick your
ward" affordance in the header. The verdict on first load reads "Rats
in Somerville (citywide) are..."

City-wide-first was chosen over auto-detect (privacy concerns, false
positives) and over force-pick (adds friction before residents see
their first answer).

### 5.2 Granularity per dashboard

- **Rat DB v2:** Ward + adaptive sub-ward (see §5.3). Block-level is
  the aspiration; the adaptive-locality mechanism handles the noise
  problem.
- **Crime 360:** Neighborhood (Davis, Union, Magoun, Spring Hill,
  etc.) where the data supports the geographic mapping; ward as
  fallback. Block-level is **out of scope** for crime — small-area
  crime counts are too noisy and the alarm potential of "one violent
  crime on your block" is too high for a calibrated dashboard to
  amplify.
- **Top to Bottom:** Ward primary, neighborhood secondary where data
  supports.

### 5.3 Adaptive locality (Rat DB v2)

When a resident selects a sub-ward locality (block, or a block-plus-
adjacent-blocks aggregation) and the data does not support a meaningful
verdict at that granularity, the dashboard **auto-zooms-out** to the
next-larger scope that does:

1. Resident selects "my block"
2. n at block granularity (last 12 months) is below the trend-test
   threshold
3. Dashboard expands to "your block + 4 adjacent blocks"
4. If still insufficient, expands to ward
5. If ward still insufficient, falls back to city
6. The dashboard tells the resident exactly what is shown: *"Your block
   had 6 complaints last year, not enough to call a trend. Showing
   your block plus 4 neighbors (n=42 over 12 months): GETTING WORSE."*

Adaptive locality is the design's most novel mechanism. It honors the
"data supports the verdict" rule while still giving residents a
verdict instead of an unhelpful "unclear" at every block.

---

## 6. Crime 360 — the editorial-summary variant

Crime 360 fits the template but with one specific deviation: it does
not use the template's algorithmic single verdict.

### 6.1 The aggregation problem

Crime is multi-typed. A simple sum produces an "overall" verdict
dominated by the most-common categories (typically quality-of-life
calls), masking real movement in serious categories. A severity-
weighted sum encodes a weighting decision the dashboard would have to
own and defend. A "worst-of" rule produces "worse" verdicts every time
any sub-category trends up.

The design's choice: **no algorithmic single verdict.** The Verdict
block carries a **prose synthesis** of the per-type verdicts.

### 6.2 The prose synthesis pattern

A 2-3 sentence summary computed by template logic from the underlying
per-type verdicts:

> *"Crime in Somerville is mixed. Property crime is GETTING WORSE
> (statistically significant). Violent crime is STABLE. Quality-of-life
> calls are GETTING BETTER. Vehicle crime is UNCLEAR."*

The synthesis is mechanical but the language is honest about
heterogeneity. There is no single "Crime: WORSE" verdict because no
single verdict would tell the truth.

### 6.3 Per-type sub-verdicts

Below the prose synthesis, each crime type gets a compact sub-verdict
block: type name, state icon, 1-line context, link to a per-type
expanded view. The per-type expanded view is itself a verdict-first
dashboard conforming to the template (verdict → evidence →
methodology), parameterized to that type.

### 6.4 Categorization is a flagged prerequisite

Crime 360 cannot be implemented until a categorization decision is
made: which 5-8 buckets divide the data in a way that (a) reflects
what residents care about, (b) groups the long tail of incident types
sensibly, (c) is defensible as a curation choice. This is a **bounded
design exercise** — examining the actual incident-type values in the
Somerville crime data, proposing 5-8 categories, documenting the
boundary decisions. It happens before the Crime 360 implementation
prompt, not during.

---

## 7. Top to Bottom — the grid-of-cards page

Top to Bottom is structurally different from Rat v2 and Crime 360. It
is not a single dashboard; it is a **grid of verdict cards**, each
backed by a template-conforming sub-dashboard.

### 7.1 Layout

The page top carries a **meta-verdict** prose block:

> *"Somerville's trajectory: 3 dimensions improving, 2 getting worse,
> 1 unclear, 1 stable. Housing affordability continues to worsen;
> the Happiness Survey shows improving social connection. See each
> dimension below for the full picture."*

Below the meta-verdict, a grid of **verdict cards** — one per dimension.
Each card is a small box containing:

- Dimension name
- Verdict state icon + verdict sentence (1 line, condensed)
- A tiny chart (sparkline, scaled to fit)
- "Open full →" affordance opening the full template dashboard for
  that dimension

Cards are sized for at-a-glance comprehension. A resident should be
able to scan the grid and read every verdict in under 10 seconds.

### 7.2 The seven dimensions

Per the business-analyst step, the dimensions are:

1. **Housing affordability** — median rent, sale prices, rent-burden
   share. **Data dependency:** not yet in the warehouse. Foundational
   data ingestion is a prerequisite (see §8).
2. **Happiness Survey indicators** — wellbeing, social connection,
   civic satisfaction. **Data dependency:** already in warehouse
   (per Plan 24's expected silver-gold curation; see Open Questions §12).
3. **Population / demographics** — Census + ACS data; growth, density,
   age distribution, demographic shifts. **Data dependency:** ACS
   ingestion required.
4. **Development permits** — building activity volume and type;
   leading indicator of neighborhood change. **Data dependency:**
   already in warehouse.
5. **311 volume** — total 311 calls, engagement signal. **Data
   dependency:** already in warehouse.
6. **Crime** — appears as a card linking into Crime 360 (see §7.3).
   **Data dependency:** crime data in warehouse; Crime 360 dashboard
   itself is a prerequisite.
7. **Environmental** — tree canopy, air quality, urban heat. **Data
   dependency:** sourcing uncertain; likely Somerville GIS + EPA
   AirNow + heat-mapping. Some new ingestion needed.

Five of seven have data dependencies that block immediate
implementation. This is real work, not just a documentation note.

### 7.3 Crime as a linking card

The Crime card in Top to Bottom is **visually distinct from the other
cards**. Other cards' "Open full →" affordance opens an in-family
template dashboard for that dimension. The Crime card's affordance
opens Crime 360, which is its own surface with its own design
(neutral colors, per-type sub-verdicts).

The visual distinction tells the resident "this card is a doorway to
a different kind of surface" before they click. Specifics in the
implementation prompt (different border, "→ Crime 360" label, etc.);
the design principle is *the navigation behavior is signaled
visually before the click happens.*

### 7.4 The meta-verdict prose

The page-top meta-verdict is computed from the underlying card
verdicts but allows editorial framing of the synthesis. The
mechanical version ("3 improving, 2 worse, 1 unclear, 1 stable") is
present; a 1-2 sentence prose follow-up calls out the highest-
signal moves.

This is the only place in the family where editorial framing layers on
top of an algorithmic summary. It is acceptable here because the
meta-verdict's whole job *is* synthesis across dimensions, and
synthesis is editorial by nature.

---

## 8. What this design deliberately omits

- **No maps as primary view.** Maps may appear in per-dashboard
  detail surfaces, but the primary visual idiom of the family is the
  trend chart. Maps lead residents toward "which neighborhoods" when
  the question is "how is this changing" — the wrong primary frame.
- **No real-time data.** Daily refresh is acceptable; sub-hourly
  refresh is out of scope for v1. The trailing-12-month frame
  smooths short-term noise; intra-day variation is below the
  dashboard's resolution.
- **No personalization beyond locality.** No accounts, no
  preferences, no saved views. The dashboard is stateless from
  visit to visit; locality is selected per session.
- **No social features.** No commenting, sharing analytics,
  community discussion. The dashboard is reference material.
- **No drill-down to individual incidents.** Crime 360 categorizes
  and trends; it does not show a police blotter. Rat v2 trends; it
  does not list addresses.
- **No predictive forecasting.** The dashboard shows past and
  present; it does not extrapolate forward. "Where this is heading"
  is the resident's inference, not the dashboard's claim.
- **No SLO / SLA framing.** Like the DBA dashboard (per its design
  doc §8), this family does not claim service levels.

---

## 9. Standards-doc impact

The existing DASHBOARDS.md describes the analyst-dashboard tier
structure (Tier 0 orientation → Tier 1 headline → Tier 2 KPIs → Tier 3
descriptive → Tier 4 takeaway). The verdict-first family follows a
different argument shape: verdict-then-evidence rather than
orientation-headline-detail-takeaway.

Both are valid; they answer different audiences. The DBA dashboard's
design doc §9 established the precedent that DASHBOARDS.md
accommodates carve-outs for differently-shaped dashboards (the operator-
dashboard carve-out). This design proposes a parallel carve-out:

> **Resident-facing verdict-first dashboards** (the verdict-first
> family at `/dashboards/rats`, `/dashboards/crime`,
> `/dashboards/somerville`, and per-dimension surfaces) follow a
> four-block structure (Header → Verdict → Evidence → Methodology
> Note) rather than the four-tier analyst structure. The
> trust-contract receipts requirement still applies: every verdict
> must cite its source data and the rule used to compute it
> (statistical test name + p-value, or heuristic threshold value).
> The methodology note (§3.4 of the family design doc) is the
> required citation location.

The family also implies one new STANDARDS.md addition: a
**verdict-significance discipline** governing how new verdict-first
dashboards select between statistical-test and heuristic-threshold
approaches, and what the methodology note must minimally disclose.
That standard is a follow-up; not part of this design doc.

---

## 10. What v1 implementation will need

Family-level infrastructure (shared across all dashboards):

**New shared modules:**

- `scripts/verdict_template/` — Python module exposing
  `render_verdict_first_dashboard(config)` taking a config dict
  (metric, locality model, color palette, significance approach)
  and producing the static HTML conforming to §3's four-block layout
- `scripts/verdict_template/significance.py` — the shared
  "is this change meaningful" module; consumed by every verdict-first
  dashboard
- `scripts/verdict_template/adaptive_locality.py` — the §5.3
  auto-zoom-out logic; usable by any dashboard whose locality model
  has small-n risk
- `scripts/verdict_template/methodology_note.py` — produces the
  §3.4 disclosure block from the underlying significance computation

**New page:**

- `/dashboards/methodology` — the family-level methodology
  explanation linked from every methodology note. Explains the
  4-state vocabulary, the trailing-12-vs-5-year-average anchor,
  the mixed-significance approach, the adaptive-locality rule.
  Resident-readable; not technical jargon.

**New data ingestion (per dimension):**

- Housing affordability source (likely ACS via Census API; possibly
  Zillow research data; check Zillow's current bulk-download policy
  before depending on it)
- Environmental metrics (tree canopy from Somerville GIS; air quality
  from EPA AirNow; heat mapping if available)
- Per-dashboard: confirmation that the existing warehouse columns
  support the planned locality granularity (Rat v2's block-level
  ambition requires verifying that 311 rat complaints carry sufficient
  geographic detail)

**Per-dashboard implementation prompts (future plans):**

- **Plan X:** Rat DB v2 — applies the template with adaptive locality
- **Plan Y (depends on Plan W):** Crime 360 — applies the template
  with the prose-synthesis variant
- **Plan W (prerequisite to Plan Y):** Crime categorization design
  exercise (bounded design work, not implementation)
- **Plan Z:** Somerville from Top to Bottom — the grid-of-cards page;
  depends on the family template being built and on each dimension's
  data being ingested
- **Plan V (prerequisite to Plan Z):** Housing affordability data
  ingestion (ACS via Census API or equivalent)
- **Plan U (prerequisite to Plan Z):** Environmental data ingestion
  (tree canopy + air quality + heat where available)

The plan numbering above is symbolic; real plan numbers will be
claimed at fire time per the project's slot-resolution discipline.

---

## 11. Future plan: family extension via new dashboards

The verdict-first family is designed to scale. Any new dashboard
answering a resident "is X getting better or worse" question can
conform to the template by:

- Identifying the metric and its locality model
- Picking a significance approach (statistical or heuristic)
- Picking a color palette (alarm or neutral)
- Implementing against the shared modules from §10

Candidate future dashboards visible at this point:

- **Ward by Ward** (per Gordon's dashboard backlog) — *not* a verdict-
  first dashboard in the same shape; it is the *inverse projection*
  (ward-first, metrics drilling out of ward selection). Possible
  future design work to reconcile Ward by Ward's shape with the
  family.
- **Affordability deep-dive** — once housing data is in warehouse,
  housing as its own focused-question dashboard ("Is housing in my
  area getting more or less affordable for people like me?") is a
  natural extension
- **Transit and mobility** — if commute data ingestion happens, a
  trend-first commute dashboard fits
- **Civic participation** — if voter turnout + board applications +
  meeting attendance can be sourced, a participation-trends
  dashboard fits

Each future extension is its own plan, conforming to this design's
template.

---

## 12. Open questions to resolve before implementation

1. **Housing affordability data source.** ACS via Census API is the
   safe default; Zillow research data is fresher but uncertain
   licensing. Decision affects Plan V's scope. Resolve in Plan V's
   own pre-flight.

2. **Block-level data availability for Rat DB v2.** Does Somerville's
   311 rat-complaints data carry the address-level geography needed
   to compute block aggregates? Likely yes, but worth a quick check
   before depending on it for the adaptive-locality mechanism.
   Resolve in Plan X's Phase A.

3. **Crime data geographic mapping to neighborhoods.** Does the crime
   data carry incident-level lat/lng allowing reliable neighborhood
   assignment (Davis, Union, Magoun, Spring Hill, etc.)? Or only
   ward-level? Decision affects Crime 360's locality model.
   Resolve in Plan Y's Phase A (parallel to the categorization
   design exercise).

4. **Plan 24 (Happiness Survey silver/gold) status.** Top to Bottom's
   Happiness Survey card depends on Plan 24's curation. Plan 24 has
   its own halt gate (the k-anonymity probe — if fewer than 12
   harmonized question-keys survive, MVP 3 reshapes). The Top to
   Bottom card's design may need to adapt to whatever survives Plan
   24's halt. Hold pending Plan 24 outcome.

5. **Methodology page audience and depth.** `/dashboards/methodology`
   is resident-readable, not technical. How deep is appropriate?
   Probably: explains the 4-state vocabulary, the time anchor, and
   the significance approaches in plain language with one concrete
   example each; offers a "technical details" expandable section
   for residents who want it. Resolve as part of Plan X's
   implementation (the first family dashboard to ship needs the
   methodology page populated).

6. **Visual identity coherence with the existing portal.** All four
   pages need to feel like part of the existing Somerville analytics
   portal, not grafted-on. Header pattern, color palette discipline
   (especially the alarm-vs-neutral choice), typography. Resolve
   during Plan X's design-review pass using the Playwright
   rendered-page helper.

7. **Map presence at all.** §8 omits maps as primary view, but a
   resident-facing rat dashboard with no map view at all may feel
   incomplete. Is a secondary map view (showing ward boundaries
   colored by verdict, for instance) acceptable, or strictly out of
   scope? Resolve before Plan X.

---

## 13. Sign-off checklist

Before this design becomes implementation prompts, the following must
be true:

- [x] Operator agrees with the four design commitments (Section 2)
- [x] Operator agrees with the four-block template (Section 3)
- [x] Operator agrees with the color discipline (Section 4)
- [x] Operator agrees with the locality model including adaptive
      locality for Rat v2 (Section 5)
- [x] Operator agrees with Crime 360's editorial-summary variant
      (Section 6)
- [x] Operator agrees with Top to Bottom's grid-of-cards shape and
      the seven dimensions (Section 7)
- [x] Operator agrees with the DASHBOARDS.md carve-out (Section 9)
- [ ] Plan numbers reserved in LOG.md Plans Registry for the family-
      template and per-dashboard plans
- [ ] Open questions in Section 12 are answered or explicitly deferred
      to per-plan Phase A inspections

After sign-off, implementation is a sequence of plans roughly
following §10's enumeration. The minimum first step is the family-
template infrastructure (the `scripts/verdict_template/` module + the
methodology page), against which Rat DB v2 becomes the first concrete
dashboard. Crime 360 and Top to Bottom follow, each with their own
prerequisites (categorization design; housing + environmental data
ingestion).

The total work to ship the full family is substantial — easily 4-6
plans, possibly more. The family is not a single sprint; it is a
strategic build-out across multiple sessions.

---

## 14. Acknowledged tensions

Design choices that involved trade-offs worth naming for future
reference:

**Verdict-first vs honest-uncertainty.** Saying "GETTING WORSE"
directly is more useful to a resident than showing them a chart, but
it also stakes the project's reputation on a verdict that might shift.
The four-state vocabulary including "unclear" is the principal
mitigation; the methodology note's disclosure is the secondary.

**Block-level ambition vs noise honesty.** Block-level "near me" is
what residents want; block-level data is too noisy for honest
verdicts. The adaptive-locality mechanism resolves the tension at the
cost of UI complexity.

**Crime 360's neutral palette vs visual consistency with the family.**
Different color systems across dashboards in the same family is a
cohesion cost. The cost is accepted because crime's alarm potential
is genuinely different.

**Top to Bottom's grid of cards vs the original "long narrative
scroll" framing.** The grid is more tractable but loses the narrative
feel. If a long-form treatment ever feels needed, it can layer over
the grid as an "alternate reading mode" — out of scope for v1.

**Housing data ingestion as a foundational prerequisite vs ship-what-
we-have.** Choosing to ingest housing data first means Top to Bottom
ships later, but ships with the most-asked-about dimension intact.
Shipping without housing would produce a Top to Bottom missing the
dimension residents most care about — a structural shortcoming worse
than a delay.

These tensions are real and may resurface as v1 contacts residents.
v1.1 design will incorporate what is learned.
