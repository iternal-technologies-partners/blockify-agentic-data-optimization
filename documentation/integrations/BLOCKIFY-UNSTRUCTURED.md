# Blockify + Unstructured.io: Parse Anything, Optimize Everything

> **TL;DR:** Unstructured.io is the de facto standard for extracting clean text and structural metadata from messy enterprise documents (PDF, DOCX, PPTX, HTML, email, images). It solves the "getting to text" problem. Blockify solves the "now what" problem: transforming that text into deduplicated IdeaBlocks ready for production RAG. The two pipelines compose perfectly.

---

## The Problem: Parsing Is Only Half the Job

Unstructured.io gives you beautifully chunked elements — titles, narrative text, tables, lists — with rich metadata. But:

- **Elements are still duplicated across documents** — a boilerplate NDA header appears identically in 500 proposals
- **Chunking options (`by_title`, `basic`, `by_page`) are mechanical** — they respect structure but don't semantically deduplicate
- **Table extraction is excellent** — but tables repeat across reports (quarterly pricing, standard SLAs) with 99% overlap
- **The output is ready to embed** — which is exactly the problem when there's redundancy in the source

Unstructured.io is the best tool for parsing. Blockify is the best tool for what comes next.

---

## How Blockify Fits

The two pipelines chain:

```
Source Docs  →  Unstructured.io  →  Blockify (Ingest + Distill)  →  Embeddings  →  Vector DB
   (PDF,         (element-level      (IdeaBlocks)                  (any)          (any)
    DOCX,         extraction +
    PPTX,         metadata)
    HTML,
    email,
    images)
```

Unstructured's element metadata (`filename`, `page_number`, `coordinates`, `parent_id`) survives through Blockify as IdeaBlock source metadata — preserving full traceability from IdeaBlock answer back to page coordinate in the source PDF.

---

## Quick Start

### 1. Install

```bash
pip install unstructured[all-docs] requests
```

### 2. Parse with Unstructured, Blockify the elements

```python
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title
import requests
import os

BK_URL = "https://api.blockify.ai/v1/chat/completions"
BK_HEADERS = {"Authorization": f"Bearer {os.environ['BLOCKIFY_API_KEY']}"}

def parse_and_blockify(filepath: str) -> list[dict]:
    elements = partition(filename=filepath, strategy="hi_res")
    chunks = chunk_by_title(elements, max_characters=2000, combine_text_under_n_chars=500)

    all_blocks: list[dict] = []
    for chunk in chunks:
        # 1. Blockify ingest
        ingest = requests.post(BK_URL, headers=BK_HEADERS, json={
            "model": "ingest",
            "messages": [{"role": "user", "content": chunk.text}],
        }).json()

        # Carry Unstructured metadata into each IdeaBlock
        for b in ingest["ideablocks"]:
            b["source_metadata"] = {
                "filename": chunk.metadata.filename,
                "page_number": chunk.metadata.page_number,
                "category": chunk.category,
                "element_id": chunk.id,
            }
        all_blocks.extend(ingest["ideablocks"])

    # 2. Distill across the whole document (or corpus)
    distilled = requests.post(BK_URL, headers=BK_HEADERS, json={
        "model": "distill",
        "messages": [{"role": "user", "content": str(all_blocks)}],
    }).json()

    return distilled["ideablocks"]
```

### 3. Embed + store

Each IdeaBlock's `trusted_answer` is what you embed. The carried `source_metadata` gives you citation-ready retrieval: "See page 47 of `Q3-Report.pdf`."

---

## Advanced Patterns

### Pattern 1: Preserve table semantics

Unstructured.io emits tables as HTML by default. Use the `technical-ingest` Blockify model for tabular content — it preserves row/column relationships better than the general `ingest` model.

```python
if chunk.category == "Table":
    model = "technical-ingest"
else:
    model = "ingest"
```

### Pattern 2: OCR + Blockify for scanned documents

Use Unstructured's `strategy="ocr_only"` for scanned PDFs. The OCR text may have errors; Blockify's LLM normalization stage tolerates and smooths many OCR artifacts into coherent IdeaBlocks.

### Pattern 3: Email + attachment ingestion

Unstructured handles MSG / EML with attachments. Blockify deduplicates across the thread — the same forwarded attachment across 30 replies collapses into one canonical IdeaBlock set.

---

## Why Blockify + Unstructured.io

| Unstructured.io alone | Unstructured.io + Blockify |
|---|---|
| Elements and chunks preserve structure but not semantics | IdeaBlocks preserve structure *and* semantics |
| Duplicate elements across documents still indexed | Cross-document duplicates collapsed |
| Tables indexed as HTML; similarity search is awkward | Tables converted into Q-A-aligned IdeaBlocks |
| Great metadata — but not used for deduplication | Metadata carried forward and used for governance |

---

## Related Integrations

- [Blockify + LlamaIndex](./BLOCKIFY-LLAMAINDEX.md) — LlamaIndex ships an `UnstructuredReader`; drop Blockify in after
- [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) — `UnstructuredFileLoader` + `BlockifyTransformer`
- [Blockify + Elastic](./BLOCKIFY-ELASTIC.md) — Unstructured → Blockify → Elastic for hybrid search over parsed docs
- [Blockify + Cloudflare](./BLOCKIFY-CLOUDFLARE.md) — Edge-hosted parse → Blockify → Vectorize pipeline

---

*Unstructured.io is a trademark of Unstructured Technologies, Inc. Blockify is an independent open-source project and is not affiliated with Unstructured.io.*
