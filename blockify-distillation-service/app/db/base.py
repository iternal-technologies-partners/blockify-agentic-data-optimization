"""Base classes for job storage abstraction."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List
from concurrent.futures import Future


class JobStatus(Enum):
    """Job execution status."""
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


@dataclass
class Job:
    """Represents a distillation job."""
    job_id: str
    status: JobStatus
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    # Progress tracking
    progress: float = 0.0  # 0.0 to 1.0
    progress_phase: str = ""
    progress_details: Dict[str, Any] = field(default_factory=dict)
    # Intermediate results (for crash recovery)
    intermediate_result: Optional[Dict[str, Any]] = None
    # Webhook
    webhook_url: Optional[str] = None


class JobStore(ABC):
    """Abstract base class for job storage backends."""

    def __init__(self):
        self._running_futures: Dict[str, Future] = {}

    @abstractmethod
    def create_job(self, webhook_url: Optional[str] = None) -> str:
        """Create a new job and return its ID."""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        pass

    @abstractmethod
    def update_job_success(self, job_id: str, result: Dict[str, Any]) -> None:
        """Mark job as successful with result."""
        pass

    @abstractmethod
    def update_job_failure(self, job_id: str, error: str) -> None:
        """Mark job as failed with error."""
        pass

    @abstractmethod
    def update_job_timeout(self, job_id: str) -> None:
        """Mark job as timed out."""
        pass

    @abstractmethod
    def update_job_progress(
        self, job_id: str, phase: str, progress: float, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update job progress."""
        pass

    @abstractmethod
    def save_intermediate_result(self, job_id: str, result: Dict[str, Any]) -> None:
        """Save intermediate result for crash recovery."""
        pass

    @abstractmethod
    def get_intermediate_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get intermediate result for a job."""
        pass

    @abstractmethod
    def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        pass

    @abstractmethod
    def cleanup_old_jobs(self, max_age_seconds: int) -> int:
        """Clean up jobs older than max_age_seconds. Returns count deleted."""
        pass

    @abstractmethod
    def get_active_job_count(self) -> int:
        """Get count of currently running jobs."""
        pass

    @abstractmethod
    def get_completed_job_count_since(self, since_timestamp: float) -> int:
        """Get count of jobs completed since timestamp."""
        pass

    def track_future(self, job_id: str, future: Future) -> None:
        """Track a running future for timeout management."""
        self._running_futures[job_id] = future

    def get_future(self, job_id: str) -> Optional[Future]:
        """Get the future for a job."""
        return self._running_futures.get(job_id)

    def remove_future(self, job_id: str) -> None:
        """Remove a tracked future."""
        if job_id in self._running_futures:
            del self._running_futures[job_id]
