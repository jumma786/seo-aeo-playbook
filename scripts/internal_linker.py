"""Suggest internal links between pages and detect orphaned pages.

A lightweight, offline internal linking analyst: given a set of pages (URL,
title, body text, and optional target keywords), suggests which pages
should link to which others based on literal title/keyword mentions in
body text, and flags orphan pages with no inbound internal links — the
hub-and-spoke site architecture concerns covered in
``docs/books/complete/seo/chapter-16.md`` (Site Architecture) and
``chapter-17.md`` (Off-Page SEO).

Example:
    >>> from scripts.internal_linker import Page, suggest_internal_links
    >>> pages = [
    ...     Page(url="/guide", title="SEO Guide", body="Read our Core Web Vitals guide for details."),
    ...     Page(url="/cwv", title="Core Web Vitals", body="An overview of Core Web Vitals."),
    ... ]
    >>> suggestions = suggest_internal_links(pages)
    >>> [(s.source_url, s.target_url, s.anchor_text) for s in suggestions]
    [('/guide', '/cwv', 'Core Web Vitals')]
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Anchor candidates shorter than this are skipped as too generic/noisy to
# suggest as a link (e.g. a two-letter keyword matching incidentally).
MIN_ANCHOR_LENGTH = 3


@dataclass
class Page:
    """A single page in an internal linking analysis."""

    url: str
    title: str
    body: str = ""
    keywords: list[str] = field(default_factory=list)
    links_to: set[str] = field(default_factory=set)

    def anchor_candidates(self) -> list[str]:
        """Candidate anchor phrases for this page (title + keywords), longest first."""
        candidates = {phrase.strip() for phrase in (self.title, *self.keywords)}
        candidates = {phrase for phrase in candidates if len(phrase) >= MIN_ANCHOR_LENGTH}
        return sorted(candidates, key=len, reverse=True)


@dataclass
class LinkSuggestion:
    """A suggested internal link from one page to another."""

    source_url: str
    target_url: str
    anchor_text: str


def _contains_phrase(body: str, phrase: str) -> bool:
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, body, re.IGNORECASE) is not None


def suggest_internal_links(pages: list[Page], *, max_suggestions_per_page: int = 5) -> list[LinkSuggestion]:
    """Suggest internal links based on title/keyword mentions in page bodies.

    For each page, scans its body text for literal mentions of every other
    page's title or keywords. A mention that isn't already an existing
    outbound link becomes a suggested link, using the matched phrase as
    anchor text. At most one suggestion is made per (source, target) pair,
    preferring the longest matching phrase.

    Args:
        pages: The site's pages to analyze.
        max_suggestions_per_page: Maximum number of suggestions to return
            for any single source page.

    Returns:
        A list of :class:`LinkSuggestion`, grouped by source page in the
        order pages were given, each internally capped at
        max_suggestions_per_page.
    """
    suggestions: list[LinkSuggestion] = []

    for source in pages:
        source_suggestions: list[LinkSuggestion] = []
        for target in pages:
            if target.url == source.url or target.url in source.links_to:
                continue
            for phrase in target.anchor_candidates():
                if _contains_phrase(source.body, phrase):
                    source_suggestions.append(
                        LinkSuggestion(source_url=source.url, target_url=target.url, anchor_text=phrase)
                    )
                    break
        suggestions.extend(source_suggestions[:max_suggestions_per_page])

    logger.info("Generated %d internal link suggestion(s) across %d page(s)", len(suggestions), len(pages))
    return suggestions


def find_orphan_pages(pages: list[Page]) -> list[str]:
    """Find pages with no existing inbound internal links from any other page.

    Args:
        pages: The site's pages, using each page's links_to to represent
            existing outbound links.

    Returns:
        URLs of pages that no other page links to, in the order given in pages.
    """
    linked_urls = {url for page in pages for url in page.links_to}
    return [page.url for page in pages if page.url not in linked_urls]


def format_report(pages: list[Page], suggestions: list[LinkSuggestion]) -> str:
    """Render a human-readable internal linking report."""
    orphans = find_orphan_pages(pages)
    lines = [f"Internal Linking Report ({len(pages)} pages, {len(suggestions)} suggestions)", ""]

    if orphans:
        lines.append(f"Orphan pages ({len(orphans)}, no inbound internal links):")
        lines.extend(f"  - {url}" for url in orphans)
        lines.append("")

    lines.append("Suggested links:")
    for suggestion in suggestions:
        lines.append(f'  {suggestion.source_url} -> {suggestion.target_url} (anchor: "{suggestion.anchor_text}")')

    return "\n".join(lines)


def pages_from_dict(raw_pages: list[dict]) -> list[Page]:
    """Build :class:`Page` objects from parsed JSON/dict data.

    Args:
        raw_pages: A list of dicts, each with a ``url`` and ``title`` (both
            required) and optional ``body``, ``keywords``, and ``links_to`` keys.

    Returns:
        The corresponding list of :class:`Page` objects.

    Raises:
        KeyError: If any entry is missing ``url`` or ``title``.
    """
    return [
        Page(
            url=raw["url"],
            title=raw["title"],
            body=raw.get("body", ""),
            keywords=raw.get("keywords", []),
            links_to=set(raw.get("links_to", [])),
        )
        for raw in raw_pages
    ]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.internal_linker pages.json``."""
    import argparse
    import json

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Suggest internal links and find orphan pages from a JSON page list."
    )
    parser.add_argument("pages_file", help="Path to a JSON file: a list of {url, title, body, keywords, links_to}")
    parser.add_argument("--max-per-page", type=int, default=5)
    args = parser.parse_args(argv)

    try:
        with open(args.pages_file, encoding="utf-8") as f:
            pages = pages_from_dict(json.load(f))
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        logging.error("Failed to load pages: %s", exc)
        return 1

    suggestions = suggest_internal_links(pages, max_suggestions_per_page=args.max_per_page)
    print(format_report(pages, suggestions))
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
