"""Generate FAQ sections (Markdown + FAQPage JSON-LD) from Q&A pairs.

Combines the "FAQ Sections" / "People Also Ask" content practice from
``docs/books/complete/seo/chapter-09.md`` with the self-contained-answer
citability principle from the AEO book (Chapter 7): validates each
answer's length and self-containedness, renders a Markdown FAQ section,
and reuses ``scripts.schema_generator`` for the matching FAQPage JSON-LD
so the visible content and the structured data never drift out of sync.

Example:
    >>> from scripts.faq_generator import FaqItem, generate_faq_markdown
    >>> items = [FaqItem(question="What is SEO?", answer="SEO is optimizing a site to rank higher in search results.")]
    >>> print(generate_faq_markdown(items))
    ## Frequently Asked Questions
    <BLANKLINE>
    ### What is SEO?
    <BLANKLINE>
    SEO is optimizing a site to rank higher in search results.
    <BLANKLINE>
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from scripts.schema_generator import generate_faq_schema, to_script_tag

logger = logging.getLogger(__name__)

MIN_ANSWER_WORDS = 15
# Longer answers can still be correct, but exceeding this makes an answer
# less likely to be lifted whole into a featured snippet or AI citation.
MAX_ANSWER_WORDS = 60

QUESTION_WORDS = frozenset(
    {"what", "why", "how", "when", "where", "who", "which", "is", "are", "can", "does", "do", "will", "should"}
)
DANGLING_OPENERS = frozenset({"it", "this", "that", "they", "these", "those"})


@dataclass
class FaqItem:
    """A single FAQ question/answer pair."""

    question: str
    answer: str


@dataclass
class FaqIssue:
    """A single problem found while validating an FAQ item."""

    question: str
    message: str


def _starts_with_dangling_pronoun(answer: str) -> bool:
    words = answer.split()
    return bool(words) and words[0].lower().strip(",.;:") in DANGLING_OPENERS


def validate_faq_item(item: FaqItem) -> list[FaqIssue]:
    """Check a single Q&A pair against FAQ/AEO best practices.

    Args:
        item: The question/answer pair to validate.

    Returns:
        A list of :class:`FaqIssue`; empty if no problems were found.
    """
    issues: list[FaqIssue] = []
    question = item.question.strip()
    answer = item.answer.strip()

    if not question.endswith("?"):
        issues.append(FaqIssue(item.question, "Question does not end with '?'"))

    first_word = question.split()[0].lower().rstrip("?") if question else ""
    if first_word not in QUESTION_WORDS:
        issues.append(
            FaqIssue(item.question, f"Question does not start with a recognizable question word (starts with {first_word!r})")
        )

    word_count = len(answer.split())
    if word_count < MIN_ANSWER_WORDS:
        issues.append(
            FaqIssue(
                item.question,
                f"Answer is only {word_count} word(s) (recommended >= {MIN_ANSWER_WORDS} for a complete, citable answer)",
            )
        )
    elif word_count > MAX_ANSWER_WORDS:
        issues.append(
            FaqIssue(
                item.question,
                f"Answer is {word_count} word(s) (recommended <= {MAX_ANSWER_WORDS} for snippet/AI-citation friendliness)",
            )
        )

    if _starts_with_dangling_pronoun(answer):
        issues.append(
            FaqIssue(
                item.question,
                "Answer opens with a pronoun ('it'/'this'/'that'/...) with no named subject — "
                "not self-contained enough to quote out of context",
            )
        )

    return issues


def validate_faq_items(items: list[FaqItem]) -> list[FaqIssue]:
    """Validate a list of FAQ items, concatenating each item's issues."""
    issues: list[FaqIssue] = []
    for item in items:
        issues.extend(validate_faq_item(item))
    return issues


def generate_faq_markdown(items: list[FaqItem], *, heading: str = "Frequently Asked Questions") -> str:
    """Render Q&A pairs as a Markdown FAQ section.

    Args:
        items: The FAQ items to render, in order.
        heading: The section's H2 heading text.

    Returns:
        A Markdown string with an H2 heading and one H3 per question.

    Raises:
        ValueError: If items is empty.
    """
    if not items:
        raise ValueError("At least one FAQ item is required")

    lines = [f"## {heading}", ""]
    for item in items:
        lines.append(f"### {item.question.strip()}")
        lines.append("")
        lines.append(item.answer.strip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_faq_schema_tag(items: list[FaqItem]) -> str:
    """Render Q&A pairs as a FAQPage JSON-LD ``<script>`` tag.

    Reuses :func:`scripts.schema_generator.generate_faq_schema` so the
    structured data always matches the same source Q&A pairs as the
    rendered Markdown.

    Args:
        items: The FAQ items to include in the schema.

    Returns:
        An HTML string containing the FAQPage schema wrapped in a script tag.

    Raises:
        scripts.schema_generator.SchemaValidationError: If items is empty
            or contains a blank question/answer.
    """
    pairs = [(item.question, item.answer) for item in items]
    schema = generate_faq_schema(pairs)
    return to_script_tag(schema)


def format_validation_report(issues: list[FaqIssue]) -> str:
    """Render FAQ validation issues as a human-readable text report."""
    lines = [f"FAQ Validation Report ({len(issues)} issue(s) found)", ""]
    for issue in issues:
        lines.append(f'  "{issue.question}": {issue.message}')
    return "\n".join(lines)


def items_from_dict(raw_items: list[dict[str, str]]) -> list[FaqItem]:
    """Build :class:`FaqItem` objects from parsed JSON/dict data."""
    return [FaqItem(question=raw["question"], answer=raw["answer"]) for raw in raw_items]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.faq_generator faq.json``.

    The JSON file is a list of ``{"question": "...", "answer": "..."}`` objects.
    """
    import argparse
    import json

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate a Markdown FAQ section and FAQPage schema from Q&A pairs.")
    parser.add_argument("faq_file", help="Path to a JSON file: a list of {question, answer} objects")
    args = parser.parse_args(argv)

    try:
        with open(args.faq_file, encoding="utf-8") as f:
            items = items_from_dict(json.load(f))
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        logging.error("Could not load FAQ items: %s", exc)
        return 1

    issues = validate_faq_items(items)
    if issues:
        print(format_validation_report(issues))
        print()

    try:
        print(generate_faq_markdown(items))
        print(generate_faq_schema_tag(items))
    except ValueError as exc:
        logging.error("FAQ generation failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
