# Clawdbot RAG Integration with Blockify

**Document Purpose:** Technical guide for integrating Blockify-processed knowledge bases into the Clawdbot website chatbot.

---

## Table of Contents

1. [Current Clawdbot Architecture](#current-clawdbot-architecture)
2. [RAG Enhancement Plan](#rag-enhancement-plan)
3. [Implementation Guide](#implementation-guide)
4. [Knowledge Base Structure](#knowledge-base-structure)
5. [Code Examples](#code-examples)
6. [Testing & Monitoring](#testing--monitoring)
7. [Deployment Checklist](#deployment-checklist)

---

## Current Clawdbot Architecture

### Existing Implementation

Based on `src/components/chatbot/chatbot.ts`:

```
+-------------------------------------------------------+
|                  CURRENT CLAWDBOT                     |
+-------------------------------------------------------+

[User Message]
      |
      v
[Session Management]
      |
      +---> Rate limiting (50 messages/day)
      +---> Session ID generation
      +---> Email capture after threshold
      |
      v
[API Call to LLM] (Grok)
      |
      +---> System prompt with company context
      +---> Conversation history
      +---> User message
      |
      v
[Response to User]
```

### Current Limitations

1. **No knowledge retrieval** - Only uses static system prompt
2. **Limited context** - Relies on LLM's training data
3. **No product details** - Can't answer specific pricing/feature questions
4. **Potential hallucinations** - No grounding in actual documentation

---

## RAG Enhancement Plan

### Enhanced Architecture

```
+-------------------------------------------------------+
|              ENHANCED CLAWDBOT WITH RAG               |
+-------------------------------------------------------+

[User Message]
      |
      v
[Session Management]
      |
      v
+---------------------------------------------------+
| NEW: QUERY ROUTING                                 |
+---------------------------------------------------+
|  [Query Classification]                            |
|       |                                            |
|       +---> FAQ → Direct FAQ lookup                |
|       +---> Product → Product KB search            |
|       +---> Technical → Documentation search       |
|       +---> Pricing → Pricing database             |
|       +---> General → Multi-source search          |
+---------------------------------------------------+
      |
      v
+---------------------------------------------------+
| NEW: RETRIEVAL LAYER                               |
+---------------------------------------------------+
|  [Hybrid Search]                                   |
|       |                                            |
|       +---> Vector search (semantic)               |
|       +---> BM25 search (keyword)                  |
|       +---> Reciprocal Rank Fusion                 |
|       |                                            |
|       v                                            |
|  [Top K IdeaBlocks]                               |
+---------------------------------------------------+
      |
      v
+---------------------------------------------------+
| NEW: CONTEXT ASSEMBLY                              |
+---------------------------------------------------+
|  System Prompt + Retrieved IdeaBlocks +            |
|  Conversation History + User Message               |
+---------------------------------------------------+
      |
      v
[Enhanced API Call to LLM]
      |
      v
[Response with Citations]
```

### Expected Improvements

| Metric | Before | After (Projected) |
|--------|--------|-------------------|
| Answer Accuracy | ~60% | ~95% |
| Hallucination Rate | ~25% | ~2% |
| Product Knowledge | Limited | Comprehensive |
| Citation Support | None | Full |

---

## Implementation Guide

### Phase 1: Knowledge Base Creation

#### Step 1: Gather Source Content

```bash
# Create content collection
mkdir -p /data/clawdbot-kb/source

# Collect product documentation
cp docs/products/*.md /data/clawdbot-kb/source/

# Collect FAQs
cp docs/faq/*.md /data/clawdbot-kb/source/

# Collect case studies
cp docs/case-studies/*.md /data/clawdbot-kb/source/
```

#### Step 2: Process with Blockify

```python
#!/usr/bin/env python3
"""Process all source content through Blockify."""

import os
import glob
from blockify_pipeline import process_document

source_dir = '/data/clawdbot-kb/source'
output_dir = '/data/clawdbot-kb/ideablocks'

os.makedirs(output_dir, exist_ok=True)

for filepath in glob.glob(f'{source_dir}/*.md'):
    filename = os.path.basename(filepath).replace('.md', '.json')
    output_path = os.path.join(output_dir, filename)

    print(f"Processing {filepath}...")
    process_document(filepath, output_path)
```

#### Step 3: Merge and Index

```python
#!/usr/bin/env python3
"""Merge all IdeaBlocks and create search index."""

import json
import glob

# Merge all IdeaBlocks
all_blocks = []
for filepath in glob.glob('/data/clawdbot-kb/ideablocks/*.json'):
    with open(filepath) as f:
        blocks = json.load(f)
        # Add source file metadata
        for block in blocks:
            block['source_file'] = filepath
        all_blocks.extend(blocks)

# Save merged knowledge base
with open('/data/clawdbot-kb/knowledge_base.json', 'w') as f:
    json.dump(all_blocks, f, indent=2)

print(f"Created knowledge base with {len(all_blocks)} IdeaBlocks")
```

### Phase 2: Vector Index Creation

#### Using Cloudflare Vectorize

```typescript
// scripts/index-ideablocks.ts

import { OpenAI } from 'openai';
import ideablocks from '../data/knowledge_base.json';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function indexIdeaBlocks(env: Env) {
  for (const block of ideablocks) {
    // Create embedding text
    const text = `${block.name} ${block.critical_question} ${block.trusted_answer}`;

    // Generate embedding
    const response = await openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: text
    });

    const embedding = response.data[0].embedding;

    // Store in Vectorize
    await env.VECTORIZE.upsert([{
      id: block.id || `ib_${Date.now()}`,
      values: embedding,
      metadata: {
        name: block.name,
        question: block.critical_question,
        answer: block.trusted_answer,
        tags: block.tags.join(','),
        keywords: block.keywords.join(',')
      }
    }]);
  }

  console.log(`Indexed ${ideablocks.length} IdeaBlocks`);
}
```

### Phase 3: Retrieval Service

```typescript
// src/services/clawdbot-retrieval.ts

interface IdeaBlock {
  name: string;
  question: string;
  answer: string;
  tags: string;
  keywords: string;
}

interface RetrievalResult {
  ideablocks: IdeaBlock[];
  sources: string[];
}

export async function retrieveContext(
  query: string,
  env: Env
): Promise<RetrievalResult> {
  // 1. Generate query embedding
  const queryEmbedding = await generateEmbedding(query, env);

  // 2. Vector search
  const vectorResults = await env.VECTORIZE.query(queryEmbedding, {
    topK: 10,
    returnMetadata: true
  });

  // 3. BM25 search (using KV-stored inverted index)
  const bm25Results = await bm25Search(query, env);

  // 4. Reciprocal Rank Fusion
  const fused = reciprocalRankFusion(
    vectorResults.matches.map(m => m.id),
    bm25Results.map(r => r.id)
  );

  // 5. Fetch full IdeaBlocks
  const ideablocks: IdeaBlock[] = [];
  const sources: string[] = [];

  for (const id of fused.slice(0, 5)) {
    const match = vectorResults.matches.find(m => m.id === id);
    if (match?.metadata) {
      ideablocks.push({
        name: match.metadata.name as string,
        question: match.metadata.question as string,
        answer: match.metadata.answer as string,
        tags: match.metadata.tags as string,
        keywords: match.metadata.keywords as string
      });
      sources.push(match.metadata.name as string);
    }
  }

  return { ideablocks, sources };
}

function reciprocalRankFusion(
  list1: string[],
  list2: string[],
  k: number = 60
): string[] {
  const scores = new Map<string, number>();

  list1.forEach((id, rank) => {
    scores.set(id, (scores.get(id) || 0) + 1 / (k + rank));
  });

  list2.forEach((id, rank) => {
    scores.set(id, (scores.get(id) || 0) + 1 / (k + rank));
  });

  return Array.from(scores.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([id]) => id);
}

async function generateEmbedding(text: string, env: Env): Promise<number[]> {
  const response = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'text-embedding-3-small',
      input: text
    })
  });

  const data = await response.json();
  return data.data[0].embedding;
}

async function bm25Search(query: string, env: Env): Promise<Array<{id: string}>> {
  // Simple keyword matching as BM25 approximation
  // For production, use a proper search index
  const keywords = query.toLowerCase().split(/\s+/);
  const allBlocks = await env.KV_IDEABLOCKS.list();

  const scored = [];
  for (const key of allBlocks.keys) {
    const block = await env.KV_IDEABLOCKS.get(key.name, 'json');
    if (!block) continue;

    const text = `${block.name} ${block.answer} ${block.keywords}`.toLowerCase();
    const matches = keywords.filter(kw => text.includes(kw)).length;

    if (matches > 0) {
      scored.push({ id: key.name, score: matches / keywords.length });
    }
  }

  return scored.sort((a, b) => b.score - a.score);
}
```

### Phase 4: Enhanced Chatbot

```typescript
// src/components/chatbot/chatbot-rag.ts

import { retrieveContext } from '../../services/clawdbot-retrieval';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export async function handleChatMessage(
  userMessage: string,
  conversationHistory: Message[],
  env: Env
): Promise<string> {
  // 1. Retrieve relevant context
  const { ideablocks, sources } = await retrieveContext(userMessage, env);

  // 2. Build RAG-enhanced prompt
  const systemPrompt = buildSystemPrompt(ideablocks);

  // 3. Prepare messages
  const messages: Message[] = [
    { role: 'system', content: systemPrompt },
    ...conversationHistory.slice(-10),
    { role: 'user', content: userMessage }
  ];

  // 4. Call LLM
  const response = await callLLM(messages, env);

  // 5. Add citation if sources used
  if (sources.length > 0) {
    return `${response}\n\n*Sources: ${sources.join(', ')}*`;
  }

  return response;
}

function buildSystemPrompt(ideablocks: IdeaBlock[]): string {
  const knowledgeBase = ideablocks.map(ib =>
    `[${ib.name}]\nQ: ${ib.question}\nA: ${ib.answer}`
  ).join('\n\n');

  return `You are Clawdbot, the AI assistant for Iternal Technologies.

## Your Knowledge Base

${knowledgeBase}

## Guidelines

1. Answer questions using ONLY the knowledge base above
2. If information isn't in the knowledge base, say "I don't have that specific information, but I can help you get in touch with our team."
3. Be concise, friendly, and helpful
4. For pricing questions, direct users to the pricing page or sales team
5. For technical questions, provide what you know and offer to connect them with support

## Products You Know About

- AirgapAI: Secure AI for air-gapped environments
- Blockify: Data optimization for enterprise RAG
- IdeaBlocks: Structured knowledge units
- Waypoint: Analytics and insights platform
- Autoreports: Automated reporting solution

## Company Info

Iternal Technologies is an enterprise AI company focused on secure, accurate AI solutions.
Website: iternal.ai
Contact: sales@iternal.ai`;
}

async function callLLM(messages: Message[], env: Env): Promise<string> {
  // Use existing Grok/Claude/GPT integration
  // This is the existing implementation from chatbot.ts
  const response = await fetch('https://api.x.ai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.XAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'grok-2-latest',
      messages,
      max_tokens: 1000,
      temperature: 0.7
    })
  });

  const data = await response.json();
  return data.choices[0].message.content;
}
```

---

## Knowledge Base Structure

### Recommended Organization

```
/data/clawdbot-kb/
├── source/                    # Raw source documents
│   ├── products/
│   │   ├── airgapai.md
│   │   ├── blockify.md
│   │   └── ...
│   ├── faq/
│   │   ├── general.md
│   │   ├── pricing.md
│   │   └── technical.md
│   ├── case-studies/
│   │   ├── intel.md
│   │   └── ...
│   └── documentation/
│       └── ...
├── ideablocks/                # Processed IdeaBlocks by source
│   ├── products/
│   ├── faq/
│   ├── case-studies/
│   └── documentation/
├── knowledge_base.json        # Merged knowledge base
└── index/                     # Search indexes
    ├── vectors/               # Vector embeddings
    └── bm25/                  # Keyword index
```

### Content Categories

| Category | Content Type | Priority |
|----------|--------------|----------|
| Products | Features, benefits, specs | High |
| FAQ | Common questions | High |
| Pricing | Plans, features | High |
| Case Studies | Customer stories | Medium |
| Documentation | Technical details | Medium |
| Blog | Thought leadership | Low |

---

## Code Examples

### Full Clawdbot RAG Integration

```typescript
// src/components/chatbot/index.ts - Main export

export { getChatbotScript } from './chatbot-ui';
export { handleChatMessage } from './chatbot-rag';

// Example API route
export async function handleChatRequest(request: Request, env: Env) {
  const { message, sessionId, history } = await request.json();

  // Rate limiting
  const rateLimit = await checkRateLimit(sessionId, env);
  if (!rateLimit.allowed) {
    return Response.json({
      error: 'Rate limit exceeded',
      remaining: rateLimit.remaining,
      reset: rateLimit.reset
    }, { status: 429 });
  }

  // Get response with RAG
  try {
    const response = await handleChatMessage(message, history, env);
    return Response.json({ response });
  } catch (error) {
    console.error('Chat error:', error);
    return Response.json({
      response: "I'm having trouble right now. Please try again or contact support@iternal.ai"
    });
  }
}
```

### Wrangler Configuration

```toml
# wrangler.toml additions

[[vectorize]]
binding = "VECTORIZE"
index_name = "clawdbot-ideablocks"

[[kv_namespaces]]
binding = "KV_IDEABLOCKS"
id = "your-kv-namespace-id"

[vars]
OPENAI_API_KEY = "" # Set in dashboard or secrets
XAI_API_KEY = ""    # Set in dashboard or secrets
```

---

## Testing & Monitoring

### Test Queries

```typescript
const testQueries = [
  // Product questions
  "What is AirgapAI?",
  "How does Blockify improve accuracy?",
  "What products does Iternal offer?",

  // Pricing
  "How much does Blockify cost?",
  "Do you offer enterprise pricing?",

  // Technical
  "What embeddings does Blockify support?",
  "How do I integrate with Azure?",

  // Edge cases
  "Can you write code for me?",
  "What's the weather like?",
  "Tell me about your competitors"
];

async function testRetrieval(env: Env) {
  for (const query of testQueries) {
    const { ideablocks, sources } = await retrieveContext(query, env);
    console.log(`Query: ${query}`);
    console.log(`Found: ${ideablocks.length} IdeaBlocks`);
    console.log(`Sources: ${sources.join(', ')}`);
    console.log('---');
  }
}
```

### Monitoring Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Retrieval Latency (p99) | <200ms | >500ms |
| Answer Accuracy | >90% | <80% |
| User Satisfaction | >4.2/5 | <3.5/5 |
| Hallucination Rate | <5% | >10% |
| No-Answer Rate | <10% | >20% |

---

## Deployment Checklist

### Pre-Deployment

- [ ] Process all source documents through Blockify
- [ ] Create and verify vector index
- [ ] Test retrieval with sample queries
- [ ] Verify API keys and bindings
- [ ] Update wrangler.toml configuration

### Deployment

- [ ] Deploy to staging environment
- [ ] Run integration tests
- [ ] Verify rate limiting works
- [ ] Test with real user scenarios
- [ ] Monitor error rates

### Post-Deployment

- [ ] Set up monitoring dashboards
- [ ] Configure alerts
- [ ] Schedule knowledge base refresh (weekly)
- [ ] Document runbooks for common issues

---

*Document created: 2026-01-25*
*Implementation version: 1.0*
