"""Scaffold a new blog post from a content brief.

Ties together this repository's content-planning and schema tools into a
single "start writing" scaffold: given a
``scripts.content_brief.ContentBrief`` and basic post metadata, renders
Markdown frontmatter, a section-by-section outline (restating each
section's word-count target and keywords as writer prompts), an FAQ
skeleton if the brief has questions to answer, and a matching Article
JSON-LD schema (``scripts.schema_generator``). This produces a scaffold
to write into — it does not fabricate body prose as if it were finished copy.

Example:
    >>> from scripts.blog_generator import BlogPostSpec, generate_blog_scaffold
    >>> from scripts.content_brief import generate_content_brief
    >>> brief = generate_content_brief("core web vitals", [], target_word_count=1000)
    >>> spec = BlogPostSpec(
    ...     title="Core Web Vitals Explained",
    ...     slug="core-web-vitals-explained",
    ...     author_name="Jane Doe",
    ...     date_published="2026-01-15",
    ...     brief=brief,
    ... )
    >>> generate_blog_scaffold(spec).splitlines()[0]
    '---'
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from scripts.content_brief import ContentBrief
from scripts.meta_generator import validate_title
from scripts.schema_generator import generate_article_schema, to_script_tag

logger = logging.getLogger(__name__)


@dataclass
class BlogPostSpec:
    """Metadata plus a content brief for a single blog post scaffold."""

    title: str
    slug: str
    author_name: str
    date_published: str
    brief: ContentBrief


def generate_blog_scaffold(spec: BlogPostSpec) -> str:
    """Render a Markdown blog post scaffold from a content brief.

    Args:
        spec: The post's metadata and content brief.

    Returns:
        Markdown with frontmatter, an outline of TODO prompts per brief
        section (and per FAQ question if present), and a matching Article
        JSON-LD schema.
    """
    for warning in validate_title(spec.title):
        logger.warning("Title guidance: %s", warning)

    lines = [
        "---",
        f'title: "{spec.title}"',
        f"date: {spec.date_published}",
        f"author: {spec.author_name}",
        f"slug: {spec.slug}",
        "---",
        "",
        f"# {spec.title}",
        "",
        "<!-- TODO: Write your introduction (~150-225 words). Lead with the direct "
        "answer/claim before supporting detail (AEO Book, Chapter 7). -->",
        "",
    ]

    for section in spec.brief.sections:
        lines.append(f"## {section.heading} (~{section.target_word_count} words)")
        lines.append("")
        lines.append(f"<!-- TODO: cover: {', '.join(section.keywords)} -->")
        lines.append("")

    if spec.brief.questions_to_answer:
        lines.append("## Frequently Asked Questions")
        lines.append("")
        for question in spec.brief.questions_to_answer:
            lines.append(f"### {question}")
            lines.append("")
            lines.append(
                "<!-- TODO: answer in 15-60 words, naming the subject explicitly "
                "(see scripts/faq_generator.py) -->"
            )
            lines.append("")

    schema = generate_article_schema(headline=spec.title, author_name=spec.author_name, date_published=spec.date_published)
    lines.append(to_script_tag(schema))

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.blog_generator spec.json``.

    The spec JSON has the shape: ``{"title": "...", "slug": "...",
    "author_name": "...", "date_published": "...", "primary_keyword": "...",
    "related_keywords": [...], "target_word_count": 1500, "questions": [...]}``.
    """
    import argparse
    import json

    from scripts.content_brief import generate_content_brief

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Scaffold a new blog post from a JSON spec.")
    parser.add_argument("spec_file", help="Path to a JSON spec file")
    parser.add_argument("--output", help="Write to a file instead of stdout")
    args = parser.parse_args(argv)

    try:
        with open(args.spec_file, encoding="utf-8") as f:
            raw = json.load(f)
        brief = generate_content_brief(
            raw["primary_keyword"],
            raw.get("related_keywords", []),
            target_word_count=raw.get("target_word_count", 1500),
            questions=raw.get("questions"),
        )
        spec = BlogPostSpec(
            title=raw["title"],
            slug=raw["slug"],
            author_name=raw["author_name"],
            date_published=raw["date_published"],
            brief=brief,
        )
        scaffold = generate_blog_scaffold(spec)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        logging.error("Blog scaffold generation failed: %s", exc)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(scaffold)
        logging.info("Wrote blog scaffold to %s", args.output)
    else:
        print(scaffold)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
