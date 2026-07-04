"""Check URLs for broken links and redirect chains.

Covers the "broken link building" / link-rot concerns mentioned in
``docs/books/complete/seo/chapter-18.md`` and general crawlability checks
from the technical SEO chapters: given a list of URLs (or an HTML page to
extract links from), reports which are broken (4xx/5xx or unreachable) and
which redirect, so stale or misconfigured links can be found and fixed
before they erode crawl budget or user trust.

Example:
    >>> from scripts.link_checker import extract_links_from_html
    >>> html = '<a href="/about">About</a><a href="https://example.com/blog">Blog</a>'
    >>> extract_links_from_html(html, base_url="https://example.com/")
    ['https://example.com/about', 'https://example.com/blog']
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

# Status codes where a HEAD request commonly fails even though the resource
# is reachable; retry with GET before concluding the link is broken.
_HEAD_UNRELIABLE_STATUSES = frozenset({403, 405, 501})


@dataclass
class LinkCheckResult:
    """The outcome of checking a single URL."""

    url: str
    status_code: int | None = None
    final_url: str | None = None
    redirected: bool = False
    error: str | None = None

    @property
    def is_broken(self) -> bool:
        """True if the URL could not be reached, or resolved to a 4xx/5xx status."""
        return self.error is not None or self.status_code is None or self.status_code >= 400


def check_link(url: str, *, timeout: float = 10.0) -> LinkCheckResult:
    """Check a single URL's reachability, status code, and redirect behavior.

    Args:
        url: The absolute URL to check.
        timeout: Request timeout in seconds.

    Returns:
        A :class:`LinkCheckResult` describing the outcome. Network failures
        are captured in the result's ``error`` field rather than raised.
    """
    import requests

    headers = {"User-Agent": "seo-aeo-playbook-link-checker/0.1"}
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        if response.status_code in _HEAD_UNRELIABLE_STATUSES:
            response = requests.get(url, timeout=timeout, allow_redirects=True, headers=headers)
    except requests.RequestException as exc:
        return LinkCheckResult(url=url, error=str(exc))

    return LinkCheckResult(
        url=url,
        status_code=response.status_code,
        final_url=response.url,
        redirected=len(response.history) > 0,
    )


def check_links(urls: list[str], *, timeout: float = 10.0) -> list[LinkCheckResult]:
    """Check a list of URLs sequentially.

    Args:
        urls: The absolute URLs to check.
        timeout: Per-request timeout in seconds, passed through to :func:`check_link`.

    Returns:
        One :class:`LinkCheckResult` per URL, in the same order.
    """
    results = [check_link(url, timeout=timeout) for url in urls]
    broken_count = sum(1 for result in results if result.is_broken)
    logger.info("Checked %d link(s): %d broken", len(results), broken_count)
    return results


def extract_links_from_html(html: str, base_url: str = "") -> list[str]:
    """Extract absolute link URLs from a page's HTML.

    Args:
        html: The page's HTML source.
        base_url: The page's own URL, used to resolve relative hrefs to
            absolute URLs. If omitted, relative hrefs are left as-is.

    Returns:
        Absolute (or, without base_url, as-authored) link URLs in document
        order, excluding fragment-only, mailto:, tel:, and javascript: links.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        links.append(urljoin(base_url, href) if base_url else href)
    return links


def format_report(results: list[LinkCheckResult]) -> str:
    """Render link check results as a human-readable text report."""
    broken = [result for result in results if result.is_broken]
    redirected = [result for result in results if result.redirected and not result.is_broken]

    lines = [f"Link Check Report ({len(results)} link(s) checked, {len(broken)} broken)", ""]

    if broken:
        lines.append(f"Broken links ({len(broken)}):")
        for result in broken:
            detail = result.error or f"HTTP {result.status_code}"
            lines.append(f"  - {result.url} [{detail}]")
        lines.append("")

    if redirected:
        lines.append(f"Redirected links ({len(redirected)}):")
        for result in redirected:
            lines.append(f"  - {result.url} -> {result.final_url} [HTTP {result.status_code}]")
        lines.append("")

    ok_count = len(results) - len(broken) - len(redirected)
    lines.append(f"{ok_count} link(s) OK, {len(redirected)} redirected, {len(broken)} broken.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.link_checker urls.txt`` or ``page.html``.

    A ``.html`` file has its links extracted and checked; any other file is
    treated as a plain text list of URLs, one per line.
    """
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Check a list of URLs (or links in an HTML page) for broken links.")
    parser.add_argument("input_file", help="Path to a urls.txt (one URL per line) or an .html file")
    parser.add_argument("--base-url", default="", help="Base URL for resolving relative links (HTML input only)")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)

    try:
        with open(args.input_file, encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        logging.error("Could not read %s: %s", args.input_file, exc)
        return 1

    if args.input_file.lower().endswith(".html"):
        urls = extract_links_from_html(content, base_url=args.base_url)
    else:
        urls = [line.strip() for line in content.splitlines() if line.strip()]

    results = check_links(urls, timeout=args.timeout)
    print(format_report(results))
    return 1 if any(result.is_broken for result in results) else 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
