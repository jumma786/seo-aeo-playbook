"""Score content passages for GEO (Generative Engine Optimization) citability.

Applies the passage-level citability criteria from
``docs/books/complete/aeo/chapter-07.md`` (self-contained passages that
name their subject explicitly rather than relying on a dangling pronoun,
specific and checkable facts, structural labels like "Definition:") and
the closing GEO strategy chapter to individual paragraphs of body
content, so problem passages can be found and rewritten before
publishing — a piece of content is retrieved and cited by AI answer
engines at the passage level, not the page level.

Example:
    >>> from scripts.geo_optimizer import score_passage
    >>> score_passage("It is a metric that measures loading speed.").self_contained
    False
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

MIN_PASSAGE_WORDS = 20
MAX_PASSAGE_WORDS = 100

DANGLING_OPENERS = frozenset({"it", "this", "that", "they", "these", "those", "he", "she"})
_STRUCTURAL_LABEL_RE = re.compile(r"^(definition|note|requirement|step\s*\d+|tip|warning)\s*:", re.IGNORECASE)
_NUMBER_RE = re.compile(r"\d")

_SELF_CONTAINED_POINTS = 40.0
_LENGTH_POINTS = 30.0
_SPECIFIC_FACT_POINTS = 20.0
_STRUCTURAL_LABEL_POINTS = 10.0


@dataclass
class PassageScore:
    """The GEO citability assessment of a single passage."""

    text: str
    word_count: int
    self_contained: bool
    has_specific_fact: bool
    has_structural_label: bool
    issues: list[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        """A 0-100 heuristic citability score. Not a ranking or citation-rate prediction."""
        points = 0.0
        if self.self_contained:
            points += _SELF_CONTAINED_POINTS
        if MIN_PASSAGE_WORDS <= self.word_count <= MAX_PASSAGE_WORDS:
            points += _LENGTH_POINTS
        if self.has_specific_fact:
            points += _SPECIFIC_FACT_POINTS
        if self.has_structural_label:
            points += _STRUCTURAL_LABEL_POINTS
        return round(points, 1)


def score_passage(text: str) -> PassageScore:
    """Score a single passage/paragraph for AI-citation readiness.

    Args:
        text: A single paragraph of body content.

    Returns:
        A :class:`PassageScore` with sub-checks, issues, and a heuristic score.
    """
    stripped = text.strip()
    words = stripped.split()
    word_count = len(words)

    first_word = words[0].lower().strip(",.;:\"'") if words else ""
    self_contained = first_word not in DANGLING_OPENERS
    has_specific_fact = bool(_NUMBER_RE.search(stripped))
    has_structural_label = bool(_STRUCTURAL_LABEL_RE.match(stripped))

    issues: list[str] = []
    if not self_contained:
        issues.append(f"Passage opens with a pronoun ('{words[0]}') with no named subject in this passage")
    if word_count < MIN_PASSAGE_WORDS:
        issues.append(
            f"Passage is only {word_count} word(s) (recommended >= {MIN_PASSAGE_WORDS} to stand alone as a citation)"
        )
    elif word_count > MAX_PASSAGE_WORDS:
        issues.append(
            f"Passage is {word_count} word(s) (recommended <= {MAX_PASSAGE_WORDS}; split into smaller citable passages)"
        )
    if not has_specific_fact:
        issues.append("Passage contains no specific, checkable fact or number")

    return PassageScore(
        text=stripped,
        word_count=word_count,
        self_contained=self_contained,
        has_specific_fact=has_specific_fact,
        has_structural_label=has_structural_label,
        issues=issues,
    )


def split_into_passages(text: str) -> list[str]:
    """Split plain text or Markdown body content into paragraph-level passages.

    Args:
        text: Plain text or Markdown content, paragraphs separated by a blank line.

    Returns:
        Non-empty, stripped paragraph strings, in document order.
    """
    return [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text.strip()) if paragraph.strip()]


def extract_passages_from_html(html: str) -> list[str]:
    """Extract paragraph-level passages from a page's HTML ``<p>`` tags.

    Args:
        html: The page's HTML source.

    Returns:
        Non-empty paragraph text content, in document order.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    return [p.get_text(" ", strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]


def score_content(passages: list[str]) -> list[PassageScore]:
    """Score a list of passages, in order.

    Args:
        passages: Passages to score, typically from :func:`split_into_passages`
            or :func:`extract_passages_from_html`.

    Returns:
        One :class:`PassageScore` per passage.
    """
    scores = [score_passage(passage) for passage in passages]
    logger.info(
        "Scored %d passage(s), average score=%.1f",
        len(scores),
        round(sum(score.score for score in scores) / len(scores), 1) if scores else 0.0,
    )
    return scores


def format_report(scores: list[PassageScore]) -> str:
    """Render passage scores as a human-readable text report."""
    average = round(sum(score.score for score in scores) / len(scores), 1) if scores else 0.0
    lines = [f"GEO Citability Report ({len(scores)} passage(s), average score {average}/100)", ""]
    for index, score in enumerate(scores, start=1):
        lines.append(f"Passage {index}: score={score.score}/100, words={score.word_count}")
        for issue in score.issues:
            lines.append(f"  - {issue}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.geo_optimizer content.md`` or ``page.html``.

    A ``.html`` file has its ``<p>`` tags scored; any other file is treated
    as plain text/Markdown, split into blank-line-separated paragraphs.
    """
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Score content passages for GEO/AI-citation readiness.")
    parser.add_argument("content_file", help="Path to a .md/.txt file or an .html file")
    args = parser.parse_args(argv)

    try:
        with open(args.content_file, encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        logging.error("Could not read %s: %s", args.content_file, exc)
        return 1

    if args.content_file.lower().endswith(".html"):
        passages = extract_passages_from_html(content)
    else:
        passages = split_into_passages(content)

    print(format_report(score_content(passages)))
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
