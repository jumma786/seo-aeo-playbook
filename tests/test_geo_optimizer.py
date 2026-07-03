"""Unit tests for scripts.geo_optimizer."""

from __future__ import annotations

from scripts.geo_optimizer import (
    MAX_PASSAGE_WORDS,
    MIN_PASSAGE_WORDS,
    extract_passages_from_html,
    format_report,
    score_content,
    score_passage,
    split_into_passages,
)

GOOD_PASSAGE = (
    "Core Web Vitals is a set of three metrics — LCP, INP, and CLS — introduced by Google in 2020 "
    "to measure loading speed, responsiveness, and visual stability. A page should aim for an LCP "
    "of 2.5 seconds or less to be classified as good."
)


class TestScorePassage:
    def test_well_formed_passage_is_self_contained(self) -> None:
        result = score_passage(GOOD_PASSAGE)
        assert result.self_contained is True
        assert result.issues == []

    def test_dangling_pronoun_opener_flagged(self) -> None:
        result = score_passage("It is a metric that measures loading speed and matters for rankings overall.")
        assert result.self_contained is False
        assert any("pronoun" in issue for issue in result.issues)

    def test_short_passage_flagged(self) -> None:
        result = score_passage("SEO matters.")
        assert result.word_count < MIN_PASSAGE_WORDS
        assert any(f">= {MIN_PASSAGE_WORDS}" in issue for issue in result.issues)

    def test_long_passage_flagged(self) -> None:
        text = "Example Corp " + ("word " * (MAX_PASSAGE_WORDS + 10))
        result = score_passage(text)
        assert result.word_count > MAX_PASSAGE_WORDS
        assert any(f"<= {MAX_PASSAGE_WORDS}" in issue for issue in result.issues)

    def test_specific_fact_detected(self) -> None:
        result = score_passage(GOOD_PASSAGE)
        assert result.has_specific_fact is True

    def test_no_specific_fact_flagged(self) -> None:
        result = score_passage(
            "SEO is the practice of optimizing a website so it appears in search results more often over time."
        )
        assert result.has_specific_fact is False
        assert any("no specific" in issue for issue in result.issues)

    def test_structural_label_detected(self) -> None:
        result = score_passage(
            "Definition: Core Web Vitals is a set of metrics that measure real-world page experience quality for users."
        )
        assert result.has_structural_label is True

    def test_empty_passage(self) -> None:
        result = score_passage("")
        assert result.word_count == 0
        assert result.self_contained is True  # no pronoun opener since there are no words


class TestPassageScoreScore:
    def test_ideal_passage_scores_100(self) -> None:
        text = "Definition: " + GOOD_PASSAGE
        result = score_passage(text)
        assert result.score == 100.0

    def test_worst_case_scores_low(self) -> None:
        result = score_passage("It works.")
        assert result.score < 50.0


class TestSplitIntoPassages:
    def test_splits_on_blank_lines(self) -> None:
        text = "First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here."
        assert split_into_passages(text) == ["First paragraph here.", "Second paragraph here.", "Third paragraph here."]

    def test_empty_text_returns_no_passages(self) -> None:
        assert split_into_passages("") == []

    def test_single_paragraph(self) -> None:
        assert split_into_passages("Just one paragraph.") == ["Just one paragraph."]


class TestExtractPassagesFromHtml:
    def test_extracts_paragraph_text(self) -> None:
        html = "<html><body><p>First paragraph.</p><p>Second paragraph.</p></body></html>"
        assert extract_passages_from_html(html) == ["First paragraph.", "Second paragraph."]

    def test_empty_paragraphs_excluded(self) -> None:
        html = "<html><body><p></p><p>Real content here.</p></body></html>"
        assert extract_passages_from_html(html) == ["Real content here."]

    def test_no_paragraphs_returns_empty(self) -> None:
        assert extract_passages_from_html("<html><body><div>No p tags</div></body></html>") == []


class TestScoreContent:
    def test_scores_all_passages_in_order(self) -> None:
        scores = score_content(["First passage.", "Second passage."])
        assert [s.text for s in scores] == ["First passage.", "Second passage."]

    def test_empty_passages_returns_empty(self) -> None:
        assert score_content([]) == []


class TestFormatReport:
    def test_report_includes_average_and_per_passage_scores(self) -> None:
        scores = score_content([GOOD_PASSAGE])
        report = format_report(scores)
        assert "GEO Citability Report" in report
        assert "Passage 1:" in report

    def test_empty_scores_report(self) -> None:
        report = format_report([])
        assert "0 passage(s)" in report
