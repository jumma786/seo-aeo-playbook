"""Unit tests for scripts.site_audit."""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import pytest
import requests

from scripts.site_audit import (
    PageAuditResult,
    audit_page,
    audit_site,
    format_report,
    summarize_site,
)

CLEAN_HTML = """
<html>
<head>
  <title>A Well Optimized Page About Core Web Vitals</title>
  <meta name="description" content="A sufficiently long meta description that satisfies the recommended length guidance for search snippets.">
  <link rel="canonical" href="https://example.com/">
  <script type="application/ld+json">{"@context": "https://schema.org", "@type": "Organization", "name": "Example Corp", "url": "https://example.com"}</script>
</head>
<body>
  <h1>Core Web Vitals</h1>
  <p>""" + ("word " * 320) + """</p>
  <a href="/about">About</a>
</body>
</html>
"""

BROKEN_SCHEMA_HTML = """
<html>
<head>
  <title>A Well Optimized Page About Core Web Vitals</title>
  <meta name="description" content="A sufficiently long meta description that satisfies the recommended length guidance for search snippets.">
  <link rel="canonical" href="https://example.com/">
  <script type="application/ld+json">{"@type": "Article", "headline": "Hi"}</script>
</head>
<body>
  <h1>Core Web Vitals</h1>
  <p>""" + ("word " * 320) + """</p>
</body>
</html>
"""


def _fake_response(html: str, *, elapsed_seconds: float = 0.1) -> SimpleNamespace:
    return SimpleNamespace(text=html, elapsed=timedelta(seconds=elapsed_seconds), raise_for_status=lambda: None)


class TestPageAuditResult:
    def test_ok_when_no_fetch_error(self) -> None:
        assert PageAuditResult(url="https://example.com/").ok is True

    def test_not_ok_with_fetch_error(self) -> None:
        assert PageAuditResult(url="https://example.com/", fetch_error="timed out").ok is False

    def test_overall_score_none_without_results(self) -> None:
        assert PageAuditResult(url="https://example.com/").overall_score is None


class TestAuditPage:
    def test_successful_fetch_runs_all_audits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: _fake_response(CLEAN_HTML))
        result = audit_page("https://example.com/")
        assert result.ok is True
        assert result.seo is not None
        assert result.performance is not None
        assert result.has_schema_errors is False
        assert result.overall_score is not None

    def test_schema_errors_detected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: _fake_response(BROKEN_SCHEMA_HTML))
        result = audit_page("https://example.com/")
        assert result.has_schema_errors is True

    def test_fetch_failure_captured_not_raised(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fail(url: str, **kwargs: object) -> SimpleNamespace:
            raise requests.ConnectionError("connection refused")

        monkeypatch.setattr(requests, "get", fail)
        result = audit_page("https://example.com/")
        assert result.ok is False
        assert "connection refused" in result.fetch_error
        assert result.seo is None


class TestAuditSite:
    def test_audits_all_urls_in_order(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: _fake_response(CLEAN_HTML))
        results = audit_site(["https://example.com/a", "https://example.com/b"])
        assert [r.url for r in results] == ["https://example.com/a", "https://example.com/b"]


class TestSummarizeSite:
    def test_summarizes_mixed_results(self, monkeypatch: pytest.MonkeyPatch) -> None:
        responses = iter([_fake_response(CLEAN_HTML), _fake_response(BROKEN_SCHEMA_HTML)])
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: next(responses))
        results = audit_site(["https://example.com/ok", "https://example.com/broken-schema"])
        summary = summarize_site(results)

        assert summary.total_pages == 2
        assert summary.pages_ok == 2
        assert summary.pages_failed == 0
        assert summary.average_seo_score is not None
        assert summary.pages_with_schema_errors == ["https://example.com/broken-schema"]

    def test_failed_fetch_excluded_from_averages(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fail(url: str, **kwargs: object) -> SimpleNamespace:
            raise requests.ConnectionError("connection refused")

        monkeypatch.setattr(requests, "get", fail)
        results = audit_site(["https://example.com/down"])
        summary = summarize_site(results)

        assert summary.pages_failed == 1
        assert summary.pages_ok == 0
        assert summary.average_seo_score is None

    def test_empty_results(self) -> None:
        summary = summarize_site([])
        assert summary.total_pages == 0
        assert summary.average_seo_score is None


class TestFormatReport:
    def test_report_includes_failed_and_ok_pages(self, monkeypatch: pytest.MonkeyPatch) -> None:
        responses = iter([_fake_response(CLEAN_HTML)])

        def get(url: str, **kwargs: object) -> SimpleNamespace:
            if url == "https://example.com/down":
                raise requests.ConnectionError("connection refused")
            return next(responses)

        monkeypatch.setattr(requests, "get", get)
        results = audit_site(["https://example.com/ok", "https://example.com/down"])
        summary = summarize_site(results)
        report = format_report(results, summary)

        assert "FAILED TO FETCH" in report
        assert "https://example.com/ok" in report
