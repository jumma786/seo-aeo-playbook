"""Unit tests for scripts.entity_extractor."""

from __future__ import annotations

from scripts.entity_extractor import (
    EntityMention,
    EntityType,
    compute_salience,
    extract_entities,
    find_entity_gaps,
    format_report,
)


class TestExtractEntities:
    def test_finds_person_organization_and_date(self) -> None:
        mentions = extract_entities("Jane Doe joined Example Corp as CEO in 2024.")
        by_text = {m.text: m for m in mentions}
        assert by_text["Jane Doe"].entity_type == EntityType.PERSON
        assert by_text["Example Corp"].entity_type == EntityType.ORGANIZATION
        assert by_text["2024"].entity_type == EntityType.DATE

    def test_sentence_initial_common_word_not_treated_as_entity(self) -> None:
        mentions = extract_entities("The Beatles played their final concert in 1969.")
        texts = {m.text for m in mentions}
        assert "The" not in texts
        assert "Beatles" in texts
        assert "1969" in texts

    def test_repeated_mentions_counted(self) -> None:
        mentions = extract_entities("Example Corp launched a product. Example Corp is based in Boston.")
        by_text = {m.text: m for m in mentions}
        assert by_text["Example Corp"].count == 2

    def test_acronym_classified_as_organization(self) -> None:
        mentions = extract_entities("NASA launched a new satellite.")
        by_text = {m.text: m for m in mentions}
        assert by_text["NASA"].entity_type == EntityType.ORGANIZATION

    def test_empty_text_returns_no_mentions(self) -> None:
        assert extract_entities("") == []

    def test_no_entities_in_lowercase_text(self) -> None:
        assert extract_entities("this sentence has no proper nouns at all.") == []

    def test_results_sorted_by_count_descending(self) -> None:
        mentions = extract_entities("Example Corp. Example Corp. Example Corp. TrailCo.")
        assert mentions[0].text == "Example Corp"
        assert mentions[0].count == 3


class TestComputeSalience:
    def test_salience_sums_to_one(self) -> None:
        mentions = [
            EntityMention(text="Example Corp", entity_type=EntityType.ORGANIZATION, count=3),
            EntityMention(text="Jane Doe", entity_type=EntityType.PERSON, count=1),
        ]
        salience = compute_salience(mentions)
        assert salience["Example Corp"] == 0.75
        assert salience["Jane Doe"] == 0.25

    def test_empty_mentions_returns_empty_dict(self) -> None:
        assert compute_salience([]) == {}


class TestFindEntityGaps:
    def test_finds_competitor_only_entities(self) -> None:
        own = [EntityMention(text="Example Corp", entity_type=EntityType.ORGANIZATION, count=1)]
        competitor = [
            EntityMention(text="Example Corp", entity_type=EntityType.ORGANIZATION, count=1),
            EntityMention(text="TrailCo", entity_type=EntityType.UNKNOWN, count=1),
        ]
        assert find_entity_gaps(own, competitor) == ["TrailCo"]

    def test_case_insensitive_matching(self) -> None:
        own = [EntityMention(text="example corp", entity_type=EntityType.ORGANIZATION, count=1)]
        competitor = [EntityMention(text="Example Corp", entity_type=EntityType.ORGANIZATION, count=1)]
        assert find_entity_gaps(own, competitor) == []

    def test_no_gaps_returns_empty_list(self) -> None:
        mentions = [EntityMention(text="Example Corp", entity_type=EntityType.ORGANIZATION, count=1)]
        assert find_entity_gaps(mentions, mentions) == []

    def test_duplicate_competitor_gaps_deduplicated(self) -> None:
        own: list[EntityMention] = []
        competitor = [
            EntityMention(text="TrailCo", entity_type=EntityType.UNKNOWN, count=1),
            EntityMention(text="TrailCo", entity_type=EntityType.UNKNOWN, count=1),
        ]
        assert find_entity_gaps(own, competitor) == ["TrailCo"]


class TestFormatReport:
    def test_report_includes_count_and_salience(self) -> None:
        mentions = extract_entities("Example Corp launched a product.")
        report = format_report(mentions)
        assert "Example Corp" in report
        assert "salience" in report
        assert "1 distinct entities" in report

    def test_empty_mentions_report(self) -> None:
        report = format_report([])
        assert "0 distinct entities" in report
