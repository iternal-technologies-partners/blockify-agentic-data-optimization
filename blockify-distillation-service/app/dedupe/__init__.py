"""Deduplication algorithm modules."""

from app.dedupe.algorithm import DedupeAlgorithm, ProgressReporter
from app.dedupe.embeddings import OpenAIEmbeddingGenerator
from app.dedupe.similarity import find_similar_pairs_dense, find_similar_pairs_sparse
from app.dedupe.lsh import find_similar_pairs_with_lsh, create_lsh_buckets

__all__ = [
    "DedupeAlgorithm",
    "ProgressReporter",
    "OpenAIEmbeddingGenerator",
    "find_similar_pairs_dense",
    "find_similar_pairs_sparse",
    "find_similar_pairs_with_lsh",
    "create_lsh_buckets",
]
