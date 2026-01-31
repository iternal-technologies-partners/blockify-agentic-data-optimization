"""
Unit tests for benchmark metrics calculations.

Run with: pytest tests/test_metrics.py -v
"""

import sys
import math
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from benchmark.metrics import (
    CHAR_TO_TOKEN_RATIO,
    ENTERPRISE_DUP_FACTOR,
    calculate_vector_improvement,
    calculate_word_improvement,
    calculate_char_improvement,
    calculate_aggregate_performance,
    calculate_projected_performance,
    calculate_projected_word_improvement,
    calculate_distilled_vs_undistilled_improvement,
    calculate_vector_distance_improvement_percentage,
    calculate_average_distance,
    calculate_cosine_similarity,
    calculate_cosine_distance,
    count_block_chars,
    calculate_token_stats,
    count_words_and_characters,
    analyze_word_frequencies,
    validate_benchmark_distances,
)


class TestConstants:
    """Test that constants are correctly defined."""

    def test_char_to_token_ratio(self):
        assert CHAR_TO_TOKEN_RATIO == 4

    def test_enterprise_dup_factor(self):
        assert ENTERPRISE_DUP_FACTOR == 15


class TestVectorImprovement:
    """Tests for calculate_vector_improvement function."""

    def test_normal_improvement(self):
        # chunk_distance=0.4, distilled_distance=0.2 → 2.0x improvement
        result = calculate_vector_improvement(0.4, 0.2)
        assert result == 2.0

    def test_no_improvement(self):
        # Same distances → 1.0x
        result = calculate_vector_improvement(0.3, 0.3)
        assert result == 1.0

    def test_worse_performance(self):
        # distilled worse than chunks → <1.0
        result = calculate_vector_improvement(0.2, 0.4)
        assert result == 0.5

    def test_zero_chunk_distance(self):
        # Zero chunk distance → 0 (invalid)
        result = calculate_vector_improvement(0, 0.2)
        assert result == 0.0

    def test_zero_distilled_distance(self):
        # Zero distilled distance → 0 (invalid, would be infinite)
        result = calculate_vector_improvement(0.4, 0)
        assert result == 0.0

    def test_negative_values(self):
        # Negative values → 0 (invalid)
        result = calculate_vector_improvement(-0.4, 0.2)
        assert result == 0.0
        result = calculate_vector_improvement(0.4, -0.2)
        assert result == 0.0

    def test_none_values(self):
        # None values → 0
        result = calculate_vector_improvement(None, 0.2)
        assert result == 0.0
        result = calculate_vector_improvement(0.4, None)
        assert result == 0.0


class TestWordImprovement:
    """Tests for calculate_word_improvement function."""

    def test_normal_improvement(self):
        # 10000 words → 400 words = 25x improvement
        result = calculate_word_improvement(10000, 400)
        assert result == 25.0

    def test_no_improvement(self):
        result = calculate_word_improvement(1000, 1000)
        assert result == 1.0

    def test_zero_values(self):
        assert calculate_word_improvement(0, 400) == 0.0
        assert calculate_word_improvement(10000, 0) == 0.0


class TestCharImprovement:
    """Tests for calculate_char_improvement function."""

    def test_normal_improvement(self):
        result = calculate_char_improvement(50000, 2000)
        assert result == 25.0

    def test_zero_values(self):
        assert calculate_char_improvement(0, 2000) == 0.0
        assert calculate_char_improvement(50000, 0) == 0.0


class TestAggregatePerformance:
    """Tests for calculate_aggregate_performance function."""

    def test_normal_calculation(self):
        # 2.0 × 25.0 = 50.0
        result = calculate_aggregate_performance(2.0, 25.0)
        assert result == 50.0

    def test_one_zero(self):
        # If either is zero, return the other or 0
        result = calculate_aggregate_performance(2.0, 0)
        assert result == 2.0  # Returns vector_improvement
        result = calculate_aggregate_performance(0, 25.0)
        assert result == 0.0

    def test_both_zero(self):
        result = calculate_aggregate_performance(0, 0)
        assert result == 0.0


class TestProjectedPerformance:
    """Tests for calculate_projected_performance function."""

    def test_default_factor(self):
        # 2.0 × 25.0 × 15 = 750.0
        result = calculate_projected_performance(2.0, 25.0)
        assert result == 750.0

    def test_custom_factor(self):
        # 2.0 × 25.0 × 10 = 500.0
        result = calculate_projected_performance(2.0, 25.0, 10)
        assert result == 500.0


class TestProjectedWordImprovement:
    """Tests for calculate_projected_word_improvement function."""

    def test_default_factor(self):
        # 25.0 × 15 = 375.0
        result = calculate_projected_word_improvement(25.0)
        assert result == 375.0

    def test_custom_factor(self):
        result = calculate_projected_word_improvement(25.0, 10)
        assert result == 250.0

    def test_zero_improvement(self):
        result = calculate_projected_word_improvement(0)
        assert result == 0.0


class TestDistilledVsUndistilledImprovement:
    """Tests for calculate_distilled_vs_undistilled_improvement function."""

    def test_improvement_percentage(self):
        # (0.3 - 0.2) / 0.3 * 100 = 33.33%
        result = calculate_distilled_vs_undistilled_improvement(0.3, 0.2)
        assert abs(result - 33.333) < 0.01

    def test_no_improvement(self):
        result = calculate_distilled_vs_undistilled_improvement(0.3, 0.3)
        assert result == 0.0


class TestVectorDistanceImprovementPercentage:
    """Tests for calculate_vector_distance_improvement_percentage function."""

    def test_improvement_percentage(self):
        # (0.4 - 0.2) / 0.4 * 100 = 50%
        result = calculate_vector_distance_improvement_percentage(0.4, 0.2)
        assert result == 50.0


class TestAverageDistance:
    """Tests for calculate_average_distance function."""

    def test_normal_average(self):
        result = calculate_average_distance([0.1, 0.2, 0.3])
        assert abs(result - 0.2) < 0.0001

    def test_single_value(self):
        result = calculate_average_distance([0.5])
        assert result == 0.5

    def test_empty_list(self):
        result = calculate_average_distance([])
        assert result == 0.0

    def test_none_list(self):
        result = calculate_average_distance(None)
        assert result == 0.0

    def test_filters_invalid(self):
        # Should filter out None and NaN
        result = calculate_average_distance([0.1, None, 0.3, float('nan')])
        assert abs(result - 0.2) < 0.0001


class TestCosineSimilarity:
    """Tests for calculate_cosine_similarity function."""

    def test_identical_vectors(self):
        vec = [0.5, 0.5, 0.5, 0.5]
        # Normalized: length = 1.0
        result = calculate_cosine_similarity(vec, vec)
        assert abs(result - 1.0) < 0.0001

    def test_orthogonal_vectors(self):
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        result = calculate_cosine_similarity(vec1, vec2)
        assert result == 0.0

    def test_empty_vectors(self):
        result = calculate_cosine_similarity([], [])
        assert result == 0.0

    def test_different_lengths(self):
        result = calculate_cosine_similarity([1, 2], [1, 2, 3])
        assert result == 0.0


class TestCosineDistance:
    """Tests for calculate_cosine_distance function."""

    def test_identical_vectors(self):
        vec = [0.5, 0.5, 0.5, 0.5]
        result = calculate_cosine_distance(vec, vec)
        assert abs(result) < 0.0001

    def test_orthogonal_vectors(self):
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        result = calculate_cosine_distance(vec1, vec2)
        assert result == 1.0


class TestCountBlockChars:
    """Tests for count_block_chars function."""

    def test_full_block(self):
        block = {
            'name': 'Test',  # 4 chars
            'critical_question': 'What?',  # 5 chars
            'trusted_answer': 'Answer.'  # 7 chars
        }
        result = count_block_chars(block)
        assert result == 16

    def test_empty_block(self):
        result = count_block_chars({})
        assert result == 0

    def test_partial_block(self):
        block = {'name': 'Test'}
        result = count_block_chars(block)
        assert result == 4


class TestCountWordsAndCharacters:
    """Tests for count_words_and_characters function."""

    def test_normal_text(self):
        result = count_words_and_characters("Hello world test")
        assert result['word_count'] == 3
        assert result['char_count'] == 16

    def test_empty_text(self):
        result = count_words_and_characters("")
        assert result['word_count'] == 0
        assert result['char_count'] == 0

    def test_with_newlines(self):
        result = count_words_and_characters("Hello\nworld\ttest")
        assert result['word_count'] == 3


class TestAnalyzeWordFrequencies:
    """Tests for analyze_word_frequencies function."""

    def test_basic_frequency(self):
        text = "apple banana apple cherry apple banana"
        result = analyze_word_frequencies(text)
        # Should be sorted by frequency
        assert result[0][0] == 'apple'
        assert result[0][1] == 3
        assert result[1][0] == 'banana'
        assert result[1][1] == 2

    def test_filters_stop_words(self):
        text = "the apple and the banana"
        result = analyze_word_frequencies(text)
        words = [w for w, _ in result]
        assert 'the' not in words
        assert 'and' not in words
        assert 'apple' in words

    def test_empty_text(self):
        result = analyze_word_frequencies("")
        assert result == []

    def test_top_n_limit(self):
        text = "a b c d e f g h i j k l m n o p q r s t u v w x y z"
        result = analyze_word_frequencies(text, top_n=5)
        assert len(result) <= 5


class TestValidateBenchmarkDistances:
    """Tests for validate_benchmark_distances function."""

    def test_valid_distances(self):
        result = validate_benchmark_distances(0.4, 0.3, 0.2)
        assert result is True

    def test_zero_distance(self):
        result = validate_benchmark_distances(0, 0.3, 0.2)
        assert result is False

    def test_negative_distance(self):
        result = validate_benchmark_distances(0.4, -0.3, 0.2)
        assert result is False

    def test_nan_distance(self):
        result = validate_benchmark_distances(float('nan'), 0.3, 0.2)
        assert result is False

    def test_non_numeric(self):
        result = validate_benchmark_distances("0.4", 0.3, 0.2)
        assert result is False


class TestTokenStats:
    """Tests for calculate_token_stats function."""

    def test_basic_calculation(self):
        distilled_blocks = [
            {'name': 'Test', 'critical_question': 'What?', 'trusted_answer': 'Answer'}
        ]
        undistilled_blocks = distilled_blocks
        chunks = [{'text': 'This is a test chunk with some content.'}]

        result = calculate_token_stats(
            distilled_blocks,
            undistilled_blocks,
            chunks,
            number_of_user_queries=1000
        )

        assert 'tokens_per_distilled' in result
        assert 'tokens_per_chunk' in result
        assert 'token_improvement' in result
        assert 'cost_savings_per_year' in result
        assert result['number_of_user_queries'] == 1000

    def test_empty_inputs(self):
        result = calculate_token_stats([], [], [])
        assert result['tokens_per_distilled'] == 0
        assert result['tokens_per_chunk'] == 0


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
