"""Factory for creating job store instances based on configuration."""

from app.db.base import JobStore
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


def create_job_store() -> JobStore:
    """Create a job store instance based on configuration.

    Returns:
        JobStore instance for the configured backend
    """
    backend = settings.database_backend

    if backend == "sqlite":
        from app.db.sqlite import SQLiteJobStore
        logger.info("Using SQLite job store", database_url=settings.database_url)
        return SQLiteJobStore(settings.database_url)

    elif backend == "filesystem":
        from app.db.filesystem import FilesystemJobStore
        logger.info("Using filesystem job store", data_dir=settings.data_dir)
        return FilesystemJobStore(settings.data_dir)

    elif backend == "postgresql":
        # PostgreSQL support can be added later
        raise NotImplementedError(
            "PostgreSQL backend not yet implemented. "
            "Use sqlite or filesystem for now."
        )

    elif backend == "redis":
        # Redis support can be added later
        raise NotImplementedError(
            "Redis backend not yet implemented. "
            "Use sqlite or filesystem for now."
        )

    else:
        raise ValueError(f"Unknown database backend: {backend}")
