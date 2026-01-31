# Blockify Distillation Service

Open-source deduplication and merging service for IdeaBlocks. Uses embeddings, clustering algorithms, and LLM synthesis to consolidate similar knowledge blocks.

## Features

- **Embedding-based similarity**: Uses OpenAI embeddings for semantic similarity
- **Efficient clustering**: LSH bucketing for large datasets, Louvain/BFS for graph clustering
- **LLM merging**: Blockify API for intelligent content synthesis
- **Async job processing**: Background processing with progress tracking
- **Multiple backends**: SQLite (default), PostgreSQL, Redis, or filesystem
- **Production ready**: Docker, Helm charts, Prometheus metrics, OpenTelemetry tracing

## Quick Start

### Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization/blockify-distillation-service.git
cd blockify-distillation-service

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# BLOCKIFY_API_KEY=your-blockify-api-key
# OPENAI_API_KEY=your-openai-api-key

# Start the service
docker-compose up -d

# Check health
curl http://localhost:8315/healthz
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BLOCKIFY_API_KEY=your-blockify-api-key
export OPENAI_API_KEY=your-openai-api-key

# Run the service
python -m app.api
```

## API Usage

### Submit Distillation Job

```bash
curl -X POST http://localhost:8315/api/autoDistill \
  -H "Content-Type: application/json" \
  -d '{
    "blockifyTaskUUID": "task-123",
    "similarity": 0.55,
    "iterations": 4,
    "results": [
      {
        "type": "blockify",
        "blockifyResultUUID": "block-1",
        "blockifiedTextResult": {
          "name": "Topic A",
          "criticalQuestion": "What is Topic A?",
          "trustedAnswer": "Topic A is..."
        }
      }
    ]
  }'
```

Response:
```json
{
  "schemaVersion": 1,
  "jobId": "job-uuid-here"
}
```

### Poll for Results

```bash
curl http://localhost:8315/api/jobs/{jobId}
```

Response (when complete):
```json
{
  "schemaVersion": 1,
  "status": "success",
  "stats": {
    "startingBlockCount": 100,
    "finalBlockCount": 25,
    "blocksRemoved": 100,
    "blocksAdded": 25,
    "blockReductionPercent": 75.0
  },
  "results": [...]
}
```

## Configuration

All configuration is via environment variables. See `.env.example` for full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `BLOCKIFY_API_KEY` | (required) | Blockify API key for LLM merging |
| `OPENAI_API_KEY` | (required) | OpenAI API key for embeddings |
| `PORT` | 8315 | Server port |
| `DATABASE_BACKEND` | sqlite | Backend: sqlite, postgresql, redis, filesystem |
| `MAX_CLUSTER_SIZE_FOR_LLM` | 20 | Max blocks per LLM merge call |
| `LLM_PARALLEL_THREADS` | 5 | Parallel LLM request threads |
| `PROMETHEUS_ENABLED` | true | Enable /metrics endpoint |

## Kubernetes Deployment

```bash
# Using Helm
helm install distill ./helm/blockify-distillation \
  --set secrets.blockifyApiKey=your-key \
  --set secrets.openaiApiKey=your-key

# Or with existing secret
kubectl create secret generic blockify-secrets \
  --from-literal=BLOCKIFY_API_KEY=your-key \
  --from-literal=OPENAI_API_KEY=your-key

helm install distill ./helm/blockify-distillation \
  --set secrets.existingSecret=blockify-secrets
```

## Algorithm Overview

1. **Embedding Generation**: Convert blocks to vectors using OpenAI embeddings
2. **LSH Bucketing**: Group similar items using Locality-Sensitive Hashing (for large datasets)
3. **Similarity Search**: Find pairs above threshold using FAISS k-NN
4. **Clustering**: Create non-overlapping clusters via Louvain (large) or BFS (small)
5. **LLM Merging**: Synthesize cluster contents using Blockify API
6. **Iteration**: Re-embed merged results and repeat with increasing threshold

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/autoDistill` | POST | Submit distillation job |
| `/api/jobs/{id}` | GET | Get job status/results |
| `/api/jobs/{id}` | DELETE | Delete a job |
| `/healthz` | GET | Detailed health check |
| `/health` | GET | Simple health (for k8s) |
| `/ready` | GET | Readiness probe |
| `/metrics` | GET | Prometheus metrics |
| `/docs` | GET | OpenAPI documentation |

## License

Blockify EULA - See [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Links

- [Blockify](https://blockify.ai/signup) - Knowledge management platform
- [API Documentation](https://console.blockify.ai) - Blockify API docs
- [Claude Code Skill](./blockify-skill-for-claude-code) - Integration with Claude Code
