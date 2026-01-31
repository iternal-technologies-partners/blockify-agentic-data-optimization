# End-to-End Architecture: Blockify + Claude Code + Clawdbot Integration

**Document Purpose:** Complete technical architecture for engineers integrating Blockify data optimization with Claude Code and Clawdbot for enterprise RAG systems.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Flow](#data-flow)
3. [Component Deep Dive](#component-deep-dive)
4. [Claude Code Integration](#claude-code-integration)
5. [Clawdbot Integration](#clawdbot-integration)
6. [Vector Database Setup](#vector-database-setup)
7. [Knowledge Graph (Optional)](#knowledge-graph-optional)
8. [Deployment Architecture](#deployment-architecture)
9. [Security Considerations](#security-considerations)

---

## Architecture Overview

```
+===========================================================================+
||                    ENTERPRISE RAG ARCHITECTURE                          ||
||                  Blockify + Claude Code + Clawdbot                      ||
+===========================================================================+

                           [CONTENT SOURCES]
                                  |
     +----------------------------+----------------------------+
     |              |             |             |              |
     v              v             v             v              v
[SharePoint]  [Confluence]  [Google Drive]  [Git Repos]  [Local Docs]
     |              |             |             |              |
     +----------------------------+----------------------------+
                                  |
                                  v
+===========================================================================+
||                        DOCUMENT PARSING LAYER                           ||
+===========================================================================+
||  [Unstructured.io]  [AWS Textract]  [Google Gemini]  [Custom Parser]   ||
||                                  |                                      ||
||                                  v                                      ||
||                      [Raw Text Extraction]                              ||
||                      [Format Normalization]                             ||
||                      [Metadata Preservation]                            ||
+===========================================================================+
                                  |
                                  v
+===========================================================================+
||                        BLOCKIFY PROCESSING                              ||
+===========================================================================+
||                                                                         ||
||  +-------------------+    +-------------------+    +------------------+ ||
||  |   CHUNKING        |    |   BLOCKIFY        |    |   BLOCKIFY       | ||
||  |   ENGINE          |--->|   INGEST API      |--->|   DISTILL API    | ||
||  +-------------------+    +-------------------+    +------------------+ ||
||  | 2,000 char chunks |    | Raw --> IdeaBlocks|    | Deduplicate      | ||
||  | Sentence boundaries|    | ~99% lossless     |    | Merge similar    | ||
||  | 10% overlap        |    | Metadata + Entities|   | ~95% lossless    | ||
||  +-------------------+    +-------------------+    +------------------+ ||
||                                                                         ||
||                                  |                                      ||
||                                  v                                      ||
||                      [Optimized IdeaBlocks]                             ||
||                      [40X Size Reduction]                               ||
||                      [78X Accuracy Improvement]                         ||
+===========================================================================+
                                  |
                                  v
+===========================================================================+
||                     STORAGE & RETRIEVAL LAYER                           ||
+===========================================================================+
||                                                                         ||
||  +-------------------+              +-------------------+               ||
||  |   VECTOR DB       |              |   KNOWLEDGE       |               ||
||  |   (Primary)       |              |   GRAPH           |               ||
||  +-------------------+              +-------------------+               ||
||  | Pinecone          |              | Neo4j / Memgraph  |               ||
||  | Azure AI Search   |              | Entity relations  |               ||
||  | Milvus / Weaviate |              | Multi-hop queries |               ||
||  | Cloudflare Vectorize|            | Reasoning paths   |               ||
||  +-------------------+              +-------------------+               ||
||           |                                  |                          ||
||           +----------------------------------+                          ||
||                           |                                             ||
||                           v                                             ||
||              [Hybrid Search: Vector + KG + BM25]                        ||
||              [Reciprocal Rank Fusion]                                   ||
||              [Cross-Encoder Reranking]                                  ||
+===========================================================================+
                                  |
                                  v
+===========================================================================+
||                        APPLICATION LAYER                                ||
+===========================================================================+
||                                                                         ||
||  +-------------------+    +-------------------+    +------------------+ ||
||  |   CLAWDBOT        |    |   CLAUDE CODE     |    |   ENTERPRISE     | ||
||  |   (Website Chat)  |    |   (Dev Assistant) |    |   APPS           | ||
||  +-------------------+    +-------------------+    +------------------+ ||
||  | Customer queries  |    | Codebase context  |    | Internal tools   | ||
||  | Product info      |    | Doc search        |    | Agent systems    | ||
||  | Support           |    | Knowledge assist  |    | Custom chatbots  | ||
||  +-------------------+    +-------------------+    +------------------+ ||
||                                                                         ||
+===========================================================================+
                                  |
                                  v
                             [END USERS]
```

---

## Data Flow

### Phase 1: Content Ingestion

```
+-----------------------------------------------------------------------+
|                      INGESTION PIPELINE                               |
+-----------------------------------------------------------------------+

[Content Discovery]
      |
      v
[Document Fetch] --> Crawl SharePoint, Confluence, Google Drive, Git
      |
      v
[Format Detection] --> PDF, DOCX, PPTX, HTML, Markdown, JSON, Images
      |
      v
[Parse to Text]
      |
      +---> [Unstructured.io] --> Best for PDFs, complex layouts
      |
      +---> [AWS Textract] --> Best for scanned documents, OCR
      |
      +---> [Google Gemini] --> Best for images, visual content
      |
      v
[Metadata Extraction] --> Title, author, date, source URL, version
      |
      v
[Quality Filtering] --> Remove duplicates, boilerplate, empty docs
      |
      v
[Output: Clean Text + Metadata]
```

### Phase 2: Blockify Processing

```
+-----------------------------------------------------------------------+
|                      BLOCKIFY PIPELINE                                |
+-----------------------------------------------------------------------+

[Clean Text + Metadata]
      |
      v
[Semantic Chunking]
      |
      +---> Chunk at paragraph/sentence boundaries
      +---> Target: 2,000 characters per chunk
      +---> Overlap: 10% on boundaries
      |
      v
[Batch Preparation]
      |
      +---> Group chunks by source document
      +---> Prepare API payloads
      +---> Implement rate limiting
      |
      v
[Blockify Ingest API]
      |
      +---> POST each chunk
      +---> Receive IdeaBlocks XML
      +---> Parse and store
      |
      v
[Semantic Clustering]
      |
      +---> Embed all IdeaBlocks
      +---> Cluster by similarity (cosine > 0.85)
      +---> Group 2-15 similar blocks
      |
      v
[Blockify Distill API]
      |
      +---> POST each cluster
      +---> Receive merged IdeaBlocks
      +---> Replace cluster with consolidated block
      |
      v
[Output: Optimized IdeaBlocks]
      |
      +---> 40X fewer blocks than original chunks
      +---> Each block is semantically complete
      +---> Rich metadata for governance
```

### Phase 3: Storage & Indexing

```
+-----------------------------------------------------------------------+
|                      STORAGE PIPELINE                                 |
+-----------------------------------------------------------------------+

[Optimized IdeaBlocks]
      |
      v
[Embedding Generation]
      |
      +---> Embed: name + critical_question + trusted_answer
      +---> Model: text-embedding-3-large (3072 dims)
      +---> Cache embeddings for efficiency
      |
      v
[Vector Database Insert]
      |
      +---> ID: unique ideablock ID
      +---> Vector: embedding
      +---> Metadata: all fields
      |
      v
[BM25 Index Update]
      |
      +---> Index: name, critical_question, trusted_answer, keywords
      +---> Full-text search capability
      |
      v
[Knowledge Graph Update] (Optional)
      |
      +---> Create entity nodes
      +---> Create relationship edges
      +---> Enable multi-hop queries
      |
      v
[Index Ready for Queries]
```

### Phase 4: Retrieval

```
+-----------------------------------------------------------------------+
|                      RETRIEVAL PIPELINE                               |
+-----------------------------------------------------------------------+

[User Query]
      |
      v
[Query Processing]
      |
      +---> Query expansion (synonyms)
      +---> Entity extraction
      +---> Intent classification
      |
      v
[Hybrid Search]
      |
      +---> [Dense Vector Search] --> Semantic similarity
      |     Query embedding vs IdeaBlock embeddings
      |     Top K = 20
      |
      +---> [BM25 Sparse Search] --> Keyword matching
      |     Full-text search on text fields
      |     Top K = 20
      |
      +---> [Knowledge Graph] --> Structured lookup
            Entity-based traversal
            Related concepts
      |
      v
[Reciprocal Rank Fusion]
      |
      +---> Combine results from all sources
      +---> Score: SUM(1 / (60 + rank))
      +---> Top K = 30
      |
      v
[Cross-Encoder Reranking]
      |
      +---> Score each (query, ideablock) pair
      +---> Model: cross-encoder/ms-marco-MiniLM-L-12-v2
      +---> Top K = 10
      |
      v
[Context Assembly]
      |
      +---> Order by relevance
      +---> Include metadata for citations
      +---> Format for LLM consumption
      |
      v
[Output: Relevant IdeaBlocks]
```

---

## Component Deep Dive

### Document Parser Selection

| Parser | Best For | Strengths | Weaknesses |
|--------|----------|-----------|------------|
| **Unstructured.io** | Complex PDFs, layouts | Preserves structure | Can be slow |
| **AWS Textract** | Scanned docs, forms | Great OCR | Cost at scale |
| **Google Gemini** | Images, visual content | Multimodal | Newer, less tested |
| **Markdownify** | HTML pages | Fast, simple | Loses complex layouts |
| **PyPDF** | Simple PDFs | Fast, free | Poor on complex layouts |

### Embedding Model Selection

| Model | Dimensions | Best For | Cost |
|-------|------------|----------|------|
| **text-embedding-3-large** | 3072 | General enterprise | Medium |
| **text-embedding-3-small** | 1536 | Cost-sensitive | Low |
| **Jina-V2** | 768 | AirgapAI compatible | Medium |
| **CodeBERT** | 768 | Code repositories | Low |
| **E5-multilingual-large** | 1024 | Multi-language | Medium |

### Vector Database Selection

| Database | Best For | Hosting | Hybrid Search |
|----------|----------|---------|---------------|
| **Pinecone** | Production scale | Managed cloud | Yes |
| **Azure AI Search** | Azure ecosystem | Managed cloud | Yes |
| **Cloudflare Vectorize** | Cloudflare Workers | Serverless | No (use KV) |
| **Milvus** | Self-hosted scale | Self-hosted | Yes |
| **Weaviate** | GraphQL API | Both | Yes |
| **Chroma** | Local development | Local/cloud | No |

---

## Claude Code Integration

### MCP Server for Semantic Search

```
+-----------------------------------------------------------------------+
|                      CLAUDE CODE + BLOCKIFY                           |
+-----------------------------------------------------------------------+

                        [Developer Query]
                              |
                              v
                   [Claude Code Agent]
                              |
            +----------------+----------------+
            |                |                |
            v                v                v
    [Agentic Search]  [MCP Server]    [Local ripgrep]
    (Multi-step)      (Semantic)      (Exact match)
            |                |                |
            |                v                |
            |     [Blockify Vector DB]        |
            |     [IdeaBlock Retrieval]       |
            |                |                |
            +----------------+----------------+
                              |
                              v
                    [Result Fusion]
                              |
                              v
                    [Context Assembly]
                              |
                              v
                    [Code Generation]
```

### Recommended MCP Server Structure

```
/mcp-servers/blockify-search/
├── server.py              # MCP server implementation
├── config.json            # Connection settings
├── requirements.txt       # Dependencies
└── README.md              # Setup instructions
```

### MCP Server Implementation

```python
# server.py - Blockify Semantic Search MCP Server

from mcp import MCPServer, Tool
from blockify_client import BlockifyClient

class BlockifySearchServer(MCPServer):
    def __init__(self, config):
        super().__init__()
        self.vector_db = VectorDBClient(config['vector_db_url'])
        self.register_tools()

    def register_tools(self):
        self.register_tool(Tool(
            name="semantic_search",
            description="Search documentation using semantic similarity",
            parameters={
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "default": 5}
            },
            handler=self.semantic_search
        ))

        self.register_tool(Tool(
            name="find_related",
            description="Find IdeaBlocks related to a concept",
            parameters={
                "concept": {"type": "string"},
                "limit": {"type": "integer", "default": 5}
            },
            handler=self.find_related
        ))

    async def semantic_search(self, query: str, limit: int = 5):
        """Search IdeaBlocks by semantic similarity."""
        results = await self.vector_db.search(query, limit)
        return self.format_results(results)

    async def find_related(self, concept: str, limit: int = 5):
        """Find related IdeaBlocks via knowledge graph."""
        results = await self.knowledge_graph.traverse(concept, limit)
        return self.format_results(results)

    def format_results(self, results):
        """Format IdeaBlocks for Claude Code consumption."""
        formatted = []
        for r in results:
            formatted.append({
                'name': r['name'],
                'question': r['critical_question'],
                'answer': r['trusted_answer'],
                'source': r.get('source_document', 'Unknown'),
                'relevance': r.get('score', 0)
            })
        return formatted
```

### Claude Code Skill for Blockify

See [CLAUDE-CODE-BLOCKIFY-SKILL.md](./CLAUDE-CODE-BLOCKIFY-SKILL.md) for the complete skill implementation.

---

## Clawdbot Integration

### Architecture

```
+-----------------------------------------------------------------------+
|                      CLAWDBOT RAG INTEGRATION                         |
+-----------------------------------------------------------------------+

[Website Visitor]
      |
      v
[Chat Interface]
      |
      v
[Session Manager] --> Track conversation, rate limiting
      |
      v
[Query Router]
      |
      +---> [FAQ] --> Direct lookup
      |
      +---> [Product Info] --> Product knowledge base
      |
      +---> [Technical] --> Documentation search
      |
      +---> [Pricing] --> Pricing database
      |
      +---> [Complex] --> Multi-source agentic
      |
      v
[Retrieval Layer]
      |
      +---> [Blockify IdeaBlocks Vector DB]
      |
      +---> [FAQ Structured Database]
      |
      +---> [Case Studies Vector DB]
      |
      v
[Context Assembly]
      |
      +---> System prompt with company context
      +---> Retrieved IdeaBlocks (top 5)
      +---> Conversation history (last 5 turns)
      +---> Current user message
      |
      v
[LLM Generation] --> Grok / Claude / GPT-4
      |
      v
[Response Validation]
      |
      +---> Hallucination check
      +---> Citation verification
      +---> Content policy check
      |
      v
[Response to User]
```

### Implementation Code

```typescript
// src/services/clawdbot-rag.ts

interface IdeaBlock {
  name: string;
  critical_question: string;
  trusted_answer: string;
  tags: string[];
  keywords: string[];
  source_document?: string;
}

interface RAGContext {
  ideablocks: IdeaBlock[];
  faqs?: FAQ[];
  case_studies?: CaseStudy[];
}

export async function retrieveContext(
  query: string,
  env: Env
): Promise<RAGContext> {
  // 1. Embed the query
  const queryEmbedding = await embedQuery(query, env);

  // 2. Search vector database
  const vectorResults = await env.VECTORIZE.query(queryEmbedding, {
    topK: 10,
    returnMetadata: true
  });

  // 3. BM25 search (via KV or D1)
  const bm25Results = await searchBM25(query, env);

  // 4. Combine with RRF
  const fusedResults = reciprocalRankFusion([
    vectorResults.map(r => r.id),
    bm25Results.map(r => r.id)
  ]);

  // 5. Fetch full IdeaBlocks
  const ideablocks = await Promise.all(
    fusedResults.slice(0, 5).map(id =>
      env.KV_IDEABLOCKS.get(id, 'json')
    )
  );

  return {
    ideablocks: ideablocks.filter(Boolean) as IdeaBlock[]
  };
}

export function buildPrompt(
  context: RAGContext,
  conversationHistory: Message[],
  currentQuery: string
): string {
  const systemPrompt = `You are an AI assistant for Iternal Technologies.
You help users learn about our products: AirgapAI, Blockify, IdeaBlocks, Waypoint, and Autoreports.

Use the following knowledge base to answer questions:

${context.ideablocks.map(ib => `
[${ib.name}]
Q: ${ib.critical_question}
A: ${ib.trusted_answer}
`).join('\n')}

Guidelines:
- Answer based ONLY on the knowledge base above
- If you don't know, say "I don't have that information"
- Be concise and helpful
- Cite the source when possible`;

  const messages = [
    { role: 'system', content: systemPrompt },
    ...conversationHistory.slice(-10),
    { role: 'user', content: currentQuery }
  ];

  return messages;
}
```

---

## Vector Database Setup

### Pinecone Setup

```python
import pinecone

# Initialize
pinecone.init(api_key="YOUR_API_KEY", environment="us-west1-gcp")

# Create index
pinecone.create_index(
    name="blockify-ideablocks",
    dimension=3072,  # text-embedding-3-large
    metric="cosine",
    metadata_config={
        "indexed": ["tags", "source_document", "created_at"]
    }
)

# Connect to index
index = pinecone.Index("blockify-ideablocks")

# Upsert IdeaBlocks
def upsert_ideablock(ideablock, embedding):
    index.upsert(vectors=[{
        "id": ideablock['id'],
        "values": embedding,
        "metadata": {
            "name": ideablock['name'],
            "critical_question": ideablock['critical_question'],
            "trusted_answer": ideablock['trusted_answer'],
            "tags": ideablock['tags'],
            "keywords": ideablock['keywords'],
            "source_document": ideablock.get('source_document', ''),
            "created_at": ideablock.get('created_at', '')
        }
    }])
```

### Cloudflare Vectorize Setup

```typescript
// wrangler.toml
[[vectorize]]
binding = "VECTORIZE"
index_name = "blockify-ideablocks"

// Create index via CLI
// wrangler vectorize create blockify-ideablocks --dimensions=3072 --metric=cosine

// Usage in Worker
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Query
    const results = await env.VECTORIZE.query(queryVector, {
      topK: 10,
      returnMetadata: true
    });

    // Insert
    await env.VECTORIZE.upsert([{
      id: ideablock.id,
      values: embedding,
      metadata: {
        name: ideablock.name,
        question: ideablock.critical_question,
        answer: ideablock.trusted_answer
      }
    }]);

    return Response.json(results);
  }
};
```

---

## Knowledge Graph (Optional)

### Neo4j Schema

```cypher
// Create constraints
CREATE CONSTRAINT ideablock_id IF NOT EXISTS
FOR (i:IdeaBlock) REQUIRE i.id IS UNIQUE;

CREATE CONSTRAINT entity_name IF NOT EXISTS
FOR (e:Entity) REQUIRE e.name IS UNIQUE;

// Create IdeaBlock node
CREATE (ib:IdeaBlock {
  id: $id,
  name: $name,
  critical_question: $critical_question,
  trusted_answer: $trusted_answer,
  tags: $tags,
  keywords: $keywords
})

// Create Entity nodes and relationships
MERGE (e:Entity {name: $entity_name, type: $entity_type})
MERGE (ib)-[:MENTIONS]->(e)

// Query: Find related IdeaBlocks
MATCH (ib1:IdeaBlock)-[:MENTIONS]->(e:Entity)<-[:MENTIONS]-(ib2:IdeaBlock)
WHERE ib1.id = $ideablock_id AND ib1 <> ib2
RETURN ib2, count(e) as shared_entities
ORDER BY shared_entities DESC
LIMIT 10
```

---

## Deployment Architecture

### Cloud Deployment (Recommended for Start)

```
+-----------------------------------------------------------------------+
|                      CLOUD DEPLOYMENT                                 |
+-----------------------------------------------------------------------+

[Cloudflare Workers] <-- Application Layer
      |
      +---> [Blockify Cloud API] <-- api.blockify.ai
      |
      +---> [Pinecone] <-- Vector Database
      |
      +---> [Cloudflare D1] <-- Structured Data
      |
      +---> [Cloudflare KV] <-- IdeaBlock Storage
      |
      +---> [Cloudflare R2] <-- Document Storage

Benefits:
- Fast deployment (hours)
- Minimal infrastructure management
- Pay-per-use pricing
- Global edge distribution
```

### Hybrid Deployment (Enterprise)

```
+-----------------------------------------------------------------------+
|                      HYBRID DEPLOYMENT                                |
+-----------------------------------------------------------------------+

[On-Premise]                              [Cloud]
      |                                        |
      v                                        v
[Document Sources]                    [Blockify Cloud API]
      |                                        |
      v                                        |
[Document Parser]                              |
      |                                        |
      +----------------------------------------+
                       |
                       v
            [Processing Orchestrator]
                       |
           +-----------+-----------+
           |           |           |
           v           v           v
    [On-Prem      [Cloud      [On-Prem
     Vector DB]    Backup]     KG]

Benefits:
- Data stays on-premise
- Cloud for processing power
- Flexibility in architecture
```

---

## Security Considerations

### API Key Management

```python
# NEVER hardcode API keys
# Use environment variables

import os

BLOCKIFY_API_KEY = os.environ.get('BLOCKIFY_API_KEY')
if not BLOCKIFY_API_KEY:
    raise ValueError("BLOCKIFY_API_KEY not set")
```

### Data Classification

| Classification | Storage | Access |
|----------------|---------|--------|
| PUBLIC | Cloud vector DB | All users |
| INTERNAL | Encrypted cloud | Authenticated users |
| CONFIDENTIAL | On-premise only | Role-based |
| SECRET | Air-gapped | Named individuals |

### Audit Trail

```python
def log_query(user_id, query, results, timestamp):
    """Log all RAG queries for compliance."""
    audit_log.insert({
        "user_id": user_id,
        "query": query,
        "result_count": len(results),
        "ideablock_ids": [r['id'] for r in results],
        "timestamp": timestamp
    })
```

---

*Document created: 2026-01-25*
*Architecture version: 1.0*
