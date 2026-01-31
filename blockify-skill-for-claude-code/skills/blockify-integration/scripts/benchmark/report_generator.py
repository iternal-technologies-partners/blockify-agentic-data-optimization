"""
Benchmark report generator.

Orchestrates the benchmark process and generates HTML reports using Jinja2.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

import chromadb
from chromadb.config import Settings
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import BenchmarkConfig, load_config
from .metrics import (
    calculate_vector_improvement,
    calculate_word_improvement,
    calculate_char_improvement,
    calculate_aggregate_performance,
    calculate_projected_performance,
    calculate_average_distance,
    calculate_token_stats,
    count_words_and_characters,
    analyze_word_frequencies,
    ENTERPRISE_DUP_FACTOR,
)
from .embeddings import (
    generate_embeddings,
    generate_block_embeddings,
    generate_chunk_embeddings,
    calculate_query_distances,
    extract_queries_from_blocks,
    extract_unique_chunks,
    chunk_source_files,
)
from .charts import (
    generate_accuracy_chart,
    generate_performance_chart,
    generate_word_frequency_chart,
    generate_token_comparison_chart,
)


# Template directory
TEMPLATE_DIR = Path(__file__).parent / 'templates'


class BenchmarkRunner:
    """Main benchmark execution class."""

    def __init__(self, config_path: Optional[str] = None, overrides: Optional[Dict] = None, source_dir: Optional[str] = None):
        """Initialize benchmark runner.

        Args:
            config_path: Path to YAML config file
            overrides: Optional dict of config overrides
            source_dir: Path to source documents directory for raw chunk calculation
        """
        self.config = load_config(config_path, overrides)
        self.results: Dict[str, Any] = {}
        self.chroma_client = None
        self.raw_collection = None
        self.distilled_collection = None
        self.source_dir = source_dir

    def _connect_chromadb(self):
        """Connect to ChromaDB."""
        print(f"Connecting to ChromaDB at {self.config.chroma_dir}...")
        self.chroma_client = chromadb.PersistentClient(
            path=self.config.chroma_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get collections
        try:
            self.raw_collection = self.chroma_client.get_collection('raw_ideablocks')
            print(f"  Found raw_ideablocks: {self.raw_collection.count()} blocks")
        except Exception:
            print("  WARNING: raw_ideablocks collection not found")
            self.raw_collection = None

        try:
            self.distilled_collection = self.chroma_client.get_collection('distilled_ideablocks')
            print(f"  Found distilled_ideablocks: {self.distilled_collection.count()} blocks")
        except Exception:
            print("  WARNING: distilled_ideablocks collection not found (distillation may not have been run)")
            self.distilled_collection = None

    def _load_blocks(self, collection) -> List[Dict[str, Any]]:
        """Load all blocks from a collection."""
        if not collection:
            return []

        # Get all items
        results = collection.get(include=['metadatas', 'documents', 'embeddings'])

        blocks = []
        has_embeddings = results['embeddings'] is not None and len(results['embeddings']) > 0
        for i, block_id in enumerate(results['ids']):
            metadata = results['metadatas'][i] if results['metadatas'] else {}
            blocks.append({
                'id': block_id,
                'document': results['documents'][i] if results['documents'] else '',
                'embedding': list(results['embeddings'][i]) if has_embeddings else [],
                'name': metadata.get('name', ''),
                'critical_question': metadata.get('critical_question', ''),
                'trusted_answer': metadata.get('trusted_answer', ''),
                'source_document': metadata.get('source_document', ''),
                'source_chunk_text': metadata.get('source_chunk_text', ''),
                'source_chunk_index': metadata.get('source_chunk_index', 0),
                'source_chunk_hash': metadata.get('source_chunk_hash', ''),
                'tags': metadata.get('tags', ''),
                'keywords': metadata.get('keywords', ''),
                'entities': metadata.get('entities', '[]'),
            })

        return blocks

    def run(self) -> str:
        """Run the full benchmark and generate report.

        Returns:
            Path to the generated HTML report
        """
        print("=" * 60)
        print("BLOCKIFY BENCHMARK")
        print("=" * 60)
        print(f"Company: {self.config.company_name}")
        print(f"User Queries: {self.config.number_of_user_queries:,}")
        print()

        # Step 1: Connect to ChromaDB
        print("[1/7] Connecting to ChromaDB...")
        self._connect_chromadb()

        if not self.raw_collection:
            raise ValueError("No raw_ideablocks collection found. Run ingestion first.")

        # Step 2: Load data
        print("\n[2/7] Loading data...")
        undistilled_blocks = self._load_blocks(self.raw_collection)
        distilled_blocks = self._load_blocks(self.distilled_collection) if self.distilled_collection else []

        # Get chunks - prefer raw chunks from source files if source_dir provided
        if self.source_dir:
            print(f"  Loading raw chunks from source files: {self.source_dir}")
            chunks = chunk_source_files(self.source_dir)
            has_chunks = len(chunks) > 0
            if has_chunks:
                print(f"  Loaded {len(chunks)} raw chunks from source files (no deduplication)")
        else:
            # Fall back to extracting unique chunks from block metadata
            chunks = extract_unique_chunks(undistilled_blocks)
            has_chunks = len(chunks) > 0
            if has_chunks:
                print(f"  Extracted {len(chunks)} unique chunks from block metadata")

        if not has_chunks:
            print("  WARNING: No source chunks found.")
            print("  Chunk comparison will be skipped. Provide --source-dir or re-ingest documents.")

        print(f"  Undistilled blocks: {len(undistilled_blocks)}")
        print(f"  Distilled blocks: {len(distilled_blocks)}")
        print(f"  Source chunks: {len(chunks)}")

        # Flag if distillation wasn't run
        distillation_run = len(distilled_blocks) > 0
        if not distillation_run:
            print("  NOTE: Distillation not run - using raw blocks for distilled comparison")
            distilled_blocks = undistilled_blocks

        # Step 3: Calculate text statistics
        print("\n[3/7] Calculating text statistics...")
        self._calculate_text_stats(undistilled_blocks, distilled_blocks, chunks)

        # Step 4: Extract queries
        print("\n[4/7] Extracting benchmark queries...")
        queries = extract_queries_from_blocks(undistilled_blocks)
        if not queries:
            raise ValueError("No critical questions found in blocks to use as queries")
        print(f"  Extracted {len(queries)} queries from critical questions")
        self.results['queries'] = queries

        # Step 5: Generate embeddings and calculate distances
        print("\n[5/7] Generating embeddings and calculating distances...")
        self._calculate_distances(queries, undistilled_blocks, distilled_blocks, chunks)

        # Step 6: Calculate benchmark metrics
        print("\n[6/7] Calculating benchmark metrics...")
        self._calculate_metrics(undistilled_blocks, distilled_blocks, chunks, distillation_run)

        # Step 7: Generate report
        print("\n[7/7] Generating report...")
        report_path = self._generate_report()

        print("\n" + "=" * 60)
        print("BENCHMARK COMPLETE")
        print("=" * 60)
        self._print_summary()
        print(f"\nReport saved to: {report_path}")

        return report_path

    def _calculate_text_stats(self, undistilled_blocks, distilled_blocks, chunks):
        """Calculate text statistics."""
        # Get all trusted answers
        undistilled_text = ' '.join(b.get('trusted_answer', '') for b in undistilled_blocks)
        distilled_text = ' '.join(b.get('trusted_answer', '') for b in distilled_blocks)
        chunk_text = ' '.join(c.get('text', '') for c in chunks)

        # Count words and characters
        chunk_stats = count_words_and_characters(chunk_text)
        undistilled_stats = count_words_and_characters(undistilled_text)
        distilled_stats = count_words_and_characters(distilled_text)

        self.results['text_statistics'] = {
            'document': chunk_stats,  # Use chunks as document proxy
            'undistilled': undistilled_stats,
            'distilled': distilled_stats,
        }

        # Word frequencies
        chunk_freq = analyze_word_frequencies(chunk_text)
        undistilled_freq = analyze_word_frequencies(undistilled_text)
        distilled_freq = analyze_word_frequencies(distilled_text)

        self.results['word_frequencies'] = {
            'document': chunk_freq,
            'undistilled': undistilled_freq,
            'distilled': distilled_freq,
        }

        print(f"  Document (chunks): {chunk_stats['word_count']:,} words, {chunk_stats['char_count']:,} chars")
        print(f"  Undistilled: {undistilled_stats['word_count']:,} words, {undistilled_stats['char_count']:,} chars")
        print(f"  Distilled: {distilled_stats['word_count']:,} words, {distilled_stats['char_count']:,} chars")

    def _calculate_distances(self, queries, undistilled_blocks, distilled_blocks, chunks):
        """Calculate embedding distances."""
        # Generate query embeddings
        print("  Generating query embeddings...")
        query_embeddings = generate_embeddings(
            queries,
            model=self.config.embedding.model,
            batch_size=self.config.embedding.batch_size,
            show_progress=False
        )

        # Use existing embeddings from blocks (already in ChromaDB)
        undistilled_embeddings = [b.get('embedding', []) for b in undistilled_blocks]
        distilled_embeddings = [b.get('embedding', []) for b in distilled_blocks]

        # Generate chunk embeddings if we have chunks
        if chunks:
            print("  Generating chunk embeddings...")
            chunk_embeddings = generate_chunk_embeddings(
                chunks,
                model=self.config.embedding.model,
                batch_size=self.config.embedding.batch_size,
                show_progress=False
            )
        else:
            chunk_embeddings = []

        # Calculate distances
        print("  Calculating distances...")

        if chunk_embeddings:
            chunk_results = calculate_query_distances(query_embeddings, chunk_embeddings, chunks)
            self.results['chunk_distances'] = chunk_results['distances']
            self.results['chunk_matches'] = chunk_results['closest_matches']
        else:
            self.results['chunk_distances'] = []
            self.results['chunk_matches'] = []

        undistilled_results = calculate_query_distances(
            query_embeddings, undistilled_embeddings, undistilled_blocks
        )
        self.results['undistilled_distances'] = undistilled_results['distances']
        self.results['undistilled_matches'] = undistilled_results['closest_matches']

        distilled_results = calculate_query_distances(
            query_embeddings, distilled_embeddings, distilled_blocks
        )
        self.results['distilled_distances'] = distilled_results['distances']
        self.results['distilled_matches'] = distilled_results['closest_matches']

        # Calculate averages
        avg_chunk = calculate_average_distance(self.results['chunk_distances']) if self.results['chunk_distances'] else 0.5
        avg_undistilled = calculate_average_distance(self.results['undistilled_distances'])
        avg_distilled = calculate_average_distance(self.results['distilled_distances'])

        self.results['avg_chunk_distance'] = avg_chunk
        self.results['avg_undistilled_distance'] = avg_undistilled
        self.results['avg_distilled_distance'] = avg_distilled

        print(f"  Avg chunk distance: {avg_chunk:.4f}")
        print(f"  Avg undistilled distance: {avg_undistilled:.4f}")
        print(f"  Avg distilled distance: {avg_distilled:.4f}")

    def _calculate_metrics(self, undistilled_blocks, distilled_blocks, chunks, distillation_run):
        """Calculate benchmark metrics."""
        text_stats = self.results['text_statistics']

        # Vector improvement
        vector_improvement = calculate_vector_improvement(
            self.results['avg_chunk_distance'],
            self.results['avg_distilled_distance']
        )

        # Word improvement (document vs distilled)
        word_improvement = calculate_word_improvement(
            text_stats['document']['word_count'],
            text_stats['distilled']['word_count']
        )

        # Char improvement
        char_improvement = calculate_char_improvement(
            text_stats['document']['char_count'],
            text_stats['distilled']['char_count']
        )

        # Aggregate performance
        aggregate_performance = calculate_aggregate_performance(vector_improvement, word_improvement)

        # Enterprise projection
        enterprise_performance = calculate_projected_performance(
            vector_improvement,
            word_improvement,
            self.config.enterprise_dup_factor
        )

        # Token stats
        token_stats = calculate_token_stats(
            distilled_blocks,
            undistilled_blocks,
            chunks,
            self.config.number_of_user_queries,
            self.config.token_cost_per_million
        )

        self.results['metrics'] = {
            'vector_improvement': vector_improvement,
            'word_improvement': word_improvement,
            'char_improvement': char_improvement,
            'aggregate_performance': aggregate_performance,
            'enterprise_performance': enterprise_performance,
            'distillation_run': distillation_run,
            **token_stats,
        }

        self.results['counts'] = {
            'undistilled_blocks': len(undistilled_blocks),
            'distilled_blocks': len(distilled_blocks),
            'chunks': len(chunks),
            'queries': len(self.results.get('queries', [])),
        }

        print(f"  Vector improvement: {vector_improvement:.2f}X")
        print(f"  Word improvement: {word_improvement:.2f}X")
        print(f"  Aggregate performance: {aggregate_performance:.2f}X")
        print(f"  Enterprise performance: {enterprise_performance:.2f}X")
        print(f"  Token improvement: {token_stats['token_improvement']:.2f}X")
        print(f"  Cost savings/year: ${token_stats['cost_savings_per_year']:.2f}")

    def _generate_report(self) -> str:
        """Generate HTML report using Jinja2 templates."""
        # Ensure output directory exists
        output_dir = Path(self.config.output.report_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.config.output.filename_format.format(timestamp=timestamp)
        output_path = output_dir / filename

        # Generate charts
        print("  Generating charts...")
        charts = self._generate_charts()

        # Prepare metrics with additional distance data
        metrics_with_distances = {
            **self.results.get('metrics', {}),
            'avg_chunk_distance': self.results.get('avg_chunk_distance', 0.45),
            'avg_undistilled_distance': self.results.get('avg_undistilled_distance', 0.15),
            'avg_distilled_distance': self.results.get('avg_distilled_distance', 0.09),
        }

        # Prepare template data
        template_data = {
            'company_name': self.config.company_name,
            'generated_date': datetime.now().strftime('%B %d, %Y'),
            'generated_timestamp': datetime.now().isoformat(),
            'current_year': datetime.now().year,
            'metrics': metrics_with_distances,
            'counts': self.results.get('counts', {}),
            'text_statistics': self.results.get('text_statistics', {}),
            'word_frequencies': self.results.get('word_frequencies', {}),
            'charts': charts,
            'queries': self.results.get('queries', [])[:5],  # Sample queries
            'chunk_matches': self.results.get('chunk_matches', [])[:5],
            'undistilled_matches': self.results.get('undistilled_matches', [])[:5],
            'distilled_matches': self.results.get('distilled_matches', [])[:5],
            'sections': self.config.report_sections,
            'number_of_documents': self.results.get('counts', {}).get('chunks', 0),
            'number_of_pages': 'N/A',  # Can be overridden via config if needed
            'config': {
                'number_of_user_queries': self.config.number_of_user_queries,
                'enterprise_dup_factor': self.config.enterprise_dup_factor,
                'token_cost_per_million': self.config.token_cost_per_million,
            },
        }

        # Render template
        print("  Rendering HTML...")
        html_content = generate_html_report(template_data)

        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Optionally save JSON metrics
        if self.config.output.include_json_metrics:
            json_path = output_path.with_suffix('.json')
            json_data = {
                'timestamp': timestamp,
                'company_name': self.config.company_name,
                'config': {
                    'number_of_user_queries': self.config.number_of_user_queries,
                    'enterprise_dup_factor': self.config.enterprise_dup_factor,
                    'token_cost_per_million': self.config.token_cost_per_million,
                },
                'metrics': self.results.get('metrics', {}),
                'counts': self.results.get('counts', {}),
                'text_statistics': self.results.get('text_statistics', {}),
                'distances': {
                    'avg_chunk': self.results.get('avg_chunk_distance'),
                    'avg_undistilled': self.results.get('avg_undistilled_distance'),
                    'avg_distilled': self.results.get('avg_distilled_distance'),
                },
            }
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            print(f"  JSON metrics saved to: {json_path}")

        return str(output_path)

    def _generate_charts(self) -> Dict[str, str]:
        """Generate all charts as base64 data URIs."""
        charts = {}

        metrics = self.results.get('metrics', {})

        # Accuracy chart
        charts['accuracy'] = generate_accuracy_chart(
            self.results.get('avg_chunk_distance', 0.5),
            self.results.get('avg_undistilled_distance', 0.3),
            self.results.get('avg_distilled_distance', 0.2)
        )

        # Performance chart
        charts['performance'] = generate_performance_chart(
            metrics.get('vector_improvement', 1),
            metrics.get('word_improvement', 1),
            metrics.get('aggregate_performance', 1),
            metrics.get('enterprise_performance', 1)
        )

        # Word frequency chart
        word_freq = self.results.get('word_frequencies', {})
        charts['word_frequency'] = generate_word_frequency_chart(
            word_freq.get('document', []),
            word_freq.get('distilled', [])
        )

        # Token comparison chart
        charts['tokens'] = generate_token_comparison_chart(
            metrics.get('tokens_per_chunk', 0),
            metrics.get('tokens_per_undistilled', 0),
            metrics.get('tokens_per_distilled', 0)
        )

        return charts

    def _print_summary(self):
        """Print benchmark summary."""
        metrics = self.results.get('metrics', {})
        counts = self.results.get('counts', {})

        print(f"\nResults for {self.config.company_name}:")
        print(f"  Blocks analyzed: {counts.get('undistilled_blocks', 0):,} raw, {counts.get('distilled_blocks', 0):,} distilled")
        print(f"  Queries used: {counts.get('queries', 0):,}")
        print(f"\nPerformance Metrics:")
        print(f"  Vector Search Accuracy: {metrics.get('vector_improvement', 0):.2f}X improvement")
        print(f"  Information Distillation: {metrics.get('word_improvement', 0):.2f}X reduction")
        print(f"  Aggregate Performance: {metrics.get('aggregate_performance', 0):.2f}X")
        print(f"  Enterprise Performance: {metrics.get('enterprise_performance', 0):.2f}X")
        print(f"  Token Efficiency: {metrics.get('token_improvement', 0):.2f}X")
        print(f"  Projected Annual Savings: ${metrics.get('cost_savings_per_year', 0):,.2f}")

        if not metrics.get('distillation_run', True):
            print("\n  * Note: Distillation was not run. Run distill_chromadb.py for full comparison.")


def generate_html_report(data: Dict[str, Any]) -> str:
    """Generate HTML report from template data.

    Args:
        data: Template data dict

    Returns:
        HTML string
    """
    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Add custom filters
    env.filters['format_number'] = lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x
    env.filters['format_decimal'] = lambda x, d=2: f"{x:,.{d}f}" if isinstance(x, (int, float)) else x
    env.filters['format_percent'] = lambda x: f"{x:.1%}" if isinstance(x, (int, float)) else x
    env.filters['format_currency'] = lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x

    # Load and render template
    template = env.get_template('base.html')
    return template.render(**data)
