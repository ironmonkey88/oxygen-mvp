# How We Build — our approach

*A plain-language guide to the principles and process behind this project.*

This is a short, jargon-free explanation of how this project works — what we're
building, what we believe, and the working habits that keep the quality high.
If you're new to the project, start here.

> **How to use this document.** This is the **reference standard** for the
> project's approach — the durable statement of principles and process that our
> other, more detailed documents are kept consistent with. It deliberately
> avoids specific tools and implementation details, which change over time;
> those live in the detailed docs. From time to time we **reconcile** the
> detailed docs against this one. Throughout, we illustrate with our first
> instance — a civic-analytics platform built on Somerville's public data — but
> the approach applies to any community.

---

## What we're building

We turn a community's public data — things like 311 service requests (potholes,
missed trash pickups, noise complaints) — into clear answers anyone can
understand. The goal isn't a wall of charts. It's to help a community member see
how their city is actually doing, honestly and in context.

We call the things we make **knowledge products**: not just raw numbers, but
numbers turned into understanding. You can ask a question in plain language and
get an answer backed by real evidence.

## What we believe

Every knowledge product we build rests on three words:

- **Empathy.** The answer has to fit the person asking and their situation. The
  same fact means different things to different people, so context isn't a
  nicety — it's part of being correct.
- **Honesty.** We show the hard news and the good news with equal rigor. Every
  answer carries its evidence, and we say plainly what we don't know or can't
  show. Honesty is the rule the other two answer to.
- **Optimism.** Data built from complaints and incidents tells a gloomy story by
  default. We deliberately surface real progress too — not to spin, but to
  correct a bias the data would otherwise hide. Optimism here is earned: it's a
  conclusion the evidence supports, never a mood we paint on.

Put simply: *see the whole community honestly — the hard and the hopeful —
because the people who live there deserve the full truth.*

## How we work: the trust contract

Our single most important habit is what we call the **trust contract**. Every
answer the system gives must show its work: the exact query it ran, how many
records it covered, where the data came from, and any limitations. Nothing is
asserted without the evidence sitting right next to it.

This means a reader never has to take our word for anything. They can always get
to the proof underneath a claim. An answer that can't show its evidence isn't
finished.

## How we think: hypothesis, then result

We treat turning data into understanding like the scientific method, in two
clearly-labeled stages:

- **A hypothesis** is a working idea. It's allowed to be quick, rough, and
  exploratory — that's how thinking happens. But it always wears the label
  "hypothesis" so no one mistakes it for a settled fact.
- **A result** is an answer that has earned its place. It pays the full trust
  contract: real query, real numbers, citations, limitations.

The rule that keeps us honest: a hypothesis only becomes a result by passing the
evidence gate. If it can't, it's presented as an open question — never quietly
dressed up as a finding. Cheap exploration is fine; **unlabeled** speculation is
not.

Why this matters: both people and AI tools tend to either freeze when handed too
much data, or confidently make up a story. A clear structure — a hypothesis
under test, a gate before it counts — prevents both failures.

## How the work gets done: decide, then build

We work in two phases, always in this order:

- **Decide.** Understand the need and what solving it is worth, look at possible
  solutions, weigh the value against the effort, and settle on a design worth
  building.
- **Build.** Execute the design that was agreed — write the code, run the
  system, save the changes.

This mirrors **Scrum**: someone identifies a problem along with the value of
solving it, the team proposes a solution and estimates the effort, and the
**ratio of value to effort** decides whether it's worth doing. Only after it
earns a place does anyone build it. Work that doesn't clear that ratio never
enters the build phase. Deciding *what is worth building* is its own job,
separate from building it.

The phases are the constant; how they're staffed is not. The deciding phase and
the building phase could be filled by different tools, different AIs, or
different people — what matters is the process and its order, not what's filling
the seats. (Today, for instance, we run the deciding phase in one mode we call
**Chat** and the building phase in another we call **Code**, with a written
instruction carrying the agreed design between them — but that's one current
arrangement, not the principle.) Keeping the phases distinct also forces the
design to be **written down** before building starts — stating, in plain words,
who benefits and what changes for them — so the work survives whoever picks it
up.

### We describe the outcome, not the steps

When we hand a design to the build phase, we describe the **outcome we want and
the tests that prove it** — not the exact steps to get there. The builder is
trusted to work out the how, within fixed guardrails: follow the agreed
methodology, honor the principles, and don't add new technology or complexity
without a critical reason.

The build phase's job is then to make reality match that description — a process
worth naming, because mature systems are built on it: **reconciliation**. You
state the desired end-state; the system continuously checks actual against
desired and closes the gap. This isn't a one-time instruction — it's a standing
description of what should be true, enforced over time. Our tests and
documentation work exactly this way: they declare what must stay true, and they
drive the system back toward it when something drifts.

### How much to specify depends on the builder

How much direction a design needs depends on how capable the builder is for that
task — the same way a manager **coaches** an experienced person ("here's the
goal, you handle it") but **directs** an inexperienced one ("do this, then
this"). A capable, well-supported builder can be handed an outcome; a weak or
unproven one needs the steps spelled out. The methodology and principles exist
partly to *raise the builder's capability* — so we can describe outcomes more
often and dictate steps less often.

### Why we design for declarative use — and why it matters

This same idea shapes the **finished product**, and it's one of the most
important choices we make. We deliberately build the system to be highly capable
and tightly constrained — reliable data handling, standardized terms and
definitions, structured transformations, and tests that enforce what must stay
true. We do this so the people using it can simply **state what they want and
trust the answer**, without needing to know how it's produced.

That constraint is what makes the trust possible. An AI left unconstrained can
make things up; the standardized terms, the structure, and the tests are the
guardrails that keep it honest. We spend the engineering effort on the inside so
the user doesn't have to spend the decision effort on the outside.

Think of flying a plane versus riding an elevator. A plane is *imperative*: it
takes enormous skill, and you control every step. An elevator is *declarative*:
you press a button and the system handles the rest. Better still, some systems
let you say "take me to oncology" without even knowing the floor — the system
holds the knowledge you'd otherwise need. The more capable the technology, the
more it absorbs on your behalf, and the simpler your request can be.

This is the payoff: **a simpler surface lowers the skill needed to use it, which
widens who can use it and how much value it creates.** Designing for plain,
outcome-level requests isn't just convenience — it's how we broaden the audience
from trained analysts to any community member with a question. But the ease has
to be *earned*: a system can only honestly offer a simple surface when the
reliability underneath it is real. That is the whole job of the trust contract.

## How we get better over time

When we learn something the hard way, we write it down as a reusable rule —
short, clear, and usable by someone with no prior context. A few examples we
live by:

- Test the real thing, not just the parts. A system can pass every component
  check while the actual product is broken, so we always include one end-to-end
  test of the real promise.
- Be honest about what's done. We use a plain status vocabulary — complete,
  partial, blocked, deferred — and never fake a passing result to look finished.
- Record the reasoning behind decisions, including the things we chose not to
  do, so the thinking compounds instead of getting lost.

The point is that effort **compounds**. A lesson learned once becomes a rule
that helps forever, and transfers to anyone who joins.

## The one idea underneath all of it

Good systems give people more understanding and more agency — they widen what a
person can see and do, rather than narrow it. We measure success by whether the
people the work is about understand their community better, not by how clever or
complete the system looks. Some things — people's dignity, their privacy, and
the truth — are never traded away for speed or efficiency. They're the boundary
everything else operates inside.

*Independent and honest about it: this is an independent, community-built
effort, not an official government platform — in our first instance, not
affiliated with the City of Somerville. We draw on public data and name our
inspirations openly, and never imply an affiliation we don't have.*

## Where these ideas come from — a short reading list

The approach above isn't invented from scratch. It draws on established bodies
of thought worth knowing by name:

- **Scrum / Agile** — decide-then-build cadence, and prioritizing work by value
  against effort.
- **Declarative & desired-state design** — describing the outcome and letting
  the system reconcile to it; the thinking behind tools like SQL and modern
  infrastructure automation.
- **Systems engineering (the V-model)** — pairing each build stage with a test
  stage; "built right" and "the right thing" are separate questions.
- **Situational Leadership** — the choice between coaching and directing based
  on how capable the doer is for the task at hand.
- **Progressive disclosure / migrating complexity into the system** — the design
  move that lets a hard thing be operated simply (the elevator, not the
  airplane).
- **Sensemaking (Klein's Data-Frame Theory)** — the structured way people turn
  raw data into understanding; the basis for our hypothesis-then-result
  discipline.
- **Solutions journalism & Intelligent Optimism** — reporting the full picture,
  counting progress as rigorously as problems; the roots of our empathy,
  honesty, and optimism creed.

---

*This document is the reference standard. Companion docs specialize or implement
it: the project-specific convictions doc (PHILOSOPHY.md) is the instance of this
standard for the Somerville build; the methodology and operational docs hold the
implementation detail this document deliberately omits. When this document and a
more detailed doc disagree on a **principle**, this one wins and the detailed doc
is reconciled to it; when they disagree on **how something is currently done**,
the operational doc wins. They answer different questions.*
