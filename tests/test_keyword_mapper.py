"""Unit tests for scripts.keyword_mapper."""

from __future__ import annotations

from scripts.keyword_mapper import (
    KeywordMapping,
    find_cannibalization,
    format_cannibalization_report,
    format_mapping_report,
    map_keywords_to_urls,
    mappings_from_dict,
    suggest_url_for_keyword,
    unmapped_keywords,
)


class TestFindCannibalization:
    def test_keyword_with_two_urls_flagged(self) -> None:
        mappings = [
            KeywordMapping(keyword="running shoes", url="/running-shoes"),
            KeywordMapping(keyword="running shoes", url="/best-running-shoes"),
        ]
        issues = find_cannibalization(mappings)
        assert len(issues) == 1
        assert issues[0].keyword == "running shoes"
        assert set(issues[0].urls) == {"/running-shoes", "/best-running-shoes"}

    def test_case_insensitive_matching(self) -> None:
        mappings = [
            KeywordMapping(keyword="Running Shoes", url="/a"),
            KeywordMapping(keyword="running shoes", url="/b"),
        ]
        assert len(find_cannibalization(mappings)) == 1

    def test_same_keyword_same_url_not_flagged(self) -> None:
        mappings = [
            KeywordMapping(keyword="running shoes", url="/a"),
            KeywordMapping(keyword="running shoes", url="/a"),
        ]
        assert find_cannibalization(mappings) == []

    def test_no_overlap_no_issues(self) -> None:
        mappings = [
            KeywordMapping(keyword="running shoes", url="/a"),
            KeywordMapping(keyword="trail shoes", url="/b"),
        ]
        assert find_cannibalization(mappings) == []

    def test_empty_mappings(self) -> None:
        assert find_cannibalization([]) == []


class TestSuggestUrlForKeyword:
    def test_matches_best_page(self) -> None:
        pages = {"/cwv": "Core Web Vitals Guide", "/faq": "Frequently Asked Questions"}
        assert suggest_url_for_keyword("core web vitals", pages) == "/cwv"

    def test_no_match_returns_none(self) -> None:
        pages = {"/faq": "Frequently Asked Questions"}
        assert suggest_url_for_keyword("core web vitals", pages) is None

    def test_empty_pages_returns_none(self) -> None:
        assert suggest_url_for_keyword("core web vitals", {}) is None


class TestMapKeywordsToUrls:
    def test_maps_matching_keywords_only(self) -> None:
        pages = {"/cwv": "Core Web Vitals Guide"}
        mappings = map_keywords_to_urls(["core web vitals", "totally unrelated topic"], pages)
        assert len(mappings) == 1
        assert mappings[0].keyword == "core web vitals"
        assert mappings[0].url == "/cwv"


class TestUnmappedKeywords:
    def test_finds_keywords_without_mapping(self) -> None:
        mappings = [KeywordMapping(keyword="core web vitals", url="/cwv")]
        result = unmapped_keywords(["core web vitals", "schema markup"], mappings)
        assert result == ["schema markup"]

    def test_case_insensitive(self) -> None:
        mappings = [KeywordMapping(keyword="Core Web Vitals", url="/cwv")]
        assert unmapped_keywords(["core web vitals"], mappings) == []

    def test_all_mapped_returns_empty(self) -> None:
        mappings = [KeywordMapping(keyword="a", url="/a")]
        assert unmapped_keywords(["a"], mappings) == []


class TestMappingsFromDict:
    def test_builds_mappings(self) -> None:
        raw = [{"keyword": "running shoes", "url": "/running-shoes"}]
        mappings = mappings_from_dict(raw)
        assert mappings == [KeywordMapping(keyword="running shoes", url="/running-shoes")]

    def test_missing_key_raises(self) -> None:
        import pytest

        with pytest.raises(KeyError):
            mappings_from_dict([{"keyword": "running shoes"}])


class TestFormatReports:
    def test_cannibalization_report_lists_urls(self) -> None:
        issues = find_cannibalization(
            [KeywordMapping(keyword="running shoes", url="/a"), KeywordMapping(keyword="running shoes", url="/b")]
        )
        report = format_cannibalization_report(issues)
        assert "running shoes" in report
        assert "/a" in report
        assert "/b" in report

    def test_mapping_report_lists_unmapped(self) -> None:
        mappings = [KeywordMapping(keyword="core web vitals", url="/cwv")]
        report = format_mapping_report(mappings, ["schema markup"])
        assert "core web vitals" in report
        assert "Unmapped keywords" in report
        assert "schema markup" in report

    def test_mapping_report_no_unmapped_section_when_none(self) -> None:
        mappings = [KeywordMapping(keyword="core web vitals", url="/cwv")]
        report = format_mapping_report(mappings, [])
        assert "Unmapped keywords" not in report
