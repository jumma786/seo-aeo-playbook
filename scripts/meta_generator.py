"""Generate and validate SEO title tags and meta descriptions.

Applies the length guidance from ``docs/books/complete/seo/chapter-09.md``
(Content Optimization) and truncates safely at word boundaries so titles
and descriptions never end mid-word or mid-punctuation.

Example:
    >>> from scripts.meta_generator import generate_title
    >>> generate_title("Core Web Vitals", brand="Example Corp")
    'Core Web Vitals | Example Corp'
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

TITLE_MIN_LENGTH = 30
TITLE_MAX_LENGTH = 60
META_DESCRIPTION_MIN_LENGTH = 70
META_DESCRIPTION_MAX_LENGTH = 160

DEFAULT_TITLE_SEPARATOR = " | "


def truncate_at_word_boundary(text: str, max_length: int, *, suffix: str = "...") -> str:
    """Truncate text to at most max_length characters without cutting mid-word.

    Args:
        text: The text to truncate.
        max_length: The maximum allowed length, including the suffix.
        suffix: Appended when truncation occurs (counted toward max_length).

    Returns:
        The original text if it already fits, otherwise a word-boundary-safe
        truncation with the suffix appended.

    Raises:
        ValueError: If max_length is not large enough to hold the suffix.
    """
    if max_length < len(suffix):
        raise ValueError(f"max_length ({max_length}) must be >= len(suffix) ({len(suffix)})")
    if len(text) <= max_length:
        return text

    budget = max_length - len(suffix)
    truncated = text[:budget].rstrip()
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]
    return truncated.rstrip(",.;:-") + suffix


def generate_title(
    page_title: str,
    *,
    brand: str | None = None,
    separator: str = DEFAULT_TITLE_SEPARATOR,
    max_length: int = TITLE_MAX_LENGTH,
) -> str:
    """Build a title tag, optionally appending a brand suffix, within length limits.

    Args:
        page_title: The primary, page-specific title text.
        brand: An optional brand name appended after a separator.
        separator: The separator placed between the page title and brand.
        max_length: The maximum total title length.

    Returns:
        A title string truncated to fit max_length if necessary. If adding
        the brand would exceed max_length, the brand is dropped rather than
        truncating the page title itself.

    Raises:
        ValueError: If page_title is blank.
    """
    if not page_title.strip():
        raise ValueError("page_title must not be blank")

    page_title = page_title.strip()
    if brand:
        candidate = f"{page_title}{separator}{brand.strip()}"
        if len(candidate) <= max_length:
            return candidate
        logger.debug("Dropping brand suffix; combined title would exceed max_length=%d", max_length)

    if len(page_title) > max_length:
        return truncate_at_word_boundary(page_title, max_length)
    return page_title


def generate_meta_description(
    text: str,
    *,
    max_length: int = META_DESCRIPTION_MAX_LENGTH,
) -> str:
    """Build a meta description truncated safely within the recommended length.

    Args:
        text: Source text to derive the description from (e.g. an article's
            opening summary or a generated snippet).
        max_length: The maximum total description length.

    Returns:
        The description truncated at a word boundary if it exceeds max_length.

    Raises:
        ValueError: If text is blank.
    """
    if not text.strip():
        raise ValueError("text must not be blank")
    return truncate_at_word_boundary(text.strip(), max_length)


def validate_title(title: str) -> list[str]:
    """Check a title tag against SEO length guidance.

    Args:
        title: The title tag content to validate.

    Returns:
        A list of human-readable warning strings; empty if no issues found.
    """
    warnings: list[str] = []
    length = len(title)
    if not title.strip():
        return ["Title is empty"]
    if length < TITLE_MIN_LENGTH:
        warnings.append(f"Title is {length} characters (recommended >= {TITLE_MIN_LENGTH})")
    if length > TITLE_MAX_LENGTH:
        warnings.append(f"Title is {length} characters (recommended <= {TITLE_MAX_LENGTH})")
    return warnings


def validate_meta_description(description: str) -> list[str]:
    """Check a meta description against SEO length guidance.

    Args:
        description: The meta description content to validate.

    Returns:
        A list of human-readable warning strings; empty if no issues found.
    """
    warnings: list[str] = []
    length = len(description)
    if not description.strip():
        return ["Meta description is empty"]
    if length < META_DESCRIPTION_MIN_LENGTH:
        warnings.append(
            f"Meta description is {length} characters (recommended >= {META_DESCRIPTION_MIN_LENGTH})"
        )
    if length > META_DESCRIPTION_MAX_LENGTH:
        warnings.append(
            f"Meta description is {length} characters (recommended <= {META_DESCRIPTION_MAX_LENGTH})"
        )
    return warnings


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.meta_generator --title "..." [--brand "..."]``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate an SEO title tag and/or meta description.")
    parser.add_argument("--title", help="Page-specific title text")
    parser.add_argument("--brand", help="Brand name to append to the title")
    parser.add_argument("--description", help="Source text for the meta description")
    args = parser.parse_args(argv)

    if not args.title and not args.description:
        parser.error("Provide --title and/or --description")

    if args.title:
        title = generate_title(args.title, brand=args.brand)
        print(f"Title ({len(title)} chars): {title}")
        for warning in validate_title(title):
            logger.warning(warning)

    if args.description:
        description = generate_meta_description(args.description)
        print(f"Description ({len(description)} chars): {description}")
        for warning in validate_meta_description(description):
            logger.warning(warning)

    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
