"""Unit tests for scripts.seo_audit."""

from __future__ import annotations

from scripts.seo_audit import (
    META_DESCRIPTION_MIN_LENGTH,
    THIN_CONTENT_WORD_THRESHOLD,
    TITLE_MIN_LENGTH,
    audit_html,
    format_report,
)


def _wrap_body(body: str, *, head_extra: str = "") -> str:
    filler = " ".join(["word"] * THIN_CONTENT_WORD_THRESHOLD)
    return f"""
    <html>
    <head>
        <title>{"A" * (TITLE_MIN_LENGTH + 5)}</title>
        <meta name="description" content="{"d" * (META_DESCRIPTION_MIN_LENGTH + 5)}">
        <link rel="canonical" href="https://example.com/page">
        {head_extra}
    </head>
    <body>
        <h1>Heading</h1>
        {body}
        <p>{filler}</p>
    </body>
    </html>
    """


class TestCleanPage:
    def test_well_formed_page_has_no_errors(self) -> None:
        html = _wrap_body('<img src="a.jpg" alt="descriptive text">')
        result = audit_html(html, url="https://example.com/page")
        errors = [i for i in result.issues if i.severity == "error"]
        assert errors == []

    def test_score_is_high_for_clean_page(self) -> None:
        html = _wrap_body('<img src="a.jpg" alt="descriptive text">')
        result = audit_html(html, url="https://example.com/page")
        assert result.score >= 90.0


class TestTitleChecks:
    def test_missing_title_is_error(self) -> None:
        html = "<html><head></head><body><h1>H</h1><p>text</p></body></html>"
        result = audit_html(html)
        assert any(i.category == "title" and i.severity == "error" for i in result.issues)

    def test_short_title_is_warning(self) -> None:
        html = "<html><head><title>Short</title></head><body><h1>H</h1></body></html>"
        result = audit_html(html)
        assert any(i.category == "title" and i.severity == "warning" for i in result.issues)
        assert result.title == "Short"


class TestMetaDescriptionChecks:
    def test_missing_meta_description_is_error(self) -> None:
        html = "<html><head><title>A perfectly reasonable page title here</title></head><body></body></html>"
        result = audit_html(html)
        assert any(i.category == "meta_description" and i.severity == "error" for i in result.issues)

    def test_too_long_meta_description_is_warning(self) -> None:
        long_desc = "d" * 200
        html = f"""<html><head><title>A perfectly reasonable page title here</title>
        <meta name="description" content="{long_desc}"></head><body></body></html>"""
        result = audit_html(html)
        assert any(i.category == "meta_description" and i.severity == "warning" for i in result.issues)


class TestHeadingChecks:
    def test_missing_h1_is_error(self) -> None:
        html = "<html><head><title>Title long enough here</title></head><body><p>text</p></body></html>"
        result = audit_html(html)
        assert result.h1_count == 0
        assert any(i.category == "headings" and i.severity == "error" for i in result.issues)

    def test_multiple_h1_is_warning(self) -> None:
        html = _wrap_body("<h1>Second heading</h1>")
        result = audit_html(html)
        assert result.h1_count == 2
        assert any(i.category == "headings" and i.severity == "warning" for i in result.issues)


class TestImageChecks:
    def test_missing_alt_text_flagged(self) -> None:
        html = _wrap_body('<img src="a.jpg"><img src="b.jpg" alt="">')
        result = audit_html(html)
        assert result.images_missing_alt == 2
        assert any(i.category == "images" for i in result.issues)

    def test_all_images_with_alt_not_flagged(self) -> None:
        html = _wrap_body('<img src="a.jpg" alt="a"><img src="b.jpg" alt="b">')
        result = audit_html(html)
        assert result.images_missing_alt == 0


class TestCanonicalAndRobots:
    def test_missing_canonical_flagged(self) -> None:
        html = "<html><head><title>Title long enough here for checks</title></head><body><h1>H</h1></body></html>"
        result = audit_html(html)
        assert result.has_canonical is False
        assert any(i.category == "canonical" for i in result.issues)

    def test_noindex_flagged(self) -> None:
        html = _wrap_body("", head_extra='<meta name="robots" content="noindex, follow">')
        result = audit_html(html)
        assert result.is_noindex is True
        assert any(i.category == "indexability" for i in result.issues)


class TestLinkClassification:
    def test_internal_and_external_links_classified(self) -> None:
        body = (
            '<a href="https://example.com/other-page">internal</a>'
            '<a href="/relative-path">internal relative</a>'
            '<a href="https://otherdomain.com/page">external</a>'
            '<a href="#section">anchor ignored</a>'
        )
        html = _wrap_body(body)
        result = audit_html(html, url="https://example.com/page")
        assert result.internal_link_count == 2
        assert result.external_link_count == 1

    def test_no_internal_links_flagged(self) -> None:
        html = _wrap_body('<a href="https://otherdomain.com/page">external only</a>')
        result = audit_html(html, url="https://example.com/page")
        assert any(i.category == "internal_links" for i in result.issues)


class TestThinContent:
    def test_thin_content_flagged(self) -> None:
        html = """<html><head><title>Title long enough here for checks</title>
        <meta name="description" content="A description that is definitely long enough to pass the check here.">
        <link rel="canonical" href="https://example.com/p"></head>
        <body><h1>H</h1><p>Too short.</p></body></html>"""
        result = audit_html(html)
        assert result.word_count < THIN_CONTENT_WORD_THRESHOLD
        assert any(i.category == "content" for i in result.issues)


class TestReportFormatting:
    def test_format_report_contains_score_and_url(self) -> None:
        html = _wrap_body('<img src="a.jpg" alt="descriptive text">')
        result = audit_html(html, url="https://example.com/page")
        report = format_report(result)
        assert "https://example.com/page" in report
        assert "Score:" in report
