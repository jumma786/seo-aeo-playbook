"""Generate an ``llms.txt`` file per the llmstxt.org convention.

Follows the structure documented in
``docs/books/complete/aeo/chapter-08.md`` section 4: an H1 with the
site/project name, a 1-3 sentence blockquote summary, then H2-labeled
sections grouping links with short descriptions. A section named
``Optional`` signals lower-priority links an LLM can skip under context
constraints.

Example:
    >>> from scripts.llms_txt_generator import LlmsTxtLink, LlmsTxtSection, generate_llms_txt
    >>> sections = [
    ...     LlmsTxtSection(
    ...         heading="Documentation",
    ...         links=[LlmsTxtLink(title="Getting Started", url="https://example.com/docs", description="Setup steps")],
    ...     )
    ... ]
    >>> print(generate_llms_txt("Example Corp", "Example Corp builds SEO tools.", sections))
    # Example Corp
    <BLANKLINE>
    > Example Corp builds SEO tools.
    <BLANKLINE>
    ## Documentation
    <BLANKLINE>
    - [Getting Started](https://example.com/docs): Setup steps
    <BLANKLINE>
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class LlmsTxtValidationError(ValueError):
    """Raised when llms.txt content or structure is invalid."""


@dataclass
class LlmsTxtLink:
    """A single curated link entry within an llms.txt section."""

    title: str
    url: str
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise LlmsTxtValidationError("Link title must not be empty")
        if not self.url.strip():
            raise LlmsTxtValidationError("Link url must not be empty")

    def to_markdown(self) -> str:
        """Render this link as a single Markdown list item."""
        line = f"- [{self.title.strip()}]({self.url.strip()})"
        if self.description:
            line += f": {self.description.strip()}"
        return line


@dataclass
class LlmsTxtSection:
    """An H2-labeled group of links, e.g. "Documentation" or "Optional"."""

    heading: str
    links: list[LlmsTxtLink] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.heading.strip():
            raise LlmsTxtValidationError("Section heading must not be empty")
        if not self.links:
            raise LlmsTxtValidationError(f"Section {self.heading!r} must have at least one link")

    def to_markdown(self) -> str:
        """Render this section as an H2 heading followed by its link list."""
        lines = [f"## {self.heading.strip()}", ""]
        lines.extend(link.to_markdown() for link in self.links)
        return "\n".join(lines)


def generate_llms_txt(name: str, summary: str, sections: list[LlmsTxtSection]) -> str:
    """Render a complete llms.txt document.

    Args:
        name: The site or project name, rendered as the H1 heading.
        summary: A short (ideally 1-3 sentence) description of the site,
            rendered as a blockquote.
        sections: One or more :class:`LlmsTxtSection` groupings of curated links.

    Returns:
        The rendered llms.txt content as a Markdown string.

    Raises:
        LlmsTxtValidationError: If name or summary is blank, or sections is empty.
    """
    if not name.strip():
        raise LlmsTxtValidationError("name must not be empty")
    if not summary.strip():
        raise LlmsTxtValidationError("summary must not be empty")
    if not sections:
        raise LlmsTxtValidationError("At least one section is required")

    parts = [f"# {name.strip()}", "", f"> {summary.strip()}", ""]
    parts.append("\n\n".join(section.to_markdown() for section in sections))
    return "\n".join(parts).rstrip() + "\n"


def sections_from_dict(raw_sections: list[dict[str, Any]]) -> list[LlmsTxtSection]:
    """Build :class:`LlmsTxtSection` objects from parsed JSON/dict data.

    Args:
        raw_sections: A list of dicts, each with a ``heading`` string and a
            ``links`` list of dicts with ``title``, ``url``, and optional
            ``description`` keys.

    Returns:
        The corresponding list of :class:`LlmsTxtSection` objects.

    Raises:
        LlmsTxtValidationError: If any section or link is missing required fields.
    """
    sections = []
    for raw_section in raw_sections:
        links = [
            LlmsTxtLink(
                title=raw_link["title"],
                url=raw_link["url"],
                description=raw_link.get("description"),
            )
            for raw_link in raw_section.get("links", [])
        ]
        sections.append(LlmsTxtSection(heading=raw_section["heading"], links=links))
    return sections


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.llms_txt_generator spec.json output.txt``.

    The spec JSON file has the shape:
    ``{"name": "...", "summary": "...", "sections": [{"heading": "...", "links": [...]}]}``.
    """
    import argparse
    import json

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate an llms.txt file from a JSON spec.")
    parser.add_argument("spec_file", help="Path to a JSON spec file (name, summary, sections)")
    parser.add_argument("output_file", help="Path to write the generated llms.txt")
    args = parser.parse_args(argv)

    try:
        with open(args.spec_file, encoding="utf-8") as f:
            spec = json.load(f)
        sections = sections_from_dict(spec.get("sections", []))
        content = generate_llms_txt(spec["name"], spec["summary"], sections)
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(content)
    except (OSError, KeyError, LlmsTxtValidationError, json.JSONDecodeError) as exc:
        logging.error("llms.txt generation failed: %s", exc)
        return 1

    logging.info("Wrote llms.txt to %s", args.output_file)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
