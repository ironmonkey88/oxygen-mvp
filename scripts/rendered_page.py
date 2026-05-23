"""Rendered-page verification helper.

Render any public URL in headless Chromium via Playwright, then either run
pass/fail assertions or emit a grounded review artifact. Closes the gap where
verification gates that depend on the *rendered surface* (per the MVP 1
retrospective's binding principle) had no automation path and were bouncing
back unverified.

Two entry points:

    test_page(url, assertions, screenshot_path) -> TestResult
        Run a list of callable assertions against the rendered page. Each
        assertion takes the Playwright page object and returns
        (passed: bool, message: str). Writes a full-page screenshot to
        screenshot_path even on pass.

    review_page(url, output_dir, focus=None) -> ReviewArtifact
        Capture the page, the network log, window-global signatures matching
        common library names, source-map probes, and a DOM sample for the
        back-link element. Annotate the screenshot with numbered callouts on
        targets and a legend. Write everything plus a scaffolded finding.md
        into output_dir; the human/LLM reviewer fills in the prose findings
        section based on the evidence.

CLI:

    python scripts/rendered_page.py --demo-inspect-dbt-docs-library
    python scripts/rendered_page.py --url <url> --output-dir <dir> [--focus "..."]

See STANDARDS.md "Rendered-page verification" for usage policy.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Page, sync_playwright
from PIL import Image, ImageDraw, ImageFont

DEFAULT_TIMEOUT_MS = 30000
DEFAULT_WAIT_UNTIL = "networkidle"


@dataclass
class TestResult:
    url: str
    passed: bool
    screenshot_path: Path
    assertions: list = field(default_factory=list)


@dataclass
class ReviewArtifact:
    url: str
    output_dir: Path
    annotated_path: Path
    finding_path: Path
    raw_evidence: dict


def test_page(url, assertions, screenshot_path):
    """Run assertions against the rendered page; return TestResult.

    Each assertion is callable(page) -> (passed: bool, message: str). Always
    writes a screenshot for evidence even on pass.
    """
    screenshot_path = Path(screenshot_path)
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    results = []
    overall_pass = True
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until=DEFAULT_WAIT_UNTIL, timeout=DEFAULT_TIMEOUT_MS)
            page.screenshot(path=str(screenshot_path), full_page=True)
            for assertion in assertions:
                try:
                    passed, msg = assertion(page)
                except Exception as exc:
                    passed, msg = False, f"assertion raised: {exc}"
                results.append((passed, msg))
                if not passed:
                    overall_pass = False
        finally:
            browser.close()

    return TestResult(
        url=url,
        passed=overall_pass,
        screenshot_path=screenshot_path,
        assertions=results,
    )


def review_page(url, output_dir, focus=None):
    """Capture evidence + write annotated screenshot + scaffolded finding."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    requests_log = []
    responses_log = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page()

            page.on(
                "request",
                lambda req: requests_log.append(
                    {"url": req.url, "method": req.method, "resource_type": req.resource_type}
                ),
            )
            page.on(
                "response",
                lambda res: responses_log.append(
                    {
                        "url": res.url,
                        "status": res.status,
                        "content_type": res.headers.get("content-type", ""),
                    }
                ),
            )

            page.goto(url, wait_until=DEFAULT_WAIT_UNTIL, timeout=DEFAULT_TIMEOUT_MS)

            # SPA pages may keep loading after networkidle fires once; give a
            # short window for late hydration / lazy bundles.
            page.wait_for_timeout(2000)

            rendered_html = page.content()
            globals_hits = page.evaluate(_WINDOW_GLOBALS_PROBE)
            backlink_info = page.evaluate(_BACKLINK_DOM_PROBE)

            screenshot_path = output_dir / "screenshot.png"
            page.screenshot(path=str(screenshot_path), full_page=True)

            annotation_targets = []
            for link in backlink_info:
                bb = link.get("boundingBox") or {}
                if not bb or bb.get("width", 0) == 0:
                    continue
                annotation_targets.append(
                    {
                        "x": bb["x"],
                        "y": bb["y"],
                        "width": bb["width"],
                        "height": bb["height"],
                        "label": "Back-link element",
                        "detail": f"display={link['computedStyle']['display']}",
                    }
                )
        finally:
            browser.close()

    js_requests = [
        r
        for r in requests_log
        if r["resource_type"] == "script"
        or r["url"].endswith(".js")
        or ".js?" in r["url"]
    ]
    sourcemap_requests = [r for r in requests_log if r["url"].endswith(".map")]
    sourcemap_responses = [
        r for r in responses_log if r["url"].endswith(".map") and r["status"] < 400
    ]

    (output_dir / "network-requests.json").write_text(
        json.dumps({"requests": requests_log, "responses": responses_log}, indent=2)
    )
    (output_dir / "window-globals.json").write_text(json.dumps(globals_hits, indent=2))
    (output_dir / "back-link-dom.json").write_text(json.dumps(backlink_info, indent=2))
    (output_dir / "rendered.html").write_text(rendered_html)

    annotated_path = output_dir / "annotated.png"
    _annotate(screenshot_path, annotated_path, annotation_targets, url=url, focus=focus)

    finding_path = output_dir / "finding.md"
    finding_path.write_text(
        _render_finding_template(
            url=url,
            focus=focus,
            js_requests=js_requests,
            sourcemap_requests=sourcemap_requests,
            sourcemap_responses=sourcemap_responses,
            globals_hits=globals_hits,
            backlink_info=backlink_info,
            annotation_targets=annotation_targets,
        )
    )

    return ReviewArtifact(
        url=url,
        output_dir=output_dir,
        annotated_path=annotated_path,
        finding_path=finding_path,
        raw_evidence={
            "js_requests": js_requests,
            "sourcemap_requests": sourcemap_requests,
            "sourcemap_responses": sourcemap_responses,
            "globals_hits": globals_hits,
            "backlink_info": backlink_info,
        },
    )


_WINDOW_GLOBALS_PROBE = """() => {
    const patterns = /mark|md|remark|show|micro|commonmark|markdownit|parse/i;
    const keys = Object.keys(window).filter(k => patterns.test(k));
    const result = {};
    for (const k of keys) {
        try {
            const v = window[k];
            if (v === null || v === undefined) {
                result[k] = String(v);
            } else if (typeof v === 'function') {
                result[k] = `function ${v.name || '(anon)'} length=${v.length}`;
            } else if (typeof v === 'object') {
                const ownKeys = Object.keys(v).slice(0, 12);
                result[k] = `object keys=[${ownKeys.join(',')}]`;
            } else {
                result[k] = `${typeof v} = ${String(v).slice(0, 100)}`;
            }
        } catch (e) {
            result[k] = `unreadable: ${e.message}`;
        }
    }
    return result;
}"""

_BACKLINK_DOM_PROBE = """() => {
    const matches = [];
    // Look for the rendered <a> elements (working case)
    const links = Array.from(document.querySelectorAll('a')).filter(a =>
        a.textContent && a.textContent.includes('Back to Somerville')
    );
    for (const a of links) {
        const cs = getComputedStyle(a);
        matches.push({
            kind: 'anchor',
            outerHTML: a.outerHTML.slice(0, 500),
            boundingBox: a.getBoundingClientRect().toJSON(),
            computedStyle: {
                display: cs.display,
                background: cs.background.slice(0, 200),
                color: cs.color,
                padding: cs.padding,
                fontWeight: cs.fontWeight,
            }
        });
    }
    // Also look for literal-text occurrences (broken case)
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
        if (node.textContent && node.textContent.includes('Back to Somerville')) {
            // Skip if this text is already inside an <a> we matched above
            if (node.parentElement && node.parentElement.tagName === 'A') continue;
            const parent = node.parentElement;
            const cs = parent ? getComputedStyle(parent) : null;
            const rect = parent ? parent.getBoundingClientRect().toJSON() : null;
            matches.push({
                kind: 'literal-text',
                outerHTML: parent ? parent.outerHTML.slice(0, 500) : node.textContent.slice(0, 500),
                textContent: node.textContent.slice(0, 300),
                boundingBox: rect,
                computedStyle: cs ? {
                    display: cs.display,
                    background: cs.background.slice(0, 200),
                    color: cs.color,
                    padding: cs.padding,
                    fontWeight: cs.fontWeight,
                } : null,
            });
        }
    }
    return matches;
}"""


def _annotate(screenshot_path, annotated_path, targets, url=None, focus=None):
    """Draw numbered callouts on a copy of the screenshot + a legend panel."""
    img = Image.open(screenshot_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
        )
        font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16
        )
    except OSError:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    for i, tgt in enumerate(targets, 1):
        x, y, w, h = tgt["x"], tgt["y"], tgt["width"], tgt["height"]
        draw.rectangle([x - 4, y - 4, x + w + 4, y + h + 4], outline=(220, 38, 38), width=4)
        label_x, label_y = x + w + 8, max(y - 4, 0)
        draw.ellipse([label_x, label_y, label_x + 36, label_y + 36], fill=(220, 38, 38))
        draw.text((label_x + 11, label_y + 4), str(i), fill=(255, 255, 255), font=font)

    legend_height = max(140, 60 + 30 * (len(targets) + 1))
    new_img = Image.new("RGB", (img.width, img.height + legend_height), (245, 245, 245))
    new_img.paste(img, (0, 0))
    legend = ImageDraw.Draw(new_img)
    legend.text(
        (20, img.height + 12),
        f"URL: {url or '(not provided)'}",
        fill=(0, 0, 0),
        font=font_small,
    )
    if focus:
        focus_short = focus if len(focus) <= 180 else focus[:177] + "..."
        legend.text((20, img.height + 36), f"Focus: {focus_short}", fill=(0, 0, 0), font=font_small)
    for i, tgt in enumerate(targets, 1):
        legend.text(
            (20, img.height + 64 + (i - 1) * 22),
            f"{i}. {tgt['label']} — {tgt.get('detail', '')}",
            fill=(0, 0, 0),
            font=font_small,
        )
    if not targets:
        legend.text(
            (20, img.height + 64),
            "(no annotation targets identified)",
            fill=(100, 100, 100),
            font=font_small,
        )

    new_img.save(annotated_path)


def _render_finding_template(
    url,
    focus,
    js_requests,
    sourcemap_requests,
    sourcemap_responses,
    globals_hits,
    backlink_info,
    annotation_targets,
):
    parts = []
    parts.append(f"# Rendered-page review — {url}")
    parts.append("")
    parts.append(f"_Generated: {datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}_")
    parts.append("")
    if focus:
        parts.append("## Focus")
        parts.append("")
        parts.append(focus)
        parts.append("")
    parts.append("## Annotated screenshot")
    parts.append("")
    parts.append("![annotated](annotated.png)")
    parts.append("")
    parts.append("## Finding")
    parts.append("")
    parts.append(
        "_Reviewer to fill in — name the answer to the focus question (or honestly enumerate "
        "what was tried and where it hit a limit) and ground each claim in the evidence sections "
        "below. Reference numbered callouts on the annotated screenshot when relevant._"
    )
    parts.append("")
    parts.append("## Evidence")
    parts.append("")

    parts.append("### JavaScript bundles loaded")
    parts.append("")
    if js_requests:
        parts.append(f"{len(js_requests)} script request(s):")
        parts.append("")
        for r in js_requests[:30]:
            parts.append(f"- `{r['url']}`")
        if len(js_requests) > 30:
            parts.append(f"- _(+{len(js_requests) - 30} more — see `network-requests.json`)_")
    else:
        parts.append("_(none observed)_")
    parts.append("")

    parts.append("### Source maps")
    parts.append("")
    if sourcemap_requests:
        parts.append(f"{len(sourcemap_requests)} `.map` request(s):")
        parts.append("")
        for r in sourcemap_requests:
            parts.append(f"- `{r['url']}`")
        parts.append("")
        if sourcemap_responses:
            parts.append(
                f"{len(sourcemap_responses)} returned a 2xx/3xx response — source maps available "
                "for de-minification."
            )
        else:
            parts.append("None returned a successful response — likely 404 / not served.")
    else:
        parts.append(
            "_(no `.map` requests observed — bundle is likely minified without source-maps)_"
        )
    parts.append("")

    parts.append("### Window-global signature matches")
    parts.append("")
    parts.append("Scanned `window` for keys matching `/mark|md|remark|show|micro|commonmark|markdownit|parse/i`:")
    parts.append("")
    if globals_hits:
        parts.append("```")
        for k, v in globals_hits.items():
            parts.append(f"{k}: {v}")
        parts.append("```")
    else:
        parts.append(
            "_(no matching globals — library may be enclosed in a bundle module scope; "
            "inspect the bundle source directly via the URLs above)_"
        )
    parts.append("")

    parts.append("### Back-link DOM samples")
    parts.append("")
    if backlink_info:
        for i, link in enumerate(backlink_info, 1):
            parts.append(f"**Sample {i}** (kind: `{link.get('kind', 'unknown')}`):")
            parts.append("")
            parts.append("```html")
            parts.append(link.get("outerHTML", ""))
            parts.append("```")
            if link.get("computedStyle"):
                parts.append("")
                parts.append("```")
                for k, v in link["computedStyle"].items():
                    parts.append(f"{k}: {v}")
                parts.append("```")
            parts.append("")
    else:
        parts.append("_(no back-link element or literal-text occurrence matched)_")
    parts.append("")

    parts.append("## Raw evidence files")
    parts.append("")
    parts.append("- `screenshot.png` — full-page screenshot")
    parts.append("- `annotated.png` — screenshot with numbered callouts + legend")
    parts.append("- `network-requests.json` — full network request/response log")
    parts.append("- `window-globals.json` — captured `window` global signature hits")
    parts.append("- `back-link-dom.json` — DOM + computed style for matched elements")
    parts.append("- `rendered.html` — full rendered HTML at capture time")
    parts.append("")
    return "\n".join(parts)


def _cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--demo-inspect-dbt-docs-library",
        action="store_true",
        help="Run the Plan 33 worked example (review http://18.224.151.49/docs/).",
    )
    parser.add_argument("--url", help="URL to review")
    parser.add_argument("--output-dir", help="Output directory for review artifact")
    parser.add_argument("--focus", help="Focus question for the review")
    args = parser.parse_args(argv)

    if args.demo_inspect_dbt_docs_library:
        url = "http://18.224.151.49/docs/"
        output_dir = Path("docs/design-reviews/dbt-docs-library-inspection-2026-05-22")
        focus = (
            "Identify the JavaScript library responsible for rendering the markdown in "
            "block_contents into HTML. Inspect the bundled JS via network tab, window "
            "globals, and any source-map references. Annotate the rendered back-link "
            "element with its actual DOM shape. The finding feeds Plan 34's back-link "
            "fix and needs to name the library precisely (marked / markdown-it / "
            "showdown / remark / dbt-bespoke / etc.) with evidence."
        )
        artifact = review_page(url, output_dir, focus=focus)
        print(f"Finding written: {artifact.finding_path}")
        print(f"Annotated screenshot: {artifact.annotated_path}")
        return 0

    if args.url and args.output_dir:
        artifact = review_page(args.url, args.output_dir, focus=args.focus)
        print(f"Finding written: {artifact.finding_path}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(_cli())
