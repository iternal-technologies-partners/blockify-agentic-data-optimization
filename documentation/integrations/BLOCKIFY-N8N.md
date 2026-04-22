# Blockify + n8n: No-Code Document Optimization for AI Workflows

> **TL;DR:** n8n is the leading open-source workflow-automation platform for AI pipelines, but its default "load → chunk → embed → store" template produces noisy vector indexes. Add a single Blockify HTTP node to transform raw documents into deduplicated IdeaBlocks before embedding — and get 2.29X vector search accuracy with no code.

---

## The Problem: n8n AI Templates Ship With Naive Chunking

n8n's pre-built RAG templates (and the community AI Agent / Vector Store nodes) default to token-based chunking. This works for demos and breaks on real corpora:

- Document Loader nodes dump full files into a generic text splitter
- Embeddings nodes vectorize every chunk, including near-duplicates
- Vector Store nodes (Pinecone, Qdrant, Supabase, Postgres) index the noise
- AI Agent nodes retrieve redundant context and answer quality stalls

n8n's strength — connecting 400+ services without code — becomes a liability when the "AI data prep" step is left as a token-splitter.

---

## How Blockify Fits

Blockify slots in as a single HTTP Request node between document load and embedding:

```
[Trigger]  →  [Load Docs]  →  [HTTP: Blockify Ingest]  →  [HTTP: Blockify Distill]  →  [Embeddings]  →  [Vector Store]  →  [AI Agent]
 (cron,        (Google         (api.blockify.ai/v1,         (deduplicate                (OpenAI,          (Pinecone,        (OpenAI Chat)
  webhook,     Drive,           model: ingest)              similar blocks)              Cohere,           Supabase, ...)
  Slack)       Notion,                                                                   Voyage)
              SharePoint)
```

---

## Quick Start

### 1. Add a credential for Blockify

In n8n: **Credentials → New → HTTP Header Auth**
- Name: `Blockify API`
- Header Name: `Authorization`
- Header Value: `Bearer YOUR_BLOCKIFY_API_KEY`

### 2. Build the workflow

Import this JSON skeleton (replace nodes with your loader + vector store of choice):

```json
{
  "nodes": [
    {
      "name": "Google Drive - New File",
      "type": "n8n-nodes-base.googleDriveTrigger"
    },
    {
      "name": "Extract Text",
      "type": "n8n-nodes-base.extractFromFile"
    },
    {
      "name": "Blockify Ingest",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://api.blockify.ai/v1/chat/completions",
        "authentication": "headerAuth",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"model\": \"ingest\",\n  \"messages\": [{\"role\": \"user\", \"content\": {{ $json.text | toJsonString }}}],\n  \"max_tokens\": 8000\n}"
      }
    },
    {
      "name": "Blockify Distill",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://api.blockify.ai/v1/chat/completions",
        "authentication": "headerAuth",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"model\": \"distill\",\n  \"messages\": [{\"role\": \"user\", \"content\": {{ $json.ideablocks | toJsonString }}}]\n}"
      }
    },
    {
      "name": "Split Out IdeaBlocks",
      "type": "n8n-nodes-base.splitOut",
      "parameters": { "fieldToSplitOut": "ideablocks" }
    },
    {
      "name": "OpenAI Embeddings",
      "type": "@n8n/n8n-nodes-langchain.embeddingsOpenAi"
    },
    {
      "name": "Pinecone Vector Store",
      "type": "@n8n/n8n-nodes-langchain.vectorStorePinecone",
      "parameters": { "operation": "insert" }
    }
  ]
}
```

### 3. Point your AI Agent node at the new vector store

The AI Agent retrieves IdeaBlocks instead of chunks. Tag metadata travels through n8n so you can filter at retrieval time.

---

## Advanced Patterns

### Pattern 1: Scheduled re-distillation

n8n's **Cron** trigger + **Blockify Distill** node = a nightly job that re-deduplicates your index as new docs land. Because distillation is idempotent and merge-based, rerunning it is safe.

### Pattern 2: Per-source routing with Switch nodes

Route SharePoint → sales index, Confluence → engineering index, Notion → product index. Each index is Blockified separately. n8n's **Switch** node makes this declarative.

### Pattern 3: Slack-triggered ingestion

Approve a document by reacting with an emoji in Slack; n8n picks up the event, pulls the doc, Blockifies it, and upserts to the vector store. IdeaBlocks carry the Slack approver's name as a `reviewer` tag.

---

## Why Blockify + n8n

| n8n AI template default | Blockify + n8n |
|---|---|
| Code-node text splitter or LangChain node chunking | No-code Blockify HTTP node produces IdeaBlocks |
| 1 chunk in → 1 embedding out (includes duplicates) | 1 doc in → N deduplicated IdeaBlocks out |
| Re-ingesting a document re-indexes everything | Blockify Distill merges the new ingest with existing blocks |
| No per-block metadata for routing | Tags and entities usable in n8n Switch / Filter nodes |

---

## Related Integrations

- [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) — For the `@n8n/n8n-nodes-langchain` AI Agent / Vector Store nodes
- [Blockify + Supabase](./BLOCKIFY-SUPABASE.md) — Popular n8n vector store target
- [Blockify + Milvus](./BLOCKIFY-MILVUS.md) — Alternative vector store for large corpora
- [Blockify + Unstructured.io](./BLOCKIFY-UNSTRUCTURED.md) — Pair with n8n's Unstructured nodes for PDF / DOCX parsing

---

*n8n is a trademark of n8n GmbH. Blockify is an independent open-source project and is not affiliated with n8n.*
