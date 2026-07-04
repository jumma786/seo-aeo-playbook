"""Unit tests for scripts.generate_toc."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_toc import (
    ChapterParseError,
    generate_toc_from_directory,
    generate_toc_table,
    parse_chapter,
)

SAMPLE_CHAPTER = """# Chapter 1: Example Chapter

**Version:** 1.0

---

# Table of Contents

1. Intro
2. Summary

---

# 1. Intro

This chapter covers the basics of the topic. More detail follows in later sections.

---

# 2. Summary

Recap goes here.
"""


class TestParseChapter:
    def test_extracts_number_and_title(self) -> None:
        info = parse_chapter(SAMPLE_CHAPTER, filename="chapter-01.md")
        assert info.number == 1
        assert info.title == "Example Chapter"
        assert info.filename == "chapter-01.md"

    def test_extracts_focus_from_first_sentence(self) -> None:
        info = parse_chapter(SAMPLE_CHAPTER, filename="chapter-01.md")
        assert info.focus == "This chapter covers the basics of the topic."

    def test_missing_title_heading_raises(self) -> None:
        with pytest.raises(ChapterParseError):
            parse_chapter("No title heading here.\n\nSome text.", filename="chapter-99.md")

    def test_double_digit_chapter_number(self) -> None:
        text = SAMPLE_CHAPTER.replace("Chapter 1:", "Chapter 14:")
        info = parse_chapter(text, filename="chapter-14.md")
        assert info.number == 14

    def test_missing_content_section_produces_empty_focus(self) -> None:
        text = "# Chapter 1: Example Chapter\n\n**Version:** 1.0\n\n---\n\n# Table of Contents\n"
        info = parse_chapter(text, filename="chapter-01.md")
        assert info.focus == ""


class TestGenerateTocTable:
    def test_renders_header_and_rows_sorted_by_number(self) -> None:
        chapters = [
            parse_chapter(SAMPLE_CHAPTER.replace("Chapter 1:", "Chapter 2:"), filename="chapter-02.md"),
            parse_chapter(SAMPLE_CHAPTER, filename="chapter-01.md"),
        ]
        table = generate_toc_table(chapters)
        lines = table.splitlines()
        assert lines[0] == "| # | Chapter | Focus |"
        assert "chapter-01.md" in lines[2]
        assert "chapter-02.md" in lines[3]

    def test_empty_chapters_raises(self) -> None:
        with pytest.raises(ValueError):
            generate_toc_table([])


class TestGenerateTocFromDirectory:
    def test_parses_all_chapter_files(self, tmp_path: Path) -> None:
        (tmp_path / "chapter-01.md").write_text(SAMPLE_CHAPTER, encoding="utf-8")
        (tmp_path / "chapter-02.md").write_text(SAMPLE_CHAPTER.replace("Chapter 1:", "Chapter 2:"), encoding="utf-8")
        table = generate_toc_from_directory(tmp_path)
        assert table.count("| [") == 2

    def test_no_chapter_files_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            generate_toc_from_directory(tmp_path)

    def test_against_real_geo_book(self) -> None:
        real_dir = Path(__file__).resolve().parents[1] / "docs" / "books" / "complete" / "geo"
        if not real_dir.is_dir():
            pytest.skip("GEO book directory not present")
        table = generate_toc_from_directory(real_dir)
        assert "| 1 | [Introduction to Generative Engine Optimization](chapter-01.md) |" in table
        assert table.count("\n") == 9  # 10 lines (header + separator + 8 chapters) joined by 9 newlines
