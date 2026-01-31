"""Pytest configuration and fixtures."""

import os
import pytest
from unittest.mock import patch

# Set test environment variables before importing app modules
os.environ["BLOCKIFY_API_KEY"] = "test-blockify-key"
os.environ["OPENAI_API_KEY"] = "test-openai-key"
os.environ["DATABASE_BACKEND"] = "filesystem"
os.environ["DATA_DIR"] = "/tmp/blockify-test-data"


@pytest.fixture
def sample_blocks():
    """Sample IdeaBlocks for testing."""
    return [
        {
            "type": "blockify",
            "blockifyResultUUID": "block-1",
            "blockifiedTextResult": {
                "name": "Python Basics",
                "criticalQuestion": "What is Python?",
                "trustedAnswer": "Python is a programming language.",
            },
            "hidden": False,
            "exported": False,
            "reviewed": False,
        },
        {
            "type": "blockify",
            "blockifyResultUUID": "block-2",
            "blockifiedTextResult": {
                "name": "Python Introduction",
                "criticalQuestion": "What is Python programming?",
                "trustedAnswer": "Python is a high-level programming language.",
            },
            "hidden": False,
            "exported": False,
            "reviewed": False,
        },
        {
            "type": "blockify",
            "blockifyResultUUID": "block-3",
            "blockifiedTextResult": {
                "name": "JavaScript Basics",
                "criticalQuestion": "What is JavaScript?",
                "trustedAnswer": "JavaScript is a scripting language for web browsers.",
            },
            "hidden": False,
            "exported": False,
            "reviewed": False,
        },
    ]


@pytest.fixture
def mock_embeddings():
    """Mock embedding generator."""
    import numpy as np

    with patch("app.dedupe.embeddings.OpenAIEmbeddingGenerator") as mock:
        instance = mock.return_value
        instance.generate_embeddings.return_value = np.random.rand(3, 1536)
        instance.create_text_blob.side_effect = lambda b: b.get("blockifiedTextResult", {}).get(
            "trustedAnswer", ""
        )
        yield instance
