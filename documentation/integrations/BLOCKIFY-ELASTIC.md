# Blockify + Elastic: Hybrid BM25 + Dense Retrieval Without the Duplicate Noise

> **TL;DR:** Elasticsearch (and its vector-native successor Elastic's `dense_vector` + ELSER) is the production search tier for many enterprises. But whether you run classic BM25, ELSER sparse retrieval, or hybrid RRF, your results are only as good as your documents. Blockify transforms noisy enterprise content into IdeaBlocks before indexing — eliminating near-duplicate hits that ELSER alone cannot.

---

## The Problem: Elastic Returns Duplicate Hits When Your Corpus Is Redundant

Elastic handles scale (billions of documents) and gives you hybrid search out of the box via Reciprocal Rank Fusion. But:

- **BM25 alone** surfaces the boilerplate heading that appears in every HR doc
- **ELSER** (Elastic Learned Sparse EncodER) expands query terms well but inherits corpus duplication
- **Dense vectors** (`dense_vector` + HNSW) have the same redundancy problem as any vector DB
- **Hybrid (RRF)** averages the ranks — duplicates near the top of both lists stay near the top of the fused list

When the source of truth is 1,000 proposals that share 80% of their content, no retriever wins. You need fewer, better documents.

---

## How Blockify Fits

Blockify runs upstream of Elastic ingest:

```
Source Docs  →  Blockify (Ingest + Distill)  →  Elastic Ingest Pipeline  →  Elastic Index
   (DOCX,        (IdeaBlocks)                   (ELSER inference on         (hybrid BM25 +
    PDF,                                          trusted_answer)             ELSER + dense)
    Confluence)
```

Each IdeaBlock becomes one Elastic document. The mapping preserves the full IdeaBlock structure so you can query against `critical_question`, `tags`, `entity`, or `keywords` alongside the vector / sparse scores.

---

## Quick Start

### 1. Create the index mapping

```json
PUT /blockify-ideablocks
{
  "mappings": {
    "properties": {
      "name":              { "type": "text" },
      "critical_question": { "type": "text" },
      "trusted_answer":    {
        "type": "text",
        "copy_to": "content_expanded"
      },
      "tags":              { "type": "keyword" },
      "entity_name":       { "type": "keyword" },
      "entity_type":       { "type": "keyword" },
      "keywords":          { "type": "text" },
      "source_doc":        { "type": "keyword" },
      "content_expanded": {
        "type": "semantic_text",
        "inference_id": ".elser-2-elasticsearch"
      }
    }
  }
}
```

### 2. Ingest IdeaBlocks

```python
from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch("https://your-cluster.es.cloud:9243", api_key="...")

with open("blockified.jsonl") as f:
    actions = ({
        "_index": "blockify-ideablocks",
        "_id": block["id"],
        "_source": {
            "name":              block["name"],
            "critical_question": block["critical_question"],
            "trusted_answer":    block["trusted_answer"],
            "tags":              block["tags"].split(","),
            "entity_name":       block["entity"]["entity_name"],
            "entity_type":       block["entity"]["entity_type"],
            "keywords":          block["keywords"],
            "source_doc":        block["source"],
        },
    } for block in map(json.loads, f))

helpers.bulk(es, actions)
```

### 3. Hybrid query (RRF)

```json
POST /blockify-ideablocks/_search
{
  "retriever": {
    "rrf": {
      "retrievers": [
        { "standard": { "query": { "multi_match": {
          "query": "what is our enterprise SLA",
          "fields": ["name^2", "critical_question^3", "trusted_answer", "keywords"]
        }}}},
        { "standard": { "query": { "semantic": {
          "field": "content_expanded",
          "query": "what is our enterprise SLA"
        }}}}
      ],
      "rank_window_size": 50,
      "rank_constant": 20
    }
  }
}
```

---

## Advanced Patterns

### Pattern 1: Filter by entity_type before ranking

```json
{
  "retriever": {
    "rrf": {
      "retrievers": [ ... ],
      "filter": { "term": { "entity_type": "PRODUCT" } }
    }
  }
}
```

### Pattern 2: Promote critical_question matches

IdeaBlocks have an explicit question. Boost heavily when the user query matches:

```json
{ "match": { "critical_question": { "query": "...", "boost": 3 } } }
```

### Pattern 3: Kibana dashboards over IdeaBlock tags

See [Blockify + Kibana](./BLOCKIFY-KIBANA.md) for governance dashboards that visualize tag coverage, entity distribution, and retrieval hit-rate trends.

---

## Why Blockify + Elastic

| Elastic alone | Blockify + Elastic |
|---|---|
| BM25 + ELSER still return boilerplate duplicates | Duplicates removed before indexing |
| ELSER inference is run on every chunk, including redundant ones | ELSER runs on 40X fewer documents = 40X lower inference cost |
| Query-side reranking adds latency | Corpus-side deduplication means fewer candidates to rerank |
| No structured Q-A in documents | Every doc has `critical_question` + `trusted_answer` for precise matching |

---

## Related Integrations

- [Blockify + Kibana](./BLOCKIFY-KIBANA.md) — Governance dashboards on the same cluster
- [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) — LangChain's `ElasticsearchStore` backed by Blockified data
- [Blockify + LlamaIndex](./BLOCKIFY-LLAMAINDEX.md) — LlamaIndex `ElasticsearchStore`
- [Blockify + Unstructured.io](./BLOCKIFY-UNSTRUCTURED.md) — Parse → Blockify → Elastic

---

*Elasticsearch, Kibana, and ELSER are trademarks of Elasticsearch N.V. Blockify is an independent open-source project and is not affiliated with Elastic.*
