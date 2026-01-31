# Blockify Skill for Claude Code

A Claude Code Skill to improve accuracy of RAG and Agentic Search using Blockify's IdeaBlock technology. Can improve accuracy by up to 78X (7,800%) and significantly reduce information size via intelligent distillation.

## What is Blockify?

Blockify transforms raw text into **IdeaBlocks**—self-contained semantic knowledge units optimized for AI retrieval. Unlike traditional chunking that splits text by character count, IdeaBlocks preserve semantic coherence.

| Metric | Improvement |
|--------|-------------|
| Enterprise Performance | 78X |
| Vector Search Accuracy | 2.29X |
| Dataset Size Reduction | 40X (to ~2.5%) |
| Token Efficiency | 3.09X |

## Quick Start

### Step 1: Set Up API Keys

Create a `.env` file in the project root:

```bash
cd /path/to/blockify-skill-for-claude-code

cat > .env << 'EOF'
# Get your key from: https://app.blockify.ai/settings/api
BLOCKIFY_API_KEY=blk_your_key_here

# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your_key_here

# Optional: parallel workers for ingestion (default: 5)
BLOCKIFY_PARALLEL_WORKERS=10
EOF
```

**Load environment variables** (required before running any script):

```bash
# Option A: Load for current session
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)

# Option B: Add to ~/.zshrc or ~/.bashrc for persistence
echo 'export $(cat /path/to/blockify-skill-for-claude-code/.env | grep -v "^#" | grep -v "^$" | xargs)' >> ~/.zshrc
```

### Step 2: Install Dependencies

```bash
cd skills/blockify-integration
python3 scripts/setup_check.py --install
```

### Step 3: Process Documents

```bash
# Ingest documents (10 parallel workers)
python3 scripts/ingest_to_chromadb.py /path/to/docs/ --batch --parallel 10

# Deduplicate with distillation (NO Docker required)
python3 scripts/distill_chromadb.py

# Search your knowledge base
python3 scripts/search_chromadb.py "your query" --collection distilled
```

### Step 4: Generate Benchmark Report

```bash
python3 scripts/run_benchmark.py --company "Your Company"
open data/reports/benchmark_report_*.html
```

### Optional: Register as Claude Code Skill

Add to `~/.claude/settings.json`:

```json
{
  "skills": [
    {
      "path": "/absolute/path/to/blockify-skill-for-claude-code/skills/blockify-integration"
    }
  ]
}
```

> **Note:** The skill path must be absolute. After registering, Claude Code can invoke the skill automatically when you mention Blockify, IdeaBlocks, or knowledge distillation.

## Components

### Skill

The main skill is in `skills/blockify-integration/`:
- `SKILL.md` - Skill instructions for Claude Code
- `scripts/` - Python scripts for ingestion and search
- `references/` - API and algorithm documentation

### Distillation

Distillation deduplicates and merges similar IdeaBlocks across documents.

**Option A: Direct API (Recommended - No Docker)**
```bash
python3 scripts/distill_chromadb.py
```

**Option B: Docker Service (for 10k+ blocks)**
```bash
git clone https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization/blockify-distillation-service.git
cd blockify-distillation-service
docker-compose up -d
python3 scripts/run_distillation.py
```

See [Distillation Service](https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization/blockify-distillation-service) for full documentation.

### Documentation

The `/documentation/` directory contains detailed documentation:
- `ARCHITECTURE-END-TO-END.md` - System architecture
- `BLOCKIFY-API-REFERENCE.md` - API documentation
- `LOCAL-VECTOR-DATABASE-SETUP.md` - ChromaDB setup
- `DISTILLATION-SERVICE.md` - Distillation algorithms

## License

Blockify EULA - See [LICENSE](LICENSE) for details.

## Links

- [Blockify Platform](https://blockify.ai/signup)
- [API Documentation](https://console.blockify.ai)
- [Distillation Service](./blockify-distillation-service)
