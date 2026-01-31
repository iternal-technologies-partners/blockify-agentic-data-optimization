"""Pydantic models for API request/response schemas."""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class BlockifiedTextResult(BaseModel):
    """Content of a single IdeaBlock."""
    name: str
    criticalQuestion: str
    trustedAnswer: str
    entityType: Optional[str] = None
    entityUUID: Optional[str] = None
    isPublic: Optional[bool] = None


class BlockifyResult(BaseModel):
    """A single blockify result (IdeaBlock)."""
    type: Literal["blockify", "merged", "synthetic", "new"]
    blockifyResultUUID: str
    blockifiedTextResult: BlockifiedTextResult
    hidden: bool = False
    exported: bool = False
    reviewed: bool = False
    blockifyDocumentUUID: Optional[str] = None
    blockifyResultsUsed: Optional[List[str]] = None


class AutoDistillRequest(BaseModel):
    """Request to distill/deduplicate IdeaBlocks."""
    blockifyTaskUUID: str = Field(..., description="UUID of the blockify task")
    similarity: float = Field(default=0.55, ge=0.0, le=1.0, description="Similarity threshold")
    iterations: int = Field(default=4, ge=1, le=10, description="Number of iterations")
    results: List[BlockifyResult] = Field(..., min_length=1, description="List of blockify results")


class ProcessingStats(BaseModel):
    """Statistics about the distillation process."""
    startingBlockCount: int
    finalBlockCount: int
    blocksRemoved: int
    blocksAdded: int
    blockReductionPercent: float


class ProgressInfo(BaseModel):
    """Progress information for running jobs."""
    percent: float = Field(description="Progress percentage (0-100)")
    phase: str = Field(description="Current processing phase")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")


class AutoDistillResponse(BaseModel):
    """Response from distillation request."""
    schemaVersion: int = Field(default=1, description="API schema version")
    status: Literal["success", "running", "failure", "timeout"]
    stats: Optional[ProcessingStats] = None
    results: List[BlockifyResult] = Field(default_factory=list)
    error: Optional[str] = None
    progress: Optional[ProgressInfo] = None
    intermediate_result: Optional[Dict[str, Any]] = None


class JobSubmissionResponse(BaseModel):
    """Response when submitting an async job."""
    schemaVersion: int = Field(default=1, description="API schema version")
    jobId: str = Field(description="Job ID for polling")


class HealthResponse(BaseModel):
    """Detailed health check response."""
    status: str = "ok"
    version: str
    model: str
    embedding_model: str
    max_cluster_size: str
    database_backend: str
    jobs_active: int = 0
    jobs_completed_24h: int = 0
    uptime_seconds: float = 0
    memory_usage_mb: float = 0
    cpu_percent: float = 0


class WebhookPayload(BaseModel):
    """Payload sent to webhook URL on job completion."""
    job_id: str
    status: Literal["success", "failure", "timeout"]
    stats: Optional[ProcessingStats] = None
    error: Optional[str] = None
    completed_at: str
