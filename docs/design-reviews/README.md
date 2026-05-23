# Design reviews

Reviews of rendered pages — UI surfaces, dashboards, dbt-docs pages,
portal routes — produced on demand by `scripts/rendered_page.py`'s
`review_page()` entry point. Each review captures the live state of a
URL at a point in time and writes a self-contained finding artifact
plus the raw evidence behind it.

## What a review is

A review is a directory under `docs/design-reviews/<slug>-<YYYY-MM-DD>/`
containing:

- `finding.md` — the prose finding, written by the reviewer (Code or a
  person) based on the evidence files in the same dir. Names the answer
  to the focus question (or honestly enumerates what was tried and
  where the inspection hit a limit) and grounds each claim in specific
  evidence.
- `annotated.png` — full-page screenshot with numbered callouts on
  elements of interest and a legend panel below.
- `screenshot.png` — un-annotated full-page screenshot.
- `network-requests.json` — full network request/response log captured
  by Playwright during the page load.
- `window-globals.json` — `window` object scan for library-shaped
  identifiers (`mark`, `markdown-it`, `remark`, `showdown`, etc.).
- `back-link-dom.json` / `<target>-dom.json` — DOM dumps + computed
  style for elements the review focuses on.
- `rendered.html` — full rendered HTML at capture time (useful for
  grepping inline bundles or hunting for signatures the targeted probes
  missed).

## When reviews happen

- **On request.** Reviews are not generated on every PR. They exist
  because Code or a human asked one for a specific reason — to verify a
  gate, identify a library, audit a design surface, debug a render
  regression, or document the rendered shape of something contentious.
- **Not on every PR.** Gates that have a clean static-artifact check
  (a schema.yml line, a config value, a deny pattern) do not need a
  review; they need their normal evidence.
- **Always when a gate says "verify the rendered surface."** This is
  binding — the MVP 1 retrospective named it, Plan 33 added the helper
  that closes the gap, and STANDARDS.md §8 codifies the rule.

## How reviews are scoped

The `focus` argument to `review_page()` carries the question being
asked. The same helper handles both technical and design questions —
only the focus changes:

- **Technical inspection:** "identify the JavaScript library
  responsible for rendering Markdown in block_contents."
- **Design feedback:** "the rat-complaints panel feels too crowded
  below 1024px; pinpoint which elements cause the overflow and what
  the contributing styles are."
- **Regression debugging:** "the /trust banner went from green to
  yellow overnight — what's actually rendering and what does the
  fct_test_run latest run say?"
- **Open-ended audit:** `focus=None` — walk the page, surface what
  looks off, no specific question.

All four shapes produce the same kind of artifact. The reviewer's
prose in `finding.md` adapts to the focus.

## Who writes reviews

Code, on request. The helper produces the evidence; Code (or a person)
writes the `finding.md` prose by reading the evidence. The helper's
scaffolded `finding.md` template has the evidence sections pre-filled
and a placeholder for the prose Finding section that the reviewer
replaces.

## Honest reporting

If the inspection genuinely can't answer the focus question — minified
bundle with no source-maps, page that won't render, target element
that doesn't exist on the rendered surface — the finding says so and
enumerates what was tried. "I looked at X, Y, Z; the closest match
is W but I'm not certain" is a valid finding. Vacuous claims like
"it's a JavaScript library" without evidence are not. This mirrors the
honest-reporting discipline named in `BUILD.md` §7.

## Browsing

Each review is dated in its directory name so chronological browsing
is straightforward (`ls docs/design-reviews/`). The `slug` portion of
the directory name describes the target — `dbt-docs-library-inspection`,
`rat-complaints-mobile-overflow`, `trust-banner-yellow-debug`. Keep
slugs descriptive enough to grep.
