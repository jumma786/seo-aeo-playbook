"""Cluster keywords into topical groups using lexical (token-overlap) similarity.

This is a lightweight, offline clustering method suitable for quick topic
grouping without calling an external SERP-overlap or embeddings API. For
true SERP-based clustering (grouping by actual ranking-page overlap), see
the ``seo-cluster`` skill/agent documented in this repository's README.

Example:
    >>> from scripts.keyword_cluster import cluster_keywords
    >>> clusters = cluster_keywords([
    ...     "best running shoes",
    ...     "best trail running shoes",
    ...     "how to bake sourdough bread",
    ...     "sourdough bread recipe",
    ... ])
    >>> len(clusters)
    2
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Common English stopwords excluded from similarity comparisons so clusters
# form around meaningful topic words rather than filler words.
STOPWORDS = frozenset(
    {
        "a", "an", "the", "and", "or", "but", "for", "of", "to", "in", "on",
        "at", "is", "are", "was", "were", "be", "how", "what", "why", "when",
        "where", "who", "which", "with", "by", "from", "this", "that", "it",
        "do", "does", "did", "can", "will", "should", "i", "you", "your",
        "my", "vs", "near", "me",
    }
)

DEFAULT_SIMILARITY_THRESHOLD = 0.34


@dataclass
class KeywordCluster:
    """A group of keywords judged topically similar to one another."""

    label: str
    keywords: list[str] = field(default_factory=list)

    def add(self, keyword: str) -> None:
        self.keywords.append(keyword)


def normalize_tokens(keyword: str) -> set[str]:
    """Lowercase, tokenize, and strip stopwords from a keyword phrase.

    Args:
        keyword: A raw keyword or query string.

    Returns:
        The set of significant (non-stopword) tokens.
    """
    words = re.findall(r"[a-z0-9]+", keyword.lower())
    return {w for w in words if w not in STOPWORDS}


def jaccard_similarity(a: set[str], b: set[str]) -> float:
    """Compute Jaccard similarity between two token sets.

    Args:
        a: First token set.
        b: Second token set.

    Returns:
        A similarity score between 0.0 (no overlap) and 1.0 (identical sets).
        Returns 0.0 if both sets are empty.
    """
    if not a and not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def cluster_keywords(
    keywords: list[str],
    *,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> list[KeywordCluster]:
    """Group keywords into clusters using pairwise token-overlap similarity.

    Uses a simple greedy single-linkage approach: each keyword joins the
    first existing cluster where its similarity to any member exceeds the
    threshold, otherwise it starts a new cluster.

    Args:
        keywords: The list of keyword strings to cluster. Duplicates and
            blank entries are ignored.
        similarity_threshold: Minimum Jaccard similarity (0.0-1.0) required
            for a keyword to join an existing cluster.

    Returns:
        A list of :class:`KeywordCluster`, each labeled after its first
        (seed) keyword, in the order clusters were created.

    Raises:
        ValueError: If similarity_threshold is not between 0.0 and 1.0.
    """
    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError(f"similarity_threshold must be between 0.0 and 1.0, got {similarity_threshold}")

    seen: set[str] = set()
    clusters: list[KeywordCluster] = []
    cluster_tokens: list[set[str]] = []

    for raw_keyword in keywords:
        keyword = raw_keyword.strip()
        if not keyword or keyword.lower() in seen:
            continue
        seen.add(keyword.lower())

        tokens = normalize_tokens(keyword)
        best_cluster_index = None
        best_score = 0.0
        for index, existing_tokens in enumerate(cluster_tokens):
            score = jaccard_similarity(tokens, existing_tokens)
            if score >= similarity_threshold and score > best_score:
                best_cluster_index = index
                best_score = score

        if best_cluster_index is not None:
            clusters[best_cluster_index].add(keyword)
            cluster_tokens[best_cluster_index] |= tokens
        else:
            clusters.append(KeywordCluster(label=keyword, keywords=[keyword]))
            cluster_tokens.append(set(tokens))

    logger.info("Clustered %d keywords into %d clusters", len(seen), len(clusters))
    return clusters


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.keyword_cluster keywords.txt``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Cluster keywords by lexical similarity.")
    parser.add_argument("keywords_file", help="Path to a text file, one keyword per line")
    parser.add_argument("--threshold", type=float, default=DEFAULT_SIMILARITY_THRESHOLD)
    args = parser.parse_args(argv)

    try:
        with open(args.keywords_file, encoding="utf-8") as f:
            keywords = [line.strip() for line in f if line.strip()]
    except OSError as exc:
        logging.error("Could not read %s: %s", args.keywords_file, exc)
        return 1

    clusters = cluster_keywords(keywords, similarity_threshold=args.threshold)
    for cluster in clusters:
        print(f"# {cluster.label}")
        for keyword in cluster.keywords:
            print(f"  - {keyword}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
