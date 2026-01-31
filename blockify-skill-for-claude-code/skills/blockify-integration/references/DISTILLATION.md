# Distillation Algorithm Reference

## Overview

The distillation service merges semantically similar IdeaBlocks at 100k+ scale using a multi-stage pipeline optimized for O(n log n) complexity rather than naive O(n^2) pairwise comparison.

## Pipeline Stages

```
┌─────────────────┐
│  Raw IdeaBlocks │  100k+ blocks with duplicates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LSH Indexing  │  Locality-Sensitive Hashing for O(n×k) candidates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FAISS k-NN     │  Dense vector similarity search
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Clustering     │  Louvain/BFS for non-overlapping groups
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Merging    │  Hierarchical merge for clusters >20
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Distilled Blocks│  Deduplicated, production-ready
└─────────────────┘
```

## Stage 1: LSH Candidate Selection

**Algorithm:** MinHash with multiple hash tables

```
For each IdeaBlock:
  1. Generate MinHash signature (128 permutations)
  2. Band into 16 bands × 8 rows
  3. Hash each band → bucket
  4. Candidates = blocks sharing any bucket
```

**Complexity:** O(n × k) where k = average candidates per block (~50-200)

**Why LSH:** Avoids O(n^2) pairwise comparison. At 100k blocks, reduces from 5B comparisons to ~10M.

## Stage 2: FAISS Similarity Search

**Index Type:** IVF (Inverted File) with PQ (Product Quantization)

```python
# Configuration
index = faiss.index_factory(dimension, "IVF1024,PQ32")
index.nprobe = 64  # Search 64 of 1024 clusters
```

**Threshold:** cosine similarity > 0.55 (configurable)

**Output:** Similarity graph where edges = similar block pairs

## Stage 3: Clustering

**Algorithm:** Louvain community detection on similarity graph

```
1. Build graph: nodes = blocks, edges = similarity > threshold
2. Run Louvain to find communities
3. For disconnected subgraphs, use BFS components
4. Output: Non-overlapping clusters
```

**Cluster size distribution (typical 100k dataset):**
- 60% singletons (no merging needed)
- 30% pairs/triplets
- 8% medium clusters (4-20 blocks)
- 2% large clusters (>20 blocks)

## Stage 4: LLM Merging

### Small Clusters (2-20 blocks)

Single LLM call with all blocks:

```
Merge these IdeaBlocks into consolidated blocks.
Preserve all unique facts. Combine overlapping information.
Output XML format.

<ideablock>...</ideablock>
<ideablock>...</ideablock>
```

### Large Clusters (>20 blocks)

Hierarchical merging to avoid context limits:

```
Level 0: [100 blocks] → split into 5 groups of 20
Level 1: [5 merged blocks from each group]
Level 2: [Final consolidated block(s)]
```

**Max blocks per LLM call:** 20 (fits in 8k context with XML)

## Configuration

```toml
[distillation]
similarity_threshold = 0.55      # Initial threshold
refinement_threshold = 0.58      # Second pass
max_cluster_size = 20            # Before hierarchical split
lsh_bands = 16
lsh_rows = 8
faiss_nprobe = 64
```

## Iterative Refinement

After initial distillation, run second pass with higher threshold:

```bash
# Pass 1: Aggressive merging
python run_distillation.py --threshold 0.55

# Pass 2: Catch remaining duplicates
python run_distillation.py --threshold 0.58 --input distilled_pass1
```

Typical reduction:
- Pass 1: 100k → 40k blocks
- Pass 2: 40k → 35k blocks

## Docker Setup

The distillation service is available as an open-source Docker image:

```bash
# Clone the distillation service
git clone https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization/blockify-distillation-service.git
cd blockify-distillation-service

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
# BLOCKIFY_API_KEY=your-blockify-key
# OPENAI_API_KEY=your-openai-key

# Start the service
docker-compose up -d

# Check health
curl http://localhost:8315/healthz
```

### Submit Distillation Job

```bash
curl -X POST http://localhost:8315/api/autoDistill \
  -H "Content-Type: application/json" \
  -d '{
    "blockifyTaskUUID": "task-123",
    "similarity": 0.55,
    "iterations": 4,
    "results": [...]
  }'

# Response: {"schemaVersion": 1, "jobId": "job-uuid"}
```

### Poll for Results

```bash
curl http://localhost:8315/api/jobs/{jobId}
```

### Kubernetes Deployment

```bash
helm install distill ./helm/blockify-distillation \
  --set secrets.blockifyApiKey=your-key \
  --set secrets.openaiApiKey=your-key
```

## Performance Benchmarks

| Dataset Size | LSH Time | Clustering | LLM Merging | Total |
|-------------|----------|------------|-------------|-------|
| 10k blocks | 30s | 10s | 5min | ~6min |
| 100k blocks | 5min | 2min | 45min | ~52min |
| 500k blocks | 25min | 10min | 3hr | ~3.5hr |

**Note:** LLM merging dominates at scale. Use parallel workers for production.
