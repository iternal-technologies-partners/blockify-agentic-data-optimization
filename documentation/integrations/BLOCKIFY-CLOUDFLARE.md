# Blockify + Cloudflare: Edge-Native RAG on Workers + Vectorize + R2

> **TL;DR:** Cloudflare's AI stack — Workers, Vectorize (vector DB), Workers AI (serverless inference), AutoRAG, R2 (storage), and D1 (edge SQLite) — is the fastest path to globally distributed RAG. But it inherits every chunking problem of traditional RAG. Blockify replaces the chunking step so Vectorize indexes deduplicated IdeaBlocks, cutting cost and latency while improving accuracy.

---

## The Problem: AutoRAG and Vectorize Default to Naive Chunking

Cloudflare's AutoRAG orchestrates the pipeline for you — and uses sensible defaults. But defaults are the problem at enterprise scale:

- **AutoRAG's default chunker** splits by tokens, not semantics
- **Vectorize** has generous limits (5M vectors per index) — so redundancy is tolerated rather than fixed
- **Workers AI embedding models** charge per input token — duplicates inflate your bill
- **R2 stores source docs** — but there's no deduplication between R2 objects before they land in Vectorize

The edge is fast, but speed amplifies garbage-in-garbage-out.

---

## How Blockify Fits

Blockify runs as a Worker step between R2 and Vectorize:

```
R2 bucket  →  Worker: Blockify step  →  Worker: Embed (Workers AI)  →  Vectorize index  →  Worker: RAG endpoint  →  Client
  (raw docs)   (fetch ideablocks via     (@cf/baai/bge-m3 or          (ideablocks-v1)      (retrieve + compose
                api.blockify.ai)          OpenAI via Gateway)                               with Workers AI LLM)
```

R2 → Worker triggers (via Event Notifications) make this fully reactive.

---

## Quick Start

### 1. Worker: ingest an R2 object into Vectorize as IdeaBlocks

```typescript
// src/ingest.ts
export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const { key } = await req.json<{ key: string }>();
    const obj = await env.DOCS.get(key);
    if (!obj) return new Response("not found", { status: 404 });
    const text = await obj.text();

    const ingest = await fetch("https://api.blockify.ai/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.BLOCKIFY_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "ingest",
        messages: [{ role: "user", content: text }],
      }),
    }).then((r) => r.json<any>());

    const distilled = await fetch("https://api.blockify.ai/v1/chat/completions", {
      method: "POST",
      headers: { Authorization: `Bearer ${env.BLOCKIFY_API_KEY}` },
      body: JSON.stringify({
        model: "distill",
        messages: [{ role: "user", content: JSON.stringify(ingest.ideablocks) }],
      }),
    }).then((r) => r.json<any>());

    const vectors: VectorizeVector[] = [];
    for (const b of distilled.ideablocks) {
      const emb = await env.AI.run("@cf/baai/bge-m3", { text: [b.trusted_answer] });
      vectors.push({
        id: b.id,
        values: emb.data[0],
        metadata: {
          name: b.name,
          critical_question: b.critical_question,
          trusted_answer: b.trusted_answer,
          tags: b.tags,
          entity_type: b.entity.entity_type,
          source_key: key,
        },
      });
    }
    await env.BLOCKIFY_INDEX.upsert(vectors);
    return new Response(JSON.stringify({ upserted: vectors.length }));
  },
} satisfies ExportedHandler<Env>;
```

### 2. Worker: RAG endpoint

```typescript
// src/rag.ts
export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const { query } = await req.json<{ query: string }>();
    const q = await env.AI.run("@cf/baai/bge-m3", { text: [query] });
    const hits = await env.BLOCKIFY_INDEX.query(q.data[0], { topK: 5, returnMetadata: "all" });

    const context = hits.matches.map((m) => m.metadata!.trusted_answer).join("\n\n");
    const answer = await env.AI.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", {
      messages: [
        { role: "system", content: "Answer using only the provided IdeaBlocks." },
        { role: "user", content: `Context:\n${context}\n\nQuestion: ${query}` },
      ],
    });
    return Response.json({ answer, sources: hits.matches });
  },
} satisfies ExportedHandler<Env>;
```

### 3. `wrangler.toml`

```toml
name = "blockify-rag"
main = "src/rag.ts"
compatibility_date = "2026-01-01"

[[r2_buckets]]
binding = "DOCS"
bucket_name = "enterprise-docs"

[[vectorize]]
binding = "BLOCKIFY_INDEX"
index_name = "ideablocks-v1"

[ai]
binding = "AI"

[vars]
# BLOCKIFY_API_KEY set via `wrangler secret put`
```

---

## Advanced Patterns

### Pattern 1: R2 Event Notifications → auto-ingest

Wire R2 Event Notifications to a Queue. Every new/updated object triggers the ingest Worker. Deletions trigger a Vectorize `deleteByIds` keyed on `source_key`.

### Pattern 2: Namespace per tenant

Vectorize supports namespaces. Put each tenant's IdeaBlocks in their own namespace (`namespace: org-<uuid>`). A single index, strong isolation, one upsert/query flow.

### Pattern 3: OpenClaw on the edge

The repo's [OpenClaw RAG Integration](../OPENCLAW-RAG-INTEGRATION.md) example runs the chatbot entirely on Cloudflare Workers with Blockified knowledge in Vectorize. Sub-100ms retrieval anywhere in the world.

---

## Why Blockify + Cloudflare

| AutoRAG / Vanilla Vectorize | Blockify + Cloudflare |
|---|---|
| Default token chunker produces duplicates | IdeaBlocks are deduplicated before embedding |
| Workers AI embedding bill scales with corpus size | 40X fewer embeddings = 40X lower cost |
| Vectorize queries return near-duplicate top-K | 2.29X improvement in vector precision |
| No per-block governance story on the edge | Tags travel in Vectorize metadata, filter at query time |

---

## Related Integrations

- [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) — Use LangChain's `CloudflareWorkersAI` embedding with Blockified docs
- [Blockify + Unstructured.io](./BLOCKIFY-UNSTRUCTURED.md) — Parse PDFs in a Worker before Blockifying
- [Blockify + Supabase](./BLOCKIFY-SUPABASE.md) — Alternative when you need SQL + vectors in one store
- [OpenClaw RAG Integration](../OPENCLAW-RAG-INTEGRATION.md) — Full chatbot reference implementation

---

*Cloudflare, Workers, Vectorize, R2, and AutoRAG are trademarks of Cloudflare, Inc. Blockify is an independent open-source project and is not affiliated with Cloudflare.*
