# Blockify + LlamaIndex: Drop-In Node Parser for High-Accuracy RAG

> **TL;DR:** LlamaIndex gives you document loaders, index types, and query engines — but its default `SentenceSplitter` and `SemanticSplitterNodeParser` still produce duplicate, fragmented nodes on real enterprise corpora. Blockify replaces the chunking stage with a patented ingestion + distillation pipeline that yields 2.29X better vector search accuracy and 40X dataset compression.

---

## The Problem: LlamaIndex Chunking Limits

LlamaIndex's built-in node parsers are good at mechanics but blind to semantics at scale:

- **`SentenceSplitter`** — Fixed token windows that still break mid-argument
- **`SemanticSplitterNodeParser`** — Better boundary detection, but no deduplication
- **`HierarchicalNodeParser`** — Preserves document structure but amplifies duplicate content across levels
- **Custom extractors** — `TitleExtractor`, `QuestionsAnsweredExtractor`, `SummaryExtractor` help retrieval but each adds LLM cost without reducing the underlying redundancy problem

When your corpus contains near-duplicate passages — the norm in enterprise SharePoint, Confluence exports, or scraped documentation — LlamaIndex retrieval returns redundant neighbors that crowd out diverse, relevant context.

---

## How Blockify Fits

Blockify replaces the node-parser stage of the LlamaIndex pipeline:

```
Documents  →  LlamaIndex Reader  →  Blockify (Ingest + Distill)  →  LlamaIndex Nodes  →  VectorStoreIndex
  (raw)       (SimpleDirectory,     (IdeaBlocks via API)            (each block = one    (Pinecone, Milvus,
               PDFReader,           deduplicated                     Node w/ metadata)    Chroma, etc.)
               NotionReader, ...)   canonical blocks)
```

Each IdeaBlock becomes one LlamaIndex `TextNode` — but the node count is 40X smaller and the semantic quality is substantially higher.

---

## Quick Start

### 1. Install

```bash
pip install llama-index blockify-client requests
```

### 2. Wrap Blockify as a LlamaIndex Node Parser

```python
from typing import List, Sequence
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import BaseNode, Document, TextNode
import requests
import os

class BlockifyNodeParser(NodeParser):
    """Convert LlamaIndex Documents into IdeaBlock-backed TextNodes."""

    api_key: str = os.getenv("BLOCKIFY_API_KEY")
    api_url: str = "https://api.blockify.ai/v1/chat/completions"
    model: str = "ingest"
    distill: bool = True

    def _parse_nodes(
        self, nodes: Sequence[BaseNode], show_progress: bool = False, **kwargs
    ) -> List[BaseNode]:
        result = []
        for doc in nodes:
            blocks = self._blockify(doc.get_content())
            if self.distill:
                blocks = self._distill(blocks)
            for b in blocks:
                result.append(
                    TextNode(
                        text=b["trusted_answer"],
                        metadata={
                            "name": b["name"],
                            "critical_question": b["critical_question"],
                            "tags": b["tags"],
                            "entity_name": b["entity"]["entity_name"],
                            "keywords": b["keywords"],
                            "source_doc_id": doc.doc_id,
                        },
                    )
                )
        return result

    def _blockify(self, text: str) -> list:
        r = requests.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "messages": [{"role": "user", "content": text}]},
        )
        return r.json()["ideablocks"]

    def _distill(self, blocks: list) -> list:
        r = requests.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": "distill", "messages": [{"role": "user", "content": str(blocks)}]},
        )
        return r.json()["ideablocks"]
```

### 3. Use it end-to-end

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

docs = SimpleDirectoryReader("./enterprise-docs").load_data()
parser = BlockifyNodeParser()
nodes = parser.get_nodes_from_documents(docs)

index = VectorStoreIndex(nodes)
query_engine = index.as_query_engine()
print(query_engine.query("What is our current pricing for Enterprise Pro?"))
```

The retrieved nodes are now IdeaBlocks with a `critical_question` you can also match against at query time using LlamaIndex's `QueryFusionRetriever`.

---

## Advanced Patterns

### Pattern 1: Hybrid retrieval over critical_question

IdeaBlocks carry an explicit `critical_question`. Add a second retriever that BM25-matches the user query against `critical_question` text, then fuse with vector retrieval:

```python
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever

vector_retriever = index.as_retriever(similarity_top_k=5)
bm25_retriever = BM25Retriever.from_defaults(
    nodes=nodes,
    similarity_top_k=5,
    tokenizer=lambda n: (n.metadata["critical_question"] + " " + n.metadata["keywords"]).split(),
)
fusion = QueryFusionRetriever([vector_retriever, bm25_retriever], num_queries=1)
```

### Pattern 2: Metadata filtering by entity type

Because each IdeaBlock has `entity_type` (PRODUCT, PERSON, CONCEPT, etc.), you can filter at retrieval time:

```python
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters

filters = MetadataFilters(filters=[MetadataFilter(key="entity_type", value="PRODUCT")])
retriever = index.as_retriever(filters=filters)
```

### Pattern 3: Router over multiple Blockified indexes

Run Blockify separately over `sales/`, `engineering/`, `legal/` and route queries via `RouterQueryEngine` — each sub-index is already deduplicated within its domain.

---

## Why Blockify + LlamaIndex

| LlamaIndex alone | Blockify + LlamaIndex |
|---|---|
| `SemanticSplitterNodeParser` boundaries are semantic but content is still duplicated | IdeaBlocks are deduplicated and merged at enterprise scale |
| `QuestionsAnsweredExtractor` adds one question per node via LLM | Each IdeaBlock *is* a Q-A pair, generated once at ingest |
| Retrieval returns near-duplicate nodes | 40X fewer nodes; each is semantically distinct |
| No governance story | Tags, entities, and metadata travel with every node |

---

## Related Integrations

- [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) — Same idea, LangChain `Document` loader adapter
- [Blockify + Milvus](./BLOCKIFY-MILVUS.md) — Recommended LlamaIndex `VectorStore` backend
- [Blockify + Unstructured.io](./BLOCKIFY-UNSTRUCTURED.md) — Parse before you Blockify
- [Blockify + Obsidian](./BLOCKIFY-OBSIDIAN.md) — If your LlamaIndex source is a personal vault

---

*LlamaIndex is an open-source project maintained by LlamaIndex, Inc. Blockify is an independent project and is not affiliated with LlamaIndex.*
