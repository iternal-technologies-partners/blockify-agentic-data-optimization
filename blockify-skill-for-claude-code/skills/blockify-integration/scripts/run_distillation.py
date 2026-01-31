#!/usr/bin/env python3
"""
Automated distillation pipeline: ChromaDB -> Distillation Service -> ChromaDB

This script bridges the local ChromaDB vector database with the distillation
service, enabling fully autonomous deduplication without human intervention.

Pipeline:
1. Export active (non-distilled) blocks from raw_ideablocks
2. Submit to distillation service
3. Poll for completion
4. Import merged blocks to distilled_ideablocks
5. Mark source blocks as "distilled" in raw_ideablocks (inactive)

Usage:
    python run_distillation.py
    python run_distillation.py --threshold 0.60
    python run_distillation.py --service-url http://distill.example.com:8315
    python run_distillation.py --dry-run

Environment:
    OPENAI_API_KEY - Required for embeddings
    BLOCKIFY_API_KEY - Required for distillation service
    DISTILL_SERVICE_URL - Distillation service URL (default: http://localhost:8315)
    IDEABLOCK_DATA_DIR - Data directory (default: ./data/ideablocks)
"""

import os
import sys
import json
import time
import uuid
import argparse
from datetime import datetime
from pathlib import Path

import requests
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
BLOCKIFY_API_KEY = os.environ.get('BLOCKIFY_API_KEY')
DISTILL_SERVICE_URL = os.environ.get('DISTILL_SERVICE_URL', 'http://localhost:8315')
DATA_DIR = os.environ.get('IDEABLOCK_DATA_DIR', './data/ideablocks')
CHROMA_DIR = os.path.join(DATA_DIR, 'chroma_db')

EMBEDDING_MODEL = 'text-embedding-3-small'
EMBEDDING_BATCH_SIZE = 100
POLL_INTERVAL = 5  # seconds
MAX_POLL_TIME = 7200  # 2 hours max


def log(message, level="INFO"):
    """Simple logging with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


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


def export_blocks_from_chromadb(collection, limit=None, only_active=True):
    """Export blocks from ChromaDB in distillation service format.

    Args:
        collection: ChromaDB collection
        limit: Max blocks to export
        only_active: If True, skip blocks already marked as distilled
    """
    log(f"Exporting blocks from {collection.name}...")

    count = collection.count()
    if count == 0:
        log("No blocks found in collection", "WARNING")
        return []

    log(f"Found {count} total blocks in collection")

    # Fetch all blocks
    fetch_limit = limit if limit else count

    # Build where clause to filter out already-distilled blocks
    where = None
    if only_active:
        where = {
            "$or": [
                {"distilled": {"$eq": False}},
                {"distilled": {"$exists": False}}
            ]
        }

    try:
        results = collection.get(
            limit=fetch_limit,
            where=where,
            include=["metadatas", "documents"]
        )
    except Exception:
        # Fallback if where clause fails (older ChromaDB versions)
        results = collection.get(
            limit=fetch_limit,
            include=["metadatas", "documents"]
        )
        # Filter manually
        if only_active:
            filtered_ids = []
            filtered_metas = []
            filtered_docs = []
            for i, meta in enumerate(results['metadatas']):
                if not meta.get('distilled', False):
                    filtered_ids.append(results['ids'][i])
                    filtered_metas.append(meta)
                    if results.get('documents'):
                        filtered_docs.append(results['documents'][i])
            results = {
                'ids': filtered_ids,
                'metadatas': filtered_metas,
                'documents': filtered_docs if filtered_docs else None
            }

    blocks = []
    for i, doc_id in enumerate(results['ids']):
        metadata = results['metadatas'][i]

        # Skip if already distilled
        if only_active and metadata.get('distilled', False):
            continue

        block = {
            "type": "blockify",
            "blockifyResultUUID": doc_id,
            "blockifiedTextResult": {
                "name": metadata.get('name', ''),
                "criticalQuestion": metadata.get('critical_question', ''),
                "trustedAnswer": metadata.get('trusted_answer', '')
            },
            "hidden": False,
            "exported": False,
            "reviewed": False
        }

        if metadata.get('source_document'):
            block["blockifyDocumentUUID"] = metadata.get('source_document')

        blocks.append(block)

    log(f"Exported {len(blocks)} active blocks (skipped {count - len(blocks)} already distilled)")
    return blocks


def check_service_health(service_url):
    """Check if distillation service is healthy."""
    try:
        response = requests.get(f"{service_url}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - is the service running?"
    except Exception as e:
        return False, str(e)


def submit_distillation_job(service_url, blocks, similarity, iterations):
    """Submit distillation job to service."""
    log(f"Submitting {len(blocks)} blocks to distillation service...")

    task_uuid = str(uuid.uuid4())

    payload = {
        "blockifyTaskUUID": task_uuid,
        "similarity": similarity,
        "iterations": iterations,
        "results": blocks
    }

    try:
        response = requests.post(
            f"{service_url}/api/autoDistill",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        job_id = data.get('jobId')
        log(f"Job submitted successfully: {job_id}")
        return job_id, task_uuid

    except requests.exceptions.RequestException as e:
        log(f"Failed to submit job: {e}", "ERROR")
        return None, None


def poll_job_status(service_url, job_id, max_time=MAX_POLL_TIME):
    """Poll for job completion."""
    log(f"Polling for job completion (max {max_time}s)...")

    start_time = time.time()
    last_progress = None

    while time.time() - start_time < max_time:
        try:
            response = requests.get(
                f"{service_url}/api/jobs/{job_id}",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            status = data.get('status')

            if status == 'running' and 'progress' in data:
                progress = data['progress']
                progress_str = f"{progress.get('percent', 0):.1f}% - {progress.get('phase', 'unknown')}"
                if progress_str != last_progress:
                    log(f"Progress: {progress_str}")
                    last_progress = progress_str

            if status == 'success':
                log("Job completed successfully!")
                return data
            elif status == 'failure':
                log(f"Job failed: {data.get('error', 'Unknown error')}", "ERROR")
                if data.get('intermediate_result'):
                    log("Intermediate results available", "WARNING")
                    return data
                return None
            elif status == 'timeout':
                log("Job timed out", "ERROR")
                if data.get('intermediate_result'):
                    log("Intermediate results available", "WARNING")
                    return data
                return None

            time.sleep(POLL_INTERVAL)

        except requests.exceptions.RequestException as e:
            log(f"Poll error: {e}", "WARNING")
            time.sleep(POLL_INTERVAL * 2)

    log(f"Max poll time ({max_time}s) exceeded", "ERROR")
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


def mark_source_blocks_as_distilled(collection, source_block_ids, distill_task_uuid):
    """Mark source blocks as distilled in the raw collection.

    This prevents them from being re-processed in future distillation runs.
    """
    if not source_block_ids:
        return 0

    log(f"Marking {len(source_block_ids)} source blocks as distilled...")

    timestamp = datetime.utcnow().isoformat()

    # Get existing blocks to preserve their data
    existing = collection.get(
        ids=list(source_block_ids),
        include=["metadatas", "documents", "embeddings"]
    )

    if not existing['ids']:
        log("No matching blocks found to mark", "WARNING")
        return 0

    # Update metadata to mark as distilled
    updated_metadatas = []
    for meta in existing['metadatas']:
        updated_meta = dict(meta)
        updated_meta['distilled'] = True
        updated_meta['distilled_at'] = timestamp
        updated_meta['distill_task'] = distill_task_uuid
        updated_metadatas.append(updated_meta)

    # Upsert with updated metadata
    collection.upsert(
        ids=existing['ids'],
        metadatas=updated_metadatas,
        documents=existing['documents'] if existing.get('documents') else None,
        embeddings=existing['embeddings'] if existing.get('embeddings') else None
    )

    log(f"Marked {len(existing['ids'])} blocks as distilled")
    return len(existing['ids'])


def import_results_to_chromadb(collection, results, source_task_uuid):
    """Import distillation results to ChromaDB."""
    merged_blocks = [
        r for r in results
        if r.get('type') == 'merged' and not r.get('hidden', False)
    ]

    if not merged_blocks:
        log("No merged blocks to import", "WARNING")
        return 0, set()

    log(f"Importing {len(merged_blocks)} merged blocks to ChromaDB...")

    ids = []
    documents = []
    metadatas = []
    all_source_ids = set()
    timestamp = datetime.utcnow().isoformat()

    for block in merged_blocks:
        result = block.get('blockifiedTextResult', {})
        name = result.get('name', '')
        question = result.get('criticalQuestion', '')
        answer = result.get('trustedAnswer', '')

        source_ids = block.get('blockifyResultsUsed', [])
        all_source_ids.update(source_ids)

        ids.append(block.get('blockifyResultUUID', str(uuid.uuid4())))
        documents.append(f"{name} {question} {answer}")
        metadatas.append({
            'name': name,
            'critical_question': question,
            'trusted_answer': answer,
            'block_type': 'distilled',
            'source_task': source_task_uuid,
            'source_blocks': json.dumps(source_ids),
            'source_count': len(source_ids),
            'created_at': timestamp
        })

    log(f"Generating embeddings for {len(documents)} blocks...")
    embeddings = generate_embeddings(documents)

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    log(f"Imported {len(ids)} blocks to {collection.name}")
    return len(ids), all_source_ids


def save_results_to_file(results, stats, output_dir):
    """Save results to JSON file for backup."""
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"distillation_results_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'stats': stats,
            'results': results
        }, f, indent=2)

    log(f"Results saved to {filepath}")
    return filepath


def run_distillation(
    service_url=DISTILL_SERVICE_URL,
    similarity=0.55,
    iterations=4,
    source_collection='raw',
    target_collection='distilled',
    limit=None,
    dry_run=False,
    save_backup=True,
    mark_inactive=True,
    process_all=False
):
    """Run the full distillation pipeline.

    Args:
        service_url: Distillation service URL
        similarity: Similarity threshold (0.0-1.0)
        iterations: Number of clustering iterations
        source_collection: Source collection name (raw/distilled)
        target_collection: Target collection name (raw/distilled)
        limit: Max blocks to process
        dry_run: If True, export only without submitting
        save_backup: Save results to JSON file
        mark_inactive: Mark source blocks as distilled
        process_all: If True, process all blocks including already-distilled
    """
    log("=" * 60)
    log("BLOCKIFY DISTILLATION PIPELINE")
    log("=" * 60)
    log(f"Service URL: {service_url}")
    log(f"Similarity threshold: {similarity}")
    log(f"Iterations: {iterations}")
    log(f"Source: {source_collection}_ideablocks")
    log(f"Target: {target_collection}_ideablocks")
    log(f"Process all: {process_all} (includes already-distilled)")
    log(f"Mark inactive: {mark_inactive}")
    log("=" * 60)

    if not OPENAI_API_KEY:
        log("OPENAI_API_KEY not set", "ERROR")
        return False

    if not dry_run and not BLOCKIFY_API_KEY:
        log("BLOCKIFY_API_KEY not set (required for distillation service)", "ERROR")
        return False

    if not dry_run:
        healthy, info = check_service_health(service_url)
        if not healthy:
            log(f"Distillation service not available: {info}", "ERROR")
            log("Start the service with: docker-compose up -d")
            return False
        log(f"Service healthy: {info}")

    # Initialize ChromaDB
    client = get_chroma_client()
    source = get_collection(client, source_collection)
    target = get_collection(client, target_collection)

    log(f"Source collection: {source.count()} blocks")
    log(f"Target collection: {target.count()} blocks (before)")

    # Export blocks (only active unless process_all)
    blocks = export_blocks_from_chromadb(source, limit, only_active=not process_all)
    if not blocks:
        log("No blocks to process", "ERROR")
        return False

    if len(blocks) < 2:
        log("Need at least 2 blocks for distillation", "ERROR")
        return False

    if dry_run:
        log("DRY RUN - skipping submission")
        output_dir = os.path.join(DATA_DIR, 'exports')
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_dir, f"export_{timestamp}.json")
        with open(filepath, 'w') as f:
            json.dump(blocks, f, indent=2)
        log(f"Exported {len(blocks)} blocks to {filepath}")
        return True

    # Submit job
    job_id, task_uuid = submit_distillation_job(
        service_url, blocks, similarity, iterations
    )
    if not job_id:
        return False

    # Poll for completion
    result = poll_job_status(service_url, job_id)
    if not result:
        return False

    results = result.get('results', [])
    stats = result.get('stats', {})

    log("=" * 60)
    log("DISTILLATION STATS")
    log(f"  Starting blocks: {stats.get('startingBlockCount', 'N/A')}")
    log(f"  Final blocks: {stats.get('finalBlockCount', 'N/A')}")
    log(f"  Reduction: {stats.get('blockReductionPercent', 'N/A')}%")
    log("=" * 60)

    if save_backup:
        backup_dir = os.path.join(DATA_DIR, 'distillation_results')
        save_results_to_file(results, stats, backup_dir)

    # Import merged blocks and get source IDs
    imported, source_ids = import_results_to_chromadb(target, results, task_uuid)

    # Mark source blocks as distilled (inactive)
    if mark_inactive and source_ids:
        mark_source_blocks_as_distilled(source, source_ids, task_uuid)

    log("=" * 60)
    log("PIPELINE COMPLETE")
    log(f"  Source: {source.count()} blocks ({len(source_ids)} now marked as distilled)")
    log(f"  Target: {target.count()} blocks (after)")
    log(f"  Imported: {imported} merged blocks")
    log("=" * 60)

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Run distillation pipeline: ChromaDB -> Service -> ChromaDB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Basic distillation with defaults
  %(prog)s --threshold 0.60         # Higher similarity threshold
  %(prog)s --iterations 6           # More iterations
  %(prog)s --limit 1000             # Process first 1000 blocks only
  %(prog)s --dry-run                # Export only, don't submit
  %(prog)s --process-all            # Include already-distilled blocks
  %(prog)s --no-mark-inactive       # Don't mark source blocks as distilled

Environment Variables:
  OPENAI_API_KEY      - Required for embeddings
  BLOCKIFY_API_KEY    - Required for distillation service
  DISTILL_SERVICE_URL - Service URL (default: http://localhost:8315)
  IDEABLOCK_DATA_DIR  - Data directory (default: ./data/ideablocks)
        """
    )

    parser.add_argument('--service-url', '-u', default=DISTILL_SERVICE_URL,
                       help='Distillation service URL')
    parser.add_argument('--threshold', '-t', type=float, default=0.55,
                       help='Similarity threshold (0.0-1.0, default: 0.55)')
    parser.add_argument('--iterations', '-i', type=int, default=4,
                       help='Number of iterations (default: 4)')
    parser.add_argument('--source', '-s', default='raw',
                       choices=['raw', 'distilled'],
                       help='Source collection (default: raw)')
    parser.add_argument('--target', '-T', default='distilled',
                       choices=['raw', 'distilled'],
                       help='Target collection (default: distilled)')
    parser.add_argument('--limit', '-l', type=int, default=None,
                       help='Limit number of blocks to process')
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='Export only, do not submit to service')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip saving results backup')
    parser.add_argument('--no-mark-inactive', action='store_true',
                       help='Do not mark source blocks as distilled')
    parser.add_argument('--process-all', action='store_true',
                       help='Process all blocks including already-distilled')

    args = parser.parse_args()

    success = run_distillation(
        service_url=args.service_url,
        similarity=args.threshold,
        iterations=args.iterations,
        source_collection=args.source,
        target_collection=args.target,
        limit=args.limit,
        dry_run=args.dry_run,
        save_backup=not args.no_backup,
        mark_inactive=not args.no_mark_inactive,
        process_all=args.process_all
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
