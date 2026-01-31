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
                wait = 2 ** attempt
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"Error {response.status_code}: {response.text[:100]}")
                return None
        except requests.exceptions.Timeout:
            print("  Timeout, retrying...")
            time.sleep(2)

    return None


def main():
    if not API_KEY:
        print("Error: BLOCKIFY_API_KEY environment variable not set")
        print("Set it with: export BLOCKIFY_API_KEY='blk_your_key_here'")
        sys.exit(1)

    if len(sys.argv) != 3:
        print("Usage: python blockify_ingest.py input.txt output.json")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    # Read and chunk
    print(f"Reading {input_path}...")
    with open(input_path, 'r') as f:
        text = f.read()

    print(f"  {len(text)} characters")

    chunks = chunk_text(text)
    print(f"  Split into {len(chunks)} chunks")

    # Process
    print("Processing chunks...")
    all_blocks = []
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}/{len(chunks)}...", end=' ')
        content = call_api(chunk)
        if content:
            blocks = parse_ideablocks(content)
            all_blocks.extend(blocks)
            print(f"{len(blocks)} IdeaBlocks")
        else:
            print("failed")
        time.sleep(0.5)

    # Save
    print(f"Saving to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(all_blocks, f, indent=2)

    print(f"Done! Generated {len(all_blocks)} IdeaBlocks")


if __name__ == '__main__':
    main()
