# Getting Started with Blockify: A Complete Guide

**Document Purpose:** Step-by-step instructions for engineers of any skill level to set up and use Blockify.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [Understanding the Response](#understanding-the-response)
4. [Processing Your First Document](#processing-your-first-document)
5. [Building a Processing Pipeline](#building-a-processing-pipeline)
6. [Storing IdeaBlocks](#storing-ideablocks)
7. [Building a Search System](#building-a-search-system)
8. [Integration with Claude Code](#integration-with-claude-code)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

---

## Prerequisites

### Required

- [ ] API key from [console.blockify.ai](https://console.blockify.ai)
- [ ] cURL or any HTTP client (Python, Node.js, etc.)
- [ ] Text content to process

### Optional (for Full Pipeline)

- [ ] Python 3.8+ or Node.js 16+
- [ ] Vector database account (Pinecone, Milvus, etc.)
- [ ] OpenAI API key (for embeddings)

---

## Quick Start (5 Minutes)

### Step 1: Get Your API Key

1. Go to [console.blockify.ai](https://console.blockify.ai)
2. Create an account or sign in
3. Navigate to "API Keys"
4. Click "Generate New Key"
5. Copy and save your key (format: `blk_xxxx...`)

### Step 2: Test the API

Open your terminal and run:

```bash
curl --location 'https://api.blockify.ai/v1/chat/completions' \
--header 'Authorization: Bearer YOUR_API_KEY_HERE' \
--header 'Content-Type: application/json' \
--data '{
    "model": "ingest",
    "messages": [{"role": "user", "content": "Blockify is a data optimization tool that transforms messy unstructured text into structured IdeaBlocks. It improves LLM accuracy by 78X while reducing data size to 2.5% of the original."}],
    "max_tokens": 8000,
    "temperature": 0.5
}'
```

### Step 3: Verify Success

You should receive a response like:

```json
{
  "id": "oUjtbqw-...",
  "object": "chat.completion",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "<ideablock>...</ideablock>"
    }
  }],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 300,
    "total_tokens": 350
  }
}
```

**Congratulations!** You've successfully called the Blockify API.

---

## Understanding the Response

### Response Structure

```json
{
  "id": "unique-request-id",
  "object": "chat.completion",
  "created": 1769366850,
  "choices": [{
    "finish_reason": "stop",
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "<ideablock>...</ideablock><ideablock>...</ideablock>"
    }
  }],
  "usage": {
    "prompt_tokens": 97,      // Input tokens
    "completion_tokens": 416,  // Output tokens
    "total_tokens": 513        // Total
  }
}
```

### Extracting IdeaBlocks

The `content` field contains XML IdeaBlocks. Example:

```xml
<ideablock>
  <name>Blockify Overview</name>
  <critical_question>What is Blockify?</critical_question>
  <trusted_answer>Blockify is a data optimization tool that transforms
    messy unstructured text into structured IdeaBlocks.</trusted_answer>
  <tags>IMPORTANT, PRODUCT FOCUS, TECHNOLOGY</tags>
  <entity>
    <entity_name>BLOCKIFY</entity_name>
    <entity_type>PRODUCT</entity_type>
  </entity>
  <keywords>Blockify, data optimization, IdeaBlocks</keywords>
</ideablock>
```

### Parsing IdeaBlocks (Python)

```python
import re
import json

def parse_ideablocks(content):
    """Extract all IdeaBlocks from API response content."""
    pattern = r'<ideablock>(.*?)</ideablock>'
    blocks = re.findall(pattern, content, re.DOTALL)

    parsed = []
    for block in blocks:
        parsed.append({
            'name': extract_field(block, 'name'),
            'critical_question': extract_field(block, 'critical_question'),
            'trusted_answer': extract_field(block, 'trusted_answer'),
            'tags': extract_field(block, 'tags').split(', '),
            'keywords': extract_field(block, 'keywords').split(', ')
        })
    return parsed

def extract_field(xml, field):
    """Extract a single field from XML."""
    match = re.search(f'<{field}>(.*?)</{field}>', xml, re.DOTALL)
    return match.group(1).strip() if match else ''

# Usage
content = response['choices'][0]['message']['content']
ideablocks = parse_ideablocks(content)
print(json.dumps(ideablocks, indent=2))
```

---

## Processing Your First Document

### Step 1: Prepare Your Document

```python
# Read your document
with open('my-document.txt', 'r') as f:
    document_text = f.read()

print(f"Document length: {len(document_text)} characters")
```

### Step 2: Chunk the Document

```python
def chunk_text(text, chunk_size=2000, overlap=200):
    """
    Split text into chunks at sentence boundaries.

    Args:
        text: The full document text
        chunk_size: Target characters per chunk (default 2000)
        overlap: Characters to overlap between chunks (default 200)

    Returns:
        List of text chunks
    """
    # Split into sentences (simple approach)
    sentences = text.replace('\n', ' ').split('. ')

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip() + '. '
        sentence_length = len(sentence)

        if current_length + sentence_length > chunk_size and current_chunk:
            # Save current chunk
            chunks.append(''.join(current_chunk))

            # Start new chunk with overlap
            overlap_text = ''.join(current_chunk)[-overlap:]
            current_chunk = [overlap_text, sentence]
            current_length = len(overlap_text) + sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(''.join(current_chunk))

    return chunks

# Usage
chunks = chunk_text(document_text)
print(f"Created {len(chunks)} chunks")
```

### Step 3: Process Each Chunk

```python
import requests
import time

def process_chunk(chunk, api_key):
    """Send a chunk to Blockify and get IdeaBlocks."""
    response = requests.post(
        'https://api.blockify.ai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'ingest',
            'messages': [{'role': 'user', 'content': chunk}],
            'max_tokens': 8000,
            'temperature': 0.5
        }
    )

    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        return parse_ideablocks(content)
    elif response.status_code == 429:
        # Rate limited - wait and retry
        time.sleep(2)
        return process_chunk(chunk, api_key)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Process all chunks
API_KEY = 'blk_your_key_here'
all_ideablocks = []

for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i+1}/{len(chunks)}...")
    ideablocks = process_chunk(chunk, API_KEY)
    all_ideablocks.extend(ideablocks)
    time.sleep(0.5)  # Be nice to the API

print(f"Generated {len(all_ideablocks)} IdeaBlocks")
```

### Step 4: Save Results

```python
import json

# Save as JSON
with open('ideablocks.json', 'w') as f:
    json.dump(all_ideablocks, f, indent=2)

print("IdeaBlocks saved to ideablocks.json")
```

---

## Building a Processing Pipeline

### Complete Pipeline Script

```python
#!/usr/bin/env python3
"""
Blockify Document Processing Pipeline

Usage:
    python blockify_pipeline.py input.txt output.json

Requirements:
    pip install requests
"""

import sys
import json
import re
import time
import requests
from pathlib import Path

# Configuration
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with env var in production
CHUNK_SIZE = 2000
OVERLAP = 200
RATE_LIMIT_DELAY = 0.5

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Split text into overlapping chunks at sentence boundaries."""
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence += '. '

        if current_length + len(sentence) > chunk_size and current_chunk:
            chunks.append(''.join(current_chunk))
            overlap_text = ''.join(current_chunk)[-overlap:]
            current_chunk = [overlap_text, sentence]
            current_length = len(overlap_text) + len(sentence)
        else:
            current_chunk.append(sentence)
            current_length += len(sentence)

    if current_chunk:
        chunks.append(''.join(current_chunk))

    return chunks

def extract_field(xml, field):
    """Extract a field from XML."""
    match = re.search(f'<{field}>(.*?)</{field}>', xml, re.DOTALL)
    return match.group(1).strip() if match else ''

def parse_ideablocks(content):
    """Parse IdeaBlocks from API response."""
    pattern = r'<ideablock>(.*?)</ideablock>'
    blocks = re.findall(pattern, content, re.DOTALL)

    parsed = []
    for block in blocks:
        # Extract entities
        entities = []
        entity_pattern = r'<entity>(.*?)</entity>'
        for entity_xml in re.findall(entity_pattern, block, re.DOTALL):
            entities.append({
                'name': extract_field(entity_xml, 'entity_name'),
                'type': extract_field(entity_xml, 'entity_type')
            })

        parsed.append({
            'name': extract_field(block, 'name'),
            'critical_question': extract_field(block, 'critical_question'),
            'trusted_answer': extract_field(block, 'trusted_answer'),
            'tags': [t.strip() for t in extract_field(block, 'tags').split(',')],
            'entities': entities,
            'keywords': [k.strip() for k in extract_field(block, 'keywords').split(',')]
        })
    return parsed

def call_blockify(chunk, max_retries=3):
    """Call Blockify API with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'https://api.blockify.ai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'ingest',
                    'messages': [{'role': 'user', 'content': chunk}],
                    'max_tokens': 8000,
                    'temperature': 0.5
                },
                timeout=60
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            elif response.status_code == 429:
                wait = 2 ** attempt
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  Error {response.status_code}: {response.text[:100]}")
                return None

        except requests.exceptions.Timeout:
            print(f"  Timeout, retrying...")
            time.sleep(2)

    return None

def process_document(input_path, output_path):
    """Process a document through Blockify."""
    # Read input
    print(f"Reading {input_path}...")
    text = Path(input_path).read_text()
    print(f"  {len(text)} characters")

    # Chunk
    print("Chunking...")
    chunks = chunk_text(text)
    print(f"  {len(chunks)} chunks")

    # Process
    print("Processing chunks...")
    all_ideablocks = []
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}/{len(chunks)}...", end=' ')
        content = call_blockify(chunk)
        if content:
            ideablocks = parse_ideablocks(content)
            all_ideablocks.extend(ideablocks)
            print(f"{len(ideablocks)} IdeaBlocks")
        else:
            print("failed")
        time.sleep(RATE_LIMIT_DELAY)

    # Save output
    print(f"Saving to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(all_ideablocks, f, indent=2)

    print(f"Done! Generated {len(all_ideablocks)} IdeaBlocks")
    return all_ideablocks

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python blockify_pipeline.py input.txt output.json")
        sys.exit(1)

    process_document(sys.argv[1], sys.argv[2])
```

### Usage

```bash
# Set your API key
export BLOCKIFY_API_KEY="blk_your_key_here"

# Edit the script to use os.environ.get('BLOCKIFY_API_KEY')

# Run the pipeline
python blockify_pipeline.py my-document.txt ideablocks.json
```

---

## Storing IdeaBlocks

### Option 1: Local JSON File

Simple, good for prototyping:

```python
# Save
with open('ideablocks.json', 'w') as f:
    json.dump(ideablocks, f, indent=2)

# Load
with open('ideablocks.json', 'r') as f:
    ideablocks = json.load(f)

# Search (simple)
def search(query, ideablocks):
    query_lower = query.lower()
    results = []
    for ib in ideablocks:
        text = f"{ib['name']} {ib['trusted_answer']} {' '.join(ib['keywords'])}"
        if query_lower in text.lower():
            results.append(ib)
    return results
```

### Option 2: SQLite (Local Database)

Good for larger datasets with structured queries:

```python
import sqlite3
import json

# Create database
conn = sqlite3.connect('ideablocks.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS ideablocks (
    id INTEGER PRIMARY KEY,
    name TEXT,
    critical_question TEXT,
    trusted_answer TEXT,
    tags TEXT,
    keywords TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Insert IdeaBlocks
for ib in ideablocks:
    cursor.execute('''
    INSERT INTO ideablocks (name, critical_question, trusted_answer, tags, keywords)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        ib['name'],
        ib['critical_question'],
        ib['trusted_answer'],
        json.dumps(ib['tags']),
        json.dumps(ib['keywords'])
    ))

conn.commit()

# Search
def search_db(query):
    cursor.execute('''
    SELECT * FROM ideablocks
    WHERE name LIKE ? OR trusted_answer LIKE ? OR keywords LIKE ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    return cursor.fetchall()
```

### Option 3: Vector Database (Production)

For semantic search, use a vector database. Example with Pinecone:

```python
import pinecone
import openai

# Initialize
pinecone.init(api_key="PINECONE_API_KEY", environment="us-west1-gcp")
index = pinecone.Index("blockify-ideablocks")
openai.api_key = "OPENAI_API_KEY"

def embed(text):
    """Generate embedding using OpenAI."""
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# Insert IdeaBlocks with embeddings
for i, ib in enumerate(ideablocks):
    text = f"{ib['name']} {ib['critical_question']} {ib['trusted_answer']}"
    embedding = embed(text)

    index.upsert(vectors=[{
        "id": f"ib_{i}",
        "values": embedding,
        "metadata": {
            "name": ib['name'],
            "question": ib['critical_question'],
            "answer": ib['trusted_answer']
        }
    }])

# Semantic search
def semantic_search(query, k=5):
    query_embedding = embed(query)
    results = index.query(vector=query_embedding, top_k=k, include_metadata=True)
    return results['matches']
```

---

## Building a Search System

### Simple RAG Example

```python
import openai

def answer_question(question, ideablocks, k=3):
    """Answer a question using IdeaBlocks as context."""

    # 1. Find relevant IdeaBlocks (using semantic search)
    relevant = semantic_search(question, k=k)

    # 2. Build context
    context = "\n\n".join([
        f"[{r['metadata']['name']}]\n"
        f"Q: {r['metadata']['question']}\n"
        f"A: {r['metadata']['answer']}"
        for r in relevant
    ])

    # 3. Generate answer
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": f"""You are a helpful assistant. Answer questions using only the following knowledge base:

{context}

If the answer isn't in the knowledge base, say "I don't have that information."
"""
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response.choices[0].message.content

# Usage
answer = answer_question("What is Blockify?", ideablocks)
print(answer)
```

---

## Integration with Claude Code

### Method 1: CLAUDE.md Knowledge File

Add processed IdeaBlocks to your project's CLAUDE.md:

```markdown
# CLAUDE.md

## Project Knowledge Base

The following IdeaBlocks contain key project information:

### Product Overview
**Q: What is our main product?**
A: Our main product is a data optimization platform that improves
   AI accuracy by 78X.

### Technical Architecture
**Q: What database do we use?**
A: We use Cloudflare D1 for structured data and Cloudflare KV
   for key-value storage.

[Add more IdeaBlocks as needed]
```

### Method 2: Claude Code Skill

Create a skill that can process and search IdeaBlocks. See `CLAUDE-CODE-BLOCKIFY-SKILL.md` for the full implementation.

### Method 3: MCP Server

For advanced integration, create an MCP server that provides semantic search. See `ARCHITECTURE-END-TO-END.md` for details.

---

## Troubleshooting

### Common Issues

#### Issue: Empty or truncated output

**Cause:** `max_tokens` too low

**Solution:** Increase to 8000+

```json
{
  "max_tokens": 8000
}
```

#### Issue: Nonsensical or repeating IdeaBlocks

**Cause:** Temperature too high or too low

**Solution:** Use 0.5

```json
{
  "temperature": 0.5
}
```

#### Issue: Rate limit errors (429)

**Cause:** Too many requests

**Solution:** Add delay between requests

```python
import time
time.sleep(0.5)  # Wait 500ms between requests
```

#### Issue: No IdeaBlocks generated

**Cause:** Input text is too short or lacks factual content

**Solution:**
- Ensure chunks are 1000-4000 characters
- Text should contain facts, not just marketing fluff
- Check that input is actual text, not just whitespace

#### Issue: API key not working

**Cause:** Invalid or expired key

**Solution:**
- Check key format: `blk_xxxx...`
- Generate a new key at console.blockify.ai
- Ensure no extra spaces in the key

### Debug Checklist

- [ ] API key is valid and correctly formatted
- [ ] Content-Type header is `application/json`
- [ ] Model is one of: `ingest`, `distill`, `technical-ingest`
- [ ] max_tokens is at least 4000
- [ ] temperature is 0.5
- [ ] Input text is 1000-4000 characters
- [ ] Input text contains factual content

---

## Next Steps

### 1. Scale Your Pipeline

- Add parallel processing for faster ingestion
- Implement batch embedding generation
- Set up automated document syncing

### 2. Improve Search Quality

- Add hybrid search (vector + BM25)
- Implement reranking
- Build a knowledge graph for entity relationships

### 3. Build Applications

- Create a chatbot using IdeaBlocks
- Build a search interface
- Integrate with existing tools

### 4. Governance

- Set up regular IdeaBlock review cycles
- Implement access controls
- Track usage and accuracy metrics

### Documentation Links

- [Deep Dive](./BLOCKIFY-DEEP-DIVE.md) - Understanding Blockify
- [API Reference](./BLOCKIFY-API-REFERENCE.md) - Complete API docs
- [Architecture](./ARCHITECTURE-END-TO-END.md) - System design
- [Claude Code Skill](./CLAUDE-CODE-BLOCKIFY-SKILL.md) - Claude integration

---

*Document created: 2026-01-25*
*Difficulty level: Beginner to Intermediate*
