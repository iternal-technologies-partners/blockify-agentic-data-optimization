#!/usr/bin/env python3
"""
Run Blockify Benchmark - Compare IdeaBlocks vs Traditional Chunking

This script runs a comprehensive benchmark comparing Blockify IdeaBlocks against
traditional text chunking methods, generating an HTML report with detailed metrics.

Usage:
    python run_benchmark.py
    python run_benchmark.py --config ./my_config.yaml
    python run_benchmark.py --company "Acme Corp" --queries 5000

Options:
    --config, -c PATH      Path to YAML config file (default: config/benchmark_config.yaml)
    --company NAME         Override company name from config
    --queries NUM          Override number of annual user queries
    --cost PRICE           Override token cost per million
    --output DIR           Override output directory
    --help, -h             Show this help message

Environment:
    OPENAI_API_KEY         Required for embedding generation
    IDEABLOCK_DATA_DIR     Data directory (default: ./data/ideablocks)

Prerequisites:
    1. Run ingestion first: python scripts/ingest_to_chromadb.py ...
    2. (Optional) Run distillation: python scripts/distill_chromadb.py

Output:
    - HTML report saved to ./data/reports/benchmark_report_YYYYMMDD_HHMMSS.html
    - JSON metrics saved alongside if include_json_metrics=true in config

Examples:
    # Basic usage with default config
    python scripts/run_benchmark.py

    # Custom company name and queries
    python scripts/run_benchmark.py --company "My Company" --queries 10000

    # Use custom config file
    python scripts/run_benchmark.py --config ./my_benchmark_config.yaml
"""

import os
import sys
import argparse
from pathlib import Path

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from benchmark import BenchmarkRunner, load_config
from benchmark.config import save_default_config, DEFAULT_CONFIG_PATH


def validate_environment():
    """Validate required environment variables."""
    errors = []

    if not os.environ.get('OPENAI_API_KEY'):
        errors.append("OPENAI_API_KEY environment variable not set")

    data_dir = os.environ.get('IDEABLOCK_DATA_DIR', './data/ideablocks')
    chroma_dir = os.path.join(data_dir, 'chroma_db')
    if not os.path.exists(chroma_dir):
        errors.append(f"ChromaDB directory not found at {chroma_dir}")
        errors.append("Run ingestion first: python scripts/ingest_to_chromadb.py <documents>")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description='Run Blockify Benchmark - Compare IdeaBlocks vs Traditional Chunking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_benchmark.py                           # Use default config
  python run_benchmark.py --company "Acme Corp"    # Override company name
  python run_benchmark.py --config ./config.yaml   # Use custom config

For more information, see BENCHMARK-GUIDE.md
        """
    )

    parser.add_argument(
        '--config', '-c',
        type=str,
        default=None,
        help='Path to YAML config file (default: config/benchmark_config.yaml)'
    )
    parser.add_argument(
        '--company',
        type=str,
        default=None,
        help='Override company name for the report'
    )
    parser.add_argument(
        '--queries',
        type=int,
        default=None,
        help='Override number of annual user queries for cost projections'
    )
    parser.add_argument(
        '--cost',
        type=float,
        default=None,
        help='Override token cost per million (default: $0.72)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Override output directory for reports'
    )
    parser.add_argument(
        '--init-config',
        action='store_true',
        help='Create default config file and exit'
    )

    args = parser.parse_args()

    # Handle --init-config
    if args.init_config:
        config_path = save_default_config()
        print(f"Created default config at: {config_path}")
        print("Edit this file to customize your benchmark settings.")
        sys.exit(0)

    # Validate environment
    errors = validate_environment()
    if errors:
        print("Environment validation failed:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the above issues and try again.")
        sys.exit(1)

    # Build overrides from CLI arguments
    overrides = {}
    if args.company:
        overrides['company_name'] = args.company
    if args.queries:
        overrides['number_of_user_queries'] = args.queries
    if args.cost:
        overrides['token_cost_per_million'] = args.cost

    # Run benchmark
    try:
        runner = BenchmarkRunner(config_path=args.config, overrides=overrides)

        # Apply output override if specified
        if args.output:
            runner.config.output.report_dir = args.output

        report_path = runner.run()

        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"Report saved to: {report_path}")
        print("\nTo view the report:")
        print(f"  open {report_path}")

    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
