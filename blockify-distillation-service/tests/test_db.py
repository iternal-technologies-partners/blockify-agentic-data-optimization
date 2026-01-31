"""Tests for database backends."""

import os
import tempfile
import pytest

from app.db.base import JobStatus
from app.db.filesystem import FileSystemJobStore


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_filesystem_job_store_create(temp_data_dir):
    """Test creating a job in filesystem store."""
    store = FileSystemJobStore(data_dir=temp_data_dir)

    job_id = store.create_job()

    assert job_id is not None
    job = store.get_job(job_id)
    assert job is not None
    assert job.status == JobStatus.PENDING


def test_filesystem_job_store_update_success(temp_data_dir):
    """Test updating job to success."""
    store = FileSystemJobStore(data_dir=temp_data_dir)

    job_id = store.create_job()
    result = {"results": [], "stats": {"count": 10}}

    store.update_job_success(job_id, result)

    job = store.get_job(job_id)
    assert job.status == JobStatus.SUCCESS
    assert job.result == result


def test_filesystem_job_store_update_failure(temp_data_dir):
    """Test updating job to failure."""
    store = FileSystemJobStore(data_dir=temp_data_dir)

    job_id = store.create_job()
    error = "Something went wrong"

    store.update_job_failure(job_id, error)

    job = store.get_job(job_id)
    assert job.status == JobStatus.FAILURE
    assert job.error == error


def test_filesystem_job_store_delete(temp_data_dir):
    """Test deleting a job."""
    store = FileSystemJobStore(data_dir=temp_data_dir)

    job_id = store.create_job()
    assert store.get_job(job_id) is not None

    deleted = store.delete_job(job_id)
    assert deleted is True
    assert store.get_job(job_id) is None


def test_filesystem_job_store_progress(temp_data_dir):
    """Test updating job progress."""
    store = FileSystemJobStore(data_dir=temp_data_dir)

    job_id = store.create_job()
    store.update_job_progress(job_id, "embedding", 0.5, {"blocks": 100})

    job = store.get_job(job_id)
    assert job.status == JobStatus.RUNNING
    assert job.progress == 0.5
    assert job.progress_phase == "embedding"
