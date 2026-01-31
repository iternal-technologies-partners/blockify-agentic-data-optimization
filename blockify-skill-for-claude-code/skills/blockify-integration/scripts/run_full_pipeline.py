#!/usr/bin/env python3
"""
Full autonomous pipeline: Folder -> Blockify -> ChromaDB -> Distillation -> Benchmark -> Search-ready

This script runs the entire knowledge base pipeline without human intervention:
1. Ingests documents from a folder via Blockify API (parallel by default)
2. Stores raw IdeaBlocks in ChromaDB
3. Runs distillation to deduplicate (if service available)
4. Marks source blocks as inactive
5. Stores distilled blocks in ChromaDB
6. Runs benchmark comparing IdeaBlocks vs traditional chunking
7. Generates HTML performance report
8. Reports final statistics

Usage:
    python run_full_pipeline.py /path/to/documents/
    python run_full_pipeline.py /path/to/docs/ --no-distill
    python run_full_pipeline.py /path/to/docs/ --threshold 0.60
    python run_full_pipeline.py /path/to/docs/ --parallel 10
    python run_full_pipeline.py /path/to/docs/ --sequential

Environment:
    BLOCKIFY_API_KEY - Required for Blockify API and distillation
    OPENAI_API_KEY - Required for embeddings
    DISTILL_SERVICE_URL - Distillation service URL (default: http://localhost:8315)
    IDEABLOCK_DATA_DIR - Data directory (default: ./data/ideablocks)
    BLOCKIFY_PARALLEL_WORKERS - Default parallel workers (default: 5)
"""

import os
import sys
import re
import json
import time
import uuid
import hashlib
import argparse
import threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# Configuration
BLOCKIFY_API_KEY = os.environ.get('BLOCKIFY_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
DISTILL_SERVICE_URL = os.environ.get('DISTILL_SERVICE_URL', 'http://localhost:8315')
DATA_DIR = os.environ.get('IDEABLOCK_DATA_DIR', './data/ideablocks')
CHROMA_DIR = os.path.join(DATA_DIR, 'chroma_db')

CHUNK_SIZE = 2000
OVERLAP = 200
EMBEDDING_MODEL = 'text-embedding-3-small'
EMBEDDING_BATCH_SIZE = 100
POLL_INTERVAL = 5
MAX_POLL_TIME = 7200
PARALLEL_WORKERS = int(os.environ.get('BLOCKIFY_PARALLEL_WORKERS', '5'))

# Thread-safe logging
_log_lock = threading.Lock()


def log(message, level="INFO"):
    """Thread-safe logging with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _log_lock:
        print(f"[{timestamp}] [{level}] {message}")


# =============================================================================
# ChromaDB Functions
# =============================================================================

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


# =============================================================================
# Ingestion Functions
# =============================================================================

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Split text into overlapping chunks."""
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
                log(f"Blockify API error: {response.status_code}", "WARNING")
                return None
        except Exception as e:
            log(f"Blockify API exception: {e}", "WARNING")
            time.sleep(2)

    return None


def extract_field(xml, field):
    """Extract field from XML."""
    match = re.search(f'<{field}>(.*?)</{field}>', xml, re.DOTALL)
    return match.group(1).strip() if match else ''


def parse_ideablocks(content):
    """Parse IdeaBlocks from API response."""
    blocks = re.findall(r'<ideablock>(.*?)</ideablock>', content, re.DOTALL)
    parsed = []

    for block in blocks:
        name = extract_field(block, 'name')
        question = extract_field(block, 'critical_question')
        answer = extract_field(block, 'trusted_answer')

        if not all([name, question, answer]):
            continue

        content_hash = hashlib.sha256(f"{name}{question}{answer}".encode()).hexdigest()[:16]

        entities = []
        for entity in re.findall(r'<entity>(.*?)</entity>', block, re.DOTALL):
            entities.append({
                'name': extract_field(entity, 'entity_name'),
                'type': extract_field(entity, 'entity_type')
            })

        parsed.append({
            'id': f"ib_{content_hash}",
            'name': name,
            'critical_question': question,
            'trusted_answer': answer,
            'tags': extract_field(block, 'tags'),
            'keywords': extract_field(block, 'keywords'),
            'entities': entities,
            'primary_entity': entities[0]['name'] if entities else '',
            'primary_entity_type': entities[0]['type'] if entities else ''
        })

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


def ingest_blocks_to_collection(blocks, collection, source_document):
    """Ingest parsed blocks to ChromaDB."""
    if not blocks:
        return 0

    ids = []
    documents = []
    metadatas = []
    timestamp = datetime.utcnow().isoformat()

    for block in blocks:
        ids.append(block['id'])
        documents.append(f"{block['name']} {block['critical_question']} {block['trusted_answer']}")
        metadatas.append({
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
        })

    log(f"Generating embeddings for {len(documents)} blocks...")
    embeddings = generate_embeddings(documents)

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
        parallel: If True, include filename prefix in logs for clarity
    """
    filename = os.path.basename(filepath)
    prefix = f"[{filename}] " if parallel else ""

    log(f"{prefix}Processing {filepath}...")

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    log(f"{prefix}{len(text)} characters")

    chunks = chunk_text(text)
    log(f"{prefix}Split into {len(chunks)} chunks")

    all_blocks = []
    for i, chunk in enumerate(chunks):
        log(f"{prefix}Chunk {i+1}/{len(chunks)}...")
        content = call_blockify(chunk)
        if content:
            blocks = parse_ideablocks(content)
            all_blocks.extend(blocks)
            log(f"{prefix}  -> {len(blocks)} blocks")
        else:
            log(f"{prefix}  -> failed", "WARNING")
        time.sleep(0.5)

    if all_blocks:
        source = filename
        count = ingest_blocks_to_collection(all_blocks, collection, source)
        log(f"{prefix}Ingested {count} blocks to ChromaDB")
        return count

    return 0


# =============================================================================
# Distillation Functions
# =============================================================================

def check_distillation_service(service_url):
    """Check if distillation service is healthy."""
    try:
        response = requests.get(f"{service_url}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except Exception as e:
        return False, str(e)


def export_blocks_for_distillation(collection, only_active=True):
    """Export blocks from ChromaDB for distillation."""
    count = collection.count()
    if count == 0:
        return []

    results = collection.get(
        limit=count,
        include=["metadatas", "documents"]
    )

    blocks = []
    for i, doc_id in enumerate(results['ids']):
        metadata = results['metadatas'][i]

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

    return blocks


def submit_distillation_job(service_url, blocks, similarity, iterations):
    """Submit distillation job."""
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
        return data.get('jobId'), task_uuid

    except Exception as e:
        log(f"Failed to submit job: {e}", "ERROR")
        return None, None


def poll_distillation_job(service_url, job_id):
    """Poll for job completion."""
    start_time = time.time()
    last_progress = None

    while time.time() - start_time < MAX_POLL_TIME:
        try:
            response = requests.get(f"{service_url}/api/jobs/{job_id}", timeout=30)
            response.raise_for_status()
            data = response.json()

            status = data.get('status')

            if status == 'running' and 'progress' in data:
                progress = data['progress']
                progress_str = f"{progress.get('percent', 0):.1f}%"
                if progress_str != last_progress:
                    log(f"  Distillation progress: {progress_str}")
                    last_progress = progress_str

            if status == 'success':
                return data
            elif status in ['failure', 'timeout']:
                log(f"Distillation {status}: {data.get('error', 'Unknown')}", "ERROR")
                return data if data.get('intermediate_result') else None

            time.sleep(POLL_INTERVAL)

        except Exception as e:
            log(f"Poll error: {e}", "WARNING")
            time.sleep(POLL_INTERVAL * 2)

    return None


def import_distillation_results(target_collection, source_collection, results, task_uuid):
    """Import distillation results and mark source blocks."""
    merged_blocks = [
        r for r in results
        if r.get('type') == 'merged' and not r.get('hidden', False)
    ]

    if not merged_blocks:
        return 0, 0

    # Import merged blocks
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
            'source_task': task_uuid,
            'source_blocks': json.dumps(source_ids),
            'source_count': len(source_ids),
            'created_at': timestamp
        })

    log(f"Generating embeddings for {len(documents)} merged blocks...")
    embeddings = generate_embeddings(documents)

    target_collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    # Mark source blocks as distilled
    marked_count = 0
    if all_source_ids:
        existing = source_collection.get(
            ids=list(all_source_ids),
            include=["metadatas", "documents", "embeddings"]
        )

        if existing['ids']:
            updated_metadatas = []
            for meta in existing['metadatas']:
                updated_meta = dict(meta)
                updated_meta['distilled'] = True
                updated_meta['distilled_at'] = timestamp
                updated_meta['distill_task'] = task_uuid
                updated_metadatas.append(updated_meta)

            source_collection.upsert(
                ids=existing['ids'],
                metadatas=updated_metadatas,
                documents=existing.get('documents'),
                embeddings=existing.get('embeddings')
            )
            marked_count = len(existing['ids'])

    return len(ids), marked_count


# =============================================================================
# Main Pipeline
# =============================================================================

def run_full_pipeline(
    input_path,
    threshold=0.55,
    iterations=4,
    skip_distillation=False,
    service_url=DISTILL_SERVICE_URL,
    file_extensions=None,
    parallel_workers=PARALLEL_WORKERS
):
    """Run the full pipeline from documents to searchable knowledge base.

    Args:
        input_path: Path to file or directory to process
        threshold: Similarity threshold for distillation (default: 0.55)
        iterations: Number of distillation iterations (default: 4)
        skip_distillation: If True, skip distillation step
        service_url: URL for distillation service
        file_extensions: List of file extensions to process (default: ['.txt', '.md'])
        parallel_workers: Number of parallel workers for ingestion (default: 5)
    """

    if file_extensions is None:
        file_extensions = ['.txt', '.md']

    log("=" * 70)
    log("BLOCKIFY FULL PIPELINE")
    log("=" * 70)
    log(f"Input: {input_path}")
    log(f"Extensions: {file_extensions}")
    log(f"Parallel workers: {parallel_workers}")
    log(f"Distillation: {'SKIP' if skip_distillation else 'ENABLED'}")
    if not skip_distillation:
        log(f"Threshold: {threshold}")
        log(f"Iterations: {iterations}")
    log("=" * 70)

    # Validate environment
    if not BLOCKIFY_API_KEY:
        log("BLOCKIFY_API_KEY not set", "ERROR")
        return False
    if not OPENAI_API_KEY:
        log("OPENAI_API_KEY not set", "ERROR")
        return False

    # Check distillation service
    distill_available = False
    if not skip_distillation:
        healthy, info = check_distillation_service(service_url)
        if healthy:
            log(f"Distillation service available: {info}")
            distill_available = True
        else:
            log(f"Distillation service not available: {info}", "WARNING")
            log("Will skip distillation - run separately later")

    # Initialize ChromaDB
    client = get_chroma_client()
    raw_collection = get_collection(client, 'raw')
    distilled_collection = get_collection(client, 'distilled')

    initial_raw_count = raw_collection.count()
    log(f"Initial raw collection: {initial_raw_count} blocks")

    # Phase 1: Ingest documents
    log("")
    log("=" * 70)
    log("PHASE 1: DOCUMENT INGESTION")
    log("=" * 70)

    input_path = Path(input_path)
    files_to_process = []

    if input_path.is_file():
        files_to_process.append(input_path)
    elif input_path.is_dir():
        for ext in file_extensions:
            files_to_process.extend(input_path.glob(f'**/*{ext}'))
    else:
        log(f"Input path not found: {input_path}", "ERROR")
        return False

    if not files_to_process:
        log(f"No files found with extensions {file_extensions}", "ERROR")
        return False

    log(f"Found {len(files_to_process)} files to process with {parallel_workers} worker(s)")

    total_ingested = 0
    if parallel_workers > 1:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
            futures = {
                executor.submit(process_file, str(fp), raw_collection, True): fp
                for fp in files_to_process
            }
            for future in as_completed(futures):
                filepath = futures[future]
                try:
                    count = future.result()
                    total_ingested += count
                except Exception as e:
                    log(f"Error processing {filepath}: {e}", "ERROR")
    else:
        # Sequential processing
        for filepath in files_to_process:
            try:
                count = process_file(str(filepath), raw_collection, parallel=False)
                total_ingested += count
            except Exception as e:
                log(f"Error processing {filepath}: {e}", "ERROR")

    final_raw_count = raw_collection.count()

    log("")
    log(f"Ingestion complete:")
    log(f"  Files processed: {len(files_to_process)}")
    log(f"  Blocks created: {total_ingested}")
    log(f"  Raw collection: {final_raw_count} blocks")

    # Phase 2: Distillation
    imported_count = 0
    marked_count = 0

    if distill_available and not skip_distillation and final_raw_count >= 2:
        log("")
        log("=" * 70)
        log("PHASE 2: DISTILLATION")
        log("=" * 70)

        # Export active blocks
        blocks = export_blocks_for_distillation(raw_collection, only_active=True)
        log(f"Exported {len(blocks)} active blocks for distillation")

        if len(blocks) >= 2:
            # Submit job
            job_id, task_uuid = submit_distillation_job(
                service_url, blocks, threshold, iterations
            )

            if job_id:
                log(f"Job submitted: {job_id}")

                # Poll for completion
                result = poll_distillation_job(service_url, job_id)

                if result:
                    results = result.get('results', [])
                    stats = result.get('stats', {})

                    log(f"Distillation stats:")
                    log(f"  Starting: {stats.get('startingBlockCount', 'N/A')}")
                    log(f"  Final: {stats.get('finalBlockCount', 'N/A')}")
                    log(f"  Reduction: {stats.get('blockReductionPercent', 'N/A')}%")

                    # Import results
                    imported_count, marked_count = import_distillation_results(
                        distilled_collection, raw_collection, results, task_uuid
                    )
                    log(f"Imported {imported_count} merged blocks")
                    log(f"Marked {marked_count} source blocks as distilled")
                else:
                    log("Distillation failed", "ERROR")
            else:
                log("Failed to submit distillation job", "ERROR")
        else:
            log("Not enough blocks for distillation", "WARNING")
    elif skip_distillation:
        log("")
        log("Skipping distillation (--no-distill flag)")
    elif not distill_available:
        log("")
        log("Docker distillation service not available - using direct API fallback")
        try:
            # Import and run distill_chromadb directly
            scripts_dir = Path(__file__).parent
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))

            from distill_chromadb import run_distillation as run_direct_distillation

            log("Running distillation via direct Blockify API...")
            run_direct_distillation(
                threshold=0.7,
                max_cluster_size=15,
                dry_run=False
            )
            log("Direct API distillation complete")
        except ImportError as e:
            log(f"Direct distillation module not available: {e}", "WARNING")
            log("Skipping distillation - run distill_chromadb.py manually")
        except Exception as e:
            log(f"Direct distillation failed: {e}", "WARNING")
            log("Distillation skipped - run distill_chromadb.py manually")
    else:
        log("")
        log("Skipping distillation (need at least 2 blocks)")

    # Phase 3: Benchmark
    benchmark_report = None
    log("")
    log("=" * 70)
    log("PHASE 3: BENCHMARK")
    log("=" * 70)

    try:
        # Add scripts directory to path for benchmark import
        scripts_dir = Path(__file__).parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        from benchmark import BenchmarkRunner

        log("Running benchmark comparison...")
        runner = BenchmarkRunner()
        benchmark_report = runner.run()
        log(f"Benchmark complete. Report: {benchmark_report}")
    except ImportError as e:
        log(f"Benchmark module not available: {e}", "WARNING")
        log("Skipping benchmark. Install dependencies: pip install jinja2 matplotlib pyyaml")
    except Exception as e:
        log(f"Benchmark failed: {e}", "WARNING")
        log("Pipeline will continue without benchmark report")

    # Phase 4: Summary
    log("")
    log("=" * 70)
    log("PIPELINE COMPLETE")
    log("=" * 70)

    # Count actual active blocks
    raw_total = raw_collection.count()
    try:
        active_results = raw_collection.get(
            limit=raw_total,
            where={"distilled": {"$eq": False}},
            include=[]
        )
        active_count = len(active_results['ids']) if active_results['ids'] else 0
    except Exception:
        # Fallback: count all and subtract marked
        active_count = raw_total - marked_count

    log(f"Raw collection: {raw_total} blocks")
    log(f"  - Active: {active_count}")
    log(f"  - Distilled (inactive): {raw_total - active_count}")
    log(f"Distilled collection: {distilled_collection.count()} blocks")
    if benchmark_report:
        log(f"Benchmark report: {benchmark_report}")
    log("")
    log("Next steps:")
    log("  Search: python search_chromadb.py \"your query\"")
    if benchmark_report:
        log(f"  View report: open {benchmark_report}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Full pipeline: Folder -> Blockify -> ChromaDB -> Distillation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/docs/              # Process folder (5 parallel workers)
  %(prog)s document.txt                # Process single file
  %(prog)s /docs/ --no-distill         # Ingest only
  %(prog)s /docs/ --threshold 0.60     # Higher similarity
  %(prog)s /docs/ --ext .txt .md .rst  # Custom extensions
  %(prog)s /docs/ --parallel 10        # Use 10 parallel workers
  %(prog)s /docs/ --sequential         # Sequential processing
        """
    )

    parser.add_argument('input', help='File or directory to process')
    parser.add_argument('--threshold', '-t', type=float, default=0.55,
                       help='Similarity threshold (default: 0.55)')
    parser.add_argument('--iterations', '-i', type=int, default=4,
                       help='Distillation iterations (default: 4)')
    parser.add_argument('--no-distill', action='store_true',
                       help='Skip distillation step')
    parser.add_argument('--service-url', '-u', default=DISTILL_SERVICE_URL,
                       help='Distillation service URL')
    parser.add_argument('--ext', nargs='+', default=['.txt', '.md'],
                       help='File extensions to process (default: .txt .md)')
    parser.add_argument('--parallel', '-p', type=int, default=PARALLEL_WORKERS,
                       metavar='N',
                       help=f'Number of parallel workers (default: {PARALLEL_WORKERS})')
    parser.add_argument('--sequential', '-s', action='store_true',
                       help='Force sequential processing (disable parallelization)')

    args = parser.parse_args()

    # Determine number of workers
    num_workers = 1 if args.sequential else args.parallel

    success = run_full_pipeline(
        input_path=args.input,
        threshold=args.threshold,
        iterations=args.iterations,
        skip_distillation=args.no_distill,
        service_url=args.service_url,
        file_extensions=args.ext,
        parallel_workers=num_workers
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
