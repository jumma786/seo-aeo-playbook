"""Static, heuristic page speed analysis from HTML.

This is not a substitute for lab or field Core Web Vitals data (LCP, INP,
CLS use PageSpeed Insights / CrUX — see the ``seo-google`` skill in this
repository, or ``docs/books/complete/seo/chapter-13.md`` sections 19-21
for Lighthouse/DevTools). Instead it scans a page's raw HTML and measured
time-to-first-byte for the render-blocking-resource, image, and font
issues that most commonly *cause* poor Core Web Vitals scores (chapter-13
sections 9-15), so problems can be caught without running a headless
browser.

Example:
    >>> from scripts.page_speed import audit_html_performance
    >>> html = '<html><head><script src="a.js"></script></head><body></body></html>'
    >>> result = audit_html_performance(html)
    >>> result.render_blocking_scripts
    1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

LARGE_HTML_THRESHOLD_BYTES = 100_000
GOOD_TTFB_SECONDS = 0.8
POOR_TTFB_SECONDS = 1.8
MIN_IMAGES_FOR_LAZY_LOADING_CHECK = 3
_MAX_RECOMMENDED_BLOCKING_STYLESHEETS = 2

# Each error-severity issue deducts more than a warning from a 100-point baseline.
_ERROR_PENALTY = 8.0
_WARNING_PENALTY = 4.0


@dataclass
class PerformanceIssue:
    """A single performance issue found during a page speed audit."""

    severity: str  # "error" | "warning"
    category: str
    message: str


@dataclass
class PageSpeedResult:
    """The outcome of a static page speed audit."""

    url: str = ""
    html_size_bytes: int = 0
    ttfb_seconds: float | None = None
    render_blocking_scripts: int = 0
    render_blocking_stylesheets: int = 0
    total_images: int = 0
    images_missing_dimensions: int = 0
    lazy_loaded_images: int = 0
    issues: list[PerformanceIssue] = field(default_factory=list)

    @property
    def score(self) -> float:
        """A 0-100 heuristic health score. Not a Lighthouse or CrUX score."""
        penalty = sum(
            _ERROR_PENALTY if issue.severity == "error" else _WARNING_PENALTY for issue in self.issues
        )
        return max(0.0, round(100.0 - penalty, 1))

    def add_issue(self, severity: str, category: str, message: str) -> None:
        self.issues.append(PerformanceIssue(severity=severity, category=category, message=message))


def _check_render_blocking_scripts(soup: BeautifulSoup, result: PageSpeedResult) -> None:
    head = soup.find("head")
    if not head:
        return
    blocking = [tag for tag in head.find_all("script", src=True) if not tag.has_attr("async") and not tag.has_attr("defer")]
    result.render_blocking_scripts = len(blocking)
    if blocking:
        result.add_issue(
            "error",
            "render_blocking",
            f"{len(blocking)} render-blocking <script> tag(s) in <head> (missing async/defer)",
        )


def _check_render_blocking_stylesheets(soup: BeautifulSoup, result: PageSpeedResult) -> None:
    head = soup.find("head")
    if not head:
        return
    stylesheets = [
        link
        for link in head.find_all("link", rel="stylesheet")
        if not link.get("media") or link.get("media") == "all"
    ]
    result.render_blocking_stylesheets = len(stylesheets)
    if len(stylesheets) > _MAX_RECOMMENDED_BLOCKING_STYLESHEETS:
        result.add_issue(
            "warning",
            "render_blocking",
            f"{len(stylesheets)} render-blocking stylesheet(s) found; consider critical CSS or reducing count",
        )


def _check_images(soup: BeautifulSoup, result: PageSpeedResult) -> None:
    images = soup.find_all("img")
    result.total_images = len(images)

    missing_dimensions = [img for img in images if not (img.has_attr("width") and img.has_attr("height"))]
    result.images_missing_dimensions = len(missing_dimensions)
    if missing_dimensions:
        result.add_issue(
            "warning",
            "cls",
            f"{len(missing_dimensions)} of {len(images)} <img> tag(s) missing width/height attributes (CLS risk)",
        )

    lazy_images = [img for img in images if img.get("loading") == "lazy"]
    result.lazy_loaded_images = len(lazy_images)
    if len(images) >= MIN_IMAGES_FOR_LAZY_LOADING_CHECK and not lazy_images:
        result.add_issue(
            "warning", "lazy_loading", f'Page has {len(images)} images but none use loading="lazy"'
        )


def _check_fonts(soup: BeautifulSoup, result: PageSpeedResult) -> None:
    for link in soup.find_all("link", href=True):
        href = link["href"]
        if "fonts.googleapis.com" in href and "display=swap" not in href and "display=optional" not in href:
            result.add_issue(
                "warning", "fonts", f"Google Fonts stylesheet is missing a 'display=swap' parameter: {href}"
            )


def _check_page_weight(html: str, result: PageSpeedResult) -> None:
    result.html_size_bytes = len(html.encode("utf-8"))
    if result.html_size_bytes > LARGE_HTML_THRESHOLD_BYTES:
        result.add_issue(
            "warning",
            "page_weight",
            f"HTML document is {result.html_size_bytes:,} bytes (recommended <= {LARGE_HTML_THRESHOLD_BYTES:,})",
        )


def _check_ttfb(result: PageSpeedResult) -> None:
    if result.ttfb_seconds is None:
        return
    if result.ttfb_seconds > POOR_TTFB_SECONDS:
        result.add_issue(
            "error", "ttfb", f"Time to first byte is {result.ttfb_seconds:.2f}s (poor: > {POOR_TTFB_SECONDS}s)"
        )
    elif result.ttfb_seconds > GOOD_TTFB_SECONDS:
        result.add_issue(
            "warning",
            "ttfb",
            f"Time to first byte is {result.ttfb_seconds:.2f}s (needs improvement: > {GOOD_TTFB_SECONDS}s)",
        )


def audit_html_performance(html: str, url: str = "", *, ttfb_seconds: float | None = None) -> PageSpeedResult:
    """Run a static performance audit against a page's raw HTML.

    Args:
        html: The page's HTML source.
        url: The page's canonical URL, included in the result for reporting.
        ttfb_seconds: A pre-measured time-to-first-byte, if available (see
            :func:`audit_url_performance`). Omitted from HTML-only audits.

    Returns:
        A :class:`PageSpeedResult` with the discovered issues and a heuristic score.
    """
    soup = BeautifulSoup(html, "lxml")
    result = PageSpeedResult(url=url, ttfb_seconds=ttfb_seconds)

    _check_render_blocking_scripts(soup, result)
    _check_render_blocking_stylesheets(soup, result)
    _check_images(soup, result)
    _check_fonts(soup, result)
    _check_page_weight(html, result)
    _check_ttfb(result)

    logger.info("Audited %s: score=%s, issues=%d", url or "<no url>", result.score, len(result.issues))
    return result


def audit_url_performance(url: str, *, timeout: float = 10.0) -> PageSpeedResult:
    """Fetch a URL, measure time-to-first-byte, and audit the response HTML.

    Args:
        url: The absolute URL to fetch and audit.
        timeout: Request timeout in seconds.

    Returns:
        A :class:`PageSpeedResult` for the fetched page, including measured
        ``ttfb_seconds`` (via ``requests.Response.elapsed``, which measures
        time to finish parsing response headers — unaffected by how long
        the body takes to download).

    Raises:
        requests.RequestException: If the page cannot be fetched.
    """
    import requests

    response = requests.get(url, timeout=timeout, headers={"User-Agent": "seo-aeo-playbook-page-speed/0.1"})
    response.raise_for_status()
    return audit_html_performance(response.text, url=url, ttfb_seconds=response.elapsed.total_seconds())


def format_report(result: PageSpeedResult) -> str:
    """Render a :class:`PageSpeedResult` as a human-readable text report."""
    lines = [
        f"Page Speed Report: {result.url or '(no URL provided)'}",
        f"Score: {result.score}/100",
        f"HTML size: {result.html_size_bytes:,} bytes",
    ]
    if result.ttfb_seconds is not None:
        lines.append(f"Time to first byte: {result.ttfb_seconds:.2f}s")
    lines.extend(
        [
            f"Render-blocking scripts: {result.render_blocking_scripts} | stylesheets: {result.render_blocking_stylesheets}",
            f"Images: {result.total_images} total, {result.images_missing_dimensions} missing dimensions, "
            f"{result.lazy_loaded_images} lazy-loaded",
            "",
            f"Issues ({len(result.issues)}):",
        ]
    )
    for issue in result.issues:
        lines.append(f"  [{issue.severity.upper()}] {issue.category}: {issue.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.page_speed <url>``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Run a static page speed audit against a live URL.")
    parser.add_argument("url", help="The URL to fetch and audit")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)

    try:
        result = audit_url_performance(args.url, timeout=args.timeout)
    except Exception as exc:  # noqa: BLE001 - surface any fetch failure to the CLI user
        logger.error("Failed to audit %s: %s", args.url, exc)
        return 1

    print(format_report(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
