"""Filesystem backend for job persistence (fallback/simple mode)."""

import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from app.db.base import JobStore, Job, JobStatus
from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)


class FilesystemJobStore(JobStore):
    """Filesystem-based job storage (simple, no database required)."""

    def __init__(self, data_dir: str = None):
        super().__init__()
        self._jobs: Dict[str, Job] = {}

        # Setup data directory
        self.data_dir = Path(data_dir or settings.data_dir)
        self.jobs_dir = self.data_dir / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Filesystem job store initialized", data_dir=str(self.data_dir))

    def _persist_job(self, job: Job) -> None:
        """Persist job to disk."""
        job_file = self.jobs_dir / f"{job.job_id}.json"
        job_data = {
            "job_id": job.job_id,
            "status": job.status.value,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
            "result": job.result,
            "error": job.error,
            "webhook_url": job.webhook_url,
        }

        try:
            with open(job_file, "w") as f:
                json.dump(job_data, f, indent=2)
        except Exception as e:
            logger.error("Failed to persist job", job_id=job.job_id, error=str(e))

    def _load_job_from_disk(self, job_id: str) -> Optional[Job]:
        """Load job from disk."""
        job_file = self.jobs_dir / f"{job_id}.json"
        if not job_file.exists():
            return None

        try:
            with open(job_file, "r") as f:
                data = json.load(f)

            return Job(
                job_id=data["job_id"],
                status=JobStatus(data["status"]),
                created_at=data["created_at"],
                completed_at=data.get("completed_at"),
                result=data.get("result"),
                error=data.get("error"),
                webhook_url=data.get("webhook_url"),
            )
        except Exception as e:
            logger.error("Failed to load job from disk", job_id=job_id, error=str(e))
            return None

    def create_job(self, webhook_url: Optional[str] = None) -> str:
        """Create a new job and return its ID."""
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            status=JobStatus.RUNNING,
            webhook_url=webhook_url,
        )
        self._jobs[job_id] = job
        logger.info("Created job", job_id=job_id)
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        # Check memory first
        if job_id in self._jobs:
            return self._jobs[job_id]

        # Try loading from disk
        return self._load_job_from_disk(job_id)

    def update_job_success(self, job_id: str, result: Dict[str, Any]) -> None:
        """Mark job as successful with result."""
        job = self._jobs.get(job_id)
        if job:
            job.status = JobStatus.SUCCESS
            job.completed_at = time.time()
            job.result = result

            self._persist_job(job)
            self._cleanup_intermediate(job_id)

            del self._jobs[job_id]
            self.remove_future(job_id)

            logger.info("Job completed successfully", job_id=job_id)

    def update_job_failure(self, job_id: str, error: str) -> None:
        """Mark job as failed with error."""
        job = self._jobs.get(job_id)
        if job:
            job.status = JobStatus.FAILURE
            job.completed_at = time.time()
            job.error = error

            self._persist_job(job)

            del self._jobs[job_id]
            self.remove_future(job_id)

            logger.error("Job failed", job_id=job_id, error=error)

    def update_job_timeout(self, job_id: str) -> None:
        """Mark job as timed out."""
        job = self._jobs.get(job_id)
        if job:
            if job.status == JobStatus.SUCCESS:
                return

            job.status = JobStatus.TIMEOUT
            job.completed_at = time.time()
            job.error = "Job execution timed out"

            self._persist_job(job)

            del self._jobs[job_id]
            self.remove_future(job_id)

            logger.warning("Job timed out", job_id=job_id)

    def update_job_progress(
        self, job_id: str, phase: str, progress: float, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update job progress."""
        job = self._jobs.get(job_id)
        if job:
            job.progress = progress
            job.progress_phase = phase
            job.progress_details = details or {}

    def save_intermediate_result(self, job_id: str, result: Dict[str, Any]) -> None:
        """Save intermediate result for crash recovery."""
        job = self._jobs.get(job_id)
        if job:
            job.intermediate_result = result

            # Also persist to disk
            intermediate_file = self.jobs_dir / f"{job_id}.intermediate.json"
            try:
                with open(intermediate_file, "w") as f:
                    json.dump(result, f)
            except Exception as e:
                logger.error("Failed to save intermediate result", job_id=job_id, error=str(e))

    def get_intermediate_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get intermediate result for a job."""
        # Check memory
        job = self._jobs.get(job_id)
        if job and job.intermediate_result:
            return job.intermediate_result

        # Check disk
        intermediate_file = self.jobs_dir / f"{job_id}.intermediate.json"
        if intermediate_file.exists():
            try:
                with open(intermediate_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Failed to load intermediate result", job_id=job_id, error=str(e))

        return None

    def _cleanup_intermediate(self, job_id: str) -> None:
        """Clean up intermediate files."""
        intermediate_file = self.jobs_dir / f"{job_id}.intermediate.json"
        if intermediate_file.exists():
            try:
                intermediate_file.unlink()
            except Exception as e:
                logger.warning("Failed to cleanup intermediate file", job_id=job_id, error=str(e))

    def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        deleted = False

        if job_id in self._jobs:
            del self._jobs[job_id]
            deleted = True

        job_file = self.jobs_dir / f"{job_id}.json"
        if job_file.exists():
            try:
                job_file.unlink()
                deleted = True
            except Exception as e:
                logger.error("Failed to delete job file", job_id=job_id, error=str(e))

        self._cleanup_intermediate(job_id)

        future = self.get_future(job_id)
        if future and not future.done():
            future.cancel()
        self.remove_future(job_id)

        return deleted

    def cleanup_old_jobs(self, max_age_seconds: int) -> int:
        """Clean up jobs older than max_age_seconds."""
        cutoff = time.time() - max_age_seconds
        count = 0

        for job_file in self.jobs_dir.glob("*.json"):
            if job_file.name.endswith(".intermediate.json"):
                continue

            try:
                if job_file.stat().st_mtime < cutoff:
                    job_file.unlink()
                    count += 1
            except Exception as e:
                logger.error("Failed to cleanup old job file", file=str(job_file), error=str(e))

        if count > 0:
            logger.info("Cleaned up old jobs", count=count)

        return count

    def get_active_job_count(self) -> int:
        """Get count of currently running jobs."""
        return len(self._jobs)

    def get_completed_job_count_since(self, since_timestamp: float) -> int:
        """Get count of jobs completed since timestamp."""
        count = 0
        for job_file in self.jobs_dir.glob("*.json"):
            if job_file.name.endswith(".intermediate.json"):
                continue
            try:
                if job_file.stat().st_mtime >= since_timestamp:
                    count += 1
            except Exception:
                pass
        return count
