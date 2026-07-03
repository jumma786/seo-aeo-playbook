"""Unit tests for scripts.internal_linker."""

from __future__ import annotations

from scripts.internal_linker import (
    LinkSuggestion,
    Page,
    find_orphan_pages,
    format_report,
    suggest_internal_links,
)


class TestPageAnchorCandidates:
    def test_includes_title_and_keywords_sorted_longest_first(self) -> None:
        page = Page(url="/cwv", title="Core Web Vitals", keywords=["CWV", "performance metrics"])
        candidates = page.anchor_candidates()
        assert candidates == sorted(candidates, key=len, reverse=True)
        assert set(candidates) == {"Core Web Vitals", "performance metrics", "CWV"}

    def test_short_keywords_excluded(self) -> None:
        page = Page(url="/x", title="AI", keywords=["ok"])
        assert page.anchor_candidates() == []


class TestSuggestInternalLinks:
    def test_suggests_link_when_title_mentioned_in_body(self) -> None:
        pages = [
            Page(url="/guide", title="SEO Guide", body="Read our Core Web Vitals guide for details."),
            Page(url="/cwv", title="Core Web Vitals", body="An overview of Core Web Vitals."),
        ]
        suggestions = suggest_internal_links(pages)
        assert LinkSuggestion(source_url="/guide", target_url="/cwv", anchor_text="Core Web Vitals") in suggestions

    def test_no_self_links(self) -> None:
        pages = [Page(url="/a", title="Alpha Topic", body="Alpha Topic is discussed here.")]
        assert suggest_internal_links(pages) == []

    def test_existing_link_not_resuggested(self) -> None:
        pages = [
            Page(url="/guide", title="SEO Guide", body="See Core Web Vitals.", links_to={"/cwv"}),
            Page(url="/cwv", title="Core Web Vitals", body=""),
        ]
        assert suggest_internal_links(pages) == []

    def test_no_mention_produces_no_suggestion(self) -> None:
        pages = [
            Page(url="/a", title="Alpha Topic", body="Nothing relevant here."),
            Page(url="/b", title="Beta Topic", body="Also nothing relevant."),
        ]
        assert suggest_internal_links(pages) == []

    def test_respects_max_suggestions_per_page(self) -> None:
        targets = [Page(url=f"/t{i}", title=f"Topic {i}", body="") for i in range(10)]
        body = " ".join(f"Topic {i}" for i in range(10))
        source = Page(url="/hub", title="Hub", body=body)
        suggestions = suggest_internal_links([source, *targets], max_suggestions_per_page=3)
        assert len(suggestions) == 3

    def test_uses_keyword_when_title_not_mentioned(self) -> None:
        pages = [
            Page(url="/guide", title="SEO Guide", body="Learn about performance metrics here."),
            Page(url="/cwv", title="Core Web Vitals", body="", keywords=["performance metrics"]),
        ]
        suggestions = suggest_internal_links(pages)
        assert suggestions == [LinkSuggestion(source_url="/guide", target_url="/cwv", anchor_text="performance metrics")]


class TestFindOrphanPages:
    def test_page_with_no_inbound_links_is_orphan(self) -> None:
        pages = [
            Page(url="/a", title="A", links_to={"/b"}),
            Page(url="/b", title="B"),
            Page(url="/c", title="C"),
        ]
        assert find_orphan_pages(pages) == ["/a", "/c"]

    def test_fully_linked_site_has_no_orphans(self) -> None:
        pages = [
            Page(url="/a", title="A", links_to={"/b"}),
            Page(url="/b", title="B", links_to={"/a"}),
        ]
        assert find_orphan_pages(pages) == []


class TestFormatReport:
    def test_report_lists_orphans_and_suggestions(self) -> None:
        pages = [
            Page(url="/guide", title="SEO Guide", body="See Core Web Vitals."),
            Page(url="/cwv", title="Core Web Vitals", body=""),
        ]
        suggestions = suggest_internal_links(pages)
        report = format_report(pages, suggestions)
        assert "Orphan pages" in report
        assert "/cwv" in report
        assert "/guide -> /cwv" in report

    def test_no_orphans_omits_section(self) -> None:
        pages = [
            Page(url="/a", title="A", links_to={"/b"}),
            Page(url="/b", title="B", links_to={"/a"}),
        ]
        report = format_report(pages, [])
        assert "Orphan pages" not in report
