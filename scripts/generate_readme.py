"""Generate a book's README.md from its chapter files.

Assembles the README.md format already used by hand for the SEO, AEO, and
GEO books (see ``docs/books/complete/{seo,aeo,geo}/README.md``): a title,
a one-paragraph description, a table of contents (reusing
``scripts.generate_toc``), an optional "Related Books" section, and a
closing License line.

Example:
    >>> from scripts.generate_readme import generate_readme
    >>> import tempfile, os
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     _ = open(os.path.join(tmp, "chapter-01.md"), "w", encoding="utf-8").write(
    ...         "# Chapter 1: Example\\n\\n**Version:** 1.0\\n\\n---\\n\\n# Table of Contents\\n\\n---\\n\\n"
    ...         "# 1. Intro\\n\\nAn example chapter for doctest purposes only. More text follows.\\n"
    ...     )
    ...     readme = generate_readme("The Example Book", "A short description.", tmp)
    >>> readme.startswith("# The Example Book")
    True
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from scripts.generate_toc import generate_toc_from_directory

logger = logging.getLogger(__name__)

DEFAULT_LICENSE_PATH = "../../../../LICENSE"


@dataclass
class RelatedBook:
    """A cross-linked book entry for the README's "Related Books" section."""

    title: str
    path: str
    description: str


def generate_readme(
    title: str,
    description: str,
    book_directory: str | Path,
    *,
    related_books: list[RelatedBook] | None = None,
    license_path: str = DEFAULT_LICENSE_PATH,
) -> str:
    """Assemble a book's README.md content.

    Args:
        title: The book's display title, rendered as the H1 heading.
        description: A one-paragraph description of the book.
        book_directory: Path to the book directory containing chapter-*.md
            files, passed to :func:`scripts.generate_toc.generate_toc_from_directory`.
        related_books: Other books to cross-link, in order. Omitted section if empty/None.
        license_path: Relative path to the repository LICENSE file.

    Returns:
        The rendered README.md Markdown content.

    Raises:
        ValueError: If title or description is blank, or no chapter files are found.
        scripts.generate_toc.ChapterParseError: If a chapter file doesn't parse.
    """
    if not title.strip():
        raise ValueError("title must not be empty")
    if not description.strip():
        raise ValueError("description must not be empty")

    toc = generate_toc_from_directory(book_directory)

    lines = [f"# {title.strip()}", "", description.strip(), "", "## Table of Contents", "", toc]

    if related_books:
        lines += ["", "## Related Books", ""]
        lines += [f"- [{book.title}]({book.path}) — {book.description}" for book in related_books]

    lines += ["", "## License", "", f"Content licensed under the terms in the repository [LICENSE]({license_path})."]

    logger.info("Generated README for %r (%d related book(s))", title, len(related_books or []))
    return "\n".join(lines) + "\n"


def related_books_from_dict(raw_books: list[dict[str, str]]) -> list[RelatedBook]:
    """Build :class:`RelatedBook` objects from parsed JSON/dict data."""
    return [RelatedBook(title=raw["title"], path=raw["path"], description=raw["description"]) for raw in raw_books]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.generate_readme spec.json``.

    The spec JSON has the shape: ``{"title": "...", "description": "...",
    "book_directory": "...", "related_books": [...], "license_path": "..."}``.
    """
    import argparse
    import json

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate a book's README.md from a JSON spec.")
    parser.add_argument("spec_file", help="Path to a JSON spec file")
    parser.add_argument("--output", help="Write to a file instead of stdout")
    args = parser.parse_args(argv)

    try:
        with open(args.spec_file, encoding="utf-8") as f:
            spec = json.load(f)
        readme = generate_readme(
            spec["title"],
            spec["description"],
            spec["book_directory"],
            related_books=related_books_from_dict(spec.get("related_books", [])),
            license_path=spec.get("license_path", DEFAULT_LICENSE_PATH),
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        logging.error("README generation failed: %s", exc)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(readme)
        logging.info("Wrote README to %s", args.output)
    else:
        print(readme)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
