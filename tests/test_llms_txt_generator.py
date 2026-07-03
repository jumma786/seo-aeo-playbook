"""Unit tests for scripts.llms_txt_generator."""

from __future__ import annotations

import pytest

from scripts.llms_txt_generator import (
    LlmsTxtLink,
    LlmsTxtSection,
    LlmsTxtValidationError,
    generate_llms_txt,
    sections_from_dict,
)


class TestLlmsTxtLink:
    def test_renders_with_description(self) -> None:
        link = LlmsTxtLink(title="Getting Started", url="https://example.com/docs", description="Setup steps")
        assert link.to_markdown() == "- [Getting Started](https://example.com/docs): Setup steps"

    def test_renders_without_description(self) -> None:
        link = LlmsTxtLink(title="Blog", url="https://example.com/blog")
        assert link.to_markdown() == "- [Blog](https://example.com/blog)"

    def test_blank_title_raises(self) -> None:
        with pytest.raises(LlmsTxtValidationError):
            LlmsTxtLink(title="  ", url="https://example.com/")

    def test_blank_url_raises(self) -> None:
        with pytest.raises(LlmsTxtValidationError):
            LlmsTxtLink(title="Blog", url="  ")


class TestLlmsTxtSection:
    def test_renders_heading_and_links(self) -> None:
        section = LlmsTxtSection(
            heading="Documentation",
            links=[LlmsTxtLink(title="API Reference", url="https://example.com/api")],
        )
        markdown = section.to_markdown()
        assert markdown.startswith("## Documentation")
        assert "- [API Reference](https://example.com/api)" in markdown

    def test_blank_heading_raises(self) -> None:
        with pytest.raises(LlmsTxtValidationError):
            LlmsTxtSection(heading="  ", links=[LlmsTxtLink(title="A", url="https://example.com/")])

    def test_empty_links_raises(self) -> None:
        with pytest.raises(LlmsTxtValidationError):
            LlmsTxtSection(heading="Documentation", links=[])


class TestGenerateLlmsTxt:
    def test_full_document_structure(self) -> None:
        sections = [
            LlmsTxtSection(
                heading="Documentation",
                links=[LlmsTxtLink(title="Getting Started", url="https://example.com/docs", description="Setup steps")],
            ),
            LlmsTxtSection(
                heading="Optional",
                links=[LlmsTxtLink(title="Blog", url="https://example.com/blog")],
            ),
        ]
        content = generate_llms_txt("Example Corp", "Example Corp builds SEO tools.", sections)
        assert content.startswith("# Example Corp\n\n> Example Corp builds SEO tools.\n\n")
        assert "## Documentation" in content
        assert "## Optional" in content
        assert content.endswith("\n")
        assert not content.endswith("\n\n")

    def test_blank_name_raises(self) -> None:
        section = LlmsTxtSection(heading="Docs", links=[LlmsTxtLink(title="A", url="https://example.com/")])
        with pytest.raises(LlmsTxtValidationError):
            generate_llms_txt("  ", "A summary.", [section])

    def test_blank_summary_raises(self) -> None:
        section = LlmsTxtSection(heading="Docs", links=[LlmsTxtLink(title="A", url="https://example.com/")])
        with pytest.raises(LlmsTxtValidationError):
            generate_llms_txt("Example Corp", "  ", [section])

    def test_no_sections_raises(self) -> None:
        with pytest.raises(LlmsTxtValidationError):
            generate_llms_txt("Example Corp", "A summary.", [])


class TestSectionsFromDict:
    def test_builds_sections_and_links(self) -> None:
        raw = [
            {
                "heading": "Documentation",
                "links": [{"title": "Getting Started", "url": "https://example.com/docs", "description": "Setup"}],
            }
        ]
        sections = sections_from_dict(raw)
        assert len(sections) == 1
        assert sections[0].heading == "Documentation"
        assert sections[0].links[0].title == "Getting Started"

    def test_missing_link_title_raises_key_error(self) -> None:
        raw = [{"heading": "Documentation", "links": [{"url": "https://example.com/"}]}]
        with pytest.raises(KeyError):
            sections_from_dict(raw)
