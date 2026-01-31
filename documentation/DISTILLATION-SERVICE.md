# Blockify Auto-Dedupe Distillation Service

**Document Purpose:** Technical guide for deploying and using the Blockify Auto-Dedupe Server to cluster and merge similar IdeaBlocks at enterprise scale (100k+ blocks).

**Reference Implementation:** `/Volumes/HEDRA4TB/John/Documents/GitHub/blockify-distill-python-server`

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Algorithms Deep Dive](#algorithms-deep-dive)
4. [Deployment](#deployment)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Scaling to 100k+ Blocks](#scaling-to-100k-blocks)
8. [Integration Guide](#integration-guide)

---

## Overview

The Blockify Auto-Dedupe Server is a **headless Python service** that intelligently deduplicates and merges IdeaBlocks using:

- **LSH (Locality-Sensitive Hashing)** for candidate pair reduction
- **FAISS-based similarity search** for efficient nearest neighbor lookup
- **Louvain/BFS clustering** for grouping similar blocks
- **Hierarchical LLM merging** for intelligent content consolidation
- **Iterative refinement** with progressive threshold increases

### Key Results

| Metric | Typical Value |
|--------|---------------|
| **Block Reduction** | 60-70% |
| **Processing Time (100k)** | 2-2.5 hours |
| **Memory Usage** | ~2GB peak |
| **Accuracy Preservation** | ~95% lossless |

---

## Architecture

### High-Level Flow

```
+===========================================================================+
|                    DISTILLATION PIPELINE                                  |
+===========================================================================+

[Input IdeaBlocks]
        |
        v
+--------------------------------------------------+
| 1. EMBEDDING GENERATION                           |
|    • Model: text-embedding-3-small (1536 dim)    |
|    • Batch size: 1000 blocks                      |
|    • Text: name + question + answer               |
+--------------------------------------------------+
        |
        v
+--------------------------------------------------+
| 2. CANDIDATE PAIR SELECTION                       |
|    • LSH bucketing (100k+ scale)                 |
|    • OR Dense similarity (<50 items)              |
|    • Reduces O(n²) → O(n×k)                      |
+--------------------------------------------------+
        |
        v
+--------------------------------------------------+
| 3. ITERATIVE CLUSTERING LOOP (4 iterations)       |
|    ┌─────────────────────────────────────────┐   |
|    │ a. Find similar pairs (cosine > threshold)│  |
|    │ b. Create clusters (Louvain/BFS)          │  |
|    │ c. LLM merge clusters (hierarchical)      │  |
|    │ d. Re-embed merged results                 │  |
|    │ e. Increase threshold (+0.01)             │  |
|    └─────────────────────────────────────────┘   |
+--------------------------------------------------+
        |
        v
+--------------------------------------------------+
| 4. OUTPUT ASSEMBLY                                |
|    • Original blocks: marked hidden              |
|    • Merged blocks: visible, linked to parents   |
|    • Statistics: reduction %, counts             |
+--------------------------------------------------+
        |
        v
[Distilled IdeaBlocks] (60-70% fewer)
```

### Component Architecture

```
+===========================================================================+
|                    SERVICE COMPONENTS                                     |
+===========================================================================+

┌─────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                   │
│  FastAPI + Uvicorn                                                       │
│  • POST /api/autoDistill (sync/async)                                   │
│  • GET /api/jobs/{job_id}                                               │
│  • GET /healthz                                                          │
└─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICE ORCHESTRATION                            │
│  • Job management (create, poll, timeout)                               │
│  • Progress tracking (percent, phase, details)                          │
│  • Disk persistence for recovery                                        │
└─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORE ALGORITHM                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │
│  │  Embeddings   │  │  Similarity   │  │  Clustering   │               │
│  │  (OpenAI)     │  │  (FAISS+LSH)  │  │  (Louvain)    │               │
│  └───────────────┘  └───────────────┘  └───────────────┘               │
│                                                                          │
│  ┌───────────────┐  ┌───────────────┐                                   │
│  │  LLM Merge    │  │  XML Parser   │                                   │
│  │  (Hierarchical)│  │  (Robust)     │                                   │
│  └───────────────┘  └───────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Algorithms Deep Dive

### 1. LSH (Locality-Sensitive Hashing)

**Purpose:** Reduce candidate pairs from O(n²) to O(n×k) for large datasets.

```
ALGORITHM: LSH Bucketing
─────────────────────────

Parameters:
  • NUM_HASH_TABLES = 10
  • NUM_HASH_BITS = 8
  • MIN_ITEMS_TO_ENABLE = 50

Process:
  1. Create 10 random hyperplanes (1536-dim each)
  2. For each vector:
     • Compute: sign(dot(hyperplane, vector)) for each hyperplane
     • Concatenate bits → 8-bit hash per table
  3. Vectors with same hash → same bucket
  4. Candidate pairs = vectors sharing any bucket

Complexity: O(n × num_tables × num_bits)

Example (100k blocks):
  • Without LSH: 5 billion pair comparisons
  • With LSH: ~500k candidate pairs
  • Reduction: 10,000x fewer comparisons
```

### 2. FAISS Similarity Search

**Purpose:** Efficient k-nearest neighbor search using approximate methods.

```python
# Sparse similarity for large datasets (≥50 items)
def sparse_similarity(embeddings, threshold=0.55, k=50):
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    # Create flat inner product index
    index = faiss.IndexFlatIP(dim=1536)
    index.add(embeddings)

    # K-NN search (k+1 to exclude self)
    similarities, indices = index.search(embeddings, k + 1)

    # Filter pairs above threshold
    pairs = []
    for i, (sims, idxs) in enumerate(zip(similarities, indices)):
        for sim, j in zip(sims, idxs):
            if i < j and sim >= threshold:  # Avoid duplicates
                pairs.append((i, j, sim))

    return pairs
```

### 3. Clustering Algorithms

**Two strategies based on dataset size:**

```
LOUVAIN COMMUNITY DETECTION (≥1000 nodes)
─────────────────────────────────────────
• Graph-based community detection
• Optimizes modularity
• Better for large, interconnected clusters
• O(n log n) complexity

BFS CONNECTED COMPONENTS (<1000 nodes)
─────────────────────────────────────────
• Simple graph traversal
• Creates non-overlapping clusters
• O(n + e) complexity
• Faster for smaller graphs
```

### 4. Hierarchical LLM Merging

**Problem:** Large clusters (>20 blocks) exceed LLM context limits.

**Solution:** Recursive subclustering

```
HIERARCHICAL MERGE ALGORITHM
────────────────────────────

Input: Cluster of N blocks

if N ≤ 20:
    return LLM_merge(cluster)

else:
    # Calculate target subcluster size
    target_size = min(20, max(5, floor(sqrt(N) * 2)))

    # Split deterministically by UUID ordering
    subclusters = split(cluster, target_size)

    # Process subclusters in parallel (5 threads)
    results = parallel_map(LLM_merge, subclusters)

    # Flatten results
    merged = flatten(results)

    # Recurse if still too large
    if len(merged) > 20:
        return hierarchical_merge(merged)

    return merged

Example (100 blocks):
  • sqrt(100) * 2 = 20 blocks per subcluster
  • 5 subclusters processed in parallel
  • Results merged, recursion if needed
```

### 5. Iterative Refinement

```
ITERATION PROGRESSION
─────────────────────

Iteration 1: threshold = 0.55 (coarse matching)
  → Catches obvious duplicates
  → High recall, some false positives

Iteration 2: threshold = 0.56 (start increasing)
  → Tighter matching
  → Catches similarities between merged blocks

Iteration 3: threshold = 0.57
  → Even tighter
  → Diminishing returns begin

Iteration 4: threshold = 0.58 (final pass)
  → Fine-grained cleanup
  → Maximum threshold = 0.98 (configurable)
```

---

## Deployment

### Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/iternal/blockify-distill-python-server.git
cd blockify-distill-python-server

# Build Docker image
docker build -t blockify-dedupe:latest .

# Run with environment variables
docker run -d \
  --name blockify-dedupe \
  -p 8315:8315 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY="sk-..." \
  -e BLOCKIFY_API_KEY="blk_..." \
  -e USE_BLOCKIFY_LLM="true" \
  blockify-dedupe:latest
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="sk-..."
export BLOCKIFY_API_KEY="blk_..."
export USE_BLOCKIFY_LLM="true"

# Run server
python -m uvicorn app.api:app --host 0.0.0.0 --port 8315
```

### Health Check

```bash
curl http://localhost:8315/healthz

# Response:
{
  "status": "ok",
  "model": "distill",
  "embedding_model": "text-embedding-3-small",
  "max_cluster_size": "20"
}
```

---

## API Reference

### POST /api/autoDistill

Submit a deduplication job.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `wait` | boolean | false | Synchronous (true) or async (false) |

**Request Body:**

```json
{
  "blockifyTaskUUID": "task-uuid",
  "similarity": 0.55,
  "iterations": 4,
  "results": [
    {
      "type": "blockify",
      "blockifyResultUUID": "block-uuid",
      "blockifiedTextResult": {
        "name": "IdeaBlock Title",
        "criticalQuestion": "What question?",
        "trustedAnswer": "The answer.",
        "tags": "TAG1, TAG2",
        "keywords": "key1, key2"
      },
      "hidden": false,
      "exported": false,
      "reviewed": false
    }
  ]
}
```

**Response (Async):**

```json
{
  "schemaVersion": 1,
  "jobId": "job-uuid"
}
```

**Response (Sync/Complete):**

```json
{
  "schemaVersion": 1,
  "status": "success",
  "stats": {
    "startingBlockCount": 1000,
    "finalBlockCount": 350,
    "blocksRemoved": 750,
    "blocksAdded": 100,
    "blockReductionPercent": 65.0
  },
  "results": [
    {
      "type": "merged",
      "blockifyResultUUID": "merged-uuid",
      "blockifiedTextResult": {...},
      "hidden": false,
      "blockifyResultsUsed": ["original-uuid-1", "original-uuid-2"]
    },
    {
      "type": "blockify",
      "blockifyResultUUID": "original-uuid",
      "hidden": true
    }
  ]
}
```

### GET /api/jobs/{job_id}

Poll job status.

**Response:**

```json
{
  "schemaVersion": 1,
  "status": "running",
  "progress": {
    "percent": 45.5,
    "phase": "iteration",
    "details": {
      "iteration": 2,
      "block_count": 500,
      "threshold": 0.56
    }
  }
}
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| **Server** | | |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8315` | Server port |
| `LOG_LEVEL` | `INFO` | Log verbosity |
| **LLM Provider** | | |
| `USE_BLOCKIFY_LLM` | `false` | Use Blockify distill model |
| `BLOCKIFY_API_KEY` | - | Blockify API key |
| `BLOCKIFY_BASE_URL` | `https://api.blockify.ai/v1` | Blockify endpoint |
| `OPENAI_API_KEY` | - | OpenAI API key (fallback) |
| `LLM_MODEL_NAME` | `gpt-4.1-mini-2025-04-14` | OpenAI model |
| **Embeddings** | | |
| `EMBEDDING_MODEL_NAME` | `text-embedding-3-small` | Embedding model |
| **Algorithm** | | |
| `SIMILARITY_INCREASE_PER_ITERATION` | `0.01` | Threshold increment |
| `MAX_SIMILARITY_THRESHOLD` | `0.98` | Maximum threshold |
| `MAX_CLUSTER_SIZE_FOR_LLM` | `20` | Blocks before subclustering |
| `LOUVAIN_NODE_THRESHOLD` | `1000` | When to use Louvain |
| **LSH** | | |
| `USE_LSH` | `true` | Enable LSH for large datasets |
| `MAX_SIMILARITY_NEIGHBORS` | `50` | k-NN k value |
| **Performance** | | |
| `LLM_PARALLEL_THREADS` | `5` | Parallel merge threads |
| `JOB_TIMEOUT_SECONDS` | `1200` | Max job time (20 min) |
| `MAX_WORKERS` | `4` | Thread pool size |

---

## Scaling to 100k+ Blocks

### Memory Profile

```
100k BLOCKS MEMORY BREAKDOWN
────────────────────────────

Embeddings:     100k × 1536 × 4 bytes = ~600MB
FAISS Index:    ~600MB (flat index)
Block Metadata: ~50MB
Working Memory: ~200MB
────────────────────────────
Total Peak:     ~1.5GB

Without LSH (full matrix):
Similarity:     100k × 100k × 4 = ~40GB ❌
```

### Performance Expectations

| Dataset Size | Embedding Time | Total Time | Memory |
|--------------|---------------|------------|--------|
| 1k blocks | ~30s | ~5 min | ~100MB |
| 10k blocks | ~5 min | ~30 min | ~500MB |
| 100k blocks | ~50 min | ~2.5 hours | ~2GB |
| 1M blocks | ~8 hours | ~24 hours | ~20GB |

### Optimization Strategies

```python
# 1. Use LSH (enabled by default)
USE_LSH = "true"

# 2. Tune FAISS k-NN
MAX_SIMILARITY_NEIGHBORS = 50  # Increase for better recall

# 3. Parallel LLM processing
LLM_PARALLEL_THREADS = 5  # Increase if API allows

# 4. Batch embeddings
# Already batched at 1000 blocks per API call

# 5. Incremental processing
# Process in chunks if memory constrained:
#   - Split 1M blocks into 10 × 100k jobs
#   - Run distillation on each
#   - Final distillation pass on merged results
```

---

## Integration Guide

### With ChromaDB Local Database

```python
#!/usr/bin/env python3
"""
Full integration: ChromaDB → Distillation → ChromaDB
"""

import os
import requests
import chromadb
from typing import List, Dict

DISTILL_SERVER = os.environ.get('BLOCKIFY_DISTILL_SERVER', 'http://localhost:8315')


def full_distillation_pipeline(
    raw_collection: chromadb.Collection,
    distilled_collection: chromadb.Collection
):
    """
    Complete pipeline:
    1. Export raw blocks from ChromaDB
    2. Submit to distillation service
    3. Poll until complete
    4. Import distilled blocks to ChromaDB
    """

    # 1. Export
    print(f"Exporting {raw_collection.count()} blocks...")
    results = raw_collection.get(include=['metadatas'])

    blocks = []
    for i, id in enumerate(results['ids']):
        meta = results['metadatas'][i]
        blocks.append({
            "type": "blockify",
            "blockifyResultUUID": id,
            "blockifiedTextResult": {
                "name": meta['name'],
                "criticalQuestion": meta['critical_question'],
                "trustedAnswer": meta['trusted_answer'],
                "tags": meta.get('tags', ''),
                "keywords": meta.get('keywords', '')
            },
            "hidden": False
        })

    # 2. Submit job
    print("Submitting distillation job...")
    response = requests.post(
        f"{DISTILL_SERVER}/api/autoDistill?wait=false",
        json={
            "blockifyTaskUUID": f"chromadb_{len(blocks)}",
            "similarity": 0.55,
            "iterations": 4,
            "results": blocks
        }
    )
    job_id = response.json()['jobId']
    print(f"Job ID: {job_id}")

    # 3. Poll
    print("Waiting for completion...")
    while True:
        status = requests.get(f"{DISTILL_SERVER}/api/jobs/{job_id}").json()
        progress = status.get('progress', {})
        print(f"  Status: {status['status']}, Progress: {progress.get('percent', 0):.1f}%")

        if status['status'] in ['success', 'failure', 'timeout']:
            break

        import time
        time.sleep(10)

    if status['status'] != 'success':
        raise Exception(f"Distillation failed: {status.get('error')}")

    # 4. Import distilled blocks
    print("Importing distilled blocks...")
    from ingest_ideablocks import generate_embeddings

    merged_blocks = [r for r in status['results'] if r.get('type') == 'merged']

    ids = []
    documents = []
    metadatas = []

    for block in merged_blocks:
        text = block['blockifiedTextResult']
        ids.append(block['blockifyResultUUID'])
        documents.append(f"{text['name']} {text['criticalQuestion']} {text['trustedAnswer']}")
        metadatas.append({
            'name': text['name'],
            'critical_question': text['criticalQuestion'],
            'trusted_answer': text['trustedAnswer'],
            'tags': text.get('tags', ''),
            'block_type': 'distilled',
            'parent_blocks': ','.join(block.get('blockifyResultsUsed', []))
        })

    # Generate embeddings
    embeddings = generate_embeddings(documents)

    # Upsert to distilled collection
    distilled_collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    stats = status.get('stats', {})
    print(f"\nDistillation complete!")
    print(f"  Raw blocks: {stats.get('startingBlockCount', len(blocks))}")
    print(f"  Distilled blocks: {stats.get('finalBlockCount', len(merged_blocks))}")
    print(f"  Reduction: {stats.get('blockReductionPercent', 0):.1f}%")
```

### With Claude Code Skill

```markdown
# Update skill to use distillation service

## Distillation Commands

### Run Distillation
```bash
# Export, distill, import in one command
python {baseDir}/scripts/full_distillation.py
```

### Check Job Status
```bash
curl http://localhost:8315/api/jobs/{job_id}
```

### View Statistics
After distillation, check collection counts:
```bash
python {baseDir}/scripts/stats.py
```
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Job timeout | Dataset too large | Increase `JOB_TIMEOUT_SECONDS` |
| OOM error | Too many blocks | Enable LSH, reduce batch size |
| Low reduction % | Diverse content | Lower initial similarity threshold |
| LLM errors | Rate limits | Reduce `LLM_PARALLEL_THREADS` |
| Inconsistent results | Non-deterministic | Sort by UUID before clustering |

---

*Document created: 2026-01-25*
*Based on: blockify-distill-python-server codebase analysis*
