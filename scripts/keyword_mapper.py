"""Map keywords to target URLs and detect cannibalization risk.

Complements ``scripts/keyword_cluster.py``: where that module groups
keywords into topical clusters, this module (a) audits an existing
keyword-to-URL mapping for cannibalization — cases where more than one URL
is assigned the same keyword, splitting ranking signal instead of
consolidating it — and (b) suggests which existing page best matches an
unmapped keyword, reusing the same lexical token-overlap similarity as
``keyword_cluster`` for consistency.

Example:
    >>> from scripts.keyword_mapper import KeywordMapping, find_cannibalization
    >>> mappings = [
    ...     KeywordMapping(keyword="running shoes", url="/running-shoes"),
    ...     KeywordMapping(keyword="running shoes", url="/best-running-shoes"),
    ... ]
    >>> [issue.keyword for issue in find_cannibalization(mappings)]
    ['running shoes']
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass

from scripts.keyword_cluster import jaccard_similarity, normalize_tokens

logger = logging.getLogger(__name__)

DEFAULT_MATCH_THRESHOLD = 0.34


@dataclass
class KeywordMapping:
    """A single keyword assigned to a target URL."""

    keyword: str
    url: str


@dataclass
class CannibalizationIssue:
    """A keyword mapped to more than one URL."""

    keyword: str
    urls: list[str]


def find_cannibalization(mappings: list[KeywordMapping]) -> list[CannibalizationIssue]:
    """Find keywords assigned (case-insensitively) to more than one URL.

    Args:
        mappings: An existing keyword-to-URL mapping to audit.

    Returns:
        A :class:`CannibalizationIssue` for every keyword with more than
        one distinct target URL, sorted alphabetically by keyword.
    """
    urls_by_keyword: dict[str, list[str]] = defaultdict(list)
    for mapping in mappings:
        key = mapping.keyword.strip().lower()
        if mapping.url not in urls_by_keyword[key]:
            urls_by_keyword[key].append(mapping.url)

    issues = [
        CannibalizationIssue(keyword=keyword, urls=urls)
        for keyword, urls in urls_by_keyword.items()
        if len(urls) > 1
    ]
    issues.sort(key=lambda issue: issue.keyword)
    logger.info("Checked %d mapping(s): %d cannibalization issue(s) found", len(mappings), len(issues))
    return issues


def suggest_url_for_keyword(
    keyword: str, pages: dict[str, str], *, threshold: float = DEFAULT_MATCH_THRESHOLD
) -> str | None:
    """Suggest the best-matching existing page URL for a keyword, if any.

    Args:
        keyword: The keyword to map.
        pages: A mapping of URL to page title.
        threshold: Minimum token-overlap similarity (see
            :func:`scripts.keyword_cluster.jaccard_similarity`) required to
            suggest a match.

    Returns:
        The URL of the best-matching page, or None if no page meets the
        threshold — signaling the keyword may need new content rather
        than reuse of an existing page.
    """
    keyword_tokens = normalize_tokens(keyword)
    best_url: str | None = None
    best_score = 0.0
    for url, title in pages.items():
        score = jaccard_similarity(keyword_tokens, normalize_tokens(title))
        if score >= threshold and score > best_score:
            best_score = score
            best_url = url
    return best_url


def map_keywords_to_urls(
    keywords: list[str], pages: dict[str, str], *, threshold: float = DEFAULT_MATCH_THRESHOLD
) -> list[KeywordMapping]:
    """Map each keyword to its best-matching existing page, if any.

    Args:
        keywords: The keywords to map.
        pages: A mapping of URL to page title, the candidate targets.
        threshold: Minimum similarity passed to :func:`suggest_url_for_keyword`.

    Returns:
        One :class:`KeywordMapping` per keyword that matched a page above
        threshold. Keywords with no matching page are omitted (not
        assigned a mapping) rather than guessed at.
    """
    mappings = []
    for keyword in keywords:
        url = suggest_url_for_keyword(keyword, pages, threshold=threshold)
        if url is not None:
            mappings.append(KeywordMapping(keyword=keyword, url=url))
    return mappings


def unmapped_keywords(keywords: list[str], mappings: list[KeywordMapping]) -> list[str]:
    """Find keywords with no entry in a keyword-to-URL mapping.

    Args:
        keywords: The full set of keywords that should be targeted somewhere.
        mappings: The existing (or suggested) keyword-to-URL mappings.

    Returns:
        Keywords (case-insensitively) absent from mappings, in the order given.
    """
    mapped = {mapping.keyword.strip().lower() for mapping in mappings}
    return [keyword for keyword in keywords if keyword.strip().lower() not in mapped]


def mappings_from_dict(raw_mappings: list[dict[str, str]]) -> list[KeywordMapping]:
    """Build :class:`KeywordMapping` objects from parsed JSON/dict data."""
    return [KeywordMapping(keyword=raw["keyword"], url=raw["url"]) for raw in raw_mappings]


def format_cannibalization_report(issues: list[CannibalizationIssue]) -> str:
    """Render cannibalization issues as a human-readable text report."""
    lines = [f"Keyword Cannibalization Report ({len(issues)} issue(s) found)", ""]
    for issue in issues:
        lines.append(f'  "{issue.keyword}" is targeted by {len(issue.urls)} URLs:')
        lines.extend(f"    - {url}" for url in issue.urls)
    return "\n".join(lines)


def format_mapping_report(mappings: list[KeywordMapping], unmapped: list[str]) -> str:
    """Render keyword-to-URL mapping suggestions as a human-readable text report."""
    lines = [f"Keyword Mapping Report ({len(mappings)} mapped, {len(unmapped)} unmapped)", ""]
    for mapping in mappings:
        lines.append(f'  "{mapping.keyword}" -> {mapping.url}')
    if unmapped:
        lines.append("")
        lines.append(f"Unmapped keywords ({len(unmapped)}, no matching page found):")
        lines.extend(f"  - {keyword}" for keyword in unmapped)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    ``python -m scripts.keyword_mapper audit mappings.json`` checks an
    existing mapping for cannibalization.

    ``python -m scripts.keyword_mapper suggest keywords.txt pages.json``
    suggests a target URL for each keyword.
    """
    import argparse
    import json

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Map keywords to URLs and audit for cannibalization.")
    sub = parser.add_subparsers(dest="mode", required=True)

    audit_parser = sub.add_parser("audit", help="Audit an existing keyword-to-URL mapping for cannibalization")
    audit_parser.add_argument("mappings_file", help='JSON file: [{"keyword": "...", "url": "..."}, ...]')

    suggest_parser = sub.add_parser("suggest", help="Suggest a target URL for each keyword")
    suggest_parser.add_argument("keywords_file", help="Text file, one keyword per line")
    suggest_parser.add_argument("pages_file", help='JSON file: {"url": "title", ...}')
    suggest_parser.add_argument("--threshold", type=float, default=DEFAULT_MATCH_THRESHOLD)

    args = parser.parse_args(argv)

    try:
        if args.mode == "audit":
            with open(args.mappings_file, encoding="utf-8") as f:
                mappings = mappings_from_dict(json.load(f))
            print(format_cannibalization_report(find_cannibalization(mappings)))
        else:
            with open(args.keywords_file, encoding="utf-8") as f:
                keywords = [line.strip() for line in f if line.strip()]
            with open(args.pages_file, encoding="utf-8") as f:
                pages = json.load(f)
            mappings = map_keywords_to_urls(keywords, pages, threshold=args.threshold)
            print(format_mapping_report(mappings, unmapped_keywords(keywords, mappings)))
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        logging.error("keyword_mapper failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
