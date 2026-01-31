#!/usr/bin/env python3
"""
Verify Blockify integration environment is ready.

Usage:
    python setup_check.py
    python setup_check.py --install  # Auto-install missing dependencies
    python setup_check.py --status   # Show detailed status only

Exit codes:
    0 = Ready
    1 = Missing dependencies (fixable with --install)
    2 = Missing API keys (requires manual setup)
"""

import os
import sys
import subprocess

REQUIRED_PACKAGES = ['requests', 'chromadb', 'openai']
DISTILL_SERVICE_URL = os.environ.get('DISTILL_SERVICE_URL', 'http://localhost:8315')


def check_package(name):
    """Check if package is installed."""
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def check_api_keys():
    """Check required API keys."""
    issues = []

    if not os.environ.get('BLOCKIFY_API_KEY'):
        issues.append('BLOCKIFY_API_KEY not set')

    if not os.environ.get('OPENAI_API_KEY'):
        issues.append('OPENAI_API_KEY not set (required for embeddings)')

    return issues


def check_distillation_service(url=DISTILL_SERVICE_URL):
    """Check if distillation service is running."""
    try:
        import requests
        response = requests.get(f"{url}/healthz", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
        return False, f"Status {response.status_code}"
    except Exception as e:
        return False, str(e)


def get_chromadb_stats(chroma_dir):
    """Get ChromaDB collection statistics."""
    try:
        import chromadb
        from chromadb.config import Settings

        client = chromadb.PersistentClient(
            path=chroma_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        collections = client.list_collections()
        stats = {}

        for col in collections:
            stats[col.name] = col.count()

        return stats
    except Exception as e:
        return {"error": str(e)}


def install_packages():
    """Install missing packages."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements = os.path.join(script_dir, '..', 'requirements.txt')

    if os.path.exists(requirements):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements])
    else:
        for pkg in REQUIRED_PACKAGES:
            if not check_package(pkg):
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])


def main():
    print("=" * 60)
    print("BLOCKIFY INTEGRATION STATUS")
    print("=" * 60)

    auto_install = '--install' in sys.argv
    status_only = '--status' in sys.argv

    # Check packages
    missing_packages = [pkg for pkg in REQUIRED_PACKAGES if not check_package(pkg)]

    if missing_packages:
        print(f"\n[X] Missing packages: {', '.join(missing_packages)}")
        if auto_install:
            print("    Installing...")
            install_packages()
            print("    Done!")
            missing_packages = []
        else:
            print("    Run: pip install -r requirements.txt")
            print("    Or:  python setup_check.py --install")
    else:
        print("\n[OK] Python packages installed")

    # Check API keys
    key_issues = check_api_keys()

    if key_issues:
        print(f"\n[X] API key issues:")
        for issue in key_issues:
            print(f"    - {issue}")
        if not status_only:
            print("\n    Set keys with:")
            print("    export BLOCKIFY_API_KEY='blk_your_key'")
            print("    export OPENAI_API_KEY='sk-your_key'")
    else:
        print("\n[OK] API keys configured")

    # Check data directory and ChromaDB
    data_dir = os.environ.get('IDEABLOCK_DATA_DIR', './data/ideablocks')
    chroma_dir = os.path.join(data_dir, 'chroma_db')

    if os.path.exists(chroma_dir):
        print(f"\n[OK] ChromaDB directory exists")
        print(f"     Location: {chroma_dir}")

        # Get collection stats
        if not missing_packages:
            stats = get_chromadb_stats(chroma_dir)
            if "error" not in stats:
                print("\n     Collections:")
                if stats:
                    for name, count in stats.items():
                        print(f"       - {name}: {count} blocks")
                else:
                    print("       (no collections yet)")
            else:
                print(f"     Error reading stats: {stats['error']}")
    else:
        print(f"\n[--] ChromaDB not initialized")
        print(f"     Will create at: {chroma_dir}")

    # Check distillation service
    print(f"\n[..] Checking distillation service at {DISTILL_SERVICE_URL}...")

    if not missing_packages:
        healthy, info = check_distillation_service()
        if healthy:
            print(f"[OK] Distillation service running")
            print(f"     Version: {info.get('version', 'unknown')}")
            print(f"     Active jobs: {info.get('jobs_active', 0)}")
            print(f"     Completed (24h): {info.get('jobs_completed_24h', 0)}")
        else:
            print(f"[--] Distillation service not available")
            print(f"     Error: {info}")
            print(f"\n     To start the service:")
            print(f"     cd blockify-distillation-service && docker-compose up -d")
    else:
        print("[--] Cannot check (missing packages)")

    # Summary
    print("\n" + "=" * 60)

    if missing_packages and not auto_install:
        print("STATUS: NOT READY")
        print("ACTION: Install packages with --install flag")
        sys.exit(1)
    elif key_issues:
        print("STATUS: NOT READY")
        print("ACTION: Set API keys (see above)")
        sys.exit(2)
    else:
        print("STATUS: READY")
        print("\nQuick commands:")
        print("  Ingest:  python ingest_to_chromadb.py /path/to/docs/ --batch")
        print("  Search:  python search_chromadb.py \"your query\"")
        print("  Distill: python run_distillation.py")
        print("  Full:    python run_full_pipeline.py /path/to/docs/")
        sys.exit(0)


if __name__ == '__main__':
    main()
