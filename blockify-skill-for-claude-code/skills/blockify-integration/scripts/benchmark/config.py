"""
Configuration management for Blockify Benchmark.

Loads configuration from YAML files with sensible defaults.
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, Optional
from pathlib import Path


# Default paths
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / 'config' / 'benchmark_config.yaml'
DEFAULT_DATA_DIR = os.environ.get('IDEABLOCK_DATA_DIR', './data/ideablocks')
DEFAULT_REPORT_DIR = './data/reports'


@dataclass
class EmbeddingConfig:
    """Embedding configuration."""
    model: str = 'text-embedding-3-small'
    batch_size: int = 100
    dimensions: int = 1536


@dataclass
class ChunkingConfig:
    """Text chunking configuration."""
    max_chars: int = 2000
    overlap: int = 200


@dataclass
class OutputConfig:
    """Output configuration."""
    report_dir: str = DEFAULT_REPORT_DIR
    filename_format: str = 'benchmark_report_{timestamp}.html'
    include_json_metrics: bool = True


@dataclass
class ReportSections:
    """Report sections toggle."""
    header: bool = True
    report_title: bool = True
    overview: bool = True
    metrics: bool = True
    executive_summary: bool = True
    data_samples: bool = True
    introduction: bool = True
    problem: bool = True
    solution: bool = True
    benchmark_results: bool = True
    accuracy_chart: bool = True
    word_frequency: bool = True
    calculator: bool = True
    terminology: bool = True
    benefits: bool = True
    footer: bool = True


@dataclass
class BenchmarkConfig:
    """Main benchmark configuration."""
    company_name: str = 'Your Company'
    number_of_user_queries: int = 1000
    enterprise_dup_factor: int = 15
    token_cost_per_million: float = 0.72
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    report_sections: ReportSections = field(default_factory=ReportSections)

    # Runtime paths (set after loading)
    data_dir: str = DEFAULT_DATA_DIR
    chroma_dir: str = ''

    def __post_init__(self):
        """Set derived paths."""
        if not self.chroma_dir:
            self.chroma_dir = os.path.join(self.data_dir, 'chroma_db')


def load_config(config_path: Optional[str] = None, overrides: Optional[Dict] = None) -> BenchmarkConfig:
    """Load benchmark configuration from YAML file.

    Args:
        config_path: Path to YAML config file. If None, uses default path.
        overrides: Optional dict of values to override after loading.

    Returns:
        BenchmarkConfig instance with loaded values.
    """
    config = BenchmarkConfig()

    # Try to load from file
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if path.exists():
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f) or {}

            # Apply top-level settings
            if 'company_name' in data:
                config.company_name = data['company_name']
            if 'number_of_user_queries' in data:
                config.number_of_user_queries = data['number_of_user_queries']
            if 'enterprise_dup_factor' in data:
                config.enterprise_dup_factor = data['enterprise_dup_factor']
            if 'token_cost_per_million' in data:
                config.token_cost_per_million = data['token_cost_per_million']

            # Apply embedding settings
            if 'embedding' in data:
                emb = data['embedding']
                config.embedding = EmbeddingConfig(
                    model=emb.get('model', config.embedding.model),
                    batch_size=emb.get('batch_size', config.embedding.batch_size),
                    dimensions=emb.get('dimensions', config.embedding.dimensions),
                )

            # Apply chunking settings
            if 'chunking' in data:
                chunk = data['chunking']
                config.chunking = ChunkingConfig(
                    max_chars=chunk.get('max_chars', config.chunking.max_chars),
                    overlap=chunk.get('overlap', config.chunking.overlap),
                )

            # Apply output settings
            if 'output' in data:
                out = data['output']
                config.output = OutputConfig(
                    report_dir=out.get('report_dir', config.output.report_dir),
                    filename_format=out.get('filename_format', config.output.filename_format),
                    include_json_metrics=out.get('include_json_metrics', config.output.include_json_metrics),
                )

            # Apply report sections settings
            if 'report_sections' in data:
                sections = data['report_sections']
                config.report_sections = ReportSections(
                    header=sections.get('header', True),
                    report_title=sections.get('report_title', True),
                    overview=sections.get('overview', True),
                    metrics=sections.get('metrics', True),
                    executive_summary=sections.get('executive_summary', True),
                    data_samples=sections.get('data_samples', True),
                    introduction=sections.get('introduction', True),
                    problem=sections.get('problem', True),
                    solution=sections.get('solution', True),
                    benchmark_results=sections.get('benchmark_results', True),
                    accuracy_chart=sections.get('accuracy_chart', True),
                    word_frequency=sections.get('word_frequency', True),
                    calculator=sections.get('calculator', True),
                    terminology=sections.get('terminology', True),
                    benefits=sections.get('benefits', True),
                    footer=sections.get('footer', True),
                )

            print(f"Loaded config from {path}")
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
            print("Using default configuration")
    else:
        print(f"Config file not found at {path}, using defaults")

    # Apply overrides
    if overrides:
        if 'company_name' in overrides:
            config.company_name = overrides['company_name']
        if 'number_of_user_queries' in overrides:
            config.number_of_user_queries = overrides['number_of_user_queries']
        if 'token_cost_per_million' in overrides:
            config.token_cost_per_million = overrides['token_cost_per_million']
        if 'data_dir' in overrides:
            config.data_dir = overrides['data_dir']
            config.chroma_dir = os.path.join(config.data_dir, 'chroma_db')

    return config


def save_default_config(path: Optional[str] = None) -> str:
    """Save default configuration to a YAML file.

    Args:
        path: Path to save to. If None, uses default path.

    Returns:
        Path where config was saved.
    """
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    default_config = """# Blockify Benchmark Configuration
# ================================

# Company/Organization name for report header
company_name: "Your Company"

# Number of annual user queries for token cost projections
number_of_user_queries: 1000

# Enterprise data duplication factor (industry standard: 15x)
enterprise_dup_factor: 15

# Token cost per million (USD) - adjust for your LLM provider
# Default: $0.72 (LLAMA 3.3 70B)
# GPT-4: $30.00, GPT-3.5: $0.50, Claude: $15.00
token_cost_per_million: 0.72

# Embedding configuration
embedding:
  model: "text-embedding-3-small"
  batch_size: 100
  dimensions: 1536

# Chunking configuration (for traditional chunking comparison)
chunking:
  max_chars: 2000
  overlap: 200

# Output configuration
output:
  report_dir: "./data/reports"
  filename_format: "benchmark_report_{timestamp}.html"
  include_json_metrics: true

# Report sections to include (all enabled by default)
report_sections:
  header: true
  report_title: true
  overview: true
  metrics: true
  executive_summary: true
  data_samples: true
  introduction: true
  problem: true
  solution: true
  benchmark_results: true
  accuracy_chart: true
  word_frequency: true
  calculator: true
  terminology: true
  benefits: true
  footer: true
"""

    with open(config_path, 'w') as f:
        f.write(default_config)

    return str(config_path)
