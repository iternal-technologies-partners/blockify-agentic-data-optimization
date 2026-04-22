# Blockify + Milvus: Purpose-Built Vector Database Meets Purpose-Built Data Optimization

> **TL;DR:** Milvus is the leading open-source vector database — purpose-built for billion-scale vector search with rich indexing (HNSW, DiskANN, IVF) and hybrid sparse+dense retrieval. Blockify is the complementary layer: it optimizes *what* you put into Milvus. Together, you get a production RAG stack where the database is fast *and* the data is clean.

---

## The Problem: Milvus Scales, But Your Data Doesn't Improve on Its Own

Milvus handles the hardest vector-DB problems: sharding, replication, cost-tiered storage, hybrid search with `SPARSE_INVERTED_INDEX` + `HNSW`. It gives you rich schema, partitions, and output fields.

What it can't do is clean your inputs. If you index 10M raw chunks, Milvus faithfully returns the near-duplicates you asked it to store.

---

## How Blockify Fits

Blockify sits upstream of Milvus — transforming documents into deduplicated IdeaBlocks before any `insert`:

```
Docs  →  Blockify  →  Embeddings  →  Milvus Collection  →  Milvus Hybrid Query  →  App
 (raw)   (Ingest +   (any model)     (dense + sparse       (dense + BM25 sparse    (RAG / agent)
          Distill)                    indexes on IdeaBlock   with RRF)
                                      fields)
```

Because IdeaBlocks carry a `critical_question`, you can build a two-field Milvus collection where dense search matches `trusted_answer` and sparse BM25 matches `critical_question` — a purpose-built hybrid retrieval optimized for Q-A intent.

---

## Quick Start

### 1. Define the collection

```python
from pymilvus import MilvusClient, DataType, Function, FunctionType

client = MilvusClient(uri="http://milvus:19530")

schema = client.create_schema(auto_id=True, enable_dynamic_field=False)
schema.add_field("id", DataType.INT64, is_primary=True)
schema.add_field("name", DataType.VARCHAR, max_length=256)
schema.add_field("critical_question", DataType.VARCHAR, max_length=1024,
                 enable_analyzer=True)  # for BM25
schema.add_field("trusted_answer", DataType.VARCHAR, max_length=8192)
schema.add_field("tags", DataType.ARRAY, element_type=DataType.VARCHAR,
                 max_capacity=64, max_length=128)
schema.add_field("entity_name", DataType.VARCHAR, max_length=256)
schema.add_field("entity_type", DataType.VARCHAR, max_length=64)
schema.add_field("dense", DataType.FLOAT_VECTOR, dim=1024)
schema.add_field("sparse", DataType.SPARSE_FLOAT_VECTOR)

schema.add_function(Function(
    name="bm25_fn",
    function_type=FunctionType.BM25,
    input_field_names=["critical_question"],
    output_field_names=["sparse"],
))

index = client.prepare_index_params()
index.add_index(field_name="dense", index_type="HNSW", metric_type="IP",
                params={"M": 16, "efConstruction": 256})
index.add_index(field_name="sparse", index_type="SPARSE_INVERTED_INDEX",
                metric_type="BM25")

client.create_collection(
    collection_name="blockify_ideablocks",
    schema=schema,
    index_params=index,
)
```

### 2. Ingest IdeaBlocks

```python
import requests
from openai import OpenAI

bk = lambda model, content: requests.post(
    "https://api.blockify.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {BLOCKIFY_KEY}"},
    json={"model": model, "messages": [{"role": "user", "content": content}]},
).json()["ideablocks"]

oai = OpenAI()
raw_docs = load_source_docs()  # your loader

rows = []
for doc in raw_docs:
    for b in bk("distill", str(bk("ingest", doc))):
        emb = oai.embeddings.create(
            model="text-embedding-3-large", input=b["trusted_answer"], dimensions=1024
        ).data[0].embedding
        rows.append({
            "name": b["name"],
            "critical_question": b["critical_question"],
            "trusted_answer": b["trusted_answer"],
            "tags": b["tags"].split(","),
            "entity_name": b["entity"]["entity_name"],
            "entity_type": b["entity"]["entity_type"],
            "dense": emb,
        })

client.insert(collection_name="blockify_ideablocks", data=rows)
```

### 3. Hybrid query

```python
from pymilvus import AnnSearchRequest, RRFRanker

query = "what is our enterprise SLA"
q_emb = oai.embeddings.create(
    model="text-embedding-3-large", input=query, dimensions=1024
).data[0].embedding

reqs = [
    AnnSearchRequest(data=[q_emb], anns_field="dense", param={"ef": 128}, limit=20),
    AnnSearchRequest(data=[query], anns_field="sparse",
                     param={"drop_ratio_search": 0.2}, limit=20),
]
hits = client.hybrid_search(
    collection_name="blockify_ideablocks",
    reqs=reqs,
    ranker=RRFRanker(k=60),
    limit=5,
    output_fields=["name", "critical_question", "trusted_answer"],
)
```

---

## Advanced Patterns

### Pattern 1: Partition by tenant or domain

```python
client.create_partition("blockify_ideablocks", "tenant_acme")
client.insert("blockify_ideablocks", data=rows, partition_name="tenant_acme")
```

### Pattern 2: DiskANN for 100M+ IdeaBlocks

Switch `index_type` to `DISKANN` when the collection exceeds memory budget. Blockify's 40X reduction usually means you never need this — but when you do, the scale-out path is clean.

### Pattern 3: Multi-vector per block

Embed `name`, `critical_question`, and `trusted_answer` separately into three dense fields, then use Milvus multi-vector query with weighted RRF for fine-grained intent matching.

---

## Why Blockify + Milvus

| Milvus alone | Blockify + Milvus |
|---|---|
| Scales to billions, but indexes every duplicate | 40X smaller collection → 40X lower memory / DiskANN footprint |
| BM25 sparse works but matches on boilerplate | Sparse field matches on `critical_question` — purpose-built for Q-A |
| Hybrid search returns duplicate top-K | Duplicates removed upstream |
| Partitioning is structural, not semantic | IdeaBlock tags + entity types enable semantic partitioning |

---

## Related Integrations

- [Blockify + Zilliz](./BLOCKIFY-ZILLIZ.md) — Managed Milvus with the same schema
- [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) — `MilvusVectorStore` fronted by Blockified docs
- [Blockify + LlamaIndex](./BLOCKIFY-LLAMAINDEX.md) — LlamaIndex `MilvusVectorStore`
- [Blockify + n8n](./BLOCKIFY-N8N.md) — No-code orchestration into Milvus

---

*Milvus is a trademark of the LF AI & Data Foundation. Blockify is an independent open-source project and is not affiliated with the Milvus project.*
