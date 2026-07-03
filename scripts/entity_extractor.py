"""Extract named entity mentions from text using lightweight, offline heuristics.

This is a regex/heuristic proper-noun and year detector for quick content
audits — it approximates the concepts from
``docs/books/complete/geo/chapter-03.md`` (Named Entity Recognition, entity
salience, entity-based content gaps) without a trained NLP model. For
production-grade recognition and disambiguation against a real knowledge
base, use the Google Natural Language API or a library like spaCy (see
chapter section 9) and treat this module as a fast, dependency-free
first pass for editorial review.

Example:
    >>> from scripts.entity_extractor import extract_entities
    >>> mentions = extract_entities("Jane Doe joined Example Corp as CEO in 2024.")
    >>> [(m.text, m.entity_type) for m in mentions]
    [('2024', 'Date'), ('CEO', 'Organization'), ('Example Corp', 'Organization'), ('Jane Doe', 'Person')]
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass

logger = logging.getLogger(__name__)

ORG_SUFFIXES = frozenset({"Inc", "LLC", "Ltd", "Corp", "Co", "Group", "Corporation", "Company"})

# Capitalized words that only signal an entity when NOT at the start of a
# sentence (where capitalization is just sentence-initial, not proper-noun).
SENTENCE_INITIAL_STOPWORDS = frozenset(
    {
        "the", "a", "an", "this", "that", "these", "those", "it", "he", "she",
        "they", "we", "i", "in", "on", "at", "for", "with", "as", "but", "and",
        "or", "so", "if", "when", "while", "after", "before", "there", "here",
    }
)

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_PUNCTUATION_STRIP = ".,;:!?\"'()[]{}"


class EntityType:
    """Coarse entity type labels, matching the Schema.org vocabulary referenced in Chapter 3."""

    PERSON = "Person"
    ORGANIZATION = "Organization"
    DATE = "Date"
    UNKNOWN = "Unknown"


@dataclass
class EntityMention:
    """A canonical entity mention found in text, with its type and mention count."""

    text: str
    entity_type: str
    count: int = 1


def _clean_token(raw_token: str) -> str:
    return raw_token.strip(_PUNCTUATION_STRIP)


def _is_capitalized(token: str, *, is_sentence_initial: bool) -> bool:
    if not token or not token[0].isupper():
        return False
    if is_sentence_initial and token.lower() in SENTENCE_INITIAL_STOPWORDS:
        return False
    return True


def _find_capitalized_spans(sentence: str) -> list[str]:
    """Find runs of consecutive capitalized words (candidate proper-noun spans)."""
    spans: list[str] = []
    current: list[str] = []

    for index, raw_token in enumerate(sentence.split()):
        token = _clean_token(raw_token)
        if token and _is_capitalized(token, is_sentence_initial=(index == 0)):
            current.append(token)
            continue
        if current:
            spans.append(" ".join(current))
            current = []

    if current:
        spans.append(" ".join(current))
    return spans


def _classify_span(span: str) -> str:
    tokens = span.split()
    last_token = tokens[-1].rstrip(".")
    if last_token in ORG_SUFFIXES:
        return EntityType.ORGANIZATION
    if all(len(token) > 1 and token.isupper() for token in tokens):
        return EntityType.ORGANIZATION
    if len(tokens) == 2:
        return EntityType.PERSON
    return EntityType.UNKNOWN


def extract_entities(text: str) -> list[EntityMention]:
    """Extract candidate entity mentions from text, grouped and counted.

    Args:
        text: The content to scan for entity mentions.

    Returns:
        A list of :class:`EntityMention`, one per distinct mention text,
        sorted by descending mention count (a proxy for salience, per
        Chapter 3 section 6) and then alphabetically for stable ordering.
    """
    counts: Counter[str] = Counter()
    types: dict[str, str] = {}

    for sentence in _SENTENCE_SPLIT_RE.split(text.strip()):
        for span in _find_capitalized_spans(sentence):
            counts[span] += 1
            types.setdefault(span, _classify_span(span))
        for year in _YEAR_RE.findall(sentence):
            counts[year] += 1
            types.setdefault(year, EntityType.DATE)

    mentions = [
        EntityMention(text=text_, entity_type=types[text_], count=count)
        for text_, count in counts.items()
    ]
    mentions.sort(key=lambda mention: (-mention.count, mention.text))
    logger.info("Extracted %d distinct entity mention(s) from text", len(mentions))
    return mentions


def compute_salience(mentions: list[EntityMention]) -> dict[str, float]:
    """Approximate each entity's salience as its share of total entity mentions.

    This is a frequency-based proxy for the salience concept in Chapter 3
    section 6, not a trained salience model.

    Args:
        mentions: Entity mentions, typically from :func:`extract_entities`.

    Returns:
        A mapping of entity text to a salience score between 0.0 and 1.0.
        Empty if mentions is empty.
    """
    total = sum(mention.count for mention in mentions)
    if total == 0:
        return {}
    return {mention.text: round(mention.count / total, 4) for mention in mentions}


def find_entity_gaps(
    own_mentions: list[EntityMention], competitor_mentions: list[EntityMention]
) -> list[str]:
    """Find entities present in competitor content but missing from your own.

    Implements the entity-based content gap analysis described in Chapter 3
    section 8: extending keyword gap analysis into entity space.

    Args:
        own_mentions: Entities extracted from your own content.
        competitor_mentions: Entities extracted from competitor content.

    Returns:
        Competitor entity text values (case-insensitively deduplicated) that
        don't appear among own_mentions, in competitor_mentions order.
    """
    own_texts = {mention.text.lower() for mention in own_mentions}
    seen: set[str] = set()
    gaps: list[str] = []
    for mention in competitor_mentions:
        key = mention.text.lower()
        if key not in own_texts and key not in seen:
            seen.add(key)
            gaps.append(mention.text)
    return gaps


def format_report(mentions: list[EntityMention]) -> str:
    """Render extracted entities and their salience as a human-readable text report."""
    salience = compute_salience(mentions)
    lines = [f"Entity Extraction Report ({len(mentions)} distinct entities)", ""]
    for mention in mentions:
        lines.append(
            f"  [{mention.entity_type}] {mention.text} "
            f"(mentions: {mention.count}, salience: {salience[mention.text]:.2%})"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.entity_extractor content.txt [--compare other.txt]``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Extract entity mentions from a text file.")
    parser.add_argument("content_file", help="Path to a text file to scan for entities")
    parser.add_argument("--compare", help="Path to a competitor text file for entity gap analysis")
    args = parser.parse_args(argv)

    try:
        with open(args.content_file, encoding="utf-8") as f:
            mentions = extract_entities(f.read())
    except OSError as exc:
        logging.error("Could not read %s: %s", args.content_file, exc)
        return 1

    print(format_report(mentions))

    if args.compare:
        try:
            with open(args.compare, encoding="utf-8") as f:
                competitor_mentions = extract_entities(f.read())
        except OSError as exc:
            logging.error("Could not read %s: %s", args.compare, exc)
            return 1

        gaps = find_entity_gaps(mentions, competitor_mentions)
        print(f"\nEntity gaps ({len(gaps)} found in {args.compare} but not {args.content_file}):")
        for gap in gaps:
            print(f"  - {gap}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
