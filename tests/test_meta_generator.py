"""Unit tests for scripts.meta_generator."""

from __future__ import annotations

import pytest

from scripts.meta_generator import (
    META_DESCRIPTION_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    generate_meta_description,
    generate_title,
    truncate_at_word_boundary,
    validate_meta_description,
    validate_title,
)


class TestTruncateAtWordBoundary:
    def test_short_text_unchanged(self) -> None:
        assert truncate_at_word_boundary("Short text", 50) == "Short text"

    def test_truncates_at_word_boundary_with_suffix(self) -> None:
        text = "The quick brown fox jumps over the lazy dog"
        result = truncate_at_word_boundary(text, 20)
        assert len(result) <= 20
        assert result.endswith("...")
        assert not result[:-3].endswith(" ")

    def test_never_exceeds_max_length(self) -> None:
        text = "a" * 200
        result = truncate_at_word_boundary(text, 50)
        assert len(result) <= 50

    def test_max_length_smaller_than_suffix_raises(self) -> None:
        with pytest.raises(ValueError):
            truncate_at_word_boundary("hello world", 2, suffix="...")

    def test_strips_trailing_punctuation_before_suffix(self) -> None:
        result = truncate_at_word_boundary("Hello, world, this is a test,", 15)
        assert not result.replace("...", "").endswith(",")


class TestGenerateTitle:
    def test_combines_page_title_and_brand(self) -> None:
        assert generate_title("Core Web Vitals", brand="Example Corp") == "Core Web Vitals | Example Corp"

    def test_drops_brand_when_combined_exceeds_max_length(self) -> None:
        long_title = "A" * (TITLE_MAX_LENGTH - 5)
        result = generate_title(long_title, brand="Example Corp")
        assert "Example Corp" not in result
        assert result == long_title

    def test_no_brand_returns_page_title(self) -> None:
        assert generate_title("Core Web Vitals") == "Core Web Vitals"

    def test_blank_title_raises(self) -> None:
        with pytest.raises(ValueError):
            generate_title("   ")

    def test_overlong_title_without_brand_is_truncated(self) -> None:
        long_title = "word " * 30
        result = generate_title(long_title)
        assert len(result) <= TITLE_MAX_LENGTH


class TestGenerateMetaDescription:
    def test_short_text_returned_unchanged(self) -> None:
        text = "A concise summary of the page content that fits comfortably within limits here today."
        assert generate_meta_description(text) == text

    def test_long_text_truncated(self) -> None:
        text = "word " * 60
        result = generate_meta_description(text)
        assert len(result) <= META_DESCRIPTION_MAX_LENGTH

    def test_blank_text_raises(self) -> None:
        with pytest.raises(ValueError):
            generate_meta_description("   ")


class TestValidateTitle:
    def test_empty_title(self) -> None:
        assert validate_title("") == ["Title is empty"]

    def test_too_short_title_warns(self) -> None:
        warnings = validate_title("Short")
        assert len(warnings) == 1
        assert "recommended >=" in warnings[0]

    def test_too_long_title_warns(self) -> None:
        warnings = validate_title("A" * 100)
        assert len(warnings) == 1
        assert "recommended <=" in warnings[0]

    def test_well_sized_title_has_no_warnings(self) -> None:
        assert validate_title("A" * 45) == []


class TestValidateMetaDescription:
    def test_empty_description(self) -> None:
        assert validate_meta_description("") == ["Meta description is empty"]

    def test_well_sized_description_has_no_warnings(self) -> None:
        assert validate_meta_description("A" * 100) == []

    def test_too_long_description_warns(self) -> None:
        warnings = validate_meta_description("A" * 200)
        assert len(warnings) == 1
