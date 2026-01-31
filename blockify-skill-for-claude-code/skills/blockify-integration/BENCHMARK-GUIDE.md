# Blockify Benchmark Guide

## Overview

The Blockify Benchmark tool compares the performance of Blockify IdeaBlocks against traditional text chunking methods for Retrieval-Augmented Generation (RAG) systems. It generates a comprehensive HTML report with detailed metrics and visualizations.

## What It Measures

| Metric | Description |
|--------|-------------|
| **Vector Search Accuracy** | How well the retrieved content matches the query (cosine similarity) |
| **Word Improvement** | Reduction in content size (original vs distilled) |
| **Aggregate Performance** | Combined improvement (Vector × Word) |
| **Enterprise Performance** | Projected improvement at enterprise scale (× 15 duplication factor) |
| **Token Efficiency** | Reduction in tokens consumed per query |
| **Cost Savings** | Projected annual savings from reduced token usage |

## Prerequisites

1. **API Keys**
   ```bash
   export BLOCKIFY_API_KEY="blk_your_key_here"
   export OPENAI_API_KEY="sk-your_key_here"
   ```

2. **Dependencies**
   ```bash
   pip install jinja2 matplotlib pyyaml chromadb openai
   ```

3. **Ingested Data**
   - Run ingestion first to populate ChromaDB with IdeaBlocks
   - Optionally run distillation for deduplication comparison

## Quick Start

### Option 1: Run After Full Pipeline (Automatic)

The benchmark runs automatically as the final step of the full pipeline:

```bash
python scripts/run_full_pipeline.py /path/to/documents/
```

### Option 2: Run Standalone

If you've already ingested documents:

```bash
python scripts/run_benchmark.py
```

### Option 3: With Custom Settings

```bash
python scripts/run_benchmark.py --company "Acme Corp" --queries 10000
```

## Configuration

### Using the Config File

Create or edit `config/benchmark_config.yaml`:

```yaml
# Company name for the report
company_name: "Acme Corporation"

# Annual user queries for cost projections
number_of_user_queries: 5000

# Token cost per million (adjust for your LLM)
token_cost_per_million: 0.72

# Output settings
output:
  report_dir: "./data/reports"
  include_json_metrics: true
```

### Initialize Default Config

```bash
python scripts/run_benchmark.py --init-config
```

This creates `config/benchmark_config.yaml` with default values.

### CLI Overrides

Override config values from command line:

```bash
python scripts/run_benchmark.py \
    --company "My Company" \
    --queries 10000 \
    --cost 0.50 \
    --output ./my_reports/
```

## Output Files

After running, find your reports in `./data/reports/`:

```
data/reports/
├── benchmark_report_20260129_143052.html   # Main HTML report
└── benchmark_report_20260129_143052.json   # JSON metrics (optional)
```

### Viewing the Report

```bash
# macOS
open data/reports/benchmark_report_*.html

# Linux
xdg-open data/reports/benchmark_report_*.html

# Windows
start data/reports/benchmark_report_*.html
```

## Understanding the Report

### Key Performance Indicators

The report displays four main KPIs:

1. **Vector Search Accuracy Improvement**
   - How much better IdeaBlocks are at matching queries
   - Higher is better (e.g., 2.0X means 2× more accurate)

2. **Enterprise Performance**
   - Combined improvement × enterprise duplication factor
   - Represents real-world enterprise impact

3. **Token Efficiency**
   - Reduction in tokens consumed per query
   - Directly affects API costs

4. **Cost Savings**
   - Projected annual savings from token reduction
   - Based on configured queries/year and token price

### Benchmark Results Tables

The report includes detailed tables showing:

- Block and chunk counts
- Average cosine distances
- Word/character statistics
- Token consumption projections

### Charts

- **Accuracy Chart**: Visual comparison of search accuracy
- **Performance Chart**: Bar chart of improvement factors
- **Word Frequency**: Top word reduction analysis

## Manual CLI Usage (Without Claude Code)

You can run the entire benchmark workflow manually from the command line:

### Step 1: Set Up Environment

```bash
# Navigate to skill directory
cd /path/to/blockify-skill-for-claude-code/skills/blockify-integration

# Create and load environment
cat > .env << 'EOF'
BLOCKIFY_API_KEY=blk_your_key_here
OPENAI_API_KEY=sk-your_key_here
EOF

export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Ingest Documents

```bash
# Single file
python scripts/ingest_to_chromadb.py document.md

# Directory
python scripts/ingest_to_chromadb.py /path/to/docs/ --batch
```

### Step 4: Run Distillation (Optional but Recommended)

```bash
python scripts/distill_chromadb.py
```

### Step 5: Run Benchmark

```bash
python scripts/run_benchmark.py --company "My Company"
```

### Step 6: View Report

```bash
open data/reports/benchmark_report_*.html
```

### All-in-One Command

```bash
# Full pipeline including benchmark
python scripts/run_full_pipeline.py /path/to/docs/
```

## Troubleshooting

### "OPENAI_API_KEY not set"

```bash
export OPENAI_API_KEY="sk-your_key_here"
```

### "ChromaDB directory not found"

Run ingestion first:
```bash
python scripts/ingest_to_chromadb.py /path/to/documents/ --batch
```

### "No critical questions found"

Ensure documents have been properly ingested with the Blockify API:
```bash
python scripts/search_chromadb.py "test query" --collection raw
```

### "Benchmark module not available"

Install required dependencies:
```bash
pip install jinja2 matplotlib pyyaml numpy
```

### "No source_chunk_text found"

This warning means your IdeaBlocks were ingested before the benchmark tracking update. Re-ingest your documents:

```bash
# Clear existing data
rm -rf data/ideablocks/chroma_db/

# Re-ingest
python scripts/ingest_to_chromadb.py /path/to/docs/ --batch
```

## Advanced Usage

### Custom Report Sections

Disable specific sections in `benchmark_config.yaml`:

```yaml
report_sections:
  introduction: false  # Skip introduction
  problem: false       # Skip problem statement
  terminology: false   # Skip terminology
```

### Different Token Pricing

For different LLM providers:

```yaml
# GPT-4
token_cost_per_million: 30.00

# Claude 3.5 Sonnet
token_cost_per_million: 15.00

# LLAMA 3.3 70B (default)
token_cost_per_million: 0.72
```

### JSON Metrics Only

For programmatic access, disable HTML and keep JSON:

```python
from benchmark import BenchmarkRunner

runner = BenchmarkRunner()
runner.config.output.include_json_metrics = True
report_path = runner.run()

# JSON is saved alongside HTML
json_path = report_path.replace('.html', '.json')
```

## API Reference

### BenchmarkRunner Class

```python
from benchmark import BenchmarkRunner

# Initialize with defaults
runner = BenchmarkRunner()

# Initialize with custom config
runner = BenchmarkRunner(config_path='./my_config.yaml')

# Initialize with overrides
runner = BenchmarkRunner(overrides={
    'company_name': 'Acme Corp',
    'number_of_user_queries': 10000
})

# Run benchmark
report_path = runner.run()
```

### Metrics Functions

```python
from benchmark.metrics import (
    calculate_vector_improvement,
    calculate_word_improvement,
    calculate_aggregate_performance,
    calculate_projected_performance,
)

# Calculate improvements
vector_imp = calculate_vector_improvement(chunk_distance=0.4, distilled_distance=0.2)
word_imp = calculate_word_improvement(doc_words=10000, distilled_words=400)
aggregate = calculate_aggregate_performance(vector_imp, word_imp)
enterprise = calculate_projected_performance(vector_imp, word_imp, enterprise_factor=15)
```

## Future Improvements

The following enhancements are planned for future releases:

- Per-document breakdown metrics
- Query-level distance comparisons
- Statistical confidence intervals
- Hybrid search (BM25 + vector) comparison
- Cross-encoder reranking benchmarks
- Multiple embedding model comparisons

## Support

For issues and feature requests, see the main skill documentation or contact your Blockify representative.
