#!/usr/bin/env python3
"""
Search IdeaBlocks knowledge base.

Usage:
    python blockify_search.py "query" ideablocks.json
"""

import sys
import json
from difflib import SequenceMatcher


def similarity(a, b):
    """Calculate text similarity using sequence matching."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def search(query, ideablocks, top_k=5):
    """Search IdeaBlocks by text similarity and keyword matching."""
    scored = []
    query_lower = query.lower()
    query_words = set(query_lower.split())

    for ib in ideablocks:
        # Combine searchable text
        text = f"{ib['name']} {ib['critical_question']} {ib['trusted_answer']}"
        keywords = ' '.join(ib.get('keywords', []))
        full_text = f"{text} {keywords}"

        # Calculate base similarity score
        score = similarity(query, full_text)

        # Boost for exact phrase matches
        if query_lower in full_text.lower():
            score += 0.4

        # Boost if query words appear in key fields
        name_lower = ib['name'].lower()
        question_lower = ib['critical_question'].lower()

        for word in query_words:
            if word in name_lower:
                score += 0.15
            if word in question_lower:
                score += 0.1
            if word in keywords.lower():
                score += 0.05

        scored.append((score, ib))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    return scored[:top_k]


def format_result(score, ib):
    """Format a single search result."""
    print(f"\n{'='*60}")
    print(f"[{ib['name']}]")
    print(f"Score: {score:.3f}")
    print(f"{'='*60}")
    print(f"Q: {ib['critical_question']}")
    print(f"A: {ib['trusted_answer']}")
    if ib.get('tags'):
        print(f"Tags: {', '.join(ib['tags'][:5])}")
    if ib.get('keywords'):
        print(f"Keywords: {', '.join(ib['keywords'][:5])}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python blockify_search.py 'query' ideablocks.json")
        print("\nExample:")
        print("  python blockify_search.py 'What is Blockify?' knowledge_base.json")
        sys.exit(1)

    query = sys.argv[1]
    kb_path = sys.argv[2]

    # Load knowledge base
    try:
        with open(kb_path, 'r') as f:
            ideablocks = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {kb_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {kb_path}")
        sys.exit(1)

    print(f"\nSearching {len(ideablocks)} IdeaBlocks for: '{query}'")

    # Search
    results = search(query, ideablocks)

    if not results:
        print("\nNo results found.")
        return

    # Display results
    for score, ib in results:
        format_result(score, ib)

    print(f"\n{'='*60}")
    print(f"Found {len(results)} results")


if __name__ == '__main__':
    main()
