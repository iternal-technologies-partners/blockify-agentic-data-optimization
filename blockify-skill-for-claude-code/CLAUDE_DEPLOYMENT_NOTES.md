# Deployment Notes for Claude

**Last updated:** 2026-01-26
**Context:** Clean environment test run, 35 case study files

---

## Critical: Do This First

```bash
# 1. Check for existing .env file
cat /Users/admin/Documents/GitHub/blockify-skill-for-claude-code/.env

# 2. If exists, load it BEFORE any script:
export $(cat /Users/admin/Documents/GitHub/blockify-skill-for-claude-code/.env | grep -v '^#' | grep -v '^$' | xargs)

# 3. Always use python3, not python
python3 scripts/setup_check.py --install
```

---

## Gotchas I Discovered

### 1. Python command
- Use `python3` not `python` (macOS has no `python` symlink)

### 2. Environment variables
- Scripts do NOT auto-load .env files
- Must export manually before each session
- The `.env` file is at repo root, NOT in skills/blockify-integration/

### 3. Duplicate ID error (FIXED)
- `ingest_to_chromadb.py` now deduplicates before upsert
- If you see `DuplicateIDError`, the fix is already in place

### 4. Embedding dimension mismatch (FIXED)
- `search_chromadb.py` now uses OpenAI embeddings (1536-d)
- Original used ChromaDB default (384-d) - would fail

### 5. Distillation without Docker
- Use `distill_chromadb.py` (I created this)
- `run_distillation.py` requires Docker service
- Docker was not available on this system

### 6. Distillation is SLOW
- Pass 2 (global clustering) is O(n²) on cluster representatives
- ~2000 blocks took ~13 minutes for Pass 2
- ~10 minutes for API merge calls (248 clusters)

---

## File Locations

```
Repo root:        /Users/admin/Documents/GitHub/blockify-skill-for-claude-code/
.env file:        /Users/admin/Documents/GitHub/blockify-skill-for-claude-code/.env
Scripts:          .../skills/blockify-integration/scripts/
ChromaDB:         .../skills/blockify-integration/data/ideablocks/chroma_db/
Source files:     /Users/admin/Documents/GitHub/files/  (35 .md files)
```

---

## Quick Deploy Sequence

```bash
# Navigate
cd /Users/admin/Documents/GitHub/blockify-skill-for-claude-code/skills/blockify-integration

# Load env (CRITICAL)
export $(cat ../../.env | grep -v '^#' | grep -v '^$' | xargs)

# Install deps
python3 scripts/setup_check.py --install

# Ingest
python3 scripts/ingest_to_chromadb.py /Users/admin/Documents/GitHub/files/ --batch

# Distill (no Docker)
python3 scripts/distill_chromadb.py

# Test search
python3 scripts/search_chromadb.py "test query" --collection distilled
```

---

## Results from Last Run

| Metric | Value |
|--------|-------|
| Files processed | 35 |
| Raw IdeaBlocks | 2,366 |
| Distilled IdeaBlocks | 2,002 |
| Reduction | 15.4% |
| Total time | ~30 minutes |

---

## If Starting Completely Fresh

1. User needs to provide API keys (BLOCKIFY_API_KEY, OPENAI_API_KEY)
2. Create .env file at repo root
3. ChromaDB will be created automatically on first ingest
4. Existing data is at `data/ideablocks/chroma_db/` - delete if want fresh start

---

## Scripts I Created/Modified

| Script | Status | Notes |
|--------|--------|-------|
| `ingest_to_chromadb.py` | Modified | Added deduplication |
| `search_chromadb.py` | Modified | Uses OpenAI embeddings |
| `distill_chromadb.py` | **NEW** | Docker-free distillation |

---

## Don't Forget

- SKILL.md has full documentation with diagrams
- CHANGELOG.md has detailed session log
- ChromaDB data is NOT readable via SQL - use Python API or search script
