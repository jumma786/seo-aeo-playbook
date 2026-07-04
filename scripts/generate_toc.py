"""Generate a book-level README.md table of contents from chapter files.

Scans ``docs/books/complete/<book>/chapter-NN.md`` files (this repo's
established chapter convention) and produces the ``| # | Chapter | Focus |``
Markdown table used by each book's own README.md (see
``docs/books/complete/geo/README.md`` for the target format). The
"Focus" column is derived from the first sentence of each chapter's
first content section, truncated for table readability using
``scripts.meta_generator``'s word-boundary-safe truncation.

Example:
    >>> from scripts.generate_toc import parse_chapter
    >>> text = (
    ...     "# Chapter 1: Example Chapter\\n\\n**Version:** 1.0\\n\\n---\\n\\n"
    ...     "# Table of Contents\\n\\n1. Intro\\n\\n---\\n\\n"
    ...     "# 1. Intro\\n\\nThis chapter covers the basics of the topic. More detail follows.\\n"
    ... )
    >>> info = parse_chapter(text, filename="chapter-01.md")
    >>> (info.number, info.title, info.filename)
    (1, 'Example Chapter', 'chapter-01.md')
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from scripts.meta_generator import truncate_at_word_boundary

logger = logging.getLogger(__name__)

MAX_FOCUS_LENGTH = 80
_TITLE_RE = re.compile(r"^#\s*Chapter\s+(\d+)\s*:\s*(.+?)\s*$", re.MULTILINE)


class ChapterParseError(ValueError):
    """Raised when a chapter file doesn't match the expected structure."""


@dataclass
class ChapterInfo:
    """Parsed metadata for a single chapter, enough to render one TOC row."""

    number: int
    title: str
    filename: str
    focus: str


def _extract_focus(sections: list[str]) -> str:
    """Derive a short "Focus" blurb from a chapter's first content section."""
    if len(sections) < 3:
        return ""

    body_lines = [line for line in sections[2].strip().splitlines()[1:] if line.strip()]
    if not body_lines:
        return ""

    paragraph = " ".join(body_lines).strip()
    first_sentence = paragraph.split(". ")[0].rstrip(".") + "."
    return truncate_at_word_boundary(first_sentence, MAX_FOCUS_LENGTH)


def parse_chapter(text: str, *, filename: str) -> ChapterInfo:
    """Parse a single chapter file's number, title, and a short focus blurb.

    Args:
        text: The chapter file's raw Markdown content.
        filename: The chapter's filename (e.g. "chapter-01.md"), used for the TOC link.

    Returns:
        A :class:`ChapterInfo` with the chapter number, title, filename, and focus blurb.

    Raises:
        ChapterParseError: If the file's title line doesn't match "# Chapter N: Title".
    """
    match = _TITLE_RE.search(text)
    if not match:
        raise ChapterParseError(f"{filename}: could not find a '# Chapter N: Title' heading")

    number = int(match.group(1))
    title = match.group(2)
    sections = text.split("\n---\n")
    focus = _extract_focus(sections)

    return ChapterInfo(number=number, title=title, filename=filename, focus=focus)


def generate_toc_table(chapters: list[ChapterInfo]) -> str:
    """Render parsed chapters as a Markdown table of contents.

    Args:
        chapters: Chapter info; sorted by number ascending before rendering.

    Returns:
        A Markdown table: a ``| # | Chapter | Focus |`` header plus one row per chapter.

    Raises:
        ValueError: If chapters is empty.
    """
    if not chapters:
        raise ValueError("At least one chapter is required")

    ordered = sorted(chapters, key=lambda chapter: chapter.number)
    lines = ["| # | Chapter | Focus |", "|---|---|---|"]
    lines.extend(f"| {chapter.number} | [{chapter.title}]({chapter.filename}) | {chapter.focus} |" for chapter in ordered)
    return "\n".join(lines)


def generate_toc_from_directory(directory: str | Path) -> str:
    """Parse every ``chapter-*.md`` file in a directory and render a TOC table.

    Args:
        directory: Path to a book directory (e.g. ``docs/books/complete/geo``).

    Returns:
        The rendered Markdown TOC table.

    Raises:
        ChapterParseError: If any chapter file doesn't parse.
        ValueError: If no chapter files are found.
    """
    directory = Path(directory)
    chapter_files = sorted(directory.glob("chapter-*.md"))
    if not chapter_files:
        raise ValueError(f"No chapter-*.md files found in {directory}")

    chapters = [parse_chapter(path.read_text(encoding="utf-8"), filename=path.name) for path in chapter_files]
    logger.info("Generated TOC for %d chapter(s) in %s", len(chapters), directory)
    return generate_toc_table(chapters)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.generate_toc docs/books/complete/geo``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate a book's README.md table of contents from chapter files.")
    parser.add_argument("book_directory", help="Path to a book directory containing chapter-*.md files")
    parser.add_argument("--output", help="Write to a file instead of stdout")
    args = parser.parse_args(argv)

    try:
        table = generate_toc_from_directory(args.book_directory)
    except (ChapterParseError, ValueError) as exc:
        logging.error("TOC generation failed: %s", exc)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(table + "\n")
        logging.info("Wrote TOC to %s", args.output)
    else:
        print(table)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
