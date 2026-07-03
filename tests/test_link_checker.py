"""Unit tests for scripts.link_checker."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest
import requests

from scripts.link_checker import (
    LinkCheckResult,
    check_link,
    check_links,
    extract_links_from_html,
    format_report,
)


@dataclass
class FakeResponse:
    status_code: int
    url: str
    history: list[object] = field(default_factory=list)


class TestLinkCheckResult:
    def test_is_broken_for_4xx(self) -> None:
        assert LinkCheckResult(url="https://example.com/", status_code=404).is_broken is True

    def test_is_broken_for_5xx(self) -> None:
        assert LinkCheckResult(url="https://example.com/", status_code=503).is_broken is True

    def test_not_broken_for_2xx(self) -> None:
        assert LinkCheckResult(url="https://example.com/", status_code=200).is_broken is False

    def test_broken_when_error_present(self) -> None:
        assert LinkCheckResult(url="https://example.com/", error="Connection refused").is_broken is True

    def test_broken_when_no_status_code(self) -> None:
        assert LinkCheckResult(url="https://example.com/").is_broken is True


class TestCheckLink:
    def test_ok_link(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            requests, "head", lambda url, **kwargs: FakeResponse(status_code=200, url=url)
        )
        result = check_link("https://example.com/")
        assert result.status_code == 200
        assert result.is_broken is False
        assert result.redirected is False

    def test_redirected_link(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            requests,
            "head",
            lambda url, **kwargs: FakeResponse(status_code=200, url="https://example.com/new", history=[object()]),
        )
        result = check_link("https://example.com/old")
        assert result.redirected is True
        assert result.final_url == "https://example.com/new"

    def test_broken_link_status(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(requests, "head", lambda url, **kwargs: FakeResponse(status_code=404, url=url))
        result = check_link("https://example.com/missing")
        assert result.is_broken is True
        assert result.status_code == 404

    def test_network_error_captured_not_raised(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fail(url: str, **kwargs: object) -> FakeResponse:
            raise requests.ConnectionError("connection refused")

        monkeypatch.setattr(requests, "head", fail)
        result = check_link("https://example.com/")
        assert result.is_broken is True
        assert "connection refused" in result.error

    def test_head_unreliable_status_falls_back_to_get(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(requests, "head", lambda url, **kwargs: FakeResponse(status_code=405, url=url))
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: FakeResponse(status_code=200, url=url))
        result = check_link("https://example.com/")
        assert result.status_code == 200


class TestCheckLinks:
    def test_checks_all_urls_in_order(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(requests, "head", lambda url, **kwargs: FakeResponse(status_code=200, url=url))
        results = check_links(["https://example.com/a", "https://example.com/b"])
        assert [r.url for r in results] == ["https://example.com/a", "https://example.com/b"]


class TestExtractLinksFromHtml:
    def test_extracts_absolute_and_relative_links(self) -> None:
        html = '<a href="/about">About</a><a href="https://example.com/blog">Blog</a>'
        links = extract_links_from_html(html, base_url="https://example.com/")
        assert links == ["https://example.com/about", "https://example.com/blog"]

    def test_excludes_fragment_mailto_tel_javascript(self) -> None:
        html = (
            '<a href="#top">Top</a>'
            '<a href="mailto:hi@example.com">Email</a>'
            '<a href="tel:+1234567890">Call</a>'
            '<a href="javascript:void(0)">JS</a>'
            '<a href="/real-page">Real</a>'
        )
        links = extract_links_from_html(html, base_url="https://example.com/")
        assert links == ["https://example.com/real-page"]

    def test_no_base_url_keeps_href_as_authored(self) -> None:
        html = '<a href="/about">About</a>'
        assert extract_links_from_html(html) == ["/about"]

    def test_no_links_returns_empty_list(self) -> None:
        assert extract_links_from_html("<p>No links here.</p>") == []


class TestFormatReport:
    def test_reports_broken_and_redirected_separately(self) -> None:
        results = [
            LinkCheckResult(url="https://example.com/ok", status_code=200),
            LinkCheckResult(url="https://example.com/gone", status_code=404),
            LinkCheckResult(
                url="https://example.com/old", status_code=200, final_url="https://example.com/new", redirected=True
            ),
        ]
        report = format_report(results)
        assert "Broken links (1)" in report
        assert "Redirected links (1)" in report
        assert "1 link(s) OK, 1 redirected, 1 broken." in report

    def test_all_ok_report(self) -> None:
        results = [LinkCheckResult(url="https://example.com/", status_code=200)]
        report = format_report(results)
        assert "Broken links" not in report
        assert "Redirected links" not in report
