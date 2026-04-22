# Blockify + Starburst: Federated Document Optimization Across Your Data Lake

> **TL;DR:** Starburst (commercial Trino) lets you query across hundreds of data sources — S3, Iceberg, Snowflake, Postgres, Kafka, SharePoint connectors, and more — from one SQL endpoint. But the unstructured text columns in those tables (`proposal_body`, `case_study_html`, `contract_text`) are the messiest inputs to enterprise RAG. Blockify transforms those columns into IdeaBlocks written back to a curated Iceberg table, ready for governed retrieval.

---

## The Problem: Data-Lake Text Is the Worst RAG Input

A Starburst-backed data lake is a strategic asset for analytics — and a RAG disaster when used naively:

- **Unstructured columns spread across hundreds of tables** — `notes`, `description`, `comments`, `body_html` each in a different format
- **Massive duplication** — The same proposal boilerplate exists in `sales.proposals`, `legal.draft_documents`, and `marketing.case_studies`
- **Cross-domain joins amplify noise** — Federated queries return concatenated text from multiple sources, multiplying duplicates
- **Governance is per-table, not per-idea** — Access control works at the Starburst catalog level, but you can't grant access to "pricing information from 2026 and later" across every source

---

## How Blockify Fits

Blockify consumes Starburst query results and writes IdeaBlocks back to a curated Iceberg table on the same lake:

```
Starburst catalogs  →  SELECT text from federated sources  →  Blockify (Ingest + Distill)  →  Iceberg: blockify.ideablocks  →  Vector DB / Starburst AI Functions
   (S3, Iceberg,        (one SQL query across                  (IdeaBlocks)                  (curated, governed,                  (retrieval /
    Snowflake,           multiple catalogs)                                                    time-travel enabled)                 analytics)
    Postgres,
    SharePoint)
```

The Iceberg output table is queryable *back* through Starburst — so analytics, BI, and retrieval all operate on the same single source of truth.

---

## Quick Start

### 1. Pull unstructured text from federated sources

```sql
-- starburst-sql
CREATE TABLE blockify_staging.raw_text AS
SELECT
    src_catalog,
    src_table,
    src_row_id,
    text_content,
    ingested_at
FROM (
    SELECT 'sfdc' AS src_catalog, 'proposals' AS src_table,
           id AS src_row_id, body AS text_content, LAST_MODIFIED AS ingested_at
    FROM salesforce.default.proposals
    UNION ALL
    SELECT 'sharepoint', 'case_studies', doc_id, body_html, modified
    FROM sharepoint.documents.case_studies
    UNION ALL
    SELECT 'confluence', 'pages', page_id, content, updated
    FROM confluence.default.pages
);
```

### 2. Blockify the staging table

Call Blockify from a Python job or the Claude Code skill against the staged rows:

```python
import trino
from blockify_client import Blockify

conn = trino.dbapi.connect(host="starburst.corp", user="etl")
bk = Blockify(api_key=...)

cur = conn.cursor()
cur.execute("SELECT src_catalog, src_table, src_row_id, text_content FROM blockify_staging.raw_text")

for cat, tbl, row_id, text in cur.fetchall():
    blocks = bk.distill(bk.ingest(text))
    for b in blocks:
        cur.execute("""
            INSERT INTO iceberg.blockify.ideablocks
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, current_timestamp)
        """, (b.name, b.critical_question, b.trusted_answer,
              b.tags, b.entity_name, b.entity_type, b.keywords,
              cat, tbl, row_id))
```

### 3. Query IdeaBlocks via Starburst

```sql
-- Governance at the idea level via SQL row filters
SELECT name, trusted_answer
FROM iceberg.blockify.ideablocks
WHERE contains(tags, 'pricing')
  AND contains(tags, 'current')
  AND src_catalog IN ('sfdc', 'confluence');
```

---

## Advanced Patterns

### Pattern 1: Iceberg time-travel for block lineage

Iceberg snapshots every insert. Roll back to "what IdeaBlocks did we retrieve on 2026-01-15?" for audit:

```sql
SELECT * FROM iceberg.blockify.ideablocks FOR VERSION AS OF 1234567890;
```

### Pattern 2: Starburst materialized views for hot IdeaBlock subsets

```sql
CREATE MATERIALIZED VIEW blockify.hot_sales_blocks AS
SELECT * FROM iceberg.blockify.ideablocks
WHERE entity_type = 'PRODUCT' AND contains(tags, 'sales');
```

Downstream vector-DB syncers read the materialized view, so they never re-process the full Iceberg table.

### Pattern 3: Starburst AI Functions over IdeaBlocks

Starburst's AI functions (`ai_extract`, `ai_classify`, `ai_gen`) run fastest on small, clean inputs. Point them at `ideablocks.trusted_answer` instead of raw columns to cut inference cost.

---

## Why Blockify + Starburst

| Starburst alone | Blockify + Starburst |
|---|---|
| `ai_*` functions run on raw, duplicated text columns | AI functions run on 40X smaller IdeaBlock table |
| Governance is per-catalog, per-table | Per-IdeaBlock tags enable row-level compliance filtering |
| Duplicate content across federated sources | Cross-source duplicates collapsed into canonical blocks |
| No structured Q-A layer for retrieval | First-class retrieval-ready columns in Iceberg |

---

## Related Integrations

- [Blockify + Elastic](./BLOCKIFY-ELASTIC.md) — Push IdeaBlocks from Iceberg to Elastic for hybrid search
- [Blockify + Milvus](./BLOCKIFY-MILVUS.md) — Or Milvus if you need dense vector at scale
- [Blockify + Kibana](./BLOCKIFY-KIBANA.md) — Visualize IdeaBlock coverage and drift
- [Blockify + Unstructured.io](./BLOCKIFY-UNSTRUCTURED.md) — Parse blob storage before Blockifying

---

*Starburst, Trino, and Iceberg are trademarks of their respective owners. Blockify is an independent open-source project and is not affiliated with Starburst Data.*
