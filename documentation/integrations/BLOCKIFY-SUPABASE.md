# Blockify + Supabase: Cleaner pgvector, Smaller Indexes, Faster Queries

> **TL;DR:** Supabase's pgvector extension makes Postgres a first-class vector database, and the Supabase AI toolkit makes RAG dead simple for full-stack developers. But pgvector performance (and your OpenAI embedding bill) degrades with corpus redundancy. Blockify reduces your corpus 40X before you ever call `INSERT`, cutting embedding spend and improving retrieval precision 2.29X.

---

## The Problem: pgvector Scales With Row Count, Not Signal

Supabase is attractive for RAG because it's Postgres: row-level security, real-time subscriptions, edge functions, and pgvector all in one stack. But:

- **Embedding cost** — Every row you insert gets an embedding API call. Duplicates = paying twice.
- **Index size** — HNSW and IVFFlat indexes grow linearly. A 1M-row index with 80% redundancy is doing 5X more work than it should.
- **Query latency** — HNSW traversal slows as `ef_search` encounters near-duplicate neighbors.
- **RLS complexity** — Per-block governance tags require extra schema that's painful to retrofit after indexing.

---

## How Blockify Fits

Blockify runs before the `INSERT`. Your Supabase table stores IdeaBlocks, not raw chunks:

```
Source Docs  →  Blockify  →  Edge Function  →  ideablocks table  →  RPC (match_ideablocks)  →  App
   (Storage     (Ingest +    (fetch embedding                         (cosine similarity +
    bucket,      Distill)     from OpenAI /                            RLS policy)
    Webhook)                  Cohere / Voyage)
```

---

## Quick Start

### 1. Enable pgvector and create the table

```sql
create extension if not exists vector;

create table public.ideablocks (
    id                uuid primary key default gen_random_uuid(),
    name              text not null,
    critical_question text not null,
    trusted_answer    text not null,
    tags              text[] not null default '{}',
    entity_name       text,
    entity_type       text,
    keywords          text[] not null default '{}',
    source_doc        text,
    org_id            uuid not null,
    embedding         vector(1536)
);

create index on public.ideablocks using hnsw (embedding vector_cosine_ops);
create index on public.ideablocks using gin (tags);

alter table public.ideablocks enable row level security;

create policy "tenant_read" on public.ideablocks for select
    using (org_id = (auth.jwt() ->> 'org_id')::uuid);
```

### 2. Edge Function: Blockify + embed + insert

```typescript
// supabase/functions/ingest/index.ts
import { createClient } from "jsr:@supabase/supabase-js";
import OpenAI from "jsr:@openai/openai";

const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SERVICE_ROLE_KEY")!);
const openai = new OpenAI();

Deno.serve(async (req) => {
  const { text, org_id, source_doc } = await req.json();

  const ingest = await fetch("https://api.blockify.ai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${Deno.env.get("BLOCKIFY_API_KEY")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "ingest",
      messages: [{ role: "user", content: text }],
    }),
  }).then(r => r.json());

  const distilled = await fetch("https://api.blockify.ai/v1/chat/completions", {
    method: "POST",
    headers: { "Authorization": `Bearer ${Deno.env.get("BLOCKIFY_API_KEY")}` },
    body: JSON.stringify({
      model: "distill",
      messages: [{ role: "user", content: JSON.stringify(ingest.ideablocks) }],
    }),
  }).then(r => r.json());

  for (const b of distilled.ideablocks) {
    const emb = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: b.trusted_answer,
    });

    await sb.from("ideablocks").insert({
      name: b.name,
      critical_question: b.critical_question,
      trusted_answer: b.trusted_answer,
      tags: b.tags.split(",").map((t: string) => t.trim()),
      entity_name: b.entity.entity_name,
      entity_type: b.entity.entity_type,
      keywords: b.keywords.split(",").map((k: string) => k.trim()),
      source_doc,
      org_id,
      embedding: emb.data[0].embedding,
    });
  }

  return new Response(JSON.stringify({ inserted: distilled.ideablocks.length }));
});
```

### 3. RPC for retrieval

```sql
create or replace function match_ideablocks(
    query_embedding vector(1536),
    match_count int default 5,
    filter_tag text default null
) returns setof public.ideablocks
language sql stable as $$
    select *
    from public.ideablocks
    where (filter_tag is null or filter_tag = any(tags))
    order by embedding <=> query_embedding
    limit match_count;
$$;
```

---

## Advanced Patterns

### Pattern 1: RLS by tag

Push governance into the DB. Users with the `sales` role only see IdeaBlocks tagged `sales`:

```sql
create policy "role_scoped" on public.ideablocks for select
    using (exists (
        select 1 from auth.user_roles r
        where r.user_id = auth.uid()
        and r.role = any(tags)
    ));
```

### Pattern 2: Realtime re-distillation

Use a Postgres trigger + `pg_notify` to enqueue re-distillation when a source document changes. An Edge Function listens, calls Blockify Distill on the affected rows, and UPSERTs the merged block.

### Pattern 3: Drop-in with LangChain `SupabaseVectorStore`

```python
from langchain_community.vectorstores import SupabaseVectorStore
store = SupabaseVectorStore(client=sb, embedding=..., table_name="ideablocks", query_name="match_ideablocks")
```

---

## Why Blockify + Supabase

| Vanilla Supabase pgvector RAG | Blockify + Supabase |
|---|---|
| Embedding bill = O(chunks), grows with duplication | 40X fewer rows → 40X lower embedding + storage cost |
| HNSW index bloated by near-duplicate neighbors | Index is lean; `ef_search` finds distinct results faster |
| RLS is per-row, but tags are ad hoc | IdeaBlocks carry structured `tags` + `entity_type` for precise RLS |
| No structured Q-A in the schema | First-class `critical_question` and `trusted_answer` columns |

---

## Related Integrations

- [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) — Use `SupabaseVectorStore` with Blockified data
- [Blockify + n8n](./BLOCKIFY-N8N.md) — Orchestrate the Edge Function from an n8n workflow
- [Blockify + LlamaIndex](./BLOCKIFY-LLAMAINDEX.md) — LlamaIndex `SupabaseVectorStore`
- [Blockify + Unstructured.io](./BLOCKIFY-UNSTRUCTURED.md) — Parse PDFs into text before Blockifying

---

*Supabase is a trademark of Supabase Inc. Blockify is an independent open-source project and is not affiliated with Supabase.*
