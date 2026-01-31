# Claude Code Blockify Skill

**Document Purpose:** Complete skill implementation for Claude Code to process documents with Blockify and search optimized knowledge bases.

---

## Overview

This skill enables Claude Code to:
1. Process documents through the Blockify API
2. Convert raw text to structured IdeaBlocks
3. Search existing IdeaBlock knowledge bases
4. Integrate Blockify-optimized knowledge into coding workflows

---

## Skill Location

```
skills/blockify-integration/
├── SKILL.md                 # Main skill file (copy content below)
├── scripts/
│   ├── blockify_ingest.py   # Process documents
│   ├── blockify_distill.py  # Merge similar blocks
│   └── blockify_search.py   # Search knowledge base
└── references/
    ├── API.md               # Quick API reference
    └── SCHEMA.md            # IdeaBlock schema
```

---

## SKILL.md Content

Copy this to `skills/blockify-integration/SKILL.md`:

```markdown
---
name: blockify-integration
description: >-
  Process documents with Blockify API to create optimized IdeaBlocks for RAG.
  Use when processing documentation, creating knowledge bases, or improving
  AI context retrieval. Supports ingest, distill, and search operations.
---

# Blockify Integration Skill

Process documents through Blockify to create optimized IdeaBlocks for RAG systems.

## Quick Start

### Process a Document

```bash
python {baseDir}/scripts/blockify_ingest.py input.txt output.json
```

### Search Knowledge Base

```bash
python {baseDir}/scripts/blockify_search.py "your query" ideablocks.json
```

## API Reference

### Ingest (Raw Text → IdeaBlocks)

```bash
curl -X POST https://api.blockify.ai/v1/chat/completions \
  -H "Authorization: Bearer $BLOCKIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ingest",
    "messages": [{"role": "user", "content": "YOUR_TEXT_HERE"}],
    "max_tokens": 8000,
    "temperature": 0.5
  }'
```

### Distill (Merge Similar IdeaBlocks)

```bash
curl -X POST https://api.blockify.ai/v1/chat/completions \
  -H "Authorization: Bearer $BLOCKIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "distill",
    "messages": [{"role": "user", "content": "<ideablock>...</ideablock>"}],
    "max_tokens": 8000,
    "temperature": 0.5
  }'
```

## Configuration

### Required Environment Variables

```bash
export BLOCKIFY_API_KEY="blk_your_key_here"
```

### Optimal Settings

| Parameter | Value | Notes |
|-----------|-------|-------|
| model | ingest / distill | Use ingest for raw text |
| max_tokens | 8000 | Minimum recommended |
| temperature | 0.5 | Don't change |
| chunk_size | 2000 chars | For input chunking |

## IdeaBlock Structure

Each IdeaBlock contains:

```xml
<ideablock>
  <name>Title</name>
  <critical_question>What question does this answer?</critical_question>
  <trusted_answer>The validated answer (2-3 sentences).</trusted_answer>
  <tags>TAG1, TAG2</tags>
  <entity>
    <entity_name>ENTITY</entity_name>
    <entity_type>TYPE</entity_type>
  </entity>
  <keywords>keyword1, keyword2</keywords>
</ideablock>
```

## Common Workflows

### 1. Process Project Documentation

```bash
# Chunk all markdown files
find docs/ -name "*.md" -exec cat {} \; > all_docs.txt

# Process through Blockify
python {baseDir}/scripts/blockify_ingest.py all_docs.txt project_kb.json
```

### 2. Create CLAUDE.md Knowledge Section

After processing, add key IdeaBlocks to CLAUDE.md:

```markdown
## Project Knowledge Base

[Paste relevant IdeaBlocks here in Q&A format]
```

### 3. Search Before Coding

```bash
# Find relevant context before implementing
python {baseDir}/scripts/blockify_search.py "authentication flow" project_kb.json
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 429 Rate Limit | Too many requests | Wait 2s, retry |
| Empty output | max_tokens too low | Increase to 8000+ |
| Truncated blocks | Large input | Reduce chunk size |

## See Also

- [API.md](references/API.md) - Full API documentation
- [SCHEMA.md](references/SCHEMA.md) - IdeaBlock schema details
```

---

## Script: blockify_ingest.py

```python
#!/usr/bin/env python3
"""
Process documents through Blockify Ingest API.

Usage:
    python blockify_ingest.py input.txt output.json

Environment:
    BLOCKIFY_API_KEY - Your Blockify API key
"""

import os
import sys
import json
import re
import time
import requests

API_KEY = os.environ.get('BLOCKIFY_API_KEY')
API_URL = 'https://api.blockify.ai/v1/chat/completions'
CHUNK_SIZE = 2000
OVERLAP = 200


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Split text into overlapping chunks at sentence boundaries."""
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current = []
    length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence += '. '

        if length + len(sentence) > chunk_size and current:
            chunks.append(''.join(current))
            overlap_text = ''.join(current)[-overlap:]
            current = [overlap_text, sentence]
            length = len(overlap_text) + len(sentence)
        else:
            current.append(sentence)
            length += len(sentence)

    if current:
        chunks.append(''.join(current))

    return chunks


def extract_field(xml, field):
    """Extract field from XML."""
    match = re.search(f'<{field}>(.*?)</{field}>', xml, re.DOTALL)
    return match.group(1).strip() if match else ''


def parse_ideablocks(content):
    """Parse IdeaBlocks from API response."""
    blocks = re.findall(r'<ideablock>(.*?)</ideablock>', content, re.DOTALL)
    parsed = []

    for block in blocks:
        entities = []
        for entity in re.findall(r'<entity>(.*?)</entity>', block, re.DOTALL):
            entities.append({
                'name': extract_field(entity, 'entity_name'),
                'type': extract_field(entity, 'entity_type')
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


def call_api(chunk, retries=3):
    """Call Blockify API with retry logic."""
    for attempt in range(retries):
        try:
            response = requests.post(
                API_URL,
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
                time.sleep(2 ** attempt)
            else:
                print(f"Error {response.status_code}: {response.text[:100]}")
                return None
        except requests.exceptions.Timeout:
            time.sleep(2)

    return None


def main():
    if not API_KEY:
        print("Error: BLOCKIFY_API_KEY not set")
        sys.exit(1)

    if len(sys.argv) != 3:
        print("Usage: python blockify_ingest.py input.txt output.json")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    # Read and chunk
    with open(input_path, 'r') as f:
        text = f.read()

    chunks = chunk_text(text)
    print(f"Processing {len(chunks)} chunks...")

    # Process
    all_blocks = []
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}/{len(chunks)}...", end=' ')
        content = call_api(chunk)
        if content:
            blocks = parse_ideablocks(content)
            all_blocks.extend(blocks)
            print(f"{len(blocks)} blocks")
        else:
            print("failed")
        time.sleep(0.5)

    # Save
    with open(output_path, 'w') as f:
        json.dump(all_blocks, f, indent=2)

    print(f"Done! {len(all_blocks)} IdeaBlocks saved to {output_path}")


if __name__ == '__main__':
    main()
```

---

## Script: blockify_search.py

```python
#!/usr/bin/env python3
"""
Search IdeaBlocks knowledge base.

Usage:
    python blockify_search.py "query" ideablocks.json

For semantic search, set OPENAI_API_KEY for embeddings.
"""

import sys
import json
from difflib import SequenceMatcher


def similarity(a, b):
    """Calculate text similarity."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def search(query, ideablocks, top_k=5):
    """Search IdeaBlocks by text similarity."""
    scored = []

    for ib in ideablocks:
        # Combine searchable text
        text = f"{ib['name']} {ib['critical_question']} {ib['trusted_answer']}"
        text += ' ' + ' '.join(ib.get('keywords', []))

        # Calculate score
        score = similarity(query, text)

        # Boost if query appears in question or name
        if query.lower() in ib['critical_question'].lower():
            score += 0.3
        if query.lower() in ib['name'].lower():
            score += 0.2

        scored.append((score, ib))

    # Sort by score
    scored.sort(key=lambda x: x[0], reverse=True)

    return scored[:top_k]


def main():
    if len(sys.argv) != 3:
        print("Usage: python blockify_search.py 'query' ideablocks.json")
        sys.exit(1)

    query = sys.argv[1]
    kb_path = sys.argv[2]

    with open(kb_path, 'r') as f:
        ideablocks = json.load(f)

    results = search(query, ideablocks)

    print(f"\nSearch: '{query}'\n")
    print("=" * 60)

    for score, ib in results:
        print(f"\n[{ib['name']}] (score: {score:.2f})")
        print(f"Q: {ib['critical_question']}")
        print(f"A: {ib['trusted_answer']}")
        print("-" * 40)


if __name__ == '__main__':
    main()
```

---

## Script: blockify_distill.py

```python
#!/usr/bin/env python3
"""
Merge similar IdeaBlocks using Blockify Distill API.

Usage:
    python blockify_distill.py ideablocks.json distilled.json

Environment:
    BLOCKIFY_API_KEY - Your Blockify API key
"""

import os
import sys
import json
import re
import time
import requests
from difflib import SequenceMatcher

API_KEY = os.environ.get('BLOCKIFY_API_KEY')
API_URL = 'https://api.blockify.ai/v1/chat/completions'
SIMILARITY_THRESHOLD = 0.7


def similarity(a, b):
    """Calculate text similarity."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def cluster_similar(ideablocks, threshold=SIMILARITY_THRESHOLD):
    """Group similar IdeaBlocks."""
    clusters = []
    used = set()

    for i, ib1 in enumerate(ideablocks):
        if i in used:
            continue

        cluster = [ib1]
        used.add(i)

        for j, ib2 in enumerate(ideablocks):
            if j in used:
                continue

            sim = similarity(ib1['trusted_answer'], ib2['trusted_answer'])
            if sim >= threshold:
                cluster.append(ib2)
                used.add(j)

        clusters.append(cluster)

    return clusters


def ideablock_to_xml(ib):
    """Convert IdeaBlock dict to XML."""
    entities = ''.join([
        f'<entity><entity_name>{e["name"]}</entity_name>'
        f'<entity_type>{e["type"]}</entity_type></entity>'
        for e in ib.get('entities', [])
    ])

    return f'''<ideablock>
<name>{ib["name"]}</name>
<critical_question>{ib["critical_question"]}</critical_question>
<trusted_answer>{ib["trusted_answer"]}</trusted_answer>
<tags>{", ".join(ib.get("tags", []))}</tags>
{entities}
<keywords>{", ".join(ib.get("keywords", []))}</keywords>
</ideablock>'''


def call_distill(ideablocks_xml):
    """Call Blockify Distill API."""
    response = requests.post(
        API_URL,
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'distill',
            'messages': [{'role': 'user', 'content': ideablocks_xml}],
            'max_tokens': 8000,
            'temperature': 0.5
        },
        timeout=60
    )

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return None


def extract_field(xml, field):
    match = re.search(f'<{field}>(.*?)</{field}>', xml, re.DOTALL)
    return match.group(1).strip() if match else ''


def parse_ideablocks(content):
    """Parse distilled IdeaBlocks."""
    blocks = re.findall(r'<ideablock>(.*?)</ideablock>', content, re.DOTALL)
    parsed = []

    for block in blocks:
        entities = []
        for entity in re.findall(r'<entity>(.*?)</entity>', block, re.DOTALL):
            entities.append({
                'name': extract_field(entity, 'entity_name'),
                'type': extract_field(entity, 'entity_type')
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


def main():
    if not API_KEY:
        print("Error: BLOCKIFY_API_KEY not set")
        sys.exit(1)

    if len(sys.argv) != 3:
        print("Usage: python blockify_distill.py ideablocks.json distilled.json")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, 'r') as f:
        ideablocks = json.load(f)

    print(f"Loaded {len(ideablocks)} IdeaBlocks")

    # Cluster similar blocks
    clusters = cluster_similar(ideablocks)
    print(f"Found {len(clusters)} clusters")

    # Distill clusters with 2+ blocks
    distilled = []
    for i, cluster in enumerate(clusters):
        if len(cluster) == 1:
            distilled.append(cluster[0])
        else:
            print(f"  Distilling cluster {i+1} ({len(cluster)} blocks)...")
            xml = ''.join([ideablock_to_xml(ib) for ib in cluster[:15]])
            result = call_distill(xml)
            if result:
                distilled.extend(parse_ideablocks(result))
            else:
                distilled.extend(cluster)  # Keep originals on failure
            time.sleep(0.5)

    # Save
    with open(output_path, 'w') as f:
        json.dump(distilled, f, indent=2)

    print(f"Done! {len(distilled)} distilled IdeaBlocks saved")
    print(f"Reduction: {len(ideablocks)} → {len(distilled)} "
          f"({100 - (len(distilled)/len(ideablocks)*100):.1f}% reduction)")


if __name__ == '__main__':
    main()
```

---

## Installation

### 1. Create Skill Directory

```bash
mkdir -p skills/blockify-integration/scripts
mkdir -p skills/blockify-integration/references
```

### 2. Copy Files

Copy the SKILL.md content to `skills/blockify-integration/SKILL.md`

Copy scripts to `skills/blockify-integration/scripts/`

### 3. Set Environment Variable

```bash
export BLOCKIFY_API_KEY="blk_your_key_here"
```

### 4. Install Dependencies

```bash
pip install requests
```

---

## Usage Examples

### Process Project Docs

```bash
# Combine all docs
cat docs/*.md > all_docs.txt

# Process through Blockify
python skills/blockify-integration/scripts/blockify_ingest.py all_docs.txt kb.json

# Search the knowledge base
python skills/blockify-integration/scripts/blockify_search.py "API endpoints" kb.json
```

### Reduce Duplication

```bash
# After initial ingest, distill to remove duplicates
python skills/blockify-integration/scripts/blockify_distill.py kb.json kb_distilled.json
```

---

*Document created: 2026-01-25*
*Skill version: 1.0*
