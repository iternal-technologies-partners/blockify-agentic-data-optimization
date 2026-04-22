# Blockify Integrations

Blockify is designed to plug into existing RAG, vector search, and data-management stacks. It sits between your document source and your retrieval / storage layer, replacing naive chunking with deduplicated IdeaBlocks.

Each integration below includes a problem statement, architecture diagram, quick-start code, advanced patterns, and a side-by-side comparison showing what Blockify adds on top of the platform's default behavior.

## RAG Frameworks

| Integration | Use Case |
|---|---|
| [Blockify + LlamaIndex](./BLOCKIFY-LLAMAINDEX.md) | Drop-in `NodeParser` producing deduplicated `TextNode`s |
| [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) | `BaseDocumentTransformer` adapter for any LangChain RAG chain or LangGraph agent |

## Knowledge & Workflow

| Integration | Use Case |
|---|---|
| [Blockify + Obsidian](./BLOCKIFY-OBSIDIAN.md) | Turn an Obsidian vault into a high-accuracy RAG knowledge base |
| [Blockify + n8n](./BLOCKIFY-N8N.md) | No-code Blockify HTTP node for AI workflow automation |

## Vector & Search Databases

| Integration | Use Case |
|---|---|
| [Blockify + Milvus](./BLOCKIFY-MILVUS.md) | Self-hosted billion-scale vector DB with hybrid dense + BM25 retrieval |
| [Blockify + Zilliz Cloud](./BLOCKIFY-ZILLIZ.md) | Managed Milvus with autoscaling and serverless pricing |
| [Blockify + Elastic](./BLOCKIFY-ELASTIC.md) | Hybrid BM25 + ELSER + dense retrieval on cleaned IdeaBlocks |
| [Blockify + Supabase](./BLOCKIFY-SUPABASE.md) | Postgres + pgvector with row-level security on IdeaBlock tags |
| [Blockify + Cloudflare](./BLOCKIFY-CLOUDFLARE.md) | Edge-native RAG on Workers + Vectorize + R2 |

## Data Platform & Observability

| Integration | Use Case |
|---|---|
| [Blockify + Starburst](./BLOCKIFY-STARBURST.md) | Federated IdeaBlock generation across data-lake catalogs |
| [Blockify + Kibana](./BLOCKIFY-KIBANA.md) | Governance dashboards for knowledge-base coverage, drift, and retrieval |

## Document Parsing

| Integration | Use Case |
|---|---|
| [Blockify + Unstructured.io](./BLOCKIFY-UNSTRUCTURED.md) | Parse PDF, DOCX, PPTX, HTML, email, images — then Blockify |

---

## Integration Pattern Reference

Regardless of stack, Blockify always occupies the same position in the pipeline:

```
Source Documents  →  Parser  →  Blockify (Ingest + Distill)  →  Embeddings  →  Retrieval / Storage  →  LLM / Agent
```

- **Parser** — Unstructured.io, native connectors, or raw file readers
- **Blockify Ingest** — Transform raw text into draft IdeaBlocks (structured XML Q-A units)
- **Blockify Distill** — Merge near-duplicates, produce canonical IdeaBlock set (~40X reduction)
- **Embeddings** — Any provider; Blockify is embedding-model agnostic
- **Retrieval / Storage** — Any vector DB, hybrid search engine, or keyword store
- **LLM / Agent** — Any chat completion model or agent framework

---

## Don't See Your Stack?

Blockify exposes an OpenAI-compatible `/v1/chat/completions` endpoint with `model: "ingest"` and `model: "distill"`. If your platform can make an HTTP POST, it can use Blockify. Open an issue with your integration request, or submit a PR adding a new page to this directory.

See [BLOCKIFY-API-REFERENCE.md](../BLOCKIFY-API-REFERENCE.md) for full API details.
