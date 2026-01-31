"""Locality-Sensitive Hashing (LSH) for efficient similarity bucketing.

This module implements LSH to reduce the O(n^2) pairwise comparison problem
by grouping similar items into buckets before comparing.
"""

import numpy as np
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

# Configuration constants
MIN_ITEMS_TO_ENABLE_LSH = 50  # Only use LSH for datasets larger than this
NUM_HASH_TABLES = 10  # Number of hash tables
NUM_HASH_BITS = 8  # Number of bits per hash
SIMILARITY_PARALLEL_THREADS = settings.similarity_parallel_threads


class LSHIndex:
    """Locality-Sensitive Hashing index for cosine similarity."""

    def __init__(
        self,
        dim: int,
        num_tables: int = NUM_HASH_TABLES,
        num_bits: int = NUM_HASH_BITS,
    ):
        """Initialize LSH index.

        Args:
            dim: Dimension of vectors
            num_tables: Number of hash tables
            num_bits: Number of bits per hash
        """
        self.dim = dim
        self.num_tables = num_tables
        self.num_bits = num_bits

        # Generate random hyperplanes for each table
        self.hyperplanes = [
            np.random.randn(num_bits, dim).astype(np.float32) for _ in range(num_tables)
        ]

        # Hash tables: table_idx -> hash_value -> set of item indices
        self.tables: List[Dict[int, Set[int]]] = [
            defaultdict(set) for _ in range(num_tables)
        ]

    def _hash_vector(self, vector: np.ndarray, table_idx: int) -> int:
        """Compute hash value for a vector in a specific table."""
        hyperplane = self.hyperplanes[table_idx]
        projections = np.dot(hyperplane, vector)
        bits = (projections > 0).astype(int)
        hash_value = int(sum(bit << i for i, bit in enumerate(bits)))
        return hash_value

    def index(self, vectors: np.ndarray) -> None:
        """Index all vectors into the hash tables.

        Args:
            vectors: Array of shape (n_items, dim)
        """
        n_items = vectors.shape[0]

        for idx in range(n_items):
            vector = vectors[idx]
            for table_idx in range(self.num_tables):
                hash_value = self._hash_vector(vector, table_idx)
                self.tables[table_idx][hash_value].add(idx)

    def get_candidate_pairs(self) -> Set[Tuple[int, int]]:
        """Get all candidate pairs that share at least one bucket.

        Returns:
            Set of (i, j) tuples where i < j
        """
        candidates = set()

        for table in self.tables:
            for bucket in table.values():
                if len(bucket) > 1:
                    bucket_list = sorted(bucket)
                    for i in range(len(bucket_list)):
                        for j in range(i + 1, len(bucket_list)):
                            candidates.add((bucket_list[i], bucket_list[j]))

        return candidates

    def get_buckets(self) -> List[List[int]]:
        """Get non-overlapping buckets for initial grouping.

        Returns:
            List of buckets, each containing item indices
        """
        buckets = []
        seen = set()

        for hash_value, items in self.tables[0].items():
            bucket = [idx for idx in items if idx not in seen]
            if bucket:
                buckets.append(bucket)
                seen.update(bucket)

        return buckets


def create_lsh_buckets(embeddings: np.ndarray) -> List[List[int]]:
    """Create LSH buckets for similarity matching.

    Args:
        embeddings: Array of shape (n_items, dim)

    Returns:
        List of buckets, each containing item indices
    """
    n_items = embeddings.shape[0]

    if n_items < MIN_ITEMS_TO_ENABLE_LSH:
        logger.info("Small dataset, using single bucket", n_items=n_items)
        return [list(range(n_items))]

    dim = embeddings.shape[1]

    lsh = LSHIndex(dim)
    lsh.index(embeddings)

    buckets = lsh.get_buckets()

    logger.info(
        "Created LSH buckets",
        n_items=n_items,
        n_buckets=len(buckets),
        avg_bucket_size=n_items / len(buckets) if buckets else 0,
    )

    return buckets


def find_similar_pairs_with_lsh(
    embeddings: np.ndarray, threshold: float
) -> List[Tuple[int, int, float]]:
    """Find similar pairs using LSH for candidate generation.

    Uses parallel similarity computation for improved performance.

    Args:
        embeddings: Array of shape (n_items, dim)
        threshold: Similarity threshold

    Returns:
        List of (i, j, similarity) tuples where similarity >= threshold
    """
    n_items = embeddings.shape[0]

    if n_items < MIN_ITEMS_TO_ENABLE_LSH:
        from app.dedupe.similarity import find_similar_pairs_dense

        return find_similar_pairs_dense(embeddings, threshold)

    dim = embeddings.shape[1]

    lsh = LSHIndex(dim)
    lsh.index(embeddings)

    candidates = lsh.get_candidate_pairs()

    logger.info(
        "LSH candidate generation",
        n_items=n_items,
        n_candidates=len(candidates),
        reduction_ratio=len(candidates) / (n_items * (n_items - 1) / 2) if n_items > 1 else 0,
    )

    # Normalize embeddings for cosine similarity (shared across threads)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    normalized = embeddings / norms

    # Partition candidates into chunks for parallel processing
    candidates_list = list(candidates)
    n_candidates = len(candidates_list)

    if n_candidates == 0:
        return []

    # Calculate chunk size based on thread count
    chunk_size = max(1, (n_candidates + SIMILARITY_PARALLEL_THREADS - 1) // SIMILARITY_PARALLEL_THREADS)
    chunks = [
        candidates_list[i:i + chunk_size]
        for i in range(0, n_candidates, chunk_size)
    ]

    logger.info(
        "LSH parallel similarity computation",
        n_candidates=n_candidates,
        n_chunks=len(chunks),
        parallel_threads=SIMILARITY_PARALLEL_THREADS,
    )

    def compute_chunk_similarities(chunk: List[Tuple[int, int]]) -> List[Tuple[int, int, float]]:
        """Compute similarities for a chunk of candidate pairs (thread worker function)."""
        chunk_results = []
        for i, j in chunk:
            similarity = float(np.dot(normalized[i], normalized[j]))
            if similarity >= threshold:
                chunk_results.append((i, j, similarity))
        return chunk_results

    similar_pairs = []

    with ThreadPoolExecutor(max_workers=SIMILARITY_PARALLEL_THREADS) as executor:
        futures = {executor.submit(compute_chunk_similarities, chunk): chunk for chunk in chunks}

        for future in as_completed(futures):
            chunk_results = future.result()
            similar_pairs.extend(chunk_results)

    logger.info(
        "LSH similarity matching (parallel)",
        candidates=len(candidates),
        matches=len(similar_pairs),
        threshold=threshold,
    )

    return similar_pairs
