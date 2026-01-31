"""SQLite backend for job persistence."""

import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from sqlalchemy import create_engine, Column, String, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.db.base import JobStore, Job, JobStatus
from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

Base = declarative_base()


class JobModel(Base):
    """SQLAlchemy model for jobs table."""
    __tablename__ = "jobs"

    job_id = Column(String(36), primary_key=True)
    status = Column(String(20), nullable=False, default="running")
    created_at = Column(Float, nullable=False)
    completed_at = Column(Float, nullable=True)
    result = Column(Text, nullable=True)  # JSON
    error = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)
    progress_phase = Column(String(100), default="")
    progress_details = Column(Text, default="{}")  # JSON
    intermediate_result = Column(Text, nullable=True)  # JSON
    webhook_url = Column(String(500), nullable=True)


class SQLiteJobStore(JobStore):
    """SQLite-based job storage."""

    def __init__(self, database_url: str = None):
        super().__init__()
        url = database_url or settings.database_url

        # Ensure data directory exists
        if url.startswith("sqlite:///"):
            db_path = url.replace("sqlite:///", "")
            if db_path.startswith("./"):
                db_path = db_path[2:]
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create engine with connection pooling for SQLite
        self.engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )

        # Create tables
        Base.metadata.create_all(self.engine)

        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)

        logger.info("SQLite job store initialized", database_url=url)

    def _to_job(self, model: JobModel) -> Job:
        """Convert SQLAlchemy model to Job dataclass."""
        return Job(
            job_id=model.job_id,
            status=JobStatus(model.status),
            created_at=model.created_at,
            completed_at=model.completed_at,
            result=json.loads(model.result) if model.result else None,
            error=model.error,
            progress=model.progress,
            progress_phase=model.progress_phase,
            progress_details=json.loads(model.progress_details) if model.progress_details else {},
            intermediate_result=json.loads(model.intermediate_result) if model.intermediate_result else None,
            webhook_url=model.webhook_url,
        )

    def create_job(self, webhook_url: Optional[str] = None) -> str:
        """Create a new job and return its ID."""
        job_id = str(uuid.uuid4())

        with self.SessionLocal() as session:
            job = JobModel(
                job_id=job_id,
                status=JobStatus.RUNNING.value,
                created_at=time.time(),
                progress=0.0,
                progress_phase="",
                progress_details="{}",
                webhook_url=webhook_url,
            )
            session.add(job)
            session.commit()

        logger.info("Created job", job_id=job_id)
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        with self.SessionLocal() as session:
            model = session.query(JobModel).filter(JobModel.job_id == job_id).first()
            if model:
                return self._to_job(model)
        return None

    def update_job_success(self, job_id: str, result: Dict[str, Any]) -> None:
        """Mark job as successful with result."""
        with self.SessionLocal() as session:
            model = session.query(JobModel).filter(JobModel.job_id == job_id).first()
            if model:
                model.status = JobStatus.SUCCESS.value
                model.completed_at = time.time()
                model.result = json.dumps(result)
                model.intermediate_result = None  # Clean up
                session.commit()
                logger.info("Job completed successfully", job_id=job_id)

        self.remove_future(job_id)

    def update_job_failure(self, job_id: str, error: str) -> None:
        """Mark job as failed with error."""
        with self.SessionLocal() as session:
            model = session.query(JobModel).filter(JobModel.job_id == job_id).first()
            if model:
                model.status = JobStatus.FAILURE.value
                model.completed_at = time.time()
                model.error = error
                session.commit()
                logger.error("Job failed", job_id=job_id, error=error)

        self.remove_future(job_id)

    def update_job_timeout(self, job_id: str) -> None:
        """Mark job as timed out."""
        with self.SessionLocal() as session:
            model = session.query(JobModel).filter(JobModel.job_id == job_id).first()
            if model:
                # Don't overwrite if already completed
                if model.status == JobStatus.SUCCESS.value:
                    logger.info("Timeout called but job already succeeded", job_id=job_id)
                    return

                model.status = JobStatus.TIMEOUT.value
                model.completed_at = time.time()
                model.error = "Job execution timed out"
                session.commit()
                logger.warning("Job timed out", job_id=job_id)

        self.remove_future(job_id)

    def update_job_progress(
        self, job_id: str, phase: str, progress: float, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update job progress."""
        with self.SessionLocal() as session:
            model = session.query(JobModel).filter(JobModel.job_id == job_id).first()
            if model and model.status == JobStatus.RUNNING.value:
                model.progress = progress
                model.progress_phase = phase
                model.progress_details = json.dumps(details or {})
                session.commit()

    def save_intermediate_result(self, job_id: str, result: Dict[str, Any]) -> None:
        """Save intermediate result for crash recovery."""
        with self.SessionLocal() as session:
            model = session.query(JobModel).filter(JobModel.job_id == job_id).first()
            if model:
                model.intermediate_result = json.dumps(result)
                session.commit()
                logger.debug("Saved intermediate result", job_id=job_id)

    def get_intermediate_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get intermediate result for a job."""
        job = self.get_job(job_id)
        return job.intermediate_result if job else None

    def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        with self.SessionLocal() as session:
            model = session.query(JobModel).filter(JobModel.job_id == job_id).first()
            if model:
                session.delete(model)
                session.commit()
                logger.info("Job deleted", job_id=job_id)

                # Cancel future if running
                future = self.get_future(job_id)
                if future and not future.done():
                    future.cancel()
                self.remove_future(job_id)

                return True
        return False

    def cleanup_old_jobs(self, max_age_seconds: int) -> int:
        """Clean up jobs older than max_age_seconds."""
        cutoff = time.time() - max_age_seconds

        with self.SessionLocal() as session:
            count = session.query(JobModel).filter(
                JobModel.completed_at != None,
                JobModel.completed_at < cutoff
            ).delete()
            session.commit()

            if count > 0:
                logger.info("Cleaned up old jobs", count=count, max_age_seconds=max_age_seconds)

            return count

    def get_active_job_count(self) -> int:
        """Get count of currently running jobs."""
        with self.SessionLocal() as session:
            return session.query(JobModel).filter(
                JobModel.status == JobStatus.RUNNING.value
            ).count()

    def get_completed_job_count_since(self, since_timestamp: float) -> int:
        """Get count of jobs completed since timestamp."""
        with self.SessionLocal() as session:
            return session.query(JobModel).filter(
                JobModel.completed_at != None,
                JobModel.completed_at >= since_timestamp
            ).count()
