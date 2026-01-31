#!/usr/bin/env python3
"""
Distill IdeaBlocks directly from/to ChromaDB using Blockify API.

This script performs distillation without requiring the Docker service,
using the Blockify distill API endpoint directly.

Usage:
    python distill_chromadb.py
    python distill_chromadb.py --threshold 0.7
    python distill_chromadb.py --dry-run

Environment:
    BLOCKIFY_API_KEY - Required for Blockify API
    OPENAI_API_KEY - Required for embeddings
    IDEABLOCK_DATA_DIR - Data directory (default: ./data/ideablocks)
"""

import os
import sys
import json
import re
import time
import hashlib
import argparse
from datetime import datetime
from difflib import SequenceMatcher

import requests
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# Configuration
BLOCKIFY_API_KEY = os.environ.get('BLOCKIFY_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
DATA_DIR = os.environ.get('IDEABLOCK_DATA_DIR', './data/ideablocks')
CHROMA_DIR = os.path.join(DATA_DIR, 'chroma_db')

API_URL = 'https://api.blockify.ai/v1/chat/completions'
EMBEDDING_MODEL = 'text-embedding-3-small'
EMBEDDING_BATCH_SIZE = 100


def log(message, level="INFO"):
    """Simple logging with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def get_chroma_client():
    """Get ChromaDB client."""
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


def export_blocks(collection):
    """Export all active blocks from ChromaDB."""
    log(f"Exporting blocks from {collection.name}...")

    results = collection.get(include=["metadatas", "documents"])

    blocks = []
    for i, doc_id in enumerate(results['ids']):
        meta = results['metadatas'][i]

        # Skip already distilled blocks
        if meta.get('distilled', False):
            continue

        blocks.append({
            'id': doc_id,
            'name': meta.get('name', ''),
            'critical_question': meta.get('critical_question', ''),
            'trusted_answer': meta.get('trusted_answer', ''),
            'tags': meta.get('tags', ''),
            'keywords': meta.get('keywords', ''),
            'entities': json.loads(meta.get('entities', '[]')),
            'source_document': meta.get('source_document', '')
        })

    log(f"Exported {len(blocks)} active blocks")
    return blocks


def similarity(a, b):
    """Calculate text similarity."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def cluster_within_groups(blocks, threshold=0.7):
    """Cluster blocks within the given list."""
    clusters = []
    used = set()

    for i, b1 in enumerate(blocks):
        if i in used:
            continue

        cluster = [b1]
        used.add(i)

        for j, b2 in enumerate(blocks):
            if j in used:
                continue

            sim = similarity(b1['trusted_answer'], b2['trusted_answer'])
            if sim >= threshold:
                cluster.append(b2)
                used.add(j)

        clusters.append(cluster)

    return clusters


def cluster_similar(blocks, threshold=0.7, global_pass=True):
    """Group similar blocks based on answer similarity.

    Two-pass approach:
    1. First pass: cluster within each source document (fast)
    2. Second pass: global clustering on representatives (cross-document dedup)
    """
    log(f"Clustering with threshold {threshold}...")

    # Pass 1: Group by source document and cluster within
    by_source = {}
    for block in blocks:
        source = block.get('source_document', 'unknown')
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(block)

    log(f"  Pass 1: Clustering within {len(by_source)} source documents...")

    doc_clusters = []
    for source, source_blocks in by_source.items():
        clusters = cluster_within_groups(source_blocks, threshold)
        doc_clusters.extend(clusters)

    log(f"  Pass 1 result: {len(doc_clusters)} clusters from within-document")

    if not global_pass:
        singles = sum(1 for c in doc_clusters if len(c) == 1)
        multis = sum(1 for c in doc_clusters if len(c) > 1)
        log(f"Found {len(doc_clusters)} clusters: {singles} unique, {multis} to merge")
        return doc_clusters

    # Pass 2: Global clustering using cluster representatives
    log(f"  Pass 2: Global cross-document clustering...")

    # Use first block of each cluster as representative
    representatives = []
    for i, cluster in enumerate(doc_clusters):
        rep = cluster[0].copy()
        rep['_cluster_idx'] = i
        representatives.append(rep)

    # Cluster representatives globally
    global_clusters = cluster_within_groups(representatives, threshold)

    # Merge original clusters based on global clustering
    final_clusters = []
    for global_cluster in global_clusters:
        merged = []
        for rep in global_cluster:
            original_cluster = doc_clusters[rep['_cluster_idx']]
            merged.extend(original_cluster)
        final_clusters.append(merged)

    singles = sum(1 for c in final_clusters if len(c) == 1)
    multis = sum(1 for c in final_clusters if len(c) > 1)
    log(f"  Pass 2 result: {len(final_clusters)} clusters after global merge")
    log(f"Found {len(final_clusters)} clusters: {singles} unique, {multis} to merge")

    return final_clusters


def block_to_xml(block):
    """Convert block to XML for distill API."""
    entities = ''
    for e in block.get('entities', []):
        entities += f'<entity><entity_name>{e.get("name", "")}</entity_name>'
        entities += f'<entity_type>{e.get("type", "")}</entity_type></entity>'

    return f'''<ideablock>
<name>{block["name"]}</name>
<critical_question>{block["critical_question"]}</critical_question>
<trusted_answer>{block["trusted_answer"]}</trusted_answer>
<tags>{block.get("tags", "")}</tags>
{entities}
<keywords>{block.get("keywords", "")}</keywords>
</ideablock>'''


def extract_field(xml, field):
    """Extract field from XML."""
    match = re.search(f'<{field}>(.*?)</{field}>', xml, re.DOTALL)
    return match.group(1).strip() if match else ''


def parse_distilled(content):
    """Parse distilled blocks from API response."""
    blocks_xml = re.findall(r'<ideablock>(.*?)</ideablock>', content, re.DOTALL)
    parsed = []

    for block in blocks_xml:
        name = extract_field(block, 'name')
        question = extract_field(block, 'critical_question')
        answer = extract_field(block, 'trusted_answer')

        if not all([name, question, answer]):
            continue

        # Generate ID from content
        content_hash = hashlib.sha256(f"{name}{question}{answer}".encode()).hexdigest()[:16]

        entities = []
        for entity in re.findall(r'<entity>(.*?)</entity>', block, re.DOTALL):
            entities.append({
                'name': extract_field(entity, 'entity_name'),
                'type': extract_field(entity, 'entity_type')
            })

        parsed.append({
            'id': f"distilled_{content_hash}",
            'name': name,
            'critical_question': question,
            'trusted_answer': answer,
            'tags': extract_field(block, 'tags'),
            'keywords': extract_field(block, 'keywords'),
            'entities': entities
        })

    return parsed


def call_distill_api(blocks_xml, retries=3):
    """Call Blockify Distill API."""
    for attempt in range(retries):
        try:
            response = requests.post(
                API_URL,
                headers={
                    'Authorization': f'Bearer {BLOCKIFY_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'distill',
                    'messages': [{'role': 'user', 'content': blocks_xml}],
                    'max_tokens': 8000,
                    'temperature': 0.5
                },
                timeout=90
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            elif response.status_code == 429:
                wait = 2 ** (attempt + 1)
                log(f"Rate limited, waiting {wait}s...", "WARNING")
                time.sleep(wait)
            else:
                log(f"API error {response.status_code}: {response.text[:200]}", "ERROR")
                return None
        except Exception as e:
            log(f"Exception: {e}", "ERROR")
            time.sleep(2)

    return None


def generate_embeddings(texts):
    """Generate embeddings using OpenAI."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    embeddings = []

    for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[i:i + EMBEDDING_BATCH_SIZE]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        embeddings.extend([item.embedding for item in response.data])

    return embeddings


def import_distilled(collection, blocks, source_ids):
    """Import distilled blocks to ChromaDB."""
    if not blocks:
        return 0

    log(f"Importing {len(blocks)} distilled blocks...")

    # Deduplicate blocks by ID (keep first occurrence)
    seen_ids = set()
    unique_blocks = []
    for block in blocks:
        if block['id'] not in seen_ids:
            seen_ids.add(block['id'])
            unique_blocks.append(block)

    if len(unique_blocks) < len(blocks):
        log(f"  Deduplicated: {len(blocks)} -> {len(unique_blocks)} blocks (removed {len(blocks) - len(unique_blocks)} duplicates)")

    ids = []
    documents = []
    metadatas = []
    timestamp = datetime.utcnow().isoformat()

    for block in unique_blocks:
        ids.append(block['id'])
        documents.append(f"{block['name']} {block['critical_question']} {block['trusted_answer']}")
        metadatas.append({
            'name': block['name'],
            'critical_question': block['critical_question'],
            'trusted_answer': block['trusted_answer'],
            'tags': block.get('tags', ''),
            'keywords': block.get('keywords', ''),
            'entities': json.dumps(block.get('entities', [])),
            'primary_entity': block['entities'][0]['name'] if block.get('entities') else '',
            'primary_entity_type': block['entities'][0]['type'] if block.get('entities') else '',
            'block_type': 'distilled',
            'source_blocks': json.dumps(source_ids),
            'source_count': len(source_ids),
            'created_at': timestamp
        })

    log(f"Generating embeddings...")
    embeddings = generate_embeddings(documents)

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return len(unique_blocks)


def mark_as_distilled(collection, block_ids):
    """Mark source blocks as distilled."""
    if not block_ids:
        return

    log(f"Marking {len(block_ids)} source blocks as distilled...")

    # Get existing data
    existing = collection.get(
        ids=list(block_ids),
        include=["metadatas", "documents", "embeddings"]
    )

    if not existing['ids']:
        return

    # Update metadata
    timestamp = datetime.utcnow().isoformat()
    updated_metas = []
    for meta in existing['metadatas']:
        updated = dict(meta)
        updated['distilled'] = True
        updated['distilled_at'] = timestamp
        updated_metas.append(updated)

    collection.upsert(
        ids=existing['ids'],
        metadatas=updated_metas,
        documents=existing['documents'],
        embeddings=existing['embeddings']
    )


def run_distillation(threshold=0.7, max_cluster_size=15, dry_run=False):
    """Run the full distillation pipeline."""
    log("=" * 60)
    log("BLOCKIFY DISTILLATION (Direct API)")
    log("=" * 60)
    log(f"Similarity threshold: {threshold}")
    log(f"Max cluster size: {max_cluster_size}")
    log(f"Dry run: {dry_run}")
    log("=" * 60)

    if not BLOCKIFY_API_KEY:
        log("BLOCKIFY_API_KEY not set", "ERROR")
        return False

    if not OPENAI_API_KEY:
        log("OPENAI_API_KEY not set", "ERROR")
        return False

    # Get ChromaDB collections
    client = get_chroma_client()
    raw_collection = get_collection(client, 'raw')
    distilled_collection = get_collection(client, 'distilled')

    log(f"Raw collection: {raw_collection.count()} blocks")
    log(f"Distilled collection: {distilled_collection.count()} blocks (before)")

    # Export active blocks
    blocks = export_blocks(raw_collection)
    if len(blocks) < 2:
        log("Need at least 2 blocks for distillation", "ERROR")
        return False

    # Cluster similar blocks
    clusters = cluster_similar(blocks, threshold)

    if dry_run:
        log("DRY RUN - stopping before API calls")
        return True

    # Process clusters
    distilled_blocks = []
    all_source_ids = set()

    for i, cluster in enumerate(clusters):
        if len(cluster) == 1:
            # Single block, copy as-is with new ID
            block = cluster[0]
            distilled_blocks.append({
                'id': f"distilled_{block['id'].replace('ib_', '')}",
                'name': block['name'],
                'critical_question': block['critical_question'],
                'trusted_answer': block['trusted_answer'],
                'tags': block.get('tags', ''),
                'keywords': block.get('keywords', ''),
                'entities': block.get('entities', [])
            })
            all_source_ids.add(block['id'])
        else:
            # Merge cluster via API
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Merging cluster {i+1}: {len(cluster)} blocks...", end=' ', flush=True)

            # Limit cluster size
            to_merge = cluster[:max_cluster_size]
            xml = ''.join([block_to_xml(b) for b in to_merge])

            result = call_distill_api(xml)
            if result:
                merged = parse_distilled(result)
                distilled_blocks.extend(merged)
                for b in to_merge:
                    all_source_ids.add(b['id'])
                print(f" -> {len(merged)} blocks")
            else:
                # Keep originals on failure
                for b in to_merge:
                    distilled_blocks.append({
                        'id': f"distilled_{b['id'].replace('ib_', '')}",
                        'name': b['name'],
                        'critical_question': b['critical_question'],
                        'trusted_answer': b['trusted_answer'],
                        'tags': b.get('tags', ''),
                        'keywords': b.get('keywords', ''),
                        'entities': b.get('entities', [])
                    })
                    all_source_ids.add(b['id'])
                print(" -> FAILED, keeping originals")

            time.sleep(0.5)  # Rate limiting

    # Import to distilled collection
    imported = import_distilled(distilled_collection, distilled_blocks, list(all_source_ids))

    # Mark source blocks as distilled
    mark_as_distilled(raw_collection, all_source_ids)

    # Final stats
    reduction = (1 - len(distilled_blocks) / len(blocks)) * 100

    log("=" * 60)
    log("DISTILLATION COMPLETE")
    log(f"  Input blocks: {len(blocks)}")
    log(f"  Output blocks: {len(distilled_blocks)}")
    log(f"  Reduction: {reduction:.1f}%")
    log(f"  Distilled collection: {distilled_collection.count()} blocks (after)")
    log("=" * 60)

    return True


def main():
    parser = argparse.ArgumentParser(description='Distill IdeaBlocks using Blockify API')
    parser.add_argument('--threshold', '-t', type=float, default=0.7,
                       help='Similarity threshold for clustering (default: 0.7)')
    parser.add_argument('--max-cluster', '-m', type=int, default=15,
                       help='Max blocks per distill call (default: 15)')
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='Cluster only, do not call API')

    args = parser.parse_args()

    success = run_distillation(
        threshold=args.threshold,
        max_cluster_size=args.max_cluster,
        dry_run=args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
