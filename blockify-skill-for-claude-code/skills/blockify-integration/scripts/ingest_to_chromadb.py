#!/usr/bin/env python3
"""
Ingest documents through Blockify API directly to ChromaDB.

Usage:
    python ingest_to_chromadb.py input.txt
    python ingest_to_chromadb.py input.txt --collection raw
    python ingest_to_chromadb.py docs/ --batch
    python ingest_to_chromadb.py docs/ --batch --parallel 10
    python ingest_to_chromadb.py docs/ --batch --sequential

Options:
    --parallel, -p N    Number of parallel workers (default: 5)
    --sequential, -s    Force sequential processing (disable parallelization)

Environment:
    BLOCKIFY_API_KEY - Required for Blockify API
    OPENAI_API_KEY - Required for embeddings
    IDEABLOCK_DATA_DIR - Data directory (default: ./data/ideablocks)
    BLOCKIFY_PARALLEL_WORKERS - Default parallel workers (default: 5)
"""

import os
import sys
import re
import json
import time
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import requests
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# Configuration
BLOCKIFY_API_KEY = os.environ.get('BLOCKIFY_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
DATA_DIR = os.environ.get('IDEABLOCK_DATA_DIR', './data/ideablocks')
CHROMA_DIR = os.path.join(DATA_DIR, 'chroma_db')

CHUNK_SIZE = 2000
OVERLAP = 200
EMBEDDING_MODEL = 'text-embedding-3-small'
EMBEDDING_BATCH_SIZE = 100
PARALLEL_WORKERS = int(os.environ.get('BLOCKIFY_PARALLEL_WORKERS', '5'))

# Thread-safe print lock
_print_lock = threading.Lock()


def safe_print(*args, **kwargs):
    """Thread-safe print function."""
    with _print_lock:
        print(*args, **kwargs)


def get_chroma_client():
    """Get ChromaDB client."""
    os.makedirs(CHROMA_DIR, exist_ok=True)
    return chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False)
    )


def get_collection(client, collection_type='raw'):
    """Get or create collection."""
    name = f"{collection_type}_ideablocks"
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Split text into overlapping chunks.

    Returns:
        List of dicts with 'text', 'index', and 'hash' keys for benchmark tracking.
    """
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
            chunk_text_content = ''.join(current)
            chunks.append({
                'text': chunk_text_content,
                'index': len(chunks),
                'hash': hashlib.sha256(chunk_text_content.encode()).hexdigest()[:16]
            })
            overlap_text = ''.join(current)[-overlap:]
            current = [overlap_text, sentence]
            length = len(overlap_text) + len(sentence)
        else:
            current.append(sentence)
            length += len(sentence)

    if current:
        chunk_text_content = ''.join(current)
        chunks.append({
            'text': chunk_text_content,
            'index': len(chunks),
            'hash': hashlib.sha256(chunk_text_content.encode()).hexdigest()[:16]
        })

    return chunks


def call_blockify(chunk, retries=3):
    """Call Blockify Ingest API."""
    for attempt in range(retries):
        try:
            response = requests.post(
                'https://api.blockify.ai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {BLOCKIFY_API_KEY}',
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
                safe_print(f"    Error {response.status_code}")
                return None
        except Exception as e:
            safe_print(f"    Exception: {e}")
            time.sleep(2)

    return None


def extract_field(xml, field):
    """Extract field from XML."""
    match = re.search(f'<{field}>(.*?)</{field}>', xml, re.DOTALL)
    return match.group(1).strip() if match else ''


def parse_ideablocks(content, source_chunk=None):
    """Parse IdeaBlocks from API response.

    Args:
        content: XML content from Blockify API
        source_chunk: Optional dict with 'text', 'index', 'hash' from chunk_text()
                     Used for benchmark tracking

    Returns:
        List of parsed IdeaBlock dicts with source chunk metadata
    """
    blocks = re.findall(r'<ideablock>(.*?)</ideablock>', content, re.DOTALL)
    parsed = []

    for block in blocks:
        name = extract_field(block, 'name')
        question = extract_field(block, 'critical_question')
        answer = extract_field(block, 'trusted_answer')

        if not all([name, question, answer]):
            continue

        # Generate stable ID
        content_hash = hashlib.sha256(f"{name}{question}{answer}".encode()).hexdigest()[:16]

        # Extract entities
        entities = []
        for entity in re.findall(r'<entity>(.*?)</entity>', block, re.DOTALL):
            entities.append({
                'name': extract_field(entity, 'entity_name'),
                'type': extract_field(entity, 'entity_type')
            })

        block_data = {
            'id': f"ib_{content_hash}",
            'name': name,
            'critical_question': question,
            'trusted_answer': answer,
            'tags': extract_field(block, 'tags'),
            'keywords': extract_field(block, 'keywords'),
            'entities': entities,
            'primary_entity': entities[0]['name'] if entities else '',
            'primary_entity_type': entities[0]['type'] if entities else ''
        }

        # Add source chunk metadata for benchmark tracking
        if source_chunk:
            block_data['source_chunk_text'] = source_chunk['text']
            block_data['source_chunk_index'] = source_chunk['index']
            block_data['source_chunk_hash'] = source_chunk['hash']

        parsed.append(block_data)

    return parsed


def generate_embeddings(texts):
    """Generate embeddings using OpenAI."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    embeddings = []

    for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[i:i + EMBEDDING_BATCH_SIZE]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        embeddings.extend([item.embedding for item in response.data])

    return embeddings


def ingest_to_collection(blocks, collection, source_document, use_safe_print=False):
    """Ingest parsed blocks to ChromaDB.

    Args:
        blocks: List of parsed IdeaBlock dicts (may include source_chunk_* fields)
        collection: ChromaDB collection to ingest into
        source_document: Source document filename
        use_safe_print: Use thread-safe printing

    Returns:
        Number of blocks ingested
    """
    _print = safe_print if use_safe_print else print
    if not blocks:
        return 0

    # Deduplicate blocks by ID (keep first occurrence)
    seen_ids = set()
    unique_blocks = []
    for block in blocks:
        if block['id'] not in seen_ids:
            seen_ids.add(block['id'])
            unique_blocks.append(block)

    if len(unique_blocks) < len(blocks):
        _print(f"    Deduplicated: {len(blocks)} -> {len(unique_blocks)} blocks")

    blocks = unique_blocks

    ids = []
    documents = []
    metadatas = []
    timestamp = datetime.utcnow().isoformat()

    for block in blocks:
        ids.append(block['id'])
        documents.append(f"{block['name']} {block['critical_question']} {block['trusted_answer']}")

        metadata = {
            'name': block['name'],
            'critical_question': block['critical_question'],
            'trusted_answer': block['trusted_answer'],
            'tags': block['tags'],
            'keywords': block['keywords'],
            'entities': json.dumps(block['entities']),
            'primary_entity': block['primary_entity'],
            'primary_entity_type': block['primary_entity_type'],
            'source_document': source_document,
            'block_type': 'raw',
            'distilled': False,
            'created_at': timestamp
        }

        # Add source chunk metadata for benchmark tracking (if available)
        if 'source_chunk_text' in block:
            metadata['source_chunk_text'] = block['source_chunk_text']
            metadata['source_chunk_index'] = block['source_chunk_index']
            metadata['source_chunk_hash'] = block['source_chunk_hash']

        metadatas.append(metadata)

    # Generate embeddings
    _print(f"    Generating embeddings for {len(documents)} blocks...")
    embeddings = generate_embeddings(documents)

    # Upsert to collection
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return len(blocks)


def process_file(filepath, collection, parallel=False):
    """Process a single file through Blockify to ChromaDB.

    Args:
        filepath: Path to the file to process
        collection: ChromaDB collection to ingest into
        parallel: If True, use thread-safe printing

    Returns:
        Number of blocks ingested
    """
    _print = safe_print if parallel else print
    _print(f"Processing {filepath}...")

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    _print(f"  [{os.path.basename(filepath)}] {len(text)} characters")

    chunks = chunk_text(text)
    _print(f"  [{os.path.basename(filepath)}] Split into {len(chunks)} chunks")

    all_blocks = []
    for i, chunk in enumerate(chunks):
        _print(f"  [{os.path.basename(filepath)}] Chunk {i+1}/{len(chunks)}...", end=' ')
        # Pass the chunk text (not dict) to Blockify API
        content = call_blockify(chunk['text'])
        if content:
            # Pass source chunk info for benchmark tracking
            blocks = parse_ideablocks(content, source_chunk=chunk)
            all_blocks.extend(blocks)
            _print(f"{len(blocks)} blocks")
        else:
            _print("failed")
        time.sleep(0.5)

    if all_blocks:
        source = os.path.basename(filepath)
        count = ingest_to_collection(all_blocks, collection, source, use_safe_print=parallel)
        _print(f"  [{os.path.basename(filepath)}] Ingested {count} blocks to ChromaDB")
        return count

    return 0


def main():
    parser = argparse.ArgumentParser(description='Ingest documents to ChromaDB via Blockify')
    parser.add_argument('input', help='File or directory to process')
    parser.add_argument('--collection', '-c', default='raw',
                       choices=['raw', 'distilled'],
                       help='Target collection (default: raw)')
    parser.add_argument('--batch', '-b', action='store_true',
                       help='Process directory of files')
    parser.add_argument('--parallel', '-p', type=int, default=PARALLEL_WORKERS,
                       metavar='N',
                       help=f'Number of parallel workers (default: {PARALLEL_WORKERS}, set via BLOCKIFY_PARALLEL_WORKERS env var)')
    parser.add_argument('--sequential', '-s', action='store_true',
                       help='Force sequential processing (disable parallelization)')

    args = parser.parse_args()

    # Validate environment
    if not BLOCKIFY_API_KEY:
        print("Error: BLOCKIFY_API_KEY not set")
        sys.exit(1)
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not set")
        sys.exit(1)

    # Initialize ChromaDB
    client = get_chroma_client()
    collection = get_collection(client, args.collection)

    print(f"Target: {collection.name} ({collection.count()} existing blocks)")

    # Process files
    total = 0
    if args.batch or os.path.isdir(args.input):
        # Collect all files to process
        filepaths = []
        for filepath in Path(args.input).glob('**/*.txt'):
            filepaths.append(str(filepath))
        for filepath in Path(args.input).glob('**/*.md'):
            filepaths.append(str(filepath))

        if not filepaths:
            print("No .txt or .md files found")
            sys.exit(0)

        num_workers = 1 if args.sequential else args.parallel
        print(f"Found {len(filepaths)} files to process with {num_workers} worker(s)")

        if num_workers > 1:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = {
                    executor.submit(process_file, fp, collection, True): fp
                    for fp in filepaths
                }
                for future in as_completed(futures):
                    filepath = futures[future]
                    try:
                        result = future.result()
                        total += result
                    except Exception as e:
                        safe_print(f"Error processing {filepath}: {e}")
        else:
            # Sequential processing
            for filepath in filepaths:
                total += process_file(filepath, collection, parallel=False)
    else:
        total = process_file(args.input, collection, parallel=False)

    print(f"\n{'='*50}")
    print(f"Total: {total} blocks ingested")
    print(f"Collection now has {collection.count()} blocks")


if __name__ == '__main__':
    main()
