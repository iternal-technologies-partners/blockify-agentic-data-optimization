"""Job management with timeout enforcement and persistence."""

import time
from typing import Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, Future, wait

from app.db import create_job_store, JobStore, JobStatus
from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)


class JobManager:
    """Manages job execution using thread pool with timeout enforcement."""

    def __init__(self, job_store: JobStore = None):
        max_workers = settings.max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.job_store = job_store or create_job_store()
        self.timeout_seconds = settings.job_timeout_seconds

        logger.info(
            "JobManager initialized",
            max_workers=max_workers,
            timeout_seconds=self.timeout_seconds,
            database_backend=settings.database_backend,
        )

    def submit_job(
        self,
        func: Callable,
        webhook_url: Optional[str] = None,
        *args,
        **kwargs,
    ) -> str:
        """Submit a job for execution with timeout enforcement.

        Args:
            func: Function to execute
            webhook_url: Optional URL for completion notification
            *args, **kwargs: Arguments for the function

        Returns:
            Job ID for polling
        """
        job_id = self.job_store.create_job(webhook_url=webhook_url)

        future = self.executor.submit(
            self._execute_job_with_timeout, job_id, func, *args, **kwargs
        )

        self.job_store.track_future(job_id, future)

        logger.info("Job submitted to thread pool", job_id=job_id)
        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result."""
        job = self.job_store.get_job(job_id)
        if not job:
            return None

        response = {
            "schemaVersion": 1,
            "status": job.status.value,
            "results": [],
            "error": None,
        }

        if job.status == JobStatus.RUNNING:
            response["progress"] = {
                "percent": round(job.progress * 100, 1),
                "phase": job.progress_phase,
                "details": job.progress_details,
            }

        if job.status == JobStatus.SUCCESS and job.result:
            response.update(job.result)
        elif job.status in [JobStatus.FAILURE, JobStatus.TIMEOUT]:
            response["error"] = job.error

            intermediate = self.job_store.get_intermediate_result(job_id)
            if intermediate:
                response["intermediate_result"] = intermediate
                logger.info("Returning intermediate result for failed job", job_id=job_id)

        return response

    def update_job_progress(
        self, job_id: str, phase: str, progress: float, details: Dict[str, Any] = None
    ) -> None:
        """Update progress for a running job."""
        self.job_store.update_job_progress(job_id, phase, progress, details)

    def delete_job(self, job_id: str) -> bool:
        """Delete a job (admin endpoint)."""
        return self.job_store.delete_job(job_id)

    def _execute_job_with_timeout(self, job_id: str, func: Callable, *args, **kwargs):
        """Execute job with timeout enforcement."""
        try:
            logger.info(
                "Starting job execution",
                job_id=job_id,
                timeout=self.timeout_seconds,
            )
            start_time = time.time()

            work_future = self.executor.submit(self._execute_job, job_id, func, *args, **kwargs)

            done, not_done = wait([work_future], timeout=self.timeout_seconds)

            if work_future in done:
                try:
                    work_future.result()
                except Exception:
                    pass
            else:
                work_future.cancel()
                execution_time = time.time() - start_time
                logger.warning(
                    "Job execution timed out",
                    job_id=job_id,
                    timeout=self.timeout_seconds,
                    execution_time=execution_time,
                )
                self.job_store.update_job_timeout(job_id)

        except Exception as e:
            logger.error("Error in job timeout wrapper", job_id=job_id, error=str(e))
            self.job_store.update_job_failure(job_id, f"Timeout wrapper error: {str(e)}")

    def _execute_job(self, job_id: str, func: Callable, *args, **kwargs):
        """Execute job with error handling."""
        try:
            logger.info("Starting job execution", job_id=job_id)
            start_time = time.time()

            result = func(*args, **kwargs)

            execution_time = time.time() - start_time
            logger.info(
                "Job execution completed",
                job_id=job_id,
                execution_time=execution_time,
            )

            self.job_store.update_job_success(job_id, result)

        except Exception as e:
            logger.error("Job execution failed", job_id=job_id, error=str(e))
            self.job_store.update_job_failure(job_id, str(e))

    def cleanup_old_jobs(self) -> int:
        """Clean up old completed jobs. Returns count deleted."""
        if settings.job_retention_enabled:
            max_age = settings.job_retention_days * 24 * 60 * 60
            return self.job_store.cleanup_old_jobs(max_age)
        return 0

    def get_active_job_count(self) -> int:
        """Get count of currently running jobs."""
        return self.job_store.get_active_job_count()

    def get_completed_job_count_24h(self) -> int:
        """Get count of jobs completed in last 24 hours."""
        since = time.time() - (24 * 60 * 60)
        return self.job_store.get_completed_job_count_since(since)

    def shutdown(self):
        """Shutdown the job manager."""
        logger.info("Shutting down job manager")
        self.executor.shutdown(wait=True)


# Global job manager instance - created lazily
_job_manager: Optional[JobManager] = None


def get_job_manager() -> JobManager:
    """Get the global job manager instance."""
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager


def shutdown_job_manager():
    """Shutdown the global job manager."""
    global _job_manager
    if _job_manager is not None:
        _job_manager.shutdown()
        _job_manager = None
