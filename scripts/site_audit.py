"""Orchestrate a multi-page site audit across existing single-page tools.

Fetches each page once and runs ``scripts.seo_audit``,
``scripts.schema_validator``, and ``scripts.page_speed`` against that same
fetched HTML (avoiding redundant requests), then rolls the per-page
results up into a site-wide summary — the "full site audit" workflow the
SEO book's technical chapters build toward individually.

Example:
    >>> from scripts.site_audit import PageAuditResult
    >>> PageAuditResult(url="https://example.com/broken", fetch_error="timed out").ok
    False
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from scripts.page_speed import PageSpeedResult, audit_html_performance
from scripts.schema_validator import ValidationIssue, has_errors, validate_html
from scripts.seo_audit import AuditResult, audit_html

logger = logging.getLogger(__name__)


@dataclass
class PageAuditResult:
    """Combined SEO, schema, and performance audit results for one page."""

    url: str
    seo: AuditResult | None = None
    schema_results: list[tuple[dict[str, Any], list[ValidationIssue]]] = field(default_factory=list)
    performance: PageSpeedResult | None = None
    fetch_error: str | None = None

    @property
    def ok(self) -> bool:
        """True if the page was successfully fetched and audited."""
        return self.fetch_error is None

    @property
    def has_schema_errors(self) -> bool:
        return any(has_errors(issues) for _, issues in self.schema_results)

    @property
    def overall_score(self) -> float | None:
        """Average of the SEO and performance heuristic scores, if both are available."""
        if self.seo is None or self.performance is None:
            return None
        return round((self.seo.score + self.performance.score) / 2, 1)


@dataclass
class SiteAuditSummary:
    """Site-wide rollup of a set of :class:`PageAuditResult`."""

    total_pages: int
    pages_ok: int
    pages_failed: int
    average_seo_score: float | None
    average_performance_score: float | None
    pages_with_schema_errors: list[str]
    total_seo_issues: int
    total_performance_issues: int


def audit_page(url: str, *, timeout: float = 10.0) -> PageAuditResult:
    """Fetch a single page and run the SEO, schema, and performance audits against it.

    Args:
        url: The absolute URL to fetch and audit.
        timeout: Request timeout in seconds.

    Returns:
        A :class:`PageAuditResult`. If the page cannot be fetched, the
        result has ``fetch_error`` set and ``seo``/``performance`` left ``None``
        rather than raising.
    """
    import requests

    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "seo-aeo-playbook-site-audit/0.1"})
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return PageAuditResult(url=url, fetch_error=str(exc))

    html = response.text
    seo_result = audit_html(html, url=url)
    schema_results = validate_html(html)
    performance_result = audit_html_performance(html, url=url, ttfb_seconds=response.elapsed.total_seconds())
    return PageAuditResult(url=url, seo=seo_result, schema_results=schema_results, performance=performance_result)


def audit_site(urls: list[str], *, timeout: float = 10.0) -> list[PageAuditResult]:
    """Audit multiple pages sequentially.

    Args:
        urls: The absolute URLs to audit.
        timeout: Per-page request timeout in seconds, passed to :func:`audit_page`.

    Returns:
        One :class:`PageAuditResult` per URL, in the same order.
    """
    results = [audit_page(url, timeout=timeout) for url in urls]
    failed = sum(1 for result in results if not result.ok)
    logger.info("Audited %d page(s): %d failed to fetch", len(results), failed)
    return results


def summarize_site(results: list[PageAuditResult]) -> SiteAuditSummary:
    """Roll up per-page audit results into a site-wide summary.

    Args:
        results: Per-page results, typically from :func:`audit_site`.

    Returns:
        A :class:`SiteAuditSummary` aggregating scores and issue counts
        across all successfully-audited pages.
    """
    ok_results = [result for result in results if result.ok]
    seo_scores = [result.seo.score for result in ok_results if result.seo]
    performance_scores = [result.performance.score for result in ok_results if result.performance]

    return SiteAuditSummary(
        total_pages=len(results),
        pages_ok=len(ok_results),
        pages_failed=len(results) - len(ok_results),
        average_seo_score=round(sum(seo_scores) / len(seo_scores), 1) if seo_scores else None,
        average_performance_score=(
            round(sum(performance_scores) / len(performance_scores), 1) if performance_scores else None
        ),
        pages_with_schema_errors=[result.url for result in ok_results if result.has_schema_errors],
        total_seo_issues=sum(len(result.seo.issues) for result in ok_results if result.seo),
        total_performance_issues=sum(len(result.performance.issues) for result in ok_results if result.performance),
    )


def format_report(results: list[PageAuditResult], summary: SiteAuditSummary) -> str:
    """Render per-page results and the site-wide summary as a text report."""
    lines = [
        f"Site Audit Report ({summary.total_pages} page(s), {summary.pages_failed} failed to fetch)",
        f"Average SEO score: {summary.average_seo_score if summary.average_seo_score is not None else 'n/a'}",
        f"Average performance score: "
        f"{summary.average_performance_score if summary.average_performance_score is not None else 'n/a'}",
        f"Total SEO issues: {summary.total_seo_issues} | Total performance issues: {summary.total_performance_issues}",
    ]
    if summary.pages_with_schema_errors:
        lines.append(f"Pages with schema errors ({len(summary.pages_with_schema_errors)}):")
        lines.extend(f"  - {url}" for url in summary.pages_with_schema_errors)

    lines.append("")
    lines.append("Per-page results:")
    for result in results:
        if not result.ok:
            lines.append(f"  {result.url}: FAILED TO FETCH ({result.fetch_error})")
            continue
        lines.append(
            f"  {result.url}: overall={result.overall_score} "
            f"(seo={result.seo.score if result.seo else 'n/a'}, "
            f"performance={result.performance.score if result.performance else 'n/a'}, "
            f"schema_errors={result.has_schema_errors})"
        )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.site_audit urls.txt``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Audit multiple pages for SEO, schema, and performance issues.")
    parser.add_argument("urls_file", help="Path to a text file, one absolute URL per line")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)

    try:
        with open(args.urls_file, encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    except OSError as exc:
        logging.error("Could not read %s: %s", args.urls_file, exc)
        return 1

    results = audit_site(urls, timeout=args.timeout)
    summary = summarize_site(results)
    print(format_report(results, summary))
    return 1 if summary.pages_failed or summary.pages_with_schema_errors else 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
