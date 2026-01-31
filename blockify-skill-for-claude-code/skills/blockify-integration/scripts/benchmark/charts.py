"""
Chart generation for benchmark reports using matplotlib.

All charts are returned as base64-encoded PNG data URIs for embedding in HTML.
"""

import io
import base64
from typing import List, Dict, Any, Tuple, Optional

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# Color scheme matching frontend
COLORS = {
    'primary': '#0066B3',
    'secondary': '#333333',
    'accent': '#009FDA',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'light_gray': '#f5f7fa',
    'medium_gray': '#e0e5ec',
}


def _fig_to_base64(fig: plt.Figure, dpi: int = 150) -> str:
    """Convert matplotlib figure to base64 PNG data URI.

    Args:
        fig: Matplotlib figure
        dpi: Resolution

    Returns:
        Base64 data URI string
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"


def generate_accuracy_chart(
    chunk_distance: float,
    undistilled_distance: float,
    distilled_distance: float
) -> str:
    """Generate accuracy comparison bar chart.

    Shows vector search accuracy (1 - distance) for each method.

    Args:
        chunk_distance: Average distance for traditional chunking
        undistilled_distance: Average distance for undistilled blocks
        distilled_distance: Average distance for distilled blocks

    Returns:
        Base64 PNG data URI
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Convert distance to accuracy (lower distance = higher accuracy)
    # Clamp between 0 and 1
    chunk_acc = max(0, min(1, 1 - chunk_distance))
    undistilled_acc = max(0, min(1, 1 - undistilled_distance))
    distilled_acc = max(0, min(1, 1 - distilled_distance))

    categories = ['Traditional\nChunking', 'Undistilled\nIdeaBlocks', 'Distilled\nIdeaBlocks']
    accuracies = [chunk_acc, undistilled_acc, distilled_acc]
    colors = [COLORS['danger'], COLORS['warning'], COLORS['success']]

    bars = ax.bar(categories, accuracies, color=colors, width=0.6, edgecolor='white', linewidth=1.5)

    # Styling
    ax.set_ylabel('Vector Search Accuracy', fontsize=12, fontweight='500')
    ax.set_title('Vector Search Accuracy Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 1.1)
    ax.set_xlim(-0.5, 2.5)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.03,
                f'{acc:.1%}', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color=COLORS['secondary'])

    # Add improvement annotation
    if chunk_acc > 0 and distilled_acc > 0:
        improvement = distilled_acc / chunk_acc if chunk_acc != 0 else 0
        if improvement > 1:
            ax.annotate(f'{improvement:.2f}X\nImprovement',
                       xy=(2, distilled_acc),
                       xytext=(2.3, distilled_acc - 0.15),
                       fontsize=11, fontweight='bold', color=COLORS['success'],
                       ha='left')

    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_performance_chart(
    vector_improvement: float,
    word_improvement: float,
    aggregate_performance: float,
    enterprise_performance: float
) -> str:
    """Generate performance metrics bar chart.

    Args:
        vector_improvement: Vector accuracy improvement factor
        word_improvement: Word count improvement factor
        aggregate_performance: Combined improvement
        enterprise_performance: Projected enterprise performance

    Returns:
        Base64 PNG data URI
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    categories = [
        'Vector Search\nAccuracy',
        'Information\nDistillation',
        'Aggregate\nPerformance',
        'Enterprise\nPerformance'
    ]
    values = [vector_improvement, word_improvement, aggregate_performance, enterprise_performance]
    colors = [COLORS['accent'], COLORS['primary'], COLORS['success'], COLORS['success']]

    bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor='white', linewidth=1.5)

    # Styling
    ax.set_ylabel('Improvement Factor (X)', fontsize=12, fontweight='500')
    ax.set_title('Blockify Performance Improvements', fontsize=14, fontweight='bold', pad=20)

    # Dynamic y-axis limit
    max_val = max(values) if values else 1
    ax.set_ylim(0, max_val * 1.2)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + (max_val * 0.02),
                f'{val:.1f}X', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color=COLORS['secondary'])

    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_word_frequency_chart(
    document_frequencies: List[Tuple[str, int]],
    distilled_frequencies: List[Tuple[str, int]],
    top_n: int = 10
) -> str:
    """Generate word frequency comparison chart.

    Shows top words and their reduction from document to distilled.

    Args:
        document_frequencies: List of (word, count) for original document
        distilled_frequencies: List of (word, count) for distilled content
        top_n: Number of top words to show

    Returns:
        Base64 PNG data URI
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    # Get top N words from document
    doc_words = document_frequencies[:top_n]
    if not doc_words:
        # Return empty chart
        ax.text(0.5, 0.5, 'No word frequency data available',
                ha='center', va='center', fontsize=14)
        return _fig_to_base64(fig)

    # Create dict for easy lookup
    distilled_dict = dict(distilled_frequencies)

    words = [w for w, _ in doc_words]
    doc_counts = [c for _, c in doc_words]
    distilled_counts = [distilled_dict.get(w, 0) for w in words]

    x = np.arange(len(words))
    width = 0.35

    bars1 = ax.bar(x - width/2, doc_counts, width, label='Original Document',
                   color=COLORS['danger'], alpha=0.8)
    bars2 = ax.bar(x + width/2, distilled_counts, width, label='Distilled IdeaBlocks',
                   color=COLORS['success'], alpha=0.8)

    # Styling
    ax.set_xlabel('Words', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Word Frequency: Original vs Distilled', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(words, rotation=45, ha='right', fontsize=10)
    ax.legend(loc='upper right', fontsize=10)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_token_comparison_chart(
    tokens_per_chunk: int,
    tokens_per_undistilled: int,
    tokens_per_distilled: int
) -> str:
    """Generate token usage comparison chart.

    Args:
        tokens_per_chunk: Tokens per traditional chunk
        tokens_per_undistilled: Tokens per undistilled block
        tokens_per_distilled: Tokens per distilled block

    Returns:
        Base64 PNG data URI
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ['Traditional\nChunking', 'Undistilled\nIdeaBlocks', 'Distilled\nIdeaBlocks']
    values = [tokens_per_chunk, tokens_per_undistilled, tokens_per_distilled]
    colors = [COLORS['danger'], COLORS['warning'], COLORS['success']]

    bars = ax.bar(categories, values, color=colors, width=0.6)

    # Styling
    ax.set_ylabel('Tokens per Item', fontsize=12)
    ax.set_title('Token Usage Comparison', fontsize=14, fontweight='bold', pad=20)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + (max(values) * 0.02),
                f'{val:,}', ha='center', va='bottom',
                fontsize=11, fontweight='bold')

    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_distance_comparison_chart(
    chunk_distances: List[float],
    distilled_distances: List[float],
    max_points: int = 20
) -> str:
    """Generate query-level distance comparison scatter plot.

    Args:
        chunk_distances: List of distances for each query to chunks
        distilled_distances: List of distances for each query to distilled blocks
        max_points: Maximum number of points to show

    Returns:
        Base64 PNG data URI
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Limit to max_points
    n = min(len(chunk_distances), len(distilled_distances), max_points)
    chunk_d = chunk_distances[:n]
    distilled_d = distilled_distances[:n]

    x = np.arange(n)

    ax.scatter(x, chunk_d, color=COLORS['danger'], label='Traditional Chunking',
               s=80, alpha=0.7, marker='o')
    ax.scatter(x, distilled_d, color=COLORS['success'], label='Distilled IdeaBlocks',
               s=80, alpha=0.7, marker='s')

    # Connect points with lines
    for i in range(n):
        ax.plot([i, i], [chunk_d[i], distilled_d[i]],
                color=COLORS['medium_gray'], linestyle='--', linewidth=1, alpha=0.5)

    # Styling
    ax.set_xlabel('Query Index', fontsize=12)
    ax.set_ylabel('Cosine Distance (lower is better)', fontsize=12)
    ax.set_title('Per-Query Distance Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=10)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return _fig_to_base64(fig)
