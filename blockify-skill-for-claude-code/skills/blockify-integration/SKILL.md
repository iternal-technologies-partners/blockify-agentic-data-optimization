---
name: blockify-integration
description: >-
  Process documents with Blockify API to create optimized IdeaBlocks for RAG.
  Search external ChromaDB knowledge bases with 100k+ blocks.
  Use when processing documentation, creating knowledge bases, improving
  AI context retrieval, or when user mentions Blockify, IdeaBlocks, or
  knowledge distillation.
---

# Blockify Integration Skill

## Why This Exists

**Problem:** Traditional RAG systems chunk documents by character/token count, losing semantic coherence. A 500-token chunk may split a concept mid-sentence, contain unrelated paragraphs, or bury key facts in noise.

**Solution:** Blockify is a patented distillation platform that transforms raw text into **IdeaBlocks**—self-contained semantic knowledge units optimized for AI retrieval.

| Metric | Improvement |
|--------|-------------|
| Enterprise Performance | 78X |
| Vector Search Accuracy | 2.29X |
| Dataset Size Reduction | 40X (to ~2.5%) |
| Token Efficiency | 3.09X |

---

## End-to-End Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BLOCKIFY PIPELINE OVERVIEW                          │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  Source  │     │ Blockify │     │ ChromaDB │     │  Search  │
  │Documents │────▶│   API    │────▶│  Vector  │────▶│  Query   │
  │ .md .txt │     │ (ingest) │     │   Store  │     │ Results  │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘
       │                │                │                │
       │                ▼                ▼                │
       │         ┌──────────┐     ┌──────────┐           │
       │         │IdeaBlocks│     │  OpenAI  │           │
       │         │   XML    │     │Embeddings│           │
       │         └──────────┘     │  1536-d  │           │
       │                          └──────────┘           │
       │                               │                 │
       │                               ▼                 │
       │                    ┌─────────────────┐          │
       │                    │   DISTILLATION  │          │
       │                    │  (deduplicate)  │          │
       │                    │                 │          │
       │                    │ raw_ideablocks  │          │
       │                    │       ▼         │          │
       │                    │ distilled_      │          │
       │                    │   ideablocks    │          │
       │                    └─────────────────┘          │
       │                                                 │
       └─────────────────────────────────────────────────┘
```

---

## Complete Setup (Step-by-Step)

### Prerequisites

- Python 3.9+
- API Keys:
  - `BLOCKIFY_API_KEY` - Get from https://app.blockify.ai/settings/api
  - `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys

### Step 1: Create Environment File

```bash
cd /path/to/blockify-skill-for-claude-code

# Create .env file
cat > .env << 'EOF'
# Blockify API Keys
BLOCKIFY_API_KEY=blk_your_key_here
OPENAI_API_KEY=sk-your_key_here
EOF
```

### Step 2: Load Environment Variables

**IMPORTANT:** You must load these before running any script:

```bash
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
```

Or add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Blockify environment
export BLOCKIFY_API_KEY="blk_your_key_here"
export OPENAI_API_KEY="sk-your_key_here"
```

### Step 3: Install Dependencies

```bash
cd skills/blockify-integration
python3 scripts/setup_check.py --install
```

**Expected output:**
```
[OK] All packages installed
[OK] API keys configured
[--] ChromaDB not initialized (will create on first ingest)
```

### Step 4: Ingest Documents

```bash
# Single file
python3 scripts/ingest_to_chromadb.py /path/to/document.md

# Directory (batch mode)
python3 scripts/ingest_to_chromadb.py /path/to/documents/ --batch
```

**What happens:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Read File  │───▶│   Chunk     │───▶│  Blockify   │───▶│   Parse     │
│             │    │  (2000 chr) │    │   API       │    │   XML       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                               │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│   Store     │◀───│  Dedupe     │◀───│  Generate   │◀─────────┘
│  ChromaDB   │    │  (by ID)    │    │  Embeddings │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Step 5: Distill (Deduplicate)

**Option A: Docker-based (full service)**
```bash
cd /path/to/blockify-distillation-service
cp .env.example .env
# Add API keys to .env
docker-compose up -d
python3 scripts/run_distillation.py
```

**Option B: Direct API (no Docker required)**
```bash
python3 scripts/distill_chromadb.py
```

**What happens:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    DISTILLATION PROCESS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Pass 1: Within-Document Clustering                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                         │
│  │  Doc A  │  │  Doc B  │  │  Doc C  │                         │
│  │ ┌─┐┌─┐  │  │ ┌─┐┌─┐  │  │ ┌─┐┌─┐  │  (cluster similar      │
│  │ └─┘└─┘  │  │ └─┘└─┘  │  │ └─┘└─┘  │   blocks per doc)      │
│  └─────────┘  └─────────┘  └─────────┘                         │
│       │            │            │                               │
│       ▼            ▼            ▼                               │
│  Pass 2: Cross-Document Clustering                              │
│  ┌──────────────────────────────────┐                          │
│  │  Compare representatives across  │  (find duplicates        │
│  │  all documents for global dedup  │   across documents)      │
│  └──────────────────────────────────┘                          │
│                    │                                            │
│                    ▼                                            │
│  Pass 3: Merge via Blockify Distill API                        │
│  ┌─────────┐    ┌─────────┐                                    │
│  │ Cluster │───▶│ Merged  │  (LLM combines similar blocks)     │
│  │ 5 blocks│    │ 1 block │                                    │
│  └─────────┘    └─────────┘                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 6: Search

```bash
# Search distilled collection (recommended)
python3 scripts/search_chromadb.py "your query" --collection distilled

# Search raw collection
python3 scripts/search_chromadb.py "your query" --collection raw

# Filter by entity type
python3 scripts/search_chromadb.py "your query" --entity PRODUCT

# JSON output
python3 scripts/search_chromadb.py "your query" --json
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────┘

SOURCE FILES                    PROCESSING                      STORAGE
────────────                    ──────────                      ───────

  document1.md ─┐
  document2.md ─┼──▶ ingest_to_chromadb.py ──▶ raw_ideablocks (ChromaDB)
  document3.md ─┤         │                          │
       ...     ─┘         │                          │
                          │                          ▼
                          │               distill_chromadb.py
                          │                          │
                          ▼                          ▼
                   Blockify API              distilled_ideablocks
                   (ingest model)                    │
                          │                          │
                          ▼                          ▼
                   OpenAI Embeddings ◀──────── search_chromadb.py
                   (text-embedding-              (semantic search)
                    3-small, 1536d)

COLLECTIONS:
┌────────────────────────────────────────────────────────────────────────────┐
│ raw_ideablocks        │ Pre-distillation blocks, may have duplicates      │
├────────────────────────────────────────────────────────────────────────────┤
│ distilled_ideablocks  │ Production-ready, deduplicated (USE THIS)         │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concept: IdeaBlocks

An IdeaBlock is a **complete, self-contained unit of knowledge** that answers exactly one question:

```xml
<ideablock>
  <name>Title describing this knowledge unit</name>
  <critical_question>What specific question does this answer?</critical_question>
  <trusted_answer>The validated answer (2-3 sentences, complete).</trusted_answer>
  <tags>IMPORTANT, TECHNOLOGY, CATEGORY</tags>
  <entity>
    <entity_name>PRODUCT_NAME</entity_name>
    <entity_type>PRODUCT</entity_type>
  </entity>
  <keywords>keyword1, keyword2, keyword3</keywords>
</ideablock>
```

**Entity types:** PRODUCT, ORGANIZATION, PERSON, TECHNOLOGY, CONCEPT, LOCATION, EVENT

---

## Model Selection

```
Is the content ordered/sequential (manual, procedure)?
├─ YES → Use `technical-ingest` (preserves order context)
└─ NO → Is this raw source material?
         ├─ YES → Use `ingest` (creates new IdeaBlocks)
         └─ NO → Are these existing IdeaBlocks with duplicates?
                  └─ YES → Use `distill` (merges similar blocks)
```

| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| `ingest` | Raw text | New IdeaBlocks | First-time processing |
| `distill` | IdeaBlocks XML | Merged IdeaBlocks | Deduplication |
| `technical-ingest` | Ordered text + context | Sequenced IdeaBlocks | Manuals, procedures |

---

## Script Reference

### Scripts Overview

```
scripts/
├── setup_check.py          # Verify environment, install deps
├── ingest_to_chromadb.py   # Documents → IdeaBlocks → ChromaDB (parallel)
├── search_chromadb.py      # Semantic search with OpenAI embeddings
├── distill_chromadb.py     # Deduplication (NO Docker required)
├── run_distillation.py     # Deduplication (requires Docker service)
├── run_full_pipeline.py    # End-to-end: ingest + distill + benchmark (parallel)
├── run_benchmark.py        # Compare IdeaBlocks vs chunking, generate HTML report
├── blockify_ingest.py      # Documents → JSON (no ChromaDB)
├── blockify_distill.py     # JSON → distilled JSON
└── blockify_search.py      # Search JSON files
```

**Note:** Ingestion scripts use 5 parallel workers by default. Configure via `--parallel N` flag or `BLOCKIFY_PARALLEL_WORKERS` environment variable.

### Detailed Script Usage

#### setup_check.py
```bash
python3 scripts/setup_check.py           # Check status
python3 scripts/setup_check.py --install # Install missing packages
```

#### ingest_to_chromadb.py
```bash
python3 scripts/ingest_to_chromadb.py input.txt              # Single file
python3 scripts/ingest_to_chromadb.py docs/ --batch          # Directory (5 parallel workers)
python3 scripts/ingest_to_chromadb.py docs/ --batch -p 10    # Use 10 parallel workers
python3 scripts/ingest_to_chromadb.py docs/ --batch -s       # Sequential processing
python3 scripts/ingest_to_chromadb.py input.txt -c distilled # Target collection
```

#### search_chromadb.py
```bash
python3 scripts/search_chromadb.py "query"                    # Auto-select collection
python3 scripts/search_chromadb.py "query" -c distilled       # Specific collection
python3 scripts/search_chromadb.py "query" -e PRODUCT         # Filter by entity
python3 scripts/search_chromadb.py "query" -n 20              # Limit results
python3 scripts/search_chromadb.py "query" --json             # JSON output
```

#### distill_chromadb.py (NO Docker)
```bash
python3 scripts/distill_chromadb.py                           # Default settings
python3 scripts/distill_chromadb.py --threshold 0.8           # Higher = fewer merges
python3 scripts/distill_chromadb.py --dry-run                 # Cluster only, no API calls
```

---

## Troubleshooting

### Common Errors and Solutions

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ERROR                          │ CAUSE              │ SOLUTION             │
├────────────────────────────────────────────────────────────────────────────┤
│ DuplicateIDError               │ Same IdeaBlock     │ Script handles this  │
│ "found duplicates of: ib_..."  │ extracted twice    │ automatically now    │
├────────────────────────────────────────────────────────────────────────────┤
│ InvalidArgumentError           │ Embedding model    │ Use search_chromadb  │
│ "dimension 1536, got 384"      │ mismatch           │ (fixed in script)    │
├────────────────────────────────────────────────────────────────────────────┤
│ BLOCKIFY_API_KEY not set       │ Missing env var    │ export $(cat .env    │
│                                │                    │ | grep -v '^#' |     │
│                                │                    │ grep -v '^$' | xargs)│
├────────────────────────────────────────────────────────────────────────────┤
│ 429 Rate Limit                 │ Too many requests  │ Script retries with  │
│                                │                    │ exponential backoff  │
├────────────────────────────────────────────────────────────────────────────┤
│ Empty output from API          │ max_tokens too low │ Use 8000+ tokens     │
│                                │                    │ (default in scripts) │
├────────────────────────────────────────────────────────────────────────────┤
│ ChromaDB not found             │ Not initialized    │ Run ingest first     │
├────────────────────────────────────────────────────────────────────────────┤
│ Distillation service not       │ Docker not running │ Use distill_chromadb │
│ available                      │ OR no Docker       │ .py (no Docker)      │
└────────────────────────────────────────────────────────────────────────────┘
```

### Important Technical Notes

1. **Embedding Model Consistency**
   - Ingestion uses: `text-embedding-3-small` (OpenAI, 1536 dimensions)
   - Search MUST use the same model
   - The `search_chromadb.py` script handles this automatically

2. **Duplicate Handling**
   - IdeaBlock IDs are SHA256 hashes of `name + question + answer`
   - Identical content = identical ID (by design)
   - `ingest_to_chromadb.py` deduplicates within each batch automatically

3. **Chunking Strategy**
   - 2000 characters per chunk
   - 200 character overlap at sentence boundaries
   - Optimal for Blockify API processing

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BLOCKIFY_API_KEY` | Yes | - | API key from console.blockify.ai |
| `OPENAI_API_KEY` | Yes | - | API key from platform.openai.com |
| `IDEABLOCK_DATA_DIR` | No | `./data/ideablocks` | Data storage directory |
| `DISTILL_SERVICE_URL` | No | `http://localhost:8315` | Distillation service URL |
| `BLOCKIFY_PARALLEL_WORKERS` | No | `5` | Default parallel workers for ingestion |

### API Settings (Do Not Change)

| Parameter | Value | Reason |
|-----------|-------|--------|
| max_tokens | 8000 | Minimum for complete blocks |
| temperature | 0.5 | Calibrated for consistency |
| chunk_size | 2000 chars | Optimal input chunking |

---

## Search Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SEARCH FLOW                                        │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
   User Query ────▶ │ OpenAI Embedding│ ────▶ Query Vector (1536-d)
                    │ text-embedding- │
                    │ 3-small         │
                    └─────────────────┘
                                              │
                                              ▼
                                   ┌─────────────────┐
                                   │ ChromaDB Query  │
                                   │ (cosine sim)    │
                                   └─────────────────┘
                                              │
                                              ▼
                                   ┌─────────────────┐
                                   │ Top-K Results   │
                                   │ (no reranker)   │
                                   └─────────────────┘

CURRENT LIMITATIONS:
- Single-stage retrieval only (no reranking)
- No hybrid search (vector only, no BM25)
- No query expansion

POTENTIAL IMPROVEMENTS:
- Add cross-encoder reranker for top-100 → top-10
- Implement hybrid search with BM25
- Add query expansion via LLM
```

---

## Quick Reference Commands

```bash
# ═══════════════════════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════════════════════

# Load environment (run this first, every session)
export $(cat /path/to/.env | grep -v '^#' | grep -v '^$' | xargs)

# Check setup
python3 scripts/setup_check.py

# Install dependencies
python3 scripts/setup_check.py --install

# ═══════════════════════════════════════════════════════════════════════════
# INGEST (parallel by default, 5 workers)
# ═══════════════════════════════════════════════════════════════════════════

# Single file
python3 scripts/ingest_to_chromadb.py document.md

# Directory of files (5 parallel workers by default)
python3 scripts/ingest_to_chromadb.py /path/to/docs/ --batch

# Use more parallel workers for faster ingestion
python3 scripts/ingest_to_chromadb.py /path/to/docs/ --batch --parallel 10

# Sequential processing (disable parallelization)
python3 scripts/ingest_to_chromadb.py /path/to/docs/ --batch --sequential

# ═══════════════════════════════════════════════════════════════════════════
# DISTILL (DEDUPLICATE)
# ═══════════════════════════════════════════════════════════════════════════

# Without Docker (recommended for most users)
python3 scripts/distill_chromadb.py

# With Docker service
python3 scripts/run_distillation.py

# ═══════════════════════════════════════════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════════════════════════════════════════

# Basic search (uses distilled if available)
python3 scripts/search_chromadb.py "your query"

# Search specific collection
python3 scripts/search_chromadb.py "your query" --collection distilled

# Filter by entity
python3 scripts/search_chromadb.py "your query" --entity PRODUCT

# JSON output
python3 scripts/search_chromadb.py "your query" --json --limit 5

# ═══════════════════════════════════════════════════════════════════════════
# BENCHMARK (compare IdeaBlocks vs traditional chunking)
# ═══════════════════════════════════════════════════════════════════════════

# Run benchmark (generates HTML report)
python3 scripts/run_benchmark.py

# With custom company name
python3 scripts/run_benchmark.py --company "My Company"

# With custom config
python3 scripts/run_benchmark.py --config ./config/benchmark_config.yaml

# Create default config file
python3 scripts/run_benchmark.py --init-config

# View generated report
open data/reports/benchmark_report_*.html
```

---

## Required Execution Workflow (For Autonomous/Skill Use)

**IMPORTANT:** When running Blockify as a skill or autonomous task, you MUST complete ALL steps below in order. Do not skip any step.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REQUIRED EXECUTION STEPS (IN ORDER)                       │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Environment Setup
    └─► Verify API keys configured
    └─► Run setup_check.py to confirm dependencies

Step 2: Document Ingestion
    └─► Run ingest_to_chromadb.py with --batch for directories
    └─► Record: file count, block count, any errors

Step 3: Distillation (Deduplication)
    └─► Run distill_chromadb.py (no Docker required)
    └─► Record: clusters found, blocks merged, reduction %

Step 4: Search Verification
    └─► Run at least 3 different test queries
    └─► Verify results are relevant (scores > 0.5)
    └─► Test both text and JSON output formats

Step 5: Benchmark (REQUIRED - DO NOT SKIP)          ◄── MANDATORY
    └─► Run: python3 scripts/run_benchmark.py --company "Company Name"
    └─► Record all metrics from output:
        - Vector Search Accuracy (X improvement)
        - Information Distillation (X reduction)
        - Aggregate Performance (X)
        - Enterprise Performance (X)
        - Token Efficiency (X)
        - Projected Annual Savings ($X)
    └─► Note the report file path for reference

Step 6: Documentation/Changelog
    └─► Create or update CHANGELOG.md in target directory
    └─► Include ALL metrics from Steps 2-5
    └─► Document any errors or issues encountered
    └─► Note any confusing steps for documentation improvement
```

### Why Benchmark is Required

The benchmark compares IdeaBlocks performance against traditional chunking methods. Without running the benchmark:
- You cannot quantify the improvement from using Blockify
- You have no baseline for comparison
- The value proposition cannot be demonstrated

### Benchmark Output Metrics Explained

| Metric | What It Measures | Good Value |
|--------|-----------------|------------|
| Vector Search Accuracy | How much closer IdeaBlocks are to query intent vs chunks | > 2.0X |
| Information Distillation | Word count reduction while preserving meaning | > 1.2X |
| Aggregate Performance | Combined accuracy × distillation improvement | > 3.0X |
| Enterprise Performance | Aggregate × scale factor for enterprise workloads | > 40X |
| Token Efficiency | LLM token savings from using IdeaBlocks | > 3.0X |

---

## Example Session (Complete Workflow)

```bash
# 1. Navigate to skill directory
cd /path/to/blockify-skill-for-claude-code/skills/blockify-integration

# 2. Create .env file with your API keys
cat > ../../.env << 'EOF'
BLOCKIFY_API_KEY=blk_your_key_here
OPENAI_API_KEY=sk-your_key_here
BLOCKIFY_PARALLEL_WORKERS=5
EOF

# 3. Load environment
export $(cat ../../.env | grep -v '^#' | grep -v '^$' | xargs)

# 4. Install dependencies
python3 scripts/setup_check.py --install

# 5. Ingest documents (parallel by default, 5 workers)
python3 scripts/ingest_to_chromadb.py /path/to/documents/ --batch

# Or use more workers for faster ingestion
python3 scripts/ingest_to_chromadb.py /path/to/documents/ --batch --parallel 10

# 6. Run distillation (no Docker needed)
python3 scripts/distill_chromadb.py

# 7. Search your knowledge base (run multiple test queries)
python3 scripts/search_chromadb.py "what are the key features?" --collection distilled
python3 scripts/search_chromadb.py "product benefits" --collection distilled
python3 scripts/search_chromadb.py "technical specifications" --collection distilled --json

# 8. Run benchmark (REQUIRED - generates HTML report with metrics)
python3 scripts/run_benchmark.py --company "Your Company Name"

# 9. View benchmark report
open data/reports/benchmark_report_*.html

# 10. Export results as JSON for further processing
python3 scripts/search_chromadb.py "important concepts" --json --limit 20 > results.json
```

---

## Scale Considerations

| Dataset Size | Recommended Approach | Storage | Search Time |
|--------------|---------------------|---------|-------------|
| < 1,000 blocks | JSON files | ~10 MB | Instant |
| 1K - 10K blocks | ChromaDB, no distill | ~50 MB | < 100ms |
| 10K - 100K blocks | ChromaDB + distill | ~500 MB | < 100ms |
| 100K+ blocks | ChromaDB + distill + FAISS | ~2 GB | < 50ms |

**Distillation time estimates (2,000+ blocks):**
- Pass 1 (within-document): ~30 seconds
- Pass 2 (cross-document): ~10-15 minutes
- Pass 3 (API merges): ~1-2 seconds per cluster

---

## References

- **API Details**: See [references/API.md](references/API.md)
- **IdeaBlock Schema**: See [references/SCHEMA.md](references/SCHEMA.md)
- **Distillation Algorithms**: See [references/DISTILLATION.md](references/DISTILLATION.md)
- **Benchmark Guide**: See [BENCHMARK-GUIDE.md](BENCHMARK-GUIDE.md)
- **Distillation Service**: https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization/blockify-distillation-service
