"""
Blockify Benchmark Module

This module provides headless benchmarking capabilities for comparing
IdeaBlocks against traditional text chunking methods.

Components:
    - config: Configuration loading from YAML
    - metrics: Mathematical calculations (ported from reportMath.ts)
    - embeddings: OpenAI embedding generation
    - charts: Matplotlib chart generation
    - report_generator: Jinja2-based HTML report assembly
"""

from .config import BenchmarkConfig, load_config
from .metrics import (
    CHAR_TO_TOKEN_RATIO,
    ENTERPRISE_DUP_FACTOR,
    DEFAULT_TOKEN_COST_PER_MILLION,
    calculate_vector_improvement,
    calculate_word_improvement,
    calculate_char_improvement,
    calculate_aggregate_performance,
    calculate_projected_performance,
    calculate_average_distance,
    calculate_cosine_similarity,
    calculate_token_stats,
    count_words_and_characters,
    analyze_word_frequencies,
)
from .embeddings import generate_embeddings, calculate_query_distances
from .charts import (
    generate_accuracy_chart,
    generate_word_frequency_chart,
    generate_performance_chart,
)
from .report_generator import BenchmarkRunner, generate_html_report

__version__ = '1.0.0'
__all__ = [
    'BenchmarkConfig',
    'load_config',
    'BenchmarkRunner',
    'generate_html_report',
    'generate_embeddings',
    'calculate_query_distances',
    'generate_accuracy_chart',
    'generate_word_frequency_chart',
    'generate_performance_chart',
    'calculate_vector_improvement',
    'calculate_word_improvement',
    'calculate_char_improvement',
    'calculate_aggregate_performance',
    'calculate_projected_performance',
    'calculate_average_distance',
    'calculate_cosine_similarity',
    'calculate_token_stats',
    'count_words_and_characters',
    'analyze_word_frequencies',
    'CHAR_TO_TOKEN_RATIO',
    'ENTERPRISE_DUP_FACTOR',
    'DEFAULT_TOKEN_COST_PER_MILLION',
]
