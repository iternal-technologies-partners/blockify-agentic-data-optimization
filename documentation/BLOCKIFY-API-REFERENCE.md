# Blockify API Reference

**Document Purpose:** Complete API documentation for integrating Blockify into applications.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [Endpoints](#endpoints)
4. [Model Reference](#model-reference)
5. [Request/Response Examples](#requestresponse-examples)
6. [Error Handling](#error-handling)
7. [Rate Limits](#rate-limits)
8. [SDK Examples](#sdk-examples)

---

## Authentication

All API requests require authentication via Bearer token.

```bash
Authorization: Bearer YOUR_API_KEY
```

### Getting an API Key

1. Create account at [console.blockify.ai](https://console.blockify.ai)
2. Navigate to API Keys section
3. Generate a new key
4. Store securely (key is shown only once)

### Key Format

```
blk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Base URL

```
https://api.blockify.ai/v1
```

---

## Endpoints

### POST /chat/completions

The primary endpoint for all Blockify operations. Follows OpenAI API standard.

#### Request Headers

| Header | Value | Required |
|--------|-------|----------|
| `Authorization` | `Bearer YOUR_API_KEY` | Yes |
| `Content-Type` | `application/json` | Yes |

#### Request Body

```json
{
  "model": "ingest",
  "messages": [
    {
      "role": "user",
      "content": "Your text content here"
    }
  ],
  "max_tokens": 8000,
  "temperature": 0.5
}
```

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model to use: `ingest`, `distill`, or `technical-ingest` |
| `messages` | array | Yes | Array of message objects |
| `max_tokens` | integer | Yes | Maximum output tokens (recommended: 8000+) |
| `temperature` | float | Yes | Model temperature (recommended: 0.5) |

#### Response

```json
{
  "id": "oUjtbqw-z1gNr-9c39f07ef51c2e5d",
  "object": "chat.completion",
  "created": 1769366850,
  "prompt": [],
  "choices": [
    {
      "finish_reason": "stop",
      "seed": 4575226201806995500,
      "index": 0,
      "logprobs": null,
      "message": {
        "role": "assistant",
        "content": "<ideablock>...</ideablock>",
        "tool_calls": []
      }
    }
  ],
  "usage": {
    "prompt_tokens": 97,
    "completion_tokens": 416,
    "total_tokens": 513,
    "cached_tokens": 0
  },
  "legal_reminder": "See https://iternal.ai/legal/..."
}
```

---

## Model Reference

### Blockify Ingest (`ingest`)

**Purpose:** Convert raw text to IdeaBlocks

**Input:** Raw text chunks (1,000-4,000 characters)

**Output:** XML IdeaBlocks

**Fidelity:** ~99% lossless for facts and numbers

```bash
curl -X POST https://api.blockify.ai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ingest",
    "messages": [{
      "role": "user",
      "content": "Blockify is a data optimization tool that takes messy, unstructured text and intelligently optimizes it into small, easy-to-understand IdeaBlocks. Blockify improves accuracy of LLMs by an average aggregate 78X."
    }],
    "max_tokens": 8000,
    "temperature": 0.5
  }'
```

### Blockify Distill (`distill`)

**Purpose:** Merge/deduplicate similar IdeaBlocks

**Input:** 2-15 similar IdeaBlocks in XML format

**Output:** Consolidated XML IdeaBlocks

**Fidelity:** ~95% lossless

```bash
curl -X POST https://api.blockify.ai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "distill",
    "messages": [{
      "role": "user",
      "content": "<ideablock>..first block..</ideablock><ideablock>..second block..</ideablock><ideablock>..third block..</ideablock>"
    }],
    "max_tokens": 8000,
    "temperature": 0.5
  }'
```

### Blockify Technical Ingest (`technical-ingest`)

**Purpose:** Process ordered content (manuals, procedures)

**Input:** Structured markdown with Primary/Proceeding/Following sections

**Output:** Procedural XML with sentence roles

**Fidelity:** ~99% lossless

```bash
curl -X POST https://api.blockify.ai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "technical-ingest",
    "messages": [{
      "role": "user",
      "content": "### Primary ###\n---\n[Main content]\n---\n### Proceeding ###\n---\n[Previous section]\n---\n### Following ###\n---\n[Next section]"
    }],
    "max_tokens": 8000,
    "temperature": 0.5
  }'
```

---

## Request/Response Examples

### Example 1: Basic Ingest

**Request:**
```json
{
  "model": "ingest",
  "messages": [{
    "role": "user",
    "content": "Claude Code is an AI-powered development tool that helps programmers write, debug, and optimize code. It provides intelligent code suggestions, automated testing, and context-aware assistance. Claude Code integrates with popular IDEs and supports multiple programming languages."
  }],
  "max_tokens": 8000,
  "temperature": 0.5
}
```

**Response Content:**
```xml
<ideablock>
  <name>Claude Code Overview</name>
  <critical_question>What is Claude Code?</critical_question>
  <trusted_answer>Claude Code is an AI-powered development tool that helps
    programmers write, debug, and optimize code. It offers intelligent code
    suggestions, automated testing, and context-aware assistance.</trusted_answer>
  <tags>IMPORTANT, PRODUCT FOCUS, INFORM (WITHOUT EMOTION), SIMPLE (OVERVIEW),
    INNOVATION, TECHNOLOGY</tags>
  <entity>
    <entity_name>CLAUDE CODE</entity_name>
    <entity_type>PRODUCT</entity_type>
  </entity>
  <keywords>Claude Code, AI, Development Tool, Code, Intelligent Code
    Suggestions, Automated Testing, Context-Aware Assistance</keywords>
</ideablock>
<ideablock>
  <name>Claude Code Integration</name>
  <critical_question>How does Claude Code integrate with development environments?</critical_question>
  <trusted_answer>Claude Code integrates with popular IDEs and supports
    multiple programming languages.</trusted_answer>
  <tags>IMPORTANT, PRODUCT FOCUS, INFORM (WITHOUT EMOTION), SIMPLE (OVERVIEW),
    INNOVATION, TECHNOLOGY, INTEGRATION</tags>
  <entity>
    <entity_name>CLAUDE CODE</entity_name>
    <entity_type>PRODUCT</entity_type>
  </entity>
  <entity>
    <entity_name>IDES</entity_name>
    <entity_type>OTHER</entity_type>
  </entity>
  <keywords>Claude Code, IDEs, Integration, Programming Languages</keywords>
</ideablock>
```

### Example 2: Enterprise Data

**Request:**
```json
{
  "model": "ingest",
  "messages": [{
    "role": "user",
    "content": "This report presents a comprehensive analysis of the Blockify data ingestion, distillation and optimization capabilities to support Big Four Consulting Firm, compared to traditional chunking methods. Using Blockify's distillation approach, the projected aggregate Enterprise Performance improvement for Big Four Consulting Firm is 68.44X. This performance includes the improvements made by Blockify in enterprise distillation of knowledge, vector accuracy, and data volume reductions for enterprise content lifecycle management."
  }],
  "max_tokens": 8000,
  "temperature": 0.5
}
```

**Response generates multiple IdeaBlocks covering:**
- Performance improvement metrics (68.44X)
- Enterprise distillation approach
- Comparison to traditional chunking
- Vector accuracy improvements
- Data volume reductions

### Example 3: Distillation

**Request:**
```json
{
  "model": "distill",
  "messages": [{
    "role": "user",
    "content": "<ideablock><name>Blockify Distillation Approach</name><critical_question>What is Blockify's distillation approach?</critical_question><trusted_answer>Blockify's distillation approach enables improvements in enterprise distillation of knowledge.</trusted_answer>...</ideablock><ideablock><name>Blockify Distillation Approach</name><critical_question>What is Blockify's distillation approach?</critical_question><trusted_answer>Blockify's unique distillation approach enables improvements in enterprise distillation of ideas.</trusted_answer>...</ideablock><ideablock><name>Blockify Distillation Approach</name><critical_question>What is Blockify's distillation approach?</critical_question><trusted_answer>Blockify's distillation approach enables improvements in enterprise distillation of documents.</trusted_answer>...</ideablock>"
  }],
  "max_tokens": 8000,
  "temperature": 0.5
}
```

**Response (Consolidated):**
```xml
<ideablock>
  <name>Blockify's Distillation Approach Overview</name>
  <critical_question>What is Blockify's distillation approach and its benefits
    for enterprise content management?</critical_question>
  <trusted_answer>Blockify's distillation approach enhances enterprise knowledge
    distillation, improves vector accuracy, and reduces data volume by
    streamlining and refining documents, ideas, and written content. This
    method supports efficient enterprise content lifecycle management and
    governance by optimizing content size and maintaining high information
    quality.</trusted_answer>
  <tags>IMPORTANT, PRODUCT FOCUS, INFORM (WITHOUT EMOTION), SIMPLE (OVERVIEW),
    PROCESS, TECHNOLOGY</tags>
  ...
</ideablock>
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Check input format |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Check permissions/licensing |
| 429 | Rate Limited | Implement backoff |
| 500 | Server Error | Retry with backoff |

### Common Errors

#### Invalid API Key
```json
{
  "error": {
    "message": "Invalid API key provided",
    "type": "authentication_error",
    "code": "invalid_api_key"
  }
}
```

#### Token Limit Exceeded
```json
{
  "error": {
    "message": "Output exceeds max_tokens limit",
    "type": "invalid_request_error",
    "code": "max_tokens_exceeded"
  }
}
```

**Solution:** Reduce input chunk size or increase max_tokens

#### Invalid Model
```json
{
  "error": {
    "message": "Model 'invalid-model' not found",
    "type": "invalid_request_error",
    "code": "model_not_found"
  }
}
```

**Solution:** Use `ingest`, `distill`, or `technical-ingest`

---

## Rate Limits

| Plan | Requests/Minute | Requests/Day |
|------|-----------------|--------------|
| Free Tier | 10 | 100 |
| Starter | 60 | 1,000 |
| Professional | 300 | 10,000 |
| Enterprise | Custom | Custom |

### Handling Rate Limits

```python
import time
import requests

def call_blockify_with_retry(payload, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(
            'https://api.blockify.ai/v1/chat/completions',
            headers={
                'Authorization': 'Bearer YOUR_API_KEY',
                'Content-Type': 'application/json'
            },
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            response.raise_for_status()

    raise Exception("Max retries exceeded")
```

---

## SDK Examples

### Python

```python
import requests
import json

class BlockifyClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.blockify.ai/v1'

    def ingest(self, text, max_tokens=8000, temperature=0.5):
        """Convert raw text to IdeaBlocks."""
        return self._call('ingest', text, max_tokens, temperature)

    def distill(self, ideablocks_xml, max_tokens=8000, temperature=0.5):
        """Merge similar IdeaBlocks."""
        return self._call('distill', ideablocks_xml, max_tokens, temperature)

    def technical_ingest(self, structured_text, max_tokens=8000, temperature=0.5):
        """Process ordered technical content."""
        return self._call('technical-ingest', structured_text, max_tokens, temperature)

    def _call(self, model, content, max_tokens, temperature):
        response = requests.post(
            f'{self.base_url}/chat/completions',
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': model,
                'messages': [{'role': 'user', 'content': content}],
                'max_tokens': max_tokens,
                'temperature': temperature
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

# Usage
client = BlockifyClient('blk_your_api_key_here')

# Ingest raw text
ideablocks = client.ingest("""
    Your enterprise content here. This can be meeting transcripts,
    documentation, proposals, or any unstructured text.
""")
print(ideablocks)
```

### JavaScript/Node.js

```javascript
class BlockifyClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.blockify.ai/v1';
  }

  async ingest(text, maxTokens = 8000, temperature = 0.5) {
    return this._call('ingest', text, maxTokens, temperature);
  }

  async distill(ideablocksXml, maxTokens = 8000, temperature = 0.5) {
    return this._call('distill', ideablocksXml, maxTokens, temperature);
  }

  async technicalIngest(structuredText, maxTokens = 8000, temperature = 0.5) {
    return this._call('technical-ingest', structuredText, maxTokens, temperature);
  }

  async _call(model, content, maxTokens, temperature) {
    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model,
        messages: [{ role: 'user', content }],
        max_tokens: maxTokens,
        temperature
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  }
}

// Usage
const client = new BlockifyClient('blk_your_api_key_here');

async function processDocument() {
  const ideablocks = await client.ingest(`
    Your enterprise content here.
  `);
  console.log(ideablocks);
}
```

### cURL (Shell Script)

```bash
#!/bin/bash

API_KEY="blk_your_api_key_here"
CONTENT="Your text content to process"

curl -s -X POST "https://api.blockify.ai/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"ingest\",
    \"messages\": [{\"role\": \"user\", \"content\": \"$CONTENT\"}],
    \"max_tokens\": 8000,
    \"temperature\": 0.5
  }" | jq '.choices[0].message.content'
```

---

## Configuration Recommendations

### Optimal Settings by Use Case

| Use Case | Chunk Size | max_tokens | temperature |
|----------|------------|------------|-------------|
| General content | 2,000 chars | 8000 | 0.5 |
| Technical docs | 4,000 chars | 8000 | 0.5 |
| Meeting transcripts | 4,000 chars | 8000 | 0.5 |
| Short facts | 1,000 chars | 4000 | 0.5 |

### Token Budget

Each IdeaBlock outputs approximately **1,300 tokens**. Plan accordingly:

- 1 chunk (2,000 chars) = 2-5 IdeaBlocks = ~3,000-6,500 tokens
- Set max_tokens to at least 8,000 for safety margin

---

## Legal Notice

```
See https://iternal.ai/legal/legal-agreements-and-terms/blockify-eula/

- No training on outputs
- No reverse-engineering
- No derivatives
- No third-party disclosures without permission
```

---

*Document created: 2026-01-25*
*API Version: v1*
