# Blockify + Obsidian: Turn Your Vault Into a High-Accuracy RAG Knowledge Base

> **TL;DR:** Obsidian is a second brain for humans. When you plug it into an LLM for RAG (Smart Connections, Copilot, Text Generator, Khoj, BMO), naive chunking of markdown notes produces duplicate hits, fragmented retrieval, and hallucinated answers. Blockify converts your vault into deduplicated IdeaBlocks that dramatically improve vector search accuracy against Obsidian notes.

---

## The Problem: Obsidian RAG at Scale

An Obsidian vault with 5,000+ notes is a pathological case for traditional RAG:

- **Heavy duplication** — Daily notes, templated meeting notes, transcribed voice memos, and Readwise highlights all restate the same ideas in slightly different words
- **Fragmented atomic notes** — The Zettelkasten method (one idea per note) means related context is scattered across backlinks, which naive chunking ignores
- **Version drift** — Notes evolve for years; old decisions, deprecated plans, and stale status updates live side-by-side with current truth
- **Mixed content types** — Literature notes, fleeting notes, project docs, and journal entries all have different reliability, but a vector DB treats them identically

**Result:** An Obsidian-powered chatbot that cheerfully surfaces a 2021 project plan alongside a 2026 status update as if both were current.

---

## How Blockify Fits

Blockify sits between your Obsidian vault and your vector database:

```
Obsidian Vault (.md)  →  Parser  →  Blockify Ingest  →  Blockify Distill  →  Vector DB  →  Obsidian LLM plugin
   (messy)              (markdown    (IdeaBlocks)       (deduplicated)       (ChromaDB,    (Smart Connections,
                         aware)                                               Pinecone,     Copilot, Khoj)
                                                                              Vectorize)
```

Each note becomes one or more IdeaBlocks with:
- A `critical_question` derived from the note's main claim
- A `trusted_answer` that synthesizes the note with its backlinks
- Tags carrying the YAML frontmatter + folder path
- An `entity` pointing back to the source note for citation

---

## Quick Start

### 1. Export your vault as a flat corpus

```bash
# From the root of your Obsidian vault
find . -name "*.md" -not -path "./.obsidian/*" -exec cat {} + > vault-corpus.md
```

### 2. Run the Blockify Claude Code skill against it

```bash
cd blockify-agentic-data-optimization/blockify-skill-for-claude-code/skills/blockify-integration

python3 scripts/run_full_pipeline.py \
  --source /path/to/your/obsidian/vault \
  --output ./blockified-vault \
  --distill
```

### 3. Load IdeaBlocks into your vector DB

If you use **Smart Connections** (Obsidian community plugin), repoint its embedding source at the Blockified JSON-L file. If you use **Khoj**, ingest the distilled corpus as a custom index.

### 4. Query from inside Obsidian

Your LLM plugin now retrieves against curated IdeaBlocks instead of raw chunks. Expected outcomes on a 5k-note vault:

- 40X reduction in the embedding index size
- 2.29X improvement in vector search precision
- Near-elimination of duplicate retrievals from daily notes and templated meeting notes

---

## Advanced Patterns

### Pattern 1: Preserve Obsidian links as entity references

When Blockify ingests your markdown, the `entity_name` field can carry the target of Obsidian wiki-links (`[[Some Note]]`). This keeps the link graph intact in the vector store:

```python
# Pre-processing hook (pseudo-code)
for note in vault_notes:
    frontmatter = parse_yaml(note)
    wiki_links = extract_wiki_links(note)
    note.metadata["linked_entities"] = wiki_links
    note.metadata["folder"] = note.relative_path
```

### Pattern 2: Separate indexes per note type

Run Blockify separately over `literature/`, `projects/`, and `daily/` folders and tag the resulting IdeaBlocks. Then route queries by intent — "what did I decide about X" goes to `projects/`, "what did Kahneman say about X" goes to `literature/`.

### Pattern 3: Ignore archived/deprecated notes

Filter on frontmatter before ingestion:

```bash
# Skip notes with `status: archived` in frontmatter
python3 scripts/blockify_ingest.py --source ./vault --exclude-tag "status: archived"
```

---

## Why Blockify + Obsidian

| Problem with vanilla Obsidian RAG | Blockify solution |
|---|---|
| Duplicate daily-note entries crowd out real answers | Distillation merges near-duplicates into one canonical block |
| Version drift: old decisions mixed with current ones | Governance tags let you filter by date / status |
| Fragmented atomic notes lose backlink context | IdeaBlocks synthesize the note + its immediate backlink context |
| Smart Connections retrieval returns too-similar chunks | 2.29X improvement in average-distance-to-best-match |
| Vault too large for Copilot context | 40X compression makes the full vault fit in affordable embedding budgets |

---

## Related Integrations

- [Blockify + LlamaIndex](./BLOCKIFY-LLAMAINDEX.md) — If you're building a custom Obsidian reader with LlamaIndex
- [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) — For agentic workflows that reason over your vault
- [Blockify + Milvus](./BLOCKIFY-MILVUS.md) — Recommended vector DB for large vaults (50k+ notes)
- [Blockify + Cloudflare](./BLOCKIFY-CLOUDFLARE.md) — Host your personal Obsidian chatbot on Cloudflare Workers + Vectorize

---

*Obsidian is a trademark of Dynalist Inc. Blockify is an independent open-source project and is not affiliated with Obsidian.*
