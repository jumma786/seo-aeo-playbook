"""Unit tests for scripts.keyword_cluster."""

from __future__ import annotations

import pytest

from scripts.keyword_cluster import (
    cluster_keywords,
    jaccard_similarity,
    normalize_tokens,
)


class TestNormalizeTokens:
    def test_lowercases_and_strips_punctuation(self) -> None:
        assert normalize_tokens("Best Running-Shoes!") == {"best", "running", "shoes"}

    def test_removes_stopwords(self) -> None:
        assert normalize_tokens("How to Bake Bread") == {"bake", "bread"}

    def test_empty_string_returns_empty_set(self) -> None:
        assert normalize_tokens("") == set()


class TestJaccardSimilarity:
    def test_identical_sets_score_one(self) -> None:
        assert jaccard_similarity({"a", "b"}, {"a", "b"}) == 1.0

    def test_disjoint_sets_score_zero(self) -> None:
        assert jaccard_similarity({"a"}, {"b"}) == 0.0

    def test_both_empty_scores_zero(self) -> None:
        assert jaccard_similarity(set(), set()) == 0.0

    def test_partial_overlap(self) -> None:
        score = jaccard_similarity({"a", "b", "c"}, {"b", "c", "d"})
        assert score == pytest.approx(2 / 4)


class TestClusterKeywords:
    def test_similar_keywords_grouped(self) -> None:
        clusters = cluster_keywords(
            [
                "best running shoes",
                "best trail running shoes",
                "how to bake sourdough bread",
                "sourdough bread recipe",
            ]
        )
        assert len(clusters) == 2
        shoe_cluster = next(c for c in clusters if "running shoes" in c.label)
        assert "best trail running shoes" in shoe_cluster.keywords

    def test_empty_input_returns_no_clusters(self) -> None:
        assert cluster_keywords([]) == []

    def test_duplicate_keywords_deduplicated(self) -> None:
        clusters = cluster_keywords(["best running shoes", "Best Running Shoes", "  "])
        assert len(clusters) == 1
        assert len(clusters[0].keywords) == 1

    def test_completely_unrelated_keywords_form_separate_clusters(self) -> None:
        clusters = cluster_keywords(["running shoes", "car insurance quotes", "wedding photography tips"])
        assert len(clusters) == 3

    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(ValueError):
            cluster_keywords(["a"], similarity_threshold=1.5)

    def test_threshold_zero_merges_everything_with_shared_tokens(self) -> None:
        # A threshold of 0.0 still requires >0 tokens in common to beat the
        # "score > best_score" strict-improvement check on ties.
        clusters = cluster_keywords(
            ["running shoes", "running gear", "running apparel"], similarity_threshold=0.0
        )
        assert len(clusters) == 1
