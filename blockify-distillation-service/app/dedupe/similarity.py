"""Similarity computation using cosine similarity and FAISS."""

import numpy as np
import faiss
from typing import List, Tuple, Set
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

SIMILARITY_PARALLEL_THREADS = settings.similarity_parallel_threads


def compute_cosine_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """Compute cosine similarity matrix for embeddings.

    Args:
        embeddings: numpy array of shape (n_samples, n_features)

    Returns:
        Similarity matrix of shape (n_samples, n_samples)
    """
    if embeddings.size == 0:
        return np.array([])

    return cosine_similarity(embeddings)


def find_similar_pairs_sparse(
    embeddings: np.ndarray, threshold: float, k: int = None
) -> List[Tuple[int, int, float]]:
    """Find pairs of items above similarity threshold using sparse nearest-neighbor search.

    Uses parallel processing for result extraction.

    Args:
        embeddings: numpy array of shape (n_samples, n_features)
        threshold: Minimum similarity threshold
        k: Maximum number of neighbors to consider per item

    Returns:
        List of tuples (i, j, similarity_score) where i < j
    """
    if embeddings.size == 0 or embeddings.shape[0] < 2:
        return []

    n_samples, n_features = embeddings.shape

    # Set default k if not provided
    if k is None:
        k = min(50, n_samples - 1)
    else:
        k = min(k, n_samples - 1)

    logger.info(
        "Finding similar pairs with sparse search (parallel)",
        n_samples=n_samples,
        threshold=threshold,
        k=k,
        parallel_threads=SIMILARITY_PARALLEL_THREADS,
    )

    try:
        # Normalize embeddings for cosine similarity
        embeddings_normalized = embeddings.astype(np.float32)
        faiss.normalize_L2(embeddings_normalized)

        # Build FAISS index for inner product
        index = faiss.IndexFlatIP(n_features)
        index.add(embeddings_normalized)

        # Search for k nearest neighbors
        similarities, indices = index.search(embeddings_normalized, k + 1)

        # Partition sample indices for parallel processing
        chunk_size = max(1, (n_samples + SIMILARITY_PARALLEL_THREADS - 1) // SIMILARITY_PARALLEL_THREADS)
        sample_chunks = [
            range(i, min(i + chunk_size, n_samples))
            for i in range(0, n_samples, chunk_size)
        ]

        def process_sample_chunk(sample_range) -> List[Tuple[int, int, float]]:
            """Process a chunk of samples to find similar pairs (thread worker function)."""
            chunk_pairs = []
            local_seen: Set[Tuple[int, int]] = set()

            for i in sample_range:
                for j_idx in range(1, len(indices[i])):  # Skip self
                    j = indices[i][j_idx]
                    similarity = float(similarities[i][j_idx])

                    if similarity >= threshold:
                        pair = (min(i, j), max(i, j))
                        if pair not in local_seen:
                            chunk_pairs.append((pair[0], pair[1], similarity))
                            local_seen.add(pair)

            return chunk_pairs

        # Process chunks in parallel
        all_chunk_pairs = []
        with ThreadPoolExecutor(max_workers=SIMILARITY_PARALLEL_THREADS) as executor:
            futures = {executor.submit(process_sample_chunk, chunk): chunk for chunk in sample_chunks}

            for future in as_completed(futures):
                chunk_pairs = future.result()
                all_chunk_pairs.extend(chunk_pairs)

        # Deduplicate pairs across chunks
        seen_pairs: Set[Tuple[int, int]] = set()
        pairs = []
        for pair in all_chunk_pairs:
            pair_key = (pair[0], pair[1])
            if pair_key not in seen_pairs:
                pairs.append(pair)
                seen_pairs.add(pair_key)

        pairs.sort(key=lambda x: x[2], reverse=True)

        logger.info(
            "Found similar pairs with sparse search (parallel)",
            count=len(pairs),
            threshold=threshold,
        )
        return pairs

    except Exception as e:
        logger.error("Error in sparse similarity search, falling back to dense", error=str(e))
        return find_similar_pairs_dense(embeddings, threshold)


def find_similar_pairs_dense(
    embeddings: np.ndarray, threshold: float
) -> List[Tuple[int, int, float]]:
    """Find pairs of items above similarity threshold using dense matrix computation.

    Uses parallel processing for pair extraction from the similarity matrix.

    Args:
        embeddings: numpy array of shape (n_samples, n_features)
        threshold: Minimum similarity threshold

    Returns:
        List of tuples (i, j, similarity_score) where i < j
    """
    if embeddings.size == 0 or embeddings.shape[0] < 2:
        return []

    n = embeddings.shape[0]
    logger.info(
        "Using dense similarity computation (parallel)",
        n_samples=n,
        parallel_threads=SIMILARITY_PARALLEL_THREADS,
    )

    similarity_matrix = cosine_similarity(embeddings)

    # Partition rows for parallel processing
    chunk_size = max(1, (n + SIMILARITY_PARALLEL_THREADS - 1) // SIMILARITY_PARALLEL_THREADS)
    row_chunks = [
        range(i, min(i + chunk_size, n))
        for i in range(0, n, chunk_size)
    ]

    def process_row_chunk(row_range) -> List[Tuple[int, int, float]]:
        """Process a chunk of rows to find similar pairs (thread worker function)."""
        chunk_pairs = []
        for i in row_range:
            for j in range(i + 1, n):  # Only upper triangle
                similarity = similarity_matrix[i, j]
                if similarity >= threshold:
                    chunk_pairs.append((i, j, float(similarity)))
        return chunk_pairs

    # Process chunks in parallel
    pairs = []
    with ThreadPoolExecutor(max_workers=SIMILARITY_PARALLEL_THREADS) as executor:
        futures = {executor.submit(process_row_chunk, chunk): chunk for chunk in row_chunks}

        for future in as_completed(futures):
            chunk_pairs = future.result()
            pairs.extend(chunk_pairs)

    pairs.sort(key=lambda x: x[2], reverse=True)

    logger.info(
        "Found similar pairs with dense computation (parallel)",
        count=len(pairs),
        threshold=threshold,
    )
    return pairs


def find_similar_pairs(
    similarity_matrix: np.ndarray, threshold: float
) -> List[Tuple[int, int, float]]:
    """Find pairs of items above similarity threshold from precomputed matrix.

    Args:
        similarity_matrix: Square similarity matrix
        threshold: Minimum similarity threshold

    Returns:
        List of tuples (i, j, similarity_score) where i < j
    """
    pairs = []
    n = similarity_matrix.shape[0]

    for i in range(n):
        for j in range(i + 1, n):
            similarity = similarity_matrix[i, j]
            if similarity >= threshold:
                pairs.append((i, j, similarity))

    pairs.sort(key=lambda x: x[2], reverse=True)

    logger.info("Found similar pairs", count=len(pairs), threshold=threshold)
    return pairs


def compute_pairwise_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """Compute cosine similarity between two embeddings.

    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector

    Returns:
        Cosine similarity score
    """
    emb1 = embedding1.reshape(1, -1)
    emb2 = embedding2.reshape(1, -1)

    similarity = cosine_similarity(emb1, emb2)[0, 0]
    return float(similarity)
