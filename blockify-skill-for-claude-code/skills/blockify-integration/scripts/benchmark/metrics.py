"""
Centralized mathematical functions for benchmark calculations.

Ported from blockify-frontend/src/components/.../reports/lib/reportMath.ts
All calculations should use these functions to ensure consistency.
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter


# Constants (matching frontend)
CHAR_TO_TOKEN_RATIO = 4
ENTERPRISE_DUP_FACTOR = 15
DEFAULT_TOKEN_COST_PER_MILLION = 0.72  # LLAMA 3.3 70B model
DEFAULT_QUERIES_PER_RESULT = 5
DEFAULT_NUMBER_OF_USER_QUERIES = 1000

# Common words to filter in word frequency analysis
STOP_WORDS = frozenset([
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'with', 'by', 'of', 'is', 'are', 'was', 'were', 'can', 'that', 'as',
    'be', 'use', 'more', 'this', 'their', 'from', 'it', 'have', 'how',
    'using', 'new', 'across', 'into', 'between', 'among', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
    'why', 'all', 'any', 'some', 'one', 'two', 'three', 'four', 'five',
    'six', 'seven', 'eight', 'nine', 'ten', 'not', 'they', 'other',
    'another', 'such', 'no', 'yes', 'out', 'up', 'down', 'back', 'off',
    'onto', 'via', 'our', 'your', 'its', 'has', 'had', 'been', 'being',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
    'might', 'must', 'shall', 'if', 'than', 'so', 'just', 'also', 'only',
    'very', 'too', 'each', 'which', 'who', 'whom', 'what', 'these', 'those'
])


def calculate_vector_improvement(chunk_distance: float, distilled_distance: float) -> float:
    """Calculate vector accuracy improvement factor.

    Args:
        chunk_distance: Average distance for traditional chunking
        distilled_distance: Average distance for Blockify distilled results

    Returns:
        Improvement factor (higher is better). Returns 0 if inputs invalid.
    """
    if not chunk_distance or not distilled_distance:
        return 0.0
    if chunk_distance <= 0 or distilled_distance <= 0:
        return 0.0
    return chunk_distance / distilled_distance


def calculate_word_improvement(document_words: int, distilled_words: int) -> float:
    """Calculate word count improvement factor.

    Args:
        document_words: Original document word count
        distilled_words: Distilled content word count

    Returns:
        Improvement factor (higher is better). Returns 0 if inputs invalid.
    """
    if not document_words or not distilled_words:
        return 0.0
    if document_words <= 0 or distilled_words <= 0:
        return 0.0
    return document_words / distilled_words


def calculate_char_improvement(document_chars: int, distilled_chars: int) -> float:
    """Calculate character count improvement factor.

    Args:
        document_chars: Original document character count
        distilled_chars: Distilled content character count

    Returns:
        Improvement factor (higher is better). Returns 0 if inputs invalid.
    """
    if not document_chars or not distilled_chars:
        return 0.0
    if document_chars <= 0 or distilled_chars <= 0:
        return 0.0
    return document_chars / distilled_chars


def calculate_aggregate_performance(vector_improvement: float, word_improvement: float) -> float:
    """Calculate aggregate performance (vector accuracy x word improvement).

    Args:
        vector_improvement: Vector accuracy improvement factor
        word_improvement: Word count improvement factor

    Returns:
        Combined improvement factor
    """
    if not vector_improvement or not word_improvement:
        return vector_improvement or 0.0
    return vector_improvement * word_improvement


def calculate_projected_performance(
    vector_improvement: float,
    word_improvement: float,
    enterprise_factor: float = ENTERPRISE_DUP_FACTOR
) -> float:
    """Calculate projected enterprise aggregate performance.

    Args:
        vector_improvement: Vector accuracy improvement factor
        word_improvement: Word count improvement factor
        enterprise_factor: Enterprise data duplication factor (default 15x)

    Returns:
        Projected enterprise aggregate performance
    """
    return vector_improvement * word_improvement * enterprise_factor


def calculate_projected_word_improvement(
    base_word_improvement: float,
    enterprise_factor: float = ENTERPRISE_DUP_FACTOR
) -> float:
    """Calculate projected enterprise word improvement.

    Args:
        base_word_improvement: Base word improvement factor
        enterprise_factor: Enterprise data duplication factor

    Returns:
        Projected enterprise word improvement
    """
    if not base_word_improvement or not enterprise_factor:
        return base_word_improvement or 0.0
    return base_word_improvement * enterprise_factor


def calculate_distilled_vs_undistilled_improvement(
    undistilled_distance: float,
    distilled_distance: float
) -> float:
    """Calculate distilled vs undistilled improvement percentage.

    Args:
        undistilled_distance: Distance for undistilled blocks
        distilled_distance: Distance for distilled blocks

    Returns:
        Improvement percentage
    """
    if not undistilled_distance or not distilled_distance:
        return 0.0
    if undistilled_distance <= 0:
        return 0.0
    return ((undistilled_distance - distilled_distance) / undistilled_distance) * 100


def calculate_vector_distance_improvement_percentage(
    chunk_distance: float,
    distilled_distance: float
) -> float:
    """Calculate vector distance improvement percentage.

    Args:
        chunk_distance: Distance for traditional chunking
        distilled_distance: Distance for distilled blocks

    Returns:
        Improvement percentage
    """
    if not chunk_distance or not distilled_distance:
        return 0.0
    if chunk_distance <= 0:
        return 0.0
    return ((chunk_distance - distilled_distance) / chunk_distance) * 100


def calculate_average_distance(distances: List[float]) -> float:
    """Calculate average from list of distances.

    Args:
        distances: List of distance values

    Returns:
        Average distance, or 0 if invalid input
    """
    if not distances:
        return 0.0

    valid = [d for d in distances if isinstance(d, (int, float)) and not math.isnan(d)]
    if not valid:
        return 0.0

    return sum(valid) / len(valid)


def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.

    Note: Assumes vectors are already normalized (OpenAI embeddings are).
    For normalized vectors, dot product equals cosine similarity.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity (0 to 1)
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    return sum(a * b for a, b in zip(vec1, vec2))


def calculate_cosine_distance(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine distance between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine distance (1 - similarity)
    """
    return 1.0 - calculate_cosine_similarity(vec1, vec2)


def count_block_chars(block: Dict[str, Any]) -> int:
    """Count characters in block content (name + question + answer).

    Args:
        block: Block dict with name, critical_question, trusted_answer

    Returns:
        Total character count
    """
    name = block.get('name', '') or ''
    question = block.get('critical_question', '') or ''
    answer = block.get('trusted_answer', '') or ''
    return len(name) + len(question) + len(answer)


def calculate_token_stats(
    distilled_blocks: List[Dict],
    undistilled_blocks: List[Dict],
    chunks: List[Dict],
    number_of_user_queries: int = DEFAULT_NUMBER_OF_USER_QUERIES,
    token_cost_per_million: float = DEFAULT_TOKEN_COST_PER_MILLION
) -> Dict[str, Any]:
    """Calculate comprehensive token statistics.

    Args:
        distilled_blocks: List of distilled IdeaBlock dicts
        undistilled_blocks: List of undistilled IdeaBlock dicts
        chunks: List of chunk dicts with 'text' key
        number_of_user_queries: Annual user queries for projections
        token_cost_per_million: Cost per million tokens

    Returns:
        Dict with all token metrics
    """
    # Calculate total characters for each type
    total_distilled_chars = sum(count_block_chars(b) for b in distilled_blocks)
    total_undistilled_chars = sum(count_block_chars(b) for b in undistilled_blocks)
    total_chunk_chars = sum(len(c.get('text', '')) for c in chunks)

    # Convert to tokens
    total_distilled_tokens = round(total_distilled_chars / CHAR_TO_TOKEN_RATIO)
    total_undistilled_tokens = round(total_undistilled_chars / CHAR_TO_TOKEN_RATIO)
    total_chunk_tokens = round(total_chunk_chars / CHAR_TO_TOKEN_RATIO)

    # Calculate per-item averages
    tokens_per_distilled = (
        round(total_distilled_tokens / len(distilled_blocks))
        if distilled_blocks else 0
    )
    tokens_per_undistilled = (
        round(total_undistilled_tokens / len(undistilled_blocks))
        if undistilled_blocks else 0
    )
    tokens_per_chunk = (
        round(total_chunk_tokens / len(chunks))
        if chunks else 0
    )

    # Calculate annual consumption (assuming top 5 results per query)
    annual_distilled_tokens = tokens_per_distilled * number_of_user_queries * DEFAULT_QUERIES_PER_RESULT
    annual_undistilled_tokens = tokens_per_undistilled * number_of_user_queries * DEFAULT_QUERIES_PER_RESULT
    annual_chunk_tokens = tokens_per_chunk * number_of_user_queries * DEFAULT_QUERIES_PER_RESULT

    # Calculate token efficiency improvement
    token_improvement = (
        annual_chunk_tokens / annual_distilled_tokens
        if annual_distilled_tokens > 0 and annual_chunk_tokens > 0 else 0.0
    )

    # Calculate cost savings (chunks - distilled)
    cost_savings_per_year = (
        (annual_chunk_tokens - annual_distilled_tokens) * token_cost_per_million / 1_000_000
    )

    return {
        'tokens_per_distilled': tokens_per_distilled,
        'tokens_per_undistilled': tokens_per_undistilled,
        'tokens_per_chunk': tokens_per_chunk,
        'total_distilled_tokens': total_distilled_tokens,
        'total_undistilled_tokens': total_undistilled_tokens,
        'total_chunk_tokens': total_chunk_tokens,
        'annual_distilled_tokens': annual_distilled_tokens,
        'annual_undistilled_tokens': annual_undistilled_tokens,
        'annual_chunk_tokens': annual_chunk_tokens,
        'token_improvement': token_improvement,
        'cost_savings_per_year': cost_savings_per_year,
        'number_of_user_queries': number_of_user_queries,
    }


def count_words_and_characters(text: str) -> Dict[str, int]:
    """Count words and characters in text.

    Args:
        text: Input text

    Returns:
        Dict with 'word_count' and 'char_count'
    """
    if not text:
        return {'word_count': 0, 'char_count': 0}

    # Replace newlines and tabs with spaces
    normalized = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    # Count characters
    char_count = len(normalized)

    # Count words (split by whitespace)
    words = [w for w in normalized.split() if w]
    word_count = len(words)

    return {'word_count': word_count, 'char_count': char_count}


def analyze_word_frequencies(text: str, top_n: int = 30) -> List[Tuple[str, int]]:
    """Analyze word frequencies in text.

    Args:
        text: Input text
        top_n: Number of top words to return

    Returns:
        List of (word, count) tuples sorted by frequency (descending)
    """
    if not text:
        return []

    # Normalize and split into words
    normalized = text.lower().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    # Remove punctuation and split
    import re
    words = re.findall(r'\b[a-z]+\b', normalized)

    # Filter stop words and short words
    filtered = [w for w in words if w not in STOP_WORDS and len(w) > 2]

    # Count frequencies
    counter = Counter(filtered)

    # Return top N
    return counter.most_common(top_n)


def validate_benchmark_distances(
    chunk_distance: float,
    undistilled_distance: float,
    distilled_distance: float
) -> bool:
    """Validate that benchmark distances are valid numbers.

    Args:
        chunk_distance: Distance for traditional chunks
        undistilled_distance: Distance for undistilled blocks
        distilled_distance: Distance for distilled blocks

    Returns:
        True if all distances are valid positive numbers
    """
    for d in [chunk_distance, undistilled_distance, distilled_distance]:
        if not isinstance(d, (int, float)):
            return False
        if math.isnan(d) or d <= 0:
            return False
    return True
