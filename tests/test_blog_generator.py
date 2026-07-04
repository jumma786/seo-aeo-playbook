"""Unit tests for scripts.blog_generator."""

from __future__ import annotations

from scripts.blog_generator import BlogPostSpec, generate_blog_scaffold
from scripts.content_brief import generate_content_brief


def _make_spec(**overrides: object) -> BlogPostSpec:
    brief = generate_content_brief(
        "core web vitals",
        ["largest contentful paint guide", "cumulative layout shift guide"],
        target_word_count=1000,
        questions=overrides.pop("questions", None),
    )
    defaults = dict(
        title="Core Web Vitals Explained: A Complete Guide",
        slug="core-web-vitals-explained",
        author_name="Jane Doe",
        date_published="2026-01-15",
        brief=brief,
    )
    defaults.update(overrides)
    return BlogPostSpec(**defaults)


class TestGenerateBlogScaffold:
    def test_includes_frontmatter(self) -> None:
        scaffold = generate_blog_scaffold(_make_spec())
        assert scaffold.startswith("---\n")
        assert 'title: "Core Web Vitals Explained: A Complete Guide"' in scaffold
        assert "date: 2026-01-15" in scaffold
        assert "author: Jane Doe" in scaffold
        assert "slug: core-web-vitals-explained" in scaffold

    def test_includes_title_heading(self) -> None:
        scaffold = generate_blog_scaffold(_make_spec())
        assert "# Core Web Vitals Explained: A Complete Guide" in scaffold

    def test_includes_intro_todo(self) -> None:
        scaffold = generate_blog_scaffold(_make_spec())
        assert "TODO: Write your introduction" in scaffold

    def test_includes_section_outline_with_keywords(self) -> None:
        scaffold = generate_blog_scaffold(_make_spec())
        assert "largest contentful paint guide" in scaffold
        assert "## " in scaffold
        assert "words)" in scaffold

    def test_includes_faq_skeleton_when_questions_present(self) -> None:
        scaffold = generate_blog_scaffold(_make_spec(questions=["What is a good LCP score?"]))
        assert "## Frequently Asked Questions" in scaffold
        assert "### What is a good LCP score?" in scaffold

    def test_omits_faq_section_when_no_questions(self) -> None:
        scaffold = generate_blog_scaffold(_make_spec())
        assert "Frequently Asked Questions" not in scaffold

    def test_includes_article_schema(self) -> None:
        scaffold = generate_blog_scaffold(_make_spec())
        assert '<script type="application/ld+json">' in scaffold
        assert '"@type": "Article"' in scaffold
        assert "Jane Doe" in scaffold

    def test_no_fabricated_body_prose(self) -> None:
        scaffold = generate_blog_scaffold(_make_spec())
        # every section body is a TODO comment, not fabricated prose
        for section in scaffold.split("## ")[1:]:
            body = section.split("\n", 1)[1] if "\n" in section else ""
            if "Frequently Asked Questions" in section:
                continue
            assert "<!-- TODO" in body
