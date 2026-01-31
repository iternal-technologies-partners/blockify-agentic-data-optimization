"""Data models for LLM requests and responses."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MergeRequest:
    """Request to merge a cluster of blocks via LLM."""
    cluster_blocks: List[Dict[str, Any]]
    iteration: int = 1


@dataclass
class MergeResponse:
    """Response from LLM merge operation."""
    success: bool
    merged_content: Optional[Dict[str, str]] = None  # Single block (backward compat)
    merged_contents: Optional[List[Dict[str, str]]] = None  # Multiple blocks
    error: Optional[str] = None
