# Blockify + LangChain: A Higher-Quality Document Transformer for RAG Chains

> **TL;DR:** LangChain ships a dozen `TextSplitter` implementations, but none of them deduplicate, none of them preserve Q-A structure, and none of them scale to enterprise corpora without retrieval noise. Blockify is a drop-in `BaseDocumentTransformer` that produces deduplicated IdeaBlock documents — turning any LangChain RAG chain into a production-grade system.

---

## The Problem: LangChain Splitters Are Mechanical, Not Semantic

LangChain's default document transformers are generic:

- **`RecursiveCharacterTextSplitter`** — Token-count based, breaks context mid-paragraph
- **`MarkdownHeaderTextSplitter`** — Header-aware but doesn't merge duplicate sections across files
- **`SemanticChunker`** (experimental, from `langchain-experimental`) — Uses embeddings to find boundaries, but still leaves duplicates intact
- **`ParentDocumentRetriever`** — Helps context but doubles your storage footprint

When you scale to real corpora (10k+ documents), retrieval returns the same boilerplate across multiple sources, the LLM sees redundant context, token costs explode, and answer quality plateaus.

---

## How Blockify Fits

Blockify is a `BaseDocumentTransformer`. It replaces — or runs after — your splitter:

```
Documents  →  Loader  →  Blockify DocumentTransformer  →  VectorStore  →  Retriever  →  Chain / Agent
   (raw)      (PyPDF,    (IdeaBlocks as                   (FAISS,         (any)         (RetrievalQA,
               Notion,    LangChain Documents)            Chroma,                        ConversationalRetrievalChain,
               Confluence,                                Pinecone, ...)                LangGraph agents)
               ...)
```

Each IdeaBlock is a `langchain_core.documents.Document` whose `page_content` is the `trusted_answer` and whose `metadata` carries the full IdeaBlock schema.

---

## Quick Start

### 1. Install

```bash
pip install langchain langchain-core langchain-openai requests
```

### 2. Implement the transformer

```python
from typing import Sequence
from langchain_core.documents import Document
from langchain_core.documents.transformers import BaseDocumentTransformer
import requests
import os

class BlockifyTransformer(BaseDocumentTransformer):
    def __init__(self, api_key: str | None = None, distill: bool = True):
        self.api_key = api_key or os.environ["BLOCKIFY_API_KEY"]
        self.distill = distill
        self.url = "https://api.blockify.ai/v1/chat/completions"

    def transform_documents(
        self, documents: Sequence[Document], **kwargs
    ) -> Sequence[Document]:
        out: list[Document] = []
        for d in documents:
            blocks = self._call("ingest", d.page_content)
            if self.distill:
                blocks = self._call("distill", str(blocks))
            for b in blocks:
                out.append(
                    Document(
                        page_content=b["trusted_answer"],
                        metadata={
                            **d.metadata,
                            "ideablock_name": b["name"],
                            "critical_question": b["critical_question"],
                            "tags": b["tags"],
                            "entity_name": b["entity"]["entity_name"],
                            "entity_type": b["entity"]["entity_type"],
                            "keywords": b["keywords"],
                        },
                    )
                )
        return out

    def _call(self, model: str, content: str) -> list:
        r = requests.post(
            self.url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": model, "messages": [{"role": "user", "content": content}]},
        )
        return r.json()["ideablocks"]
```

### 3. Use it in any RAG chain

```python
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

docs = DirectoryLoader("./enterprise-docs", glob="**/*.md").load()
blocks = BlockifyTransformer().transform_documents(docs)

store = Chroma.from_documents(blocks, OpenAIEmbeddings(), persist_directory="./chroma")
retriever = store.as_retriever(search_kwargs={"k": 5})

qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(model="gpt-4o"), retriever=retriever)
print(qa.invoke({"query": "What is our SLA for Enterprise customers?"}))
```

---

## Advanced Patterns

### Pattern 1: LCEL pipeline

```python
from langchain_core.runnables import RunnableLambda

pipeline = (
    DirectoryLoader("./docs").lazy_load
    | RunnableLambda(lambda docs: BlockifyTransformer().transform_documents(list(docs)))
    | RunnableLambda(lambda d: Chroma.from_documents(d, OpenAIEmbeddings()))
)
```

### Pattern 2: LangGraph agent with per-tool Blockified indexes

Build a LangGraph agent where each tool queries a domain-specific Blockified index (sales, engineering, legal). Routing becomes dramatically cheaper because each sub-index is already deduplicated and small.

### Pattern 3: Self-query retriever over IdeaBlock metadata

LangChain's `SelfQueryRetriever` shines when metadata is rich. Since IdeaBlocks carry `tags`, `entity_type`, and `keywords`, the self-query LLM can compose precise metadata filters:

```python
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

field_info = [
    AttributeInfo(name="entity_type", description="Primary entity classification", type="string"),
    AttributeInfo(name="tags", description="Topical tags", type="string"),
]
self_q = SelfQueryRetriever.from_llm(ChatOpenAI(), store, "IdeaBlocks", field_info)
```

---

## Why Blockify + LangChain

| Default LangChain RAG | Blockify + LangChain |
|---|---|
| Retrieval surfaces duplicates from boilerplate | 40X distillation removes duplicates before vectorization |
| Context windows bloated by redundant chunks | 3.09X fewer tokens per query |
| Agents make wrong tool choices on similar content | `entity_type` filtering routes queries correctly |
| No audit trail from answer → source | Every IdeaBlock carries a source reference |

---

## Related Integrations

- [Blockify + LlamaIndex](./BLOCKIFY-LLAMAINDEX.md) — Same pattern, LlamaIndex flavor
- [Blockify + n8n](./BLOCKIFY-N8N.md) — Orchestrate LangChain + Blockify in a workflow
- [Blockify + Supabase](./BLOCKIFY-SUPABASE.md) — pgvector-backed LangChain vector store
- [Blockify + Elastic](./BLOCKIFY-ELASTIC.md) — ELSER + Blockify for hybrid retrieval

---

*LangChain is a trademark of LangChain, Inc. Blockify is an independent open-source project and is not affiliated with LangChain.*
