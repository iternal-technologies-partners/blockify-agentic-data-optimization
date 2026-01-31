"""Tests for LSH bucketing."""

import numpy as np
import pytest

from app.dedupe.lsh import LSHIndex, create_lsh_buckets, find_similar_pairs_with_lsh


def test_lsh_index_basic():
    """Test basic LSH index functionality."""
    dim = 128
    lsh = LSHIndex(dim, num_tables=5, num_bits=4)

    # Create some random vectors
    vectors = np.random.randn(20, dim).astype(np.float32)
    lsh.index(vectors)

    # Get candidate pairs
    candidates = lsh.get_candidate_pairs()

    # Should return a set of tuples
    assert isinstance(candidates, set)
    for pair in candidates:
        assert len(pair) == 2
        assert pair[0] < pair[1]


def test_create_lsh_buckets_small_dataset():
    """Test that small datasets use single bucket."""
    embeddings = np.random.randn(10, 128).astype(np.float32)
    buckets = create_lsh_buckets(embeddings)

    # Small dataset should return single bucket with all items
    assert len(buckets) == 1
    assert len(buckets[0]) == 10


def test_find_similar_pairs_with_lsh():
    """Test similarity search using LSH."""
    np.random.seed(42)

    # Create embeddings with some similar pairs
    dim = 128
    n = 100
    embeddings = np.random.randn(n, dim).astype(np.float32)

    # Make some pairs very similar
    embeddings[1] = embeddings[0] + np.random.randn(dim) * 0.01
    embeddings[3] = embeddings[2] + np.random.randn(dim) * 0.01

    pairs = find_similar_pairs_with_lsh(embeddings, threshold=0.95)

    # Should find similar pairs
    assert isinstance(pairs, list)
    for pair in pairs:
        assert len(pair) == 3  # (i, j, similarity)
        assert pair[2] >= 0.95
