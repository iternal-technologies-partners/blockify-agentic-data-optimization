"""Tests for similarity computation."""

import numpy as np
import pytest

from app.dedupe.similarity import (
    compute_cosine_similarity_matrix,
    find_similar_pairs_dense,
    compute_pairwise_similarity,
)


def test_compute_cosine_similarity_matrix():
    """Test cosine similarity matrix computation."""
    embeddings = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    similarity = compute_cosine_similarity_matrix(embeddings)

    assert similarity.shape == (3, 3)
    # Diagonal should be 1 (self-similarity)
    np.testing.assert_array_almost_equal(np.diag(similarity), [1.0, 1.0, 1.0])


def test_find_similar_pairs_dense():
    """Test finding similar pairs above threshold."""
    # Two similar vectors and one different
    embeddings = np.array([[1.0, 0.0, 0.0], [0.99, 0.1, 0.0], [0.0, 0.0, 1.0]])

    pairs = find_similar_pairs_dense(embeddings, threshold=0.9)

    # Should find the pair (0, 1) as similar
    assert len(pairs) >= 1
    pair_indices = [(p[0], p[1]) for p in pairs]
    assert (0, 1) in pair_indices


def test_find_similar_pairs_empty():
    """Test with empty embeddings."""
    embeddings = np.array([])
    pairs = find_similar_pairs_dense(embeddings, threshold=0.5)
    assert pairs == []


def test_compute_pairwise_similarity():
    """Test pairwise similarity between two vectors."""
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    similarity = compute_pairwise_similarity(v1, v2)
    assert abs(similarity - 1.0) < 0.001

    v3 = np.array([0.0, 1.0, 0.0])
    similarity = compute_pairwise_similarity(v1, v3)
    assert abs(similarity) < 0.001
