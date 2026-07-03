"""Audit a page's HTML for common on-page and technical SEO issues.

Checks title length, meta description, heading structure, image alt text,
canonical tags, robots directives, and internal/external link counts —
covering the on-page fundamentals from ``docs/books/complete/seo/`` chapters
9 (Content Optimization) and 14 (Structured Data).

Example:
    >>> from scripts.seo_audit import audit_html
    >>> result = audit_html("<html>...</html>", url="https://example.com/page")
    >>> result.score
    82.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from urllib.parse import urlparse

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

TITLE_MIN_LENGTH = 30
TITLE_MAX_LENGTH = 60
META_DESCRIPTION_MIN_LENGTH = 70
META_DESCRIPTION_MAX_LENGTH = 160
THIN_CONTENT_WORD_THRESHOLD = 300

# Each check that fails deducts this many points from a 100-point baseline.
_PENALTY_PER_ISSUE = 8.0


@dataclass
class Issue:
    """A single SEO issue found during an audit."""

    severity: str  # "error" | "warning"
    category: str
    message: str


@dataclass
class AuditResult:
    """The outcome of auditing a single page's HTML."""

    url: str
    word_count: int = 0
    title: str | None = None
    meta_description: str | None = None
    h1_count: int = 0
    images_missing_alt: int = 0
    internal_link_count: int = 0
    external_link_count: int = 0
    has_canonical: bool = False
    is_noindex: bool = False
    issues: list[Issue] = field(default_factory=list)

    @property
    def score(self) -> float:
        """A 0-100 heuristic health score. Not a ranking prediction."""
        penalty = sum(
            _PENALTY_PER_ISSUE if issue.severity == "error" else _PENALTY_PER_ISSUE / 2
            for issue in self.issues
        )
        return max(0.0, round(100.0 - penalty, 1))

    def add_issue(self, severity: str, category: str, message: str) -> None:
        self.issues.append(Issue(severity=severity, category=category, message=message))


def _check_title(soup: BeautifulSoup, result: AuditResult) -> None:
    title_tag = soup.find("title")
    if not title_tag or not title_tag.get_text(strip=True):
        result.add_issue("error", "title", "Missing <title> tag")
        return

    title = title_tag.get_text(strip=True)
    result.title = title
    length = len(title)
    if length < TITLE_MIN_LENGTH:
        result.add_issue("warning", "title", f"Title is only {length} characters (recommended >= {TITLE_MIN_LENGTH})")
    elif length > TITLE_MAX_LENGTH:
        result.add_issue("warning", "title", f"Title is {length} characters (recommended <= {TITLE_MAX_LENGTH})")


def _check_meta_description(soup: BeautifulSoup, result: AuditResult) -> None:
    meta = soup.find("meta", attrs={"name": "description"})
    content = meta.get("content", "").strip() if meta else ""
    if not content:
        result.add_issue("error", "meta_description", "Missing meta description")
        return

    result.meta_description = content
    length = len(content)
    if length < META_DESCRIPTION_MIN_LENGTH:
        result.add_issue(
            "warning",
            "meta_description",
            f"Meta description is only {length} characters (recommended >= {META_DESCRIPTION_MIN_LENGTH})",
        )
    elif length > META_DESCRIPTION_MAX_LENGTH:
        result.add_issue(
            "warning",
            "meta_description",
            f"Meta description is {length} characters (recommended <= {META_DESCRIPTION_MAX_LENGTH})",
        )


def _check_headings(soup: BeautifulSoup, result: AuditResult) -> None:
    h1_tags = soup.find_all("h1")
    result.h1_count = len(h1_tags)
    if result.h1_count == 0:
        result.add_issue("error", "headings", "Missing <h1> tag")
    elif result.h1_count > 1:
        result.add_issue("warning", "headings", f"Multiple <h1> tags found ({result.h1_count})")


def _check_images(soup: BeautifulSoup, result: AuditResult) -> None:
    images = soup.find_all("img")
    missing = [img for img in images if not img.get("alt", "").strip()]
    result.images_missing_alt = len(missing)
    if missing:
        result.add_issue(
            "warning", "images", f"{len(missing)} of {len(images)} images are missing alt text"
        )


def _check_canonical(soup: BeautifulSoup, result: AuditResult) -> None:
    canonical = soup.find("link", attrs={"rel": "canonical"})
    result.has_canonical = bool(canonical and canonical.get("href"))
    if not result.has_canonical:
        result.add_issue("warning", "canonical", "Missing canonical link tag")


def _check_robots_meta(soup: BeautifulSoup, result: AuditResult) -> None:
    robots = soup.find("meta", attrs={"name": "robots"})
    content = robots.get("content", "").lower() if robots else ""
    result.is_noindex = "noindex" in content
    if result.is_noindex:
        result.add_issue("warning", "indexability", "Page is marked noindex")


def _check_content_length(soup: BeautifulSoup, result: AuditResult) -> None:
    text = soup.get_text(separator=" ", strip=True)
    result.word_count = len(text.split())
    if result.word_count < THIN_CONTENT_WORD_THRESHOLD:
        result.add_issue(
            "warning",
            "content",
            f"Page has only {result.word_count} words (recommended >= {THIN_CONTENT_WORD_THRESHOLD})",
        )


def _check_links(soup: BeautifulSoup, result: AuditResult, page_url: str) -> None:
    page_domain = urlparse(page_url).netloc if page_url else ""
    internal = external = 0
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        domain = urlparse(href).netloc
        if not domain or (page_domain and domain == page_domain):
            internal += 1
        else:
            external += 1
    result.internal_link_count = internal
    result.external_link_count = external
    if internal == 0:
        result.add_issue("warning", "internal_links", "No internal links found on page")


def audit_html(html: str, url: str = "") -> AuditResult:
    """Run a full on-page SEO audit against a page's raw HTML.

    Args:
        html: The page's HTML source (post-render if JavaScript-dependent).
        url: The page's canonical URL, used to classify internal vs. external
            links. Optional but recommended.

    Returns:
        An :class:`AuditResult` with the discovered issues and a heuristic score.
    """
    soup = BeautifulSoup(html, "lxml")
    result = AuditResult(url=url)

    _check_title(soup, result)
    _check_meta_description(soup, result)
    _check_headings(soup, result)
    _check_images(soup, result)
    _check_canonical(soup, result)
    _check_robots_meta(soup, result)
    _check_content_length(soup, result)
    _check_links(soup, result, url)

    logger.info("Audited %s: score=%s, issues=%d", url or "<no url>", result.score, len(result.issues))
    return result


def audit_url(url: str, *, timeout: float = 10.0) -> AuditResult:
    """Fetch a URL and run :func:`audit_html` against the response body.

    Args:
        url: The absolute URL to fetch and audit.
        timeout: Request timeout in seconds.

    Returns:
        An :class:`AuditResult` for the fetched page.

    Raises:
        requests.RequestException: If the page cannot be fetched.
    """
    import requests

    response = requests.get(url, timeout=timeout, headers={"User-Agent": "seo-aeo-playbook-audit/0.1"})
    response.raise_for_status()
    return audit_html(response.text, url=url)


def format_report(result: AuditResult) -> str:
    """Render an :class:`AuditResult` as a human-readable text report."""
    lines = [
        f"SEO Audit Report: {result.url or '(no URL provided)'}",
        f"Score: {result.score}/100",
        f"Word count: {result.word_count}",
        f"Title: {result.title!r}",
        f"Meta description: {result.meta_description!r}",
        f"H1 count: {result.h1_count}",
        f"Images missing alt: {result.images_missing_alt}",
        f"Internal links: {result.internal_link_count} | External links: {result.external_link_count}",
        f"Canonical present: {result.has_canonical} | Noindex: {result.is_noindex}",
        "",
        f"Issues ({len(result.issues)}):",
    ]
    for issue in result.issues:
        lines.append(f"  [{issue.severity.upper()}] {issue.category}: {issue.message}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.seo_audit <url>``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Audit a live URL for common SEO issues.")
    parser.add_argument("url", help="The URL to fetch and audit")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)

    try:
        result = audit_url(args.url, timeout=args.timeout)
    except Exception as exc:  # noqa: BLE001 - surface any fetch failure to the CLI user
        logger.error("Failed to audit %s: %s", args.url, exc)
        return 1

    print(format_report(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
