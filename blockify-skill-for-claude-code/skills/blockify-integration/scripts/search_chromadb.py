#!/usr/bin/env python3
"""
Search IdeaBlocks in ChromaDB vector database.

Usage:
    python search_chromadb.py "your query"
    python search_chromadb.py "your query" --collection raw
    python search_chromadb.py "your query" --entity PRODUCT
    python search_chromadb.py "your query" --active-only

Environment:
    IDEABLOCK_DATA_DIR - Path to data directory (default: ./data/ideablocks)
    OPENAI_API_KEY - Required for semantic search
"""

import os
import sys
import argparse
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# Configuration
DATA_DIR = os.environ.get('IDEABLOCK_DATA_DIR', './data/ideablocks')
CHROMA_DIR = os.path.join(DATA_DIR, 'chroma_db')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
EMBEDDING_MODEL = 'text-embedding-3-small'


def get_query_embedding(query: str):
    """Generate embedding for query using OpenAI."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set - required for semantic search")
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    return response.data[0].embedding


def get_client():
    """Get ChromaDB client."""
    return chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False)
    )


def get_best_collection(client, preferred='distilled'):
    """Get the best available collection with fallback.

    Args:
        client: ChromaDB client
        preferred: Preferred collection ('distilled' or 'raw')

    Returns:
        tuple: (collection, collection_name)
    """
    collections = {c.name: c for c in client.list_collections()}

    # Try preferred collection first
    preferred_name = f"{preferred}_ideablocks"
    if preferred_name in collections:
        col = collections[preferred_name]
        if col.count() > 0:
            return col, preferred_name

    # Fallback to other collection
    fallback = 'raw' if preferred == 'distilled' else 'distilled'
    fallback_name = f"{fallback}_ideablocks"
    if fallback_name in collections:
        col = collections[fallback_name]
        if col.count() > 0:
            print(f"Note: {preferred_name} empty/missing, using {fallback_name}")
            return col, fallback_name

    # No collections with data
    if collections:
        print(f"Available collections (all empty): {list(collections.keys())}")
    else:
        print("No collections found. Run ingest first.")

    return None, None


def get_collection(client, name):
    """Get collection by name."""
    try:
        return client.get_collection(name)
    except Exception:
        return None


def search_collection(
    query: str,
    collection,
    n_results: int = 10,
    entity_filter: str = None,
    tag_filter: str = None,
    active_only: bool = False
):
    """
    Search IdeaBlocks with optional filters.

    Args:
        query: Natural language search query
        collection: ChromaDB collection
        n_results: Number of results to return
        entity_filter: Filter by primary entity type (e.g., PRODUCT)
        tag_filter: Filter by tag (e.g., IMPORTANT)
        active_only: If True, exclude distilled (inactive) blocks
    """
    # Build where clause
    conditions = []

    if entity_filter:
        conditions.append({'primary_entity_type': {'$eq': entity_filter.upper()}})

    if tag_filter:
        conditions.append({'tags': {'$contains': tag_filter.upper()}})

    if active_only:
        conditions.append({
            '$or': [
                {'distilled': {'$eq': False}},
                {'distilled': {'$exists': False}}
            ]
        })

    where = None
    if conditions:
        where = {'$and': conditions} if len(conditions) > 1 else conditions[0]

    # Generate query embedding using OpenAI (same model as ingestion)
    query_embedding = get_query_embedding(query)

    # Execute search
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=['documents', 'metadatas', 'distances']
        )
    except Exception as e:
        # Fallback without where clause if it fails
        print(f"Warning: Filter failed ({e}), searching without filters")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )

    return results


def format_results(results, query, collection_name):
    """Format and display search results."""

    if not results['ids'][0]:
        print(f"\nNo results found for: '{query}'")
        return []

    print(f"\n{'='*70}")
    print(f"Search: '{query}'")
    print(f"Collection: {collection_name}")
    print(f"Found: {len(results['ids'][0])} results")
    print(f"{'='*70}")

    formatted = []
    for i, doc_id in enumerate(results['ids'][0]):
        meta = results['metadatas'][0][i]
        distance = results['distances'][0][i]

        # Convert distance to similarity score
        similarity = max(0, 1 - distance) if distance <= 1 else 1 / (1 + distance)

        result = {
            'id': doc_id,
            'name': meta.get('name', 'Unnamed'),
            'critical_question': meta.get('critical_question', 'N/A'),
            'trusted_answer': meta.get('trusted_answer', 'N/A'),
            'similarity': similarity,
            'metadata': meta
        }
        formatted.append(result)

        print(f"\n[{i+1}] {result['name']}")
        print(f"    Score: {similarity:.3f}")
        print(f"    Q: {result['critical_question']}")

        # Truncate long answers
        answer = result['trusted_answer']
        if len(answer) > 200:
            answer = answer[:200] + "..."
        print(f"    A: {answer}")

        if meta.get('primary_entity'):
            print(f"    Entity: {meta['primary_entity']} ({meta.get('primary_entity_type', 'N/A')})")

        if meta.get('tags'):
            tags = meta['tags'].split(',')[:5]
            print(f"    Tags: {', '.join(tags)}")

        if meta.get('distilled'):
            print(f"    Status: DISTILLED (inactive)")
        elif meta.get('block_type') == 'distilled':
            print(f"    Status: MERGED from {meta.get('source_count', '?')} blocks")

        print(f"    {'-'*50}")

    return formatted


def main():
    parser = argparse.ArgumentParser(description='Search IdeaBlocks in ChromaDB')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--collection', '-c', default='auto',
                       choices=['auto', 'raw', 'distilled'],
                       help='Collection to search (default: auto = distilled with fallback)')
    parser.add_argument('--limit', '-n', type=int, default=10,
                       help='Number of results (default: 10)')
    parser.add_argument('--entity', '-e', type=str,
                       help='Filter by entity type (PRODUCT, ORGANIZATION, etc.)')
    parser.add_argument('--tags', '-t', type=str,
                       help='Filter by tag (IMPORTANT, TECHNOLOGY, etc.)')
    parser.add_argument('--active-only', '-a', action='store_true',
                       help='Exclude blocks that have been distilled (raw collection only)')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output results as JSON')

    args = parser.parse_args()

    # Check data directory exists
    if not os.path.exists(CHROMA_DIR):
        print(f"ChromaDB not found at {CHROMA_DIR}")
        print("Initialize with: python ingest_to_chromadb.py <input>")
        print("Or set IDEABLOCK_DATA_DIR environment variable")
        sys.exit(1)

    # Get client
    client = get_client()

    # Get collection
    if args.collection == 'auto':
        collection, collection_name = get_best_collection(client, 'distilled')
    else:
        collection_name = f"{args.collection}_ideablocks"
        collection = get_collection(client, collection_name)

    if collection is None:
        print(f"No collection available")
        sys.exit(1)

    print(f"Searching {collection_name} ({collection.count()} blocks)...")

    # Execute search
    results = search_collection(
        query=args.query,
        collection=collection,
        n_results=args.limit,
        entity_filter=args.entity,
        tag_filter=args.tags,
        active_only=args.active_only
    )

    # Display results
    if args.json:
        import json
        formatted = []
        for i, doc_id in enumerate(results['ids'][0]):
            meta = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            similarity = max(0, 1 - distance) if distance <= 1 else 1 / (1 + distance)
            formatted.append({
                'id': doc_id,
                'similarity': similarity,
                'name': meta.get('name'),
                'critical_question': meta.get('critical_question'),
                'trusted_answer': meta.get('trusted_answer'),
                'metadata': meta
            })
        print(json.dumps(formatted, indent=2))
    else:
        format_results(results, args.query, collection_name)


if __name__ == '__main__':
    main()
