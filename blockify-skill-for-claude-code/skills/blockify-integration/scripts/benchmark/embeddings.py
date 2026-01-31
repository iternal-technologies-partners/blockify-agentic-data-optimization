"""
Embedding generation and distance calculations for benchmarking.

Uses OpenAI embeddings directly (not Blockify API).
"""

import os
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from openai import OpenAI

from .metrics import calculate_cosine_distance


# Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
DEFAULT_EMBEDDING_MODEL = 'text-embedding-3-small'
DEFAULT_BATCH_SIZE = 100


def get_openai_client() -> OpenAI:
    """Get OpenAI client instance."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_embeddings(
    texts: List[str],
    model: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    show_progress: bool = True
) -> List[List[float]]:
    """Generate embeddings for a list of texts using OpenAI.

    Args:
        texts: List of text strings to embed
        model: OpenAI embedding model name
        batch_size: Number of texts per API call
        show_progress: Print progress updates

    Returns:
        List of embedding vectors (each is a list of floats)
    """
    if not texts:
        return []

    client = get_openai_client()
    embeddings = []

    total_batches = (len(texts) + batch_size - 1) // batch_size

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_num = i // batch_size + 1

        if show_progress:
            print(f"  Generating embeddings: batch {batch_num}/{total_batches} ({len(batch)} items)")

        try:
            response = client.embeddings.create(model=model, input=batch)
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"  Error generating embeddings for batch {batch_num}: {e}")
            # Return empty embeddings for failed items
            embeddings.extend([[] for _ in batch])

    return embeddings


def generate_block_embeddings(
    blocks: List[Dict[str, Any]],
    model: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    show_progress: bool = True
) -> List[List[float]]:
    """Generate embeddings for IdeaBlocks.

    Embeds the concatenation of name + critical_question + trusted_answer
    (same approach as frontend).

    Args:
        blocks: List of IdeaBlock dicts
        model: OpenAI embedding model name
        batch_size: Number of texts per API call
        show_progress: Print progress updates

    Returns:
        List of embedding vectors
    """
    texts = []
    for block in blocks:
        name = block.get('name', '') or ''
        cq = block.get('critical_question', '') or ''
        ta = block.get('trusted_answer', '') or ''
        texts.append(f"{name} {cq} {ta}")

    return generate_embeddings(texts, model, batch_size, show_progress)


def generate_chunk_embeddings(
    chunks: List[Dict[str, Any]],
    model: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    show_progress: bool = True
) -> List[List[float]]:
    """Generate embeddings for text chunks.

    Args:
        chunks: List of chunk dicts with 'text' key
        model: OpenAI embedding model name
        batch_size: Number of texts per API call
        show_progress: Print progress updates

    Returns:
        List of embedding vectors
    """
    texts = [c.get('text', '') or '' for c in chunks]
    return generate_embeddings(texts, model, batch_size, show_progress)


def calculate_query_distances(
    query_embeddings: List[List[float]],
    result_embeddings: List[List[float]],
    original_items: List[Any]
) -> Dict[str, Any]:
    """Calculate distances between queries and results, finding best matches.

    For each query embedding, finds the closest result embedding and returns
    the distance and the original item.

    Uses numpy for vectorized operations - orders of magnitude faster than
    pure Python loops for large datasets.

    Args:
        query_embeddings: List of query embedding vectors
        result_embeddings: List of result embedding vectors
        original_items: List of original data items (blocks or chunks)

    Returns:
        Dict with:
            - 'distances': List of best (minimum) distances for each query
            - 'closest_matches': List of original items that were closest
            - 'match_indices': List of indices of closest matches
    """
    # Filter out empty embeddings and track valid indices
    valid_query_indices = [i for i, emb in enumerate(query_embeddings) if emb]
    valid_result_indices = [i for i, emb in enumerate(result_embeddings) if emb]

    if not valid_query_indices or not valid_result_indices:
        return {
            'distances': [float('inf')] * len(query_embeddings),
            'closest_matches': [None] * len(query_embeddings),
            'match_indices': [-1] * len(query_embeddings),
        }

    # Convert to numpy arrays for vectorized operations
    query_matrix = np.array([query_embeddings[i] for i in valid_query_indices])
    result_matrix = np.array([result_embeddings[i] for i in valid_result_indices])

    # Normalize vectors (OpenAI embeddings should already be normalized, but ensure it)
    query_norms = np.linalg.norm(query_matrix, axis=1, keepdims=True)
    result_norms = np.linalg.norm(result_matrix, axis=1, keepdims=True)
    query_matrix = query_matrix / np.where(query_norms > 0, query_norms, 1)
    result_matrix = result_matrix / np.where(result_norms > 0, result_norms, 1)

    # Compute all cosine similarities at once: (n_queries x n_results)
    # For normalized vectors, cosine similarity = dot product
    similarity_matrix = np.dot(query_matrix, result_matrix.T)

    # Convert to distances (1 - similarity)
    distance_matrix = 1.0 - similarity_matrix

    # Find best matches for each query
    best_result_indices_in_valid = np.argmin(distance_matrix, axis=1)
    best_distances = distance_matrix[np.arange(len(valid_query_indices)), best_result_indices_in_valid]

    # Map back to original indices
    best_result_indices = [valid_result_indices[i] for i in best_result_indices_in_valid]

    # Build output lists with proper indexing for invalid queries
    distances = [float('inf')] * len(query_embeddings)
    closest_matches = [None] * len(query_embeddings)
    match_indices = [-1] * len(query_embeddings)

    for i, valid_idx in enumerate(valid_query_indices):
        distances[valid_idx] = float(best_distances[i])
        result_idx = best_result_indices[i]
        match_indices[valid_idx] = result_idx
        if 0 <= result_idx < len(original_items):
            closest_matches[valid_idx] = original_items[result_idx]

    return {
        'distances': distances,
        'closest_matches': closest_matches,
        'match_indices': match_indices,
    }


def extract_queries_from_blocks(blocks: List[Dict[str, Any]]) -> List[str]:
    """Extract critical questions from blocks to use as benchmark queries.

    Args:
        blocks: List of IdeaBlock dicts

    Returns:
        List of critical question strings
    """
    queries = []
    for block in blocks:
        cq = block.get('critical_question', '')
        if cq and cq.strip():
            queries.append(cq.strip())
    return queries


def extract_unique_chunks(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract unique source chunks from block metadata.

    NOTE: This returns deduplicated chunks by hash. For raw chunk counts
    from source files, use chunk_source_files() instead.

    Args:
        blocks: List of IdeaBlock dicts with source_chunk_* metadata

    Returns:
        List of unique chunk dicts with 'text', 'index', 'hash' keys
    """
    seen_hashes = set()
    chunks = []

    for block in blocks:
        chunk_hash = block.get('source_chunk_hash', '')
        if not chunk_hash or chunk_hash in seen_hashes:
            continue

        chunk_text = block.get('source_chunk_text', '')
        if not chunk_text:
            continue

        seen_hashes.add(chunk_hash)
        chunks.append({
            'text': chunk_text,
            'index': block.get('source_chunk_index', len(chunks)),
            'hash': chunk_hash,
        })

    # Sort by index
    chunks.sort(key=lambda c: c.get('index', 0))
    return chunks


def chunk_source_files(
    source_dir: str,
    chunk_size: int = 2000,
    overlap: int = 200
) -> List[Dict[str, Any]]:
    """Chunk all source files in a directory without deduplication.

    This provides the true baseline for traditional RAG comparison -
    all chunks from all files, including duplicates.

    Args:
        source_dir: Path to directory containing source files
        chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks in characters

    Returns:
        List of chunk dicts with 'text', 'index', 'source_file' keys
    """
    from pathlib import Path

    def _chunk_text(text: str) -> List[str]:
        """Split text into overlapping chunks."""
        sentences = text.replace('\n', ' ').split('. ')
        chunks = []
        current = []
        length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence += '. '

            if length + len(sentence) > chunk_size and current:
                chunks.append(''.join(current))
                overlap_text = ''.join(current)[-overlap:]
                current = [overlap_text, sentence]
                length = len(overlap_text) + len(sentence)
            else:
                current.append(sentence)
                length += len(sentence)

        if current:
            chunks.append(''.join(current))

        return chunks

    all_chunks = []
    source_path = Path(source_dir)

    # Find all text files
    files = list(source_path.glob('**/*.md')) + list(source_path.glob('**/*.txt'))

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

            file_chunks = _chunk_text(text)
            for i, chunk_text in enumerate(file_chunks):
                all_chunks.append({
                    'text': chunk_text,
                    'index': len(all_chunks),
                    'source_file': filepath.name,
                })
        except Exception as e:
            print(f"  Warning: Could not read {filepath}: {e}")

    return all_chunks
