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
    """Group similar IdeaBlocks based on answer similarity."""
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

            # Compare by trusted_answer similarity
            sim = similarity(ib1['trusted_answer'], ib2['trusted_answer'])
            if sim >= threshold:
                cluster.append(ib2)
                used.add(j)

        clusters.append(cluster)

    return clusters


def ideablock_to_xml(ib):
    """Convert IdeaBlock dict to XML string."""
    entities = ''.join([
        f'<entity><entity_name>{e["name"]}</entity_name>'
        f'<entity_type>{e["type"]}</entity_type></entity>'
        for e in ib.get('entities', [])
    ])

    tags = ', '.join(ib.get('tags', []))
    keywords = ', '.join(ib.get('keywords', []))

    return f'''<ideablock>
<name>{ib["name"]}</name>
<critical_question>{ib["critical_question"]}</critical_question>
<trusted_answer>{ib["trusted_answer"]}</trusted_answer>
<tags>{tags}</tags>
{entities}
<keywords>{keywords}</keywords>
</ideablock>'''


def extract_field(xml, field):
    """Extract a field from XML."""
    match = re.search(f'<{field}>(.*?)</{field}>', xml, re.DOTALL)
    return match.group(1).strip() if match else ''


def parse_ideablocks(content):
    """Parse distilled IdeaBlocks from API response."""
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
            'tags': [t.strip() for t in extract_field(block, 'tags').split(',') if t.strip()],
            'entities': entities,
            'keywords': [k.strip() for k in extract_field(block, 'keywords').split(',') if k.strip()]
        })

    return parsed


def call_distill(ideablocks_xml, retries=3):
    """Call Blockify Distill API."""
    for attempt in range(retries):
        try:
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
            elif response.status_code == 429:
                wait = 2 ** attempt
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    Error {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print("    Timeout, retrying...")
            time.sleep(2)

    return None


def main():
    if not API_KEY:
        print("Error: BLOCKIFY_API_KEY environment variable not set")
        print("Set it with: export BLOCKIFY_API_KEY='blk_your_key_here'")
        sys.exit(1)

    if len(sys.argv) != 3:
        print("Usage: python blockify_distill.py ideablocks.json distilled.json")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    # Load IdeaBlocks
    print(f"Loading {input_path}...")
    with open(input_path, 'r') as f:
        ideablocks = json.load(f)

    print(f"  Loaded {len(ideablocks)} IdeaBlocks")

    # Cluster similar blocks
    print("Clustering similar IdeaBlocks...")
    clusters = cluster_similar(ideablocks)

    singles = sum(1 for c in clusters if len(c) == 1)
    multis = sum(1 for c in clusters if len(c) > 1)
    print(f"  {len(clusters)} clusters: {singles} unique, {multis} to distill")

    # Distill multi-block clusters
    print("Distilling similar clusters...")
    distilled = []

    for i, cluster in enumerate(clusters):
        if len(cluster) == 1:
            # Single block, keep as-is
            distilled.append(cluster[0])
        else:
            # Multiple similar blocks, distill
            print(f"  Cluster {i+1}: {len(cluster)} blocks...", end=' ')

            # Limit to 15 blocks per distill call (API recommendation)
            xml = ''.join([ideablock_to_xml(ib) for ib in cluster[:15]])
            result = call_distill(xml)

            if result:
                merged = parse_ideablocks(result)
                distilled.extend(merged)
                print(f"merged to {len(merged)}")
            else:
                # Keep originals on failure
                distilled.extend(cluster)
                print("failed, keeping originals")

            time.sleep(0.5)

    # Save
    print(f"Saving to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(distilled, f, indent=2)

    reduction = (1 - len(distilled) / len(ideablocks)) * 100
    print(f"Done! {len(ideablocks)} -> {len(distilled)} IdeaBlocks ({reduction:.1f}% reduction)")


if __name__ == '__main__':
    main()
