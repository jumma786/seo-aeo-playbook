"""Unit tests for scripts.page_speed."""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import pytest
import requests

from scripts.page_speed import (
    GOOD_TTFB_SECONDS,
    POOR_TTFB_SECONDS,
    audit_html_performance,
    audit_url_performance,
    format_report,
)


class TestRenderBlockingScripts:
    def test_blocking_script_flagged(self) -> None:
        html = '<html><head><script src="a.js"></script></head><body></body></html>'
        result = audit_html_performance(html)
        assert result.render_blocking_scripts == 1
        assert any(issue.category == "render_blocking" and issue.severity == "error" for issue in result.issues)

    def test_async_script_not_flagged(self) -> None:
        html = '<html><head><script src="a.js" async></script></head><body></body></html>'
        result = audit_html_performance(html)
        assert result.render_blocking_scripts == 0

    def test_defer_script_not_flagged(self) -> None:
        html = '<html><head><script src="a.js" defer></script></head><body></body></html>'
        result = audit_html_performance(html)
        assert result.render_blocking_scripts == 0

    def test_inline_script_not_counted(self) -> None:
        html = "<html><head><script>console.log('hi');</script></head><body></body></html>"
        result = audit_html_performance(html)
        assert result.render_blocking_scripts == 0


class TestRenderBlockingStylesheets:
    def test_few_stylesheets_not_flagged(self) -> None:
        html = '<html><head><link rel="stylesheet" href="a.css"></head><body></body></html>'
        result = audit_html_performance(html)
        assert result.render_blocking_stylesheets == 1
        assert not any(issue.category == "render_blocking" for issue in result.issues)

    def test_many_stylesheets_flagged(self) -> None:
        links = "".join(f'<link rel="stylesheet" href="{i}.css">' for i in range(4))
        html = f"<html><head>{links}</head><body></body></html>"
        result = audit_html_performance(html)
        assert result.render_blocking_stylesheets == 4
        assert any(issue.category == "render_blocking" and issue.severity == "warning" for issue in result.issues)

    def test_print_media_stylesheet_not_counted(self) -> None:
        html = '<html><head><link rel="stylesheet" href="print.css" media="print"></head><body></body></html>'
        result = audit_html_performance(html)
        assert result.render_blocking_stylesheets == 0


class TestImages:
    def test_missing_dimensions_flagged(self) -> None:
        html = '<html><body><img src="a.jpg"></body></html>'
        result = audit_html_performance(html)
        assert result.images_missing_dimensions == 1
        assert any(issue.category == "cls" for issue in result.issues)

    def test_dimensions_present_not_flagged(self) -> None:
        html = '<html><body><img src="a.jpg" width="100" height="100"></body></html>'
        result = audit_html_performance(html)
        assert result.images_missing_dimensions == 0

    def test_lazy_loading_recommended_when_many_images(self) -> None:
        images = "".join(f'<img src="{i}.jpg" width="1" height="1">' for i in range(3))
        html = f"<html><body>{images}</body></html>"
        result = audit_html_performance(html)
        assert any(issue.category == "lazy_loading" for issue in result.issues)

    def test_lazy_loading_present_not_flagged(self) -> None:
        images = "".join(f'<img src="{i}.jpg" width="1" height="1" loading="lazy">' for i in range(3))
        html = f"<html><body>{images}</body></html>"
        result = audit_html_performance(html)
        assert result.lazy_loaded_images == 3
        assert not any(issue.category == "lazy_loading" for issue in result.issues)

    def test_few_images_no_lazy_loading_check(self) -> None:
        html = '<html><body><img src="a.jpg" width="1" height="1"></body></html>'
        result = audit_html_performance(html)
        assert not any(issue.category == "lazy_loading" for issue in result.issues)


class TestFonts:
    def test_google_fonts_without_display_swap_flagged(self) -> None:
        html = '<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto"></head></html>'
        result = audit_html_performance(html)
        assert any(issue.category == "fonts" for issue in result.issues)

    def test_google_fonts_with_display_swap_not_flagged(self) -> None:
        html = (
            '<html><head><link rel="stylesheet" '
            'href="https://fonts.googleapis.com/css2?family=Roboto&display=swap"></head></html>'
        )
        result = audit_html_performance(html)
        assert not any(issue.category == "fonts" for issue in result.issues)


class TestPageWeight:
    def test_large_html_flagged(self) -> None:
        html = "<html><body>" + ("a" * 200_000) + "</body></html>"
        result = audit_html_performance(html)
        assert any(issue.category == "page_weight" for issue in result.issues)

    def test_small_html_not_flagged(self) -> None:
        result = audit_html_performance("<html><body>hi</body></html>")
        assert not any(issue.category == "page_weight" for issue in result.issues)


class TestTtfb:
    def test_good_ttfb_not_flagged(self) -> None:
        result = audit_html_performance("<html></html>", ttfb_seconds=GOOD_TTFB_SECONDS - 0.1)
        assert not any(issue.category == "ttfb" for issue in result.issues)

    def test_needs_improvement_ttfb_is_warning(self) -> None:
        result = audit_html_performance("<html></html>", ttfb_seconds=GOOD_TTFB_SECONDS + 0.1)
        issue = next(issue for issue in result.issues if issue.category == "ttfb")
        assert issue.severity == "warning"

    def test_poor_ttfb_is_error(self) -> None:
        result = audit_html_performance("<html></html>", ttfb_seconds=POOR_TTFB_SECONDS + 0.1)
        issue = next(issue for issue in result.issues if issue.category == "ttfb")
        assert issue.severity == "error"

    def test_no_ttfb_measurement_skips_check(self) -> None:
        result = audit_html_performance("<html></html>")
        assert not any(issue.category == "ttfb" for issue in result.issues)


class TestScore:
    def test_clean_page_scores_high(self) -> None:
        html = '<html><head></head><body><img src="a.jpg" width="1" height="1"></body></html>'
        result = audit_html_performance(html)
        assert result.score == 100.0

    def test_score_never_negative(self) -> None:
        html = "".join(f'<script src="{i}.js"></script>' for i in range(50))
        result = audit_html_performance(f"<html><head>{html}</head></html>")
        assert result.score >= 0.0


class TestAuditUrlPerformance:
    def test_uses_response_elapsed_as_ttfb(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_response = SimpleNamespace(
            text="<html><body>hi</body></html>",
            elapsed=timedelta(seconds=0.42),
            raise_for_status=lambda: None,
        )
        monkeypatch.setattr(requests, "get", lambda url, **kwargs: fake_response)
        result = audit_url_performance("https://example.com/")
        assert result.ttfb_seconds == pytest.approx(0.42)
        assert result.url == "https://example.com/"


class TestFormatReport:
    def test_includes_score_and_ttfb(self) -> None:
        result = audit_html_performance("<html></html>", url="https://example.com/", ttfb_seconds=0.5)
        report = format_report(result)
        assert "Score:" in report
        assert "Time to first byte: 0.50s" in report
