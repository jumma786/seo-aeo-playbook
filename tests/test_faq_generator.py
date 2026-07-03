"""Unit tests for scripts.faq_generator."""

from __future__ import annotations

import pytest

from scripts.faq_generator import (
    MAX_ANSWER_WORDS,
    MIN_ANSWER_WORDS,
    FaqItem,
    generate_faq_markdown,
    generate_faq_schema_tag,
    items_from_dict,
    validate_faq_item,
    validate_faq_items,
)

GOOD_ANSWER = "SEO is the practice of optimizing a website so it ranks higher in organic search engine results pages."


class TestValidateFaqItem:
    def test_well_formed_item_has_no_issues(self) -> None:
        item = FaqItem(question="What is SEO?", answer=GOOD_ANSWER)
        assert validate_faq_item(item) == []

    def test_question_without_question_mark_flagged(self) -> None:
        item = FaqItem(question="What is SEO", answer=GOOD_ANSWER)
        issues = validate_faq_item(item)
        assert any("end with" in issue.message for issue in issues)

    def test_question_not_starting_with_question_word_flagged(self) -> None:
        item = FaqItem(question="SEO explained?", answer=GOOD_ANSWER)
        issues = validate_faq_item(item)
        assert any("question word" in issue.message for issue in issues)

    def test_short_answer_flagged(self) -> None:
        item = FaqItem(question="What is SEO?", answer="Search engine optimization.")
        issues = validate_faq_item(item)
        assert any(f">= {MIN_ANSWER_WORDS}" in issue.message for issue in issues)

    def test_long_answer_flagged(self) -> None:
        item = FaqItem(question="What is SEO?", answer=" ".join(["word"] * (MAX_ANSWER_WORDS + 10)))
        issues = validate_faq_item(item)
        assert any(f"<= {MAX_ANSWER_WORDS}" in issue.message for issue in issues)

    def test_dangling_pronoun_opener_flagged(self) -> None:
        item = FaqItem(question="What is SEO?", answer="It is the practice of optimizing a website for search engines to find and rank well.")
        issues = validate_faq_item(item)
        assert any("dangling" in issue.message.lower() or "pronoun" in issue.message for issue in issues)

    def test_named_subject_opener_not_flagged(self) -> None:
        item = FaqItem(question="What is SEO?", answer=GOOD_ANSWER)
        issues = validate_faq_item(item)
        assert not any("pronoun" in issue.message for issue in issues)


class TestValidateFaqItems:
    def test_aggregates_issues_across_items(self) -> None:
        items = [
            FaqItem(question="What is SEO", answer=GOOD_ANSWER),
            FaqItem(question="What is AEO?", answer="Short."),
        ]
        issues = validate_faq_items(items)
        assert len(issues) >= 2


class TestGenerateFaqMarkdown:
    def test_renders_heading_and_qa(self) -> None:
        items = [FaqItem(question="What is SEO?", answer=GOOD_ANSWER)]
        markdown = generate_faq_markdown(items)
        assert markdown.startswith("## Frequently Asked Questions")
        assert "### What is SEO?" in markdown
        assert GOOD_ANSWER in markdown

    def test_custom_heading(self) -> None:
        items = [FaqItem(question="What is SEO?", answer=GOOD_ANSWER)]
        markdown = generate_faq_markdown(items, heading="Common Questions")
        assert markdown.startswith("## Common Questions")

    def test_empty_items_raises(self) -> None:
        with pytest.raises(ValueError):
            generate_faq_markdown([])

    def test_multiple_items_all_rendered(self) -> None:
        items = [
            FaqItem(question="What is SEO?", answer=GOOD_ANSWER),
            FaqItem(question="What is AEO?", answer=GOOD_ANSWER),
        ]
        markdown = generate_faq_markdown(items)
        assert markdown.count("### ") == 2


class TestGenerateFaqSchemaTag:
    def test_produces_script_tag(self) -> None:
        items = [FaqItem(question="What is SEO?", answer=GOOD_ANSWER)]
        tag = generate_faq_schema_tag(items)
        assert tag.startswith('<script type="application/ld+json">')
        assert "FAQPage" in tag
        assert "What is SEO?" in tag

    def test_empty_items_raises(self) -> None:
        from scripts.schema_generator import SchemaValidationError

        with pytest.raises(SchemaValidationError):
            generate_faq_schema_tag([])


class TestItemsFromDict:
    def test_builds_items(self) -> None:
        raw = [{"question": "What is SEO?", "answer": GOOD_ANSWER}]
        items = items_from_dict(raw)
        assert items == [FaqItem(question="What is SEO?", answer=GOOD_ANSWER)]

    def test_missing_key_raises(self) -> None:
        with pytest.raises(KeyError):
            items_from_dict([{"question": "What is SEO?"}])
