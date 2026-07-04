"""Unit tests for scripts.generate_readme."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_readme import RelatedBook, generate_readme, related_books_from_dict

SAMPLE_CHAPTER = """# Chapter 1: Example Chapter

**Version:** 1.0

---

# Table of Contents

1. Intro

---

# 1. Intro

An example chapter used only for testing generate_readme. More text follows here.
"""


@pytest.fixture
def book_dir(tmp_path: Path) -> Path:
    (tmp_path / "chapter-01.md").write_text(SAMPLE_CHAPTER, encoding="utf-8")
    return tmp_path


class TestGenerateReadme:
    def test_basic_structure(self, book_dir: Path) -> None:
        readme = generate_readme("The Example Book", "A short description of the book.", book_dir)
        assert readme.startswith("# The Example Book")
        assert "A short description of the book." in readme
        assert "## Table of Contents" in readme
        assert "chapter-01.md" in readme
        assert "## License" in readme

    def test_related_books_section_included_when_present(self, book_dir: Path) -> None:
        related = [RelatedBook(title="Other Book", path="../other/README.md", description="A companion book.")]
        readme = generate_readme("The Example Book", "A description.", book_dir, related_books=related)
        assert "## Related Books" in readme
        assert "[Other Book](../other/README.md) — A companion book." in readme

    def test_related_books_section_omitted_when_absent(self, book_dir: Path) -> None:
        readme = generate_readme("The Example Book", "A description.", book_dir)
        assert "## Related Books" not in readme

    def test_custom_license_path(self, book_dir: Path) -> None:
        readme = generate_readme("The Example Book", "A description.", book_dir, license_path="../LICENSE")
        assert "[LICENSE](../LICENSE)" in readme

    def test_blank_title_raises(self, book_dir: Path) -> None:
        with pytest.raises(ValueError):
            generate_readme("  ", "A description.", book_dir)

    def test_blank_description_raises(self, book_dir: Path) -> None:
        with pytest.raises(ValueError):
            generate_readme("The Example Book", "  ", book_dir)

    def test_no_chapters_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            generate_readme("The Example Book", "A description.", tmp_path)


class TestRelatedBooksFromDict:
    def test_builds_related_books(self) -> None:
        raw = [{"title": "Other Book", "path": "../other/README.md", "description": "A companion book."}]
        books = related_books_from_dict(raw)
        assert books == [RelatedBook(title="Other Book", path="../other/README.md", description="A companion book.")]

    def test_missing_key_raises(self) -> None:
        with pytest.raises(KeyError):
            related_books_from_dict([{"title": "Other Book"}])


class TestAgainstRealBooks:
    def test_reproduces_geo_readme_shape(self) -> None:
        real_dir = Path(__file__).resolve().parents[1] / "docs" / "books" / "complete" / "geo"
        if not real_dir.is_dir():
            pytest.skip("GEO book directory not present")
        readme = generate_readme(
            "The GEO Book",
            "A complete, practitioner-grade guide to Generative Engine Optimization.",
            real_dir,
            related_books=[
                RelatedBook(title="SEO Book", path="../seo/README.md", description="the foundational layer"),
            ],
        )
        assert readme.startswith("# The GEO Book")
        assert "chapter-08.md" in readme
        assert "## Related Books" in readme
