"""Unit tests for scripts.content_brief."""

from __future__ import annotations

import pytest

from scripts.content_brief import (
    MIN_SECTION_WORD_COUNT,
    generate_content_brief,
    format_brief,
)


class TestGenerateContentBrief:
    def test_basic_brief_has_expected_primary_keyword(self) -> None:
        brief = generate_content_brief("core web vitals", ["largest contentful paint guide"])
        assert brief.primary_keyword == "core web vitals"

    def test_sections_built_from_clusters(self) -> None:
        brief = generate_content_brief(
            "core web vitals",
            ["largest contentful paint guide", "measuring largest contentful paint", "cumulative layout shift guide"],
        )
        assert len(brief.sections) >= 1
        all_keywords = {kw for section in brief.sections for kw in section.keywords}
        assert "largest contentful paint guide" in all_keywords

    def test_section_word_counts_sum_close_to_body_target(self) -> None:
        brief = generate_content_brief(
            "core web vitals",
            ["largest contentful paint guide", "cumulative layout shift guide"],
            target_word_count=1000,
        )
        total_section_words = sum(section.target_word_count for section in brief.sections)
        assert total_section_words <= 1000

    def test_no_related_keywords_produces_no_sections(self) -> None:
        brief = generate_content_brief("core web vitals", [])
        assert brief.sections == []

    def test_questions_and_entities_passed_through(self) -> None:
        brief = generate_content_brief(
            "core web vitals",
            [],
            questions=["What is LCP?"],
            entities=["Google"],
        )
        assert brief.questions_to_answer == ["What is LCP?"]
        assert brief.entities_to_mention == ["Google"]

    def test_blank_primary_keyword_raises(self) -> None:
        with pytest.raises(ValueError):
            generate_content_brief("  ", [])

    def test_non_positive_word_count_raises(self) -> None:
        with pytest.raises(ValueError):
            generate_content_brief("core web vitals", [], target_word_count=0)

    def test_small_cluster_gets_minimum_word_count(self) -> None:
        brief = generate_content_brief("core web vitals", ["one unique topic"], target_word_count=200)
        assert brief.sections[0].target_word_count >= MIN_SECTION_WORD_COUNT


class TestFormatBrief:
    def test_includes_title_and_meta_guidance(self) -> None:
        brief = generate_content_brief("core web vitals", ["largest contentful paint guide"])
        report = format_brief(brief)
        assert "Title guidance" in report
        assert "Meta description guidance" in report
        assert "core web vitals" in report

    def test_includes_questions_section_when_present(self) -> None:
        brief = generate_content_brief("core web vitals", [], questions=["What is LCP?"])
        report = format_brief(brief)
        assert "Questions to Answer" in report
        assert "What is LCP?" in report

    def test_omits_questions_section_when_absent(self) -> None:
        brief = generate_content_brief("core web vitals", [])
        report = format_brief(brief)
        assert "Questions to Answer" not in report

    def test_includes_entities_section_when_present(self) -> None:
        brief = generate_content_brief("core web vitals", [], entities=["Google"])
        report = format_brief(brief)
        assert "Entities to Mention" in report
        assert "Google" in report
