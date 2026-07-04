"""Generate a structured content brief for a target keyword.

A lightweight, offline complement to the ``seo-content-brief`` skill in
this repository (which pulls live competitor SERP data): given a primary
keyword and a list of related keywords, clusters the related keywords
into topical sections (reusing ``scripts.keyword_cluster``), distributes
a target word count across those sections, and reuses the title/meta
description length guidance from ``scripts.meta_generator`` — producing a
ready-to-hand-to-a-writer brief without requiring any external API.

Example:
    >>> from scripts.content_brief import generate_content_brief
    >>> brief = generate_content_brief(
    ...     "core web vitals",
    ...     ["largest contentful paint guide", "cumulative layout shift guide"],
    ...     target_word_count=1000,
    ... )
    >>> brief.primary_keyword
    'core web vitals'
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from scripts.keyword_cluster import DEFAULT_SIMILARITY_THRESHOLD, cluster_keywords
from scripts.meta_generator import (
    META_DESCRIPTION_MAX_LENGTH,
    META_DESCRIPTION_MIN_LENGTH,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
)

logger = logging.getLogger(__name__)

# Fraction of the total target word count reserved for the intro and
# conclusion, leaving the remainder to be distributed across body sections.
INTRO_CONCLUSION_SHARE = 0.15
MIN_SECTION_WORD_COUNT = 100


@dataclass
class BriefSection:
    """A single H2-level section of a content brief."""

    heading: str
    keywords: list[str]
    target_word_count: int


@dataclass
class ContentBrief:
    """A structured brief for writing a piece of content targeting a keyword."""

    primary_keyword: str
    target_word_count: int
    sections: list[BriefSection] = field(default_factory=list)
    questions_to_answer: list[str] = field(default_factory=list)
    entities_to_mention: list[str] = field(default_factory=list)


def generate_content_brief(
    primary_keyword: str,
    related_keywords: list[str],
    *,
    target_word_count: int = 1500,
    questions: list[str] | None = None,
    entities: list[str] | None = None,
    cluster_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> ContentBrief:
    """Build a content brief: clustered sections with per-section word targets.

    Args:
        primary_keyword: The keyword the piece should primarily target.
        related_keywords: Supporting keywords, clustered into sections via
            :func:`scripts.keyword_cluster.cluster_keywords`.
        target_word_count: The total word count the finished piece should hit.
        questions: Questions the content should explicitly answer (e.g. from
            "People Also Ask" or community research).
        entities: Named entities the content should mention (see
            :mod:`scripts.entity_extractor` for extracting these from
            competitor content).
        cluster_threshold: Similarity threshold passed to ``cluster_keywords``.

    Returns:
        A :class:`ContentBrief` with body word count distributed across
        sections proportional to each cluster's keyword count.

    Raises:
        ValueError: If primary_keyword is blank or target_word_count isn't positive.
    """
    if not primary_keyword.strip():
        raise ValueError("primary_keyword must not be empty")
    if target_word_count <= 0:
        raise ValueError("target_word_count must be positive")

    clusters = cluster_keywords(related_keywords, similarity_threshold=cluster_threshold)
    body_word_count = int(target_word_count * (1 - INTRO_CONCLUSION_SHARE))
    total_clustered_keywords = sum(len(cluster.keywords) for cluster in clusters) or 1

    sections = []
    for cluster in clusters:
        share = len(cluster.keywords) / total_clustered_keywords
        section_word_count = max(MIN_SECTION_WORD_COUNT, round(body_word_count * share))
        sections.append(
            BriefSection(heading=cluster.label.title(), keywords=cluster.keywords, target_word_count=section_word_count)
        )

    logger.info(
        "Generated content brief for %r: %d section(s), %d target word(s)",
        primary_keyword,
        len(sections),
        target_word_count,
    )
    return ContentBrief(
        primary_keyword=primary_keyword.strip(),
        target_word_count=target_word_count,
        sections=sections,
        questions_to_answer=list(questions or []),
        entities_to_mention=list(entities or []),
    )


def format_brief(brief: ContentBrief) -> str:
    """Render a :class:`ContentBrief` as a Markdown document."""
    lines = [
        f"# Content Brief: {brief.primary_keyword}",
        "",
        f"**Target word count:** {brief.target_word_count}",
        f'**Title guidance:** {TITLE_MIN_LENGTH}-{TITLE_MAX_LENGTH} characters, include "{brief.primary_keyword}"',
        f"**Meta description guidance:** {META_DESCRIPTION_MIN_LENGTH}-{META_DESCRIPTION_MAX_LENGTH} characters",
        "",
        "## Outline",
        "",
    ]
    for section in brief.sections:
        lines.append(f"### {section.heading} (~{section.target_word_count} words)")
        lines.extend(f"- {keyword}" for keyword in section.keywords)
        lines.append("")

    if brief.questions_to_answer:
        lines.append("## Questions to Answer")
        lines.extend(f"- {question}" for question in brief.questions_to_answer)
        lines.append("")

    if brief.entities_to_mention:
        lines.append("## Entities to Mention")
        lines.extend(f"- {entity}" for entity in brief.entities_to_mention)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.content_brief spec.json``.

    The spec JSON has the shape: ``{"primary_keyword": "...",
    "related_keywords": [...], "target_word_count": 1500,
    "questions": [...], "entities": [...]}``.
    """
    import argparse
    import json

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate a content brief from a JSON spec.")
    parser.add_argument("spec_file", help="Path to a JSON spec file")
    parser.add_argument("--output", help="Write to a file instead of stdout")
    args = parser.parse_args(argv)

    try:
        with open(args.spec_file, encoding="utf-8") as f:
            spec = json.load(f)
        brief = generate_content_brief(
            spec["primary_keyword"],
            spec.get("related_keywords", []),
            target_word_count=spec.get("target_word_count", 1500),
            questions=spec.get("questions"),
            entities=spec.get("entities"),
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        logging.error("Content brief generation failed: %s", exc)
        return 1

    content = format_brief(brief)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info("Wrote content brief to %s", args.output)
    else:
        print(content)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
